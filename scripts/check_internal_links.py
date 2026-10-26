#!/usr/bin/env python3
"""Check anchor destinations against the files served by the Cloudflare Worker.

Run from any directory: python scripts/check_internal_links.py
Check the assembled assets: python scripts/check_internal_links.py --root dist
Canonical, hreflang metadata and image sources are separate audit concerns.
"""

import argparse
import json
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.parse import unquote, urljoin, urlsplit


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from site_config import SITE, LEGACY_SITE, iter_public_html
HOST = urlsplit(SITE).hostname


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for name, value in attrs:
                if name == 'href' and value is not None:
                    self.links.append((self.getpos()[0], value))

    handle_startendtag = handle_starttag


def check(root):
    root = root.resolve()

    @lru_cache(maxsize=None)
    def target_exists(url_path):
        destination = unquote(url_path).lstrip('/')
        if not destination or destination.endswith('/'):
            destination += 'index.html'
        target = (root / destination).resolve()
        return target.is_relative_to(root) and target.is_file()

    pages = list(iter_public_html(root))
    errors = []
    internal_count = 0
    targets = set()
    for page in pages:
        relative = page.relative_to(root).as_posix()
        path = relative[:-10] if page.name == 'index.html' else relative
        page_url = SITE + '/' + path
        parser = Links()
        # Match the existing Worker's transformation before resolving links.
        parser.feed(page.read_text(encoding='utf-8-sig').replace(LEGACY_SITE, SITE))
        for line, href in parser.links:
            url = urlsplit(urljoin(page_url, href))
            if url.scheme not in ('http', 'https') or url.hostname not in (HOST, 'www.'+HOST):
                continue
            internal_count += 1
            targets.add(url.path)
            if not target_exists(url.path):
                errors.append({'source': relative, 'line': line, 'href': href,
                               'destination': url.path, 'reason': 'missing file'})
    return {'root': str(root), 'html_files': len(pages), 'internal_links': internal_count,
            'unique_destinations': len(targets), 'broken_links': len(errors),
            'broken_destinations': len({e['destination'] for e in errors}), 'errors': errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--json', type=Path, help='Optional full machine-readable report')
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error('root must be an existing directory')
    result = check(args.root)
    if args.json:
        args.json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'errors'}))
    for error in result['errors'][:20]:
        print(json.dumps(error, ensure_ascii=True))
    if result['broken_links'] or not result['html_files']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
