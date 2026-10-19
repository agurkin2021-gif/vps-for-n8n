import { cp, mkdir, readdir, rm } from 'node:fs/promises';
import { extname, join, relative } from 'node:path';

const root = process.cwd();
const out = join(root, 'dist');
const allowed = new Set(['.html', '.css', '.svg', '.txt', '.xml']);
const ignoredTop = new Set(['.git', '.github', 'dist', 'scripts']);

await rm(out, { recursive: true, force: true });
await mkdir(out, { recursive: true });

let copied = 0;
async function walk(dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const src = join(dir, entry.name);
    const rel = relative(root, src).replaceAll('\\', '/');
    const top = rel.split('/')[0];

    if (entry.isDirectory()) {
      if (ignoredTop.has(top)) continue;
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
