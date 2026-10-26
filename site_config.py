"""Shared URL settings and source-file discovery for site maintenance tools."""
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / 'site-config.json').read_text(encoding='utf-8'))
SITE = CONFIG['origin']
LEGACY_SITE = CONFIG['legacyBase']
origin = urlsplit(SITE)
if origin.scheme != 'https' or not origin.netloc or origin.path or origin.query or origin.fragment:
    raise ValueError('site-config.json origin must be an HTTPS origin without a trailing slash')
BASE_URL = SITE + '/'
EXCLUDED_DIRS = {'.git', '.github', '.wrangler', 'dist', 'node_modules', 'scripts', 'tests', '__pycache__'}


def iter_public_html(root=ROOT):
    # Match Path.rglob's path style: workflow callers using Path('.') rely on
    # parts[0] being the locale, while validators pass an absolute root.
    root = Path(root)
    # Prune build/tooling directories rather than descending into their copies.
    def walk(folder):
        for file in sorted(folder.iterdir()):
            if file.is_symlink():
                continue
            if file.is_dir():
                if file.name not in EXCLUDED_DIRS:
                    yield from walk(file)
            elif file.suffix.lower() == '.html':
                yield file
    yield from walk(root)


def page_url(relative):
    relative = Path(relative).as_posix()
    if relative == 'index.html':
        relative = ''
    elif relative.endswith('/index.html'):
        relative = relative[:-10]
    return BASE_URL + relative


def regenerate_sitemap(root=ROOT):
    # Lazy import keeps config usable from the metadata validator as well.
    from scripts.generate_sitemap import generate
    return generate(Path(root))
