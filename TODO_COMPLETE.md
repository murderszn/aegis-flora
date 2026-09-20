# Aegis Flora 3D — Complete Task List
## Prioritized by Impact & Effort

---

## 🔴 CRITICAL — Must Have for Launch

### 1. Meta-Progression (Verdant Glyphs)
- [ ] **localStorage persistence** — Save/load glyph levels between runs
- [ ] **Foundry Engineering** — +2% tower damage per level (max 15), cost scales 50/80/110/...
- [ ] **Ancient Vaults** — +50 starting scrap per level (max 3), reduces initial bank
- [ ] **Flora Symbiosis** — +15% max Sanctum HP per level (max 5), also adds passive regen
- [ ] **Mazing Mastery** — Unlock decorative blocker walls (low-cost non-pathable tiles)
- [ ] **Glyph shop UI** — Add `G` key to open/close, show progress bars, enable purchases
- [ ] **Apply bonuses to new games** — Foundry dmgMult, startCash bonus, maxLives bonus

### 2. Sanctum Abilities (D/F keys)
- [ ] **Verdant Overgrowth (D)** — 35 Mana, 25s cooldown
  - [ ] Root all creeps in 4×4 radius around Sanctum for 3.5s (speed → 0)
  - [ ] Deal 60 Sonic damage instantly to rooted creeps
  - [ ] Visual: green shockwave ring + green mist overlay
  - [ ] Add `rooted` flag to creep state, handle in `update()` loop
- [ ] **Solar Flare (F)** — 75 Mana, 60s cooldown
  - [ ] Target mouse position on grid
  - [ ] Golden beam from sky → impact explosion
  - [ ] 800 Energy damage in 3-tile radius
  - [ ] Leave scorch + crater decals that linger 6s
  - [ ] Visual: impact explosion + ground scorching
- [ ] **Ability buttons in top HUD** — Disabled when on cooldown / not enough mana
- [ ] **Mana regen** — +4/sec (max 100), display in HUD

### 3. Armor System
- [ ] **Armor values per enemy** — spider: 0, tank: 8, walker: 10, boss: 16, drone: 1, ship: 6
- [ ] **Dota 2 armor formula** — `1 - (0.06*Armor)/(1+0.06*Armor)` for positive armor
- [ ] **Negative armor** (stripped) — `2 - 0.94^|Armor|` → damage amplification
- [ ] **Damage type modifiers** —
  - [ ] Kinetic: +25% vs unarmored, -40% vs armored
  - [ ] Energy: ignores 50% of armor value
  - [ ] Sonic: pure damage (ignores armor completely)
  - [ ] Blast: neutral (AoE splash only)
- [ ] **Shatter mechanic** — Resonance T3-B strips armor (set `shattered` timer = 3.0)
- [ ] **Update all tower damage** to use `applyDamage()` function instead of inline `hp -= dmg`

### 4. Flow Field Pathfinding (Performance)
- [ ] **Integration Flow Field** — Replace per-creep A* with single Dijkstra flood-fill from Sanctum
- [ ] **Distance potential field** — Each tile stores distance to goal
- [ ] **Gradient vector sampling** — Creeps sample vector of their tile each frame
- [ ] **Tower targeting optimization** — Spatial hash grid to limit range checks
- [ ] **Benefit** — 200+ creeps should maintain 60 FPS without frame drops

### 5. Object Pooling
- [ ] **Particle pool** — Pre-allocate 3,000 particle objects, recycle instead of create/destroy
- [ ] **Shell casing pool** — 50 spent brass casings
- [ ] **Floating combat text** — 500 damage number DOM elements
- [ ] **Decal pool** — 90 scorch/crater/oil moss decals, recycle instead of accumulate
- [ ] **FX pools** — Mortars, beams, rings, sparks, debris, lights
- [ ] **Benefit** — Zero GC allocations during runtime, eliminates frame stutters

### 6. Mobile / Touch Support
- [ ] **Virtual on-screen buttons** — Q/W/E/R for tower selection, D/F for abilities
- [ ] **Touch-drag camera panning** — Left-click drag to pan, pinch-to-zoom
- [ ] **Touch tower placement** — Tap grid cells, drag to preview, tap to place
- [ ] **Responsive HUD** — Bottom drawer resizes for touch targets
- [ ] **Benefit** — Game playable on tablets and phones

---

## 🟠 HIGH — Should Have for Gameplay Depth

### 7. Targeting Priority System
- [ ] **5 priority modes** — First (furthest along path), Last (closest to spawn), Strongest (highest HP), Weakest (lowest HP), Closest (Euclidean distance)
- [ ] **Cycle priority** — `T` key or click tower inspector to cycle through modes
- [ ] **Visual indicator** — Show priority icon above target preview
- [ ] **Benefit** — Strategic depth: focus fire, last stand, or quick swarm clearing

### 8. Tower Branch Upgrade Mechanics
- [ ] **Implement all T3 special abilities**:
  - [ ] **Gun T3-A Phalanx Petal-Storm** — 8-barrel rotary, incendiary tracers, -3 armor
  - [ ] **Gun T3-B Rail-Needler** — Pierces 3 creeps in a line
  - [ ] **Rocket T3-A Cluster Sporepod** — Splits into 2 mini-munitions, 2.4 splash
  - [ ] **Rocket T3-B Cataclysm Bloom** — Creates lingering fissures, 40% slow, aftershock dmg
  - [ ] **Beam T3-A Sol Invictus** — Piercing beam that leaves scorch line on ground
  - [ ] **Beam T3-B Refraction Prism** — Splits into 3 secondary beams (60% dmg each)
  - [ ] **Slow T3-A Chrono-Stutter** — Every 4th pulse = 0.75s stun (complete freeze)
  - [ ] **Slow T3-B Resonance Shatter** — Strips 50% armor/MR, +35% damage taken
- [ ] **Benefit** — Each upgrade branch feels distinct and strategic

### 9. Missing Creep Types
- [ ] **Steam Prowler** — Skirmisher with +20% dodge chance (5% base miss chance per attack)
- [ ] **Dreadnought Ram** — Siege ram that charges towers if trapped in maze >300% direct distance
- [ ] **Benefit** — More enemy variety and strategic counterplay

### 10. Boss Mechanics
- [ ] **Multi-phase bosses** — 3 phases with different abilities
- [ ] **EMP pulse** — Disables towers for 3s every 15s
- [ ] **Shield regeneration** — Bosses recover HP if not damaged within 5s
- [ ] **Micro-drone deployments** — Summon 3 small drones that hunt nearest tower
- [ ] **Benefit** — Epic finale waves feel like true "boss battles"

### 11. Economy: Interest & Early Wave Call
- [ ] **Interest system** — 5% interest on held scrap between waves, capped at +50/scrap/wave
- [ ] **Early wave call bonus** — `floor(T_remaining × 2.5 × sqrt(Wave))` bonus scrap + 15% bounty bonus
- [ ] **`N` key** — Call next wave early (with scrap bonus)
- [ ] **Benefit** — Strategic decision: spend scrap now or bank for interest?

### 12. Screen Shake + Post-Processing Bloom
- [ ] **Screen shake** — Trauma decay on heavy impacts (mortars, boss deaths)
- [ ] **Bloom effect** — Halo glow on emissive materials (cyan crystals, amber explosions)
- [ ] **Vignette** — Darkened edges for cinematic feel
- [ ] **Film grain** — Subtle noise for texture
- [ ] **Chromatic aberration** — Minor color shift on extreme brightness
- [ ] **Benefit** — Dota 2-level visual fidelity

### 13. Debuff Visual Icons
- [ ] **Frost/Slow** — Creeps turn frost-tinted cyan with frost trail particles
- [ ] **Armor Shattered** — Cracked shield badge over head
- [ ] **Stun** — Spinning gold star halo
- [ ] **Rooted** — Vine/bramble icon
- [ ] **Benefit** — Clear visual communication of status effects

### 14. Audio Upgrades
- [ ] **Spatial audio panning** — Positional turret shots and creep deaths
- [ ] **Ambient soundscape** — Wind, birds, distant fountain
- [ ] **Dynamic low-pass filter** — When Sanctum < 25% HP (ominous heartbeat pulse)
- [ ] **Dota-style announcer** — Key voice lines ("Path constructed!", "Colossus approaching!")
- [ ] **Benefit** — Immersion and polish

---

## 🟡 MEDIUM — Nice to Have

### 15. WASD Camera Panning
- [ ] **`W`** — Forward (toward Sanctum)
- [ ] **`S`** — Backward (away from Sanctum)
- [ ] **`A`** — Left (strafe)
- [ ] **`D`** — Right (strafe)
- [ ] **Benefit** — Quick repositioning without right-click dragging

### 16. Visual Mana Bar
- [ ] **Fill bar** — Same style as health bar (green gradient)
- [ ] **Show `/100`** — Next to number
- [ ] **Pulse when regenerating** — Soft glow pulse when mana increases
- [ ] **Benefit** — Matches the health bar UX

### 17. Ability Cooldown Indicators
- [ ] **D button** — Show root cooldown countdown
- [ ] **F button** — Show flare cooldown countdown
- [ ] **Benefit** — Player knows when abilities will be ready

### 18. Kill Feed / Toast Notifications
- [ ] **Multi-kill toast** — "5 Krax! +150 Scrap!" etc.
- [ ] **Wave completed** — "Wave 12 complete! +35 Scrap interest!"
- [ ] **Boss alerts** — "Goliath Colossus approaching the perimeter!"
- [ ] **Benefit** — Keeps player informed during intense combat

### 19. Debuff Visual Icons Above Creeps
- [ ] **Frost/Slow** — Cyan tint + frost trail particle effect
- [ ] **Armor Shattered** — Cracked shield badge sprite
- [ ] **Stun** — Spinning gold star halo sprite
- [ ] **Rooted** — Vine/bramble icon
- [ ] **Benefit** — Clear visual communication without needing tooltips

### 20. Weather / Day-Night Cycle
- [ ] **Dynamic weather** — Rain particles, fog density changes
- [ ] **Day/night cycle** — Affects lighting (softer, warmer tones at dusk)
- [ ] **Benefit** — Atmospheric variety

### 21. Performance: Spatial Hash Grid
- [ ] **Spatial hash for tower targeting** — Only check creeps in nearby cells
- [ ] **Benefit** — Reduce O(towers × creeps) to O(nearby creeps)

### 22. Frustum Culling + LOD
- [ ] **Enable frustum culling** (Three.js default, verify it works)
- [ ] **Add LOD groups** for distant models
- [ ] **Benefit** — Reduce GPU load on large battles

### 23. Damage Number Pooling
- [ ] **Pool DOM damage number elements** — Recycle instead of create/remove
- [ ] **Benefit** — No DOM churn during massive battles

### 24. Tower Sell Confirmation
- [ ] **Are you sure?** — Prompt before selling, show refund amount
- [ ] **Benefit** — Prevent accidental sales

### 25. Unity C# Script Parity
- [ ] Bring Unity scripts to feature parity with web version
- [ ] Or focus web as primary, use Unity for future port

---

## 🟢 LOW — Polish & Flourishes

### 25. Screen Space Effects (Post-Processing)
- [ ] Bloom simulation
- [ ] Vignette
- [ ] Film grain
- [ ] Chromatic aberration

### 26. Screen Shake
- [ ] On heavy impacts + boss deaths

### 27. Day/Night Cycle
- [ ] Affects lighting colors

### 28. Additional Sound Effects
- [ ] Variety: different rifle cracks, explosion variations

### 29. Additional Tower Skins
- [ ] Unlockable cosmetic styles

### 30. Replay System
- [ ] Record/playback of successful runs

### 31. Steam Achievements / Leaderboards
- [ ] Integration for PC release

### 32. Accessibility Options
- [ ] Colorblind mode (alternative damage numbers)
- [ ] Font scaling
- [ ] Key remapping

---

## 📊 Priority Matrix

| Priority | Category | Effort | Impact |
|----------|----------|--------|--------|
| 🔴 Critical | Meta-Progression | High | Very High |
| 🔴 Critical | Sanctum Abilities | Medium | Very High |
| 🔴 Critical | Armor System | Medium | High |
| 🔴 Critical | Flow Field Pathfinding | High | High |
| 🔴 Critical | Object Pooling | High | High |
| 🟠 High | Targeting Priority | Medium | High |
| 🟠 High | Tower Branch Mechanics | High | High |
| 🟠 High | Missing Creep Types | Low | Medium |
| 🟠 High | Boss Mechanics | Medium | High |
| 🟡 Medium | Interest & Early Call | Low | Medium |
| 🟡 Medium | Screen Shake + Bloom | Medium | High |
| 🟡 Medium | Debuff Icons | Low | Medium |
| 🟡 Medium | Audio Upgrades | Medium | Medium |
| 🟢 Low | WASD Panning | Low | Medium |
| 🟢 Low | Visual Mana Bar | Low | Medium |
| 🟢 Low | Ability Cooldowns | Low | Medium |
| 🟢 Low | Kill Feed | Low | Medium |

---

## 🚀 Recommended Next Steps (Choose Your Path)

### **Path A: Gameplay Depth First**
1. Meta-Progression (glyphs + localStorage)
2. Armor System + Damage Types
3. Tower Branch Upgrade Mechanics
4. Targeting Priority System

### **Path B: Visual Polish First**
1. Screen Bloom + Post-Processing
2. Debuff Visual Icons
3. Audio Upgrades (spatial + ambient)
4. Visual Mana Bar + Cooldown Indicators

### **Path C: Performance First**
1. Flow Field Pathfinding
2. Object Pooling (particles + FX)
3. Spatial Hash Grid (targeting optimization)
4. Frustum Culling + LOD

### **Path D: User Experience First**
1. WASD Camera Panning
2. Mobile/Touch Support
3. Kill Feed + Toast Notifications
4. HUD Refinement (mana bar, cooldowns)

---

*Last updated: `TODAY`*
*Generated by AI analysis of project gaps vs specifications*