# Cloudflare deployment

This repository is the source of truth for https://vpsforn8n.com/.

## Cloudflare Workers build settings

Dashboard settings:

- Build command: leave empty
- Deploy command: `npx wrangler deploy`
- Root directory: `/`
- Preview builds: disabled

Wrangler runs `node cloudflare-build.mjs` through the `build.command` setting in `wrangler.jsonc`.

The build needs Node.js 22+ and Python 3.9+ (standard library only). Both runtimes
are available in the [Cloudflare Workers build image](https://developers.cloudflare.com/workers/ci-cd/builds/build-image/).
Locally, `PYTHON` can select a Python executable; otherwise the build uses `python`
on Windows and `python3` on other platforms.

Every build first regenerates `sitemap.xml` from the current indexable source pages,
recreating a missing sitemap and replacing stale entries. Before replacing `dist/`,
the build checks the generated sitemap inventory, canonical URLs,
page identity metadata, robots sitemap declaration and crawl access, internal anchor destinations,
reciprocal hreflang groups, language-menu destinations, referenced local assets
and page reachability through ordinary links.
It also runs the Worker routing regression tests against the source assets.
Any generation or validation failure stops the build and preserves the previous
`dist/`. Only the derived sitemap is regenerated; HTML, robots rules, hreflang and
language menus must pass validation as supplied.

Robots validation checks every sitemap URL and the sitemap itself for both the
generic `*` group and `Googlebot`. A rule that blocks any of these URLs fails the
build before `dist/` is replaced. The check handles merged groups, specific-agent
overrides, longest-match Allow/Disallow precedence, `*` and `$` path patterns,
comments and percent-encoded UTF-8. Separate AI-crawler restrictions do not apply
to Googlebot. A commented-out Sitemap declaration does not pass validation.
Malformed access directives fail validation rather than silently allowing a build.
Run `python -B scripts/check_robots.py` for the focused report. This checks source
rules; Cloudflare changes to live robots.txt still require a post-deploy check.

The build copies only public web assets (HTML, CSS, SVG, TXT and XML) into `dist/`.
Both the build and Python checks use `assets.extensions` and
`assets.excludedDirectories` in `site-config.json` for the publication inventory.
Editorial/translation Python scripts, GitHub workflow caches, Git metadata and maintenance files are not published.

Local resource references must resolve to that inventory with the correct filename
case. This includes images and `srcset`, external script tags, stylesheet/icon/preload
links, inline CSS and URLs/imports in reachable stylesheets. A file that exists in
the repository but is excluded from publication still fails. Before introducing a
new asset format (for example, `.js`), deliberately update the shared extension
policy. External and data URLs are skipped; the check makes no network requests
and does not execute JavaScript or discover runtime-generated resource URLs.
CSS variable evaluation and string candidates in `image-set()` are outside its scope.
The first active `<base href>` must resolve to an HTTP(S) URL with a valid hostname
and port, without credentials. Relative, root-relative and protocol-relative bases
are supported, including external HTTP(S) hosts; bases inside templates are ignored.
Forbidden schemes such as `data:` or `javascript:`, malformed hosts/ports and
nonportable control characters or backslashes fail with the source file and line.
They cannot silently suppress local resource checks or replace the existing `dist/`.
Run `python -B scripts/check_assets.py` for the focused report.

Every indexable page must be reachable from `/` through ordinary `<a href>` links.
It must also be reachable from its language's homepage, using pages in that locale
and excluding `.lang-switch` / `.lang-menu` navigation. The reviewed home hreflang
group defines locale roots; regional codes sharing a homepage are checked together.
This checks a complete traversal, so isolated cycles fail even when their pages
link to each other. Head hreflang, script/template markup, nofollow links and
noindex/redirect pages do not provide navigation paths for this guard. This is a
conservative publication requirement, not a simulation of Google's crawler.
Run `python -B scripts/check_crawl_reachability.py` for the focused report.
Both guards run before `dist/` is removed; a failure leaves the previous build intact.

## URL configuration and sitemap maintenance

`site-config.json` is the common source for the production origin and legacy base.
The Worker imports it directly; Python generators and workflow checks use
`site_config.py`. Infrastructure bindings in `wrangler.jsonc` must also match the
domain if it is changed in the future.

After adding, removing or renaming a source page, update its entry in
`hreflang-groups.json`, then run:

```sh
python -B scripts/generate_sitemap.py
python -B scripts/generate_hreflang.py
python -B scripts/sync_language_menus.py
python -B scripts/validate_site.py
python -B -m unittest discover -s tests -v
node --test tests/worker-routing.test.mjs
node cloudflare-build.mjs
```

The generator includes indexable HTML pages with a self-referencing canonical on
the configured origin. It excludes noindex pages, meta-refresh redirects, Google's
verification file and build/tooling directories. Invalid or legacy canonicals
stop generation before the existing sitemap is changed. URLs are sorted and
unique; running the generator again leaves the sitemap bytes unchanged.
`python -B scripts/generate_sitemap.py --check` checks without writing.
The Cloudflare build runs generation automatically before validation and copies
the resulting sitemap into `dist/`; the manual generation command above is useful
when reviewing or committing updated sitemap output.

Language publication scripts use the same generator. Translation and navigation
jobs are separate maintenance operations; a normal build does not run them.

Historical GitHub workflows that commit or push generated content run only through
`workflow_dispatch`. Publishing a reviewed change must not automatically start
translation or navigation jobs that overwrite its URLs or hreflang groups. Their
manual jobs remain available. The obsolete Czech final-validation, Estonian
live-QA and Finnish live-check workflows are also manual: their historical
generator, menu-order assumptions or missing checkout do not validate the current
site. Other read-only probes retain their existing triggers.

`site-validation.yml` is the current read-only CI for pushes to `main`, pull
requests and manual runs. It uses Node.js 22 and Python 3.13 to run the Python
regression tests and the complete Cloudflare build, including site metadata and
Worker routing validation. It never publishes. After manual maintenance,
regenerate hreflang, synchronize language menus and run the validation commands above before publishing the
resulting content.

## Language alternatives

Visible language menus use the same reviewed topic map as head hreflang.
Run `python -B scripts/sync_language_menus.py` after manual translation or
navigation jobs; `--check` reports stale targets without writing. Existing menu
links point to the same topic when a translation exists, and otherwise to that
language's homepage. Correct links through configured redirects are preserved.
The tool preserves labels, attributes, menu order and all non-menu HTML; it does
not add missing language options. It recognizes a link's `hreflang`, then `lang`,
or infers the language from its mapped destination when both are absent.
Ambiguous or unknown languages and invalid maps fail before any file is written.
Noindex and redirect pages are excluded. The build checks these destinations
before replacing `dist/`, so stale output from historical navigation scripts
cannot be published silently.

`hreflang-groups.json` is the reviewed map of equivalent pages by topic. Each
indexable page belongs to exactly one group. Map paths must be existing,
indexable canonical URLs with a compatible HTML language. Do not substitute a
homepage for a missing article translation. In particular, Italian is currently
available only for the homepage (`/it/vps-n8n/`) and the VPS comparison.

The generator writes the same complete set of absolute hreflang links to the
head of every member, including a self-link. An optional `x_default` names a
language within that group: the English article is the fallback for its own
translations. Country hosting guides, managed hosting guides and the French
budget article are separate groups with no unrelated English fallback. The
French regional guide supports both `fr` and `fr-FR` for the same URL.
See [Google's localized-version guidelines](https://developers.google.com/search/docs/specialty/international/localized-versions).

Run `python -B scripts/generate_hreflang.py` after translation or navigation jobs,
some of which still emit their historical alternate-link blocks. The central
generator replaces only hreflang link tags, removes them from noindex/redirect
pages and leaves other source bytes unchanged. Repeated runs make no changes.
New pages require an explicit map entry; generation never guesses equivalent
articles from old links. A page without translations can have its own group.

`python -B scripts/generate_hreflang.py --check` validates without writing. The
pre-build check rejects missing targets, redirect/noindex targets, wrong language
assignments, incomplete or nonreciprocal sets, duplicates and misplaced tags.
`--root dist` can also check the built assets against the same source map.

## Routing

- `vpsforn8n.com` is attached as a Cloudflare Worker custom domain.
- HTTP and `www.vpsforn8n.com/*` redirect permanently to `https://vpsforn8n.com`.
- Old `/vps-for-n8n/...` paths redirect to the corresponding existing public asset.
- Existing `.../index.html` URLs redirect to their directory URL. A missing trailing
  slash is added only when the directory has a real `index.html` asset.
- Directory URLs such as `/` and `/es/` are served from their existing `index.html` files.
- Existing content `.html` URLs remain unchanged.
- Missing files use the site's `404.html` with HTTP 404; they are never sent to a homepage.

The former meta-refresh aliases use server-side 301 redirects, configured in
`site-config.json`:

| Old path | Destination |
| --- | --- |
| `/backup-restore.html` | `/n8n-backup-and-restore.html` |
| `/docker-install.html` | `/install-n8n-on-a-vps.html` |
| `/production-security.html` | `/secure-n8n-on-a-vps.html` |
| `/queue-mode.html` | `/n8n-queue-mode.html` |
| `/it/` | `/it/vps-n8n/` |

Rules are combined before responding, preserving the query string. For example,
`http://www.vpsforn8n.com/vps-for-n8n/it/index.html?ref=old` returns one 301 to
`https://vpsforn8n.com/it/vps-n8n/?ref=old`. GET and HEAD behave consistently.
Local and preview hosts retain their origin so previews can be tested independently.
When testing with this repository's production routes in Wrangler, use
`npx wrangler dev --local --local-protocol https`. Wrangler proxies the configured
production host; an HTTP-only local listener would keep triggering HTTPS enforcement.

Keep [`assets.html_handling`](https://developers.cloudflare.com/workers/static-assets/routing/advanced/html-handling/)
set to `none` and `run_worker_first` set to `true`: the Worker owns these redirects.
Directory/legacy-target existence checks use HEAD through the ASSETS binding and
accept only HTTP 200, without forwarding client cache or range headers.

## Legacy GitHub Pages

GitHub Pages is not published for this repository.
Indexable source HTML, `robots.txt` and `sitemap.xml` use the production domain directly.
The Worker retains its legacy HTML rewrite as a compatibility fallback; indexable
source pages containing the legacy base are rejected by pre-build validation.
