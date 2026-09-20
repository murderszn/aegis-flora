// Automated test suite for Issue #12: Feature Matrix & Documentation Synchronization
const assert = require('assert');
const fs = require('fs');

console.log('--- Aegis Flora: Running Feature Matrix & Documentation Verification Tests (Issue #12) ---');

// 1. Verify existence of documentation files
assert(fs.existsSync('SHIPPING_FEATURE_MATRIX.md'), 'SHIPPING_FEATURE_MATRIX.md must exist');
assert(fs.existsSync('ANALYSIS.md'), 'ANALYSIS.md must exist');
assert(fs.existsSync('TODO_COMPLETE.md'), 'TODO_COMPLETE.md must exist');
assert(fs.existsSync('README.md'), 'README.md must exist');
assert(fs.existsSync('GDD.md'), 'GDD.md must exist');

const matrixContent = fs.readFileSync('SHIPPING_FEATURE_MATRIX.md', 'utf8');
const analysisContent = fs.readFileSync('ANALYSIS.md', 'utf8');
const todoContent = fs.readFileSync('TODO_COMPLETE.md', 'utf8');
const readmeContent = fs.readFileSync('README.md', 'utf8');
const gddContent = fs.readFileSync('GDD.md', 'utf8');
const htmlContent = fs.readFileSync('game.html', 'utf8');

console.log('1. Checking Wave Count consistency across docs and code...');
const htmlWaveMatch = htmlContent.match(/var\s+WAVE_MAX\s*=\s*(\d+)/);
assert(htmlWaveMatch, 'game.html must define WAVE_MAX');
const waveMax = parseInt(htmlWaveMatch[1], 10);
assert.strictEqual(waveMax, 50, 'game.html WAVE_MAX must be 50');

assert(readmeContent.includes('50 Progressive Waves') || readmeContent.includes('50 progressive waves'), 'README.md must specify 50 progressive waves');
assert(gddContent.includes('Standard 50-Wave Mode'), 'GDD.md must specify Standard 50-Wave Mode');
assert(matrixContent.includes('50 progressive waves') || matrixContent.includes('WAVE_MAX = 50'), 'SHIPPING_FEATURE_MATRIX.md must specify 50 waves');
console.log('✓ Verified: Wave count is uniformly 50 across code and all documentation.');

console.log('2. Checking Keybindings & Controls consistency...');
const expectedBindings = [
  { key: 'Q', action: 'Gatling' },
  { key: 'W', action: 'Mortar' },
  { key: 'E', action: 'Beam' },
  { key: 'R', action: 'Obelisk' },
  { key: 'Space', action: 'Start Wave' },
  { key: 'D', action: 'Verdant Overgrowth' },
  { key: 'F', action: 'Solar Flare' },
  { key: 'P', action: 'Pause' },
  { key: 'V', action: 'Speed' },
  { key: 'M', action: 'mute' },
  { key: 'K', action: 'Tactical Clarity' },
  { key: 'G', action: 'Glyphs' },
  { key: '?', action: 'tutorial' }
];

expectedBindings.forEach(b => {
  assert(readmeContent.includes(`\`${b.key}\``), `README.md must document keybinding \`${b.key}\``);
  assert(matrixContent.includes(`\`${b.key}\``), `SHIPPING_FEATURE_MATRIX.md must document keybinding \`${b.key}\``);
});
console.log('✓ Verified: All 13 core gameplay hotkeys match between README and SHIPPING_FEATURE_MATRIX.');

console.log('3. Checking Tower Branch synchronization...');
const expectedBranches = [
  'Vulcan Pedestal',
  'Rail-Needler',
  'Cataclysm Bloom',
  'Skyburst Flak',
  'Sol Invictus',
  'Refraction Lens',
  'Chrono-Stutter',
  'Resonance Shatter'
];

expectedBranches.forEach(branch => {
  assert(matrixContent.includes(branch), `SHIPPING_FEATURE_MATRIX.md must document branch: ${branch}`);
  assert(htmlContent.includes(branch), `game.html must include branch: ${branch}`);
});
console.log('✓ Verified: All 8 tower elite branch upgrades are accurately documented.');

console.log('4. Checking Status reconciliation in ANALYSIS.md and TODO_COMPLETE.md...');
// Ensure completed features are not marked as NOT IMPLEMENTED
assert(!analysisContent.includes('Sanctum Super-Abilities (D & F keys) — NOT IMPLEMENTED'), 'ANALYSIS.md must not state Sanctum Super-Abilities are un-implemented');
assert(!analysisContent.includes('Meta-Progression (Verdant Glyphs) — NOT IMPLEMENTED'), 'ANALYSIS.md must not state Meta-Progression is un-implemented');
assert(!analysisContent.includes('Armor System — NOT IMPLEMENTED'), 'ANALYSIS.md must not state Armor System is un-implemented');
assert(!analysisContent.includes('Flow Field Pathfinding — NOT IMPLEMENTED'), 'ANALYSIS.md must not state Flow Field Pathfinding is un-implemented');

// Ensure TODO_COMPLETE marks them with [x]
assert(todoContent.includes('[x] **localStorage persistence**'), 'TODO_COMPLETE.md must mark localStorage persistence checked');
assert(todoContent.includes('[x] **Verdant Overgrowth (D)**'), 'TODO_COMPLETE.md must mark Verdant Overgrowth checked');
assert(todoContent.includes('[x] **Solar Flare (F)**'), 'TODO_COMPLETE.md must mark Solar Flare checked');
assert(todoContent.includes('[x] **Dota 2 armor formula**'), 'TODO_COMPLETE.md must mark armor formula checked');
assert(todoContent.includes('[x] **Integration Flow Field**'), 'TODO_COMPLETE.md must mark flow field checked');
console.log('✓ Verified: ANALYSIS.md and TODO_COMPLETE.md correctly reflect verified status.');

console.log('\nAll Feature Matrix & Documentation Verification (Issue #12) tests passed successfully!');
process.exit(0);
