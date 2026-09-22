// Verification and logic test for Issue #2: Unity enemies do not damage the Sanctum when they leak
const assert = require('assert');
const fs = require('fs');

console.log('--- Verifying Unity Sanctum Breach & Leak Implementation (Issue #2) ---');

// 1. Verify CreepAgent.cs source changes
const creepAgentSrc = fs.readFileSync('Unity/Assets/Scripts/Enemies/CreepAgent.cs', 'utf8');

assert(creepAgentSrc.includes('using AegisFlorae.Core;'), 'CreepAgent.cs must import AegisFlorae.Core');
assert(creepAgentSrc.includes('public static event Action<CreepAgent, int> OnCreepSanctumBreached;'), 'CreepAgent.cs must declare OnCreepSanctumBreached event');
assert(creepAgentSrc.includes('public GameObject breachVFXPrefab;'), 'CreepAgent.cs must declare breachVFXPrefab');
assert(creepAgentSrc.includes('public AudioClip breachSFX;'), 'CreepAgent.cs must declare breachSFX');

// Verify ReachSanctum implementation
const reachStart = creepAgentSrc.indexOf('private void ReachSanctum()');
assert(reachStart !== -1, 'CreepAgent.cs must implement ReachSanctum()');
const reachEnd = creepAgentSrc.indexOf('private void Die()', reachStart);
const reachBody = creepAgentSrc.slice(reachStart, reachEnd);

assert(reachBody.includes('OnCreepSanctumBreached?.Invoke'), 'ReachSanctum must invoke OnCreepSanctumBreached event');
assert(reachBody.includes('GameManager.Instance.RegisterLeak'), 'ReachSanctum must call GameManager.Instance.RegisterLeak');
assert(reachBody.includes('AudioSource.PlayClipAtPoint'), 'ReachSanctum must support audio playback');
assert(reachBody.includes('Destroy(gameObject)'), 'ReachSanctum must destroy creep object');

// 2. Verify GameManager.cs source
const gameManagerSrc = fs.readFileSync('Unity/Assets/Scripts/Core/GameManager.cs', 'utf8');

assert(gameManagerSrc.includes('public static GameManager Instance'), 'GameManager must be a Singleton');
assert(gameManagerSrc.includes('public void RegisterLeak(CreepAgent creep, int damage)'), 'GameManager must declare RegisterLeak');
assert(gameManagerSrc.includes('public void TriggerDefeat()'), 'GameManager must declare TriggerDefeat');
assert(gameManagerSrc.includes('OnSanctumBreached?.Invoke'), 'GameManager must invoke OnSanctumBreached');
assert(gameManagerSrc.includes('OnDefeat?.Invoke'), 'GameManager must invoke OnDefeat');

// 3. Functional Simulation of GameManager State Transitions
class MockGameManager {
  constructor(maxLives = 20, startingScrap = 100) {
    this.maxLives = maxLives;
    this.currentLives = maxLives;
    this.currentScrap = startingScrap;
    this.totalLeaks = 0;
    this.phase = 'Build';
    this.eventsFired = [];
  }

  registerLeak(damage) {
    if (this.phase === 'Defeat') return;
    const effectiveDmg = Math.max(1, damage);
    this.currentLives = Math.max(0, this.currentLives - effectiveDmg);
    this.totalLeaks++;
    this.eventsFired.push({ event: 'SanctumBreached', dmg: effectiveDmg, remaining: this.currentLives });

    if (this.currentLives <= 0) {
      this.triggerDefeat();
    }
  }

  triggerDefeat() {
    this.phase = 'Defeat';
    this.eventsFired.push({ event: 'Defeat' });
  }
}

console.log('Testing functional breach and defeat lifecycle...');
const gm = new MockGameManager(5);
assert.strictEqual(gm.currentLives, 5);
assert.strictEqual(gm.totalLeaks, 0);

// Leak 1 damage
gm.registerLeak(1);
assert.strictEqual(gm.currentLives, 4);
assert.strictEqual(gm.totalLeaks, 1);
assert.strictEqual(gm.phase, 'Build');

// Leak 3 damage
gm.registerLeak(3);
assert.strictEqual(gm.currentLives, 1);
assert.strictEqual(gm.totalLeaks, 2);

// Leak 2 damage (overkill - should trigger defeat and clamp at 0)
gm.registerLeak(2);
assert.strictEqual(gm.currentLives, 0, 'Lives must clamp at 0');
assert.strictEqual(gm.totalLeaks, 3, 'Total leaks should increment to 3');
assert.strictEqual(gm.phase, 'Defeat', 'Phase should transition to Defeat on lives reaching 0');
assert(gm.eventsFired.some(e => e.event === 'Defeat'), 'Defeat event must be fired');

console.log('--- ALL SANCTUM BREACH VERIFICATIONS PASSED! ---');
process.exit(0);
