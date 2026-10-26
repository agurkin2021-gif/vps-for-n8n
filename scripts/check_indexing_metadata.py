#!/usr/bin/env python3
"""Verify page identity for every sitemap URL, as served by the current Worker.

Usage: python scripts/check_indexing_metadata.py [--root dist] [--json report.json]
Only page identity is checked; Organization/WebSite IDs and parent breadcrumbs
may legitimately point at other URLs. Missing optional metadata is not an error.
"""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urldefrag, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from site_config import LEGACY_SITE, SITE


class Metadata(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_head = False
        self.canonical = []
        self.og_url = []
        self.robots = []
        self.refresh = []
        self.schemas = []
        self.schema_text = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'head':
            self.in_head = True
        if tag == 'link' and 'canonical' in (attrs.get('rel') or '').lower().split():
            self.canonical.append((attrs.get('href'), self.in_head))
        if tag == 'meta':
            if (attrs.get('http-equiv') or '').lower() == 'refresh':
                self.refresh.append(attrs.get('content') or '')
            if (attrs.get('property') or '').lower() == 'og:url':
                self.og_url.append((attrs.get('content'), self.in_head))
            if (attrs.get('name') or '').lower() in ('robots', 'googlebot'):
                self.robots.append(attrs.get('content') or '')
        if tag == 'script' and (attrs.get('type') or '').lower() == 'application/ld+json':
            self.schema_text = []

    handle_startendtag = handle_starttag

    def handle_endtag(self, tag):
        if tag == 'head':
            self.in_head = False
        if tag == 'script' and self.schema_text is not None:
            self.schemas.append(''.join(self.schema_text))
            self.schema_text = None

    def handle_data(self, data):
        if self.schema_text is not None:
            self.schema_text.append(data)


def page_references(value, pointer='$'):
    """Yield only structured-data references identifying the current page."""
    if isinstance(value, list):
        for index, child in enumerate(value):
            yield from page_references(child, f'{pointer}[{index}]')
    elif isinstance(value, dict):
        types = value.get('@type', [])
        if isinstance(types, str):
            types = [types]
        if 'BreadcrumbList' in types and value.get('itemListElement'):
            elements = value['itemListElement']
            last_index = max(range(len(elements)), key=lambda i: elements[i].get('position', 0))
            item = elements[last_index].get('item')
            item_pointer = f'{pointer}.itemListElement[{last_index}].item'
            if isinstance(item, dict):
                for key in ('@id', 'url'):
                    if key in item:
                        yield item_pointer+'.'+key, item[key]
            elif item is not None:
                yield item_pointer, item
        if 'WebPage' in types:
            for key in ('url', '@id'):
                if key in value:
                    yield pointer+'.'+key, value[key]
        for key, child in value.items():
            if isinstance(child, (dict, list)):
                yield from page_references(child, pointer+'.'+key)


def check(root):
    root = root.resolve()
    sitemap = ET.parse(root / 'sitemap.xml')
    urls = [n.text for n in sitemap.getroot().iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    errors = []
    totals = Counter()

    def error(page, kind, actual, expected):
        errors.append({'page': page, 'kind': kind, 'actual': actual, 'expected': expected})

    if len(urls) != len(set(urls)):
        error('sitemap.xml', 'duplicate_sitemap_urls', len(urls), len(set(urls)))
    for url in urls:
        parsed = urlsplit(url)
        if not url.startswith(SITE+'/') or parsed.query or parsed.fragment:
            error('sitemap.xml', 'sitemap_url', url, SITE+'/<page>')
            continue
        relative = unquote(parsed.path).lstrip('/')
        if not relative or relative.endswith('/'):
            relative += 'index.html'
        file = (root / relative).resolve()
        if not file.is_relative_to(root) or not file.is_file():
            error(url, 'missing_file', relative, 'existing HTML file')
            continue
        data = Metadata()
        data.feed(file.read_text(encoding='utf-8-sig').replace(LEGACY_SITE, SITE))
        totals['html_files'] += 1
        if data.canonical != [(url, True)]:
            error(relative, 'canonical', data.canonical, [(url, True)])
        if data.og_url:
            totals['pages_with_og_url'] += 1
            if data.og_url != [(url, True)]:
                error(relative, 'og_url', data.og_url, [(url, True)])
        if any(re.search(r'\b(?:noindex|none)\b', value, re.I) for value in data.robots):
            error(relative, 'noindex', data.robots, 'indexable sitemap page')
        for index, source in enumerate(data.schemas):
            totals['json_ld_blocks'] += 1
            try:
                schema = json.loads(source)
            except ValueError as exc:
                error(relative, 'invalid_json_ld', str(exc), 'valid JSON')
                continue
            for pointer, target in page_references(schema):
                totals['json_ld_page_references'] += 1
                if not isinstance(target, str) or urldefrag(target)[0] != url:
                    error(relative, 'json_ld_page_url', {'block': index, 'pointer': pointer, 'url': target}, url)
    return {'root': str(root), 'sitemap_urls': len(urls), **totals,
            'error_count': len(errors), 'errors_by_kind': dict(Counter(e['kind'] for e in errors)), 'errors': errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--json', type=Path)
    args = parser.parse_args()
    result = check(args.root)
    if args.json:
        args.json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k != 'errors'}))
    for error in result['errors'][:35]:
        print(json.dumps(error))
    if result['error_count'] or not result['sitemap_urls']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
