// Automated test suite for Issue #7: Tower Targeting Priorities (First, Last, Strongest, Weakest, Closest)
const assert = require('assert');
const fs = require('fs');

console.log('--- Aegis Flora: Running Tower Targeting Priority Tests (Issue #7) ---');

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
    querySelectorAll: () => [],
    querySelector: () => null,
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
    createBuffer: () => ({ getChannelData: () => new Float32Array(1024) })
  };
};

const html = fs.readFileSync('game.html', 'utf8');
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/m);
if (!scriptMatch) throw new Error('Could not find script tag in game.html');

try {
  eval(scriptMatch[1]);
} catch(e) {
  console.log('Script evaluated with non-fatal init notice:', e.message);
}

const api = global.AegisFlora || global.RoboFlora;
assert(api, 'AegisFlora API must be exposed on window');

console.log('1. Checking TARGET_MODES definition and API exports...');
assert(Array.isArray(api.TARGET_MODES), 'TARGET_MODES must be an array');
assert.strictEqual(api.TARGET_MODES.length, 5, 'Should have 5 targeting modes');
const modeIds = api.TARGET_MODES.map(m => m.id);
assert.deepStrictEqual(modeIds, ['first', 'last', 'strongest', 'weakest', 'closest']);
console.log('✓ Verified: All 5 targeting modes defined:', modeIds.join(', '));

console.log('2. Verifying default targetMode on newly placed towers...');
const S = api.newGame(42);
api.setMetaScrap(1000);
S.cash = 1000;

// Place a gun tower at (5, 5)
const placed = api.placeAt(5, 5, 'gun');
assert(placed, 'Tower placement at (5,5) should succeed');
const tower = S.towers.find(t => t.gx === 5 && t.gy === 5);
assert(tower, 'Tower should exist in state');
assert.strictEqual(tower.targetMode, 'first', 'Default targeting mode must be "first"');
console.log('✓ Verified: Newly placed tower defaults to "first" target mode');

console.log('3. Testing cycleTowerTargetMode and setTowerTargetMode...');
api.cycleTowerTargetMode(tower, 1);
assert.strictEqual(tower.targetMode, 'last', 'Cycling forward from "first" should select "last"');
api.cycleTowerTargetMode(tower, 1);
assert.strictEqual(tower.targetMode, 'strongest', 'Cycling forward should select "strongest"');
api.cycleTowerTargetMode(tower, -1);
assert.strictEqual(tower.targetMode, 'last', 'Cycling backward should return to "last"');

api.setTowerTargetMode(tower, 'weakest');
assert.strictEqual(tower.targetMode, 'weakest', 'setTowerTargetMode("weakest") should work');
api.setTowerTargetMode(tower, 'invalid_mode');
assert.strictEqual(tower.targetMode, 'first', 'Invalid target mode should fallback safely to "first"');
console.log('✓ Verified: Mode setting and cycling work as expected.');

console.log('4. Testing combat targeting selection logic across all 5 modes...');
// Create a cluster of enemies in range of tower at (5, 5) (center: 5.5, 5.5, range: ~3.4 tiles)
// Let's create dummy foes with distinct properties:
// Tower center is at (5.5, 5.5)
function createFoe(id, x, y, hp, maxHp, wp) {
  return {
    id: id,
    x: x,
    y: y,
    r: 0.3,
    hp: hp,
    maxHp: maxHp,
    wp: wp, // waypoint index / progress along maze path
    speed: 1.0,
    mesh: {
      position: new global.THREE.Vector3(x, 0.5, y),
      rotation: { y: 0 },
      scale: { set: () => {}, x: 1, y: 1, z: 1 },
      material: { opacity: 1, color: { setHex: () => {} } },
      userData: {}
    },
    dead: false,
    escaped: false,
    slow: 0,
    armorShred: 0,
    burn: 0,
    scorch: 0,
    shield: 0,
    flying: false,
    air: false
  };
}

// Enemy A: Leading furthest along path (wp=8), distance = 2.0 (x=5.5, y=7.5), hp = 100
const foeA_First = createFoe('A', 5.5, 7.5, 100, 200, 8);
// Enemy B: Trailing nearest to spawn (wp=1), distance = 1.5 (x=5.5, y=4.0), hp = 200
const foeB_Last = createFoe('B', 5.5, 4.0, 200, 200, 1);
// Enemy C: Tankiest/highest HP (hp=500), wp=4, distance = 2.2 (x=7.7, y=5.5)
const foeC_Strongest = createFoe('C', 7.7, 5.5, 500, 500, 4);
// Enemy D: Weakest/lowest HP (hp=20), wp=5, distance = 2.1 (x=3.4, y=5.5)
const foeD_Weakest = createFoe('D', 3.4, 5.5, 20, 200, 5);
// Enemy E: Closest physical distance to tower (distance = 0.5, x=5.5, y=6.0), hp = 150, wp=3
const foeE_Closest = createFoe('E', 5.5, 6.0, 150, 200, 3);

const allFoes = [foeA_First, foeB_Last, foeC_Strongest, foeD_Weakest, foeE_Closest];

// Helper to simulate targeting update and check which foe is targeted
function getTargetForMode(mode) {
  tower.targetMode = mode;
  tower.cd = 0; // ready to acquire/fire
  // Deep clone foes for isolated test
  S.foes = allFoes.map(f => Object.assign({}, f, {
    mesh: {
      position: new global.THREE.Vector3(f.x, 0.5, f.y),
      rotation: { y: 0 },
      scale: { set: () => {}, x: 1, y: 1, z: 1 },
      material: { opacity: 1, color: { setHex: () => {} } },
      traverse: () => {},
      userData: {}
    }
  }));
  tower.beamTgt = null;
  // Run update for 0.05s
  api.update(0.05);
  return tower.lastTarget || S.foes.find(f => f.hp < f.maxHp);
}

// Mode: 'first' -> Expected: foeA_First
S.projs = [];
const targetFirst = getTargetForMode('first');
assert(targetFirst, 'Target should be acquired for "first"');
assert.strictEqual(targetFirst.id, 'A', `Mode 'first' must pick Foe A (furthest along path wp=8), picked ${targetFirst.id}`);
console.log('✓ Verified: "first" mode prioritizes highest waypoint path progression (Sanctum proximity)');

// Mode: 'last' -> Expected: foeB_Last
S.projs = [];
const targetLast = getTargetForMode('last');
assert(targetLast, 'Target should be acquired for "last"');
assert.strictEqual(targetLast.id, 'B', `Mode 'last' must pick Foe B (trailing enemy near spawn wp=1), picked ${targetLast.id}`);
console.log('✓ Verified: "last" mode prioritizes lowest waypoint path progression (Portal proximity)');

// Mode: 'strongest' -> Expected: foeC_Strongest
S.projs = [];
const targetStrongest = getTargetForMode('strongest');
assert(targetStrongest, 'Target should be acquired for "strongest"');
assert.strictEqual(targetStrongest.id, 'C', `Mode 'strongest' must pick Foe C (highest hp 500), picked ${targetStrongest.id}`);
console.log('✓ Verified: "strongest" mode prioritizes highest current HP');

// Mode: 'weakest' -> Expected: foeD_Weakest
S.projs = [];
const targetWeakest = getTargetForMode('weakest');
assert(targetWeakest, 'Target should be acquired for "weakest"');
assert.strictEqual(targetWeakest.id, 'D', `Mode 'weakest' must pick Foe D (lowest hp 20), picked ${targetWeakest.id}`);
console.log('✓ Verified: "weakest" mode prioritizes lowest current HP (execute priority)');

// Mode: 'closest' -> Expected: foeE_Closest
S.projs = [];
const targetClosest = getTargetForMode('closest');
assert(targetClosest, 'Target should be acquired for "closest"');
assert.strictEqual(targetClosest.id, 'E', `Mode 'closest' must pick Foe E (distance 0.5), picked ${targetClosest.id}`);
console.log('✓ Verified: "closest" mode prioritizes nearest Euclidean distance to the battery');

console.log('--- ALL TOWER TARGETING PRIORITY TESTS PASSED! ---');
process.exit(0);
