#!/usr/bin/env python3
"""Fail the build if source URLs or indexing metadata have regressed."""
import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from site_config import ROOT
from scripts.generate_sitemap import generate
from scripts.check_internal_links import check as check_links
from scripts.check_indexing_metadata import check as check_metadata
from scripts.generate_hreflang import MAP_FILE, prepare, inspect as inspect_hreflang
from scripts.check_robots import check as check_robots
from scripts.sync_language_menus import MenuDocument, inspect as inspect_menus
from scripts.check_assets import check as check_assets
from scripts.check_crawl_reachability import check as check_reachability


def validate(root=ROOT, hreflang_map=MAP_FILE):
    root = Path(root).resolve()
    count = generate(root, check=True)
    robots = check_robots(root)
    if robots['errors']:
        raise ValueError('robots.txt blocks crawl access: '+json.dumps(robots['errors'][:10]))
    metadata = check_metadata(root)
    if metadata['errors']:
        raise ValueError('Indexing metadata errors: '+json.dumps(metadata['errors'][:10]))
    prepared = prepare(root, hreflang_map, document_class=MenuDocument)
    hreflang = inspect_hreflang(*prepared)
    if hreflang['errors']:
        raise ValueError('Hreflang errors: '+json.dumps(hreflang['errors'][:10]))
    menus = inspect_menus(*prepared)
    if menus['errors']:
        raise ValueError('Language menu errors: '+json.dumps(menus['errors'][:10]))
    links = check_links(root)
    if links['errors']:
        raise ValueError('Broken internal links: '+json.dumps(links['errors'][:10]))
    assets = check_assets(root, documents=prepared[0])
    if assets['errors']:
        raise ValueError('Missing or unpublished assets: '+json.dumps(assets['errors'][:10]))
    crawl = check_reachability(root, hreflang_map, prepared=prepared)
    if crawl['errors']:
        raise ValueError('Unreachable indexable pages: '+json.dumps(crawl['errors'][:10]))
    return {'sitemap_urls': count, 'html_files': links['html_files'],
            'internal_links': links['internal_links'], 'metadata_errors': 0, 'broken_links': 0,
            'robots_errors': 0, 'robots_checked_urls': robots['checked_urls'],
            'robots_checked_agents': robots['checked_agents'],
            'language_menus': menus['menu_count'], 'language_menu_links': menus['menu_links'],
            'language_menu_errors': 0,
            'asset_references': assets['references'], 'unique_assets': assets['unique_assets'],
            'asset_errors': 0, 'crawl_reachable_pages': crawl['global_reachable'],
            'crawl_locales_checked': crawl['locales_checked'], 'crawl_errors': 0,
            'hreflang_groups': hreflang['groups'],
            'hreflang_declarations': hreflang['hreflang_declarations'], 'hreflang_errors': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--hreflang-map', type=Path, default=MAP_FILE)
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.root, args.hreflang_map)))
    except (ValueError, OSError, ET.ParseError) as exc:
        print('Site validation failed: '+str(exc), file=sys.stderr)
        raise SystemExit(1)
