// Automated regression test for Issue #1: Pause does not fully freeze gameplay
const assert = require('assert');
const fs = require('fs');

console.log('--- Aegis Flora: Running Pause Gameplay-Mutation Regression Tests ---');

// Mock browser environment for game logic testing in Node
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
      get: (target, prop) => {
        if (prop in target) return target[prop];
        return () => {};
      }
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
  getItem: (k) => global.localStorage._data[k] || null,
  setItem: (k, v) => { global.localStorage._data[k] = String(v); },
  removeItem: (k) => { delete global.localStorage._data[k]; }
};

// Require Three.js
global.THREE = require('../js/three.min.js');
global.THREE.GLTFLoader = function() {
  this.load = () => {};
};
global.THREE.OrbitControls = function() {
  return {
    target: new global.THREE.Vector3(),
    update: () => {},
    addEventListener: () => {}
  };
};
global.THREE.WebGLRenderer = function() {
  const r = {
    domElement: makeEl('canvas'),
    setSize: () => {},
    setPixelRatio: () => {},
    render: () => {},
    shadowMap: {},
    outputEncoding: 0,
    toneMapping: 0,
    toneMappingExposure: 1
  };
  return new Proxy(r, {
    get: (target, prop) => {
      if (prop in target) return target[prop];
      return () => {};
    }
  });
};
global.document.createElementNS = (ns, tag) => global.document.createElement(tag);
global.AudioContext = function() {
  return {
    createOscillator: () => ({ connect: () => {}, start: () => {}, stop: () => {} }),
    createGain: () => ({ connect: () => {}, gain: { setValueAtTime: () => {}, exponentialRampToValueAtTime: () => {} } }),
    destination: {}
  };
};
global.webkitAudioContext = global.AudioContext;

// Load game code
const html = fs.readFileSync('game.html', 'utf8');
const startTag = '<script>';
const endTag = '</script>';
const startIdx = html.indexOf(startTag, html.indexOf('use strict') - 20);
const endIdx = html.lastIndexOf(endTag);
const jsCode = html.slice(startIdx + startTag.length, endIdx);

// Execute game script in test context
eval(jsCode);

console.log('Game initialized. Testing API and state...');
const API = global.AegisFlora || global.RoboFlora;
assert(API, 'AegisFlora API must be exported');

const S = API.newGame(100);
assert(S, 'Game state must exist');

// 1. Verify Unpaused State Behavior
console.log('1. Testing Unpaused Gameplay Mutations...');
assert.strictEqual(API.isPaused(), false, 'Game should initialize unpaused');
assert.strictEqual(API.canMutateGameplay('test', true), true, 'canMutateGameplay should return true when unpaused');

const startCash = S.cash;
const testX = 10, testY = 10;
const placeRes = API.placeAt(testX, testY, 'gun');
assert.strictEqual(placeRes.ok, true, 'Placement should succeed when unpaused');
assert(S.cash < startCash, 'Scrap should be deducted on placement');
const placedTower = S.towers.find(t => t.gx === testX && t.gy === testY);
assert(placedTower, 'Tower should be registered in state');

// 2. Pause Game & Verify Mutation Lockout
console.log('2. Testing Paused Mutation Lockout...');
API.togglePause(true);
assert.strictEqual(API.isPaused(), true, 'Game should be paused');
assert.strictEqual(API.canMutateGameplay('test', true), false, 'canMutateGameplay must return false when paused');

// Test A: Placement blocked
const cashBeforePlace = S.cash;
const towerCountBefore = S.towers.length;
const blockedPlace = API.placeAt(12, 10, 'gun');
assert.strictEqual(blockedPlace.ok, false, 'Placement must be rejected when paused');
assert.strictEqual(S.cash, cashBeforePlace, 'Cash must NOT change when placement rejected');
assert.strictEqual(S.towers.length, towerCountBefore, 'Tower count must NOT change when paused');

// Test B: canPlace check blocked
const canPlaceRes = API.canPlace(12, 10);
assert.strictEqual(canPlaceRes.ok, false, 'canPlace must return false when paused');

// Test C: Upgrade blocked
const cashBeforeUpgrade = S.cash;
const blockedUpgrade = API.upgradeTo(placedTower, 'A');
assert.strictEqual(blockedUpgrade.ok, false, 'Upgrade must be rejected when paused');
assert.strictEqual(S.cash, cashBeforeUpgrade, 'Cash must NOT change on blocked upgrade');
assert.strictEqual(placedTower.branch, 0, 'Tower branch must NOT change on blocked upgrade');

// Test D: Selling blocked
const blockedSell = API.sellTower(placedTower);
assert.strictEqual(blockedSell, false, 'Sell must be rejected when paused');
assert(S.towers.includes(placedTower), 'Tower must NOT be removed when sell is rejected');
assert.strictEqual(S.cash, cashBeforeUpgrade, 'Cash must NOT change on blocked sell');

// Test E: Wave start blocked
const waveBefore = S.wave;
const phaseBefore = S.phase;
const blockedWave = API.startWave();
assert.strictEqual(blockedWave, false, 'startWave must return false when paused');
assert.strictEqual(S.wave, waveBefore, 'Wave must NOT increment when paused');
assert.strictEqual(S.phase, phaseBefore, 'Phase must NOT change to combat when paused');

// Test F: Abilities blocked
const manaBefore = S.mana;
API.useSanctumAbility('root');
assert.strictEqual(S.mana, manaBefore, 'Mana must NOT be deducted for ability when paused');

// 3. Resume Game & Verify Gameplay Restored
console.log('3. Testing Resumed Gameplay Behavior...');
API.togglePause(false);
assert.strictEqual(API.isPaused(), false, 'Game should now be unpaused');
assert.strictEqual(API.canMutateGameplay('test', true), true, 'canMutateGameplay must return true after resuming');

const resumePlace = API.placeAt(14, 10, 'gun');
assert.strictEqual(resumePlace.ok, true, 'Placement should succeed after resuming');

console.log('--- ALL REGRESSION TESTS PASSED SUCCESSFULLY! ---');
process.exit(0);
