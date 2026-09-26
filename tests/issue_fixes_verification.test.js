// Verification for issues #15, #16, #23, #25, #26 — static contract checks.
// Runs in CI: `node tests/issue_fixes_verification.test.js`
const assert = require('assert');
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const read = (p) => fs.readFileSync(path.join(root, p), 'utf8');

console.log('--- Aegis Florae: Issue fixes verification (#15, #16, #23, #25, #26) ---');

const game = read('game.html');
const gdd = read('GDD.md');
const readme = read('README.md');
const gridMgr = read('Unity/Assets/Scripts/Mazing/GridManager.cs');
const astar = read('Unity/Assets/Scripts/Mazing/AStarPathfinder.cs');

// #25: single authoritative grid contract (36 x 20)
assert(game.includes('var GRID = { W: 36, H: 20'), '#25: GRID single source of truth missing in game.html');
assert(game.includes('var COLS = GRID.W, ROWS = GRID.H'), '#25: COLS/ROWS must alias GRID');
assert(gdd.includes('36 columns x 20 rows'), '#25: GDD must document the 36x20 shipping contract');
assert(/public int cols = 36;/.test(gridMgr), '#25: Unity GridManager cols must be 36');
assert(/public int rows = 20;/.test(gridMgr), '#25: Unity GridManager rows must be 20');
console.log('✓ #25 grid dimensions centralized (GRID 36x20, docs + Unity agree)');

// #26: FPS telemetry survives tab switches / throttled frames
assert(game.includes('function resetFpsTelemetry'), '#26: resetFpsTelemetry missing');
assert(game.includes('visibilitychange'), '#26: visibilitychange reset missing');
assert(game.includes('function stepFpsAndDrs(dt, rawDt)'), '#26: stepFpsAndDrs must take raw (unclamped) delta');
assert(game.includes('rawDt > 0.25'), '#26: throttled-frame gap guard missing');
assert(game.includes('AEGIS_RELEASE'), '#26: release-mode diagnostics gate missing');
assert(game.includes('var rawDt = clock.getDelta()'), '#26: animate must keep unclamped delta');
assert(game.includes('stepFpsAndDrs(dt, rawDt)'), '#26: animate must pass raw delta to telemetry');
console.log('✓ #26 FPS telemetry resets after tab-switch gaps, diagnostics gated in release');

// #23: event-scaled hit-stop with reduced-motion respect
assert(game.includes('var HITSTOP ='), '#23: HITSTOP config missing');
assert(game.includes('function requestHitStop'), '#23: requestHitStop missing');
assert(game.includes('hitStop: 0'), '#23: S.hitStop state missing');
assert(game.includes('prefersReducedMotion'), '#23: reduced-motion respect missing');
assert(game.includes("requestHitStop('mortar')"), '#23: mortar hit-stop hook missing');
assert(game.includes("requestHitStop('boss')"), '#23: boss hit-stop hook missing');
assert(game.includes("requestHitStop('ability')"), '#23: ability hit-stop hook missing');
// Hit-stop must scale only the sim delta, never gate input/pause/menu paths.
assert(game.includes('sdt = 0'), '#23: hit-stop must zero the sim delta');
assert(!/if\s*\(S\.hitStop[^}]*return;/.test(game), '#23: hit-stop must not early-return around input/pause');
console.log('✓ #23 hit-stop scales sim delta only, respects reduced-motion, hooked to mortar/boss/ability');

// #15: documented controls match implementation
assert(game.includes("k === ' ' || k === 'n'"), '#15: N must alias Space for next wave');
assert(readme.includes('`Space` or `N`'), '#15: README must document Space/N contract');
assert(readme.includes("`P` | Pause"), '#15: README must document P for pause');
assert(readme.includes('rebindable'), '#15: README must note gamepad mapping is rebindable');
console.log('✓ #15 input contract reconciled (Space/N wave, P pause, rebindable gamepad note)');

// #16: Unity tower removal lifecycle + safe maze validation
assert(gridMgr.includes('towerInstances'), '#16: GridManager must track tower instances');
assert(gridMgr.includes('Destroy(tower)'), '#16: RemoveTower must destroy the instance');
assert(/try\s*\{/.test(astar) && /finally\s*\{/.test(astar), '#16: ValidateMazeWithBlock needs try/finally');
assert(astar.includes('int original = currentGrid[testX, testY]'), '#16: must save original cell value');
assert(astar.includes('currentGrid[testX, testY] = original'), '#16: must restore original value, not 0');
assert(astar.includes('currentGrid == null'), '#16: needs null guard');
console.log('✓ #16 Unity lifecycle safe (instance tracking + try/finally restore)');

console.log('--- ALL ISSUE FIX VERIFICATION TESTS PASSED ---');
process.exit(0);
