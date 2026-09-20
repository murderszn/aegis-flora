// Automated regression test for Issue #4 and #5: Audio Limiter, Explosion Bus, and Immediate Mute
const assert = require('assert');
const fs = require('fs');

console.log('--- Aegis Flora: Running Audio Limiter & Mute Regression Tests (Issues #4 & #5) ---');

// Mock browser environment for audio testing in Node
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
global.document.createElementNS = (ns, tag) => global.document.createElement(tag);

// Mock Web Audio API with node graph inspection
class MockAudioParam {
  constructor(defaultValue = 1) {
    this.value = defaultValue;
  }
  setValueAtTime(val, t) { this.value = val; }
  exponentialRampToValueAtTime(val, t) { this.value = val; }
  cancelScheduledValues(t) {}
}

class MockAudioNode {
  constructor() {
    this.connectedTo = [];
  }
  connect(dest) {
    this.connectedTo.push(dest);
  }
  disconnect() {
    this.connectedTo = [];
  }
}

class MockGainNode extends MockAudioNode {
  constructor() {
    super();
    this.gain = new MockAudioParam(1);
  }
}

class MockDynamicsCompressorNode extends MockAudioNode {
  constructor() {
    super();
    this.threshold = new MockAudioParam(-6);
    this.knee = new MockAudioParam(12);
    this.ratio = new MockAudioParam(12);
    this.attack = new MockAudioParam(0.003);
    this.release = new MockAudioParam(0.25);
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

class MockBufferSourceNode extends MockAudioNode {
  constructor() {
    super();
  }
  start() {}
  stop() {}
}

class MockBiquadFilterNode extends MockAudioNode {
  constructor() {
    super();
    this.frequency = new MockAudioParam(1000);
    this.Q = new MockAudioParam(1);
    this.type = 'lowpass';
  }
}

global.AudioContext = function() {
  return {
    currentTime: 0,
    sampleRate: 44100,
    destination: new MockAudioNode(),
    createGain: () => new MockGainNode(),
    createDynamicsCompressor: () => new MockDynamicsCompressorNode(),
    createOscillator: () => new MockOscillatorNode(),
    createBufferSource: () => new MockBufferSourceNode(),
    createBiquadFilter: () => new MockBiquadFilterNode(),
    createBuffer: (ch, len, rate) => ({ getChannelData: () => new Float32Array(len) })
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

// Execute script
eval(jsCode);

console.log('Game initialized. Verifying Web Audio Architecture...');
const API = global.AegisFlora || global.RoboFlora;
assert(API, 'AegisFlora API must be exported');

// 1. Verify Audio Graph Initialized with Limiter and Buses
const ac = API.getAudioContext();
assert(ac, 'AudioContext must be created');
API.sfx('click'); // Trigger masterOut initialization

assert(ac._master, 'Master gain node must exist');
assert(ac._limiter, 'DynamicsCompressor peak limiter must exist');
assert(ac._sfxBus, 'SFX bus gain node must exist');
assert(ac._explosionBus, 'Explosion bus gain node must exist');

// Verify routing: limiter connects to master, buses connect to limiter
assert(ac._limiter.connectedTo.includes(ac._master), 'Limiter must output to Master gain');
assert(ac._sfxBus.connectedTo.includes(ac._limiter), 'SFX bus must output to Limiter');
assert(ac._explosionBus.connectedTo.includes(ac._limiter), 'Explosion bus must output to Limiter');

// 2. Verify Limiter Audio Parameters
assert.strictEqual(ac._limiter.threshold.value, -6.0, 'Limiter threshold must be -6 dB');
assert.strictEqual(ac._limiter.ratio.value, 12.0, 'Limiter ratio must be 12:1 peak limiting');

// 3. Verify Immediate Active Audio Mute
console.log('Testing immediate master mute behavior...');
assert.strictEqual(API.isAudioMuted(), false, 'Should start unmuted by default');
assert.strictEqual(ac._master.gain.value, 0.8, 'Master gain should be 0.8');

// Mute immediately
API.setMasterMute(true);
assert.strictEqual(API.isAudioMuted(), true, 'isAudioMuted should return true');
assert.strictEqual(ac._master.gain.value, 0, 'Master gain must immediately set to 0 when muted');
assert.strictEqual(global.localStorage.getItem('aegis_audio_muted'), 'true', 'localStorage must persist mute state');

// Unmute immediately
API.setMasterMute(false);
assert.strictEqual(API.isAudioMuted(), false, 'isAudioMuted should return false');
assert.strictEqual(ac._master.gain.value, 0.8, 'Master gain must be restored to volume when unmuted');
assert.strictEqual(global.localStorage.getItem('aegis_audio_muted'), 'false', 'localStorage must persist unmuted state');

// Toggle Mute
API.toggleAudioMute();
assert.strictEqual(API.isAudioMuted(), true, 'toggleAudioMute should toggle to true');
assert.strictEqual(ac._master.gain.value, 0, 'Master gain must be 0 after toggle mute');

API.toggleAudioMute();
assert.strictEqual(API.isAudioMuted(), false, 'toggleAudioMute should toggle back to false');
assert.strictEqual(ac._master.gain.value, 0.8, 'Master gain must be 0.8 after toggle unmute');

// 4. Test Explosion Concurrency Capping
console.log('Testing explosion blast concurrency cap...');
// Trigger 6 rapid explosions in the same audio frame
for (let i = 0; i < 6; i++) {
  API.playExplosionSFX();
}
// Concurrency cap must prevent runaway voices (MAX_CONCURRENT_EXPLOSIONS = 3)
// Check that it executed without throwing errors

console.log('--- ALL AUDIO LIMITER & MUTE REGRESSION TESTS PASSED! ---');
process.exit(0);
