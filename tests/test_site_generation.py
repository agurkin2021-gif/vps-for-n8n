"""Regression checks for sitemap generation and the build's failure boundary."""
import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from site_config import BASE_URL, LEGACY_SITE, ROOT, iter_public_html, regenerate_sitemap
from scripts.generate_sitemap import generate, NS
from scripts.validate_site import validate
from scripts.generate_hreflang import generate as generate_hreflang


class SitemapRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.page('index.html', BASE_URL, body='<a href="es/">Spanish</a>')
        self.page('es/index.html', BASE_URL+'es/', lang='es')
        self.hreflang_map = self.root/'hreflang-groups.json'
        self.hreflang_map.write_text(json.dumps({'version': 1, 'groups': [
            {'id': 'home', 'variants': {'en': '/', 'es': '/es/'}, 'x_default': 'en'}
        ]}), encoding='utf-8')
        (self.root/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+BASE_URL+'sitemap.xml\n', encoding='utf-8')

    def page(self, name, canonical=None, head='', body='', lang='en'):
        file = self.root/name
        file.parent.mkdir(parents=True, exist_ok=True)
        canonical = '' if canonical is None else f'<link rel="canonical" href="{canonical}">'
        file.write_text(f'<!doctype html><html lang="{lang}"><head>{canonical}{head}</head><body>{body}</body></html>', encoding='utf-8')
        return file

    def urls(self):
        return [n.text for n in ET.parse(self.root/'sitemap.xml').iter('{'+NS+'}loc')]

    def test_relative_scan_preserves_workflow_locale_paths(self):
        previous = Path.cwd()
        try:
            os.chdir(self.root)
            pages = list(iter_public_html(Path('.')))
            self.assertEqual(set(pages), {Path('index.html'), Path('es/index.html')})
        finally:
            os.chdir(previous)

    def test_inventory_excludes_redirects_noindex_verification_and_build_copies(self):
        self.page('404.html', head='<meta name="robots" content="noindex">')
        self.page('alias.html', head='<meta http-equiv="refresh" content="0;url=/">')
        self.page('private.html', head='<meta name="googlebot" content="none">')
        self.page('dist/incorrect.html')
        self.page('tests/fixture.html')
        self.page('nested/node_modules/incorrect.html')
        (self.root/'google123abc.html').write_text('google-site-verification: google123abc.html', encoding='utf-8')
        self.assertEqual(generate(self.root), 2)
        self.assertEqual(self.urls(), [BASE_URL, BASE_URL+'es/'])
        generate_hreflang(self.root, self.hreflang_map)
        report = validate(self.root, self.hreflang_map)
        self.assertEqual(report['broken_links'], 0)
        self.assertEqual(report['hreflang_errors'], 0)
        self.assertEqual(report['robots_errors'], 0)
        self.assertEqual(report['robots_checked_urls'], 3)
        self.assertEqual(report['robots_checked_agents'], ['*', 'Googlebot'])
        self.assertEqual(report['language_menu_errors'], 0)

    def test_regeneration_removes_legacy_duplicates_and_is_byte_stable(self):
        (self.root/'sitemap.xml').write_text(f'<urlset xmlns="{NS}"><url><loc>{LEGACY_SITE}/</loc></url><url><loc>{BASE_URL}</loc></url><url><loc>{BASE_URL}</loc></url></urlset>', encoding='utf-8')
        generate(self.root)
        first = (self.root/'sitemap.xml').read_bytes()
        # A second run must not even rewrite an unchanged file.
        with patch.object(Path, 'write_bytes', side_effect=AssertionError('Unchanged sitemap was rewritten')):
            self.assertEqual(generate(self.root), 2)
        self.assertEqual((self.root/'sitemap.xml').read_bytes(), first)
        self.assertEqual(generate(self.root, check=True), 2)

    def test_all_legacy_publish_wrappers_are_idempotent(self):
        # Execute only their sitemap entry points: no translation/network jobs.
        count = 0
        for file in ROOT.glob('*_publish_qa.py'):
            tree = ast.parse(file.read_text(encoding='utf-8-sig'))
            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and node.name == 'ensure_sitemap':
                    env = {'ROOT': self.root, 'regenerate_sitemap': regenerate_sitemap}
                    exec(compile(ast.Module(body=[node], type_ignores=[]), str(file), 'exec'), env)
                    with self.subTest(script=file.name):
                        env['ensure_sitemap']()
                        first = (self.root/'sitemap.xml').read_bytes()
                        env['ensure_sitemap']()
                        self.assertEqual((self.root/'sitemap.xml').read_bytes(), first)
                        self.assertEqual(self.urls(), [BASE_URL, BASE_URL+'es/'])
                    count += 1
        self.assertEqual(count, 21)

    def test_rejects_wrong_missing_and_duplicate_canonical_without_overwriting_sitemap(self):
        generate(self.root)
        before = (self.root/'sitemap.xml').read_bytes()
        for canonical, extra in [(LEGACY_SITE+'/', ''), (None, ''), (BASE_URL, '<link rel="canonical" href="'+BASE_URL+'">')]:
            with self.subTest(canonical=canonical, extra=extra):
                self.page('index.html', canonical, head=extra)
                with self.assertRaisesRegex(ValueError, 'canonical'):
                    generate(self.root)
                self.assertEqual((self.root/'sitemap.xml').read_bytes(), before)

    def test_rejects_legacy_links_even_with_correct_canonical(self):
        self.page('index.html', BASE_URL, body='<a href="'+LEGACY_SITE+'/es/">Spanish</a>')
        with self.assertRaisesRegex(ValueError, 'legacy'):
            generate(self.root)

    def test_check_rejects_missing_duplicate_and_foreign_sitemap_urls(self):
        for urls in [[BASE_URL], [BASE_URL, BASE_URL, BASE_URL+'es/'], [BASE_URL, LEGACY_SITE+'/es/']]:
            with self.subTest(urls=urls):
                content = f'<urlset xmlns="{NS}">'+''.join(f'<url><loc>{u}</loc></url>' for u in urls)+'</urlset>'
                (self.root/'sitemap.xml').write_text(content, encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'stale, unordered or duplicated'):
                    generate(self.root, check=True)

    def test_build_fails_before_replacing_existing_dist_on_invalid_source(self):
        generate(self.root)
        generate_hreflang(self.root, self.hreflang_map)
        sitemap = self.root/'sitemap.xml'
        valid_sitemap = sitemap.read_bytes()
        valid_home = (self.root/'index.html').read_bytes()
        valid_spanish = (self.root/'es/index.html').read_bytes()
        robots = self.root/'robots.txt'
        valid_robots = robots.read_bytes()
        for name in ['cloudflare-build.mjs', 'site_config.py', 'site-config.json']:
            shutil.copyfile(ROOT/name, self.root/name)
        (self.root/'scripts').mkdir()
        for name in ['generate_sitemap.py', 'generate_hreflang.py', 'validate_site.py', 'check_indexing_metadata.py', 'check_internal_links.py', 'check_robots.py', 'sync_language_menus.py']:
            shutil.copyfile(ROOT/'scripts'/name, self.root/'scripts'/name)
        (self.root/'dist').mkdir()
        sentinel = self.root/'dist'/'existing.txt'
        sentinel.write_text('existing build', encoding='utf-8')
        env = {**os.environ, 'PYTHON': sys.executable, 'PYTHONDONTWRITEBYTECODE': '1'}
        cases = [('sitemap', 'sitemap.xml is stale'), ('hreflang', 'Hreflang errors'),
                 ('language_menu', 'Language menu errors')]
        robots_cases = {
            'robots_all': 'User-agent: *\nDisallow: /\n',
            'robots_googlebot': 'User-agent: *\nAllow: /\nUser-agent: Googlebot\nDisallow: /\n',
            'robots_section': 'User-agent: *\nDisallow: /es/\n',
            'robots_sitemap': 'User-agent: *\nDisallow: /sitemap.xml$\n',
        }
        cases.extend((name, 'robots.txt blocks crawl access') for name in robots_cases)
        for broken, message in cases:
            with self.subTest(broken=broken):
                sitemap.write_bytes(valid_sitemap)
                (self.root/'index.html').write_bytes(valid_home)
                (self.root/'es/index.html').write_bytes(valid_spanish)
                robots.write_bytes(valid_robots)
                if broken == 'sitemap':
                    sitemap.write_text(sitemap.read_text(encoding='utf-8').replace(BASE_URL, LEGACY_SITE+'/'), encoding='utf-8')
                elif broken == 'hreflang':
                    self.page('es/index.html', BASE_URL+'es/', lang='es')  # Missing return/self links.
                elif broken == 'language_menu':
                    menu = '<div class="lang-menu"><a href="'+BASE_URL+'" hreflang="es">Spanish</a></div>'
                    (self.root/'index.html').write_bytes(valid_home.replace(b'</body>', menu.encode()+b'</body>'))
                else:
                    robots.write_text(robots_cases[broken]+'Sitemap: '+BASE_URL+'sitemap.xml\n', encoding='utf-8')
                result = subprocess.run(['node', str(self.root/'cloudflare-build.mjs')], cwd=self.root, env=env, capture_output=True, text=True, timeout=30)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stdout+result.stderr)
                self.assertEqual(sentinel.read_text(encoding='utf-8'), 'existing build')


if __name__ == '__main__':
    unittest.main()
