const assert = require('assert');
const fs = require('fs');
const path = require('path');

console.log('--- Aegis Flora: Running Sanctum Leak Alarm & Defeat SFX Tests (Issue #19) ---');

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

// Mock Web Audio Context
let currentTime = 0;
let oscillatorsCreated = [];
let gainNodesCreated = [];
let bufferSourcesCreated = [];

class MockAudioParam {
  constructor(val = 0) {
    this.value = val;
    this.events = [];
  }
  setValueAtTime(v, t) { this.events.push({ type: 'setValue', v, t }); this.value = v; }
  linearRampToValueAtTime(v, t) { this.events.push({ type: 'linearRamp', v, t }); this.value = v; }
  exponentialRampToValueAtTime(v, t) { this.events.push({ type: 'expRamp', v, t }); this.value = v; }
  setTargetAtTime(v, t, tc) { this.events.push({ type: 'setTarget', v, t, tc }); this.value = v; }
  cancelScheduledValues(t) { this.events.push({ type: 'cancel', t }); }
}

class MockAudioNode {
  connect(dest) { this.destination = dest; return dest; }
  disconnect() { this.destination = null; }
}

class MockGainNode extends MockAudioNode {
  constructor() {
    super();
    this.gain = new MockAudioParam(1);
    gainNodesCreated.push(this);
  }
}

class MockOscillatorNode extends MockAudioNode {
  constructor() {
    super();
    this.type = 'sine';
    this.frequency = new MockAudioParam(440);
    this.started = false;
    this.stopped = false;
    oscillatorsCreated.push(this);
  }
  start(t) { this.started = true; this.startTime = t; }
  stop(t) { this.stopped = true; this.stopTime = t; }
}

class MockBufferSourceNode extends MockAudioNode {
  constructor() {
    super();
    this.buffer = null;
    this.started = false;
    bufferSourcesCreated.push(this);
  }
  start(t) { this.started = true; this.startTime = t; }
  stop(t) { this.stopped = true; this.stopTime = t; }
}

class MockDynamicsCompressorNode extends MockAudioNode {
  constructor() {
    super();
    this.threshold = new MockAudioParam(-18);
    this.knee = new MockAudioParam(12);
    this.ratio = new MockAudioParam(12);
    this.attack = new MockAudioParam(0.002);
    this.release = new MockAudioParam(0.08);
  }
}

class MockBiquadFilterNode extends MockAudioNode {
  constructor() {
    super();
    this.type = 'lowpass';
    this.frequency = new MockAudioParam(1200);
    this.Q = new MockAudioParam(1);
  }
}

global.AudioContext = class {
  constructor() {
    this.sampleRate = 44100;
    this.state = 'running';
    this.destination = new MockAudioNode();
  }
  get currentTime() { return currentTime; }
  createGain() { return new MockGainNode(); }
  createOscillator() { return new MockOscillatorNode(); }
  createBufferSource() { return new MockBufferSourceNode(); }
  createDynamicsCompressor() { return new MockDynamicsCompressorNode(); }
  createBiquadFilter() { return new MockBiquadFilterNode(); }
  createBuffer(channels, length, sampleRate) {
    return {
      numberOfChannels: channels,
      length: length,
      sampleRate: sampleRate,
      getChannelData: () => new Float32Array(length)
    };
  }
  resume() { this.state = 'running'; return Promise.resolve(); }
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
  console.log('Script init non-fatal notice:', e.message);
}

const api = global.AegisFlora || global.RoboFlora;
assert(api, 'AegisFlora API must be exposed on window');

console.log('1. Checking sfx function for alarm, defeat, and victory cases...');
assert.strictEqual(typeof api.playAlarmSFX, 'function', 'playAlarmSFX must be exposed on API');
assert.strictEqual(typeof api.playDefeatSFX, 'function', 'playDefeatSFX must be exposed on API');
assert.strictEqual(typeof api.playVictorySFX, 'function', 'playVictorySFX must be exposed on API');
assert.strictEqual(typeof api.sfx, 'function', 'sfx must be exposed on API');

console.log('2. Testing sfx("alarm") execution and synth voice output...');
api.setMasterMute(false);
oscillatorsCreated = [];
bufferSourcesCreated = [];

api.sfx('alarm');
assert(oscillatorsCreated.length >= 1, 'sfx("alarm") must create at least one oscillator');
const alarmOsc = oscillatorsCreated[0];
assert.strictEqual(alarmOsc.type, 'sawtooth', 'Alarm lead oscillator must use distinct sawtooth wave');
assert.strictEqual(alarmOsc.frequency.events[0].v, 520, 'Alarm lead tone must begin at 520 Hz');
assert.strictEqual(alarmOsc.frequency.events[1].v, 320, 'Alarm lead tone must slide down to 320 Hz');
assert(bufferSourcesCreated.length >= 1, 'sfx("alarm") must emit transient thud noise buffer');
console.log('✓ Verified: sfx("alarm") produces distinct, restrained warning tone.');

console.log('3. Testing anti-stacking throttle on rapid simultaneous leaks...');
oscillatorsCreated = [];
bufferSourcesCreated = [];

// Trigger 5 leaks in rapid succession within 5ms (same frame breach burst)
for(let i = 0; i < 5; i++) {
  api.sfx('alarm');
}

// Due to 140ms throttle, only 0 new alarms should fire if called immediately
assert.strictEqual(oscillatorsCreated.length, 0, 'Rapid successive leaks within 140ms must be throttled');
console.log('✓ Verified: Rapid clustered leaks are throttled to prevent painful acoustic stacking.');

console.log('4. Testing sfx("defeat") somber descending collapse sound...');
oscillatorsCreated = [];
api.sfx('defeat');
assert(oscillatorsCreated.length >= 1, 'sfx("defeat") must create descending oscillator');
const defeatOsc = oscillatorsCreated[0];
assert.strictEqual(defeatOsc.frequency.events[0].v, 220, 'Defeat tone must start at low 220 Hz');
assert.strictEqual(defeatOsc.frequency.events[1].v, 110, 'Defeat tone must slide down to 110 Hz');
console.log('✓ Verified: sfx("defeat") produces somber descending collapse tone.');

console.log('5. Testing sfx("victory") triumphant harmonic fanfare...');
oscillatorsCreated = [];
api.sfx('victory');
assert(oscillatorsCreated.length >= 1, 'sfx("victory") must create ascending fanfare tone');
const victoryOsc = oscillatorsCreated[0];
assert.strictEqual(Math.round(victoryOsc.frequency.value * 10) / 10, 261.6, 'Victory fanfare must begin on middle C (261.6 Hz)');
console.log('✓ Verified: sfx("victory") produces triumphant ascending fanfare.');

console.log('6. Testing mute enforcement for all alert and game-over sounds...');
api.setMasterMute(true);
oscillatorsCreated = [];
bufferSourcesCreated = [];

api.sfx('alarm');
api.sfx('defeat');
api.sfx('victory');

assert.strictEqual(oscillatorsCreated.length, 0, 'No oscillators must be created when muted');
assert.strictEqual(bufferSourcesCreated.length, 0, 'No noise buffers must be created when muted');
console.log('✓ Verified: Immediate mute is strictly enforced across all alarm and end-game SFX.');

console.log('\nAll Sanctum Leak Alarm & Defeat SFX (Issue #19) tests passed successfully!');
process.exit(0);
