#!/usr/bin/env python3
"""Add Finnish to all existing site language selectors without changing page content."""
from __future__ import annotations

from collections import Counter
from html import unescape
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
BASE = "https://agurkin2021-gif.github.io/vps-for-n8n/"
EN = (
    "index.html", "best-vps-for-n8n.html", "about.html",
    "n8n-backup-and-restore.html", "contact.html", "install-n8n-on-a-vps.html",
    "n8n-cloud-vs-self-hosted.html", "n8n-vps-requirements.html",
    "privacy.html", "secure-n8n-on-a-vps.html", "n8n-queue-mode.html",
)
MENU = re.compile(r'(<div\b[^>]*class=["\'][^"\']*\blang-menu\b[^"\']*["\'][^>]*>)([\s\S]*?)(</div>)', re.I)
ANCHOR = re.compile(r'<a\b[^>]*>[^<>]*</a>', re.I)
LINK = re.compile(r'<link\b[^>]*>', re.I)
ATTR = re.compile(r'([:\w-]+)\s*=\s*(["\'])(.*?)\2', re.S)
SCRIPTS = re.compile(r'<script\b[^>]*>[\s\S]*?</script>', re.I)
STYLES = re.compile(r'<style\b[^>]*>[\s\S]*?</style>', re.I)
MAIN = re.compile(r'<main\b[^>]*>[\s\S]*?</main>', re.I)

def attr(tag, key):
    return next((m.group(3) for m in ATTR.finditer(tag) if m.group(1).lower() == key), None)

def source_page(path, html):
    if path in EN:
        return path
    if path.startswith("fi/") and path[3:] in EN:
        return path[3:]
    if path.endswith("/index.html"):
        return "index.html"
    menus = [m.group(2) for m in MENU.finditer(html)]
    # Compare exact counterpart links. A non-home link takes precedence over
    # homepage fallbacks used for content without an equivalent translation.
    for code in ("he", "sr", "sv", "en"):
        for inner in menus:
            for match in ANCHOR.finditer(inner):
                tag = match.group()
                href = attr(tag, "href") or ""
                actual = (attr(tag, "hreflang") or attr(tag, "lang") or "").lower()
                label = unescape(re.sub(r"<[^>]+>", "", tag)).strip()
                if actual != code and not (code == "en" and label == "English"):
                    continue
                if not href.startswith(BASE):
                    continue
                suffix = href[len(BASE):]
                for prefix in ("he/", "sr/", "sv/"):
                    if suffix.startswith(prefix):
                        suffix = suffix[len(prefix):]
                        break
                if suffix in EN and suffix != "index.html":
                    return suffix
    if path.rsplit("/", 1)[-1] in EN:
        return path.rsplit("/", 1)[-1]
    return None

def destination(page):
    return BASE + "fi/" + ("" if not page or page == "index.html" else page)

def update_href(tag, value):
    return re.sub(
        r'\bhref\s*=\s*(["\']).*?\1',
        lambda m: "href=" + m.group(1) + value + m.group(1),
        tag, count=1, flags=re.I | re.S,
    )

def transform(path, source):
    if "lang-menu" not in source:
        if "footer-lang-switch" in source:
            raise AssertionError(f"{path}: footer language switch has no menu")
        return source, 0
    page = source_page(path, source)
    url = destination(page)
    is_current = path.startswith("fi/")
    insert = '<a href="' + url + '" hreflang="fi" lang="fi"' + (
        ' aria-current="page"' if is_current else ""
    ) + '>Suomi</a>'
    def edit_menu(m):
        start, inner, end = m.groups()
        def remove_old(x):
            link = x.group()
            label = unescape(re.sub(r"<[^>]+>", "", link)).strip()
            if (attr(link, "hreflang") or "").lower() == "fi":
                return ""
            if (attr(link, "lang") or "").lower() == "fi":
                return ""
            if label == "Suomi":
                return ""
            return link
        return start + ANCHOR.sub(remove_old, inner) + insert + end
    result, n = MENU.subn(edit_menu, source)
    if path != "404.html":
        if n != 2 or "footer-lang-switch" not in result:
            raise AssertionError(f"{path}: expected exactly two language menus")
    elif n != 1:
        raise AssertionError("404: expected exactly one menu")
    before_head, separator, body = result.partition("</head>")
    if separator and page is not None:
        original_links = [m.group() for m in LINK.finditer(before_head)]
        matched = [x for x in original_links if (attr(x, "hreflang") or "").lower() == "fi"]
        if matched:
            # Correct any old Finnish alternate instead of creating duplicates.
            head = LINK.sub(lambda x: update_href(x.group(), url)
                            if (attr(x.group(), "hreflang") or "").lower() == "fi"
                            else x.group(), before_head)
        else:
            head = before_head + '<link rel="alternate" hreflang="fi" href="' + url + '"/>'
        result = head + separator + body
    # Preserve original body, CSS, JS, images, prices and visible content.
    old_main = MAIN.search(source)
    new_main = MAIN.search(result)
    if (old_main.group() if old_main else None) != (new_main.group() if new_main else None):
        raise AssertionError(f"{path}: main content changed")
    if SCRIPTS.findall(source) != SCRIPTS.findall(result):
        raise AssertionError(f"{path}: scripts changed")
    if STYLES.findall(source) != STYLES.findall(result):
        raise AssertionError(f"{path}: styles changed")
    anchors = [m.group() for menu in MENU.finditer(result)
               for m in ANCHOR.finditer(menu.group(2))]
    target_count = sum((attr(x, "hreflang") or "").lower() == "fi" for x in anchors)
    if target_count != n:
        raise AssertionError(f"{path}: Finnish selector count mismatch")
    for menu in MENU.finditer(result):
        matches = [x.group() for x in ANCHOR.finditer(menu.group(2))]
        if not matches or matches[-1] != insert:
            raise AssertionError(f"{path}: Finnish must be last and unique")
    if page is not None and separator:
        links = [m.group() for m in LINK.finditer(result.split("</head>", 1)[0])
                 if (attr(m.group(), "hreflang") or "").lower() == "fi"]
        if len(links) != 1 or attr(links[0], "href") != url:
            raise AssertionError(f"{path}: Finnish hreflang incorrect")
    return result, n

def verify_sources():
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
    urls = [n.text for n in ET.parse(ROOT / "sitemap.xml").iter(ns)]
    assert len(urls) == len(set(urls)), "Sitemap duplicates"
    expected_en = {BASE + ("" if x == "index.html" else x) for x in EN}
    expected_fi = {destination(x) for x in EN}
    assert expected_en.issubset(urls), "English sitemap lacks source pages"
    assert expected_fi.issubset(urls), "Finnish sitemap lacks pages"
    assert len([u for u in urls if u.startswith(BASE + "fi/")]) == 11
    pages = list((ROOT / "fi").glob("*.html"))
    assert len(pages) == 11, f"Finnish file count {len(pages)}"
    for name in EN:
        doc = (ROOT / "fi" / name)
        assert doc.is_file(), str(doc)
        body = doc.read_text(encoding="utf-8")
        assert re.search(r'<html\b[^>]*lang="fi"', body, re.I)
        assert len(re.findall(r"<h1(?:\s|>)", body, re.I)) == 1
        assert destination(name) in body
        for raw in re.findall(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', body, re.I | re.S):
            json.loads(raw)
    return len(urls)

def main():
    url_count = verify_sources()
    changed = 0
    page_count = 0
    menus = 0
    fallback_count = 0
    dests = Counter()
    for file in sorted(ROOT.rglob("*.html")):
        if ".git" in file.parts:
            continue
        rel = file.relative_to(ROOT).as_posix()
        source = file.read_text(encoding="utf-8")
        result, n = transform(rel, source)
        page_count += 1
        menus += n
        if source_page(rel, source) is None:
            fallback_count += 1
        if n:
            dests[destination(source_page(rel, source))] += n
        if result != source:
            file.write_text(result, encoding="utf-8")
            changed += 1
    assert page_count >= 400, f"Too few site pages: {page_count}"
    assert menus >= 800, f"Footer selector coverage unexpectedly low: {menus}"
    assert len(dests) == 11, f"Missing Finnish destinations: {sorted(dests)}"
    assert verify_sources() == url_count
    # A second pass must be idempotent.
    for file in sorted(ROOT.rglob("*.html")):
        if ".git" in file.parts:
            continue
        rel = file.relative_to(ROOT).as_posix()
        source = file.read_text(encoding="utf-8")
        result, _ = transform(rel, source)
        if result != source:
            raise AssertionError(f"Not idempotent: {rel}")
    print(f"FI_GLOBAL_QA_PASS english=11 finnish=11 urls={url_count} "
          f"html_pages={page_count} selectors={menus} changed={changed} "
          f"fallback_pages={fallback_count} destinations={len(dests)}",
          flush=True)

if __name__ == "__main__":
    main()
