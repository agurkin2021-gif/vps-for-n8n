# Cloudflare deployment

This repository contains the static site for https://vpsforn8n.com/.

Cloudflare build settings:

- Build command: `node cloudflare-build.mjs`
- Deploy command: `npx wrangler deploy`
- Root directory: `/`
- Output directory: `dist/`

The build copies only public web assets (HTML, CSS, SVG, TXT and XML) into `dist/`.
Editorial/translation Python scripts, GitHub workflow caches and other maintenance files are not published.

`assets.html_handling` is set to `none` so existing `.html` URLs remain unchanged.
A nearest `404.html` is served with HTTP 404 for missing files.
