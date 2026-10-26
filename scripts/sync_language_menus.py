#!/usr/bin/env python3
"""Sync/check existing language-menu destinations against the hreflang map."""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from html import escape
from pathlib import Path
from urllib.parse import urljoin, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from site_config import CONFIG, ROOT, SITE, page_url
from scripts.generate_hreflang import Document, MAP_FILE, prepare

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
        'meta', 'param', 'source', 'track', 'wbr'}
ATTR = re.compile(r'''\s+([^\s=/>]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?''')


class MenuDocument(Document):
    def __init__(self, source):
        self.menu_stack = []
        self.menus = []
        super().__init__(source)

    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)
        values = dict(attrs)
        menu = self.menu_stack[-1][1] if self.menu_stack else None
        if 'lang-menu' in (values.get('class') or '').split():
            menu = len(self.menus)
            self.menus.append([])
        if tag == 'a' and menu is not None:
            raw = self.get_starttag_text()
            spans = [match.span(next(i for i in (2, 3, 4) if match.group(i) is not None))
                     for match in ATTR.finditer(raw)
                     if match.group(1).lower() == 'href' and any(match.group(i) is not None for i in (2, 3, 4))]
            duplicate = any(count > 1 for key, count in Counter(key for key, _ in attrs).items()
                            if key in ('href', 'hreflang', 'lang'))
            self.menus[menu].append({'attrs': values, 'span': spans[0] if len(spans) == 1 else None,
                                     'duplicate': duplicate, 'start': self.source_position(),
                                     'line': self.getpos()[0]})
        if tag not in VOID:
            self.menu_stack.append((tag, menu))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        super().handle_endtag(tag)
        for index in range(len(self.menu_stack)-1, -1, -1):
            if self.menu_stack[index][0] == tag:
                del self.menu_stack[index:]
                break


def normalized_url(href, relative):
    url = urlsplit(urljoin(page_url(relative), href or ''))
    if url.scheme not in ('http', 'https') or url.hostname not in (urlsplit(SITE).hostname, 'www.'+urlsplit(SITE).hostname):
        return None
    path = url.path
    if path.endswith('/index.html'):
        path = path[:-10]
    path = CONFIG['redirects'].get(path, path)
    return SITE+path


def analyze(documents, expected, owner, groups):
    home_page = next((relative for relative in expected if owner[relative] == 'home'), None)
    if home_page is None:
        raise ValueError('Language menus require a home group in the hreflang map')
    homes = {code.lower(): url for code, url in expected[home_page] if code != 'x-default'}
    languages = defaultdict(set)
    for alternatives in expected.values():
        for code, url in alternatives:
            if code != 'x-default':
                languages[url].add(code.lower())
    known_codes = set().union(*languages.values())
    errors, edits = [], defaultdict(list)
    menu_count = link_count = 0
    for relative in sorted(expected):
        document = documents[relative]
        variants = {code.lower(): url for code, url in expected[relative] if code != 'x-default'}
        menu_count += len(document.menus)

        def destination(code):
            if code not in known_codes:
                return None
            # A reviewed regional alias can use its generic-language variant.
            generic = code.split('-')[0]
            return variants.get(code) or variants.get(generic) or homes.get(code) or homes.get(generic)

        for menu_index, anchors in enumerate(document.menus):
            for anchor in anchors:
                link_count += 1
                attrs = anchor['attrs']
                href = attrs.get('href')
                actual = normalized_url(href, relative)
                code = (attrs.get('hreflang') or attrs.get('lang') or '').lower()
                candidates = {code} if code else languages.get(actual, set())
                targets = {destination(candidate) for candidate in candidates}
                kind = None
                if anchor['duplicate'] or anchor['span'] is None:
                    kind = 'invalid_attributes'
                elif attrs.get('hreflang') and attrs.get('lang') and attrs['hreflang'].lower() != attrs['lang'].lower():
                    kind = 'conflicting_languages'
                elif not candidates or None in targets:
                    kind = 'unknown_language'
                elif len(targets) != 1:
                    kind = 'ambiguous_language'
                target = next(iter(targets)) if len(targets) == 1 else None
                if kind is None and actual != target:
                    kind = 'target'
                    start, end = anchor['span']
                    edits[relative].append((anchor['start']+start, anchor['start']+end, escape(target, quote=True)))
                if kind:
                    errors.append({'page': relative, 'line': anchor['line'], 'menu': menu_index,
                                   'kind': kind, 'href': href, 'expected': target,
                                   'languages': sorted(candidates)})
    report = {'indexable_pages': len(expected), 'menu_count': menu_count, 'menu_links': link_count,
              'error_count': len(errors), 'errors': errors}
    return report, edits


def inspect(documents, expected, owner, groups):
    return analyze(documents, expected, owner, groups)[0]


def check(root=ROOT, map_path=MAP_FILE):
    return inspect(*prepare(root, map_path, document_class=MenuDocument))


def generate(root=ROOT, map_path=MAP_FILE):
    root = Path(root).resolve()
    prepared = prepare(root, map_path, document_class=MenuDocument)
    report, edits = analyze(*prepared)
    invalid = [error for error in report['errors'] if error['kind'] != 'target']
    if invalid:
        raise ValueError('Language menu errors: '+json.dumps(invalid[:10]))
    changed = []
    for relative, replacements in edits.items():
        source = prepared[0][relative].source
        for start, end, replacement in sorted(replacements, reverse=True):
            source = source[:start]+replacement+source[end:]
        changed.append((relative, source))
    # Validate the entire map and all menu languages before writing any page.
    for relative, source in changed:
        (root/relative).write_bytes(source.encode('utf-8'))
    return {**report, 'error_count': 0, 'errors': [], 'fixed_links': len(report['errors']),
            'changed_files': [relative for relative, _ in changed]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--map', dest='map_path', type=Path, default=MAP_FILE)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--json', type=Path)
    args = parser.parse_args()
    try:
        report = check(args.root, args.map_path) if args.check else generate(args.root, args.map_path)
    except (ValueError, OSError) as exc:
        print('Language menu validation failed: '+str(exc), file=sys.stderr)
        raise SystemExit(1)
    if args.json:
        args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key: len(value) if key == 'changed_files' else value
                      for key, value in report.items() if key != 'errors'}))
    for error in report.get('errors', [])[:10]:
        print(json.dumps(error))
    raise SystemExit(bool(report['error_count']))
