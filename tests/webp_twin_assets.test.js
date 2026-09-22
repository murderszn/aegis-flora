// WebP twin coverage: the landing pages probe a `.webp` variant for every
// <img src="*.jpg"> and swap on success (index.html ~L1181). A missing twin
// means a wasted 404 probe on every page load, so each one must exist on disk.
const assert = require('assert');
const fs = require('fs');
const path = require('path');

console.log('--- Aegis Flora: Running WebP Twin Asset Tests ---');

const rootDir = path.resolve(__dirname, '..');
for (const page of ['index.html', 'landing.html']) {
  const html = fs.readFileSync(path.join(rootDir, page), 'utf8');
  const srcs = [...html.matchAll(/<img[^>]*src="([^"]+\.jpg)"/g)].map((m) => m[1]);
  assert.ok(srcs.length > 0, page + ' must contain at least one <img src="*.jpg">');
  const missing = [...new Set(srcs)].filter((s) => !fs.existsSync(path.join(rootDir, s.replace(/\.jpg$/, '.webp'))));
  assert.strictEqual(missing.length, 0,
    page + ' <img> jpgs missing .webp twins: ' + missing.join(', '));
  console.log(`✓ [${page}] all ${new Set(srcs).size} <img> jpgs have .webp twins`);
}

console.log('\nAll WebP Twin Asset tests passed!');
process.exit(0);
