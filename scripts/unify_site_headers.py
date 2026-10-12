#!/usr/bin/env python3
"""Make the site header identical to each locale's homepage on every content page.

Contract: logo left, four localized homepage-nav links center, current page's
language switcher right. All other page markup and language menus are unchanged.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter
from functools import lru_cache
import os
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
IDS = ("workloads", "requirements", "architecture", "faq")
HDR = re.compile(r"<header\b[^>]*>[\s\S]*?</header>", re.I)
NAV = re.compile(
    r"<nav\b(?=[^>]*\bclass=[\"'][^\"']*\bmain-nav\b)[^>]*>[\s\S]*?</nav>", re.I
)
BRAND = re.compile(
    r"<a\b(?=[^>]*\bclass=[\"'][^\"']*\bbrand\b)[^>]*>[\s\S]*?</a>", re.I
)
SWITCH = re.compile(
    r"<div\b(?=[^>]*\bclass=[\"'][^\"']*\blang-switch\b)[^>]*>"
    r"[\s\S]*?</div>\s*</div>", re.I
)
LOCALE_CLASS = re.compile(r"\bclass=([\"'])([^\"']*)\1", re.I)
A_HREF = re.compile(r"\bhref=([\"'])[^\"']*\1", re.I)
ANCHOR = re.compile(r"<a\b[^>]*\bhref=([\"'])#([-\w]+)\1[^>]*>", re.I)
STYLE_TOKEN = "site-header"

@lru_cache(maxsize=None)
def homepage(locale: str) -> Path:
    folder = ROOT / locale if locale else ROOT
    first = folder / "index.html"
    if first.exists() and NAV.search(first.read_text(encoding="utf-8")):
        return first
    # Italian /it/ is a redirect: the content homepage is /it/vps-n8n/.
    candidates = [
        p for p in folder.rglob("index.html")
        if p != first and NAV.search(p.read_text(encoding="utf-8"))
    ]
    if len(candidates) == 1:
        return candidates[0]
    raise AssertionError(
        f"Cannot uniquely identify translated homepage for {locale!r}: {candidates}"
    )

@lru_cache(maxsize=None)
def nav_template(locale: str) -> str:
    home = homepage(locale)
    markup = home.read_text(encoding="utf-8")
    header = HDR.search(markup)
    if not header:
        raise AssertionError(f"Homepage header missing: {home}")
    nav = NAV.search(header.group())
    if not nav:
        raise AssertionError(f"Homepage nav missing: {home}")
    anchors = ANCHOR.findall(nav.group())
    if [anchor for _quote, anchor in anchors] != list(IDS):
        raise AssertionError(f"Unexpected nav anchors on {home}: {anchors}")
    return nav.group()

def is_redirect_or_verification(path: Path, html: str) -> bool:
    return bool(
        re.search(r"<meta\b[^>]*http-equiv=[\"']refresh[\"']", html, re.I)
        or path.name.startswith("google") and path.suffix == ".html"
    )

def locale_for(path: Path) -> str:
    rel = path.relative_to(ROOT)
    return rel.parts[0] if len(rel.parts) >= 2 else ""

def home_prefix(from_page: Path, home: Path) -> str:
    rel = os.path.relpath(home.parent, start=from_page.parent).replace(os.sep, "/")
    return "./" if rel == "." else rel.rstrip("/") + "/"

def header_tag(original_header: str) -> str:
    tag = re.match(r"<header\b[^>]*>", original_header, re.I).group(0)
    m = LOCALE_CLASS.search(tag)
    if m:
        existing = m.group(2).split()
        if STYLE_TOKEN not in existing:
            existing.append(STYLE_TOKEN)
        new = " ".join(existing)
        return tag[:m.start(2)] + new + tag[m.end(2):]
    return tag[:-1] + f' class="{STYLE_TOKEN}">'

def get_language_switch(original_header: str, document: str, path: Path) -> str:
    x = SWITCH.search(original_header)
    if x:
        return x.group()
    if path.name != "404.html":
        raise AssertionError(f"No language selector in header: {path}")
    # 404 historically has only a footer selector; retain that footer and
    # use the same choices also in the header.
    foot = document.split("<footer", 1)
    if len(foot) != 2:
        raise AssertionError("404.html lacks footer")
    x = SWITCH.search(foot[1])
    if not x:
        raise AssertionError("404.html lacks footer selector")
    clone = x.group()
    clone = re.sub(r'class=(["\'])lang-switch footer-lang-switch\1',
                   'class="lang-switch"', clone, count=1)
    clone = re.sub(r'(<div\b[^>]*\bclass=["\']lang-menu["\'])\s+style=["\'][^"\']*["\']',
                   r'\1', clone, count=1)
    return clone

def target_header(path: Path, document: str, old_header: str, locale: str) -> str:
    home = homepage(locale)
    prefix = home_prefix(path, home)
    brand_match = BRAND.search(old_header)
    if not brand_match:
        # Legacy pages occasionally translated part of the CSS class name.
        # Use the original n8nVPS logo from the homepage in the same language.
        source_header = HDR.search(home.read_text(encoding="utf-8"))
        brand_match = BRAND.search(source_header.group()) if source_header else None
    if not brand_match:
        raise AssertionError(f"Missing logo on page and locale homepage: {path}")
    brand = brand_match.group()
    logo_href = "#" if path == home else prefix
    new_brand, changes = A_HREF.subn(f'href="{logo_href}"', brand, count=1)
    if changes != 1:
        raise AssertionError(f"Logo href missing: {path}")
    brand = new_brand
    nav = nav_template(locale)
    def rewrite_nav(m):
        quote, anchor = m.group(1), m.group(2)
        # Same-page anchor on homepage, homepage anchor on other sections.
        target = "#" + anchor if path == home else prefix + "#" + anchor
        return 'href="' + target + '"'
    nav = re.sub(r"\bhref=([\"'])#([-\w]+)\1", rewrite_nav, nav, flags=re.I)
    lang_picker = get_language_switch(old_header, document, path)
    return header_tag(old_header) + brand + nav + lang_picker + "</header>"

def normalize(path: Path, html: str) -> tuple[str, bool]:
    header = HDR.search(html)
    if not header:
        if not is_redirect_or_verification(path, html) and "lang-menu" in html:
            raise AssertionError(f"Content page has language menu but no header: {path}")
        return html, False
    if is_redirect_or_verification(path, html):
        return html, False
    loc = locale_for(path)
    updated = target_header(path, html, header.group(), loc)
    # Preserve all page content outside header, including metadata, CSS,
    # JS, FAQ, images, footer language switchers and affiliate URLs.
    result = html[:header.start()] + updated + html[header.end():]
    return result, result != html

def assert_valid(path: Path, html: str) -> None:
    h = HDR.search(html)
    if not h:
        return
    loc = locale_for(path)
    nav = NAV.search(h.group())
    if not nav or "site-header" not in h.group().split(">",1)[0]:
        raise AssertionError(f"Missing unified header/nav: {path}")
    anchors = re.findall(r'<a\b[^>]*href=["\']([^"\']+)["\']', nav.group(), re.I)
    if len(anchors) != 4:
        raise AssertionError(f"Expected four nav links: {path}")
    home = homepage(loc)
    prefix = home_prefix(path, home)
    expected = [
        "#" + v if path == home else prefix + "#" + v
        for v in IDS
    ]
    if anchors != expected:
        raise AssertionError(f"Wrong nav targets {path}: {anchors} vs {expected}")
    home_nav = nav_template(loc)
    original_text = re.findall(r'<a\b[^>]*>([\s\S]*?)</a>', home_nav, re.I)
    current_text = re.findall(r'<a\b[^>]*>([\s\S]*?)</a>', nav.group(), re.I)
    if original_text != current_text:
        raise AssertionError(f"Not localized as homepage: {path}")
    if SWITCH.search(h.group()) is None:
        raise AssertionError(f"No right-hand language switch: {path}")
    if not BRAND.search(h.group()):
        raise AssertionError(f"No left-hand logo: {path}")
    if not (ROOT / "styles.css").exists():
        raise AssertionError("Missing shared CSS")

def main():
    write = "--write" in sys.argv[1:]
    count_changed = 0
    count_headers = 0
    noheaders = []
    locales = Counter()
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts:
            continue
        before = path.read_text(encoding="utf-8")
        after, changed = normalize(path, before)
        if not HDR.search(after):
            noheaders.append(path.relative_to(ROOT).as_posix())
            continue
        assert_valid(path, after)
        count_headers += 1
        locales[locale_for(path) or "en"] += 1
        if changed:
            if not write:
                raise AssertionError(f"Header differs from agreed template: {path}")
            path.write_text(after, encoding="utf-8")
            count_changed += 1
    if count_headers < 550 or len(locales) < 45:
        raise AssertionError(f"Coverage unexpectedly low: {count_headers}; {locales}")
    print(
        f"HEADER_UNIFIED_PASS pages={count_headers} languages={len(locales)} "
        f"changed={count_changed} skipped_redirects={noheaders} "
        f"mode={'write' if write else 'check'}",
        flush=True,
    )

if __name__ == "__main__":
    main()
