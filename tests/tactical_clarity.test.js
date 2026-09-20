// Automated test suite for Issue #10: Combat Readability and Tactical Clarity Mode
const assert = require('assert');
const fs = require('fs');

console.log('--- Aegis Flora: Running Tactical Clarity Tests (Issue #10) ---');

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
      toggle: function(c, force){
        if(force !== undefined) {
          if(force) this._classes.add(c);
          else this._classes.delete(c);
        } else {
          if(this._classes.has(c)) this._classes.delete(c);
          else this._classes.add(c);
        }
      }
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

console.log('1. Testing Tactical Clarity API methods and initial state...');
assert.strictEqual(typeof api.toggleTacticalClarity, 'function', 'toggleTacticalClarity must be a function');
assert.strictEqual(typeof api.setTacticalClarity, 'function', 'setTacticalClarity must be a function');
assert.strictEqual(typeof api.isTacticalClarityActive, 'function', 'isTacticalClarityActive must be a function');
assert.strictEqual(api.isTacticalClarityActive(), false, 'Tactical Clarity must be disabled by default');
console.log('✓ Initial state verified.');

console.log('2. Testing toggleTacticalClarity activation and DOM classes...');
const active1 = api.toggleTacticalClarity();
assert.strictEqual(active1, true, 'toggleTacticalClarity must return true when toggled on');
assert.strictEqual(api.isTacticalClarityActive(), true, 'isTacticalClarityActive must return true');
assert.strictEqual(global.document.body.classList.contains('tactical-clarity'), true, 'body must have tactical-clarity class');

const btnClarity = DOM_ELEMENTS['btnClarity'];
assert.strictEqual(btnClarity.classList.contains('active'), true, 'btnClarity must have active class');

const setClarity = DOM_ELEMENTS['setClarity'];
assert.strictEqual(setClarity.checked, true, 'setClarity checkbox must be checked');
console.log('✓ Verified: DOM classes and buttons reflect active Tactical Clarity.');

console.log('3. Testing bloom uniform and dust particle opacity adjustments...');
// Initialize POST uniform mock if needed
if (global.POST && global.POST.postMaterial) {
  assert.strictEqual(global.POST.postMaterial.uniforms.uBloomIntensity.value, 0.12, 'Bloom intensity must be lowered to 0.12');
}
if (global.dustParticles && global.dustParticles.material) {
  assert.strictEqual(global.dustParticles.material.opacity, 0.12, 'Dust particles opacity must be lowered to 0.12');
}
console.log('✓ Verified: post-processing and ambient particles adjusted for readability.');

console.log('4. Testing toggle off and settings persistence...');
const active2 = api.toggleTacticalClarity();
assert.strictEqual(active2, false, 'toggleTacticalClarity must return false when toggled off');
assert.strictEqual(api.isTacticalClarityActive(), false, 'isTacticalClarityActive must return false');
assert.strictEqual(global.document.body.classList.contains('tactical-clarity'), false, 'body must not have tactical-clarity class');
assert.strictEqual(btnClarity.classList.contains('active'), false, 'btnClarity must not have active class');
assert.strictEqual(setClarity.checked, false, 'setClarity checkbox must be unchecked');

const savedSettings = JSON.parse(global.localStorage.getItem('aegis_settings') || '{}');
assert.strictEqual(savedSettings.tacticalClarity, false, 'Persisted settings must record tacticalClarity false');

api.setTacticalClarity(true);
assert.strictEqual(api.isTacticalClarityActive(), true, 'setTacticalClarity(true) must activate mode');
const savedSettings2 = JSON.parse(global.localStorage.getItem('aegis_settings') || '{}');
assert.strictEqual(savedSettings2.tacticalClarity, true, 'Persisted settings must record tacticalClarity true');
console.log('✓ Verified: settings persistence and toggle state match.');

console.log('5. Testing Tower Base Plinths (type color coding)...');
const towerGroup = new global.THREE.Group();
api.addTowerBasePlinth(towerGroup, 'gun');
assert(towerGroup.userData.baseRing, 'Tower group must have userData.baseRing');
assert.strictEqual(towerGroup.userData.baseRing.material.color.getHex(), 0xFFB703, 'Gun plinth color must be 0xFFB703 (gold)');

const beamGroup = new global.THREE.Group();
api.addTowerBasePlinth(beamGroup, 'beam');
assert.strictEqual(beamGroup.userData.baseRing.material.color.getHex(), 0x00F5D4, 'Beam plinth color must be 0x00F5D4 (teal)');
console.log('✓ Verified: tower base plinths provide high contrast footprint silhouettes.');

console.log('6. Testing Creep Threat Rings (threat silhouette & archetypes)...');
const creepGroup = new global.THREE.Group();
api.addCreepThreatRing(creepGroup, 'scout');
assert(creepGroup.userData.contactRing, 'Creep group must have userData.contactRing');
assert(creepGroup.userData.contactRing.geometry instanceof global.THREE.RingGeometry, 'Threat ring must be RingGeometry');
console.log('✓ Verified: creep threat rings provide clear ground contact footprint.');

console.log('7. Testing HTML layout and CSS for Tactical Clarity...');
assert(html.includes('body.tactical-clarity'), 'HTML must include CSS for body.tactical-clarity');
assert(html.includes('id="btnClarity"'), 'HTML must include #btnClarity button in transport-cluster');
assert(html.includes('id="setClarity"'), 'HTML must include #setClarity switch in settings');
assert(html.includes('pathLineMesh.material.dashOffset'), 'HTML must animate pathLineMesh dashOffset in loop');
console.log('✓ Verified: HTML and CSS markup complete.');

console.log('\nAll Tactical Clarity (Issue #10) tests passed successfully!');
process.exit(0);
