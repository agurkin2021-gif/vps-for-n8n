#!/usr/bin/env python3
"""Integrate Serbian in every existing language menu without modifying page content."""
from __future__ import annotations
from site_config import BASE_URL, iter_public_html

from collections import Counter
from html import unescape
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
BASE = BASE_URL
EN = ('index.html', 'best-vps-for-n8n.html', 'about.html',
      'n8n-backup-and-restore.html', 'contact.html',
      'install-n8n-on-a-vps.html', 'n8n-cloud-vs-self-hosted.html',
      'n8n-vps-requirements.html', 'privacy.html',
      'secure-n8n-on-a-vps.html', 'n8n-queue-mode.html')
EN_URLS = {BASE + ('' if f == 'index.html' else f): f for f in EN}
SR_URLS = {f: BASE + 'sr/' + ('' if f == 'index.html' else f) for f in EN}
MENU = re.compile(r'(<div\b[^>]*class=["\'][^"\']*\blang-menu\b[^"\']*["\'][^>]*>)([\s\S]*?)(</div>)', re.I)
ANCHOR = re.compile(r'<a\b[^>]*>[^<>]*</a>', re.I)
LINK = re.compile(r'<link\b[^>]*>', re.I)
ATTR = re.compile(r'([:\w-]+)\s*=\s*(["\'])(.*?)\2', re.S)


def attr(tag, name):
    return next((m.group(3) for m in ATTR.finditer(tag) if m.group(1).lower() == name), None)


def core_page(path, source):
    if path in EN:
        return path
    if path.startswith('sr/') and path[3:] in EN:
        return path[3:]
    for menu in MENU.finditer(source):
        for link in ANCHOR.finditer(menu.group(2)):
            if attr(link.group(), 'hreflang') == 'en':
                candidate = EN_URLS.get(attr(link.group(), 'href'))
                if candidate:
                    return candidate
    # Exact-named translated pages also retain the corresponding English page.
    tail = path.rsplit('/', 1)[-1]
    if tail in EN:
        return tail
    return None


def dest(page):
    return SR_URLS[page] if page else BASE + 'sr/'


def set_href(tag, url):
    if re.search(r'\bhref\s*=', tag, re.I):
        return re.sub(r'\bhref\s*=\s*(["\']).*?\1',
                      lambda m: 'href=' + m.group(1) + url + m.group(1),
                      tag, count=1, flags=re.I | re.S)
    return tag.replace('<link', '<link href="' + url + '"', 1)


def process(path, source):
    if path == '404.html' or 'lang-menu' not in source:
        return source, 0
    page = core_page(path, source)
    target = dest(page)
    current = path.startswith('sr/')
    anchor = ('<a href="' + target + '" hreflang="sr" lang="sr"' +
              (' aria-current="page"' if current else '') + '>Srpski</a>')

    def update_menu(m):
        opening, inner, closing = m.groups()
        # Remove only old Serbian selectors, then place one last in every menu.
        clean = ANCHOR.sub(lambda a: '' if (
            attr(a.group(), 'hreflang') == 'sr' or
            attr(a.group(), 'lang') == 'sr' or
            unescape(re.sub(r'<[^>]*>', '', a.group())).strip() == 'Srpski'
        ) else a.group(), inner)
        return opening + clean + anchor + closing

    out, menu_count = MENU.subn(update_menu, source)
    if not menu_count:
        return source, 0
    if '<footer' not in out.lower() or 'footer-lang-switch' not in out:
        raise AssertionError(path + ': language menu without expected footer selector')
    before_head, sep, rest = out.partition('</head>')
    if sep and page:
        def update_head_link(m):
            tag = m.group()
            return set_href(tag, target) if attr(tag, 'hreflang') == 'sr' else tag
        head = LINK.sub(update_head_link, before_head)
        if not any(attr(m.group(), 'hreflang') == 'sr' for m in LINK.finditer(head)):
            head += '<link rel="alternate" hreflang="sr" href="' + target + '"/>'
        out = head + sep + rest
    # No page content, scripts, CSS, images or other languages may be changed.
    original_main = re.search(r'<main\b[^>]*>[\s\S]*?</main>', source, re.I)
    final_main = re.search(r'<main\b[^>]*>[\s\S]*?</main>', out, re.I)
    if (original_main.group() if original_main else None) != (final_main.group() if final_main else None):
        raise AssertionError(path + ': main content changed')
    for tag in ('script', 'style'):
        regex = re.compile(r'<' + tag + r'\b[^>]*>[\s\S]*?</' + tag + r'>', re.I)
        if regex.findall(source) != regex.findall(out):
            raise AssertionError(path + ': ' + tag + ' content changed')
    return out, menu_count


def audit():
    sitemap = ET.parse(ROOT / 'sitemap.xml')
    urls = [n.text for n in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    if len([url for url in urls if url.startswith(BASE + 'sr/')]) != 11:
        raise AssertionError('Serbian sitemap must contain exactly 11 URLs')
    if not set(SR_URLS.values()).issubset(set(urls)):
        raise AssertionError('Missing Serbian sitemap entries')
    for en in EN:
        if not (ROOT / 'sr' / en).is_file():
            raise AssertionError('Serbian page missing: ' + en)
    pages = sorted(p for p in iter_public_html(ROOT) if '.git' not in p.parts and p.name != '404.html')
    total_pages = menu_pages = total_menus = changed_pages = missing = 0
    destinations = Counter()
    for p in pages:
        rel = p.relative_to(ROOT).as_posix()
        source = p.read_text(encoding='utf-8')
        after, menu_count = process(rel, source)
        total_pages += 1
        if menu_count:
            menu_pages += 1
            total_menus += menu_count
            target = dest(core_page(rel, source))
            for menu in MENU.finditer(after):
                entries = [a.group() for a in ANCHOR.finditer(menu.group(2))]
                sr = [a for a in entries if attr(a, 'hreflang') == 'sr']
                if len(sr) != 1 or attr(sr[0], 'href') != target or entries[-1] != sr[0]:
                    raise AssertionError(rel + ': Serbian selector is absent, duplicate, wrong or not last')
                destinations[target] += 1
            footer = after[after.lower().find('<footer'):]
            if not MENU.search(footer):
                raise AssertionError(rel + ': footer menu missing')
            if after != source:
                p.write_text(after, encoding='utf-8')
                changed_pages += 1
        elif 'footer-lang-switch' in source:
            missing += 1
    if missing:
        raise AssertionError(str(missing) + ' pages have a footer switch but no language menu')
    if total_menus < menu_pages or menu_pages < 11:
        raise AssertionError('Too few Serbian language selectors')
    print('SR_GLOBAL_QA_PASS english=11 serbian=11 site_pages=' + str(total_pages) +
          ' menu_pages=' + str(menu_pages) + ' selectors=' + str(total_menus) +
          ' changed=' + str(changed_pages) + ' destinations=' + str(len(destinations)), flush=True)


if __name__ == '__main__':
    audit()
