# Aegis Flora: Solarpunk-Mecha Mazing Tower Defense
> *A neo-classical solarpunk reimagining of classic open-field mazing (Robo Defense / WC3 Wintermaul) infused with Dota 2-tier visual fidelity, dynamic particles, and competitive tactical depth.*

---

## Executive Summary & Concept

**Aegis Flora** fuses the timeless, addictive spatial strategy of **Robo Defense** (open-grid mazing, path manipulation, progressive upgrades) with the visual majesty, kinetic animations, and tactile HUD polish of **Dota 2**.

Set in a world where decaying Greco-Roman marble ruins have synthesized with ancient brass diesel-mechs and overgrown bioluminescent flora, players defend the **Verdant Sanctum** from endless waves of rogue autonomous industrial war-machines.

```
+---------------------------------------------------------------------------------------+
|                                    GAME OVERVIEW                                      |
+-------------------+-------------------------------------------------------------------+
| Genre             | Grid-Based Mazing Tower Defense (Open Field)                      |
| Primary Reference | Robo Defense (Lupis Labs) x WC3 Mazing Maps (Wintermaul / Gem TD) |
| Aesthetic Target  | Dota 2 VFX / Animation Polish x Solarpunk Neo-Classical Mech     |
| Perspective       | 2.5D Orthographic Isometric (pan/zoomable high-res playspace)    |
| Core Mechanics    | A* Dynamic Pathing, Physical Mazing, Branching Tower Upgrades,    |
|                   | Dota-Style Hero/Sanctum Abilities, Meta-Progression Skill Tree   |
| Target Platforms  | Modern Desktop Browsers (WebGL / Canvas), Steam / Mobile Ports    |
+-------------------+-------------------------------------------------------------------+
```

---

## Key Pillars

### 1. True Open-Field Mazing (The "Robo Defense" DNA)
- Unlike fixed-lane TDs (Kingdom Rush, Bloons), enemies spawn at ingress portals and compute the mathematically shortest path to the Sanctum across a wide, open grid.
- Every tower placed acts as a solid physical obstacle (`1x1` or `2x2`).
- Players sculpt lethal serpentine labyrinths, choke points, and kill boxes to maximize tower dwell time.
- **The Golden Mazing Rule:** Placement is validated before confirmation; players can never completely wall off the path (at least one valid open route must always connect every spawn to the sanctum).

### 2. Dota 2 Animation & Particle Polish
- **Kinetic Weight & Juice:** Turrets don't just shoot static sprites. Barrels recoil with hydraulic venting; blooming petal heat-sinks glow red-hot and dissipate steam; crystal beams refract and leave smoldering scorch tracks on marble pavers.
- **Clear Visual Hierarchy:** High-contrast particle effects (cyan beam lasers, amber muzzle flashes, emerald healing/buff auras, violet void debuffs) inspired by Dota 2's readable teamfight telegraphing.
- **Unit Reactions:** Creeps tilt into turns, kick up dust plumes from tank treads, stagger on heavy impacts, and detonate into satisfying physics debris upon destruction.

### 3. The Solarpunk-Mecha Aesthetic ("Aegis Flora")
- Weathered Corinthian and Ionic marble colonnades overgrown with golden chrysanthemums, weeping wisteria, and climbing ivy.
- Heavy bolted iron, cast brass, and exposed clockwork gears powered by luminous cyan mana-crystals.
- Atmospheric depth: volumetric sun shafts, drifting sakura/pollen motes, dynamic weather, and moody cumulus cloud shadows.

### 4. Dota-Inspired HUD & Control Layout
- **Bottom Tray Console:** Complete dashboard housing Sanctum Health, Energy/Scrap reserves, active Wave Radar, unit inspection card, and tower build dock bound to `Q - W - E - R`.
- **Tactical Overlays:** Real-time path visualization lines (color-coded flow vectors showing enemy trajectories), tower range indicators, DPS statistics, and targeting priority selectors (First, Strongest, Weakest, Closest).

---

## Documentation Directory

The project documentation is organized into deep-dive specifications:

1. [**Game Design Document (`GDD.md`)**](./GDD.md)
   * Detailed mechanics, mazing rules, pathfinding validation, tower archetypes, enemy units, economy, and meta-progression.
2. [**Art & Audio Specification (`ART_AND_AUDIO_SPEC.md`)**](./ART_AND_AUDIO_SPEC.md)
   * Visual direction, Dota 2-style VFX/animation guidelines, particle systems, camera angles, sound design, and UI wireframes.
3. [**Technical Architecture (`TECHNICAL_ARCHITECTURE.md`)**](./TECHNICAL_ARCHITECTURE.md)
   * WebGL/Canvas rendering pipeline, A* pathfinding & flow fields, Entity-Component-System (ECS), audio synthesis, and performance budgets.
4. [**Balance & Progression Sheet (`TOWER_AND_ENEMY_BALANCE_SHEET.md`)**](./TOWER_AND_ENEMY_BALANCE_SHEET.md)
   * Exact unit stats, damage types vs armor resistances, DPS calculations, cost scaling curves, wave configurations, and rewards.
5. [**UI & UX Specification (`UI_AND_UX_SPEC.md`)**](./UI_AND_UX_SPEC.md)
   * Dota 2 bottom console wireframes, placement validation UX (green/red ghosts), hotkeys, and camera controls.
6. [**Visual Art Bible & 3D Gallery**](/Users/jahflyx/.gemini/antigravity-cli/brain/12f2a710-ddb7-462b-81a0-8e6d90f6f154/visual_art_bible.md)
   * High-resolution asset generation benchmarks for weapons, mechs, maps, and artillery grounded in [`aegis.jpeg`](file:///Users/jahflyx/Downloads/aegis.jpeg).
7. [**Master Art & Graphics Overhaul Prompt (`GRAPHICS_AND_ART_OVERHAUL_PROMPT.md`)**](./GRAPHICS_AND_ART_OVERHAUL_PROMPT.md)
   * Actionable, production-grade prompt and art direction manifesto to achieve AAA visual fidelity across PBR shaders, chiaroscuro lighting, botanical layering, and Dota 2 juice.
