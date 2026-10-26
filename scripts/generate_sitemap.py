#!/usr/bin/env python3
"""Regenerate sitemap.xml from indexable canonical source pages, or --check it."""
import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from site_config import ROOT, LEGACY_SITE, iter_public_html, page_url
from scripts.check_indexing_metadata import Metadata

NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'


def collect_urls(root):
    root = Path(root).resolve()
    urls = []
    for file in iter_public_html(root):
        source = file.read_text(encoding='utf-8-sig')
        relative = file.relative_to(root).as_posix()
        # Google's verification payload is an asset, not a page to index.
        if re.fullmatch(r'google[0-9a-f]+\.html', file.name) and source.strip() == 'google-site-verification: '+file.name:
            continue
        data = Metadata()
        data.feed(source)
        if any(re.search(r'\b(?:noindex|none)\b', v, re.I) for v in data.robots):
            continue
        if data.refresh:
            continue
        expected = page_url(relative)
        if data.canonical != [(expected, True)]:
            raise ValueError(f'{relative}: canonical must be {expected}')
        if LEGACY_SITE in source:
            raise ValueError(f'{relative}: legacy GitHub Pages URL in source')
        urls.append(expected)
    if not urls:
        raise ValueError('Refusing to generate an empty sitemap')
    if len(urls) != len(set(urls)):
        raise ValueError('Source pages generate duplicate canonical URLs')
    return sorted(urls)


def render(urls):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<urlset xmlns="{NS}">\n'
            + ''.join(f'  <url><loc>{escape(url)}</loc></url>\n' for url in urls)
            + '</urlset>\n').encode('utf-8')


def generate(root=ROOT, check=False):
    root = Path(root).resolve()
    urls = collect_urls(root)
    path = root / 'sitemap.xml'
    output = render(urls)
    if check:
        tree = ET.parse(path).getroot()
        if tree.tag != '{'+NS+'}urlset':
            raise ValueError('sitemap.xml must be a sitemap urlset')
        existing = [n.text for n in tree.iter('{'+NS+'}loc')]
        if existing != urls:
            missing = set(urls)-set(existing)
            extra = set(existing)-set(urls)
            raise ValueError(f'sitemap.xml is stale, unordered or duplicated: missing={sorted(missing)}, extra={sorted(extra)}')
    elif not path.exists() or path.read_bytes() != output:
        temporary = path.with_suffix('.xml.tmp')
        temporary.write_bytes(output)
        temporary.replace(path)
    return len(urls)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    print(f'Sitemap {"checked" if args.check else "generated"}: {generate(args.root, args.check)} URLs')
