#!/usr/bin/env python3
"""Generate/check reciprocal hreflang from the reviewed page-equivalence map."""
import argparse
import json
import re
import sys
from collections import Counter
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from site_config import ROOT, SITE, iter_public_html, page_url
from scripts.check_indexing_metadata import Metadata

MAP_FILE = ROOT / 'hreflang-groups.json'
LANGUAGE = re.compile(r'^[a-z]{2}(?:-[A-Za-z]{4})?(?:-[A-Za-z]{2})?$', re.I)


class Document(Metadata):
    """Keep exact source spans so generation changes only real hreflang tags."""
    def __init__(self, source):
        super().__init__()
        self.source = source
        self.line_offsets = [0] + [m.end() for m in re.finditer('\n', source)]
        self.lang = None
        self.head_count = 0
        self.head_end = None
        self.alternates = []
        self.spans = []
        self.feed(source)

    def source_position(self):
        line, column = self.getpos()
        return self.line_offsets[line-1] + column

    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)
        attrs = dict(attrs)
        if tag == 'html':
            self.lang = attrs.get('lang')
        if tag == 'head':
            self.head_count += 1
        if tag == 'link' and 'hreflang' in attrs:
            self.alternates.append((attrs.get('hreflang') or '', attrs.get('href'),
                                    self.in_head, (attrs.get('rel') or '').lower()))
            start = self.source_position()
            self.spans.append((start, start+len(self.get_starttag_text()), self.in_head))

    handle_startendtag = handle_starttag

    def handle_endtag(self, tag):
        if tag == 'head':
            self.head_end = self.source_position()
        super().handle_endtag(tag)

    @property
    def excluded(self):
        return bool(self.refresh) or any(re.search(r'\b(?:noindex|none)\b', v, re.I) for v in self.robots)


def language_matches(code, document_language):
    if not document_language:
        return False
    code, actual = code.lower().split('-'), document_language.lower().split('-')
    return code[0] == actual[0] and (len(code) == 1 or len(actual) == 1 or code == actual)


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate key in hreflang map: {key}')
        result[key] = value
    return result


def prepare(root=ROOT, map_path=MAP_FILE):
    root = Path(root).resolve()
    data = json.loads(Path(map_path).read_text(encoding='utf-8'), object_pairs_hook=unique_keys)
    if data.get('version') != 1 or not isinstance(data.get('groups'), list) or not data['groups']:
        raise ValueError('Expected version 1 and a nonempty groups list in the hreflang map')
    documents, indexed = {}, {}
    for file in iter_public_html(root):
        source = file.read_bytes().decode('utf-8')
        relative = file.relative_to(root).as_posix()
        if re.fullmatch(r'google[0-9a-f]+\.html', file.name) and source.strip() == 'google-site-verification: '+file.name:
            continue
        document = Document(source)
        documents[relative] = document
        if document.excluded:
            continue
        url = page_url(relative)
        if document.head_count != 1 or document.head_end is None:
            raise ValueError(f'{relative}: expected one complete head element')
        if document.canonical != [(url, True)]:
            raise ValueError(f'{relative}: expected canonical {url}')
        if not document.lang or not LANGUAGE.fullmatch(document.lang):
            raise ValueError(f'{relative}: missing or unsupported HTML language syntax')
        indexed[url] = relative

    expected, owner, group_ids = {}, {}, set()
    for group in data['groups']:
        group_id = group.get('id')
        variants = group.get('variants')
        if not isinstance(group_id, str) or not group_id or group_id in group_ids:
            raise ValueError('Hreflang groups must have unique nonempty IDs')
        group_ids.add(group_id)
        if not isinstance(variants, dict) or not variants:
            raise ValueError(f'{group_id}: expected a nonempty variants object')
        members, tags, codes = set(), [], set()
        for code, path in sorted(variants.items(), key=lambda item: (item[0] != 'en', item[0].lower())):
            if not LANGUAGE.fullmatch(code) or code.lower() in codes:
                raise ValueError(f'{group_id}: invalid or repeated language {code}')
            codes.add(code.lower())
            if not isinstance(path, str) or not path.startswith('/') or path.startswith('//') or '?' in path or '#' in path:
                raise ValueError(f'{group_id}: expected a root-relative canonical path, got {path}')
            url = SITE + path
            if url not in indexed:
                raise ValueError(f'{group_id}: target is missing, noncanonical or not indexable: {url}')
            relative = indexed[url]
            if not language_matches(code, documents[relative].lang):
                raise ValueError(f'{group_id}: {code} does not match {relative} HTML language {documents[relative].lang}')
            if relative in owner and owner[relative] != group_id:
                raise ValueError(f'{relative}: page occurs in different hreflang groups')
            owner[relative] = group_id
            members.add(relative)
            tags.append((code, url))
        if 'x_default' in group:
            fallback = group['x_default']
            if fallback not in variants:
                raise ValueError(f'{group_id}: x_default must name a language in this group')
            tags.append(('x-default', SITE+variants[fallback]))
        for relative in members:
            expected[relative] = tags
    missing = set(indexed.values()) - set(expected)
    if missing:
        raise ValueError('Indexable pages missing from hreflang map: '+', '.join(sorted(missing)))
    return documents, expected, owner, len(group_ids)


def inspect(documents, expected, owner, groups):
    errors, total = [], 0
    for relative, document in documents.items():
        desired = {(code.lower(), url) for code, url in expected.get(relative, [])}
        actual = [(code.lower(), url) for code, url, _, _ in document.alternates]
        total += len(actual)
        duplicate_codes = [code for code, count in Counter(code for code, _ in actual).items() if count > 1]
        if duplicate_codes:
            errors.append({'page': relative, 'kind': 'duplicate_language', 'languages': duplicate_codes})
        if any(not in_head or rel != 'alternate' for _, _, in_head, rel in document.alternates):
            errors.append({'page': relative, 'kind': 'placement_or_rel'})
        if set(actual) != desired:
            # Matching the complete group also guarantees self and return links.
            errors.append({'page': relative, 'kind': 'alternate_set', 'group': owner.get(relative),
                           'missing': sorted(desired-set(actual)),
                           'unexpected': sorted(set(actual)-desired, key=lambda item: (item[0], item[1] or ''))})
    return {'html_files': len(documents), 'indexable_pages': len(expected), 'groups': groups,
            'hreflang_declarations': total, 'error_count': len(errors),
            'errors_by_kind': dict(Counter(e['kind'] for e in errors)), 'errors': errors}


def check(root=ROOT, map_path=MAP_FILE):
    return inspect(*prepare(root, map_path))


def rewrite(document, variants):
    # A compact block preserves every byte outside the original link tags and
    # remains byte-stable on repeat runs (no accumulating separator whitespace).
    block = ''.join(f'<link rel="alternate" hreflang="{code}" href="{escape(url, quote=True)}">'
                    for code, url in variants)
    edits, inserted = [], False
    for start, end, in_head in document.spans:
        replacement = block if in_head and not inserted else ''
        inserted = inserted or in_head
        edits.append((start, end, replacement))
    if block and not inserted:
        edits.append((document.head_end, document.head_end, block))
    result, offset = [], 0
    for start, end, replacement in sorted(edits):
        result.extend([document.source[offset:start], replacement])
        offset = end
    result.append(document.source[offset:])
    return ''.join(result)


def generate(root=ROOT, map_path=MAP_FILE):
    root = Path(root).resolve()
    documents, expected, owner, groups = prepare(root, map_path)
    changes = []
    for relative, document in documents.items():
        result = rewrite(document, expected.get(relative, []))
        if result != document.source:
            changes.append((relative, result))
    # Invalid maps/targets fail above, before touching any source file.
    for relative, result in changes:
        (root/relative).write_bytes(result.encode('utf-8'))
    return {'indexable_pages': len(expected), 'groups': groups,
            'changed_files': [relative for relative, _ in changes]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--map', dest='map_path', type=Path, default=MAP_FILE)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--json', type=Path)
    args = parser.parse_args()
    try:
        report = check(args.root, args.map_path) if args.check else generate(args.root, args.map_path)
    except (ValueError, OSError) as exc:
        print('Hreflang validation failed: '+str(exc), file=sys.stderr)
        raise SystemExit(1)
    if args.json:
        args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({key:(len(value) if key == 'changed_files' else value)
                      for key, value in report.items() if key != 'errors'}))
    for error in report.get('errors', [])[:10]:
        print(error['page']+': '+error['kind'])
    if report.get('error_count'):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
