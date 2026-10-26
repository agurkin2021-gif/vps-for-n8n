#!/usr/bin/env python3
"""Check statically declared HTML/CSS resources against the published inventory.

This is an offline reference checker, not a CSS validator or JavaScript runtime
analyzer. It follows stylesheets and CSS @imports, including conditional ones,
but does not evaluate JS, CSS variables, image-set strings or network resources.
"""
import argparse
import json
import posixpath
import re
import sys
from collections import deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from site_config import CONFIG, LEGACY_SITE, ROOT, SITE, iter_public_assets, iter_public_html, page_url

SPACE = ' \t\r\n\f'
HEX = frozenset('0123456789abcdefABCDEF')
UNRESERVED = frozenset('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~')
RESOURCE_RELS = {'stylesheet', 'icon', 'apple-touch-icon', 'apple-touch-icon-precomposed',
                 'mask-icon', 'preload', 'modulepreload'}


def css_escape(source, offset):
    """Read one CSS escape, including its optional hex-escape whitespace."""
    offset += 1
    if offset == len(source):
        return '', offset
    if source[offset] in '\r\n\f':
        end = offset + 1
        if source[offset:offset+2] == '\r\n':
            end += 1
        return '', end
    if source[offset] in HEX:
        end = offset
        while end < len(source) and end-offset < 6 and source[end] in HEX:
            end += 1
        value = int(source[offset:end], 16)
        character = chr(value) if 0 < value <= 0x10ffff and not 0xd800 <= value <= 0xdfff else '\ufffd'
        if end < len(source) and source[end] in SPACE:
            end += 2 if source[end:end+2] == '\r\n' else 1
        return character, end
    return source[offset], offset+1


def css_string(source, offset):
    quote, value = source[offset], []
    offset += 1
    while offset < len(source):
        character = source[offset]
        if character == quote:
            return ''.join(value), offset+1
        if character in '\r\n\f':
            return None, offset+1
        if character == '\\':
            character, offset = css_escape(source, offset)
        else:
            offset += 1
        value.append(character)
    return None, offset


def css_identifier(source, offset):
    value = []
    while offset < len(source):
        character = source[offset]
        if character == '\\':
            character, offset = css_escape(source, offset)
        elif character.isalnum() or character in '_-' or ord(character) >= 128:
            offset += 1
        else:
            break
        value.append(character)
    return ''.join(value), offset


def css_space(source, offset):
    while offset < len(source):
        if source[offset] in SPACE:
            offset += 1
        elif source.startswith('/*', offset):
            end = source.find('*/', offset+2)
            offset = len(source) if end < 0 else end+2
        else:
            break
    return offset


def css_url(source, offset):
    """Read a url() after the opening parenthesis; ignore malformed tokens."""
    offset = css_space(source, offset)
    if offset < len(source) and source[offset] in '\"\'':
        value, end = css_string(source, offset)
        end = css_space(source, end)
        return (value, end+1) if end < len(source) and source[end] == ')' else (None, end)
    value = []
    while offset < len(source):
        character = source[offset]
        if character == ')':
            return ''.join(value), offset+1
        if character in SPACE:
            end = css_space(source, offset)
            return (''.join(value), end+1) if end < len(source) and source[end] == ')' else (None, end)
        if character in '\"\'(' or ord(character) < 32:
            return None, offset+1
        if character == '\\':
            character, offset = css_escape(source, offset)
        else:
            offset += 1
        value.append(character)
    return None, offset


def css_references(source, first_line=1):
    """Yield (line, URL, is_stylesheet) without matching comments or strings."""
    offset = 0
    while offset < len(source):
        start = offset
        if source.startswith('/*', offset):
            offset = css_space(source, offset)
            continue
        if source[offset] in '\"\'':
            _, offset = css_string(source, offset)
            continue
        imported = source[offset] == '@'
        if imported:
            offset += 1
        name, end = css_identifier(source, offset)
        if not name:
            offset += 1
            continue
        offset = end
        if imported:
            if name.lower() != 'import':
                continue
            offset = css_space(source, offset)
            if offset < len(source) and source[offset] in '\"\'':
                value, offset = css_string(source, offset)
                if value is not None:
                    yield first_line+source.count('\n', 0, start), value, True
                continue
            name, offset = css_identifier(source, offset)
        if name.lower() == 'url':
            opening = css_space(source, offset)
            if opening < len(source) and source[opening] == '(':
                value, offset = css_url(source, opening+1)
                if value is not None:
                    yield first_line+source.count('\n', 0, start), value, imported


def srcset_urls(source):
    """Split srcset URL candidates without treating data-URL commas as delimiters."""
    offset = 0
    while offset < len(source):
        while offset < len(source) and source[offset] in SPACE+',':
            offset += 1
        start = offset
        while offset < len(source) and source[offset] not in SPACE:
            offset += 1
        value = source[start:offset]
        if not value:
            break
        if value.endswith(','):
            yield value.rstrip(',')
            continue
        yield value
        depth = 0
        while offset < len(source):
            character = source[offset]
            offset += 1
            if character == '(':
                depth += 1
            elif character == ')' and depth:
                depth -= 1
            elif character == ',' and not depth:
                break


class Resources(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.references = []
        self.inline_css = []
        self.base_href = None
        self.in_style = False
        self.template_depth = 0
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        # HTML keeps the first occurrence of a repeated attribute.
        attrs = dict(reversed(attrs))
        line = self.getpos()[0]
        if tag == 'template':
            self.template_depth += 1
        if tag == 'base' and not self.template_depth and 'href' in attrs and self.base_href is None:
            self.base_href = attrs['href'] or ''
        if tag == 'style':
            self.in_style = True
        if attrs.get('style'):
            self.inline_css.append((line, attrs['style']))
        if tag in ('img', 'script', 'source', 'video', 'audio', 'track', 'embed', 'iframe'):
            if attrs.get('src'):
                self.references.append((line, attrs['src'], False))
        if tag == 'input' and (attrs.get('type') or '').lower() == 'image' and attrs.get('src'):
            self.references.append((line, attrs['src'], False))
        if tag in ('img', 'source') and attrs.get('srcset'):
            self.references.extend((line, value, False) for value in srcset_urls(attrs['srcset']))
        if tag == 'video' and attrs.get('poster'):
            self.references.append((line, attrs['poster'], False))
        if tag == 'object' and attrs.get('data'):
            self.references.append((line, attrs['data'], False))
        if tag == 'link':
            rels = set((attrs.get('rel') or '').lower().split())
            if attrs.get('href') and rels & RESOURCE_RELS:
                css = 'stylesheet' in rels or 'preload' in rels and (attrs.get('as') or '').lower() == 'style'
                self.references.append((line, attrs['href'], css))
            if 'preload' in rels and attrs.get('imagesrcset'):
                self.references.extend((line, value, False) for value in srcset_urls(attrs['imagesrcset']))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == 'style':
            self.in_style = False
        elif tag == 'template' and self.template_depth:
            self.template_depth -= 1

    def handle_data(self, data):
        if self.in_style:
            self.inline_css.append((self.getpos()[0], data))


def check(root=ROOT, documents=None):
    root = Path(root).resolve()
    inventory = {file.relative_to(root).as_posix(): file for file in iter_public_assets(root)}
    host = urlsplit(SITE).hostname
    errors, destinations = [], set()
    pending, visited = deque(), set()
    references = source_files = 0

    def asset_path(path):
        decoded = unquote(path, errors='strict').replace('\\', '/')
        relative = posixpath.normpath('/'+decoded.lstrip('/')).lstrip('/')
        if not relative or decoded.endswith('/'):
            relative += '/index.html' if relative else 'index.html'
        return relative

    def routed_path(path):
        # ASSETS normalizes unreserved escapes before the Worker redirects.
        # Reserved escapes are decoded only when looking up the asset filename.
        path = re.sub(r'%([0-9a-fA-F]{2})',
                      lambda match: chr(int(match[1], 16)) if chr(int(match[1], 16)) in UNRESERVED else match[0], path)
        original = path
        legacy_prefix = urlsplit(LEGACY_SITE).path
        if path == legacy_prefix or path.startswith(legacy_prefix+'/'):
            path = path[len(legacy_prefix):] or '/'
        if path.endswith('/index.html'):
            path = path[:-10]
        path = CONFIG['redirects'].get(path, path)
        if not path.endswith('/') and '.' not in path.rsplit('/', 1)[-1]:
            directory = CONFIG['redirects'].get(path+'/', path+'/')
            if asset_path(directory) in inventory:
                path = directory
        # The Worker applies path redirects only when the target exists.
        if path != original and asset_path(path) not in inventory:
            path = original
        return asset_path(path)

    def consume(source, line, value, stylesheet, base):
        nonlocal references
        value = value.strip()
        if not value or value.startswith('#'):
            return
        try:
            url = urlsplit(urljoin(base, value))
            if url.scheme not in ('http', 'https') or url.hostname not in (host, 'www.'+host):
                return
            relative = routed_path(url.path)
        except (ValueError, UnicodeError) as exc:
            errors.append({'source': source, 'line': line, 'url': value,
                           'reason': 'invalid resource URL: '+str(exc)})
            return
        references += 1
        destinations.add(relative)
        if relative not in inventory:
            errors.append({'source': source, 'line': line, 'url': value,
                           'destination': '/'+relative, 'reason': 'not in published asset inventory'})
        elif stylesheet and relative not in visited:
            pending.append(relative)

    for file in iter_public_html(root):
        relative = file.relative_to(root).as_posix()
        document = documents.get(relative) if documents is not None else None
        source = document.source if document is not None else file.read_bytes().decode('utf-8-sig')
        parser = Resources(source.replace(LEGACY_SITE, SITE))
        base = page_url(relative)
        if parser.base_href is not None:
            try:
                base = urljoin(base, parser.base_href)
            except ValueError as exc:
                errors.append({'source': relative, 'line': 1, 'url': parser.base_href,
                               'reason': 'invalid base URL: '+str(exc)})
                continue
        source_files += 1
        for line, value, stylesheet in parser.references:
            consume(relative, line, value, stylesheet, base)
        for line, css in parser.inline_css:
            for reference in css_references(css, line):
                consume(relative, *reference, base)

    while pending:
        relative = pending.popleft()
        if relative in visited:
            continue
        visited.add(relative)
        source_files += 1
        try:
            css = inventory[relative].read_bytes().decode('utf-8-sig')
        except UnicodeError as exc:
            errors.append({'source': relative, 'line': 1, 'reason': 'stylesheet is not UTF-8: '+str(exc)})
            continue
        for reference in css_references(css):
            consume(relative, *reference, SITE+'/'+relative)

    return {'source_files': source_files, 'references': references, 'unique_assets': len(destinations),
            'error_count': len(errors), 'errors': errors}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    report = check(args.root)
    print(json.dumps({key: value for key, value in report.items() if key != 'errors'}))
    for error in report['errors'][:20]:
        print(json.dumps(error))
    raise SystemExit(bool(report['error_count']))
