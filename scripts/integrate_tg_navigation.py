#!/usr/bin/env python3
"""Integrate Tajik into every site language menu without changing other languages."""
from pathlib import Path
from urllib.parse import urlsplit
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://agurkin2021-gif.github.io/vps-for-n8n/"
MAP = {
    "": "tg/",
    "best-vps-for-n8n.html": "tg/behtarin-vps-baroi-n8n.html",
    "about.html": "tg/dar-borai-mo.html",
    "n8n-backup-and-restore.html": "tg/nuskhai-ehtiyotii-n8n-va-barqarorsozi.html",
    "contact.html": "tg/tamos.html",
    "install-n8n-on-a-vps.html": "tg/nasbi-n8n-dar-vps.html",
    "n8n-cloud-vs-self-hosted.html": "tg/n8n-cloud-yo-hostingi-mustaqil.html",
    "n8n-vps-requirements.html": "tg/talabot-vps-baroi-n8n.html",
    "privacy.html": "tg/maxfiyat.html",
    "secure-n8n-on-a-vps.html": "tg/amniyati-n8n-dar-vps.html",
    "n8n-queue-mode.html": "tg/rejimi-navbat-n8n.html",
}
LANG = "tg"
NAME = "Тоҷикӣ"

menu_re = re.compile(
    r'(<div\b[^>]*class=["\'][^"\']*\blang-menu\b[^"\']*["\'][^>]*>)(.*?)(</div>)',
    re.I | re.S,
)
anchor_re = re.compile(
    r'<a\b(?=[^>]*\bhreflang=["\']tg["\'])[^>]*>.*?</a>', re.I | re.S
)
alternate_re = re.compile(
    r'<link\b(?=[^>]*\bhreflang=["\']tg["\'])[^>]*>\s*', re.I | re.S
)
tag_re = re.compile(r'<(?:a|link)\b[^>]*>', re.I)
href_re = re.compile(r'\bhref=["\']([^"\']+)["\']', re.I)
en_re = re.compile(r'\bhreflang=["\']en["\']', re.I)
head_end_re = re.compile(r'</head>', re.I)
canonical_re = re.compile(
    r'<link\b(?=[^>]*\brel=["\']canonical["\'])[^>]*>', re.I
)
schema_re = re.compile(
    r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.I | re.S,
)

def intent_for(html, path):
    # The English page link in a selector identifies the same page across all locales.
    menu = menu_re.search(html)
    content = menu.group(2) if menu else html
    for tag in tag_re.findall(content):
        if en_re.search(tag):
            match = href_re.search(tag)
            if match and match.group(1).startswith(BASE):
                rel = match.group(1)[len(BASE):].split('#', 1)[0].split('?', 1)[0]
                rel = "" if rel == "index.html" else rel
                if rel in MAP:
                    return rel
    # Some older pages have English alternates only in their head.
    for tag in tag_re.findall(html):
        if en_re.search(tag):
            match = href_re.search(tag)
            if match and match.group(1).startswith(BASE):
                rel = match.group(1)[len(BASE):].split('#', 1)[0].split('?', 1)[0]
                rel = "" if rel == "index.html" else rel
                if rel in MAP:
                    return rel
    if path.parent == ROOT and path.name in MAP:
        return path.name
    if path.relative_to(ROOT).as_posix() == "pt-br/n8n-hospedagem-brasil.html":
        return ""
    return None

def fix_local_tg_links(html):
    for en, tg in MAP.items():
        if not en:
            continue
        target_file = "index.html" if tg == "tg/" else tg.split("/")[-1]
        html = re.sub(
            r'(\bhref=["\'])' + re.escape(en) + r'(["\'])',
            lambda m, target_file=target_file: m.group(1) + target_file + m.group(2),
            html, flags=re.I,
        )
    return html

def normalize(html, path, intent):
    target = BASE + MAP[intent]
    is_tg = path.relative_to(ROOT).parts[0] == "tg"
    out = fix_local_tg_links(html) if is_tg else html

    def replace_menu(m):
        opener, inner, closer = m.groups()
        inner = anchor_re.sub("", inner)
        current = ' aria-current="page"' if is_tg else ""
        item = f'<a href="{target}" hreflang="tg" lang="tg"{current}>{NAME}</a>'
        return opener + inner + item + closer

    out, menu_count = menu_re.subn(replace_menu, out)
    if menu_count != 2:
        raise ValueError(f"{path}: expected header and footer menus, got {menu_count}")

    # Keep exactly one correct hreflang alternate in the head of each page.
    parts = re.split(r'</head>', out, maxsplit=1, flags=re.I)
    if len(parts) != 2:
        raise ValueError(f"{path}: missing </head>")
    head = alternate_re.sub("", parts[0])
    head += f'<link rel="alternate" hreflang="tg" href="{target}"/>'
    out = head + '</head>' + parts[1]
    return out

def validate_page(path, html, intent):
    target = BASE + MAP[intent]
    is_tg = path.relative_to(ROOT).parts[0] == "tg"
    assert len(re.findall(r'<h1(?:\s|>)', html, re.I)) == 1, path
    assert re.search(r'<html\b[^>]*lang=["\']tg["\']', html, re.I) if is_tg else True
    head = html.split("</head>", 1)[0]
    alternates = alternate_re.findall(head)
    assert len(alternates) == 1, (path, "tg alternates", len(alternates))
    assert f'href="{target}"' in alternates[0], (path, "tg hreflang", target)
    menus = menu_re.findall(html)
    assert len(menus) == 2, (path, "menus", len(menus))
    for _opener, inner, _closer in menus:
        links = re.findall(r'<a\b[^>]*>.*?</a>', inner, re.I | re.S)
        tglinks = [x for x in links if re.search(r'hreflang=["\']tg["\']', x, re.I)]
        assert len(tglinks) == 1, (path, "Tajik count", len(tglinks))
        assert links[-1] == tglinks[0], (path, "Tajik not last")
        assert f'href="{target}"' in tglinks[0], (path, "target", target)
        assert ('aria-current="page"' in tglinks[0]) == is_tg, (path, "current")
    if is_tg:
        canon = canonical_re.search(head)
        assert canon and f'href="{target}"' in canon.group(0), (path, "canonical")
        assert 'href="../styles.css"' in html, (path, "stylesheet")
        for match in schema_re.finditer(html):
            json.loads(match.group(1))

def sitemap_text():
    p = ROOT / "sitemap.xml"
    text = p.read_text(encoding="utf-8")
    for target in MAP.values():
        url = BASE + target
        if f"<loc>{url}</loc>" not in text:
            text = re.sub(
                r'</urlset>\s*$',
                f'  <url><loc>{url}</loc></url>\n</urlset>\n',
                text, count=1, flags=re.I,
            )
    root = ET.fromstring(text)
    actual = [e.text for e in root.findall(".//{*}loc")]
    for v in MAP.values():
        u = BASE + v
        assert actual.count(u) == 1, ("sitemap occurrence", u, actual.count(u))
    return text, len(actual)

def main():
    write = "--write" in sys.argv[1:]
    tg_files = sorted((ROOT / "tg").glob("*.html"))
    expected = {"index.html" if p == "tg/" else p.split("/")[-1] for p in MAP.values()}
    actual = {p.name for p in tg_files}
    if actual != expected:
        raise AssertionError(f"11 Tajik files expected; missing={expected-actual}; extra={actual-expected}")

    matched = 0
    changed = 0
    unknown = []
    all_pages = sorted(ROOT.rglob("*.html"))
    for p in all_pages:
        if ".git" in p.parts:
            continue
        html = p.read_text(encoding="utf-8")
        if not menu_re.search(html):
            continue
        intent = intent_for(html, p)
        if intent is None:
            unknown.append(str(p.relative_to(ROOT)))
            continue
        result = normalize(html, p, intent)
        if result != html:
            if write:
                p.write_text(result, encoding="utf-8")
            else:
                raise AssertionError(f"Non-finalized navigation: {p}")
        validate_page(p, result, intent)
        matched += 1
        changed += result != html
    if unknown:
        raise AssertionError("Unmapped pages with language menus: " + ", ".join(unknown))
    sitemap = ROOT / "sitemap.xml"
    new_sitemap, nloc = sitemap_text()
    if new_sitemap != sitemap.read_text(encoding="utf-8"):
        if write:
            sitemap.write_text(new_sitemap, encoding="utf-8")
        else:
            raise AssertionError("Sitemap missing Tajik URL(s)")

    for p in tg_files:
        c = p.read_text(encoding="utf-8")
        intent = intent_for(c, p)
        if intent is None:
            raise AssertionError(f"No English intent for Tajik {p}")
        if write:
            validate_page(p, c, intent)
        assert len(re.findall(r'<h1(?:\s|>)', c, re.I)) == 1, p

    print(f"TG_FINALIZE_PASS pages={len(tg_files)}/11 menus_on_files={matched} changed={changed} sitemap_urls={nloc} mode={'write' if write else 'check'}", flush=True)

if __name__ == "__main__":
    main()
