import siteConfig from './site-config.json' with { type: 'json' };

const OLD_PAGES_BASE = siteConfig.legacyBase;
const CANONICAL_BASE = siteConfig.origin;
const CANONICAL_HOST = new URL(CANONICAL_BASE).hostname;
const OLD_PATH_PREFIX = new URL(OLD_PAGES_BASE).pathname;
const REDIRECTS = new Map(Object.entries(siteConfig.redirects));

async function canonicalUrl(request, env) {
  const url = new URL(request.url);
  const originalPath = url.pathname;
  let path = originalPath;

  // Normalize all applicable rules before returning a single redirect.
  if (path === OLD_PATH_PREFIX || path.startsWith(OLD_PATH_PREFIX + '/')) {
    path = path.slice(OLD_PATH_PREFIX.length) || '/';
  }
  if (path.endsWith('/index.html')) {
    path = path.slice(0, -'index.html'.length);
  }
  path = REDIRECTS.get(path) || path;

  const checked = new Map();
  async function exists(target) {
    const assetPath = target.endsWith('/') ? target + 'index.html' : target;
    if (!checked.has(assetPath)) {
      const assetUrl = new URL(CANONICAL_BASE);
      assetUrl.pathname = assetPath;
      // Do not forward conditional/range headers: a 304 is not an existence check.
      const response = await env.ASSETS.fetch(new Request(assetUrl, { method: 'HEAD' }));
      checked.set(assetPath, response.status === 200);
    }
    return checked.get(assetPath);
  }

  // Only add a slash if the actual directory index exists. Missing pages stay 404.
  if (!path.endsWith('/') && !path.split('/').at(-1).includes('.')) {
    const directory = REDIRECTS.get(path + '/') || path + '/';
    if (await exists(directory)) path = directory;
  }
  if (path !== originalPath && await exists(path)) url.pathname = path;

  // Local and preview hosts remain usable without redirecting into production.
  if (url.hostname === CANONICAL_HOST || url.hostname === `www.${CANONICAL_HOST}`) {
    url.protocol = 'https:';
    url.hostname = CANONICAL_HOST;
    url.port = '';
  }
  return url;
}

async function serveAsset(request, env) {
  const response = await env.ASSETS.fetch(request);
  const contentType = response.headers.get('content-type') || '';

  if (request.method === 'HEAD' || [204, 205, 304].includes(response.status) ||
      !contentType.toLowerCase().includes('text/html')) {
    return response;
  }

  const html = (await response.text()).replaceAll(OLD_PAGES_BASE, CANONICAL_BASE);
  const headers = new Headers(response.headers);
  headers.delete('content-length');
  headers.delete('content-encoding');
  headers.delete('etag');

  return new Response(html, {
    status: response.status,
    statusText: response.statusText,
    headers
  });
}

export default {
  async fetch(request, env) {
    const url = await canonicalUrl(request, env);
    if (url.toString() !== request.url) {
      return Response.redirect(url.toString(), 301);
    }

    if (url.pathname.endsWith('/')) {
      url.pathname += 'index.html';
      return serveAsset(new Request(url, request), env);
    }

    return serveAsset(request, env);
  }
};
