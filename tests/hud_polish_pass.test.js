// Aegis Florae: HUD polish-pass verification (wave HUD, sidebar, tutorial,
// banners, mortar roles, flashes, audio, terrain, debug API, viewports).
const assert = require('assert');
const fs = require('fs');

console.log('--- Aegis Florae: HUD Polish Pass Tests ---');

global.window = global;
global.addEventListener = () => {};
global.removeEventListener = () => {};
global.requestAnimationFrame = (fn) => setTimeout(fn, 16);
global.cancelAnimationFrame = (id) => clearTimeout(id);
global.innerWidth = 1280;
global.innerHeight = 800;
global.matchMedia = () => ({ matches: false, addEventListener: () => {} });

function makeEl() {
  const el = {
    style: {},
    dataset: {},
    children: [],
    _qs: {},
    classList: {
      _classes: new Set(),
      add: function(c){ this._classes.add(c); },
      remove: function(c){ this._classes.delete(c); },
      contains: function(c){ return this._classes.has(c); },
      toggle: function(c, f){ if(f === undefined) f = !this._classes.has(c); if(f) this._classes.add(c); else this._classes.delete(c); }
    },
    appendChild: function(c){ this.children.push(c); return c; },
    addEventListener: () => {},
    removeEventListener: () => {},
    setAttribute: () => {},
    getAttribute: () => null,
    querySelector: function(sel){ if(!this._qs[sel]) this._qs[sel] = makeEl(); return this._qs[sel]; },
    querySelectorAll: () => [],
    closest: () => null,
    focus: () => {},
    click: () => {},
    getContext: () => new Proxy({
      measureText: () => ({ width: 10 }),
      createImageData: (w, h) => ({ data: new Uint8ClampedArray((w || 1) * (h || 1) * 4) }),
      createLinearGradient: () => ({ addColorStop: () => {} }),
      createRadialGradient: () => ({ addColorStop: () => {} })
    }, { get: (t, p) => (p in t ? t[p] : () => {}) }),
    textContent: '',
    innerHTML: '',
    value: '',
    checked: false,
    disabled: false,
    hidden: false,
    type: ''
  };
  el.parentElement = el;
  el.parentNode = el;
  return el;
}

const DOM_ELEMENTS = {};
global.document = {
  readyState: 'complete',
  addEventListener: () => {},
  removeEventListener: () => {},
  querySelector: makeEl,
  querySelectorAll: () => [],
  activeElement: null,
  body: makeEl(),
  createElement: makeEl,
  createElementNS: (ns, tag) => makeEl(),
  getElementById: function(id) {
    if(!DOM_ELEMENTS[id]) DOM_ELEMENTS[id] = makeEl();
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
  const r = { domElement: makeEl(), setSize: () => {}, setPixelRatio: () => {}, render: () => {}, shadowMap: {} };
  return new Proxy(r, { get: (t, p) => (p in t ? t[p] : () => {}) });
};
global.AudioContext = function() {
  const param = () => ({ setValueAtTime: () => {}, exponentialRampToValueAtTime: () => {}, cancelScheduledValues: () => {}, setTargetAtTime: () => {} });
  return {
    currentTime: 0,
    sampleRate: 44100,
    state: 'running',
    destination: {},
    createGain: () => ({ gain: param(), connect: () => {} }),
    createDynamicsCompressor: () => ({ threshold: param(), knee: param(), ratio: param(), attack: param(), release: param(), connect: () => {} }),
    createOscillator: () => ({ frequency: param(), start: () => {}, stop: () => {}, connect: () => {} }),
    createBufferSource: () => ({ start: () => {}, stop: () => {}, connect: () => {} }),
    createBiquadFilter: () => ({ type: '', frequency: param(), Q: param(), connect: () => {} }),
    createBuffer: () => ({ getChannelData: () => new Float32Array(1024) })
  };
};

const html = fs.readFileSync('game.html', 'utf8');
const css = fs.readFileSync('hud.css', 'utf8');
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/m);
assert(scriptMatch, 'Must find inline game script');
eval(scriptMatch[1]);

const api = global.AegisFlorae;
assert(api, 'AegisFlorae API must be exposed');
assert(api.state, 'Game state must boot without JS errors');

console.log('1. Obsolete overlays removed, wave counter preserved...');
for (const gone of ['id="field-panel"', 'id="threat-announcement"', 'id="preview"',
  'id="more-controls-panel"', 'id="transport-cluster"', 'id="btnMoreControls"',
  'INCOMING THREAT', 'preview-kicker', 'preview-pulse', 'threat-badge']) {
  assert(!html.includes(gone), 'game.html must not contain ' + gone);
}
assert(html.includes('FIELD BRIEFING'), 'Tutorial briefing must remain');
for (const kept of ['id="wave"', 'id="phaseLabel"', 'id="score"', 'id="btnWave"']) {
  assert(html.includes(kept), 'game.html must keep ' + kept);
}
assert(!/el\.preview/.test(scriptMatch[1]), 'JS must not reference el.preview');
// previewText kept only as debug helper: defined once + exported once.
const previewUses = (scriptMatch[1].match(/previewText\(/g) || []).length;
assert(previewUses <= 3, 'previewText must have no HUD call sites, found ' + previewUses);
console.log('✓ Overlays removed; primary wave counter lives in the topbar chip.');

console.log('2. Premium wave button markup + states...');
assert(html.includes('btn-wave-art'), 'Wave button must have full-bleed art layer');
assert(html.includes('btn-wave-shade'), 'Wave button must have readability gradient overlay');
assert(html.includes('btn-wave-label'), 'Wave button must keep its label span');
assert(css.includes("assets/aegis_master.jpg"), 'Wave button art must use an existing Aegis asset');
for (const state of ['#topbar #btnWave.btn-wave-heroic:hover', '#topbar #btnWave.btn-wave-heroic:active',
  '#topbar #btnWave:disabled', '#topbar #btnWave.btn-wave-heroic:focus-visible']) {
  assert(css.includes(state), 'CSS must style wave button state: ' + state);
}
assert(css.includes('prefers-reduced-motion'), 'CSS must respect prefers-reduced-motion');
assert(css.includes('overflow-x'), 'CSS must prevent horizontal overflow');
console.log('✓ Image wave button with overlay, states, and reduced-motion support.');

console.log('3. Concise wave announcements (behavioral)...');
let S = api.newGame(7);
assert.strictEqual(api.startWave(), true, 'Wave 1 must start');
let title = DOM_ELEMENTS['wavebanner'].querySelector('.wb-title').textContent;
let sub = DOM_ELEMENTS['wavebanner'].querySelector('.wb-sub').textContent;
assert.strictEqual(title, 'WAVE 1', 'Wave 1 banner must be concise, got: ' + title);
assert(!/\dx /.test(sub), 'Banner sub must not list enemy counts, got: ' + sub);
S.wave = 9; S.phase = 'build';
assert.strictEqual(api.startWave(), true, 'Wave 10 must start');
title = DOM_ELEMENTS['wavebanner'].querySelector('.wb-title').textContent;
sub = DOM_ELEMENTS['wavebanner'].querySelector('.wb-sub').textContent;
assert.strictEqual(title, '☠ COLOSSUS APPROACHES', 'Boss banner title, got: ' + title);
assert.strictEqual(sub, 'BOSS WAVE', 'Boss banner sub, got: ' + sub);
// Wave completion -> concise banner + build phase + event.
S.spawnQueue = []; S.foes = []; S.phase = 'combat';
api.update(1 / 60);
assert.strictEqual(S.phase, 'build', 'Phase must return to build on wave completion');
title = DOM_ELEMENTS['wavebanner'].querySelector('.wb-title').textContent;
assert.strictEqual(title, 'WAVE COMPLETE', 'Completion banner, got: ' + title);
const evts = api.drainEvents();
assert(evts.some((e) => e.kind === 'wave-complete'), 'wave-complete event must be logged');
console.log('✓ WAVE 1 / BOSS WAVE / WAVE COMPLETE, no composition leaks.');

console.log('4. Wave button label states + keyboard/space behavior...');
S = api.newGame(11);
S.phase = 'build'; S.wave = 0; S.spawnQueue = []; S.foes = [];
api.update(1 / 60); // update() refreshes the HUD every frame
let label = DOM_ELEMENTS['btnWave'].querySelector('.btn-wave-label').textContent;
assert(label.includes('Start Wave'), 'Build phase wave 0 label, got: ' + label);
S.phase = 'combat';
api.spawnEnemy('spider'); // keep the field non-empty so combat does not auto-complete
api.update(1 / 60);
label = DOM_ELEMENTS['btnWave'].querySelector('.btn-wave-label').textContent;
assert.strictEqual(label, 'Combat Raging…', 'Combat label, got: ' + label);
S.phase = 'over';
api.update(1 / 60);
label = DOM_ELEMENTS['btnWave'].querySelector('.btn-wave-label').textContent;
assert.strictEqual(label, 'Done', 'Game-over label, got: ' + label);
assert(scriptMatch[1].includes("k === ' '") || html.includes('Space'), 'Spacebar wave input must remain');
console.log('✓ Start Wave / Call Wave / Combat Raging… / Done preserved.');

console.log('5. Icon-first topbar and closed utility rail...');
assert(html.includes('id="control-sidebar"'), 'Sidebar markup must exist');
assert(html.includes('id="control-sidebar" class="collapsed"'), 'Utility rail must default closed');
assert(html.includes('class="topbar-tools"'), 'Topbar icon control cluster must exist');
assert(css.includes('#control-sidebar.collapsed'), 'Sidebar must be collapsible');
for (const id of ['btnPause', 'btnSpeed', 'btnAudio', 'btnCam', 'btnClarity', 'btnWeather']) {
  const tag = html.match(new RegExp('<button[^>]+id="' + id + '"[^>]*>'));
  assert(tag && tag[0].includes('hud-icon-btn'), 'High-frequency control must be a topbar icon: ' + id);
}
for (const id of ['btnFullscreen', 'btnSettings', 'btnClaudeRadio', 'btnTutorial', 'btnPad', 'gfx-mode']) {
  const tag = html.match(new RegExp('<button[^>]+id="' + id + '"[^>]*>'));
  assert(tag && tag[0].includes('rail-icon'), 'Utility control must be an icon: ' + id);
}
assert(!html.includes('Tower Selection'), 'Persistent verbose tower key legend must be removed');
assert(!html.includes('Mouse &amp; Gamepad'), 'Persistent verbose input legend must be removed');
assert(css.includes('max-width: 980px') || css.includes('max-width:980px'), 'CSS must adapt at tablet widths');
assert(css.includes('max-width: 690px') || css.includes('max-width:690px'), 'Icon HUD must adapt on small screens');
console.log('✓ Topbar icons plus a narrow utility rail that starts closed.');

console.log('6. Tutorial teaches five lessons, stays skippable...');
assert.strictEqual(api.TUTORIAL_STEPS.length, 8, 'Tutorial keeps 8 steps');
const tutText = api.TUTORIAL_STEPS.map((s) => s.title + ' ' + s.desc).join('\n');
for (const lesson of ['select a tower', 'maze wall', 'path open', 'start the wave', 'counter enemy behavior']) {
  assert(tutText.toLowerCase().includes(lesson), 'Tutorial must teach: ' + lesson);
}
assert(api.FOE_INTEL.spider && api.FOE_INTEL.drone && api.FOE_INTEL.boss, 'First-encounter codex must exist');
assert.strictEqual(api.shouldShowFirstRunTutorial({ getItem: () => null }), true, 'A new player must receive the walkthrough');
assert.strictEqual(api.shouldShowFirstRunTutorial({ getItem: () => 'true' }), false, 'A completed player may continue without a forced replay');
S = api.newGame(21);
api.spawnEnemy('drone');
assert(S.seenTypes && S.seenTypes.drone === 1, 'First drone encounter must be recorded');
console.log('✓ Five-lesson arc + one-shot encounter intel.');

console.log('7. Mortar role split (behavioral)...');
assert(api.cfg.TOWERS.rocket.desc.toLowerCase().includes('cannot hit air'), 'Base mortar desc must state the air weakness');
assert(api.cfg.BRANCH.rocket.B.aaOnly === true, 'Skyburst must stay the AA branch');
S = api.newGame(99);
S.cash = 5000;
const sx = api.cfg.SPAWN.x, sy = api.cfg.SPAWN.y;
assert(api.placeAt(sx + 2, sy, 'rocket').ok, 'Mortar placement must succeed');
api.spawnEnemy('drone');
const drone = S.foes[S.foes.length - 1];
const droneHp = drone.hp;
for (let i = 0; i < 240; i++) api.update(1 / 60);
assert.strictEqual(drone.hp, droneHp, 'Base mortar must never damage fliers');
api.spawnEnemy('spider');
for (let i = 0; i < 240; i++) api.update(1 / 60);
const spider = S.foes.find((f) => f.type === 'spider');
assert(spider && spider.hp < spider.maxhp, 'Base mortar must still punish ground swarms');
console.log('✓ Base mortar: ground-only AoE; Skyburst answers air.');

console.log('8. Tinted hit feedback, no harsh white...');
const keys = Object.keys(api.HIT_FLASH_COLORS).sort().join(',');
assert.strictEqual(keys, 'Blast,Energy,Kinetic,Sonic', 'One tint per damage type, got: ' + keys);
assert(!/fxLight\(0xffffff|addHalo\(grp, 0xffffff/.test(scriptMatch[1]), 'Explosion must not use pure-white flash');
assert(scriptMatch[1].includes('SETTINGS.reduceFlash') || scriptMatch[1].includes('reduceFlash'), 'Flashes must honor the reduced-flash setting');
assert(html.includes('id="setReduceFlash"'), 'Settings must expose reduced flashes');
console.log('✓ Damage-type tints + kill pops + reduce-flash setting.');

console.log('9. Audio: quiet UI, immediate mute, no duplicate volleys...');
const clickVol = parseFloat(scriptMatch[1].match(/name === 'click'\) tone\(720, 0\.04, 'square', ([\d.]+)\)/)[1]);
const gunVol = parseFloat(scriptMatch[1].match(/name === 'gun'\)[\s\S]*?tone\(160[^,]*, 0\.035, 'square', ([\d.]+)\)/)[1]);
assert(clickVol < gunVol, 'UI click (' + clickVol + ') must be quieter than gunfire (' + gunVol + ')');
assert(scriptMatch[1].includes('lastLaunchSnd'), 'Mortar volleys must be throttled like gunfire');
api.setMasterMute(true);
assert.strictEqual(api.isAudioMuted(), true, 'Mute must take effect immediately');
api.setMasterMute(false);
assert.strictEqual(api.isAudioMuted(), false, 'Unmute must restore');
console.log('✓ UI vols reduced, launch throttle added, mute immediate.');

console.log('10. Terrain keeps every route valid...');
S = api.newGame(4242);
const tiles = api.terrainTiles();
assert(tiles.length > 0 && tiles.length <= 10, 'A few terrain tiles expected, got ' + tiles.length);
const COLS = api.cfg.COLS, ROWS = api.cfg.ROWS;
for (const t of tiles) {
  assert(t.gx >= 0 && t.gx < COLS && t.gy >= 0 && t.gy < ROWS, 'Terrain tile in bounds');
}
const route = api.findPath(api.cfg.SPAWN.x, api.cfg.SPAWN.y, S.blocked);
assert(route && route.length >= COLS, 'A valid Sanctum route must exist with terrain');
let checked = 0;
for (let gx = 0; gx < COLS; gx++) {
  for (let gy = 0; gy < ROWS; gy++) {
    const chk = api.canPlace(gx, gy);
    if(chk.ok) {
      const test = S.blocked.slice(); test[gy * COLS + gx] = 1;
      assert(api.mazeValid(test), 'Legal placement at ' + gx + ',' + gy + ' must preserve a route');
      checked++;
    } else if(S.ruin && S.ruin[gy * COLS + gx]) {
      assert(chk.why.toLowerCase().includes('ruin'), 'Ruin tiles must explain themselves');
    }
  }
}
assert(checked > 100, 'Most of the grid must stay buildable, checked ' + checked);
console.log('✓ ' + tiles.length + ' terrain tiles; ' + checked + ' legal placements all preserve a route.');

console.log('11. Debug interfaces for autonomous testing...');
for (const fn of ['stepSimulation', 'snapshotFoes', 'drainEvents', 'terrainTiles', 'spawnPoints']) {
  assert(typeof api[fn] === 'function', 'API must expose ' + fn);
}
S = api.newGame(5);
api.spawnEnemy('spider');
const snap = api.snapshotFoes();
assert(snap.length === 1 && snap[0].type === 'spider' && typeof snap[0].x === 'number' && snap[0].pathLen >= 0, 'Snapshots must carry positions + paths');
api.stepSimulation(10);
api.logGameEvent('kill', { type: 'spider' });
const drained = api.drainEvents();
assert(drained.some((e) => e.kind === 'kill'), 'Events must drain');
assert.strictEqual(api.drainEvents().length, 0, 'Drain must clear the log');
api.gameOver(false);
assert(api.drainEvents().some((e) => e.kind === 'game-over'), 'Game over must be detectable');
assert(Array.isArray(api.spawnPoints()) && api.spawnPoints().length >= 1, 'Spawn points must be exposed');
console.log('✓ Seeded runs + snapshots + event log + stepping.');

console.log('12. Camera focus + early constraints, gamepad preserved...');
assert(typeof api.focusBattlefield === 'function', 'API must expose focusBattlefield');
assert(/k === 't'\) focusBattlefield\(\)/.test(scriptMatch[1]), 'T must trigger battlefield focus');
assert(/maxDistance = early \? 120 : 220/.test(scriptMatch[1]), 'Early waves must constrain zoom');
assert(scriptMatch[1].includes('M.wave') && scriptMatch[1].includes('btn === 15'), 'Gamepad wave + D-pad wave inputs must remain');
console.log('✓ T focuses, early zoom constrained, gamepad wave intact.');

console.log('13. Botanical field, seasons, and statue cleanup...');
assert(scriptMatch[1].includes('buildAnimatedGrass'), 'Playable field must build animated grass');
assert(scriptMatch[1].includes('createCarnationCluster'), 'Real flower bunches must replace sphere-only flower proxies');
assert(scriptMatch[1].includes("'cherry'"), 'Perimeter tree mix must include cherry blossoms');
assert(Array.isArray(api.WEATHER_MODES) && api.WEATHER_MODES.length >= 4, 'At least four seasons/weather modes expected');
for (const mode of ['bloom', 'rain', 'autumn', 'snow']) assert(api.WEATHER_MODES.some((m) => m.id === mode), 'Missing weather mode ' + mode);
assert(!scriptMatch[1].includes("key: 'statue'"), 'Statue GLB must not load');
assert(!scriptMatch[1].includes('GLTF_CACHE.statue'), 'Statue must not be mounted in the battlefield');
assert(!scriptMatch[1].includes('headless statue'), 'Procedural statue fragments must be removed');
console.log('✓ Animated turf, carnations, cherry blossoms, four weather modes, no statues.');

console.log('14. Render-budget safeguards...');
assert(scriptMatch[1].includes('new THREE.InstancedMesh(BOTANICAL_GEO_CACHE.stem'), 'Carnation stems must be instanced');
assert(scriptMatch[1].includes('new THREE.InstancedMesh(BOTANICAL_GEO_CACHE.petal'), 'Carnation petals must be instanced');
assert(scriptMatch[1].includes('mergeStaticGltfRoot'), 'Static GLBs must merge authoring parts by material');
const treeBudget = Number(scriptMatch[1].match(/var nPerimTrees = (\d+)/)[1]);
assert(treeBudget <= 18, 'Perimeter tree budget must remain bounded');
assert(!/for\(var i = 0; i < count; i\+\+\)\{\s*var flower = createBotanicalFlower\('carnation'/.test(scriptMatch[1]), 'Carnation clusters must not create one mesh hierarchy per flower');
console.log('✓ Instanced flowers, merged GLBs, bounded scenery density.');

console.log('\nAll HUD Polish Pass tests passed!');
process.exit(0);
