#!/usr/bin/env python3
"""Check source robots access for sitemap pages, using Google-compatible rules.

This is an offline build guard for the wildcard group and Googlebot's product
token, not an HTTP crawler or a simulator of other crawlers' agent aliases.
Grouping, rule precedence and URL matching follow:
https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec
https://www.rfc-editor.org/rfc/rfc9309.html
"""
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from site_config import BASE_URL, LEGACY_SITE, ROOT

CHECKED_AGENTS = ('*', 'Googlebot')
UNRESERVED = frozenset('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~')
HEX = frozenset('0123456789abcdefABCDEF')
MAX_ROBOTS_BYTES = 500 * 1024
DIRECTIVES = {'user-agent', 'allow', 'disallow', 'sitemap'}
# Reject near-directives that Google's permissive parser might still honor.
DIRECTIVE_PREFIXES = ('user-agent', 'useragent', 'user agent', 'allow', 'disallow',
                      'dissallow', 'dissalow', 'disalow', 'diasllow', 'disallaw',
                      'sitemap', 'site-map')


def normalize_path(value, *, pattern=False):
    """Keep reserved escapes distinct; unify UTF-8 and unreserved escapes."""
    out = []
    index = 0
    while index < len(value):
        char = value[index]
        if char == '%' and index + 2 < len(value) and set(value[index+1:index+3]) <= HEX:
            decoded = chr(int(value[index+1:index+3], 16))
            out.append(decoded if decoded in UNRESERVED else '%' + value[index+1:index+3].upper())
            index += 3
            continue
        literal_dollar = char == '$' and (not pattern or index != len(value)-1)
        if ord(char) > 127 or ord(char) <= 32 or char == '%' or literal_dollar or (not pattern and char == '*'):
            out.extend(f'%{byte:02X}' for byte in char.encode('utf-8'))
        else:
            out.append(char)
        index += 1
    return ''.join(out)


def product_token(value):
    # Google's product-token matching ignores a version or wildcard suffix,
    # but Googlebot-News and Google-Extended are distinct from Googlebot.
    value = value.strip()
    if value == '*':
        return '*'
    match = re.match(r'[A-Za-z_-]+', value)
    return match.group().lower() if match else ''


class RobotsPolicy:
    def __init__(self, text):
        if len(text.encode('utf-8')) > MAX_ROBOTS_BYTES:
            raise ValueError('robots.txt exceeds the 500 KiB crawler parsing limit')
        self.sitemaps = []
        self.groups = []
        agents, rules = [], []
        saw_rule = False
        for line_number, raw in enumerate(text.lstrip('\ufeff').splitlines(), 1):
            line = raw.split('#', 1)[0].strip()
            field, separator, value = line.partition(':')
            field, value = field.strip().lower(), value.strip()
            if field.startswith(DIRECTIVE_PREFIXES) and (not separator or field not in DIRECTIVES):
                raise ValueError(f'robots.txt line {line_number}: malformed directive')
            if not separator:
                continue
            if field == 'sitemap':
                if value:
                    self.sitemaps.append(value)
            elif field == 'user-agent':
                token = product_token(value)
                if not token:
                    raise ValueError(f'robots.txt line {line_number}: invalid User-agent')
                if saw_rule:
                    self.groups.append((agents, rules))
                    agents, rules, saw_rule = [], [], False
                agents.append(token)
            elif field in ('allow', 'disallow') and agents:
                # Even an empty rule ends the run of consecutive agent lines.
                saw_rule = True
                if not value:
                    continue
                if not value.startswith('/'):
                    raise ValueError(f'robots.txt line {line_number}: rule path must start with /')
                path = normalize_path(value, pattern=True)
                # Google uses the normalized pattern length for precedence,
                # including wildcards and the end anchor.
                priority = len(path)
                end = path.endswith('$')
                expression = path[:-1] if end else path
                matcher = re.compile('^' + re.escape(expression).replace(r'\*', '.*') + (r'\Z' if end else ''))
                rules.append((priority, field == 'allow', matcher))
        if agents:
            self.groups.append((agents, rules))

    def allows(self, user_agent, url):
        token = product_token(user_agent)
        specific = [rules for agents, rules in self.groups if token != '*' and token in agents]
        groups = specific if specific else [rules for agents, rules in self.groups if '*' in agents]
        parsed = urlsplit(url)
        path = parsed.path or '/'
        if '?' in url.split('#', 1)[0]:
            path += '?' + parsed.query
        path = normalize_path(path)
        if path == '/robots.txt':
            return True
        matches = [(length, allow) for rules in groups for length, allow, matcher in rules if matcher.match(path)]
        # Longest rule wins; Allow wins a tie, independent of declaration order.
        return max(matches, default=(0, True))[1]


def check(root=ROOT):
    root = Path(root)
    text = (root / 'robots.txt').read_text(encoding='utf-8-sig')
    policy = RobotsPolicy(text)
    sitemap_url = BASE_URL + 'sitemap.xml'
    if sitemap_url not in policy.sitemaps or LEGACY_SITE in text:
        raise ValueError('robots.txt must advertise the configured production sitemap')
    urls = [node.text for node in ET.parse(root / 'sitemap.xml').iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    targets = list(dict.fromkeys([*urls, sitemap_url]))
    errors = [{'url': url, 'user_agent': agent} for agent in CHECKED_AGENTS
              for url in targets if not policy.allows(agent, url)]
    return {'sitemap_urls': len(urls), 'checked_urls': len(targets),
            'checked_agents': list(CHECKED_AGENTS), 'error_count': len(errors), 'errors': errors}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        result = check(args.root)
    except (ValueError, OSError, ET.ParseError) as exc:
        print('robots.txt validation failed: ' + str(exc), file=sys.stderr)
        raise SystemExit(1)
    print(json.dumps({key: value for key, value in result.items() if key != 'errors'}))
    for error in result['errors'][:10]:
        print(json.dumps(error))
    raise SystemExit(bool(result['errors']))
