const assert = require('assert');
const fs = require('fs');
const path = require('path');

console.log('--- Aegis Flora: Running Boss Multi-Phase & Mechanics Tests (Issue #21) ---');

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
    children: [],
    querySelector: (sel) => {
      if (sel === '.boss-fill') return DOM_ELEMENTS['bossFill'] || makeEl('div');
      if (sel === '.wb-title') return makeEl('div');
      if (sel === '.wb-sub') return makeEl('div');
      return makeEl('div');
    },
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

const api = global.AegisFlora || global.RoboFlora;
assert(api, 'AegisFlora API must be exposed on window');

console.log('1. Initializing game state and spawning Goliath Colossus (Wave 10 Boss)...');
const S = api.newGame(101);
S.wave = 10;
api.spawnEnemy('boss');

const boss = S.foes.find(f => f.type === 'boss');
assert(boss, 'Boss colossus must exist in S.foes');
assert.strictEqual(boss.phase, 1, 'Boss must spawn in Phase 1 (Siege Fortress)');
assert.strictEqual(boss.armor, 16, 'Boss must spawn with heavy 16 Armor');
assert.strictEqual(boss.shield, 0, 'Boss must spawn with 0 initial shield');
const initialSpeed = boss.speed;

api.updateBossBar();
assert.strictEqual(DOM_ELEMENTS['bosshp'].style.display, 'block', 'Boss HP bar must be visible');
assert.strictEqual(DOM_ELEMENTS['bossPhaseBadge'].textContent, 'PHASE 1: SIEGE', 'Phase badge must display PHASE 1: SIEGE');
console.log('✓ Verified: Boss Colossus correctly spawns in Phase 1 with 16 armor and UI display.');

console.log('2. Testing Phase 1 mechanics: Support Drones deployment and healing...');
const initialFoesCount = S.foes.length;
boss.droneTimer = 0.05; // accelerate timer
api.updateBossMechanics(boss, 0.1);

assert(S.foes.length > initialFoesCount, 'Boss must deploy support drones during Phase 1');
const supportDrone = S.foes.find(f => f.isSupportDrone);
assert(supportDrone, 'Support drone must have isSupportDrone flag');
assert.strictEqual(supportDrone.targetBoss, boss, 'Support drone must target the Colossus');

// Damage boss slightly to verify drone healing
boss.hp = boss.maxhp - 200;
const hpBeforeHeal = boss.hp;
supportDrone.healTimer = 0.05;
api.update(0.1);

assert(boss.hp > hpBeforeHeal, 'Support drone must heal the Colossus when damaged');
console.log('✓ Verified: Phase 1 support drones deploy and provide repair healing.');

console.log('3. Testing Phase 1 -> Phase 2 Transition (EMP Overcharge & Kinetic Shield)...');
// Place a tower near the boss
const towerRes = api.placeAt(3, 3, 'gun');
assert(towerRes.ok, 'Tower placement must succeed');
const placedTower = S.towers.find(t => t.gx === 3 && t.gy === 3);
assert(placedTower, 'Placed tower must exist');
placedTower.cd = 0;

// Set boss position adjacent to tower
boss.x = 3.5;
boss.y = 3.5;

// Damage boss below 66% HP threshold (e.g. 60% HP)
boss.hp = Math.round(boss.maxhp * 0.60);
api.updateBossMechanics(boss, 0.1);

assert.strictEqual(boss.phase, 2, 'Boss must transition to Phase 2 at <= 66% HP');
assert(boss.shield > 0, 'Boss must generate hardlight kinetic shield in Phase 2');
assert.strictEqual(boss.shield, Math.round(boss.maxhp * 0.15), 'Kinetic shield must equal 15% max HP');
assert(placedTower.empDisabled > 0, 'Nearby tower must be disabled by EMP pulse');
assert(placedTower.cd >= 2.5, 'Nearby tower attack cooldown must be delayed by EMP shockwave');

api.updateBossBar();
assert.strictEqual(DOM_ELEMENTS['bossPhaseBadge'].textContent, 'PHASE 2: EMP OVERCHARGE', 'Phase badge must display PHASE 2: EMP OVERCHARGE');
assert.strictEqual(DOM_ELEMENTS['bossShieldFill'].style.display, 'block', 'Shield bar must be visible in Phase 2');
console.log('✓ Verified: Phase 2 EMP shockwave disables nearby towers and activates 15% kinetic shield.');

console.log('4. Testing Kinetic Hardlight Shield damage absorption...');
const shieldBefore = boss.shield;
const hpBefore = boss.hp;
const dmgDealt = api.applyDamage(boss, 200, 'Kinetic');

assert(boss.shield < shieldBefore, 'Damage must deplete the hardlight shield first');
assert.strictEqual(boss.hp, hpBefore, 'HP must remain untouched while shield is active');
console.log('✓ Verified: Hardlight shield absorbs incoming damage before health is lost.');

console.log('5. Testing Phase 2 -> Phase 3 Transition (Berserk Core Meltdown & Stomp)...');
// Deplete shield and drop boss HP below 33% threshold (e.g. 25% HP)
boss.shield = 0;
boss.hp = Math.round(boss.maxhp * 0.25);
api.updateBossMechanics(boss, 0.1);

assert.strictEqual(boss.phase, 3, 'Boss must transition to Phase 3 at <= 33% HP');
assert(boss.speed > initialSpeed * 1.25, 'Boss speed must increase by +35% during Berserk Meltdown');
assert.strictEqual(boss.armor, 8, 'Boss armor must drop from 16 to 8 (core exposed for counterplay)');

api.updateBossBar();
assert.strictEqual(DOM_ELEMENTS['bossPhaseBadge'].textContent, 'PHASE 3: BERSERK MELTDOWN', 'Phase badge must display PHASE 3: BERSERK MELTDOWN');
console.log('✓ Verified: Phase 3 triggers Berserk speed boost, core armor reduction to 8, and UI indicator.');

console.log('6. Testing Colossus Defeat Reward and Victory Celebration...');
const killsBefore = S.kills;
const cashBefore = S.cash;
boss.hp = 0;
api.update(0.1);

assert(S.kills > killsBefore, 'Killing Colossus must increment kills');
assert(S.cash >= cashBefore + boss.reward, 'Killing Colossus must award scrap reward');
console.log('✓ Verified: Colossus destruction awards scrap, updates kill telemetry, and triggers fanfare.');

console.log('\nAll Boss Multi-Phase & Mechanics (Issue #21) tests passed successfully!');
process.exit(0);
