#!/usr/bin/env python3
"""Integrate Latvian links throughout all existing website language selectors."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://agurkin2021-gif.github.io/vps-for-n8n/"
MATCHES = {
    "": "lv/",
    "index.html": "lv/",
    "best-vps-for-n8n.html": "lv/labakais-vps-n8n.html",
    "about.html": "lv/par-projektu.html",
    "n8n-backup-and-restore.html": "lv/n8n-rezerves-kopijas-un-atjaunosana.html",
    "contact.html": "lv/kontakti.html",
    "install-n8n-on-a-vps.html": "lv/n8n-instalesana-vps.html",
    "n8n-cloud-vs-self-hosted.html": "lv/n8n-cloud-vai-pasmitinasana.html",
    "n8n-vps-requirements.html": "lv/n8n-vps-prasibas.html",
    "privacy.html": "lv/privatuma-politika.html",
    "secure-n8n-on-a-vps.html": "lv/n8n-drosiba-vps.html",
    "n8n-queue-mode.html": "lv/n8n-rindas-rezims.html",
}
MENUS = re.compile(r'(<div\b[^>]*\bclass=["\'][^"\']*\blang-menu\b[^"\']*["\'][^>]*>)(.*?)(</div>)', re.I | re.S)
ANCHORS = re.compile(r'<a\b[^>]*>.*?</a>', re.I | re.S)
HEAD_LINKS = re.compile(r'<link\b[^>]*>', re.I | re.S)
HEAD_END = re.compile(r'</head\s*>', re.I)
JSONLD = re.compile(r'<script\b[^>]*\btype=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.I | re.S)

def attr(tag: str, name: str) -> str | None:
    m = re.search(r'\b' + re.escape(name) + r'\s*=\s*(["\'])(.*?)\1', tag, re.I | re.S)
    return m.group(2) if m else None

def verify_source() -> None:
    root = ET.parse(ROOT / "sitemap.xml")
    all_urls = [n.text for n in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc") if n.text]
    assert len(all_urls) == len(set(all_urls)), "Duplicate sitemap URLs"
    en_urls = {x for x in all_urls if x.startswith(BASE) and "/" not in x[len(BASE):]}
    lv_urls = {x for x in all_urls if x.startswith(BASE + "lv/")}
    expected_lv = {BASE + value for value in MATCHES.values()}
    assert len(en_urls) == len(lv_urls) == len(expected_lv) == 11, (len(en_urls), len(lv_urls), len(expected_lv))
    assert lv_urls == expected_lv, sorted(lv_urls ^ expected_lv)
    for item in expected_lv:
        rel = item[len(BASE):]
        file = ROOT / ("lv/index.html" if rel == "lv/" else rel)
        assert file.is_file(), str(file)
        html = file.read_text(encoding="utf-8")
        assert re.search(r'<html\b[^>]*\blang=["\']lv["\']', html), rel
        assert len(re.findall(r'<h1(?:\s|>)', html, re.I)) == 1, ("H1", rel)
        assert (BASE + rel) in html.split("</head>",1)[0], ("head URL", rel)
        for jsonld in JSONLD.findall(html):
            json.loads(jsonld)
    print(f"LV_SITEMAP_PASS english={len(en_urls)} latvian={len(lv_urls)} total={len(all_urls)}", flush=True)

def target_for(path: Path, first_menu: str) -> tuple[str, bool]:
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith("lv/"):
        return BASE + ("lv/" if rel == "lv/index.html" else rel), True
    en_option = next((a.group() for a in ANCHORS.finditer(first_menu) if attr(a.group(),"hreflang") == "en"), None)
    en_href = attr(en_option, "href") if en_option else None
    key = en_href[len(BASE):] if en_href and en_href.startswith(BASE) else None
    exact = key in MATCHES and (key not in ("", "index.html") or path.name == "index.html")
    return BASE + (MATCHES[key] if exact else "lv/"), bool(exact)

def inject_option(open_tag: str, inner: str, close_tag: str, target: str, is_lv: bool) -> str:
    filtered = ANCHORS.sub(
        lambda m: "" if attr(m.group(), "hreflang") == "lv" or attr(m.group(), "lang") == "lv" else m.group(),
        inner,
    ).rstrip()
    current = ' aria-current="page"' if is_lv else ""
    return open_tag + filtered + f'<a href="{target}" hreflang="lv" lang="lv"{current}>Latviešu</a>' + close_tag

def integrate(path: Path, original: str) -> tuple[str, int, bool, str | None]:
    menus = list(MENUS.finditer(original))
    if not menus:
        return original, 0, False, None
    target, exact = target_for(path, menus[0].group(2))
    is_lv = path.relative_to(ROOT).parts[0] == "lv"
    updated = MENUS.sub(
        lambda m: inject_option(m.group(1), m.group(2), m.group(3), target, is_lv), original
    )
    end = HEAD_END.search(updated)
    assert end, ("Missing </head>", path)
    head, rest = updated[:end.start()], updated[end.start():]
    head = HEAD_LINKS.sub(
        lambda m: "" if attr(m.group(), "hreflang") == "lv" else m.group(), head
    )
    if exact:
        head += f'<link rel="alternate" hreflang="lv" href="{target}"/>'
    return head + rest, len(menus), exact, target

def verify_page(path: Path, html: str, original: str, menus: int, exact: bool, target: str | None) -> None:
    if not menus:
        return
    found = list(MENUS.finditer(html))
    assert len(found) == menus, (path, "menu count")
    is_lv = path.relative_to(ROOT).parts[0] == "lv"
    for menu in found:
        links = [x.group() for x in ANCHORS.finditer(menu.group(2))]
        options = [a for a in links if attr(a,"hreflang") == "lv"]
        assert len(options) == 1 and links[-1] == options[0], (path, "latvian must be last once")
        assert attr(options[0], "href") == target, (path, "wrong Latvian destination")
        assert (attr(options[0], "aria-current") == "page") == is_lv, (path,"current item")
    if menus == 2:
        assert html.index('class="lang-menu"') < html.index("</header>"), path
        assert html.rfind('class="lang-menu"') > html.index("<footer"), path
    head = html.split("</head>",1)[0]
    lv_alts = [m.group() for m in HEAD_LINKS.finditer(head) if attr(m.group(),"hreflang") == "lv"]
    assert len(lv_alts) == (1 if exact else 0), (path,"alternate count")
    if exact:
        assert attr(lv_alts[0], "href") == target, (path,"alternate target")
    assert len(re.findall(r'<h1(?:\s|>)',html,re.I)) == len(re.findall(r'<h1(?:\s|>)',original,re.I)),(path,"H1 modified")
    for j in JSONLD.findall(html):
        json.loads(j)

def run(write: bool):
    verify_source()
    paths = sorted(path for path in ROOT.rglob("*.html") if ".git" not in path.parts)
    total = menus_total = exact_total = fallback_total = changed = no_menu = 0
    for path in paths:
        original = path.read_text(encoding="utf-8")
        transformed, count, exact, target = integrate(path, original)
        verify_page(path, transformed, original, count, exact, target)
        total += 1
        menus_total += count
        exact_total += int(exact and count > 0)
        fallback_total += int(not exact and count > 0)
        no_menu += int(count == 0)
        if transformed != original:
            if not write:
                raise AssertionError(f"Unpublished Latvian navigation in {path.relative_to(ROOT)}")
            path.write_text(transformed, encoding="utf-8")
            changed += 1
    assert total >= 480, total
    assert menus_total >= 940, menus_total
    assert exact_total >= 11, exact_total
    print(f"LV_GLOBAL_PASS html={total} menus={menus_total} exact={exact_total} fallback={fallback_total} no_menu={no_menu} changed={changed} write={write}", flush=True)

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    run(parser.parse_args().write)
