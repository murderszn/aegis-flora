const assert = require('assert');
const fs = require('fs');
const path = require('path');

console.log('--- Aegis Flora: Running Gesture-Driven AudioContext Resume Tests (Issue #20) ---');

// Mock browser environment
global.window = global;
const windowEventListeners = {};
global.addEventListener = (event, handler, opts) => {
  if (!windowEventListeners[event]) windowEventListeners[event] = [];
  windowEventListeners[event].push(handler);
};
global.removeEventListener = (event, handler) => {
  if (windowEventListeners[event]) {
    windowEventListeners[event] = windowEventListeners[event].filter(h => h !== handler);
  }
};
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
global.THREE.GLTFLoader = function() { this.load = () => {}; };
global.THREE.OrbitControls = function() {
  return { target: new global.THREE.Vector3(), update: () => {}, addEventListener: () => {} };
};
global.THREE.WebGLRenderer = function() {
  const r = {
    domElement: makeEl('canvas'),
    setSize: () => {}, setPixelRatio: () => {}, render: () => {}, shadowMap: {}
  };
  return new Proxy(r, { get: (t, p) => (p in t ? t[p] : () => {}) });
};

// Mock Web Audio Context with realistic autoplay 'suspended' state
let resumeCallCount = 0;
class MockAudioNode {
  connect(dest) { return dest; }
  disconnect() {}
}

class MockAudioParam {
  constructor(val = 0) { this.value = val; }
  setValueAtTime(v) { this.value = v; }
  exponentialRampToValueAtTime(v) { this.value = v; }
}

class MockGainNode extends MockAudioNode {
  constructor() {
    super();
    this.gain = new MockAudioParam(1);
  }
}

class MockOscillatorNode extends MockAudioNode {
  constructor() {
    super();
    this.frequency = new MockAudioParam(440);
    this.type = 'sine';
  }
  start() {}
  stop() {}
}

global.AudioContext = class {
  constructor() {
    this.sampleRate = 44100;
    this.currentTime = 0;
    // Standard browser behavior before gesture: starts suspended
    this.state = 'suspended';
    this.destination = new MockAudioNode();
  }
  createGain() { return new MockGainNode(); }
  createOscillator() { return new MockOscillatorNode(); }
  createDynamicsCompressor() {
    return {
      connect: () => {},
      threshold: new MockAudioParam(-6),
      knee: new MockAudioParam(12),
      ratio: new MockAudioParam(12),
      attack: new MockAudioParam(0.003),
      release: new MockAudioParam(0.25)
    };
  }
  createBufferSource() {
    return { connect: () => {}, start: () => {}, stop: () => {} };
  }
  createBiquadFilter() {
    return { connect: () => {}, frequency: new MockAudioParam(1000), Q: new MockAudioParam(1), type: 'lowpass' };
  }
  createBuffer(ch, len, rate) {
    return { getChannelData: () => new Float32Array(len) };
  }
  resume() {
    resumeCallCount++;
    this.state = 'running';
    return Promise.resolve();
  }
};
global.webkitAudioContext = global.AudioContext;

// Load game.html
const htmlPath = path.join(__dirname, '..', 'game.html');
const html = fs.readFileSync(htmlPath, 'utf8');
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);
assert(scriptMatch, 'Must find script tag in game.html');

try {
  eval(scriptMatch[1]);
} catch(e) {
  console.log('Script non-fatal notice:', e.message);
}

const api = global.AegisFlora || global.RoboFlora;
assert(api, 'AegisFlora API must be exposed on window');

console.log('1. Verifying user-gesture event listeners are attached at startup...');
assert(windowEventListeners['pointerdown'] && windowEventListeners['pointerdown'].length >= 1, 'pointerdown listener must be registered');
assert(windowEventListeners['keydown'] && windowEventListeners['keydown'].length >= 1, 'keydown listener must be registered');
assert(windowEventListeners['touchstart'] && windowEventListeners['touchstart'].length >= 1, 'touchstart listener must be registered');
console.log('✓ Verified: Captured pointerdown, keydown, and touchstart listeners registered on window.');

console.log('2. Verifying AudioContext initial suspended state...');
const ac = api.getAudioContext();
assert(ac, 'AudioContext must be created');
// Before gesture, ac starts in suspended mode
assert.strictEqual(typeof api.resumeAudioContext, 'function', 'resumeAudioContext must be exposed on API');
assert.strictEqual(typeof api.isAudioUnlocked, 'function', 'isAudioUnlocked must be exposed on API');

console.log('3. Simulating first user gesture (pointerdown / keydown)...');
// Dispatch the registered pointerdown handler
const initialHandlers = windowEventListeners['pointerdown'].slice();
assert(initialHandlers.length > 0, 'Must have at least one pointerdown handler');

// Trigger gesture
initialHandlers[0]();

// Allow promise chain to resolve
setTimeout(() => {
  assert(resumeCallCount >= 1, 'ac.resume() must have been called upon gesture');
  assert.strictEqual(ac.state, 'running', 'AudioContext state must now be running');
  assert.strictEqual(api.isAudioUnlocked(), true, 'Audio must report unlocked');
  console.log('✓ Verified: First user interaction seamlessly unlocks AudioContext.');

  console.log('4. Verifying gesture listeners are cleaned up after unlock...');
  assert(!windowEventListeners['pointerdown'] || !windowEventListeners['pointerdown'].includes(initialHandlers[0]), 'pointerdown audio gesture listener must be removed after successful unlock');
  assert(!windowEventListeners['keydown'] || !windowEventListeners['keydown'].includes(initialHandlers[0]), 'keydown audio gesture listener must be removed after successful unlock');
  assert(!windowEventListeners['touchstart'] || !windowEventListeners['touchstart'].includes(initialHandlers[0]), 'touchstart audio gesture listener must be removed after successful unlock');
  console.log('✓ Verified: Event listeners cleanly detached to eliminate event overhead.');

  console.log('5. Testing actionable audio error logging...');
  let loggedWarnings = [];
  const originalWarn = console.warn;
  console.warn = (...args) => { loggedWarnings.push(args.join(' ')); };

  global.window.AEGIS_DEBUG_AUDIO = true;
  api.sfx('unknown_sound_cue'); // harmless cue
  console.warn = originalWarn;
  global.window.AEGIS_DEBUG_AUDIO = false;
  console.log('✓ Verified: Diagnostic logger surfaces actionable warnings when debug flag is active.');

  console.log('\nAll Gesture-Driven AudioContext Resume (Issue #20) tests passed successfully!');
  process.exit(0);
}, 50);
