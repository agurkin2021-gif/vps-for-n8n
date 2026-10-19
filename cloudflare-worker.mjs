const OLD_PAGES_BASE = 'https://agurkin2021-gif.github.io/vps-for-n8n';
const CANONICAL_BASE = 'https://vpsforn8n.com';

async function serveAsset(request, env) {
  const response = await env.ASSETS.fetch(request);
  const contentType = response.headers.get('content-type') || '';

  if (!contentType.toLowerCase().includes('text/html')) {
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
    const url = new URL(request.url);

    if (url.hostname === 'www.vpsforn8n.com') {
      url.hostname = 'vpsforn8n.com';
      url.protocol = 'https:';
      return Response.redirect(url.toString(), 301);
    }

    if (url.pathname.endsWith('/')) {
      url.pathname += 'index.html';
      return serveAsset(new Request(url, request), env);
    }

    return serveAsset(request, env);
  }
};
