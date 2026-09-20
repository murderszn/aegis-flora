# Aegis Flora: Unity 3D Integration Guide

This guide details how to import the generated 3D Blender models, PBR textures, and C# mazing scripts into **Unity (URP / HDRP)** to transition from the HTML5 prototype to a full commercial-tier 3D tower defense game.

---

## 1. Project Creation & Render Pipeline
- **Recommended Unity Version:** Unity 2022.3 LTS or Unity 6 (6000.x LTS).
- **Template:** **Universal 3D (URP)**.
- **Color Space:** Set to `Linear` (`Project Settings > Player > Other Settings > Color Space: Linear`).

---

## 2. 3D Model & Texture Import Pipeline

The automated Blender pipeline generated production-ready `.glb` 3D models and renders located in:
```
Unity/Assets/Models/  (and blender_pipeline/models/)
├── tower_prism_gatling.glb       <-- Corinthian Column, Brass Gears, Cyan Crystal
├── tower_bloom_cannon.glb        <-- Stone Dais, Mechanical Lotus Petals, Heavy Mortar
├── tower_resonance_monolith.glb  <-- Basalt Obelisk, Tuning Forks, Wisteria, Violet Ring
├── sanctum_core_rotunda.glb      <-- 8-Pillar Tholos Temple, Armillary Rings, Mana Crystal
├── enemy_skitter_scout.glb       <-- Hexapod Recon Drone, Brass Cage Ribs, Cyan Optics
├── enemy_tread_tank.glb          <-- Heavy Iron Hull, Brass Wheels, Dual Cannons, Wedge Plow
├── enemy_rotor_drone.glb         <-- Dual Counter-Rotating Rotors, Searchlight, Landing Skids
├── enemy_diesel_walker.glb       <-- Heavy Boiler Chassis, Autocannon Arm, Hydraulic Claw
├── enemy_zeppelin_sky_hull.glb   <-- Armored Dirigible, 5 Girdle Rings, Gondola, Propellers
├── enemy_goliath_colossus.glb    <-- Titan Walking Fortress, Red Eye, Quad Stacks, Arm Cannons
├── statue_automata_athena.glb    <-- Classical Winged Goddess Statue, Brass Wings & Spear
├── accent_masonry_blocks.glb     <-- Carved Marble Blocks, Inlaid Brass Conduits & Flowers
├── accent_column_pediment.glb    <-- Fluted Corinthian Column with Triangular Pediment & Ivy
├── flora_cypress_tree.glb        <-- Columnar Mediterranean Cypress with Stone Plinth & Brass Clamp
├── flora_olive_tree.glb          <-- Gnarled Olive Tree with Cloud Canopy & Trailing Wisteria
├── ruin_grand_colonnade.glb      <-- Curved Colonnade with Architrave, Fallen Drum & Peonies
├── flora_wildflower_cluster.glb  <-- Alpine Peonies, Chrysanthemums, Lavender & Mana Spores
├── prop_treasure_chest.glb       <-- Ornate Steampunk Strongbox with Spilling Coins & Mana Crystals
├── prop_relic_urn.glb            <-- Classical Greco-Roman Amphora with Gold Filigree & Wisteria
├── flora_clockwork_lotus.glb     <-- Triple-Tiered Lotus Bloom with Cyan Mana Core in Marble Basin
└── flora_golden_chrysanthemum.glb <-- Radiating Golden Chrysanthemum in Engraved Brass Planter
```

### Import Steps:
1. Drag the `.glb` files from `blender_pipeline/models/` directly into your Unity Project window under `Assets/Models/`.
2. Select each imported model in Unity:
   - In the **Model** tab: Enable `Generate Colliders` (or add a Box/Capsule collider on the prefab).
   - In the **Materials** tab: Set `Location: Use External Materials (Legacy)` or extract materials to customize them.
3. Configure URP Materials:
   - **Carrara Marble:** `Base Map: #E0DAC8`, `Smoothness: 0.65`, `Subsurface Scattering: Enabled` (if using HDRP/URP Subsurface).
   - **Antique Brass:** `Base Map: #C59B27`, `Metallic: 0.92`, `Smoothness: 0.75`.
   - **Cyan Mana Core:** `Emission: #00F5D4`, `Emission Exposure: +3.0` (with URP Bloom).
   - **Cast Iron:** `Base Map: #2E3136`, `Metallic: 0.85`, `Smoothness: 0.5`.

---

## 3. Camera & Viewport Setup (2.5D Orthographic Perspective)

To match the exact tactical perspective of Dota 2 and classic mazing tower defense:
1. Select the **Main Camera**:
   - **Projection:** `Orthographic`
   - **Size:** `16` (adjust based on screen aspect ratio)
   - **Transform Position:** `(36, 32, -5)` (centered relative to the 36x20 grid)
   - **Transform Rotation:** `(54.736, 45, 0)` (standard true isometric angle)
2. **Lighting:**
   - Directional Sun: `Intensity: 2.5`, `Color: Warm White (#FFF4E5)`, `Shadows: Soft Shadows`.
   - Ambient Fill Light: `Color: Deep Cerulean Teal (#1A4550)`.
   - Post-Processing Volume:
     - **Bloom:** `Threshold: 0.9`, `Intensity: 1.8` (causes cyan crystals, lasers, and explosions to glow brilliantly).
     - **Tonemapping:** `ACES`.

---

## 4. C# Mazing & Tower Scripts Included

All core scripts are pre-authored and ready under `Unity/Assets/Scripts/`:

1. [`GridManager.cs`](file:///Users/jahflyx/towers/Unity/Assets/Scripts/Mazing/GridManager.cs)
   - Manages the `36 x 20` grid coordinates, cell occupancy, world-to-grid raycasting, and placement validation.
2. [`AStarPathfinder.cs`](file:///Users/jahflyx/towers/Unity/Assets/Scripts/Mazing/AStarPathfinder.cs)
   - Fast pure-C# A* pathfinder. Includes `ValidateMazeWithBlock(grid, x, y)` which guarantees players can never wall off the Sanctum.
3. [`TowerController.cs`](file:///Users/jahflyx/towers/Unity/Assets/Scripts/Towers/TowerController.cs)
   - Controls 3D turret aiming (`Quaternion.Slerp`), rotating Gatling barrel clusters, muzzle flash particles, continuous LineRenderer laser beams, and mortar launching.
4. [`CreepAgent.cs`](file:///Users/jahflyx/towers/Unity/Assets/Scripts/Enemies/CreepAgent.cs)
   - Controls enemy creep movement along A* waypoints, hit flash shader feedback, health bars, slow debuffs, and death explosions.
5. [`BallisticProjectile.cs`](file:///Users/jahflyx/towers/Unity/Assets/Scripts/Combat/BallisticProjectile.cs)
   - Handles true 3D parabolic arcing artillery trajectories and AoE splash detonation.
6. [`DotaHUDController.cs`](file:///Users/jahflyx/towers/Unity/Assets/Scripts/UI/DotaHUDController.cs)
   - Binds keyboard hotkeys (`Q, W, E, R, Space, Esc`), resource readouts, and tower placement previews.
