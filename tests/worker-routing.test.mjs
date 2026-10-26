import assert from 'node:assert/strict';
import { readFile, readdir } from 'node:fs/promises';
import { dirname, extname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import worker from '../cloudflare-worker.mjs';
import config from '../site-config.json' with { type: 'json' };

const repo = dirname(dirname(fileURLToPath(import.meta.url)));
const root = resolve(process.env.SITE_TEST_ROOT || repo);
const origin = config.origin;
const legacyPath = new URL(config.legacyBase).pathname;
const sitemap = await readFile(join(root, 'sitemap.xml'), 'utf8');
const urls = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map(match => match[1]);
const allowed = new Set(['.html', '.css', '.svg', '.txt', '.xml']);
const ignored = new Set(['.git', '.github', '.wrangler', 'dist', 'node_modules', 'scripts', 'tests', '__pycache__']);
const assets = new Map();

async function inventory(dir, prefix = '') {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const path = `${prefix}/${entry.name}`;
    if (entry.isDirectory() && !ignored.has(entry.name)) {
      await inventory(join(dir, entry.name), path);
    } else if (entry.isFile() && allowed.has(extname(entry.name))) {
      assets.set(path, await readFile(join(dir, entry.name)));
    }
  }
}
await inventory(root);
const directories = [...assets.keys()].filter(path => path.endsWith('/index.html'))
  .map(path => path.slice(0, -'index.html'.length));
const mime = { '.html': 'text/html', '.css': 'text/css', '.svg': 'image/svg+xml', '.xml': 'application/xml', '.txt': 'text/plain' };

// Match the configured ASSETS binding: exact paths, HTML handling disabled,
// a real 404 fallback, and bodyless HEAD/conditional responses.
function binding(calls = []) {
  return { ASSETS: { async fetch(request) {
    calls.push(request);
    const path = new URL(request.url).pathname;
    const found = assets.has(path);
    const headers = { 'content-type': mime[extname(found ? path : '/404.html')] };
    if (found && request.headers.has('if-none-match')) {
      return new Response(null, { status: 304, headers });
    }
    const body = request.method === 'HEAD' ? null : assets.get(found ? path : '/404.html');
    return new Response(body, { status: found ? 200 : 404, headers });
  } } };
}

async function redirect(from, to, method = 'GET', env = binding()) {
  const response = await worker.fetch(new Request(from, { method }), env);
  assert.equal(response.status, 301, from);
  assert.equal(response.headers.get('location'), to, from);
  return response;
}

test('test assets match the production routing configuration', async () => {
  const wrangler = JSON.parse(await readFile(join(repo, 'wrangler.jsonc'), 'utf8'));
  assert.equal(wrangler.assets.html_handling, 'none');
  assert.equal(wrangler.assets.not_found_handling, '404-page');
  assert.equal(wrangler.assets.run_worker_first, true);
  assert.ok(urls.length > 0, 'The sitemap must not be empty');
  assert.equal(new Set(urls).size, urls.length);
});

test('every sitemap URL stays HTTP 200 without a redirect, for GET and HEAD', async t => {
  for (const url of urls) {
    for (const method of ['GET', 'HEAD']) {
      const response = await worker.fetch(new Request(url, { method }), binding());
      assert.equal(response.status, 200, `${method} ${url}`);
      assert.equal(response.headers.get('location'), null, url);
      if (method === 'HEAD') assert.equal(response.body, null, url);
    }
  }
  t.diagnostic(`${urls.length} canonical URLs checked with GET and HEAD`);
});

test('HTTP, www and legacy prefix combinations reach every canonical in one hop', async t => {
  const query = '?utm_source=old&value=one%2Ftwo&value=3';
  const host = new URL(origin).host;
  let count = 0;
  for (const url of urls) {
    const path = new URL(url).pathname;
    const variants = [
      `http://${host}${path}`,
      `https://www.${host}${path}`,
      `http://www.${host}${path}`,
      `${origin}${legacyPath}${path}`,
      `http://www.${host}${legacyPath}${path}`
    ];
    for (const from of variants) {
      for (const method of ['GET', 'HEAD']) {
        await redirect(from + query, url + query, method);
        count++;
      }
    }
  }
  t.diagnostic(`${count} redirects checked, preserving the complete query string`);
});

test('all existing directory and index.html variants resolve directly to the final URL', async t => {
  for (const directory of directories) {
    const target = origin + (config.redirects[directory] || directory);
    const paths = [directory + 'index.html'];
    if (directory !== '/') paths.push(directory.slice(0, -1));
    for (const path of paths) {
      for (const method of ['GET', 'HEAD']) {
        await redirect(origin + path, target, method);
        await redirect(origin.replace('https://', 'http://www.') + legacyPath + path, target, method);
      }
    }
    const final = await worker.fetch(new Request(target), binding());
    assert.equal(final.status, 200, target);
    assert.equal(final.headers.get('location'), null, target);
  }
  await redirect(origin + legacyPath, origin + '/');
  t.diagnostic(`${directories.length} directory indexes checked`);
});

test('all five meta-refresh aliases become server redirects to indexable pages', async () => {
  const expected = {
    '/backup-restore.html': '/n8n-backup-and-restore.html',
    '/docker-install.html': '/install-n8n-on-a-vps.html',
    '/production-security.html': '/secure-n8n-on-a-vps.html',
    '/queue-mode.html': '/n8n-queue-mode.html',
    '/it/': '/it/vps-n8n/'
  };
  assert.deepEqual(config.redirects, expected);
  for (const [from, to] of Object.entries(expected)) {
    assert.ok(urls.includes(origin + to), to);
    for (const method of ['GET', 'HEAD']) {
      await redirect(origin + from, origin + to, method);
      await redirect(origin.replace('https://', 'http://www.') + legacyPath + from + '?ref=old', origin + to + '?ref=old', method);
    }
  }
});

test('unknown paths keep a real 404 and are never redirected to a homepage', async () => {
  for (const path of ['/missing', '/missing/', '/missing/index.html', '/missing.html',
    '/es/missing', '/es/missing/index.html', legacyPath + '/missing', legacyPath + '/missing.html',
    legacyPath + '-other/es/', legacyPath + '//example.com/']) {
    for (const method of ['GET', 'HEAD']) {
      const response = await worker.fetch(new Request(origin + path, { method }), binding());
      assert.equal(response.status, 404, path);
      assert.equal(response.headers.get('location'), null, path);
    }
  }
});

test('static assets retain their filenames, contents and content types', async () => {
  for (const path of ['/robots.txt', '/sitemap.xml', '/styles.css', '/favicon.svg', '/googleb2953904cf71c52f.html']) {
    const response = await worker.fetch(new Request(origin + path), binding());
    assert.equal(response.status, 200, path);
    assert.equal(response.headers.get('location'), null, path);
    assert.equal(response.headers.get('content-type'), mime[extname(path)], path);
    assert.equal(await response.text(), assets.get(path).toString(), path);
    await redirect(origin + legacyPath + path, origin + path);
  }
});

test('directory probes ignore conditional headers and use HEAD only', async () => {
  const calls = [];
  const response = await worker.fetch(new Request(origin + '/es', {
    headers: { 'if-none-match': 'cached-version', range: 'bytes=0-10' }
  }), binding(calls));
  assert.equal(response.status, 301);
  assert.equal(response.headers.get('location'), origin + '/es/');
  assert.equal(calls.length, 1);
  assert.equal(calls[0].method, 'HEAD');
  assert.equal(calls[0].headers.has('if-none-match'), false);
  assert.equal(calls[0].headers.has('range'), false);
});

test('conditional HTML responses remain bodyless without a Worker error', async () => {
  for (const method of ['GET', 'HEAD']) {
    const response = await worker.fetch(new Request(origin + '/es/', {
      method, headers: { 'if-none-match': 'cached-version' }
    }), binding());
    assert.equal(response.status, 304);
    assert.equal(response.body, null);
  }
});

test('a failed asset probe does not invent an existing directory', async () => {
  const env = { ASSETS: { fetch: async request => new Response(null, {
    status: request.method === 'HEAD' ? 503 : 404
  }) } };
  const response = await worker.fetch(new Request(origin + '/missing'), env);
  assert.equal(response.status, 404);
  assert.equal(response.headers.get('location'), null);
});

test('local and preview hosts stay usable', async () => {
  const local = 'http://localhost:8794';
  const response = await worker.fetch(new Request(local + '/'), binding());
  assert.equal(response.status, 200);
  await redirect(local + '/es', local + '/es/');
});
