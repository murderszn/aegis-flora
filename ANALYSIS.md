# Aegis Flora 3D — Gap Analysis: Areas That Need More Work

This document identifies gaps between the project's **documented specifications** (GDD, TECHNICAL_ARCHITECTURE, UI_AND_UX_SPEC, ART_AND_AUDIO_SPEC, TOWER_AND_ENEMY_BALANCE_SHEET) and the **actual implementation** in `index.html` and the Unity scripts.

---

## 🔴 CRITICAL — Missing Core Features

### 1. **Sanctum Super-Abilities (D & F keys) — NOT IMPLEMENTED**
- **Spec:** `D` → Verdant Overgrowth (root 4×4 area, 3.5s, 60 Magic DPS, 35 Mana). `F` → Solar Flare (orbital beam, 800 Energy damage, 3-tile radius, 75 Mana).
- **Reality:** Mana bar is displayed (max 100) but **never recharges** and **no abilities fire**. The `D` and `F` keys are not bound in `bindInput()`.
- **Impact:** This is a flagship feature in the GDD ("Dota-Style Hero/Sanctum Abilities") and a core part of the economy loop. Without it, mana is dead weight.
- **Action:** Implement mana regen (+5/sec or +4/sec per spec), ability cooldowns, and the two spell effects with proper AoE damage/root logic.

### 2. **Meta-Progression (Verdant Glyphs) — NOT IMPLEMENTED**
- **Spec:** Permanent upgrades between runs: Foundry Engineering (+2% tower dmg/level), Ancient Vaults (+50/+100/+200 starting scrap), Flora Symbiosis (Sanctum HP regen), Mazing Mastery (decorative blocker walls).
- **Reality:** No `localStorage` save/load, no glyph system, no between-run progression. Each game is a fresh start.
- **Impact:** Eliminates replayability and the "reward loop" that keeps players coming back.
- **Action:** Add `localStorage` persistence, a glyph/upgrade screen between runs, and apply permanent bonuses to new games.

### 3. **Armor System — NOT IMPLEMENTED**
- **Spec:** Damage type interaction matrix (Kinetic weak vs armored, Energy ignores 50% armor, Sonic is pure damage, Blast AoE). Armor provides diminishing-returns EHP (Dota 2 formula).
- **Reality:** Enemies have a boolean `armored` flag but no actual armor value. Damage types all deal flat damage with no armor mitigation or type bonuses.
- **Impact:** The entire strategic depth of choosing the right tower type against the right enemy is lost. Armored walkers are only "tougher" numerically, not strategically.
- **Action:** Add armor values to enemy types, implement the Dota 2 armor formula, and apply damage type modifiers in combat calculations.

### 4. **Flow Field Pathfinding — NOT IMPLEMENTED**
- **Spec:** For 200+ creeps, use a backward Dijkstra flood-fill from the Sanctum to generate a distance potential field. Creeps sample the gradient vector. Only one recalculation per tower placement.
- **Reality:** Every creep gets an individual A* path. When towers are placed/removed, `rerouteFoes()` runs A* for every single creep. Performance degrades badly with large creep counts.
- **Impact:** Will cause frame drops during late-game swarm waves with 100+ creeps on screen.
- **Action:** Implement the integration flow field as described in TECHNICAL_ARCHITECTURE.md.

### 5. **Object Pooling — NOT IMPLEMENTED**
- **Spec:** Pre-allocated pool of 3,000 particles and 500 floating combat text objects. Zero allocations at runtime.
- **Reality:** Every muzzle flash, shell casing, explosion, spark, and damage number creates new `THREE.Mesh` / `THREE.Group` objects and `DOM elements` dynamically. Old ones are removed via splice.
- **Impact:** Garbage collector stutters during massive battles. Memory fragmentation. Frame spikes.
- **Action:** Create object pools for FX particles, shell casings, sparks, debris, and damage number DOM elements. Recycle instead of create/destroy.

---

## 🟠 HIGH — Significant Gaps

### 6. **Targeting Priority System — STUB ONLY**
- **Spec:** Five targeting modes: First (furthest along path), Last (closest to spawn), Strongest (highest HP), Weakest (lowest HP), Closest (Euclidean distance).
- **Reality:** The inspector shows "Priority: First · Last · Strongest (click tower to cycle soon)" but **clicking does nothing**. The tower always uses the same priority (highest path progress).
- **Action:** Implement a targeting priority system with a cycle button or key (e.g., `T` key) and actual sorting logic for each mode.

### 7. **Tower Branch Upgrades — SIMPLIFIED BELOW SPEC**
- **Spec:** Detailed T2 and T3 upgrades with unique mechanics (spin-up ramp, piercing, scorch lines, refraction splits, stun on 4th pulse, armor stripping).
- **Reality:** Upgrades are just flat stat changes (different `dmg`, `iv`, `range` values). No special mechanics are implemented:
  - Gun T2 "Vulcan Pedestal" spin-up ramp → just a faster fire rate
  - Beam T2 "Focus Lens" stored ramp charge → no charge storage
  - Beam T3-A "Sol Invictus" scorch line → no ground damage-over-time
  - Beam T3-B "Refraction" 3-way split → no split beams
  - Slow T3-A "Chrono-Stutter" freeze every 4th pulse → random 25% chance per pulse
  - Slow T3-B "Resonance Shatter" armor strip → sets a timer but doesn't actually reduce armor
- **Action:** Implement the special mechanics for each branch upgrade as documented.

### 8. **Creep Types Missing from Spec**
- **Spec:** 6 types documented: Skitter Scout, Steam Prowler, Tread Tank, Rotor Drone, Dreadnought Ram, Goliath Colossus.
- **Reality:** Only 5 types implemented (spider, tank, walker, boss, drone, ship). **Steam Prowler** (skirmisher with +20% dodge) and **Dreadnought Ram** (siege unit that charges towers if stalled) are missing.
- **Action:** Add Steam Prowler (dodge mechanic) and Dreadnought Ram (charge attack) enemy types.

### 9. **Boss Mechanics — INCOMPLETE**
- **Spec:** Multi-phase bosses with shield charge, EMP pulse (disables towers for 3s), shield regeneration, micro-drone deployments.
- **Reality:** Bosses are just high-HP versions of walkers with no special abilities, phases, or mechanics.
- **Action:** Implement boss phase transitions, shield mechanics, EMP ability, and drone deployments.

### 10. **Economy — MISSING INTEREST & EARLY CALL BONUS**
- **Spec:** 5% interest on held scrap between waves (capped at +50/wave). Early wave call bonus: `floor(T_remaining × 2.5 × sqrt(wave))` bonus scrap + 15% bounty bonus.
- **Reality:** No interest system. No early wave call mechanic. No `N` key binding. The "Call Wave" button doesn't exist.
- **Action:** Implement interest calculation at wave completion, add early wave call button/key, and apply bonus formulas.

---

## 🟡 MEDIUM — Important Polish & Features

### 11. **Mana Recharge — BROKEN**
- **Spec:** Solar Mana recharges at +4.0/sec (max 100).
- **Reality:** Mana starts at 100 and **never increases**. There's no regen tick in the `update()` loop.
- **Action:** Add `S.mana = Math.min(100, S.mana + 4 * dt)` in the update loop.

### 12. **Pause Doesn't Stop Wave Timer**
- **Reality:** `S.waveT` countdown continues during pause. Waves can trigger while the game is paused.
- **Action:** Guard wave timer and spawn logic with `if (S.paused) return` checks.

### 13. **Double Scene.Add for Creeps (Potential Bug)**
- **Code:** `create3DCreepMesh()` calls `scene.add(root)` for procedural models and GLTF models. Then `spawnEnemy()` pushes the mesh to `S.foes` but doesn't re-add to scene. However, the GLTF creep models have `scene.add(root)` inside the function AND the function returns the mesh — this is fine since `spawnEnemy` doesn't call `scene.add` again. **But** the `create3DCreepMesh` for GLTF models also has `scene.add(root)` inside the function, which means the mesh is already in the scene before `spawnEnemy` stores it. This works but is confusing and could cause issues if `spawnEnemy` is ever changed to also call `scene.add`.
- **Action:** Remove the `scene.add(root)` calls from inside `create3DCreepMesh` and `create3DTowerMesh`, and ensure the caller adds to scene. This makes the data flow explicit and prevents double-add bugs.

### 14. **Screen Shake — NOT IMPLEMENTED**
- **Spec:** Screen shake triggered by heavy mortar impacts and boss deaths with trauma decay formula.
- **Reality:** No camera shake on explosions or boss kills.
- **Action:** Implement camera offset based on trauma decay, applied to the camera position in the render loop.

### 15. **Post-Processing Bloom — NOT IMPLEMENTED**
- **Spec:** Dual-pass Kawase blur for energy conduits, laser beams, and glowing flowers.
- **Reality:** No post-processing pipeline. Glow effects are faked with additive sprites, not real bloom.
- **Action:** Add Three.js EffectComposer with UnrealBloomPass for proper glow on emissive materials.

### 16. **Creep IK Foot-Planting & Lean — NOT IMPLEMENTED**
- **Spec:** Inverted kinematics for foot placement, creeps leaning into turns.
- **Reality:** Legs only do a simple sine swing rotation. No IK, no lean.
- **Action:** Add basic IK foot-placing and turn banking for walker-type creeps.

### 17. **Overhead Status Debuff Icons — NOT IMPLEMENTED**
- **Spec:** Frost/slow (cyan tint + frost trail), armor shattered (cracked shield), stun (spinning gold star).
- **Reality:** No visual debuff indicators above creeps. The `slowT`/`slowF` state is only applied to movement speed, not shown visually.
- **Action:** Add sprite-based debuff icons above creep meshes with timer sweeps.

### 18. **Audio — Minimal & Repetitive**
- **Spec:** Spatial audio panning, dynamic low-pass filter when Sanctum < 25% HP, ambient soundscape (wind, birds, fountain), Dota-style announcer voice lines, weapon-specific sound textures.
- **Reality:** Only basic Web Audio oscillator tones (square/sawtooth/sine). No spatial panning, no ambient layer, no voice lines, no dynamic filter.
- **Action:** Add AudioContext panner nodes, ambient sound layers, and at minimum a low-pass filter when Sanctum is low.

### 19. **Mobile / Touch Support — NOT IMPLEMENTED**
- **Spec:** Virtual on-screen touch buttons for Q-W-E-R, touch-drag panning, pinch-to-zoom.
- **Reality:** No touch UI elements. OrbitControls works with touch but no tower placement via touch.
- **Action:** Add virtual button overlay for tower selection and placement, and ensure touch events work for grid interaction.

---

## 🟢 LOW — Nice-to-Have Improvements

### 20. **Performance: No Spatial Hash Grid**
- Tower targeting scans all creeps for every tower (O(towers × creeps)). With 20 towers and 200 creeps, that's 4,000 distance checks per frame.
- **Action:** Implement a spatial hash grid to limit range checks to nearby creeps only.

### 21. **Performance: No Frustum Culling**
- All objects (decals, debris, particles, FX) are rendered regardless of whether they're on screen.
- **Action:** Enable Three.js frustum culling (default on) and ensure all objects have proper bounding spheres.

### 22. **Performance: No LOD**
- All 3D models are full detail regardless of camera distance.
- **Action:** Add LOD groups for distant objects, especially debris and particle systems.

### 23. **Weather / Dynamic Environment**
- **Spec:** Dynamic weather, day/night cycle, volumetric god-rays.
- **Reality:** Static sky dome, static god-ray shafts (animated only via opacity sine), no weather.
- **Action:** Add a simple weather system (rain particles, fog density changes) and a day/night cycle affecting lighting.

### 24. **Unity Scripts — Stubs**
- The Unity C# scripts are basic stubs compared to the web implementation. They lack:
  - GLTF model loading
  - PBR materials
  - Particle systems
  - Post-processing
  - Flow field pathfinding
  - Full tower upgrade branches
- **Action:** Bring Unity scripts to feature parity with the web version, or focus the web version as the primary build and use Unity for a future port.

### 25. **Decal Pool — Not Pooled**
- Scorch, crater, oil, and moss decals are created/destroyed dynamically. They also accumulate (up to 90) before old ones are removed.
- **Action:** Pool decal meshes and recycle them instead of creating new ones.

### 26. **Damage Number DOM Elements — Not Pooled**
- Every damage number creates a new DOM `<div>` element. With many hits, this creates DOM churn.
- **Action:** Pool damage number elements and reuse them.

### 27. **Wave Caller Button Missing**
- The "Send Wave Now" button from the UI spec doesn't exist in the bottom tray.
- **Action:** Add a "Call Wave" button to the HUD that grants early scrap bonus.

### 28. **Tower Priority Cycling in Inspector**
- The inspector mentions "click tower to cycle" but it's non-functional.
- **Action:** Implement the priority cycling UI and make it actually change tower targeting behavior.

---

## Summary Priority Matrix

| Priority | Area | Spec Coverage | Effort |
|----------|------|--------------|--------|
| 🔴 Critical | Sanctum Abilities (D/F) | 0% | Medium |
| 🔴 Critical | Armor System | 0% | Medium |
| 🔴 Critical | Meta-Progression | 0% | High |
| 🔴 Critical | Flow Field Pathfinding | 0% | High |
| 🔴 Critical | Object Pooling | 0% | High |
| 🟠 High | Targeting Priority | 10% | Medium |
| 🟠 High | Tower Branch Mechanics | 20% | High |
| 🟠 High | Missing Creep Types | 83% | Medium |
| 🟠 High | Boss Mechanics | 10% | High |
| 🟠 High | Interest & Early Call | 0% | Medium |
| 🟡 Medium | Mana Recharge | 0% | Low |
| 🟡 Medium | Pause Timer Fix | 0% | Low |
| 🟡 Medium | Screen Shake | 0% | Low |
| 🟡 Medium | Post-Processing Bloom | 0% | Medium |
| 🟡 Medium | Debuff Icons | 0% | Medium |
| 🟡 Medium | Audio Upgrades | 10% | Medium |
| 🟡 Medium | Mobile Touch Support | 0% | High |
| 🟢 Low | Spatial Hash Grid | 0% | Medium |
| 🟢 Low | Weather / Day-Night | 0% | High |
| 🟢 Low | Unity Feature Parity | 20% | High |

