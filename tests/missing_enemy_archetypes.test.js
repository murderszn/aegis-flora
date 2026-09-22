const assert = require('assert');
const fs = require('fs');
const path = require('path');

console.log('--- Aegis Florae: Running Missing Enemy Archetypes & Counterplay Tests (Issue #22) ---');

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
      toggle: function(c) { if(this._classes.has(c)) this._classes.delete(c); else this._classes.add(c); }
    },
    appendChild: (c) => el.children.push(c),
    addEventListener: () => {},
    setAttribute: () => {},
    textContent: '',
    innerHTML: '',
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

DOM_ELEMENTS['bosshp'] = makeEl('div');
DOM_ELEMENTS['bossFill'] = makeEl('div');
DOM_ELEMENTS['bossPhaseBadge'] = makeEl('div');
DOM_ELEMENTS['bossShieldFill'] = makeEl('div');
DOM_ELEMENTS['bossMechanicDesc'] = makeEl('span');
DOM_ELEMENTS['bossHpNumbers'] = makeEl('span');
DOM_ELEMENTS['wavebanner'] = makeEl('div');
DOM_ELEMENTS['statCreepRoster'] = makeEl('div');

global.document = {
  readyState: 'complete',
  addEventListener: () => {},
  removeEventListener: () => {},
  querySelector: (sel) => makeEl('div'),
  querySelectorAll: () => [],
  body: {
    classList: { add: () => {}, remove: () => {}, contains: () => false, toggle: () => {} },
    appendChild: () => {},
    style: {}
  },
  createElement: makeEl,
  getElementById: (id) => DOM_ELEMENTS[id] || makeEl('div')
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

const api = global.AegisFlorae || global.RoboFlora;
assert(api, 'AegisFlorae API must be exposed on window');

console.log('1. Verifying FOES balance sheet values for Steam Prowler and Dreadnought Ram...');
const FOES = api.cfg.FOES;
assert(FOES.prowler, 'Steam Prowler definition must exist in FOES');
assert.strictEqual(FOES.prowler.name, 'Steam Prowler');
assert.strictEqual(FOES.prowler.dodge, 0.20, 'Steam Prowler must have 20% dodge');
assert.strictEqual(FOES.prowler.dmgMod.Blast, 1.35, 'Steam Prowler must take +35% bonus Blast damage');
assert.strictEqual(FOES.prowler.dmgMod.Sonic, 1.35, 'Steam Prowler must take +35% bonus Sonic damage');

assert(FOES.ram, 'Dreadnought Ram definition must exist in FOES');
assert.strictEqual(FOES.ram.name, 'Dreadnought Ram');
assert.strictEqual(FOES.ram.armor, 12, 'Dreadnought Ram must have 12 Armor');
assert.strictEqual(FOES.ram.dmgMod.Kinetic, 0.5, 'Dreadnought Ram must resist Kinetic damage (0.5x)');
assert.strictEqual(FOES.ram.dmgMod.Energy, 1.2, 'Dreadnought Ram must be weak to Energy (1.2x)');
assert.strictEqual(FOES.ram.dmgMod.Sonic, 1.4, 'Dreadnought Ram must be weak to Sonic (1.4x)');
console.log('✓ Verified: Base stats, armor, dodge, and damage modifiers match balance sheet specifications.');

console.log('2. Verifying Steam Prowler dodge evasion & counterplay logic...');
const prowler = {
  type: 'prowler',
  hp: 100,
  maxhp: 100,
  dodge: 0.20,
  armor: 2,
  dmgMod: FOES.prowler.dmgMod
};

// Force Math.random to return 0.05 (< 0.20 -> Dodge triggers)
const origRandom = Math.random;
Math.random = () => 0.05;

let dealtKinetic = api.applyDamage(prowler, 50, 'Kinetic', false, false);
assert.strictEqual(dealtKinetic, 0, 'Kinetic damage must be evaded when dodge triggers');
assert.strictEqual(prowler.hp, 100, 'Prowler HP must remain untouched on dodge');

let dealtEnergy = api.applyDamage(prowler, 50, 'Energy', false, false);
assert.strictEqual(dealtEnergy, 0, 'Energy laser damage must be evaded when dodge triggers');
assert.strictEqual(prowler.hp, 100, 'Prowler HP must remain untouched on dodge');

// Blast and Sonic CANNOT be dodged and receive +35% vulnerability bonus!
let dealtBlast = api.applyDamage(prowler, 100, 'Blast', false, false);
assert(dealtBlast > 0, 'Blast AoE damage cannot be evaded by steam screen');
assert(prowler.hp < 100, 'Prowler HP must be reduced by Blast AoE');

let prevHp = prowler.hp;
let dealtSonic = api.applyDamage(prowler, 100, 'Sonic', false, false);
assert(dealtSonic > 0, 'Sonic resonance damage cannot be evaded by steam screen');
assert.strictEqual(dealtSonic, 135, 'Sonic pure damage should apply 1.35x bonus damage');

Math.random = origRandom;
console.log('✓ Verified: Steam Prowler dodges Kinetic/Energy, while Blast AoE and Sonic bypass dodge with +35% bonus.');

console.log('3. Verifying Dreadnought Ram siege pressure & tower disruption...');
const S = api.newGame(42);
S.cash = 500;
// Place player towers
api.placeAt(5, 5, 'gun');
api.placeAt(5, 6, 'beam');
api.placeAt(15, 15, 'rocket'); // far tower

const tAdjacent1 = S.towers.find(t => t.gx === 5 && t.gy === 5);
const tAdjacent2 = S.towers.find(t => t.gx === 5 && t.gy === 6);
const tFar = S.towers.find(t => t.gx === 15 && t.gy === 15);

assert(tAdjacent1 && tAdjacent2 && tFar, 'Towers must be successfully placed');

tAdjacent1.cd = 0;
tAdjacent2.cd = 0;
tFar.cd = 0;

// Create Dreadnought Ram right next to (5,5) at (5.2, 5.2)
const ram = {
  type: 'ram',
  hp: 920,
  maxhp: 920,
  x: 5.2,
  y: 5.2,
  siegeTimer: 0.1
};

api.updateRamMechanics(ram, 0.2);

assert(tAdjacent1.cd >= 1.8, 'Adjacent tower 1 must have its reload cooldown stalled by ram impact');
assert(tAdjacent2.cd >= 1.8, 'Adjacent tower 2 must have its reload cooldown stalled by ram impact');
assert.strictEqual(tFar.cd, 0, 'Distant tower must not be affected by ram siege impact');
assert.strictEqual(ram.siegeTimer, 3.5, 'Ram siege timer must reset after striking');
console.log('✓ Verified: Dreadnought Ram strikes adjacent towers within 1.6 tiles, stalling reload cooldowns.');

console.log('4. Verifying wave composition progression across waves...');
const w1 = api.waveComp(1);
assert(!w1.some(g => g.type === 'prowler' || g.type === 'ram'), 'Wave 1 must not contain prowler or ram');

const w4 = api.waveComp(4);
const prowlerInW4 = w4.find(g => g.type === 'prowler');
assert(prowlerInW4 && prowlerInW4.count >= 1, 'Wave 4 must introduce Steam Prowler');

const w7 = api.waveComp(7);
const ramInW7 = w7.find(g => g.type === 'ram');
assert(ramInW7 && ramInW7.count >= 1, 'Wave 7 must introduce Dreadnought Ram');
console.log('✓ Verified: Steam Prowler appears at Wave 4 and Dreadnought Ram appears at Wave 7.');

console.log('5. Verifying 3D procedural creep meshes for prowler and ram...');
api.spawnEnemy('prowler');
api.spawnEnemy('ram');

const spawnedProwler = S.foes.find(f => f.type === 'prowler');
const spawnedRam = S.foes.find(f => f.type === 'ram');

assert(spawnedProwler && spawnedProwler.mesh, 'Spawned Steam Prowler must have 3D mesh');
assert(spawnedProwler.mesh.userData.isProwler, 'Steam Prowler mesh must contain prowler userData flags');
assert(spawnedProwler.mesh.userData.steamHalo, 'Steam Prowler mesh must have steam screen halo');

assert(spawnedRam && spawnedRam.mesh, 'Spawned Dreadnought Ram must have 3D mesh');
assert(spawnedRam.mesh.userData.isRam, 'Dreadnought Ram mesh must contain ram userData flags');
assert(spawnedRam.mesh.userData.ramHead, 'Dreadnought Ram mesh must contain hydraulic ram head');
console.log('✓ Verified: 3D procedural creep meshes construct correctly with distinct visual cues.');

console.log('6. Verifying Telemetry, Roster, and Tutorial updates...');
assert('prowler' in S.killsByType && 'ram' in S.killsByType, 'killsByType must track prowler and ram');
assert('prowler' in S.leakedByType && 'ram' in S.leakedByType, 'leakedByType must track prowler and ram');

// Trigger gameOver to verify casualty roster render
S.killsByType.prowler = 7;
S.killsByType.ram = 2;
api.gameOver(false);

assert(DOM_ELEMENTS['statCreepRoster'].innerHTML.includes('Steam Prowler'), 'Roster must list Steam Prowler');
assert(DOM_ELEMENTS['statCreepRoster'].innerHTML.includes('Dreadnought Ram'), 'Roster must list Dreadnought Ram');

// Check Tutorial Step 8
const tutStep8 = api.TUTORIAL_STEPS.find(s => s.step === 8);
assert(tutStep8, 'Tutorial step 8 must exist');
assert(tutStep8.desc.includes('Steam Prowler'), 'Tutorial step 8 must mention Steam Prowler');
assert(tutStep8.desc.includes('Dreadnought Ram'), 'Tutorial step 8 must mention Dreadnought Ram');
assert(tutStep8.desc.includes('Bloom AoE') || tutStep8.visual.includes('Bloom AoE'), 'Tutorial must explain Bloom AoE counterplay');
console.log('✓ Verified: Casualty roster breakdown and Guided Tutorial include prowler and ram counterplay.');

console.log('\n--- All Issue #22 Enemy Archetype & Counterplay Tests Passed Successfully! ---');
process.exit(0);
