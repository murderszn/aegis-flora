const assert = require('assert');
const fs = require('fs');
const path = require('path');

console.log('--- Aegis Florae: Claude FM Radio & Rumble Tuning Tests ---');

// Mock browser environment
global.window = global;
global.addEventListener = () => {};
global.removeEventListener = () => {};
global.requestAnimationFrame = (fn) => setTimeout(fn, 16);
global.cancelAnimationFrame = (id) => clearTimeout(id);
global.innerWidth = 1920;
global.innerHeight = 1080;

const DOM_ELEMENTS = {};

function makeEl(tag) {
  const el = {
    style: {},
    classList: {
      _classes: new Set(),
      add: function(c) { this._classes.add(c); },
      remove: function(c) { this._classes.delete(c); },
      contains: function(c) { return this._classes.has(c); },
      toggle: function(c, force) {
        if(force !== undefined){ if(force) this._classes.add(c); else this._classes.delete(c); }
        else if(this._classes.has(c)) this._classes.delete(c);
        else this._classes.add(c);
      }
    },
    appendChild: (c) => el.children.push(c),
    addEventListener: () => {},
    setAttribute: () => {},
    textContent: '',
    innerHTML: '',
    value: '75',
    type: 'range',
    checked: false,
    children: [],
    querySelector: (sel) => makeEl('div'),
    querySelectorAll: () => [],
    getContext: () => new Proxy({
      measureText: () => ({ width: 10 }),
      createImageData: (w, h) => ({ data: new Uint8ClampedArray((w||1) * (h||1) * 4) }),
      createLinearGradient: () => ({ addColorStop: () => {} }),
      createRadialGradient: () => ({ addColorStop: () => {} }),
      clearRect: () => {},
      fillRect: () => {},
      fillText: () => {}
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

// Register Claude FM DOM elements so init() can find them
DOM_ELEMENTS['btnClaudeRadio'] = makeEl('button');
DOM_ELEMENTS['claude-fm-popover'] = makeEl('div');
DOM_ELEMENTS['btnClaudeFmClose'] = makeEl('button');
DOM_ELEMENTS['btnClaudeFmTogglePlay'] = makeEl('button');
DOM_ELEMENTS['claudeFmVolSlider'] = makeEl('input');
DOM_ELEMENTS['claudeFmVolLabel'] = makeEl('span');
DOM_ELEMENTS['claudeFmDot'] = makeEl('span');
// Claude FM iframe - mock with a postMessage stub
const iframeEl = makeEl('iframe');
iframeEl.contentWindow = { postMessage: function(){} };
DOM_ELEMENTS['claude-fm-iframe'] = iframeEl;

// Standard elements required by game.html
DOM_ELEMENTS['bosshp'] = makeEl('div');
DOM_ELEMENTS['bossFill'] = makeEl('div');
DOM_ELEMENTS['bossPhaseBadge'] = makeEl('div');
DOM_ELEMENTS['bossShieldFill'] = makeEl('div');
DOM_ELEMENTS['bossMechanicDesc'] = makeEl('span');
DOM_ELEMENTS['bossHpNumbers'] = makeEl('span');
DOM_ELEMENTS['wavebanner'] = makeEl('div');
DOM_ELEMENTS['statCreepRoster'] = makeEl('div');
DOM_ELEMENTS['setVolume'] = makeEl('input');
DOM_ELEMENTS['setMusicVol'] = makeEl('input');
DOM_ELEMENTS['setSfxVol'] = makeEl('input');
DOM_ELEMENTS['setAmbienceVol'] = makeEl('input');
DOM_ELEMENTS['setExplosionVol'] = makeEl('input');
DOM_ELEMENTS['setMute'] = makeEl('input');
DOM_ELEMENTS['filmgrain'] = makeEl('div');

global.document = {
  readyState: 'complete',
  hidden: false,
  addEventListener: () => {},
  removeEventListener: () => {},
  querySelector: (sel) => makeEl('div'),
  querySelectorAll: () => [],
  body: {
    classList: {
      _classes: new Set(),
      add: function(c){ this._classes.add(c); },
      remove: function(c){ this._classes.delete(c); },
      contains: function(c){ return this._classes.has(c); },
      toggle: function(c, f){
        if(f !== undefined){ if(f) this._classes.add(c); else this._classes.delete(c); }
        else if(this._classes.has(c)) this._classes.delete(c);
        else this._classes.add(c);
      }
    },
    appendChild: () => {},
    style: {}
  },
  createElement: makeEl,
  getElementById: (id) => DOM_ELEMENTS[id] || makeEl('div')
};
global.navigator = { userAgent: 'NodeTest', getGamepads: () => [] };
global.localStorage = {
  _data: {},
  getItem: (k) => global.localStorage._data[k] || null,
  setItem: (k, v) => { global.localStorage._data[k] = String(v); },
  removeItem: (k) => { delete global.localStorage._data[k]; }
};

// Mock Web Audio Context
function MockAudioParam(initVal) {
  this.value = initVal || 0;
  this.setValueAtTime = (v) => { this.value = v; };
  this.setTargetAtTime = (v) => { this.value = v; };
  this.linearRampToValueAtTime = (v) => { this.value = v; };
  this.exponentialRampToValueAtTime = (v) => { this.value = v; };
  this.cancelScheduledValues = () => {};
}

function MockAudioNode() {
  this.gain = new MockAudioParam(1.0);
  this.frequency = new MockAudioParam(1000);
  this.Q = new MockAudioParam(1);
  this.threshold = new MockAudioParam(-6);
  this.knee = new MockAudioParam(12);
  this.ratio = new MockAudioParam(12);
  this.attack = new MockAudioParam(0.003);
  this.release = new MockAudioParam(0.25);
  this.connect = (dest) => dest;
  this.disconnect = () => {};
  this.start = () => {};
  this.stop = () => {};
}

global.AudioContext = function() {
  this.state = 'suspended';
  this.currentTime = 0.5;
  this.sampleRate = 44100;
  this.destination = new MockAudioNode();
  this.createGain = () => new MockAudioNode();
  this.createOscillator = () => new MockAudioNode();
  this.createBiquadFilter = () => new MockAudioNode();
  this.createDynamicsCompressor = () => new MockAudioNode();
  this.createBuffer = (ch, len, rate) => ({
    getChannelData: () => new Float32Array(len)
  });
  this.createBufferSource = () => new MockAudioNode();
  this.resume = () => {
    this.state = 'running';
    return Promise.resolve();
  };
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

// Load and eval game.html
const htmlPath = path.join(__dirname, '..', 'game.html');
const html = fs.readFileSync(htmlPath, 'utf8');
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);
assert(scriptMatch, 'Must find script tag in game.html');

try {
  eval(scriptMatch[1]);
} catch(e) {
  console.log('Script non-fatal notice:', e.message);
}

const api = global.AegisFlorae || global.RoboFlora;
assert(api, 'AegisFlorae API must be exposed on window');

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    passed++;
    console.log('✓ ' + name);
  } catch(e) {
    failed++;
    console.error('✗ ' + name + ': ' + e.message);
  }
}

// ===== SCREEN SHAKE / TRAUMA TESTS =====

console.log('\n--- 1. Screen Shake & Trauma Reduction ---');

test('addTrauma() scales input by 0.35 and caps at 0.35', () => {
  const src = scriptMatch[1];
  // Match: S.trauma = Math.min(0.35, (S.trauma || 0) + (amount || 0.1) * 0.35)
  const traumaMatch = src.match(/S\.trauma\s*=\s*Math\.min\(([\d.]+),\s*\(S\.trauma[^)]*\)\s*\+\s*\(amount[^)]*\)\s*\*\s*([\d.]+)\)/);
  assert(traumaMatch, 'Must find scaled addTrauma formula');
  const cap = parseFloat(traumaMatch[1]);
  const scale = parseFloat(traumaMatch[2]);
  assert(cap <= 0.35, 'Trauma cap must be ≤ 0.35 (was 1.0), got: ' + cap);
  assert(scale <= 0.40, 'Trauma scale must be ≤ 0.40 (was 1.0), got: ' + scale);
});

// ===== MORTAR EXPLOSION TRAUMA =====

console.log('\n--- 2. Mortar Explosion Trauma ---');

test('spawnExplosion() applies reduced trauma formula', () => {
  // Read source code to verify the formula
  const src = scriptMatch[1];
  const explosionTraumaMatch = src.match(/addTrauma\(Math\.min\(([\d.]+),\s*([\d.]+)\s*\+\s*splash\s*\*\s*([\d.]+)\)/);
  assert(explosionTraumaMatch, 'Must find explosion trauma formula');
  const cap = parseFloat(explosionTraumaMatch[1]);
  const base = parseFloat(explosionTraumaMatch[2]);
  const multiplier = parseFloat(explosionTraumaMatch[3]);
  assert(cap <= 0.15, 'Explosion trauma cap must be ≤ 0.15 (was 0.45), got: ' + cap);
  assert(base <= 0.05, 'Explosion trauma base must be ≤ 0.05 (was 0.12), got: ' + base);
  assert(multiplier <= 0.03, 'Explosion trauma splash multiplier must be ≤ 0.03 (was 0.08), got: ' + multiplier);
});

// ===== CAMERA DISPLACEMENT =====

console.log('\n--- 3. Camera Displacement Reduction ---');

test('Camera displacement factor is reduced to ≤ 0.3 (from 1.4)', () => {
  const src = scriptMatch[1];
  // Match: var sh = S.trauma * S.trauma * <factor>
  const shMatch = src.match(/var\s+sh\s*=\s*S\.trauma\s*\*\s*S\.trauma\s*\*\s*([\d.]+)/);
  assert(shMatch, 'Must find camera displacement formula');
  const factor = parseFloat(shMatch[1]);
  assert(factor <= 0.3, 'Camera displacement factor must be ≤ 0.3 (was 1.4), got: ' + factor);
});

test('Trauma decay rate is accelerated to ≥ 3.0 (from 1.6)', () => {
  const src = scriptMatch[1];
  // Match: S.trauma - dt * <rate>
  const decayMatch = src.match(/S\.trauma\s*-\s*dt\s*\*\s*([\d.]+)/);
  assert(decayMatch, 'Must find trauma decay formula');
  const rate = parseFloat(decayMatch[1]);
  assert(rate >= 3.0, 'Trauma decay rate must be ≥ 3.0 (was 1.6), got: ' + rate);
});

// ===== PAD RUMBLE =====

console.log('\n--- 4. Gamepad Rumble Dampening ---');

test('padRumble() function is defined in source', () => {
  const src = scriptMatch[1];
  assert(src.includes('function padRumble('), 'padRumble function must exist in source');
});

test('Pad rumble duration is halved and capped at 100ms in source', () => {
  const src = scriptMatch[1];
  // Look for the duration clamping: Math.min(100, ...
  const durMatch = src.match(/duration:\s*Math\.min\((\d+)/);
  assert(durMatch, 'Must find duration clamping in padRumble');
  assert(parseInt(durMatch[1]) <= 100, 'Max rumble duration must be ≤ 100ms, got: ' + durMatch[1]);
});

test('Pad rumble magnitudes are scaled down by ≥ 60% in source', () => {
  const src = scriptMatch[1];
  // weakMagnitude: Math.min(0.2, (weak || 0.3) * 0.35)
  const weakMatch = src.match(/weakMagnitude:\s*Math\.min\(([\d.]+)/);
  assert(weakMatch, 'Must find weak magnitude clamping');
  assert(parseFloat(weakMatch[1]) <= 0.25, 'Weak magnitude cap must be ≤ 0.25, got: ' + weakMatch[1]);

  const strongMatch = src.match(/strongMagnitude:\s*Math\.min\(([\d.]+)/);
  assert(strongMatch, 'Must find strong magnitude clamping');
  assert(parseFloat(strongMatch[1]) <= 0.3, 'Strong magnitude cap must be ≤ 0.3, got: ' + strongMatch[1]);
});

// ===== CLAUDE FM CONTROLLER =====

console.log('\n--- 5. Claude FM Radio Controller ---');

test('CLAUDE_FM is exported on the API object', () => {
  assert(api.CLAUDE_FM, 'CLAUDE_FM must be exported on API');
});

test('CLAUDE_FM has all required methods', () => {
  const fm = api.CLAUDE_FM;
  assert.strictEqual(typeof fm.init, 'function', 'init');
  assert.strictEqual(typeof fm.play, 'function', 'play');
  assert.strictEqual(typeof fm.pause, 'function', 'pause');
  assert.strictEqual(typeof fm.toggle, 'function', 'toggle');
  assert.strictEqual(typeof fm.setVolume, 'function', 'setVolume');
  assert.strictEqual(typeof fm.mute, 'function', 'mute');
  assert.strictEqual(typeof fm.setActive, 'function', 'setActive');
  assert.strictEqual(typeof fm.isActive, 'function', 'isActive');
  assert.strictEqual(typeof fm.isPlaying, 'function', 'isPlaying');
  assert.strictEqual(typeof fm.getVolume, 'function', 'getVolume');
});

test('CLAUDE_FM uses correct YouTube stream ID (tRsQsTMvPNg)', () => {
  assert.strictEqual(api.CLAUDE_FM.streamId, 'tRsQsTMvPNg');
});

test('CLAUDE_FM is active by default (replaces synthesized music)', () => {
  assert.strictEqual(api.CLAUDE_FM.isActive(), true);
});

test('CLAUDE_FM toggle() flips play/pause state', () => {
  const fm = api.CLAUDE_FM;
  const wasPl = fm.isPlaying();
  fm.toggle();
  assert.strictEqual(fm.isPlaying(), !wasPl);
  fm.toggle(); // restore
  assert.strictEqual(fm.isPlaying(), wasPl);
});

test('CLAUDE_FM setVolume() clamps between 0 and 100', () => {
  const fm = api.CLAUDE_FM;
  fm.setVolume(150);
  assert.strictEqual(fm.getVolume(), 100);
  fm.setVolume(-20);
  assert.strictEqual(fm.getVolume(), 0);
  fm.setVolume(65);
  assert.strictEqual(fm.getVolume(), 65);
});

test('CLAUDE_FM mute/unmute cycle works', () => {
  const fm = api.CLAUDE_FM;
  fm.mute(true);
  fm.mute(false);
  // Should not throw — validates internal state transitions
});

test('CLAUDE_FM init() can be called without errors', () => {
  const fm = api.CLAUDE_FM;
  // Should not throw with mocked DOM
  fm.init();
});

// ===== MUSIC ENGINE SUPPRESSION =====

console.log('\n--- 6. Synthesized Music Suppression ---');

test('MUSIC_ENGINE is still exported (not deleted)', () => {
  assert(api.MUSIC_ENGINE, 'MUSIC_ENGINE must still exist for backward compat');
});

test('CLAUDE_FM init() calls MUSIC_ENGINE.stop() to suppress synth', () => {
  const src = scriptMatch[1];
  // Verify the init function contains the MUSIC_ENGINE.stop() call
  const claudeFmBlock = src.match(/var CLAUDE_FM[\s\S]*?return \{[\s\S]*?\};[\s\S]*?\}\)\(\)/);
  assert(claudeFmBlock, 'Must find CLAUDE_FM IIFE');
  assert(claudeFmBlock[0].includes('MUSIC_ENGINE') && claudeFmBlock[0].includes('stop'),
    'CLAUDE_FM must reference MUSIC_ENGINE.stop() to suppress synthesized music');
});

// ===== HTML MARKUP =====

console.log('\n--- 7. Claude FM HTML Markup ---');

test('Claude FM iframe src embeds correct YouTube stream', () => {
  const iframeSrcMatch = html.match(/id="claude-fm-iframe"[^>]*src="([^"]+)"/);
  assert(iframeSrcMatch, 'Must find claude-fm-iframe src');
  assert(iframeSrcMatch[1].includes('tRsQsTMvPNg'), 'Iframe must embed stream tRsQsTMvPNg');
  assert(iframeSrcMatch[1].includes('enablejsapi=1'), 'Iframe must enable JS API');
  assert(iframeSrcMatch[1].includes('autoplay=1'), 'Iframe must autoplay');
});

test('Claude FM button exists in HTML', () => {
  assert(html.includes('id="btnClaudeRadio"'), 'Must have btnClaudeRadio button');
});

test('Claude FM popover with controls exists in HTML', () => {
  assert(html.includes('id="claude-fm-popover"'), 'Must have claude-fm-popover');
  assert(html.includes('id="btnClaudeFmTogglePlay"'), 'Must have play/pause toggle');
  assert(html.includes('id="claudeFmVolSlider"'), 'Must have volume slider');
});

// ===== LIFECYCLE WIRING =====

console.log('\n--- 8. Lifecycle Integration ---');

test('boot() calls CLAUDE_FM.init()', () => {
  const src = scriptMatch[1];
  const bootFn = src.match(/function boot\(\)\{[\s\S]*?\n\}/);
  assert(bootFn, 'Must find boot function');
  assert(bootFn[0].includes('CLAUDE_FM') && bootFn[0].includes('init'),
    'boot() must call CLAUDE_FM.init()');
});

test('togglePause() calls CLAUDE_FM.pause() and CLAUDE_FM.play()', () => {
  const src = scriptMatch[1];
  const toggleFn = src.match(/function togglePause[\s\S]*?\n\}/);
  assert(toggleFn, 'Must find togglePause function');
  assert(toggleFn[0].includes('CLAUDE_FM') && toggleFn[0].includes('pause'),
    'togglePause() must call CLAUDE_FM.pause()');
  assert(toggleFn[0].includes('CLAUDE_FM') && toggleFn[0].includes('play'),
    'togglePause() must call CLAUDE_FM.play()');
});

test('setMasterMute() calls CLAUDE_FM.mute()', () => {
  const src = scriptMatch[1];
  const muteFn = src.match(/function setMasterMute[\s\S]*?\n\}/);
  assert(muteFn, 'Must find setMasterMute function');
  assert(muteFn[0].includes('CLAUDE_FM') && muteFn[0].includes('mute'),
    'setMasterMute() must sync CLAUDE_FM mute state');
});

test('applySettings() syncs CLAUDE_FM volume', () => {
  const src = scriptMatch[1];
  const settingsFn = src.match(/function applySettings\(\)\{[\s\S]*?\n\}/);
  assert(settingsFn, 'Must find applySettings function');
  assert(settingsFn[0].includes('CLAUDE_FM') && settingsFn[0].includes('setVolume'),
    'applySettings() must sync CLAUDE_FM.setVolume()');
});

// ===== SUMMARY =====

console.log('\n========================================');
console.log(`Results: ${passed} passed, ${failed} failed out of ${passed + failed} tests`);
console.log('========================================');

if (failed > 0) {
  process.exit(1);
} else {
  console.log('All Claude FM & Rumble Tuning tests passed! ✓');
  process.exit(0);
}
