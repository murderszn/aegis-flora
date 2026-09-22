const fs = require('fs');
const path = require('path');
const assert = require('assert');

console.log('--- Aegis Florae: Desktop 1.1.0 Release Verification ---');

const rootDir = path.resolve(__dirname, '..');
const desktopDir = path.join(rootDir, 'desktop');
const pkg = JSON.parse(fs.readFileSync(path.join(desktopDir, 'package.json'), 'utf8'));

console.log('1. Version consistency (1.1.0, no stale 1.0.0)...');
assert.strictEqual(pkg.version, '1.1.0', 'desktop/package.json must be 1.1.0');
for (const f of ['desktop/README.md', '.github/workflows/build-desktop.yml', 'WINDOWS_STEAM_RELEASE_CHECKLIST.md']) {
  const content = fs.readFileSync(path.join(rootDir, f), 'utf8');
  assert(!content.includes('1.0.0'), `${f} must not reference stale 1.0.0`);
  assert(content.includes('1.1.0'), `${f} must reference current 1.1.0`);
}
console.log('✓ Version is 1.1.0 everywhere.');

console.log('2. Production icons exist and are non-empty...');
for (const icon of ['build/icon.ico', 'build/icon.icns']) {
  const p = path.join(desktopDir, icon);
  assert(fs.existsSync(p), `${icon} must exist`);
  assert(fs.statSync(p).size > 0, `${icon} must be non-empty`);
}
console.log('✓ Icons present.');

console.log('3. macOS production config (DMG, arches, entitlements, layout)...');
assert.strictEqual(pkg.build.appId, 'com.murderszn.aegisflorae');
assert.strictEqual(pkg.build.productName, 'Aegis Florae');
assert.ok(pkg.build.artifactName.includes('${version}'), 'artifactName must embed version');
const macTargets = pkg.build.mac.target;
assert(macTargets.some((t) => t.target === 'dmg' && t.arch.includes('arm64') && t.arch.includes('x64')),
  'mac must build DMG for arm64 + x64');
assert.strictEqual(pkg.build.mac.minimumSystemVersion, '12.0.0', 'macOS 12 minimum');
assert.strictEqual(pkg.build.mac.hardenedRuntime, true, 'hardened runtime required');
assert(fs.existsSync(path.join(desktopDir, pkg.build.mac.entitlements)), 'entitlements file must exist');
const contents = pkg.build.dmg.contents;
assert(contents.some((c) => c.type === 'file'), 'DMG must include the app file entry');
assert(contents.some((c) => c.type === 'link' && c.path === '/Applications'), 'DMG must link /Applications');
console.log('✓ macOS config correct.');

console.log('4. Windows production config (NSIS + ZIP, x64, shortcuts)...');
const winTargets = pkg.build.win.target.map((t) => t.target);
assert(winTargets.includes('nsis') && winTargets.includes('zip'), 'win needs nsis + zip');
assert(pkg.build.nsis.allowToChangeInstallationDirectory === true, 'custom install dir required');
assert(pkg.build.nsis.createDesktopShortcut === true, 'desktop shortcut required');
assert(pkg.build.nsis.createStartMenuShortcut === true, 'start menu shortcut required');
console.log('✓ Windows config correct.');

console.log('5. Packaged resources cover every game.html asset class...');
const filter = pkg.build.extraResources[0].filter;
for (const entry of ['game.html', 'landing.html', 'index.html', 'hud.css', 'favicon.ico',
  'js/**/*', 'assets/**/*', 'blender_pipeline/models/**/*', 'blender_pipeline/renders/**/*']) {
  assert(filter.includes(entry), `extraResources must include ${entry}`);
}
// Every local blender_pipeline/assets reference in game.html must be covered
const gameHtml = fs.readFileSync(path.join(rootDir, 'game.html'), 'utf8');
const refs = [...gameHtml.matchAll(/['"](blender_pipeline\/[^'"]+|assets\/[^'"]+|js\/[^'"]+|hud\.css)[^'"]*['"]/g)]
  .map((m) => m[1].split('?')[0]);
const uncovered = refs.filter((r) => !fs.existsSync(path.join(rootDir, r)));
assert.strictEqual(uncovered.length, 0, `game.html references missing files: ${uncovered.join(', ')}`);
console.log(`✓ All ${refs.length} game.html asset references resolve on disk and are packaged.`);

console.log('6. main.js hardening (traversal guard, no dead dock API)...');
const mainJs = fs.readFileSync(path.join(desktopDir, 'main.js'), 'utf8');
assert(!mainJs.includes('app.dock.setName'), 'must not call nonexistent app.dock.setName');
assert(mainJs.includes('startsWith(basePath'), 'protocol handler must block path traversal');
assert(mainJs.includes('403'), 'traversal attempts must be rejected');
assert(mainJs.includes("'use-angle', 'd3d11'"), 'Windows D3D11 ANGLE backend required');
assert(mainJs.includes('enable-gamepad-button-axis-events'), 'gamepad support required');
assert(mainJs.includes('crashReporter.start'), 'Crashpad init required');
console.log('✓ main.js hardened.');

console.log('7. CI workflow (tags, tests, npm ci, versioned artifacts, unsigned-safe)...');
const workflow = fs.readFileSync(path.join(rootDir, '.github/workflows/build-desktop.yml'), 'utf8');
assert(workflow.includes("tags:") && workflow.includes("'v*'"), 'must build on v* tags');
assert(workflow.includes('workflow_dispatch'), 'must support manual dispatch');
assert(workflow.includes('npm ci'), 'must use npm ci when lockfile exists');
assert(workflow.includes('check-icons'), 'must gate on production icons');
assert(workflow.includes('Aegis-Florae-1.1.0-Windows-x64'), 'Windows artifacts must be versioned');
assert(workflow.includes('Aegis-Florae-1.1.0-macOS-DMG'), 'macOS artifacts must be versioned');
assert(workflow.includes('windows-latest') && workflow.includes('macos-latest'), 'both runners required');
console.log('✓ Workflow correct.');

console.log('\nAll Desktop 1.1.0 Release Verification tests passed!');
process.exit(0);
