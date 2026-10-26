"""Functional checks for global discovery and navigation within each language."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from site_config import SITE, page_url
from scripts.check_crawl_reachability import check
from scripts.generate_hreflang import prepare


class CrawlReachabilityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.map_path = self.root/'hreflang-groups.json'
        self.data = {'version': 1, 'groups': [
            {'id': 'home', 'variants': {'en': '/', 'es': '/es/', 'fr': '/fr/'}, 'x_default': 'en'},
            {'id': 'queue', 'variants': {
                'en': '/n8n-queue-mode.html', 'es': '/es/guide.html', 'fr': '/fr/guide.html'},
             'x_default': 'en'},
        ]}
        self.language_menu = ('<div class="lang-switch"><div class="lang-menu">'
                              '<a href="/es/">Spanish</a><a href="/fr/">French</a></div></div>')
        self.page('index.html', 'en', body=self.language_menu+'<a href="/n8n-queue-mode.html">Queue</a>')
        self.page('n8n-queue-mode.html', 'en')
        self.page('es/index.html', 'es', body='<a href="guide.html">Guide</a>')
        self.page('es/guide.html', 'es')
        self.page('fr/index.html', 'fr', body='<a href="guide.html">Guide</a>')
        self.page('fr/guide.html', 'fr')
        self.save_map()

    def page(self, name, lang, *, body='', head=''):
        file = self.root/name
        file.parent.mkdir(parents=True, exist_ok=True)
        source = (f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8">'
                  f'<link rel="canonical" href="{page_url(name)}">{head}</head>'
                  f'<body>{body}</body></html>')
        file.write_bytes(source.encode('utf-8'))
        return file

    def save_map(self):
        self.map_path.write_text(json.dumps(self.data), encoding='utf-8')

    def run_check(self):
        return check(self.root, self.map_path)

    def assert_clean(self, report, *, pages=6, locales=3):
        self.assertEqual(report['indexed_pages'], pages)
        self.assertEqual(report['global_reachable'], pages)
        self.assertEqual(report['locales_checked'], locales)
        self.assertEqual(report['global_orphans'], [])
        self.assertEqual(report['local_orphans'], [])
        self.assertEqual(report['error_count'], 0)
        self.assertEqual(report['errors'], [])

    def assert_orphan(self, report, path, language):
        self.assertIn(SITE+path, report['global_orphans'])
        self.assertIn((language, SITE+path),
                      {(row['language'], row['url']) for row in report['local_orphans']})
        self.assertGreater(report['error_count'], 0)
        self.assertTrue(report['errors'])

    def test_head_hreflang_is_not_an_incoming_crawl_link(self):
        self.assert_clean(self.run_check())
        self.page('index.html', 'en', body=self.language_menu,
                  head=f'<link rel="alternate" hreflang="en" href="{SITE}/n8n-queue-mode.html">')
        report = self.run_check()
        self.assertEqual(report['global_reachable'], 5)
        self.assertEqual(report['global_orphans'], [SITE+'/n8n-queue-mode.html'])
        self.assert_orphan(report, '/n8n-queue-mode.html', 'en')

    def test_comments_scripts_templates_and_non_anchor_controls_do_not_connect_pages(self):
        fake_links = (
            '<!-- <a href="guide.html">Comment</a> -->'
            '<script>const markup = \'<a href="guide.html">Script</a>\';</script>'
            '<template><div><a href="guide.html">Template</a></div></template>'
            '<textarea><a href="guide.html">Text only</a></textarea>'
            '<iframe><a href="guide.html">Fallback text</a></iframe>'
            '<button onclick="location.href=\'guide.html\'">Button</button>'
            '<div data-href="guide.html">Data attribute</div>'
            '<a data-href="guide.html">Anchor without href</a>')
        self.page('es/index.html', 'es', body=fake_links)
        report = self.run_check()
        self.assertEqual(report['global_orphans'], [SITE+'/es/guide.html'])
        self.assert_orphan(report, '/es/guide.html', 'es')
        # A real anchor after the closed template must remain visible to BFS.
        self.page('es/index.html', 'es', body=fake_links+'<a href="guide.html">Real link</a>')
        self.assert_clean(self.run_check())

    def test_isolated_cycle_has_incoming_links_but_is_still_unreachable(self):
        self.data['groups'].extend([
            {'id': 'orphan-one', 'variants': {'en': '/orphan-one.html'}},
            {'id': 'orphan-two', 'variants': {'en': '/orphan-two.html'}},
        ])
        self.page('orphan-one.html', 'en', body='<a href="orphan-two.html">Second</a>')
        self.page('orphan-two.html', 'en', body='<a href="orphan-one.html">First</a>')
        self.save_map()
        report = self.run_check()
        self.assertEqual(report['indexed_pages'], 8)
        self.assertEqual(report['global_reachable'], 6)
        self.assertEqual(set(report['global_orphans']), {SITE+'/orphan-one.html', SITE+'/orphan-two.html'})
        self.assert_orphan(report, '/orphan-one.html', 'en')
        self.assert_orphan(report, '/orphan-two.html', 'en')

    def test_language_menu_reaches_globally_but_does_not_replace_local_navigation(self):
        for class_name in ('lang-switch', 'lang-menu'):
            with self.subTest(class_name=class_name):
                self.page('es/index.html', 'es', body=(
                    f'<div class="{class_name}"><span><a href="guide.html">Spanish guide</a></span></div>'))
                report = self.run_check()
                self.assertEqual(report['global_reachable'], 6)
                self.assertEqual(report['global_orphans'], [])
                self.assertEqual(report['local_orphans'], [{'language': 'es', 'url': SITE+'/es/guide.html'}])
                self.assertGreater(report['error_count'], 0)
        # A detour through another language is also insufficient locally.
        self.page('es/index.html', 'es', body='<a href="/fr/guide.html">French guide</a>')
        self.page('fr/guide.html', 'fr', body='<a href="/es/guide.html">Spanish guide</a>')
        report = self.run_check()
        self.assertEqual(report['global_orphans'], [])
        self.assertEqual(report['local_orphans'], [{'language': 'es', 'url': SITE+'/es/guide.html'}])

    def test_local_chains_redirect_aliases_index_queries_and_fragments_are_crawlable(self):
        self.data['groups'].append({'id': 'details', 'variants': {'es': '/es/details.html'}})
        self.data['groups'][0]['variants']['it'] = '/it/vps-n8n/'
        self.save_map()
        self.page('es/details.html', 'es')
        self.page('it/vps-n8n/index.html', 'it')
        self.page('index.html', 'en', body=(
            '<div class="lang-menu"><a href="/es/index.html?from=menu#top">Spanish</a>'
            '<a href="/fr/index.html">French</a><a href="/it?from=menu">Italian directory alias</a></div>'
            '<a href="/queue-mode.html?campaign=test#queue">Queue alias</a>'))
        self.page('es/index.html', 'es', body='<a href="guide.html?view=full#intro">Guide</a>')
        self.page('es/guide.html', 'es', body='<a href="./details.html?x=1&amp;y=2#section">Details</a>')
        self.assert_clean(self.run_check(), pages=8, locales=4)
        # Public ASSETS normalizes this encoding with a 307 before the
        # Worker's regular alias redirect reaches the canonical article.
        home = self.root/'index.html'
        home.write_bytes(home.read_bytes().replace(
            b'/queue-mode.html?campaign=test', b'/%71ueue-mode.html?campaign=test'))
        self.assert_clean(self.run_check(), pages=8, locales=4)

    def test_rel_nofollow_and_page_robots_nofollow_are_not_guaranteed_crawl_edges(self):
        cases = [
            ('', '<a href="guide.html" rel="ugc NOFOLLOW sponsored">Not followed</a>'),
            ('<meta name="robots" content="index, nofollow">', '<a href="guide.html">Link</a>'),
            ('<meta name="googlebot" content="nofollow">', '<a href="guide.html">Link</a>'),
        ]
        for head, body in cases:
            with self.subTest(head=head, body=body):
                self.page('es/index.html', 'es', head=head, body=body)
                report = self.run_check()
                self.assertEqual(report['indexed_pages'], 6)
                self.assert_orphan(report, '/es/guide.html', 'es')
        self.page('es/index.html', 'es', body='<a href="guide.html" rel="alternate">Followed</a>')
        self.assert_clean(self.run_check())

    def test_noindex_and_refresh_pages_cannot_be_the_only_bridge(self):
        for directive in ('<meta name="robots" content="noindex, follow">',
                          '<meta name="robots" content="none">',
                          '<meta http-equiv="refresh" content="0;url=guide.html">'):
            with self.subTest(directive=directive):
                self.page('es/index.html', 'es', body='<a href="bridge.html">Bridge</a>')
                self.page('es/bridge.html', 'es', head=directive, body='<a href="guide.html">Guide</a>')
                report = self.run_check()
                self.assertEqual(report['indexed_pages'], 6)
                self.assertEqual(report['global_orphans'], [SITE+'/es/guide.html'])
                self.assert_orphan(report, '/es/guide.html', 'es')
        self.page('es/index.html', 'es', body='<a href="guide.html">Direct link</a>')
        self.assert_clean(self.run_check())

    def test_external_hosts_and_first_base_href_use_browser_resolution(self):
        cases = [
            ('', '<a href="https://outside.invalid/es/guide.html">External</a>'),
            ('', '<a href="//outside.invalid/es/guide.html">External</a>'),
            ('', '<a href="https://vpsforn8n.com.outside.invalid/es/guide.html">Lookalike</a>'),
            ('<base href="https://outside.invalid/es/">', '<a href="guide.html">Relative external</a>'),
        ]
        for head, body in cases:
            with self.subTest(head=head, body=body):
                self.page('es/index.html', 'es', head=head, body=body)
                self.assert_orphan(self.run_check(), '/es/guide.html', 'es')
        self.page('es/index.html', 'es',
                  head='<base href="https://outside.invalid/es/">',
                  body=f'<a href="{SITE}/es/guide.html">Absolute internal</a>')
        self.assert_clean(self.run_check())
        self.page('es/index.html', 'es',
                  head=f'<base href="{SITE}/es/"><base href="https://outside.invalid/">',
                  body='<a href="guide.html">First base wins</a>')
        self.assert_clean(self.run_check())

    def test_shared_regional_home_aliases_are_checked_once_and_cover_regional_articles(self):
        self.data['groups'][0]['variants']['fr-FR'] = '/fr/'
        self.data['groups'][1]['variants']['fr-FR'] = '/fr/guide.html'
        self.data['groups'].append({'id': 'regional', 'variants': {'fr-FR': '/fr/regional.html'}})
        self.page('fr/regional.html', 'fr-FR')
        self.page('fr/index.html', 'fr', body=(
            '<a href="guide.html">Generic guide</a><a href="regional.html">Regional guide</a>'))
        self.save_map()
        self.assert_clean(self.run_check(), pages=7, locales=3)
        self.page('fr/index.html', 'fr', body='<a href="guide.html">Generic guide</a>')
        report = self.run_check()
        self.assertEqual(report['locales_checked'], 3)
        self.assertEqual(report['global_orphans'], [SITE+'/fr/regional.html'])
        self.assertEqual(len(report['local_orphans']), 1)
        self.assertEqual(report['local_orphans'][0]['url'], SITE+'/fr/regional.html')

    def test_prepared_inventory_is_reused_and_check_never_writes(self):
        prepared = prepare(self.root, self.map_path)
        before = {file.relative_to(self.root).as_posix(): file.read_bytes()
                  for file in self.root.rglob('*') if file.is_file()}
        with patch.object(Path, 'write_bytes', side_effect=AssertionError('Checker wrote bytes')), \
                patch.object(Path, 'write_text', side_effect=AssertionError('Checker wrote text')):
            direct = self.run_check()
            with patch('scripts.check_crawl_reachability.prepare', side_effect=AssertionError('Prepared inventory was reread')):
                reused = check(self.root, self.map_path, prepared=prepared)
        self.assert_clean(direct)
        self.assertEqual(reused, direct)
        after = {file.relative_to(self.root).as_posix(): file.read_bytes()
                 for file in self.root.rglob('*') if file.is_file()}
        self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
