#!/usr/bin/env python3
"""Connect published Estonian pages to each other without changing page content."""
from __future__ import annotations
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ET = ROOT / "et"
LINKS = {
    "../n8n-cloud-vs-self-hosted.html": "n8n-cloud-voi-ise-majutamine.html",
    "../n8n-vps-requirements.html": "n8n-vps-nouded.html",
}

def run(write: bool) -> None:
    pages = sorted(ET.glob("*.html"))
    assert len(pages) == 8, len(pages)
    changed = 0
    total = 0
    for file in pages:
        source = file.read_text(encoding="utf-8")
        updated = source
        for old, local in LINKS.items():
            assert (ET / local).is_file(), local
            updated, n = re.subn(r'href=(["\'])' + re.escape(old) + r'\1', lambda m: f'href={m.group(1)}{local}{m.group(1)}', updated)
            total += n
        assert len(re.findall(r'<h1(?:\s|>)', source, re.I)) == len(re.findall(r'<h1(?:\s|>)', updated, re.I)) == 1, file
        assert len(re.findall(r'<a\b', source, re.I)) == len(re.findall(r'<a\b', updated, re.I)), file
        assert source.count('hreflang="et" lang="et" aria-current="page"') == updated.count('hreflang="et" lang="et" aria-current="page"') == 2, file
        if updated != source:
            if not write:
                raise AssertionError(f"Unpublished Estonian links in {file.relative_to(ROOT)}")
            file.write_text(updated, encoding="utf-8")
            changed += 1
    print(f"ET_LOCAL_LINKS_PASS pages={len(pages)} links_rewritten={total} files_changed={changed} write={write}", flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    run(args.write)
