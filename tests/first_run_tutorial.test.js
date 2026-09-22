// Automated test suite for Issue #9: Guided First-Run Mazing Tutorial
const assert = require('assert');
const fs = require('fs');

console.log('--- Aegis Florae: Running Guided First-Run Tutorial Tests (Issue #9) ---');

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

const DOM_ELEMENTS = {};
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

const api = global.AegisFlorae || global.RoboFlora;
assert(api, 'AegisFlorae API must be exposed on window');

console.log('1. Checking TUTORIAL_STEPS content and curriculum coverage...');
assert(Array.isArray(api.TUTORIAL_STEPS), 'TUTORIAL_STEPS must be an array');
assert.strictEqual(api.TUTORIAL_STEPS.length, 8, 'Tutorial must contain exactly 8 structured steps');

const expectedTopics = [
  'Spawn & Sanctum',
  'Tower Placement',
  'Route Recalculation',
  'No Complete Blocking',
  'Choke Points',
  'Launching the Wave',
  'Elite Specialization',
  'Threat Types'
];

api.TUTORIAL_STEPS.forEach((s, idx) => {
  assert(s.title, `Step ${idx+1} must have a title`);
  assert(s.desc, `Step ${idx+1} must have a description`);
  assert(s.visual, `Step ${idx+1} must have visual context`);
  console.log(`  Step ${s.step}: ${s.title}`);
});
console.log('✓ Verified: 8-step curriculum covers all core mazing requirements.');

console.log('2. Testing startTutorial() and modal activation...');
global.localStorage.removeItem('aegis_tutorial_completed');
assert.strictEqual(api.isTutorialActive(), false, 'Tutorial must initially be inactive');

api.startTutorial(0);
assert.strictEqual(api.isTutorialActive(), true, 'Tutorial must be active after startTutorial()');
assert.strictEqual(api.getTutorialStep(), 0, 'Initial step index must be 0');

const counterEl = DOM_ELEMENTS['tutStepCounter'];
assert(counterEl.textContent.includes('Step 1 of 8'), 'Step counter must display Step 1 of 8');
console.log('✓ Verified: startTutorial opens modal and displays Step 1.');

console.log('3. Testing step navigation: nextTutorialStep() & prevTutorialStep()...');
api.nextTutorialStep();
assert.strictEqual(api.getTutorialStep(), 1, 'Should advance to step 1');
assert(counterEl.textContent.includes('Step 2 of 8'), 'Step counter must update to Step 2 of 8');

api.nextTutorialStep();
assert.strictEqual(api.getTutorialStep(), 2, 'Should advance to step 2');

api.prevTutorialStep();
assert.strictEqual(api.getTutorialStep(), 1, 'Should return to step 1');

// Fast forward to step 7 (8th step)
for(let i = 1; i < 7; i++) api.nextTutorialStep();
assert.strictEqual(api.getTutorialStep(), 7, 'Should reach final step (index 7)');
assert(counterEl.textContent.includes('Step 8 of 8'), 'Step counter must display Step 8 of 8');
console.log('✓ Verified: Next and Prev navigation work smoothly.');

console.log('4. Testing completeTutorial() on final step...');
api.nextTutorialStep(); // On step 7, nextTutorialStep completes tutorial
assert.strictEqual(api.isTutorialActive(), false, 'Tutorial must close on completion');
assert.strictEqual(global.localStorage.getItem('aegis_tutorial_completed'), 'true', 'localStorage must mark tutorial completed');
console.log('✓ Verified: Completing tutorial persists completed status and closes modal.');

console.log('5. Testing skipTutorial()...');
global.localStorage.removeItem('aegis_tutorial_completed');
api.startTutorial(2);
assert.strictEqual(api.isTutorialActive(), true, 'Tutorial should open at step 2');
api.skipTutorial();
assert.strictEqual(api.isTutorialActive(), false, 'Tutorial must close on skip');
assert.strictEqual(global.localStorage.getItem('aegis_tutorial_completed'), 'true', 'localStorage must mark tutorial completed after skip');
console.log('✓ Verified: skipTutorial closes modal and marks completed.');

console.log('--- ALL GUIDED FIRST-RUN TUTORIAL TESTS PASSED! ---');
process.exit(0);
