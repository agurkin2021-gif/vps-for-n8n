"""Functional regressions for language-menu topic links and safe regeneration."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from site_config import SITE, page_url
from scripts.sync_language_menus import check, generate


def menu(anchors):
    return ('<div class="lang-switch"><button type="button">Language</button>'
            '<div class="lang-menu">'+anchors+'</div></div>')


class LanguageMenuTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.map_path = self.root/'hreflang-groups.json'
        self.data = {'version': 1, 'groups': [
            {'id': 'home', 'variants': {'en': '/', 'es': '/es/', 'fr': '/fr/'}, 'x_default': 'en'},
            {'id': 'queue', 'variants': {'en': '/n8n-queue-mode.html', 'es': '/es/queue.html'}, 'x_default': 'en'},
        ]}
        for name, lang in [('index.html', 'en'), ('es/index.html', 'es'),
                           ('fr/index.html', 'fr'), ('n8n-queue-mode.html', 'en'),
                           ('es/queue.html', 'es')]:
            self.page(name, lang)
        self.save_map()

    def page(self, name, lang, *, body='', head=''):
        file = self.root/name
        file.parent.mkdir(parents=True, exist_ok=True)
        source = (f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8">'
                  f'<link rel="canonical" href="{page_url(name)}">{head}</head>'
                  f'<body>{body}</body></html>')
        file.write_bytes(source.encode('utf-8'))
        return file

    def save_map(self, data=None):
        self.map_path.write_text(json.dumps(self.data if data is None else data), encoding='utf-8')

    def snapshot(self):
        return {file.relative_to(self.root).as_posix(): file.read_bytes()
                for file in self.root.rglob('*.html')}

    def test_header_and_footer_links_choose_the_matching_article(self):
        old = menu(f'<a href="{SITE}/" hreflang="en">English</a>'
                   f'<a href="{SITE}/es/" hreflang="es">Español</a>'
                   f'<a href="{SITE}/fr/" hreflang="fr">Français</a>')
        desired = menu(f'<a href="{SITE}/n8n-queue-mode.html" hreflang="en">English</a>'
                       f'<a href="{SITE}/es/queue.html" hreflang="es">Español</a>'
                       f'<a href="{SITE}/fr/" hreflang="fr">Français</a>')
        file = self.page('n8n-queue-mode.html', 'en',
                         body='<header>'+old+'</header><main>Queue guide</main><footer>'+old+'</footer>')
        before = file.read_bytes()
        report = check(self.root, self.map_path)
        self.assertEqual(report['menu_count'], 2)
        self.assertEqual(report['menu_links'], 6)
        self.assertEqual(report['error_count'], 4)
        self.assertTrue(all(error['page'] == 'n8n-queue-mode.html' for error in report['errors']))
        self.assertTrue(all(error.get('kind') for error in report['errors']))
        result = generate(self.root, self.map_path)
        self.assertEqual(result['changed_files'], ['n8n-queue-mode.html'])
        self.assertEqual(file.read_bytes(), before.replace(old.encode('utf-8'), desired.encode('utf-8')))
        self.assertEqual(check(self.root, self.map_path)['error_count'], 0)

    def test_home_fallback_is_used_only_until_a_topic_translation_exists(self):
        file = self.page('n8n-queue-mode.html', 'en',
                         body=menu('<a hreflang="fr" href="/es/queue.html">Français</a>'))
        generate(self.root, self.map_path)
        self.assertIn(f'href="{SITE}/fr/"'.encode(), file.read_bytes())
        self.assertEqual(check(self.root, self.map_path)['error_count'], 0)
        self.page('fr/queue.html', 'fr')
        self.data['groups'][1]['variants']['fr'] = '/fr/queue.html'
        self.save_map()
        self.assertEqual(check(self.root, self.map_path)['error_count'], 1)
        generate(self.root, self.map_path)
        self.assertIn(f'href="{SITE}/fr/queue.html"'.encode(), file.read_bytes())
        self.assertNotIn(f'href="{SITE}/fr/"'.encode(), file.read_bytes())
        self.assertEqual(check(self.root, self.map_path)['error_count'], 0)

    def test_language_attributes_and_normalized_href_inference(self):
        old = ('<a href="es/index.html">Español</a>'
               '<a href="/queue-mode.html">English</a>'
               '<a lang="fr" href="/es/">Français</a>'
               '<a hreflang="es" lang="es" href="/">Explicit language</a>')
        desired = (f'<a href="{SITE}/es/queue.html">Español</a>'
                   '<a href="/queue-mode.html">English</a>'
                   f'<a lang="fr" href="{SITE}/fr/">Français</a>'
                   f'<a hreflang="es" lang="es" href="{SITE}/es/queue.html">Explicit language</a>')
        file = self.page('n8n-queue-mode.html', 'en', body=menu(old))
        before = file.read_bytes()
        generate(self.root, self.map_path)
        self.assertEqual(file.read_bytes(), before.replace(old.encode('utf-8'), desired.encode('utf-8')))
        report = check(self.root, self.map_path)
        self.assertEqual(report['menu_links'], 4)
        self.assertEqual(report['error_count'], 0)
        # Existing redirect/index variants with the correct topic stay intact.
        home = self.page('index.html', 'en', body=menu(
            '<a href="/es/index.html">Español</a><a lang="fr" href="/fr/">Français</a>'))
        unchanged = home.read_bytes()
        self.assertEqual(generate(self.root, self.map_path)['changed_files'], [])
        self.assertEqual(home.read_bytes(), unchanged)
        self.assertEqual(check(self.root, self.map_path)['error_count'], 0)

    def test_only_real_menu_href_changes_preserving_bom_crlf_labels_and_attributes(self):
        source = ('\ufeff<!doctype html>\r\n<html lang="en"><head>\r\n'
                  f'<link rel="canonical" href="{SITE}/n8n-queue-mode.html">\r\n'
                  '<style>.lang-menu { color: red; }</style></head><body>\r\n'
                  '<!-- <div class="lang-switch"><div class="lang-menu">'
                  '<a hreflang="unknown" href="/comment">Fake</a></div></div> -->\r\n'
                  '<script>const html = \'<div class="lang-switch"><div class="lang-menu">'
                  '<a hreflang="unknown" href="/script">Fake</a></div></div>\';</script>\r\n'
                  '<a hreflang="es" href="/es/">Ordinary link outside the menu</a>\r\n'
                  '<div class="lang-switch"><button>English</button><div class="lang-menu">\r\n'
                  '<A data-href="/unchanged" HREF = \'/es/\' hreflang="es" '
                  'title="A &amp; B" rel="alternate"><b>Español</b> &amp; más</A>\r\n'
                  '</div></div>\r\n</body></html>')
        file = self.root/'n8n-queue-mode.html'
        before = source.encode('utf-8')
        file.write_bytes(before)
        generate(self.root, self.map_path)
        expected = before.replace(b"HREF = '/es/'", f"HREF = '{SITE}/es/queue.html'".encode())
        self.assertEqual(file.read_bytes(), expected)
        report = check(self.root, self.map_path)
        self.assertEqual(report['menu_count'], 1)
        self.assertEqual(report['menu_links'], 1)
        self.assertEqual(report['error_count'], 0)

    def test_checker_never_writes_and_repeat_generation_is_byte_stable(self):
        self.page('n8n-queue-mode.html', 'en', body=menu('<a hreflang="es" href="/es/">Español</a>'))
        before = self.snapshot()
        with patch.object(Path, 'write_bytes', side_effect=AssertionError('Read-only check wrote a file')):
            self.assertGreater(check(self.root, self.map_path)['error_count'], 0)
        self.assertEqual(self.snapshot(), before)
        first = generate(self.root, self.map_path)
        self.assertEqual(first['changed_files'], ['n8n-queue-mode.html'])
        stable = self.snapshot()
        with patch.object(Path, 'write_bytes', side_effect=AssertionError('Unchanged HTML was rewritten')):
            repeated = generate(self.root, self.map_path)
        self.assertEqual(repeated['changed_files'], [])
        self.assertEqual(repeated['error_count'], 0)
        self.assertEqual(self.snapshot(), stable)

    def test_noindex_and_refresh_pages_are_skipped_without_modification(self):
        invalid_menu = menu('<a hreflang="unknown" href="/missing">Unresolved language</a>')
        self.page('404.html', 'en', head='<meta name="robots" content="noindex">', body=invalid_menu)
        self.page('old.html', 'en', head='<meta http-equiv="refresh" content="0;url=/">', body=invalid_menu)
        before = self.snapshot()
        report = check(self.root, self.map_path)
        self.assertEqual(report['error_count'], 0)
        self.assertEqual(report['menu_count'], 0)
        self.assertEqual(report['menu_links'], 0)
        self.assertEqual(generate(self.root, self.map_path)['changed_files'], [])
        self.assertEqual(self.snapshot(), before)

    def test_invalid_maps_fail_before_any_html_is_written(self):
        self.page('index.html', 'en', body=menu('<a hreflang="es" href="/wrong">Español</a>'))
        cases = []
        missing_target = copy.deepcopy(self.data)
        missing_target['groups'][1]['variants']['es'] = '/es/missing.html'
        cases.append(missing_target)
        unmapped_pages = copy.deepcopy(self.data)
        unmapped_pages['groups'].pop()
        cases.append(unmapped_pages)
        before = self.snapshot()
        for data in cases:
            with self.subTest(map=data):
                self.save_map(data)
                with patch.object(Path, 'write_bytes', side_effect=AssertionError('Invalid map wrote HTML')):
                    with self.assertRaises(ValueError):
                        generate(self.root, self.map_path)
                self.assertEqual(self.snapshot(), before)

    def test_unknown_or_ambiguous_menu_language_fails_before_any_write(self):
        self.page('index.html', 'en', body=menu('<a hreflang="es" href="/wrong">Español</a>'))
        cases = [
            '<a hreflang="xx" href="/es/">Unknown explicit language</a>',
            '<a href="/not-in-the-map/">Unknown destination</a>',
            '<a hreflang="es" hreflang="fr" href="/es/">Conflicting duplicate attribute</a>',
            '<a hreflang="es" lang="fr" href="/es/">Conflicting language attributes</a>',
        ]
        for anchor in cases:
            with self.subTest(anchor=anchor):
                self.page('n8n-queue-mode.html', 'en', body=menu(anchor))
                before = self.snapshot()
                with patch.object(Path, 'write_bytes', side_effect=AssertionError('Unknown language wrote HTML')):
                    with self.assertRaises(ValueError):
                        generate(self.root, self.map_path)
                self.assertEqual(self.snapshot(), before)

        # Multiple language codes are harmless when they share one target.
        self.data['groups'][0]['variants']['fr-FR'] = '/fr/'
        self.save_map()
        self.page('n8n-queue-mode.html', 'en', body=menu('<a href="/fr/">French fallback</a>'))
        self.assertEqual(generate(self.root, self.map_path)['changed_files'], ['index.html'])
        self.assertEqual(check(self.root, self.map_path)['error_count'], 0)

        # One homepage can represent a language and a region, while their
        # corresponding articles differ; its href alone cannot choose safely.
        self.page('index.html', 'en', body=menu('<a hreflang="es" href="/wrong">Spanish</a>'))
        self.data['groups'][1]['variants'].update({'fr': '/fr/queue.html', 'fr-FR': '/fr/france-queue.html'})
        self.page('fr/queue.html', 'fr')
        self.page('fr/france-queue.html', 'fr')
        self.save_map()
        self.page('n8n-queue-mode.html', 'en', body=menu('<a href="/fr/">Français</a>'))
        before = self.snapshot()
        with patch.object(Path, 'write_bytes', side_effect=AssertionError('Ambiguous language wrote HTML')):
            with self.assertRaises(ValueError):
                generate(self.root, self.map_path)
        self.assertEqual(self.snapshot(), before)


if __name__ == '__main__':
    unittest.main()
