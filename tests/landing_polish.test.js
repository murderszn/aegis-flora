// Landing polish tests: trailer teaser, gallery filters, lightbox a11y,
// reduced-motion canvas handling, and VideoGame JSON-LD (index + landing).
const assert = require('assert');
const fs = require('fs');
const path = require('path');

console.log('--- Aegis Florae: Running Landing Polish Tests ---');

const pages = ['index.html', 'landing.html'];

function galleryCategory(src) {
  if (src.indexOf('assets/concepts/') === 0) return 'concept';
  if (/\/3d_[a-z_]+\.(jpg|webp|png)$/.test(src)) return 'asset';
  return 'render';
}

pages.forEach(function (page) {
  console.log('\n[' + page + ']');
  assert.ok(fs.existsSync(page), page + ' must exist');
  const html = fs.readFileSync(page, 'utf8');

  // 0. Favicon: declared icon link plus a root favicon.ico for direct requests
  assert.ok(html.includes('rel="icon"'), 'page must declare an icon link');
  assert.ok(fs.existsSync('favicon.ico'), 'root favicon.ico must exist');
  const ico = fs.readFileSync('favicon.ico');
  assert.strictEqual(ico.readUInt16LE(0), 0, 'favicon.ico must start with reserved field');
  assert.strictEqual(ico.readUInt16LE(2), 1, 'favicon.ico must be type 1 (icon)');
  assert.ok(ico.readUInt16LE(4) >= 1, 'favicon.ico must contain at least one image');
  console.log('✓ Favicon declared and root favicon.ico valid');

  // 0a. Footer must not link the GitHub repo (developer credit link stays)
  assert.ok(!html.includes('>GitHub</a>'), 'footer GitHub repo link must be gone');
  assert.ok(html.includes('Developer @murderszn'), 'developer credit link must remain');
  console.log('✓ Footer GitHub repo link removed');

  // 0b. Hero carries the trailer teaser only — no Launch/Inspect buttons
  assert.ok(!html.includes('>Inspect Sanctum</a>'), 'hero Inspect Sanctum button must be gone');
  const heroSplit = html.split('id="gameplay-cinematic"')[0];
  assert.ok(!heroSplit.includes('>Launch Game</a>'), 'no Launch Game button may precede the cinematic');
  assert.ok(html.includes('id="chapter-command"'), 'finale section must still exist');
  console.log('✓ Hero buttons removed, finale CTA intact');

  // 1. The hero trailer teaser has been intentionally removed; the cinematic section remains.
  assert.ok(!html.includes('hero-trailer-teaser'), 'hero trailer teaser must be removed');
  assert.ok(!html.includes('Watch the trailer'), 'hero trailer teaser label must be removed');
  assert.ok(!html.includes('Official gameplay · 60 FPS'), 'hero trailer teaser metadata must be removed');
  assert.ok(html.includes('id="gameplay-cinematic"'), 'cinematic section target must remain');
  console.log('✓ Hero trailer teaser removed; cinematic section remains');

  // 2. Gallery filters cover every tile with no orphans
  const filters = ['all', 'render', 'asset', 'concept'];
  filters.forEach(function (f) {
    assert.ok(html.includes('data-filter="' + f + '"'), 'filter button "' + f + '" must exist');
  });
  const itemSrcs = [];
  const itemRe = /class="gallery-item"[^>]*data-img="([^"]+)"/g;
  let m;
  while ((m = itemRe.exec(html)) !== null) itemSrcs.push(m[1]);
  assert.ok(itemSrcs.length >= 14, 'gallery must hold at least 14 tiles, found ' + itemSrcs.length);
  const buckets = { render: 0, asset: 0, concept: 0 };
  itemSrcs.forEach(function (src) { buckets[galleryCategory(src)]++; });
  Object.keys(buckets).forEach(function (k) {
    assert.ok(buckets[k] > 0, 'category "' + k + '" must contain at least one tile');
  });
  console.log('✓ Filters cover all ' + itemSrcs.length + ' tiles ' + JSON.stringify(buckets));

  // Every gallery image must resolve on disk
  itemSrcs.forEach(function (src) {
    assert.ok(fs.existsSync(src), 'asset must exist on disk: ' + src);
  });
  console.log('✓ All ' + itemSrcs.length + ' gallery images exist on disk');

  // 3. Lightbox accessibility: focus trap, focus restore, keyboard tiles, Escape
  assert.ok(html.includes('function openLightbox('), 'openLightbox must exist');
  assert.ok(html.includes('function closeLightbox('), 'closeLightbox must exist');
  assert.ok(html.includes('lightboxOpener'), 'opener focus must be stored and restored');
  assert.ok(html.includes("e.key === 'Tab'"), 'Tab focus trap must exist');
  assert.ok(html.includes("e.key === 'Escape'"), 'Escape-to-close must exist');
  assert.ok(html.includes("setAttribute('tabindex', '0')"), 'tiles must be keyboard-focusable');
  assert.ok(html.includes("setAttribute('role', 'button')"), 'tiles must expose a button role');
  console.log('✓ Lightbox focus trap, focus restore, and keyboard tiles present');

  // 4. Reduced motion: one shared flag, guards on parallax + particle drift
  const flagCount = (html.match(/var reducedMotion = window\.matchMedia\('\(prefers-reduced-motion: reduce\)'\)\.matches;/g) || []).length;
  assert.strictEqual(flagCount, 1, 'reducedMotion must be declared exactly once, found ' + flagCount);
  assert.ok(html.includes('if(reducedMotion) return;'), 'mouse parallax must respect reduced motion');
  assert.ok(html.includes('if(!reducedMotion){'), 'particle drift must respect reduced motion');
  console.log('✓ Reduced-motion handling covers parallax and particles');

  // 5. JSON-LD VideoGame schema parses and names the game + trailer
  const ldRe = /<script type="application\/ld\+json">([\s\S]*?)<\/script>/;
  const ldMatch = ldRe.exec(html);
  assert.ok(ldMatch, 'JSON-LD block must exist');
  const schema = JSON.parse(ldMatch[1]);
  assert.strictEqual(schema['@type'], 'VideoGame', 'schema must be a VideoGame');
  assert.strictEqual(schema.name, 'Aegis Florae', 'schema must name the game');
  assert.ok(schema.trailer && schema.trailer.contentUrl, 'schema must reference the trailer');
  assert.ok(schema.trailer.contentUrl.endsWith('.mp4'), 'trailer URL must point at the cinematic');
  const trailerLocal = 'assets/' + path.basename(schema.trailer.contentUrl);
  assert.ok(fs.existsSync(trailerLocal), 'trailer file must exist on disk: ' + trailerLocal);
  console.log('✓ JSON-LD VideoGame schema valid with trailer reference');
});

console.log('\nAll landing polish tests passed.');
