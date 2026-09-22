// Automated test suite for Issue #6 & #18: Verdant Glyph Progression & Single Authoritative Definition
const assert = require('assert');
const fs = require('fs');

console.log('--- Aegis Flora: Running Verdant Glyph Progression Tests (Issues #6 & #18) ---');

// 1. Verify Issue #18: No duplicate top-level glyph definitions
const html = fs.readFileSync('game.html', 'utf8');

function countOccurrences(str, target) {
  let count = 0, pos = 0;
  while ((pos = str.indexOf(target, pos)) !== -1) {
    count++;
    pos += target.length;
  }
  return count;
}

console.log('1. Checking for duplicate top-level glyph declarations (Issue #18)...');
assert.strictEqual(countOccurrences(html, 'var GLYPH_DEFS ='), 1, 'GLYPH_DEFS must be declared exactly once');
assert.strictEqual(countOccurrences(html, 'function loadGlyphs('), 1, 'loadGlyphs must be declared exactly once');
assert.strictEqual(countOccurrences(html, 'function saveGlyphs('), 1, 'saveGlyphs must be declared exactly once');
assert.strictEqual(countOccurrences(html, 'function getGlyphLevel('), 1, 'getGlyphLevel must be declared exactly once');
assert.strictEqual(countOccurrences(html, 'function canAffordGlyph('), 1, 'canAffordGlyph must be declared exactly once');
assert.strictEqual(countOccurrences(html, 'function purchaseGlyph('), 1, 'purchaseGlyph must be declared exactly once');
assert.strictEqual(countOccurrences(html, 'function getGlyphBonus('), 1, 'getGlyphBonus must be declared exactly once');
console.log('✓ Verified: All glyph functions are consolidated with zero duplicate definitions.');

// Mock browser environment for game runtime
global.window = global;
global.addEventListener = () => {};
global.removeEventListener = () => {};
global.requestAnimationFrame = (fn) => setTimeout(fn, 16);
global.cancelAnimationFrame = (id) => clearTimeout(id);
global.innerWidth = 1920;
global.innerHeight = 1080;

function makeEl(tag) {
  const el = {
    style: {},
    classList: { add: () => {}, remove: () => {}, contains: () => false, toggle: () => {} },
    appendChild: () => {},
    addEventListener: () => {},
    setAttribute: () => {},
    textContent: '',
    children: [],
    getContext: () => new Proxy({
      measureText: () => ({ width: 10 }),
      createImageData: (w, h) => ({ data: new Uint8ClampedArray((w||1) * (h||1) * 4) }),
      createLinearGradient: () => ({ addColorStop: () => {} }),
      createRadialGradient: () => ({ addColorStop: () => {} })
    }, {
      get: (t, p) => (p in t ? t[p] : () => {})
    })
  };
  el.parentElement = el;
  return el;
}

global.document = {
  readyState: 'complete',
  addEventListener: () => {},
  removeEventListener: () => {},
  querySelector: makeEl,
  querySelectorAll: () => [],
  body: {
    classList: { add: () => {}, remove: () => {}, contains: () => false, toggle: () => {} },
    appendChild: () => {},
    style: {}
  },
  createElement: makeEl,
  getElementById: makeEl
};
global.navigator = { userAgent: 'NodeTest' };
global.localStorage = {
  _data: {},
  getItem: (k) => global.localStorage._data[k] !== undefined ? global.localStorage._data[k] : null,
  setItem: (k, v) => { global.localStorage._data[k] = String(v); },
  removeItem: (k) => { delete global.localStorage._data[k]; }
};

global.THREE = require('../js/three.min.js');
global.THREE.GLTFLoader = function() { this.load = () => {}; };
global.THREE.OrbitControls = function() {
  return { target: new global.THREE.Vector3(), update: () => {}, addEventListener: () => {} };
};
global.THREE.WebGLRenderer = function() {
  const r = { domElement: makeEl('canvas'), setSize: () => {}, setPixelRatio: () => {}, render: () => {}, shadowMap: {} };
  return new Proxy(r, { get: (t, p) => (p in t ? t[p] : () => {}) });
};
global.document.createElementNS = (ns, tag) => global.document.createElement(tag);
global.AudioContext = function() {
  return {
    currentTime: 0,
    sampleRate: 44100,
    destination: {},
    createGain: () => ({ gain: { setValueAtTime: () => {}, exponentialRampToValueAtTime: () => {}, cancelScheduledValues: () => {} }, connect: () => {} }),
    createDynamicsCompressor: () => ({ threshold: { setValueAtTime: () => {} }, knee: { setValueAtTime: () => {} }, ratio: { setValueAtTime: () => {} }, attack: { setValueAtTime: () => {} }, release: { setValueAtTime: () => {} }, connect: () => {} }),
    createOscillator: () => ({ frequency: { setValueAtTime: () => {}, exponentialRampToValueAtTime: () => {} }, start: () => {}, stop: () => {}, connect: () => {} }),
    createBufferSource: () => ({ start: () => {}, stop: () => {}, connect: () => {} }),
    createBiquadFilter: () => ({ frequency: { setValueAtTime: () => {} }, Q: { setValueAtTime: () => {} }, connect: () => {} }),
    createBuffer: (c, l, r) => ({ getChannelData: () => new Float32Array(l) })
  };
};
global.webkitAudioContext = global.AudioContext;

// Load and evaluate script
const startTag = '<script>';
const endTag = '</script>';
const startIdx = html.indexOf(startTag, html.indexOf('use strict') - 20);
const endIdx = html.lastIndexOf(endTag);
const jsCode = html.slice(startIdx + startTag.length, endIdx);
eval(jsCode);

const API = global.AegisFlora || global.RoboFlora;
assert(API, 'API must be exported');

console.log('2. Testing Save Validation and Clamping (Issue #6)...');
// Inject malformed and overflowing save data
global.localStorage.setItem('aegis_glyphs', JSON.stringify({
  foundry: 999999, // exceeds maxLvl 15
  vault: -10,      // negative level
  invalid_key: 50  // unrecognized key
}));

const sanitized = API.loadGlyphs();
assert.strictEqual(sanitized.foundry, 15, 'Foundry level must clamp to maxLvl (15)');
assert.strictEqual(sanitized.vault, 0, 'Negative vault level must clamp to 0');
assert.strictEqual(sanitized.invalid_key, undefined, 'Unrecognized glyph keys must be stripped');

console.log('3. Testing Meta-Scrap Currency Boundary & Decoupling...');
// Clear glyphs and set specific Meta-Scrap
global.localStorage.removeItem('aegis_glyphs');
API.setMetaScrap(200);
assert.strictEqual(API.getMetaScrap(), 200, 'getMetaScrap must return 200');

const S = API.newGame(100);
const inMatchCashBefore = S.cash;

// Purchase Ancient Vault (cost 80 Meta-Scrap)
assert.strictEqual(API.canAffordGlyph('vault'), true, 'Should afford vault');
const purchaseSuccess = API.purchaseGlyph('vault');
assert.strictEqual(purchaseSuccess, true, 'purchaseGlyph must succeed');
assert.strictEqual(API.getGlyphLevel('vault'), 1, 'Vault level must be 1');
assert.strictEqual(API.getMetaScrap(), 120, 'Meta-Scrap must be decremented from 200 to 120');
assert.strictEqual(S.cash, inMatchCashBefore, 'Live in-match Scrap must NOT be consumed by Meta-Scrap purchases');

console.log('4. Testing Combat Phase Purchase Lockout...');
S.phase = 'combat';
const combatPurchase = API.purchaseGlyph('foundry');
assert.strictEqual(combatPurchase, false, 'Glyph purchases must be blocked during active combat wave');
assert.strictEqual(API.getGlyphLevel('foundry'), 0, 'Foundry level must remain unchanged');
S.phase = 'build';

console.log('5. Testing Gameplay Bonuses Applied on Boot & New Game...');
// Upgrade all glyphs
API.setMetaScrap(10000);
API.purchaseGlyph('foundry'); // lv 1 (+2% damage)
API.purchaseGlyph('foundry'); // lv 2 (+4% damage)
API.purchaseGlyph('flora');   // lv 1 (+15% Sanctum HP)
API.purchaseGlyph('mazing');  // lv 1 (unlocks blocker wall)

// Start fresh game with these upgrades
const S2 = API.newGame(42);
const bonus = API.getGlyphBonus();

// Verify Vault (+50 starting cash)
assert.strictEqual(S2.cash, 20 + 50, 'Starting cash must include Ancient Vault bonus');

// Verify Flora (+15% lives)
assert.strictEqual(S2.lives, 15 + Math.round(15 * 0.15), 'Starting lives must include Flora Symbiosis bonus');
assert.strictEqual(S2.maxLives, 15 + Math.round(15 * 0.15), 'maxLives must match upgraded lives');

// Verify Foundry (+4% tower damage multiplier)
assert.strictEqual(S2.dmgMult, 1.04, 'Tower damage multiplier must be 1.04 (+4%)');

// Verify Mazing Mastery
assert.strictEqual(S2.hasMazingWall, true, 'hasMazingWall must be true when mazing is unlocked');

// Test placing Mazing blocker wall
const blockerPlace = API.placeAt(5, 5, 'blocker');
assert.strictEqual(blockerPlace.ok, true, 'Placing Ruin Barrier blocker wall must succeed');
const placedBlocker = S2.towers.find(t => t.type === 'blocker');
assert(placedBlocker, 'Placed blocker tower must exist');
assert.strictEqual(placedBlocker.isBlocker, true, 'Placed blocker must have isBlocker flag');

console.log('6. Testing specialization prerequisites, capstones, and build effects...');
assert.strictEqual(Object.keys(API.GLYPH_BRANCHES).length, 3, 'Glyph tree must expose three specialization doctrines');
assert.strictEqual(API.getGlyphUnlockState('precision').unlocked, false, 'Petal Calibration must be gated behind Foundry rank 3');
API.setMetaScrap(20000);
assert.strictEqual(API.purchaseGlyph('foundry'), true, 'Third Foundry rank should purchase');
assert.strictEqual(API.getGlyphUnlockState('precision').unlocked, true, 'Petal Calibration should unlock at Foundry rank 3');

const solarBuild = API.getGlyphBonus({ attune: 5, deeproots: 3, solarlens: 4, aetherflow: 2, sunheart: 1 });
assert.strictEqual(solarBuild.manaRegen, 5.6, 'Solar Attunement should increase mana regeneration');
assert.strictEqual(solarBuild.rootDuration, 5, 'Deep Roots should extend Overgrowth duration');
assert.strictEqual(solarBuild.flareDamage, 1120, 'Solar Lens should amplify Solar Flare damage');
assert.strictEqual(solarBuild.cooldownMult, 0.88, 'Aetherflow should shorten ability cooldowns');
assert.strictEqual(solarBuild.abilityCostMult, 0.8, 'Sunheart capstone should lower ability costs');

console.log('7. Testing full-refund between-wave respec...');
const investment = API.getGlyphInvestment();
const bankBeforeRespec = API.getMetaScrap();
const refund = API.respecGlyphs();
assert.strictEqual(refund, investment, 'Respec should refund the complete invested amount');
assert.strictEqual(API.getMetaScrap(), bankBeforeRespec + investment, 'Refund must return to banked Meta-Scrap');
assert(Object.values(API.loadGlyphs()).every(level => level === 0), 'Respec must clear every glyph rank');

console.log('--- ALL VERDANT GLYPH PROGRESSION TESTS PASSED! ---');
process.exit(0);
