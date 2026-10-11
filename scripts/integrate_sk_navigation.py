#!/usr/bin/env python3
"""Integrate Slovenčina in every existing header/footer language selector.

The English sitemap defines the 11 translated page equivalents. For extra
regional landing pages without an English equivalent, the switch targets the
Slovak home page; such non-equivalent pages receive no hreflang alternate.
"""
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET

BASE = "https://agurkin2021-gif.github.io/vps-for-n8n/"
ROOT = Path(".")
EN_PAGES = [
    "", "best-vps-for-n8n.html", "about.html", "n8n-backup-and-restore.html",
    "contact.html", "install-n8n-on-a-vps.html",
    "n8n-cloud-vs-self-hosted.html", "n8n-vps-requirements.html",
    "privacy.html", "secure-n8n-on-a-vps.html", "n8n-queue-mode.html",
]
MENU = re.compile(r'(<div\s+class="lang-menu"[^>]*>)(.*?)(</div>)', re.S)
ANCHOR = re.compile(r'<a\b[^>]*>.*?</a>', re.I | re.S)
HREF = re.compile(r'\bhref=["\']([^"\']+)["\']', re.I)
LANG = re.compile(r'\b(?:hreflang|lang)=["\']([^"\']+)["\']', re.I)
LABEL = re.compile(r'<[^>]*>')
ALT_SK = re.compile(r'<link\b(?=[^>]*\bhreflang=["\']sk["\'])[^>]*>', re.I)


def anchors(menu):
    return ANCHOR.findall(menu)


def label(a):
    return LABEL.sub("", a).strip()


def href(a):
    match = HREF.search(a)
    return match.group(1) if match else ""


def find_language(menu, language, fallback_name):
    candidates = anchors(menu)
    return next((a for a in candidates if
                 (LANG.search(a) and LANG.search(a).group(1).lower() == language)
                 or label(a) == fallback_name), None)


def equivalent(footer):
    # Danish and Slovak share all eleven canonical page filenames.
    da = find_language(footer, "da", "Dansk")
    if da and href(da).startswith(BASE + "da/"):
        tail = href(da)[len(BASE + "da/"):]
        if tail == "index.html":
            tail = ""
        if tail in EN_PAGES and (ROOT / "sk" / (tail or "index.html")).is_file():
            return tail
    en = find_language(footer, "en", "English")
    if en and href(en).startswith(BASE):
        tail = href(en)[len(BASE):]
        if tail == "index.html":
            tail = ""
        if tail in EN_PAGES and (ROOT / "sk" / (tail or "index.html")).is_file():
            return tail
    raise AssertionError("No matching Slovak destination in language menu")


def main():
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap = ET.parse("sitemap.xml").getroot()
    locs = [(elem.text or "").strip() for elem in sitemap.findall(".//s:loc", namespace)]
    enurls = [url for url in locs if url.startswith(BASE) and
              url[len(BASE):] in EN_PAGES and
              url[len(BASE):].count("/") == 0]
    skurls = [url for url in locs if url.startswith(BASE + "sk/")]
    expected = [BASE + "sk/" + suffix for suffix in EN_PAGES]
    assert len(enurls) == len(EN_PAGES) == 11, ("English sitemap", enurls)
    assert len(skurls) == 11 and set(skurls) == set(expected) and len(set(skurls)) == 11, ("Slovak sitemap", skurls)
    assert len(list(Path("sk").glob("*.html"))) == 11, "11 Slovak files required"
    assert all((ROOT / "sk" / (suffix or "index.html")).is_file() for suffix in EN_PAGES)

    stats = {"scanned": 0, "with_menus": 0, "single_menu_pages": 0, "updated": 0,
             "already_present": 0, "skipped_no_menus": [],
             "head_alternates_added": 0, "menu_links_added": 0,
             "counterparts": {}, "checked_menu_links": 0}
    for file in sorted(ROOT.rglob("*.html")):
        if any(part in (".git", "_site", "node_modules") for part in file.parts):
            continue
        stats["scanned"] += 1
        original = file.read_text(encoding="utf-8")
        existing = list(MENU.finditer(original))
        if not existing:
            stats["skipped_no_menus"].append(str(file))
            continue
        assert len(existing) in (1, 2), "Expected one or two standard menus: " + str(file)
        if len(existing) == 1:
            stats["single_menu_pages"] += 1
        tail = equivalent(existing[-1].group(2))
        url = BASE + "sk/" + tail
        stats["counterparts"][tail or "(home)"] = stats["counterparts"].get(tail or "(home)", 0) + 1
        localized = file.parts[0] == "sk"
        entry = '<a href="' + url + '" hreflang="sk" lang="sk"' + (' aria-current="page"' if localized else '') + '>Slovenčina</a>'

        def add_language(match):
            header, inside, close = match.groups()
            a = find_language(inside, "sk", "Slovenčina")
            if a:
                assert href(a) == url, "Wrong existing Slovak target: " + str(file)
                assert a.count('aria-current="page"') == (1 if localized else 0), "Wrong Slovak selection: " + str(file)
            else:
                assert find_language(inside, "no", "Norsk"), "Cannot find Norsk: " + str(file)
                # Append after Norsk, preserving every original language link.
                anchors_here = anchors(inside)
                last_norsk = next((x for x in anchors_here if label(x) == "Norsk"), None)
                assert last_norsk is not None, "No Norsk label in " + str(file)
                inside = inside.replace(last_norsk, last_norsk + entry, 1)
                stats["menu_links_added"] += 1
            return header + inside + close

        modified = MENU.sub(add_language, original)
        # A real translated counterpart gets an SEO alternate. A regional page
        # that merely points to the Slovak home page does not.
        is_home = file.name == "index.html"
        is_counterpart = (tail != "") or is_home
        headpart = modified.partition("</head>")[0]
        if is_counterpart and not ALT_SK.search(headpart):
            assert "</head>" in modified, "No head in " + str(file)
            modified = modified.replace("</head>", '<link rel="alternate" hreflang="sk" href="' + url + '"/></head>', 1)
            stats["head_alternates_added"] += 1

        menus = list(MENU.finditer(modified))
        assert len(menus) == len(existing), "Lost a menu: " + str(file)
        for menu in menus:
            a = [x for x in anchors(menu.group(2)) if label(x) == "Slovenčina"]
            assert len(a) == 1 and href(a[0]) == url, "Missing or duplicated Slovak: " + str(file)
            stats["checked_menu_links"] += 1
        if localized:
            # The existing Slovak home page previously also selected English.
            modified = re.sub(r'(<a\b[^>]*\bhreflang="en"[^>]*?) aria-current="page"(?=[^>]*>English</a>)',
                              r'\1', modified)
            assert modified.count('aria-current="page"') == 2, "Two active Slovak entries required: " + str(file)
        if modified != original:
            file.write_text(modified, encoding="utf-8")
            stats["updated"] += 1
        else:
            stats["already_present"] += 1
        stats["with_menus"] += 1

    assert stats["with_menus"] >= 420, "Too few standard pages examined: " + repr(stats)
    assert stats["checked_menu_links"] == 2 * stats["with_menus"] - stats["single_menu_pages"], "Header/footer count mismatch"
    # Idempotence and verification for the canonical 11 Slovak pages.
    for suffix in EN_PAGES:
        page = ROOT / "sk" / (suffix or "index.html")
        html = page.read_text(encoding="utf-8")
        assert html.count('hreflang="sk" lang="sk" aria-current="page"') == 2, page
        assert ALT_SK.search(html.split("</head>")[0]), "Missing Slovak SEO self-alternate: " + str(page)
    print("SK_NAVIGATION_QA_PASS " + json.dumps(stats, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
