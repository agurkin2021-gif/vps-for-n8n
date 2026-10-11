#!/usr/bin/env python3
"""Integrate Hebrew in every existing language menu without modifying page content."""
from __future__ import annotations

from collections import Counter
from html import unescape
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
BASE = 'https://agurkin2021-gif.github.io/vps-for-n8n/'
EN = ('index.html', 'best-vps-for-n8n.html', 'about.html',
      'n8n-backup-and-restore.html', 'contact.html',
      'install-n8n-on-a-vps.html', 'n8n-cloud-vs-self-hosted.html',
      'n8n-vps-requirements.html', 'privacy.html',
      'secure-n8n-on-a-vps.html', 'n8n-queue-mode.html')
EN_URLS = {BASE + ('' if f == 'index.html' else f): f for f in EN}
SERBIAN_URLS = {BASE + 'sr/' + ('' if f == 'index.html' else f): f for f in EN}
HE_URLS = {f: BASE + 'he/' + ('' if f == 'index.html' else f) for f in EN}
MENU = re.compile(r'(<div\b[^>]*class=["\'][^"\']*\blang-menu\b[^"\']*["\'][^>]*>)([\s\S]*?)(</div>)', re.I)
ANCHOR = re.compile(r'<a\b[^>]*>[^<>]*</a>', re.I)
LINK = re.compile(r'<link\b[^>]*>', re.I)
ATTR = re.compile(r'([:\w-]+)\s*=\s*(["\'])(.*?)\2', re.S)


def attr(tag, name):
    return next((m.group(3) for m in ATTR.finditer(tag) if m.group(1).lower() == name), None)


def core_page(path, source):
    if path in EN:
        return path
    if path.startswith('he/') and path[3:] in EN:
        return path[3:]
    # Serbian selectors were verified site-wide earlier; prefer their exact
    # page mapping instead of guessing from translated URL slugs.
    for menu in MENU.finditer(source):
        for link in ANCHOR.finditer(menu.group(2)):
            if attr(link.group(), 'hreflang') == 'sr':
                candidate = SERBIAN_URLS.get(attr(link.group(), 'href'))
                if candidate:
                    return candidate
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
    return HE_URLS[page] if page else BASE + 'he/'


def set_href(tag, url):
    if re.search(r'\bhref\s*=', tag, re.I):
        return re.sub(r'\bhref\s*=\s*(["\']).*?\1',
                      lambda m: 'href=' + m.group(1) + url + m.group(1),
                      tag, count=1, flags=re.I | re.S)
    return tag.replace('<link', '<link href="' + url + '"', 1)


def normalize_hebrew_links(source):
    """Keep ordinary Hebrew internal navigation on its matching Hebrew page."""
    protected=[]
    def hide_menu(m):
        protected.append(m.group())
        return '<!--HE_LINK_MENU_'+str(len(protected)-1)+'-->'
    no_menus=MENU.sub(hide_menu,source)
    def update_anchor(m):
        tag=m.group()
        if attr(tag,'hreflang'):
            return tag
        href=attr(tag,'href')
        if not href:
            return tag
        bare, sep, hashpart=href.partition('#')
        fragment=sep+hashpart if sep else ''
        replacement=None
        if bare.startswith(BASE):
            tail=bare[len(BASE):]
            if tail=='':
                replacement=BASE+'he/'
            elif tail in EN:
                replacement=HE_URLS[tail]
        elif bare in ('../','../index.html'):
            replacement='./' if bare=='../' else 'index.html'
        elif bare.startswith('../') and bare[3:] in EN:
            replacement=bare[3:]
        if replacement is None:
            return tag
        return set_href(tag,replacement+fragment)
    preserved=re.split(r'(<(?:script|style)\b[^>]*>[\s\S]*?</(?:script|style)>)',no_menus,flags=re.I)
    for i,part in enumerate(preserved):
        if not re.match(r'<(?:script|style)\b',part,re.I):
            preserved[i]=re.sub(r'<a\b[^>]*>',update_anchor,part,flags=re.I)
    output=''.join(preserved)
    for i,menu in enumerate(protected):
        output=output.replace('<!--HE_LINK_MENU_'+str(i)+'-->',menu,1)
    if '<!--HE_LINK_MENU_' in output:
        raise AssertionError('Language menu placeholder leaked')
    return output


def process(path, source):
    if path == '404.html' or 'lang-menu' not in source:
        return source, 0
    page = core_page(path, source)
    target = dest(page)
    current = path.startswith('he/')
    anchor = ('<a href="' + target + '" hreflang="he" lang="he"' +
              (' aria-current="page"' if current else '') + '>עברית</a>')

    def update_menu(m):
        opening, inner, closing = m.groups()
        # Remove only old Hebrew selectors, then place one last in every menu.
        clean = ANCHOR.sub(lambda a: '' if (
            attr(a.group(), 'hreflang') == 'he' or
            attr(a.group(), 'lang') == 'he' or
            unescape(re.sub(r'<[^>]*>', '', a.group())).strip() == 'עברית'
        ) else a.group(), inner)
        return opening + clean + anchor + closing

    out, menu_count = MENU.subn(update_menu, source)
    if path.startswith('he/') and menu_count:
        out=normalize_hebrew_links(out)
    if not menu_count:
        return source, 0
    if menu_count != 2:
        raise AssertionError(path + ': expected header and footer language selectors')
    if '<footer' not in out.lower() or 'footer-lang-switch' not in out:
        raise AssertionError(path + ': language menu without expected footer selector')
    before_head, sep, rest = out.partition('</head>')
    if sep and page:
        def update_head_link(m):
            tag = m.group()
            return set_href(tag, target) if attr(tag, 'hreflang') == 'he' else tag
        head = LINK.sub(update_head_link, before_head)
        if not any(attr(m.group(), 'hreflang') == 'he' for m in LINK.finditer(head)):
            head += '<link rel="alternate" hreflang="he" href="' + target + '"/>'
        out = head + sep + rest
    # No page content, scripts, CSS, images or other languages may be changed.
    expected_main_source = normalize_hebrew_links(source) if path.startswith('he/') else source
    original_main = re.search(r'<main\b[^>]*>[\s\S]*?</main>', expected_main_source, re.I)
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
    english_urls = {BASE + ('' if f == 'index.html' else f) for f in EN}
    if not english_urls.issubset(set(urls)):
        raise AssertionError('English sitemap originals are missing')
    if len([url for url in urls if url.startswith(BASE + 'he/')]) != 11:
        raise AssertionError('Hebrew sitemap must contain exactly 11 URLs')
    if not set(HE_URLS.values()).issubset(set(urls)):
        raise AssertionError('Missing Hebrew sitemap entries')
    he_files=sorted((ROOT/'he').glob('*.html'))
    if len(he_files)!=11:
        raise AssertionError('Exactly 11 Hebrew HTML files expected, got '+str(len(he_files)))
    for en in EN:
        if not (ROOT / 'he' / en).is_file():
            raise AssertionError('Hebrew page missing: ' + en)
    pages = sorted(p for p in ROOT.rglob('*.html') if '.git' not in p.parts and p.name != '404.html')
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
                he = [a for a in entries if attr(a, 'hreflang') == 'he']
                if len(he) != 1 or attr(he[0], 'href') != target or entries[-1] != he[0]:
                    raise AssertionError(rel + ': Hebrew selector is absent, duplicate, wrong or not last')
                destinations[target] += 1
            footer = after[after.lower().find('<footer'):]
            if not MENU.search(footer):
                raise AssertionError(rel + ': footer menu missing')
            if after != source:
                p.write_text(after, encoding='utf-8')
                changed_pages += 1
            if core_page(rel,source) is not None:
                head=after.split('</head>',1)[0]
                matches=[x.group() for x in LINK.finditer(head) if attr(x.group(),'hreflang')=='he']
                if len(matches)!=1 or attr(matches[0],'href')!=target:
                    raise AssertionError(rel+': missing or incorrect Hebrew hreflang alternate')
            if rel.startswith('he/'):
                for link in ANCHOR.finditer(after):
                    href=attr(link.group(),'href') or ''
                    bare=href.split('#',1)[0]
                    if bare.startswith('../') and bare[3:] in EN:
                        raise AssertionError(rel+': leftover link to English '+href)
        elif 'footer-lang-switch' in source:
            missing += 1
    if missing:
        raise AssertionError(str(missing) + ' pages have a footer switch but no language menu')
    if total_menus != 2*menu_pages or menu_pages < 11:
        raise AssertionError('Too few Hebrew language selectors')
    print('HE_GLOBAL_QA_PASS english=11 hebrew=11 site_pages=' + str(total_pages) +
          ' menu_pages=' + str(menu_pages) + ' selectors=' + str(total_menus) +
          ' changed=' + str(changed_pages) + ' destinations=' + str(len(destinations)), flush=True)


if __name__ == '__main__':
    audit()
