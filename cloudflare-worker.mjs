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
      return env.ASSETS.fetch(new Request(url, request));
    }

    return env.ASSETS.fetch(request);
  }
};
