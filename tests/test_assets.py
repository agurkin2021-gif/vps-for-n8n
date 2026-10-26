"""Offline, functional tests of declared-resource and publication checks."""
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from site_config import LEGACY_SITE, SITE
from scripts.check_assets import check


class AssetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, text=''):
        file = self.root/name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text, encoding='utf-8')
        return file

    def assert_destinations(self, report, expected):
        self.assertEqual(report['error_count'], len(expected), report)
        self.assertEqual({error.get('destination') for error in report['errors']}, set(expected))

    def test_existing_local_resources_query_fragments_and_legacy_html_urls(self):
        self.write('index.html', f'''<link rel="stylesheet" href="/styles.css?v=2">
            <link rel="shortcut icon" href="{SITE}/favicon.svg#icon">
            <img src="{LEGACY_SITE}/favicon.svg"><img src="//www.vpsforn8n.com/favicon.svg">
            <link rel="canonical" href="/not-an-asset"><a href="/ordinary-link">Link</a>''')
        self.write('styles.css', 'body { background: url("favicon.svg#background"); }')
        self.write('favicon.svg', '<svg/>')
        report = check(self.root)
        self.assertEqual(report['error_count'], 0, report)
        self.assertEqual(report['source_files'], 2)
        self.assertEqual(report['references'], 5)
        self.assertEqual(report['unique_assets'], 2)

    def test_missing_img_script_and_link_resources_are_reported(self):
        self.write('index.html', '''<img src="missing.svg"><script src="missing.js"></script>
            <link rel="stylesheet" href="missing.css"><link rel="icon" href="icon.svg">
            <link rel="preload" as="font" href="font.woff2">''')
        report = check(self.root)
        self.assert_destinations(report, ['/missing.svg', '/missing.js', '/missing.css', '/icon.svg', '/font.woff2'])
        self.assertTrue(all(error['source'] == 'index.html' and error['line'] >= 1 for error in report['errors']))

    def test_exists_but_excluded_extension_and_directory_still_fail(self):
        self.write('index.html', '<script src="app.js"></script><img src="scripts/hidden.svg"><img src="dist/copy.svg">')
        self.write('app.js', 'console.log("not published")')
        self.write('scripts/hidden.svg', '<svg/>')
        self.write('dist/copy.svg', '<svg/>')
        self.assert_destinations(check(self.root), ['/app.js', '/scripts/hidden.svg', '/dist/copy.svg'])

    def test_inventory_paths_are_case_sensitive_even_on_windows(self):
        self.write('index.html', '<img src="Logo.svg"><img src="logo.svg"><img src="Images/icon.svg">')
        self.write('Logo.svg', '<svg/>')
        self.write('images/icon.svg', '<svg/>')
        self.assert_destinations(check(self.root), ['/logo.svg', '/Images/icon.svg'])

    def test_srcset_candidates_and_data_url_commas_are_parsed(self):
        self.write('index.html', '''<picture><source srcset="data:image/png;base64,AAAA 1x, /missing-wide.svg 2x">
            <img src="ok.svg" srcset="ok.svg 1x, missing.svg 2x"></picture>
            <link rel="preload" as="image" href="ok.svg" imagesrcset="ok.svg 1x, large.svg 2x">
            <link rel="preload" as="image" imagesrcset="ok.svg 1x, huge.svg 2x">''')
        self.write('ok.svg', '<svg/>')
        self.assert_destinations(check(self.root), ['/missing-wide.svg', '/missing.svg', '/large.svg', '/huge.svg'])

    def test_relative_resources_respect_first_base_and_css_own_location(self):
        self.write('nested/page.html', '''<base href="/assets/"><base href="/wrong/">
            <img src="logo.svg"><link rel="stylesheet" href="css/site.css">
            <style>.hero { background: url(logo.svg) }</style>''')
        self.write('assets/logo.svg', '<svg/>')
        self.write('assets/css/site.css', '.hero { background: url(../logo.svg) }')
        self.assertEqual(check(self.root)['error_count'], 0)
        self.write('assets/css/site.css', '.hero { background: url(logo.svg) }')
        self.assert_destinations(check(self.root), ['/assets/css/logo.svg'])

    def test_external_base_external_urls_data_and_fragments_do_not_use_network(self):
        self.write('index.html', f'''<base href="https://cdn.example.test/assets/">
            <img src="remote.svg"><link rel="stylesheet" href="remote.css">
            <img src="data:image/svg+xml,%3Csvg/%3E"><img src="#symbol">
            <script src="//example.test/app.js"></script><img src="{SITE}/local.svg">
            <style>a {{ background:url(https://elsewhere.test/a.svg) }}</style>''')
        self.write('local.svg', '<svg/>')
        with patch('urllib.request.urlopen', side_effect=AssertionError('Network access')):
            report = check(self.root)
        self.assertEqual(report['error_count'], 0, report)
        self.assertEqual(report['references'], 1)

    def test_percent_decoding_and_relative_parent_paths(self):
        self.write('nested/page.html', '<img src="../images/caf%C3%A9%20icon.svg?x=1#symbol"><img src="../images/%6dissing.svg">')
        self.write('images/café icon.svg', '<svg/>')
        self.assert_destinations(check(self.root), ['/images/missing.svg'])

    def test_worker_directory_aliases_index_and_unreserved_escape_redirects(self):
        self.write('index.html', '''<iframe src="/it"></iframe><iframe src="/it/index.html"></iframe>
            <iframe src="/%71ueue-mode.html"></iframe><img src="/vps-for-n8n/logo.svg">''')
        self.write('it/vps-n8n/index.html', '<p>Italian content</p>')
        self.write('n8n-queue-mode.html', '<p>Queue guide</p>')
        self.write('logo.svg', '<svg/>')
        report = check(self.root)
        self.assertEqual(report['error_count'], 0, report)
        self.assertEqual(report['unique_assets'], 3)

    def test_first_duplicate_attribute_and_active_base_match_browser(self):
        self.write('index.html', '''<template><template><base href="/wrong/"></template></template>
            <base href="/assets/" href="/wrong/"><img src="logo.svg" src="wrong.svg">''')
        self.write('assets/logo.svg', '<svg/>')
        report = check(self.root)
        self.assertEqual(report['error_count'], 0, report)
        self.assertEqual(report['references'], 1)

    def test_forbidden_and_malformed_bases_fail_with_the_source_line(self):
        cases = [
            'data:text/plain,ignored', 'javascript:alert(1)', 'mailto:editor@example.test',
            'file:///local/assets/', 'https:///missing-host/', '//',
            'https://[broken/', 'https://example.test:bad/', 'https://example.test:65536/',
            'https://example.test:/', 'https://user:password@example.test/',
            'https://bad host.test/', 'https://bad..host.test/', 'https://-bad.test/',
        ]
        for base in cases:
            with self.subTest(base=base):
                self.write('index.html', '<!doctype html>\n<html><head>\n'
                           f'<base href="{base}">\n</head><body><img src="missing.svg"></body></html>')
                with patch('urllib.request.urlopen', side_effect=AssertionError('Network access')):
                    report = check(self.root)
                self.assertEqual(report['source_files'], 1)
                self.assertEqual(report['error_count'], 1, report)
                error = report['errors'][0]
                self.assertEqual((error['source'], error['line'], error['url']), ('index.html', 3, base))
                self.assertIn('invalid base URL', error['reason'])

    def test_valid_relative_root_and_protocol_relative_bases_keep_local_checks(self):
        self.write('assets/logo.svg', '<svg/>')
        for base in ('../assets/', '/assets/', '/assets/?version=1#icon',
                     '//vpsforn8n.com/assets/', SITE+'/assets/',
                     'http://vpsforn8n.com/assets/'):
            with self.subTest(base=base):
                self.write('nested/page.html', f'<base href="{base}"><img src="logo.svg">'
                           '<img src="missing.svg">')
                report = check(self.root)
                self.assert_destinations(report, ['/assets/missing.svg'])
                self.assertEqual(report['references'], 2)

    def test_valid_external_https_and_ip_bases_remain_offline(self):
        for base in ('https://cdn.example.test/assets/', '//cdn.example.test/assets/',
                     'https://[2001:db8::1]:8443/assets/', 'https://127.0.0.1/assets/'):
            with self.subTest(base=base):
                self.write('index.html', f'<base href="{base}"><img src="remote.svg">')
                with patch('urllib.request.urlopen', side_effect=AssertionError('Network access')):
                    report = check(self.root)
                self.assertEqual(report['error_count'], 0, report)
                self.assertEqual(report['references'], 0)

    def test_only_first_active_base_is_validated_and_template_base_is_ignored(self):
        self.write('assets/logo.svg', '<svg/>')
        self.write('index.html', '<template><base href="data:text/plain,inert"></template>'
                   '<base href="/assets/"><base href="javascript:ignored">'
                   '<img src="logo.svg">')
        report = check(self.root)
        self.assertEqual(report['error_count'], 0, report)
        self.assertEqual(report['references'], 1)
        self.write('index.html', '<base href="data:text/plain,invalid"><base href="/assets/">')
        report = check(self.root)
        self.assertEqual(report['error_count'], 1, report)
        self.assertIn('invalid base URL', report['errors'][0]['reason'])

    def test_inline_styles_stylesheet_imports_and_cycles_are_checked_transitively(self):
        self.write('index.html', '''<link rel="stylesheet" href="css/main.css">
            <style>@import "css/inline.css"; body{background:url(inline-missing.svg)}</style>
            <div style="mask: url('attribute-missing.svg')"></div>''')
        self.write('css/main.css', '@import "nested/second.css" screen; @import url("inline.css");')
        self.write('css/nested/second.css', '@import "../main.css"; .a{background:url(../../deep-missing.svg)}')
        self.write('css/inline.css', '@import "main.css";')
        report = check(self.root)
        self.assert_destinations(report, ['/inline-missing.svg', '/attribute-missing.svg', '/deep-missing.svg'])
        self.assertEqual(report['source_files'], 4)

    def test_css_comments_strings_escapes_and_quoted_parentheses(self):
        self.write('index.html', '<link rel="stylesheet" href="main.css">')
        self.write('main.css', r'''/* url(comment.svg) @import "comment.css"; */
            .a::after{content:"url(string.svg)"; background:URL("image(1).svg")}
            .b{background:u\72l(icon\20 name.svg);mask:url(icon\)name.svg)}
            @import /* comment */ "nested\2e css";
            ''')
        self.write('image(1).svg', '<svg/>')
        self.write('icon name.svg', '<svg/>')
        self.write('icon)name.svg', '<svg/>')
        self.write('nested.css', 'a{background:url("missing.svg")}')
        self.assert_destinations(check(self.root), ['/missing.svg'])

    def test_html_comments_scripts_and_unreachable_css_are_not_resource_sources(self):
        self.write('index.html', '''<!-- <img src="comment.svg"> -->
            <script>const example = '<img src="script.svg">';</script>
            <style>body::after{content:"url(string.svg)"}</style>''')
        self.write('unused.css', '@import "missing.css"; body{background:url(missing.svg)}')
        report = check(self.root)
        self.assertEqual(report['error_count'], 0, report)
        self.assertEqual(report['references'], 0)
        self.assertEqual(report['source_files'], 1)

    def test_cached_documents_are_used_and_noindex_pages_are_checked(self):
        self.write('index.html', '<img src="disk-only.svg">')
        self.write('404.html', '<meta name="robots" content="noindex"><img src="error-page.svg">')
        documents = {'index.html': SimpleNamespace(source='<img src="cached.svg">')}
        self.write('cached.svg', '<svg/>')
        report = check(self.root, documents=documents)
        self.assert_destinations(report, ['/error-page.svg'])
        self.assertEqual(report['source_files'], 2)

    def test_malformed_resource_url_fails_without_network_or_writes(self):
        self.write('index.html', '<img src="http://[broken/image.svg">')
        with patch.object(Path, 'write_bytes', side_effect=AssertionError('Checker wrote files')):
            report = check(self.root)
        self.assertEqual(report['error_count'], 1)
        self.assertIn('invalid resource URL', report['errors'][0]['reason'])


if __name__ == '__main__':
    unittest.main()
