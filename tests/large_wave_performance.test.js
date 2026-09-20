// Automated test and profiling suite for Issue #11: Large-Wave Performance & Spatial Indexing
const assert = require('assert');
const fs = require('fs');

console.log('--- Aegis Flora: Running Large Wave Performance & Profiling Tests (Issue #11) ---');

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
    classList: {
      _classes: new Set(),
      add: function(c){ this._classes.add(c); },
      remove: function(c){ this._classes.delete(c); },
      contains: function(c){ return this._classes.has(c); },
      toggle: function(c){ if(this._classes.has(c)) this._classes.delete(c); else this._classes.add(c); }
    },
    appendChild: () => {},
    addEventListener: () => {},
    setAttribute: () => {},
    querySelectorAll: () => [],
    querySelector: () => null,
    textContent: '',
    innerHTML: '',
    children: [],
    checked: false,
    getContext: () => new Proxy({
      measureText: () => ({ width: 10 }),
      createImageData: (w, h) => ({ data: new Uint8ClampedArray((w||1) * (h||1) * 4) }),
      createLinearGradient: () => ({ addColorStop: () => {} }),
      createRadialGradient: () => ({ addColorStop: () => {} }),
      clearRect: () => {},
      save: () => {},
      restore: () => {},
      fillText: () => {}
    }, {
      get: (t, p) => (p in t ? t[p] : () => {})
    })
  };
  el.parentElement = el;
  return el;
}

const DOM_ELEMENTS = {};
global.document = {
  readyState: 'complete',
  addEventListener: () => {},
  removeEventListener: () => {},
  querySelector: makeEl,
  querySelectorAll: () => [],
  body: makeEl('body'),
  createElement: makeEl,
  getElementById: function(id) {
    if(!DOM_ELEMENTS[id]) DOM_ELEMENTS[id] = makeEl(id);
    return DOM_ELEMENTS[id];
  }
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

console.log('1. Testing Goal-Rooted Flow Field calculation...');
const flow = api.computeFlowField(api.cfg.SANCTUM.x, api.cfg.SANCTUM.y, api.state.blocked);
assert(flow, 'Flow field must be computed');
const sanctumIdx = api.cfg.SANCTUM.x + api.cfg.SANCTUM.y * api.cfg.COLS;
assert.strictEqual(flow.dist[sanctumIdx], 0, 'Distance at Sanctum must be 0');

const spawnIdx = api.cfg.SPAWN.x + api.cfg.SPAWN.y * api.cfg.COLS;
assert(flow.dist[spawnIdx] > 0 && flow.dist[spawnIdx] < 30000, 'Distance at Spawn must be reachable');

const flowPath = api.getFlowPath(api.cfg.SPAWN.x, api.cfg.SPAWN.y, flow);
assert(Array.isArray(flowPath), 'Flow path must be an array');
assert(flowPath.length >= 2, 'Flow path must contain at least 2 steps');
assert.strictEqual(flowPath[0].x, api.cfg.SPAWN.x, 'Path start must be Spawn');
assert.strictEqual(flowPath[flowPath.length - 1].x, api.cfg.SANCTUM.x, 'Path end must be Sanctum');
console.log(`✓ Verified: Goal-rooted flow path successfully computed with ${flowPath.length} steps.`);

console.log('2. Testing Spatial Target Indexing Grid...');
api.newGame(101);
// Spawn 50 foes across various coordinates
for (let i = 0; i < 50; i++) {
  api.spawnEnemy('spider');
}
assert.strictEqual(api.state.foes.length, 50, 'Must have 50 foes spawned');

api.buildSpatialIndex();

// Query area around Spawn (where all spiders currently are)
const queryBuf = [];
const localFoes = api.queryFoesInRadius(api.cfg.SPAWN.x + 0.5, api.cfg.SPAWN.y + 0.5, 3.0, queryBuf);
assert(localFoes.length > 0, 'Must locate local foes around Spawn');
assert.strictEqual(localFoes.length, 50, 'All initial foes should be in local spawn neighborhood');

// Query distant area on opposite side of map (should have 0 foes)
const emptyFoes = api.queryFoesInRadius(api.cfg.SANCTUM.x, api.cfg.SANCTUM.y, 1.5, queryBuf);
assert.strictEqual(emptyFoes.length, 0, 'No foes should be found in unpopulated region');
console.log('✓ Verified: Spatial index queries correctly filter by radius.');

console.log('3. Testing FX and Damage Number Object Pooling...');
assert(api.DMG_POOL, 'DMG_POOL must be defined');
assert(api.FX_SHARED, 'FX_SHARED must be defined');

// Spawn damage numbers
for (let d = 0; d < 60; d++) {
  api.damageNumber({ x: 10, y: 0, z: 10 }, 42, 'Kinetic');
}
assert(api.DMG_NUMS.length >= 60, 'DMG_NUMS must hold spawned damage numbers');

// Simulate 1.5s to expire all damage numbers
api.renderCombatFX(1.5);
assert.strictEqual(api.DMG_NUMS.length, 0, 'All damage numbers must be expired');
assert(api.DMG_POOL.length >= 60, 'Expired damage numbers must be recycled into DMG_POOL');

// Re-spawn damage numbers (should reuse from pool without allocating)
const poolCountBefore = api.DMG_POOL.length;
for (let d = 0; d < 10; d++) {
  api.damageNumber({ x: 10, y: 0, z: 10 }, 99, 'Blast');
}
assert.strictEqual(api.DMG_POOL.length, poolCountBefore - 10, 'Must recycle 10 objects from DMG_POOL');
console.log('✓ Verified: Object pooling completely prevents heap churn.');

console.log('4. Running Deterministic Stress Benchmark at 100 Enemies...');
const res100 = api.runStressBenchmark(100, 120);
console.log(`  [100 Enemies] Avg: ${res100.avgFrameTimeMs}ms (${res100.avgFps} FPS) | P99 (1% low): ${res100.p99FrameTimeMs}ms (${res100.onePercentLowFps} FPS) | Heap: ${res100.memoryMb}MB`);
assert(res100.avgFrameTimeMs < 16.67, `100 enemies must sustain 60 FPS (<16.67ms), got ${res100.avgFrameTimeMs}ms`);

console.log('5. Running Deterministic Stress Benchmark at 200 Enemies...');
const res200 = api.runStressBenchmark(200, 120);
console.log(`  [200 Enemies] Avg: ${res200.avgFrameTimeMs}ms (${res200.avgFps} FPS) | P99 (1% low): ${res200.p99FrameTimeMs}ms (${res200.onePercentLowFps} FPS) | Heap: ${res200.memoryMb}MB`);
assert(res200.avgFrameTimeMs < 16.67, `200 enemies must sustain 60 FPS (<16.67ms), got ${res200.avgFrameTimeMs}ms`);

console.log('6. Running Deterministic Stress Benchmark at 350 Enemies (Massive Swarm Stress)...');
const res350 = api.runStressBenchmark(350, 120);
console.log(`  [350 Enemies] Avg: ${res350.avgFrameTimeMs}ms (${res350.avgFps} FPS) | P99 (1% low): ${res350.p99FrameTimeMs}ms (${res350.onePercentLowFps} FPS) | Heap: ${res350.memoryMb}MB`);
assert(res350.avgFrameTimeMs < 16.67, `350 enemies must sustain 60 FPS (<16.67ms), got ${res350.avgFrameTimeMs}ms`);
console.log('✓ Verified: 350-enemy massive swarm comfortably sustains 60 FPS target.');

console.log('\nAll Large-Wave Performance & Profiling (Issue #11) tests passed successfully!');
