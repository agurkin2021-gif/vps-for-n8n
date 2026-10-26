#!/usr/bin/env python3
"""Require ordinary links from the main homepage and within each language."""
import argparse
import json
import re
import sys
from collections import deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from site_config import CONFIG, ROOT, SITE, page_url
from scripts.generate_hreflang import MAP_FILE, prepare

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
        'meta', 'param', 'source', 'track', 'wbr'}
INERT = {'script', 'style', 'template', 'textarea', 'title', 'xmp', 'iframe', 'noembed', 'noframes'}


class CrawlLinks(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.base = None
        self.links = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        # Browsers use the first occurrence of an attribute.
        attrs = dict(reversed(attrs))
        inert = any(item[0] in INERT for item in self.stack)
        menu = bool({'lang-menu', 'lang-switch'} & set((attrs.get('class') or '').split()))
        menu = menu or any(item[1] for item in self.stack)
        if not inert:
            if tag == 'base' and 'href' in attrs and self.base is None:
                self.base = attrs['href'] or ''
            if (tag == 'a' and attrs.get('href') is not None
                    and not any(item[0] == 'head' for item in self.stack)
                    and 'nofollow' not in (attrs.get('rel') or '').lower().split()):
                self.links.append((attrs['href'], menu))
        if tag not in VOID:
            self.stack.append((tag, menu))

    def handle_endtag(self, tag):
        for index in range(len(self.stack)-1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)


def canonical_target(href, base, indexed):
    try:
        target = urlsplit(urljoin(base, href.strip()))
        origin = urlsplit(SITE)
        if (target.scheme not in {'http', 'https'}
                or target.hostname not in {origin.hostname, 'www.'+origin.hostname}
                or target.username is not None or target.password is not None
                or target.port not in {None, 80 if target.scheme == 'http' else 443}):
            return None
    except ValueError:
        return None
    # ASSETS redirects percent-encoded unreserved characters to their literal
    # form, after which the Worker applies its normal redirect rules.
    def unreserved(match):
        character = chr(int(match.group()[1:], 16))
        return character if character in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~' else match.group()
    path = re.sub(r'%[0-9a-fA-F]{2}', unreserved, target.path) or '/'
    # Match the Worker's legacy-prefix, index and configured alias redirects.
    legacy = urlsplit(CONFIG['legacyBase']).path.rstrip('/')
    if path == legacy or path.startswith(legacy+'/'):
        path = path[len(legacy):] or '/'
    if path.endswith('/index.html'):
        path = path[:-10]
    path = CONFIG['redirects'].get(path, path)
    if not path.endswith('/') and '.' not in path.rsplit('/', 1)[-1]:
        directory = CONFIG['redirects'].get(path+'/', path+'/')
        if SITE+unquote(directory) in indexed:
            path = directory
    # Resolve encoded filenames only after applying the path redirect rules.
    path = unquote(path)
    return SITE+path if SITE+path in indexed else None


def reachable(start, graph, allowed):
    seen = {start} & allowed
    pending = deque(seen)
    while pending:
        for target in graph.get(pending.popleft(), set()):
            if target in allowed and target not in seen:
                seen.add(target)
                pending.append(target)
    return seen


def check(root=ROOT, map_path=MAP_FILE, prepared=None):
    documents, expected, _, _ = prepared if prepared is not None else prepare(root, map_path)
    indexed = {page_url(relative): relative for relative in expected}
    graph = {url: set() for url in indexed}
    local_graph = {url: set() for url in indexed}
    for url, relative in indexed.items():
        document = documents[relative]
        if any(re.search(r'\b(?:nofollow|none)\b', value, re.I) for value in document.robots):
            continue
        parsed = CrawlLinks(document.source)
        base = urljoin(url, parsed.base) if parsed.base is not None else url
        for href, menu in parsed.links:
            target = canonical_target(href, base, indexed)
            if target:
                graph[url].add(target)
                if not menu:
                    local_graph[url].add(target)

    # The root page's reviewed equivalence group defines locale homepages.
    # Shared regional codes (e.g. fr/fr-FR) must not duplicate a homepage check.
    homes_by_code = {code.lower(): url for code, url in expected.get('index.html', [])
                     if code != 'x-default'}
    homes = {url: set() for url in homes_by_code.values()}
    errors = []
    if SITE+'/' not in indexed or not homes:
        errors.append({'kind': 'missing_homepage', 'url': SITE+'/'})
    for url, relative in indexed.items():
        codes = {code.lower() for code, member in expected[relative]
                 if member == url and code != 'x-default'}
        candidates = {homes_by_code[code] for code in codes if code in homes_by_code}
        if not candidates:
            # A region-specific article can use its generic-language homepage.
            candidates = {homes_by_code[code.split('-')[0]] for code in codes
                          if code.split('-')[0] in homes_by_code}
        if not candidates:
            errors.append({'kind': 'missing_language_homepage', 'url': url,
                           'language': documents[relative].lang})
        for home in candidates:
            homes[home].add(url)

    globally_reached = reachable(SITE+'/', graph, set(indexed))
    global_orphans = sorted(set(indexed)-globally_reached)
    errors.extend({'kind': 'globally_unreachable', 'url': url} for url in global_orphans)
    local_orphans = []
    for home, members in sorted(homes.items()):
        language = documents[indexed[home]].lang
        reached = reachable(home, local_graph, members)
        for url in sorted(members-reached):
            row = {'language': language, 'url': url}
            local_orphans.append(row)
            errors.append({'kind': 'locally_unreachable', **row, 'homepage': home})
    return {'indexed_pages': len(indexed), 'global_reachable': len(globally_reached),
            'locales_checked': len(homes), 'global_orphans': global_orphans,
            'local_orphans': local_orphans, 'error_count': len(errors), 'errors': errors}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--map', dest='map_path', type=Path, default=MAP_FILE)
    args = parser.parse_args()
    try:
        report = check(args.root, args.map_path)
    except (ValueError, OSError) as exc:
        print('Crawl reachability validation failed: '+str(exc), file=sys.stderr)
        raise SystemExit(1)
    print(json.dumps(report))
    raise SystemExit(bool(report['error_count']))
