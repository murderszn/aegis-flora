# Aegis Florae Unity port contract

This contract separates the playable browser game's current rules from old documentation and from the incomplete Unity starter. `game.html` is the gameplay baseline; `tests/` contains regression evidence for named behaviors. The contract does not certify the Unity scripts as a faithful port.

## Verified source baseline

| Rule | Browser source | Unity port requirement |
| --- | --- | --- |
| Logical field | `GRID.W = 36`, `GRID.H = 20`, `GRID.CELL = 2.0` (`game.html`, around line 917) | 36 columns by 20 rows; each logical cell is 2 world units. Keep render decoration separate from occupancy. |
| Route endpoints | `SPAWN = (0,10)`; `SANCTUM = (35,10)` | Ground route begins at the spawn and reaches the Sanctum. Both endpoint cells are protected from placement. |
| Opening economy | `START_CASH = 20`, `START_LIVES = 15` | Start with 20 Scrap and 15 lives before any explicitly selected meta-progression modifier. |
| Sale refund | `SELL_RATE = 0.75`; sale uses `Math.round(invested * SELL_RATE)` | Refund 75% of recorded tower investment, rounded with JavaScript-compatible positive half-up behavior. Do not calculate from current tower level cost alone. |
| Match length | `WAVE_MAX = 50` | Full parity means 50 progressive waves. A short Unity demonstration capped at 3 waves is a vertical-slice fixture, not full-game parity. |
| Grid scale | `CELL_SIZE = 2.0` | Visual paving can be irregular; world/grid conversion and path rules remain stable. |

The source also defines progression modifiers, so 20 Scrap, 15 lives, and a 0.75 sale rate are the unmodified baseline rather than a promise that every profile always starts there. Record a progression state when comparing a run.

## Documentation discrepancies and starter status

- `SHIPPING_FEATURE_MATRIX.md` calls the board 26×18. Its own reference to `COLS=26, ROWS=18` conflicts with the live `game.html` constants and must not be copied into the port.
- README and older design tables contain older opening economy values. The live source constants above take precedence for porting.
- The Unity starter `GameManager` currently serializes 100 starting Scrap and 20 max lives. These defaults are not the source baseline and need correction in a gameplay-parity implementation.
- At the initial audit, the Unity directory contained only starter scripts and prototype GLBs. The migration now adds a pinned project manifest, startup/courtyard scenes, initialization/build tooling, and a three-wave runtime in source. These additions await Unity Editor compilation and visual verification; they remain incomplete against the 50-wave source contract.
- Source regression tests are useful evidence, but JS source-inspection tests do not prove a Unity build behaves the same.

## Gameplay behaviors to preserve

The table names source behavior to audit when extending the Unity slice. Consult `game.html` and the listed tests for implementation details; this is an acceptance index, not a substitute for test porting.

| Area | Contract summary | Existing source evidence |
| --- | --- | --- |
| Mazing | Reject out-of-bounds, occupied, portal, and route-sealing placements. Ground units must retain a route; validate speculative occupancy before spending or committing placement. | `first_run_tutorial.test.js`, `large_wave_performance.test.js` |
| Ground and air | Ground units follow the maze route. Flying units bypass maze walls and use air targeting rules. Towers have different air/ground capability. | `large_wave_performance.test.js`, `tower_targeting.test.js`, `tower_branches.test.js` |
| Towers | Four core combat roles: `gun` (Petal Gatling), `rocket` (Bloom Mortar), `beam` (Prism Pillar), `slow` (Resonance Obelisk). Preserve their two branch choices and damage/targeting behavior. `blocker` is a progression-unlocked maze obstacle, not a fifth damage tower. | `tower_branches.test.js`, `first_run_tutorial.test.js` |
| Enemies | Ground scout, tank, walker, prowler and ram; air drone and zeppelin; Goliath boss. Preserve armor, evasion, leak damage, boss phases, and counters rather than reducing all units to one generic creep. | `large_wave_performance.test.js`, `missing_enemy_archetypes.test.js`, `boss_phases_mechanics.test.js` |
| Wave progression | 50 waves with scaling and boss encounters on waves divisible by 10; wave completion/victory follows the actual spawn and active-enemy state. | `large_wave_performance.test.js`, `boss_phases_mechanics.test.js` |
| Economy and combat | Placement/upgrade costs, kill rewards, tower investment, sale rounding, armor mitigation and damage types must agree with source data. Transactions should not partially spend on invalid placement. | `tower_targeting.test.js`, `tower_branches.test.js`, economy-related tests in `tests/` |
| Targeting | First, Last, Strongest, Weakest and Closest modes use source progress/health/distance comparisons. | `tower_targeting.test.js` |
| Sanctum powers and progression | Preserve Bramble Root and Solar Flare, glyph unlocks/perks, and persistence semantics when implementing those later milestones. | `game.html` ability/progression sections; `tests/` glyph and ability cases |
| Simulation controls | Pause freezes gameplay systems; 1×/2×/4× speed applies consistently; preserve keyboard and gamepad bindings and settings where in scope. | `tower_targeting.test.js`, `tactical_clarity.test.js`, `game.html` input/settings sections |

The source has additional tutorial, save, UI, audio, and progression behavior. A short visual slice may omit these, but completion claims should identify the omissions rather than imply full parity.

## Asset contract

`ArtPipeline/asset-manifest.json` is the machine-readable inventory and `ArtPipeline/asset-manifest.schema.json` its schema. Current concept images are references; existing `Unity/Assets/Models/*.glb` files are prototype assets with provenance/production readiness not established by their presence. The manifest deliberately records the five visual pilots as not yet generated or approved. No Meshy generation or Poliigon acquisition is claimed.

The initial visual pilot is Petal Gatling, Diesel Walker, Sanctum rotunda, modular ruin pieces, floral groups, and a small shared surface family. The asset workflow defines candidate references, file staging, cleanup evidence, license records, review states, and importer checks. Do not place restricted Poliigon source downloads or derivatives in a public repository. Keep those files in a private staging location and only stage distributable outputs when the applicable license permits it.

See [ArtPipeline/ACQUISITION_AND_CLEANUP.md](ArtPipeline/ACQUISITION_AND_CLEANUP.md) for the auditable authoring steps. Unity import tooling is under `Assets/Editor/AegisAssetImport.cs`; its scope is intentionally limited to `Assets/Aegis/Art/`.
