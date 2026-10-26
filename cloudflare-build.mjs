import { cp, mkdir, readdir, rm } from 'node:fs/promises';
import { dirname, extname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const root = dirname(fileURLToPath(import.meta.url));
const out = join(root, 'dist');
const allowed = new Set(['.html', '.css', '.svg', '.txt', '.xml']);
const ignoredDirs = new Set(['.git', '.github', '.wrangler', 'dist', 'scripts', 'tests', 'node_modules', '__pycache__']);

const python = process.env.PYTHON || (process.platform === 'win32' ? 'python' : 'python3');
const validation = spawnSync(python, ['-B', join(root, 'scripts', 'validate_site.py'), '--root', root], {
  cwd: root,
  stdio: 'inherit',
  env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' }
});
if (validation.error || validation.status !== 0) {
  throw new Error(`Site validation failed before building assets: ${validation.error?.message || validation.status}`);
}

const routing = spawnSync(process.execPath, ['--test', join(root, 'tests', 'worker-routing.test.mjs')], {
  cwd: root,
  stdio: 'inherit',
  env: { ...process.env, SITE_TEST_ROOT: root }
});
if (routing.error || routing.status !== 0) {
  throw new Error(`Worker routing validation failed before building assets: ${routing.error?.message || routing.status}`);
}

await rm(out, { recursive: true, force: true });
await mkdir(out, { recursive: true });

let copied = 0;
async function walk(dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const src = join(dir, entry.name);
    const rel = relative(root, src).replaceAll('\\', '/');
    if (entry.isDirectory()) {
      if (ignoredDirs.has(entry.name)) continue;
      await walk(src);
      continue;
    }
    if (!entry.isFile()) continue;
    if (!allowed.has(extname(entry.name).toLowerCase())) continue;

    const dest = join(out, rel);
    await mkdir(join(dest, '..'), { recursive: true });
    await cp(src, dest);
    copied++;
  }
}

await walk(root);

if (copied < 500) {
  throw new Error(`Unexpectedly small Cloudflare build: ${copied} public files`);
}

console.log(`Cloudflare static build: ${copied} public files copied to dist/`);
