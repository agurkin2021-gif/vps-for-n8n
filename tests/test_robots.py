"""Crawler-access regressions based on Google's REP examples and RFC 9309.

Specification: https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec
The fixtures exercise observable crawl decisions, independently of parser internals.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.check_robots import RobotsPolicy, check
from site_config import BASE_URL, LEGACY_SITE


class RobotsPolicyTests(unittest.TestCase):
    def assert_access(self, text, decisions, agent='Googlebot'):
        policy = RobotsPolicy(text)
        for path, allowed in decisions.items():
            with self.subTest(agent=agent, path=path):
                self.assertEqual(policy.allows(agent, BASE_URL.rstrip('/') + path), allowed)

    def test_empty_rules_and_unmatched_agents_allow_crawling(self):
        for text in ['', '# No restrictions\n', 'User-agent: *\nDisallow:\nAllow:\n',
                     'User-agent: OtherBot\nDisallow: /\n']:
            with self.subTest(text=text):
                self.assert_access(text, {'/': True, '/guides/page.html': True})

    def test_comments_bom_directive_case_and_path_case(self):
        policy = RobotsPolicy('\ufeff  uSeR-aGeNt: gOoGlEbOt  # crawler\r\n'
                              'dIsAlLoW: /Private # staff area\r\n'
                              'aLlOw: /Private/public\r\n'
                              'sItEmAp: ' + BASE_URL + 'sitemap.xml # map\r\n')
        self.assertEqual(policy.sitemaps, [BASE_URL+'sitemap.xml'])
        for path, allowed in {'/Private/secret': False, '/PrivateExtra': False,
                              '/private/secret': True, '/Private/public/a': True}.items():
            with self.subTest(path=path):
                self.assertEqual(policy.allows('GOOGLEBOT', BASE_URL.rstrip('/')+path), allowed)

    def test_repeated_matching_groups_are_merged(self):
        for token, agent in [('*', 'OtherBot'), ('Googlebot', 'Googlebot')]:
            text = (f'User-agent: {token}\nDisallow: /one\n'
                    'User-agent: UnrelatedBot\nDisallow: /\n'
                    f'User-agent: {token}\nDisallow: /two\nAllow: /one/public\n')
            self.assert_access(text, {'/one': False, '/two': False,
                                     '/one/public': True, '/three': True}, agent)

    def test_agent_matching_uses_complete_product_token(self):
        for unrelated in ['bot', 'google', 'Googlebot-News', 'Google-Extended']:
            text = f'User-agent: {unrelated}\nDisallow: /\nUser-agent: *\nAllow: /\n'
            with self.subTest(unrelated=unrelated):
                self.assert_access(text, {'/': True})
        for equivalent in ['googlebot', 'GOOGLEBOT', 'googlebot/1.2', 'googlebot*']:
            text = f'User-agent: {equivalent}\nDisallow: /\nUser-agent: *\nAllow: /\n'
            with self.subTest(equivalent=equivalent):
                self.assert_access(text, {'/': False})

    def test_specific_group_replaces_global_even_when_empty(self):
        for specific in ['', 'Allow: /\n', 'Disallow: /private\n']:
            text = 'User-agent: *\nDisallow: /\nUser-agent: Googlebot\n'+specific
            with self.subTest(specific=specific):
                self.assert_access(text, {'/': True, '/public': True})
                self.assert_access(text, {'/': False}, '*')
        self.assert_access('User-agent: *\nDisallow: /\nUser-agent: Googlebot\n'
                           'Disallow: /private\n', {'/private': False})
        for empty_rule in ['Disallow:', 'Allow:']:
            # Even an empty rule ends the UA list before the next group starts.
            text = 'User-agent: Googlebot\n'+empty_rule+'\nUser-agent: *\nDisallow: /\n'
            self.assert_access(text, {'/': True})
            self.assert_access(text, {'/': False}, '*')

    def test_non_rule_lines_do_not_split_shared_agent_group(self):
        text = ('User-agent: Googlebot\n\n# same group continues\n'
                'Sitemap: '+BASE_URL+'sitemap.xml\nContent-signal: search=yes,ai-train=no\n'
                'User-agent: OtherBot\nDisallow: /shared\n')
        for agent in ['Googlebot', 'OtherBot']:
            self.assert_access(text, {'/shared/page': False, '/public': True}, agent)

    def test_longest_rule_and_allow_ties_ignore_directive_order(self):
        cases = [
            (['Disallow: /', 'Allow: /public'], '/public/page', True),
            (['Allow: /public', 'Disallow: /public/private'], '/public/private/a', False),
            (['Disallow: /same', 'Allow: /same'], '/same/page', True),
            (['Allow: /page', 'Disallow: /*.htm'], '/page.htm', False),
            (['Allow: /page', 'Disallow: /*.ph'], '/page.php5', True),
            (['Allow: /page', 'Disallow: /pa********'], '/page.htm', False),
        ]
        for rules, path, allowed in cases:
            for ordered in [rules, list(reversed(rules))]:
                with self.subTest(rules=ordered):
                    self.assert_access('User-agent: *\n'+'\n'.join(ordered), {path: allowed})

    def test_wildcard_and_end_anchor_include_query_but_not_fragment(self):
        self.assert_access('User-agent: *\nDisallow: /files/*.pdf$\n', {
            '/files/.pdf': False, '/files/a/b.pdf': False, '/files/a.pdf#section': False,
            '/files/a.pdf?download=1': True, '/files/a.pdf/': True, '/files/a.PDF': True,
        })
        self.assert_access('User-agent: *\nDisallow: /\nAllow: /$\n', {
            '/': True, '/?page=1': False, '/guide': False,
        })
        self.assert_access('User-agent: *\nAllow: /\nDisallow: /$\n', {
            '/': False, '/guide': True,
        })
        self.assert_access('User-agent: *\nDisallow: /price$usd\nDisallow: /page$*\n', {
            '/price$usd': False, '/page$': False, '/page$extra': False, '/page': True,
        })

    def test_utf8_and_unreserved_percent_encodings_match_but_reserved_do_not(self):
        for rule in ['/café', '/caf%C3%A9', '/caf%c3%a9']:
            with self.subTest(rule=rule):
                self.assert_access('User-agent: *\nDisallow: '+rule+'\n', {
                    '/café/menu': False, '/caf%C3%A9/menu': False,
                    '/caf%c3%a9/menu': False, '/cafe/menu': True,
                })
        self.assert_access('User-agent: *\nDisallow: /%70rivate/~user\n', {
            '/private/~user': False, '/%70rivate/%7euser': False,
        })
        self.assert_access('User-agent: *\nDisallow: /a%2Fb\n', {
            '/a%2Fb': False, '/a%2fb': False, '/a/b': True,
        })
        self.assert_access('User-agent: *\nDisallow: /a/b\n', {
            '/a/b': False, '/a%2Fb': True,
        })
        self.assert_access('User-agent: *\nDisallow: /a%3Fb\nDisallow: /tags/%23part\n', {
            '/a%3Fb': False, '/a?b': True,
            '/tags/%23part': False, '/tags/#part': True,
        })

    def test_ai_specific_groups_do_not_block_google_or_generic_crawlers(self):
        text = ('User-agent: GPTBot\nUser-agent: ClaudeBot\nUser-agent: Google-Extended\n'
                'Disallow: /\nUser-agent: *\nContent-signal: search=yes,ai-train=no\nAllow: /\n')
        policy = RobotsPolicy(text)
        for agent in ['Googlebot', '*', 'Bingbot']:
            with self.subTest(agent=agent):
                self.assertTrue(policy.allows(agent, BASE_URL+'page.html'))
        for agent in ['GPTBot', 'ClaudeBot', 'Google-Extended']:
            with self.subTest(agent=agent):
                self.assertFalse(policy.allows(agent, BASE_URL+'page.html'))

    def test_malformed_access_rules_fail_instead_of_silently_allowing(self):
        for rule in ['Disallow /', 'Disallow: *', 'Allow: private', 'User-agent:',
                     'User-agent Googlebot', 'Sitemap https://example.com/sitemap.xml',
                     'Disalow: /', 'Useragent: *', 'Disallowx: /']:
            with self.subTest(rule=rule):
                with self.assertRaises(ValueError):
                    RobotsPolicy('User-agent: *\n'+rule+'\n')


class RobotsSiteCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.urls = [BASE_URL, BASE_URL+'guides/', BASE_URL+'page.html']
        namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
        sitemap = ET.Element('urlset', xmlns=namespace)
        for url in self.urls:
            ET.SubElement(ET.SubElement(sitemap, 'url'), 'loc').text = url
        (self.root/'sitemap.xml').write_bytes(ET.tostring(sitemap, encoding='utf-8'))

    def robots(self, text, *, append_sitemap=True):
        if append_sitemap:
            text += '\nSitemap: '+BASE_URL+'sitemap.xml\n'
        (self.root/'robots.txt').write_text(text, encoding='utf-8')

    def test_blanket_disallow_reports_every_page_and_sitemap_for_both_agents(self):
        self.robots('User-agent: *\nDisallow: /\n')
        result = check(self.root)
        expected = {(url, agent) for url in self.urls+[BASE_URL+'sitemap.xml']
                    for agent in ['*', 'Googlebot']}
        actual = {(error['url'], error['user_agent']) for error in result['errors']}
        self.assertEqual(actual, expected)
        self.assertEqual(result['error_count'], len(expected))
        self.assertEqual(result['sitemap_urls'], len(self.urls))
        self.assertEqual(result['checked_agents'], ['*', 'Googlebot'])

    def test_specific_googlebot_block_and_blocked_sitemap_are_detected(self):
        for disallow, blocked in [('/guides/', BASE_URL+'guides/'),
                                  ('/sitemap.xml$', BASE_URL+'sitemap.xml')]:
            self.robots('User-agent: *\nAllow: /\nUser-agent: Googlebot\nDisallow: '+disallow)
            with self.subTest(disallow=disallow):
                result = check(self.root)
                self.assertEqual(result['error_count'], 1)
                self.assertEqual([(error['url'], error['user_agent']) for error in result['errors']],
                                 [(blocked, 'Googlebot')])

    def test_allowed_site_with_ai_blocks_is_valid_and_checker_never_writes(self):
        self.robots('User-agent: GPTBot\nUser-agent: Google-Extended\nDisallow: /\n'
                    'User-agent: *\nContent-signal: search=yes,ai-train=no\nAllow: /\n')
        before = {path.name: path.read_bytes() for path in self.root.iterdir()}
        result = check(self.root)
        self.assertEqual(result['error_count'], 0)
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['sitemap_urls'], 3)
        self.assertEqual(result['checked_urls'], 4)
        self.assertEqual({path.name: path.read_bytes() for path in self.root.iterdir()}, before)
        # Ensure the public API remains usable by the JSON-based build report.
        json.dumps(result)

    def test_missing_commented_and_invalid_sitemap_declarations_are_rejected(self):
        for declaration in ['', '# Sitemap: '+BASE_URL+'sitemap.xml',
                            'Sitemap: /sitemap.xml',
                            'Sitemap: https://other.example/sitemap.xml',
                            'Sitemap: '+BASE_URL+'sitemap.xml?wrong-map=1',
                            'Sitemap: '+BASE_URL+'sitemap.xml.invalid']:
            self.robots('User-agent: *\nAllow: /\n'+declaration, append_sitemap=False)
            with self.subTest(declaration=declaration):
                with self.assertRaises(ValueError):
                    check(self.root)

    def test_legacy_sitemap_is_rejected_even_with_correct_production_declaration(self):
        self.robots('User-agent: *\nAllow: /\nSitemap: '+LEGACY_SITE+'/sitemap.xml\n')
        with self.assertRaises(ValueError):
            check(self.root)


if __name__ == '__main__':
    unittest.main()
