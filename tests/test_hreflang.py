"""Regression cases for topic equivalence, reciprocal links and safe regeneration."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from site_config import SITE, page_url
from scripts.generate_hreflang import Document, check, generate


def without_alternates(source):
    for start, end, _ in reversed(Document(source).spans):
        source = source[:start] + source[end:]
    return source


class HreflangRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.map_path = self.root/'hreflang-groups.json'
        self.data = {'version': 1, 'groups': [
            {'id': 'home', 'variants': {'en': '/', 'es': '/es/', 'it': '/it/vps-n8n/'}, 'x_default': 'en'},
            {'id': 'contact', 'variants': {'en': '/contact.html', 'es': '/es/contacto.html'}, 'x_default': 'en'},
        ]}
        for name, lang in [('index.html', 'en'), ('es/index.html', 'es'),
                           ('it/vps-n8n/index.html', 'it'), ('contact.html', 'en'),
                           ('es/contacto.html', 'es')]:
            self.page(name, lang)
        self.save_map()

    def page(self, name, lang, head='', body=''):
        file = self.root/name
        file.parent.mkdir(parents=True, exist_ok=True)
        source = (f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8">'
                  f'<link rel="canonical" href="{page_url(name)}">{head}</head>'
                  f'<body>{body}</body></html>')
        file.write_bytes(source.encode('utf-8'))
        return file

    def save_map(self, data=None):
        self.map_path.write_text(json.dumps(self.data if data is None else data), encoding='utf-8')

    def tags(self, name):
        document = Document((self.root/name).read_bytes().decode('utf-8'))
        self.assertTrue(all(in_head and rel == 'alternate' for _, _, in_head, rel in document.alternates))
        return dict((code, url) for code, url, _, _ in document.alternates)

    def test_complete_reciprocal_sets_stay_within_topics_and_available_translations(self):
        generate(self.root, self.map_path)
        contact = {'en': SITE+'/contact.html', 'es': SITE+'/es/contacto.html',
                   'x-default': SITE+'/contact.html'}
        self.assertEqual(self.tags('contact.html'), contact)
        self.assertEqual(self.tags('es/contacto.html'), contact)
        home = self.tags('index.html')
        self.assertEqual(self.tags('es/index.html'), home)
        self.assertEqual(self.tags('it/vps-n8n/index.html'), home)
        self.assertEqual(home['it'], SITE+'/it/vps-n8n/')
        self.assertNotIn('it', contact)  # No Italian contact page exists.
        self.assertEqual(check(self.root, self.map_path)['error_count'], 0)

    def test_regional_alias_and_single_language_page_need_no_unrelated_fallback(self):
        self.page('fr/france.html', 'fr')
        self.page('de/germany.html', 'de')
        self.page('fr/budget.html', 'fr')
        self.data['groups'].extend([
            {'id': 'regional', 'variants': {'fr': '/fr/france.html', 'fr-FR': '/fr/france.html', 'de': '/de/germany.html'}},
            {'id': 'budget', 'variants': {'fr': '/fr/budget.html'}},
        ])
        self.save_map()
        generate(self.root, self.map_path)
        regional = self.tags('fr/france.html')
        self.assertEqual(regional, self.tags('de/germany.html'))
        self.assertEqual(regional['fr'], regional['fr-FR'])
        self.assertNotIn('x-default', regional)
        self.assertEqual(self.tags('fr/budget.html'), {'fr': SITE+'/fr/budget.html'})
        self.assertEqual(check(self.root, self.map_path)['error_count'], 0)

    def test_bad_links_duplicates_and_body_placement_are_detected_and_repaired(self):
        generate(self.root, self.map_path)
        stale = ('<link rel="alternate" hreflang="en" href="https://old.example/contact.html">'
                 '<link rel="alternate" hreflang="en" href="/missing.html">'
                 '<link rel="stylesheet" hreflang="es" href="/es/">')
        self.page('contact.html', 'en', head=stale,
                  body='<link rel="alternate" hreflang="it" href="/it/">')
        errors = check(self.root, self.map_path)['errors']
        self.assertEqual({e['kind'] for e in errors}, {'duplicate_language', 'placement_or_rel', 'alternate_set'})
        generate(self.root, self.map_path)
        self.assertEqual(check(self.root, self.map_path)['error_count'], 0)
        self.assertEqual(self.tags('contact.html')['es'], SITE+'/es/contacto.html')

    def test_missing_return_link_or_self_link_fails_check_without_repairing_source(self):
        generate(self.root, self.map_path)
        file = self.root/'es/contacto.html'
        valid = file.read_bytes()
        for code in ('en', 'es'):
            with self.subTest(removed_language=code):
                source = valid.decode('utf-8')
                doc = Document(source)
                index = next(i for i, tag in enumerate(doc.alternates) if tag[0] == code)
                start, end, _ = doc.spans[index]
                damaged = (source[:start]+source[end:]).encode('utf-8')
                file.write_bytes(damaged)
                report = check(self.root, self.map_path)
                self.assertEqual(report['error_count'], 1)
                self.assertEqual(report['errors'][0]['page'], 'es/contacto.html')
                self.assertEqual(file.read_bytes(), damaged)

    def test_noindex_and_redirect_pages_lose_alternates_but_keep_their_fallback_links(self):
        stale = f'<link rel="alternate" hreflang="en" href="{SITE}/">'
        for name, directive in [('404.html', '<meta name="robots" content="noindex">'),
                                ('it/index.html', '<meta http-equiv="refresh" content="0;url=/it/vps-n8n/">')]:
            self.page(name, 'en', head=directive+stale, body='<a href="/">Back</a>')
        (self.root/'google123abc.html').write_text('google-site-verification: google123abc.html', encoding='utf-8')
        before = {f: f.read_bytes().decode('utf-8') for f in self.root.rglob('*.html')}
        generate(self.root, self.map_path)
        for file, source in before.items():
            self.assertEqual(without_alternates(file.read_bytes().decode('utf-8')), without_alternates(source))
        self.assertEqual(self.tags('404.html'), {})
        self.assertEqual(self.tags('it/index.html'), {})
        self.assertEqual(check(self.root, self.map_path)['indexable_pages'], 5)

    def test_only_real_link_tags_change_with_bom_crlf_comments_and_script_text(self):
        source = ('\ufeff<!doctype html>\r\n<html lang="en"><head>\r\n'
                  f'<link rel="canonical" href="{SITE}/">\r\n'
                  '<!-- <link rel="alternate" hreflang="de" href="/fake"> -->\r\n'
                  '<script>const text = \'<link hreflang="es" href="/fake">\';</script>\r\n'
                  '<LINK REL="alternate" HREF="/bad" HREFLANG="en" />\r\n'
                  '<title>Title &amp; text</title></head><body>\r\n'
                  '<a hreflang="es" href="/es/">Español</a>\r\n</body></html>')
        file = self.root/'index.html'
        file.write_bytes(source.encode('utf-8'))
        generate(self.root, self.map_path)
        after = file.read_bytes().decode('utf-8')
        self.assertEqual(without_alternates(after), without_alternates(source))
        self.assertEqual(check(self.root, self.map_path)['error_count'], 0)

    def test_repeat_generation_does_not_write_unchanged_files(self):
        generate(self.root, self.map_path)
        before = {file: file.read_bytes() for file in self.root.rglob('*.html')}
        with patch.object(Path, 'write_bytes', side_effect=AssertionError('Unexpected rewrite')):
            self.assertEqual(generate(self.root, self.map_path)['changed_files'], [])
        self.assertEqual({file: file.read_bytes() for file in before}, before)

    def test_invalid_maps_fail_before_any_html_is_written(self):
        self.page('it/index.html', 'it', head='<meta http-equiv="refresh" content="0;url=/it/vps-n8n/">')
        cases = []
        for path in ['/missing.html', '/es/index.html', '/it/', '//other.example/', '/es/?preview=1']:
            data = copy.deepcopy(self.data)
            data['groups'][0]['variants']['es'] = path
            cases.append(data)
        data = copy.deepcopy(self.data)
        data['groups'][0]['variants']['de'] = data['groups'][0]['variants'].pop('es')
        cases.append(data)  # Wrong HTML language.
        data = copy.deepcopy(self.data)
        del data['groups'][1]
        cases.append(data)  # Unmapped indexable pages.
        data = copy.deepcopy(self.data)
        data['groups'][1]['variants']['en'] = '/'
        cases.append(data)  # One page claimed by two topics.
        data = copy.deepcopy(self.data)
        data['groups'][1]['x_default'] = 'it'
        cases.append(data)  # Fallback is not a translation of this article.
        data = copy.deepcopy(self.data)
        data['groups'][0]['variants']['EN'] = '/'
        cases.append(data)  # Case-insensitive duplicate language.
        before = {f: f.read_bytes() for f in self.root.rglob('*.html')}
        for number, data in enumerate(cases):
            with self.subTest(case=number):
                self.save_map(data)
                with patch.object(Path, 'write_bytes', side_effect=AssertionError('Invalid map wrote HTML')):
                    with self.assertRaises(ValueError):
                        generate(self.root, self.map_path)
                self.assertEqual({f: f.read_bytes() for f in before}, before)

    def test_duplicate_json_key_is_rejected(self):
        self.map_path.write_text('{"version":1,"version":1,"groups":[]}', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Duplicate key'):
            generate(self.root, self.map_path)

    def test_specific_language_regions_cannot_be_swapped(self):
        self.page('zh-tw/index.html', 'zh-TW')
        self.data['groups'][0]['variants']['zh-CN'] = '/zh-tw/'
        self.save_map()
        with self.assertRaisesRegex(ValueError, 'does not match'):
            generate(self.root, self.map_path)


if __name__ == '__main__':
    unittest.main()
