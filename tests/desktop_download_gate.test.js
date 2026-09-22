// Gated desktop download tests: free email-gated (Web3Forms) download section
// on index.html + landing.html, wired to canonical GitHub Release assets
// published by .github/workflows/build-desktop.yml.
const assert = require('assert');
const fs = require('fs');
const path = require('path');

console.log('--- Aegis Florae: Running Gated Desktop Download Tests ---');

const rootDir = path.resolve(__dirname, '..');
const pkg = JSON.parse(fs.readFileSync(path.join(rootDir, 'desktop', 'package.json'), 'utf8'));
const workflow = fs.readFileSync(path.join(rootDir, '.github/workflows/build-desktop.yml'), 'utf8');

const ACCESS_KEY = 'c1d12d19-35cf-48d7-9e10-380128d4f1fc';
const RELEASE_FILES = [
  'AegisFlorae-1.1.0-Windows-x64-Setup.exe',
  'AegisFlorae-1.1.0-Windows-x64-Portable.zip',
  'AegisFlorae-1.1.0-macOS-arm64.dmg',
  'AegisFlorae-1.1.0-macOS-x64.dmg',
];

const pages = ['index.html', 'landing.html'];
pages.forEach(function (page) {
  console.log('\n[' + page + ']');
  const html = fs.readFileSync(path.join(rootDir, page), 'utf8');

  // 1. Download block lives inside the intel/specs section (not a bottom chapter),
  // with the email gate form — and the classic footer stays untouched.
  assert.ok(html.includes('id="desktop-download"'), page + ' must have a #desktop-download block');
  const intelSplit = html.split('id="game-intel"')[1].split('id="chapter-command"')[0];
  assert.ok(intelSplit.includes('id="desktop-download"'),
    page + ' download block must sit inside the game-intel section');
  assert.ok(!html.includes('>Desktop Download</a>'), page + ' footer must keep its classic links only');
  assert.ok(html.includes('https://api.web3forms.com/submit'), page + ' gate must POST to Web3Forms');
  assert.ok(html.includes(ACCESS_KEY), page + ' gate must carry the Web3Forms access key');
  assert.ok(/<input[^>]*type="email"[^>]*required|<input[^>]*required[^>]*type="email"/.test(html),
    page + ' gate must require an email address');
  assert.ok(html.includes('name="botcheck"'), page + ' gate must include a botcheck honeypot');
  console.log('✓ Email gate form present (Web3Forms, required email, honeypot)');

  // 2. JS release config version tracks desktop/package.json — no silent drift.
  const m = html.match(/DESKTOP_RELEASE\s*=\s*\{[^}]*version:\s*'([^']+)'/);
  assert.ok(m, page + ' must define a DESKTOP_RELEASE config with a version');
  assert.strictEqual(m[1], pkg.version,
    page + ' DESKTOP_RELEASE version (' + m[1] + ') must match desktop/package.json (' + pkg.version + ')');
  console.log('✓ DESKTOP_RELEASE version matches desktop/package.json (' + pkg.version + ')');

  // 3. Every gated asset is referenced by the page config...
  for (const f of RELEASE_FILES) {
    assert.ok(html.includes(f), page + ' must reference release asset ' + f);
  }
  console.log('✓ All four release assets referenced (Windows x64 setup + portable, macOS arm64 + x64)');

  // 4. ...but no direct download href is exposed in the raw HTML (links render only after unlock).
  assert.ok(!html.includes('releases/download'), page + ' must not expose direct release hrefs before unlock');
  console.log('✓ No direct download hrefs in raw HTML (gated behind unlock)');

  // 5. Reachable: finale CTA points at the download block.
  assert.ok(html.includes('href="#desktop-download"'), page + ' must link to #desktop-download');
  console.log('✓ Block reachable from finale CTA');
});

// 6. CI publishes exactly the assets the site links to.
assert.ok(workflow.includes('softprops/action-gh-release'), 'workflow must publish via gh-release action');
assert.ok(workflow.includes('contents: write'), 'release job needs contents: write permission');
for (const f of RELEASE_FILES) {
  assert.ok(workflow.includes(f), 'workflow must publish canonical asset ' + f);
}
assert.ok(workflow.includes("refs/tags/v"), 'release publish must be gated on v* tags');
console.log('\n✓ Workflow publishes all four canonical assets to GitHub Releases on v* tags');

console.log('\nAll Gated Desktop Download tests passed!');
process.exit(0);
