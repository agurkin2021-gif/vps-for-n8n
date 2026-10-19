# Cloudflare deployment

This repository is the source of truth for https://vpsforn8n.com/.

## Cloudflare Workers build settings

Dashboard settings:

- Build command: leave empty
- Deploy command: `npx wrangler deploy`
- Root directory: `/`
- Preview builds: disabled

Wrangler runs `node cloudflare-build.mjs` through the `build.command` setting in `wrangler.jsonc`.

The build copies only public web assets (HTML, CSS, SVG, TXT and XML) into `dist/`.
Editorial/translation Python scripts, GitHub workflow caches, Git metadata and maintenance files are not published.

## Routing

- `vpsforn8n.com` is attached as a Cloudflare Worker custom domain.
- `www.vpsforn8n.com/*` is routed to the Worker and redirected permanently to the root hostname.
- Directory URLs such as `/` and `/es/` are served from their existing `index.html` files.
- Existing `.html` URLs remain unchanged.
- Missing files use the site's `404.html` with HTTP 404.

## Legacy GitHub Pages

GitHub Pages is not published for this repository.
The Worker rewrites legacy `https://agurkin2021-gif.github.io/vps-for-n8n` links in HTML responses to `https://vpsforn8n.com`.
`robots.txt` and `sitemap.xml` use the production domain directly.
