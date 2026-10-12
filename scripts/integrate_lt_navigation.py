#!/usr/bin/env python3
"""Integrate Lithuanian into every existing language selector without changing page content."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://agurkin2021-gif.github.io/vps-for-n8n/"
COUNTERPARTS = {
    "": "lt/",
    "index.html": "lt/",
    "best-vps-for-n8n.html": "lt/geriausias-vps-n8n.html",
    "about.html": "lt/apie.html",
    "n8n-backup-and-restore.html": "lt/n8n-atsargines-kopijos-atkurimas.html",
    "contact.html": "lt/kontaktai.html",
    "install-n8n-on-a-vps.html": "lt/kaip-idiegti-n8n-vps.html",
    "n8n-cloud-vs-self-hosted.html": "lt/n8n-cloud-ar-nuosavas-vps.html",
    "n8n-vps-requirements.html": "lt/n8n-vps-reikalavimai.html",
    "privacy.html": "lt/privatumo-politika.html",
    "secure-n8n-on-a-vps.html": "lt/n8n-vps-saugumas.html",
    "n8n-queue-mode.html": "lt/n8n-eiliu-rezimas.html",
}
MENU = re.compile(r'(<div\b[^>]*\bclass=["\'][^"\']*\blang-menu\b[^"\']*["\'][^>]*>)(.*?)(</div>)', re.I | re.S)
ANCHOR = re.compile(r'<a\b[^>]*>.*?</a>', re.I | re.S)
LINK = re.compile(r'<link\b[^>]*>', re.I | re.S)
HEAD_END = re.compile(r'</head\s*>', re.I)
JSONLD = re.compile(r'<script\b[^>]*\btype=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.I | re.S)


def attribute(element: str, name: str) -> str | None:
    match = re.search(r'\b' + re.escape(name) + r'\s*=\s*(["\'])(.*?)\1', element, re.I | re.S)
    return match.group(2) if match else None


def validate_sitemap() -> None:
    nodes = ET.parse(ROOT / "sitemap.xml").findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
    urls = [node.text for node in nodes if node.text]
    assert len(urls) == len(set(urls)), "sitemap has duplicate URLs"
    english = [url for url in urls if url.startswith(BASE) and "/" not in url[len(BASE):]]
    lithuanian = [url for url in urls if url.startswith(BASE + "lt/")]
    assert len(english) == len(lithuanian) == 11, (len(english), len(lithuanian))
    expected = {BASE + value for value in COUNTERPARTS.values()}
    assert set(lithuanian) == expected, (set(lithuanian) ^ expected)
    for url in expected:
        path = "lt/index.html" if url == BASE + "lt/" else url[len(BASE):]
        assert (ROOT / path).is_file(), path


def resolve_target(path: Path, first_menu: str) -> tuple[str, bool]:
    rel_path = path.relative_to(ROOT).as_posix()
    if rel_path.startswith("lt/"):
        dest = "lt/" if rel_path == "lt/index.html" else rel_path
        return BASE + dest, True
    english_link = next((a.group() for a in ANCHOR.finditer(first_menu)
                         if attribute(a.group(), "hreflang") == "en"), None)
    href = attribute(english_link, "href") if english_link else None
    key = href[len(BASE):] if href and href.startswith(BASE) else None
    exact = key in COUNTERPARTS and (key not in ("", "index.html") or path.name == "index.html")
    return BASE + (COUNTERPARTS[key] if exact else "lt/"), bool(exact)


def clean_menu(start: str, body: str, end: str, target: str, current: bool) -> str:
    body = ANCHOR.sub(
        lambda match: "" if attribute(match.group(), "hreflang") == "lt"
                              or attribute(match.group(), "lang") == "lt"
                      else match.group(), body)
    body = body.rstrip()
    selected = ' aria-current="page"' if current else ""
    return start + body + f'<a href="{target}" hreflang="lt" lang="lt"{selected}>Lietuvių</a>' + end


def integrate(path: Path, text: str) -> tuple[str, int, bool, str | None]:
    menus = list(MENU.finditer(text))
    if not menus:
        return text, 0, False, None
    target, exact = resolve_target(path, menus[0].group(2))
    current = path.relative_to(ROOT).parts[0] == "lt"
    transformed = MENU.sub(
        lambda m: clean_menu(m.group(1), m.group(2), m.group(3), target, current), text)
    # hreflang head alternates describe true equivalents only; fallback navigation is not a translation.
    head_match = HEAD_END.search(transformed)
    assert head_match, ("missing head", path)
    before, after = transformed[:head_match.start()], transformed[head_match.start():]
    before = LINK.sub(lambda m: "" if attribute(m.group(), "hreflang") == "lt" else m.group(), before)
    if exact:
        before += f'<link rel="alternate" hreflang="lt" href="{target}"/>'
    transformed = before + after
    if exact:
        assert (ROOT / ("lt/index.html" if target == BASE + "lt/" else target[len(BASE):])).is_file()
    return transformed, len(menus), exact, target


def verify(path: Path, text: str, menus: int, exact: bool, target: str | None) -> None:
    if not menus:
        return
    found = list(MENU.finditer(text))
    assert len(found) == menus, (path, len(found), menus)
    for menu in found:
        options = [x.group() for x in ANCHOR.finditer(menu.group(2))]
        lt = [a for a in options if attribute(a, "hreflang") == "lt"]
        assert len(lt) == 1 and options[-1] == lt[0], (path, "Lithuanian not last/unique")
        assert attribute(lt[0], "href") == target, (path, "incorrect destination")
        is_current = path.relative_to(ROOT).parts[0] == "lt"
        assert (attribute(lt[0], "aria-current") == "page") == is_current, path
    if menus == 2:
        assert text.index('class="lang-menu"') < text.index("</header>"), path
        assert text.rfind('class="lang-menu"') > text.index("<footer"), path
    head = text.split("</head>", 1)[0]
    alternates = [m.group() for m in LINK.finditer(head)
                  if attribute(m.group(), "hreflang") == "lt"]
    assert len(alternates) == (1 if exact else 0), (path, alternates)
    if exact:
        assert attribute(alternates[0], "href") == target, (path, "incorrect hreflang URL")
    if path.relative_to(ROOT).parts[0] == "lt":
        assert text.count("<h1") == 1, (path, "H1")
        assert 'lang="lt"' in text.split("<head", 1)[0], path
        for item in JSONLD.findall(text):
            json.loads(item)


def main(write: bool) -> None:
    validate_sitemap()
    changed = checked = menus_count = exact_count = fallback_count = skipped = 0
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts:
            continue
        original = path.read_text(encoding="utf-8")
        transformed, count, exact, target = integrate(path, original)
        verify(path, transformed, count, exact, target)
        checked += 1
        menus_count += count
        exact_count += int(exact and count > 0)
        fallback_count += int(not exact and count > 0)
        skipped += int(count == 0)
        if original != transformed:
            if not write:
                raise AssertionError(f"Unpublished Lithuanian navigation in {path.relative_to(ROOT)}")
            path.write_text(transformed, encoding="utf-8")
            changed += 1
    assert checked >= 480, checked
    assert menus_count >= 940, menus_count
    assert (ROOT / "lt/n8n-eiliu-rezimas.html").is_file()
    print(f"LT_GLOBAL_PASS html={checked} menu_count={menus_count} exact={exact_count} "
          f"fallback={fallback_count} no_menu={skipped} updated={changed} write={write}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    main(args.write)
