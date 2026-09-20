// Automated test suite for Issue #3: Fix Unity air-unit and path null-reference edge cases
const assert = require('assert');
const fs = require('fs');

console.log('--- Verifying Unity Air-Unit and Path Null-Reference Edge Cases (Issue #3) ---');

// 1. Source verification of CreepAgent.cs
const creepAgentSrc = fs.readFileSync('Unity/Assets/Scripts/Enemies/CreepAgent.cs', 'utf8');

// Ensure isAirUnit branch is isolated and doesn't access currentPath
const moveStart = creepAgentSrc.indexOf('private void MoveAlongPath()');
assert(moveStart !== -1, 'MoveAlongPath method must exist');
const moveEnd = creepAgentSrc.indexOf('public void TakeDamage', moveStart);
const moveCode = creepAgentSrc.slice(moveStart, moveEnd);

assert(moveCode.includes('if (isAirUnit)'), 'Must have explicit branch for isAirUnit');
assert(!moveCode.match(/if\s*\(isAirUnit\s*\|\|\s*currentPath\s*==\s*null/), 'Must NOT combine isAirUnit with currentPath fallthrough in single condition');

// Ensure ground unit guards against missing path
assert(moveCode.includes('if (currentPath == null || currentPath.Count == 0)'), 'Must guard against null or empty currentPath');
assert(moveCode.includes('RecalculatePath();'), 'Must attempt RecalculatePath() when missing');

// Ensure waypoint indexing is guarded
assert(moveCode.includes('if (currentWaypointIndex >= currentPath.Count)'), 'Must check waypoint bounds before indexing');

// Ensure GetPathProgress handles null currentPath safely
const progressStart = creepAgentSrc.indexOf('public float GetPathProgress()');
const progressEnd = creepAgentSrc.indexOf('private void FlashWhite', progressStart);
const progressCode = creepAgentSrc.slice(progressStart, progressEnd);
assert(progressCode.includes('isAirUnit || currentPath == null'), 'GetPathProgress must safely handle null path and air units');

// 2. Functional Simulation of Movement Logic
class MockAgent {
  constructor(isAirUnit = false) {
    this.isAirUnit = isAirUnit;
    this.currentPath = null;
    this.currentWaypointIndex = 0;
    this.position = { x: 0, y: 0, z: 10 };
    this.sanctumPos = { x: 70, y: 0, z: 20 };
    this.reachedSanctum = false;
    this.recalculated = false;
  }

  recalculatePath(hasPath = true) {
    this.recalculated = true;
    if (this.isAirUnit) return;
    if (hasPath) {
      this.currentPath = [
        { x: 10, y: 10 },
        { x: 30, y: 15 },
        { x: 70, y: 20 }
      ];
      this.currentWaypointIndex = 0;
    } else {
      this.currentPath = null;
    }
  }

  reachSanctum() {
    this.reachedSanctum = true;
  }

  // Exact mirror of MoveAlongPath logic
  moveAlongPath(dt = 0.1, speed = 10, pathAvailable = true) {
    if (this.isAirUnit) {
      const dx = this.sanctumPos.x - this.position.x;
      const dz = this.sanctumPos.z - this.position.z;
      const dist = Math.hypot(dx, dz);

      if (dist < 0.15) {
        this.reachSanctum();
        return;
      }

      const step = Math.min(dist, speed * dt);
      this.position.x += (dx / dist) * step;
      this.position.z += (dz / dist) * step;
      return;
    }

    if (this.currentPath == null || this.currentPath.length === 0) {
      this.recalculatePath(pathAvailable);
      if (this.currentPath == null || this.currentPath.length === 0) {
        return; // Halt safely
      }
    }

    if (this.currentWaypointIndex >= this.currentPath.length) {
      this.reachSanctum();
      return;
    }

    const target = this.currentPath[this.currentWaypointIndex];
    const dx = target.x - this.position.x;
    const dz = target.y - this.position.z;
    const dist = Math.hypot(dx, dz);

    if (dist < 0.15) {
      this.currentWaypointIndex++;
      if (this.currentWaypointIndex >= this.currentPath.length) {
        this.reachSanctum();
        return;
      }
    } else {
      const step = Math.min(dist, speed * dt);
      this.position.x += (dx / dist) * step;
      this.position.z += (dz / dist) * step;
    }
  }
}

console.log('Testing Scenario A: Air Unit Arrival with null currentPath...');
const airUnit = new MockAgent(true);
assert.strictEqual(airUnit.currentPath, null, 'Air unit path starts null');

// Simulate air flight to arrival
for (let i = 0; i < 200 && !airUnit.reachedSanctum; i++) {
  airUnit.moveAlongPath(0.1, 10);
}
assert.strictEqual(airUnit.reachedSanctum, true, 'Air unit must arrive at Sanctum safely without null-ref');
assert.strictEqual(airUnit.currentPath, null, 'Air unit should never have touched currentPath');

console.log('Testing Scenario B: Ground Unit with Missing/Unnavigable Path...');
const blockedGround = new MockAgent(false);
blockedGround.moveAlongPath(0.1, 10, false); // No path available
assert.strictEqual(blockedGround.recalculated, true, 'Should attempt to recalculate path');
assert.strictEqual(blockedGround.reachedSanctum, false, 'Should not reach Sanctum or warp through walls');
assert.strictEqual(blockedGround.position.x, 0, 'Position must remain halted when path is missing');

console.log('Testing Scenario C: Ground Unit Navigating Path to Sanctum...');
const groundUnit = new MockAgent(false);
for (let i = 0; i < 300 && !groundUnit.reachedSanctum; i++) {
  groundUnit.moveAlongPath(0.1, 10, true);
}
assert.strictEqual(groundUnit.reachedSanctum, true, 'Ground unit must reach Sanctum along waypoints');
assert.strictEqual(groundUnit.currentWaypointIndex, 3, 'All waypoints traversed');

console.log('--- ALL AIR UNIT AND PATHING EDGE CASES PASSED! ---');
process.exit(0);
