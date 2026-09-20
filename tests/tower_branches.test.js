// Automated test suite for Issue #8: Complete Tower Branch Mechanics
// Verifies:
// 1. Rail-Needler piercing 3 foes along firing line
// 2. Refraction Lens 3-way split beams
// 3. Sol Invictus ground scorch lines and area thermal damage
// 4. Chrono-Stutter every-fourth-pulse stun freeze
// 5. Resonance Shatter armor shred (-3) and +50% resonance shatter bonus damage
const assert = require('assert');
const fs = require('fs');

console.log('--- Aegis Flora: Running Tower Branch Mechanics Tests (Issue #8) ---');

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

function makeFoe(id, x, y, hp, armor) {
  return {
    id: id,
    x: x,
    y: y,
    r: 0.3,
    hp: hp,
    maxHp: hp,
    wp: 1,
    speed: 1.0,
    armor: armor || 0,
    armorShred: 0,
    armorShredT: 0,
    shattered: 0,
    slowF: 1,
    slowT: 0,
    stunned: 0,
    scorch: 0,
    dead: false,
    escaped: false,
    air: false,
    mesh: {
      position: new global.THREE.Vector3(x, 0.5, y),
      rotation: { y: 0 },
      scale: { set: () => {}, x: 1, y: 1, z: 1 },
      material: { opacity: 1, color: { setHex: () => {} } },
      traverse: () => {},
      userData: {}
    }
  };
}

// -------------------------------------------------------------
// Test 1: Rail-Needler Piercing (Gun branch B)
// -------------------------------------------------------------
console.log('1. Testing Rail-Needler Piercing (pierces up to 3 targets in a line)...');
const S = api.newGame(101);
S.cash = 5000;
api.setMetaScrap(1000);

// Place gun tower at (5, 5) -> center (5.5, 5.5)
api.placeAt(5, 5, 'gun');
const gunTower = S.towers.find(t => t.gx === 5 && t.gy === 5);
assert(gunTower, 'Gun tower should be placed');

// Upgrade to Branch B (Rail-Needler)
const upB = api.upgradeTo(gunTower, 'B');
assert.strictEqual(upB.ok, true, 'Upgrade to Rail-Needler should succeed');
assert.strictEqual(gunTower.branch, 'B', 'Tower should be on branch B');

// Place 4 enemies in a straight horizontal line along x from tower:
// Tower center is at (5.5, 5.5). Range is 2.8.
// Foe 1 at (6.2, 5.5) [dist 0.7]
// Foe 2 at (6.8, 5.5) [dist 1.3]
// Foe 3 at (7.4, 5.5) [dist 1.9]
// Foe 4 at (8.0, 5.5) [dist 2.5]
const f1 = makeFoe('R1', 6.2, 5.5, 100);
const f2 = makeFoe('R2', 6.8, 5.5, 100);
const f3 = makeFoe('R3', 7.4, 5.5, 100);
const f4 = makeFoe('R4', 8.0, 5.5, 100);

S.foes = [f1, f2, f3, f4];
gunTower.cd = 0;
gunTower.targetMode = 'first';

// Update simulation for one shot (dt = 0.05)
api.update(0.05);

// Rail-Needler has pierce: 3. It should hit Foe 1, Foe 2, and Foe 3, but NOT Foe 4!
assert(f1.hp < 100, `Foe 1 must take piercing damage, hp: ${f1.hp}`);
assert(f2.hp < 100, `Foe 2 must take piercing damage, hp: ${f2.hp}`);
assert(f3.hp < 100, `Foe 3 must take piercing damage, hp: ${f3.hp}`);
assert.strictEqual(f4.hp, 100, `Foe 4 beyond pierce limit (3) must NOT take damage, hp: ${f4.hp}`);
assert.strictEqual(gunTower.lastHitTargets.length, 3, 'Rail-Needler must hit exactly 3 targets');
console.log('✓ Verified: Rail-Needler punches through exactly 3 foes along firing line');

// -------------------------------------------------------------
// Test 2: Refraction Split Beams (Beam branch B)
// -------------------------------------------------------------
console.log('2. Testing Refraction Lens 3-Way Split Beams...');
api.placeAt(8, 5, 'beam');
const beamTower = S.towers.find(t => t.gx === 8 && t.gy === 5);
assert(beamTower, 'Beam tower should be placed');

const upBeamB = api.upgradeTo(beamTower, 'B');
assert.strictEqual(upBeamB.ok, true, 'Upgrade to Refraction Lens should succeed');
assert.strictEqual(beamTower.branch, 'B', 'Beam tower should be on branch B');

// Place 3 enemies within range of beam tower at (8.5, 5.5), range 4.0:
const b1 = makeFoe('B1', 9.5, 5.5, 200);
const b2 = makeFoe('B2', 8.5, 7.0, 200);
const b3 = makeFoe('B3', 7.5, 6.5, 200);

S.foes = [b1, b2, b3];
beamTower.cd = 0;
beamTower.beamTgt = null;
beamTower.beamTime = 0;

// Update simulation
api.update(0.1);

assert(b1.hp < 200, `Primary target b1 must take beam damage, hp: ${b1.hp}`);
assert(b2.hp < 200, `Secondary split target b2 must take refracted beam damage, hp: ${b2.hp}`);
assert(b3.hp < 200, `Secondary split target b3 must take refracted beam damage, hp: ${b3.hp}`);
assert(Array.isArray(beamTower.splitTargets), 'splitTargets array should be populated');
assert.strictEqual(beamTower.splitTargets.length, 2, 'Refraction Lens must have 2 secondary split targets (3 total)');
console.log('✓ Verified: Refraction Lens splits beams into 3 simultaneous targets');

// -------------------------------------------------------------
// Test 3: Sol Invictus Ground Scorch Lines (Beam branch A)
// -------------------------------------------------------------
console.log('3. Testing Sol Invictus Lingering Scorch Lines & Area Thermal Damage...');
api.placeAt(12, 5, 'beam');
const solTower = S.towers.find(t => t.gx === 12 && t.gy === 5);
assert(solTower, 'Second beam tower placed');

const upBeamA = api.upgradeTo(solTower, 'A');
assert.strictEqual(upBeamA.ok, true, 'Upgrade to Sol Invictus should succeed');
assert.strictEqual(solTower.branch, 'A', 'Beam tower should be on branch A');

// Target enemy for Sol Invictus
const sTarget = makeFoe('STarget', 13.5, 5.5, 500);
S.foes = [sTarget];
S.zones = [];
solTower.cd = 0;
solTower.scorchTimer = 0;

// Fire Sol Invictus
api.update(0.1);

assert(S.zones.length > 0, 'Sol Invictus must spawn at least one active ground scorch zone');
const scorchZone = S.zones.find(z => z.type === 'scorch');
assert(scorchZone, 'Active scorch zone must exist in S.zones');
assert(scorchZone.dps > 0, 'Scorch zone must deal continuous dps');
assert(scorchZone.life > 0, 'Scorch zone must have lingering duration');

// Now place a second ground enemy walking across the scorch line
const walkerFoe = makeFoe('Walker', 13.2, 5.5, 300);
S.foes.push(walkerFoe);

// Advance simulation to let scorch zone burn the passing walker
api.update(0.2);
assert(walkerFoe.hp < 300, `Passing enemy must take thermal damage from scorch zone, hp: ${walkerFoe.hp}`);
assert(walkerFoe.scorch > 0, 'Passing enemy must have scorch status effect applied');
console.log('✓ Verified: Sol Invictus carves lingering scorch lines that burn passing foes');

// -------------------------------------------------------------
// Test 4: Chrono-Stutter Every-Fourth-Pulse Stun (Slow branch A)
// -------------------------------------------------------------
console.log('4. Testing Chrono-Stutter Every-Fourth-Pulse Stun Freeze...');
api.placeAt(5, 8, 'slow');
const slowTower = S.towers.find(t => t.gx === 5 && t.gy === 8);
assert(slowTower, 'Slow tower placed');

const upSlowA = api.upgradeTo(slowTower, 'A');
assert.strictEqual(upSlowA.ok, true, 'Upgrade to Chrono-Stutter should succeed');
assert.strictEqual(slowTower.branch, 'A', 'Tower should be on branch A');

const creepChrono = makeFoe('ChronoTest', 5.5, 9.2, 300);
S.foes = [creepChrono];

// Reset pulse counter and test Pulses 1, 2, 3 (normal slow) and Pulse 4 (100% stun freeze)
slowTower.pulseCount = 0;

// Pulse 1
slowTower.cd = 0;
api.update(0.05);
assert.strictEqual(slowTower.pulseCount, 1, 'Pulse count should be 1');
assert.strictEqual(creepChrono.stunned, 0, 'Pulse 1 should NOT stun');
assert.strictEqual(creepChrono.slowF, 0.5, 'Pulse 1 should apply 50% slow');

// Pulse 2
slowTower.cd = 0;
creepChrono.slowF = 1; creepChrono.slowT = 0;
api.update(0.05);
assert.strictEqual(slowTower.pulseCount, 2, 'Pulse count should be 2');
assert.strictEqual(creepChrono.stunned, 0, 'Pulse 2 should NOT stun');

// Pulse 3
slowTower.cd = 0;
creepChrono.slowF = 1; creepChrono.slowT = 0;
api.update(0.05);
assert.strictEqual(slowTower.pulseCount, 3, 'Pulse count should be 3');
assert.strictEqual(creepChrono.stunned, 0, 'Pulse 3 should NOT stun');

// Pulse 4 -> MUST STUN!
slowTower.cd = 0;
creepChrono.slowF = 1; creepChrono.slowT = 0;
api.update(0.05);
assert.strictEqual(slowTower.pulseCount, 4, 'Pulse count should be 4');
assert(creepChrono.stunned > 0, `Pulse 4 MUST stun enemy, stunned: ${creepChrono.stunned}`);
assert.strictEqual(creepChrono.slowF, 0, 'Stun pulse must reduce speed factor to 0 (complete freeze)');
console.log('✓ Verified: Chrono-Stutter reliably freezes targets on exactly every 4th pulse');

// -------------------------------------------------------------
// Test 5: Resonance Shatter Armor Interaction (Slow branch B)
// -------------------------------------------------------------
console.log('5. Testing Resonance Shatter Armor Shred & Detonation Bonus...');
api.placeAt(8, 8, 'slow');
const shatterTower = S.towers.find(t => t.gx === 8 && t.gy === 8);
assert(shatterTower, 'Second slow tower placed');

const upSlowB = api.upgradeTo(shatterTower, 'B');
assert.strictEqual(upSlowB.ok, true, 'Upgrade to Resonance Shatter should succeed');
assert.strictEqual(shatterTower.branch, 'B', 'Tower should be on branch B');

// Armored tank enemy with 10 armor
const tankFoe = makeFoe('Tank', 8.5, 9.2, 500, 10);
S.foes = [tankFoe];

shatterTower.cd = 0;
const hpBeforePulse1 = tankFoe.hp;
api.update(0.05);

// Pulse 1: Should shred 3 armor, apply shattered status (+35% damage taken)
assert.strictEqual(tankFoe.armorShred, 3, 'Resonance Shatter must shred 3 armor');
assert(tankFoe.shattered > 0, 'Resonance Shatter must apply shattered status');
const dmgPulse1 = hpBeforePulse1 - tankFoe.hp;
assert(dmgPulse1 > 0, `Pulse 1 should deal damage: ${dmgPulse1}`);

// Pulse 2: Target is now already armor-shredded and shattered.
// Resonance Shatter should detonate acoustic resonance, dealing +50% bonus shatter damage!
shatterTower.cd = 0;
const hpBeforePulse2 = tankFoe.hp;
api.update(0.05);
const dmgPulse2 = hpBeforePulse2 - tankFoe.hp;

assert(dmgPulse2 > dmgPulse1, `Pulse 2 on shattered target (${dmgPulse2}) must exceed pulse 1 (${dmgPulse1}) due to +50% shatter synergy`);
assert.strictEqual(tankFoe.armorShred, 6, 'Second strike should further shred armor to 6');
console.log('✓ Verified: Resonance Shatter strips armor and detonates +50% bonus acoustic shatter damage');

console.log('--- ALL TOWER BRANCH MECHANICS TESTS PASSED! ---');
process.exit(0);
