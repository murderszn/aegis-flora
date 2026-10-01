# Aegis Florae — Unity migration and visual production plan

Prepared 2026-10-01. This is a proposed implementation plan, not a claim that the Unity port or new artwork is complete. Use [the implementation prompt](UNITY_VISUAL_MIGRATION_PROMPT.md) to begin executing it.

The goal is a native Unity tower defense game whose playable battlefield carries the carved architecture, intricate machinery, abundant flowers, and dramatic atmosphere of our concept art. Build one convincing, playable courtyard before producing the entire asset library.

## 1. What the repository actually contains

| Area | Observed state | Migration consequence |
| --- | --- | --- |
| Runtime | Three.js gameplay in `game.html`, HTML/CSS HUD, Web Audio, browser storage; Electron desktop packaging | Port gameplay and presentation into C# and Unity assets. A Unity build replaces the Electron game runtime. |
| Unity starter | Seven C# scripts and existing GLB models; no `Packages/`, `ProjectSettings/`, scenes, or configured prefabs | Establish a real project, compile it, and review the scripts before treating them as reusable. |
| Live rules | `GRID = { W: 36, H: 20, CELL: 2.0 }`; 50 waves; base starting scrap 20, lives 15, sell rate 0.75 | Extract these rules from live code and regression cases. The starter's 100 scrap / 20 lives and older documentation are not the baseline. |
| Documentation | Shipping matrix still describes a 26×18 grid; README contains older economy values | Resolve discrepancies in a port contract. Code behavior plus executable tests outrank stale tables. |
| Gameplay assets | Procedural Blender models with simplified forms; starter Unity uses basic components | Retain useful proportions and temporary models during the mechanics port, then replace visible assets deliberately. |
| Art direction | Existing master, map, sanctum, tower, and enemy reference images | Use specific files and matching camera comparisons to judge progress. |

`game.html` also explicitly requests a “Chunky toy-like presence (Roblox vibe)” through its `CHUNK_*` scaling. That direction conflicts with the user's desired visual target. Choose new proportions by comparing silhouettes at gameplay zoom; do not carry that instruction into the final art brief.

The existing Unity integration guide overstates readiness: direct GLB import requires an importer, and its URP/HDRP instructions mix features from different pipelines. It remains historical context; this plan governs the proposed migration.

## 2. Visual target and reference hierarchy

| Reference | What to match |
| --- | --- |
| `assets/aegis_master.jpg` | Warm stone, deep teal atmosphere, golden and pink floral masses, dramatic cloud silhouettes |
| `assets/battlefield_map.jpg` | Architectural enclosure, carved borders, cracked paving, mountains, layered depth |
| `assets/sanctum_core.jpg` | Monumental rotunda, brass armillary rings, suspended cyan crystal, flowering overgrowth |
| `assets/3d_turret_pbr.jpg` | Engraved metal, substantial mechanics, Corinthian pedestal, believable materials |
| `assets/3d_walker_pbr.jpg` | Riveted plates, joints, pistons, boilers, worn iron and brass, amber optics |
| `assets/concepts/tower_heliostat_orchid.png` | Distinctive botanical machinery, ceramic petals, mirror supports, concentrated energy |
| `assets/aegis_gameplay_poster.jpg` and existing Blender renders | Comparison baseline for the current simpler appearance |

Art direction: **a living Greco-Roman sanctuary defending itself against industrial automata, presented with the atmosphere of a Romantic landscape painting and the clarity of a strategy game.** The references mix illustrative scenery and realistic object renders. Unify them through composition, material scale, restrained color, and lighting; reproducing every illustration stroke is a separate shader project.

Concrete changes:

- Carve flutes, capitals, plinth edges, gear silhouettes, and armor overlaps into visible geometry. Bake tiny filigree, scratches, and shallow relief into maps.
- Replace broad white plastic-looking surfaces with warm veined stone and broken edges. Metal needs varied roughness, patina, and controlled highlights.
- Arrange flowers in uneven masses around architecture. Use larger blooms as punctuation, smaller plants as supporting density, and clear ground around tactical cells.
- Frame the board with ruins and landscape. Preserve the open, player-authored maze; the decorative maze in the map concept must not become a mandatory route.
- Use warm sunlight, cool shadow fill, dark foliage, and selective cyan energy. Keep the center quieter than the perimeter.
- Give each tower a recognizable profile at ordinary zoom. Every upgrade branch needs a visible change such as barrel assembly, petal arrangement, lens, or tuning structure.

Success must be visible with bloom disabled. Texture detail and effects cannot compensate for weak shapes or composition.

## 3. Technical direction

**Starting assumption:** Windows x64 desktop / Steam is the primary release, reflecting the existing release checklist. macOS and Linux builds can follow. Browser access is a separate scope decision; a native Unity migration does not retain static HTML deployment automatically.

Start with a supported patch of **Unity 6.3 LTS and URP**, pinning the exact Editor and compatible package versions when creating the project. Unity lists 6.3 as an available LTS; URP supports a broad range of devices. This recommendation also follows Unity's stated 2026 emphasis on advancing URP and maintaining HDRP. It is a project choice, not a claim that URP automatically achieves the reference look. [Unity releases](https://unity.com/releases/unity-6), [URP introduction](https://docs.unity3d.com/6000.0/Documentation/Manual/urp/urp-introduction.html), [render pipeline strategy](https://discussions.unity.com/t/render-pipelines-strategy-for-2026/1710004).

Use Linear color, HDR rendering, a measured exposure/color grade, soft directional shadows, baked lighting for the environment, reflection probes, and probe lighting for dynamic units. Start with an orthographic tactical camera; add a bounded perspective showcase camera after readability works. Avoid building both pipelines. Revisit HDRP only if a measured visual requirement cannot be met within the chosen URP workflow and supported hardware.

Required foundations: Input System, TextMeshPro with uGUI for the gameplay HUD, Unity Test Framework, and a compatible glTFast package if retaining GLBs. Cinemachine is optional. Avoid adding DOTS/ECS, networking, or an asset streaming framework until profiling or product scope justifies them.

Proposed layout inside the existing `Unity/` folder:

```text
Unity/
  Packages/                     # manifest and dependency lock
  ProjectSettings/              # Editor version, input, render/build settings
  Assets/
    Scripts/                    # audit existing scripts; migrate in place
    Aegis/
      Art/{Models,Materials,Textures,Animations,VFX}/
      Audio/
      Data/{Towers,Enemies,Waves,Maps}/
      Prefabs/{Towers,Enemies,Environment,UI}/
      Scenes/{Boot,MainMenu,SanctuaryCourtyard,ArtReview}/
      Settings/                 # URP assets and quality/volume profiles
    Editor/                     # import validation and build automation
    Tests/{EditMode,PlayMode}/
```

Keep the simulation separate from views. Use ScriptableObjects for immutable definitions, explicit runtime state for health/economy/cooldowns, stable IDs for saves, pooled enemies/projectiles/effects, and a fixed simulation step with interpolated presentation. Pause and speed changes must apply consistently to gameplay, timers, and effects.

Use a shared goal-rooted flow field for moving hordes. Placement validation must leave routes for the spawn and all active ground units, then commit occupancy and currency atomically. Honor the source game's neighbor rules; visual irregularity in paving must not change logical cell occupancy. Flying units follow their own path and targeting rules. Do not replace the mazing system with a general NavMesh without demonstrating equivalent behavior.

## 4. Asset production: Meshy → Blender → Unity, with Poliigon materials

These services are **authoring tools**. The shipped game consumes approved local assets and runs without Meshy/Poliigon account access.

### Meshy: concept-driven geometry drafts

Use our own reference images for Image-to-3D wherever possible. Meshy documents text/image generation and FBX/GLB export. Its Unity bridge is optional: the official plugin page requires Pro or above and lists testing on Unity 6000.0.45f1, so compatibility with our pinned version must be checked. Manual export is a valid primary workflow. [Meshy docs](https://docs.meshy.ai/en), [Unity integration](https://www.meshy.ai/integrations/unity).

1. Prepare an isolated asset reference with unclipped silhouette and neutral illumination. Scene illustrations should first become consistent object views; do not generate the entire battlefield as one mesh.
2. Generate one representative tower, ruin, and enemy before committing to bulk production. Compare multiple candidates to the same reference and keep only useful results.
3. Save the reference, prompt, task ID, chosen generator/settings, original export, and selection notes.
4. Separate turret bases, yaw pivots, barrels, mirror petals, armillary rings, legs, rotors, and other moving parts in Blender. Generation may fuse these together.
5. Repair geometry, retopologize as needed, unwrap UVs, bake detail, normalize scale, and create LODs and simple collision proxies.
6. Export an FBX with textures for the reviewed production asset, or retain GLB through a tested importer. Commit Unity metadata with the asset.

Meshy output is an art draft. A high-detail preview does not establish animation readiness, acceptable topology, or in-game performance. Mechanical walkers and multi-legged units need rigging appropriate to their construction; auto-rigging is only a candidate workflow after deformation checks.

### Poliigon: a controlled surface palette

Acquire a small family of compatible materials first: warm marble/limestone, worn paving, patinated brass/copper, dark iron, soil/moss, stone/rock, plus an outdoor HDRI for lighting tests. These are search categories, not assertions that a particular named asset exists. Poliigon supports PBR textures, FBX models, and HDRIs in Unity. Its current tutorial uses HDRP-specific material/sky instructions, which need adaptation for this URP project. [Poliigon Unity guide](https://help.poliigon.com/en/articles/2285413-using-poliigon-assets-in-unity-updated-2026).

Apply these materials in Blender/Unity **after** Meshy generation. Poliigon's published standard terms restrict AI/ML use and raw asset redistribution, while permitting use in games subject to the applicable license. Keep downloads and derived restricted material files in controlled storage, with references rather than raw assets in a public repository. Record the license and permitted collaborators. [Poliigon licensing guidance](https://help.poliigon.com/en/articles/8749749-asset-use-licensing).

For URP Lit, build an explicit conversion/import preset:

| Input | Unity treatment |
| --- | --- |
| Base color | sRGB texture; color only, without painted lighting |
| Normal | Normal Map import type; verify tangent orientation under a rotating test light |
| Metallic | Linear data; metallic texture red channel |
| Roughness | Convert to smoothness using `1 - roughness`; pack in metallic texture alpha and select metallic-alpha smoothness |
| Ambient occlusion | Linear data; occlusion texture green channel |
| Height | Preserve as source data; bake subtle relief into normals or use a deliberate custom shader |
| Emission | Separate authored mask and controlled HDR color |

A source ORM texture is not automatically compatible with these slots. Verify packing against the pinned shader and a reference material ball. Do not copy HDRP mask packing or tessellation settings into URP Lit. [URP Lit reference](https://docs.unity3d.com/6000.0/Documentation/Manual/urp/lit-shader.html).

Existing GLBs need a compatible importer such as `com.unity.cloud.gltfast` or conversion to FBX. Simply copying them into an unconfigured Unity project is insufficient. [Unity glTFast Editor import](https://github.com/Unity-Technologies/com.unity.cloud.gltfast/blob/main/Packages/com.unity.cloud.gltfast/Documentation~/ImportEditor.md).

### Initial asset order and provisional budgets

All numbers below are proposed starting budgets, to revise after testing at actual zoom and worst-case unit counts.

| Priority | Asset group | Starting allocation |
| --- | --- | --- |
| First | Petal Gatling and Diesel Walker | Tower 12–25k triangles; repeat enemy 8–18k at LOD0; mostly 2K textures |
| First | Sanctum rotunda | 35–60k triangles across reusable parts; selective 4K hero surface |
| First | Modular ruin kit | Column, capital, wall, arch, stair, paving, rubble; approximately 1–8k triangles per module, shared trims/materials |
| First | Foliage kit | Peony/chrysanthemum clusters, ivy strips, grass, cypress; approximately 0.3–3k triangles per cluster, shared atlases |
| Next | Mortar, heliostat/prism, resonance/mycelium visuals | Similar tower budgets; preserve four existing gameplay roles |
| Next | Scout, tank, drone, zeppelin, boss | LODs by projected size; boss approximately 35–60k triangles at LOD0 |
| Later | Upgrade attachments, props, weather variants | Reuse accepted meshes/materials before introducing unique sets |

Create at least three LODs for frequently repeated meshes, cull tiny accents, and limit material slots. Many repeated LOD0 assets can exceed the scene budget despite acceptable per-asset counts. Do not use the “150k LOD0” text in the walker concept as a shipping requirement.

For each asset, maintain a manifest entry: stable ID, source/reference path or URL, Meshy task/prompt, material IDs, license record, raw export location, final path, dimensions/pivots, triangle counts per LOD, texture sizes, collision/rig status, and review status (`draft`, `cleanup`, `accepted`).

## 5. Lighting, scene composition, and combat presentation

Create `ArtReview` with a material ball, one tower, one enemy, foliage, a ruin, and three saved camera positions. Validate materials under neutral lighting before introducing the cinematic grade.

For the courtyard, use one warm sun with readable soft shadows, cool ambient fill, bounded SSAO, reflections that reveal brass, and selective bloom. Design cloud masses and distant alpine silhouettes to echo the references. Atmospheric depth can start with fog, sky artwork, and restrained particles; true volumetric shafts require a separately evaluated URP-compatible solution. Do not assume built-in HDRP volumetrics, stone subsurface scattering, or tessellation are URP toggles.

Organize the scene in layers: low foreground framing, clear combat floor, taller perimeter ruins, then mountains/sky. Fade tall scenery when it blocks ground units. Small irregular heights are visual; traversal and placement stay consistent. The Sanctum should dominate composition without obscuring its approach.

Combat requirements:

- Gatling: barrel rotation, short recoil, precise muzzle event, readable tracers; cap shell casings and light flashes.
- Mortar: visible flight arc and landing telegraph, sharp impact followed by a restrained dust ring and temporary scorch.
- Prism/heliostat: focused beam with an impact point, restrained energy halo, animated machinery.
- Resonance/mycelium: distinct pulse radius and timing, clear slow/stun feedback, brief rings.
- Enemies: gait/rotor/tread motion, localized hit response, damage progression, capped pooled debris.
- Tactical clarity: retain silhouettes, path previews, selection outlines, and threats while reducing scenery saturation and effect density.

Keep gameplay sharp. Depth of field and stronger camera motion belong in optional showcase shots. Default camera shake should be subtle, adjustable, and disabled when requested.

Use a dark teal HUD with restrained brass framing, legible type, and portraits rendered from actual approved prefabs. Rebuild the resource readouts, build dock, wave preview, selection/upgrades, abilities, minimap, tutorial, settings, pause, and end screens in Unity. Decorative borders must not dominate the battlefield or block placement input.

## 6. Milestones and exit criteria

| Stage | Work | Evidence required to advance |
| --- | --- | --- |
| 0 — Contract | Extract source data and regression cases; inventory art; record platform, hardware and dependency assumptions | `PORT_CONTRACT.md`, baseline screenshots, prioritized asset manifest; grid/economy discrepancies explicitly resolved |
| 1 — Project | Configure Unity, URP, imports, input, camera, board, bootstrap scene, build entry point | Fresh checkout opens and compiles; board runs; native player launches; dependency versions committed |
| 2 — Mechanics slice | Placement/validation, shared pathfinding, scrap/lives, one tower and one enemy, wave scheduler, leaks, pause/restart | A complete short match runs; invalid placement spends nothing; active ground units cannot be trapped; unit tests plus PlayMode evidence |
| 3 — Visual benchmark | Approved tower, walker, Sanctum, modular courtyard section, flora, lighting, final camera, minimal HUD | Matched in-engine comparison shots and gameplay clip; materials also work without bloom; visual scorecard passes |
| 4 — Full gameplay | All four towers and branches, enemies and boss phases, 50-wave data, abilities, glyphs, tutorial, controls, audio | Feature contract fulfilled; combat/path/pause/save regression checks pass; full match and late-wave capture |
| 5 — Production polish | Complete asset replacement, animation/VFX, HUD, sound mix, accessibility and quality tiers | Worst-case crowd and crowded maze measured in a player build; visual/readability gates pass on every supported tier |
| 6 — Release | Native build profiles, versioned saves, installer/distribution, crash diagnostics and CI | Reproducible clean-machine build and launch, offline play, save reload, input/settings smoke test, release checklist |

Stage 3 is the principal art gate: improve it until the actual playable scene communicates the reference look. Do not scale production from an attractive isolated asset or an offline Blender render alone. Review screenshots with the user as visual feedback; routine approved implementation can keep progressing.

A rough planning allowance for an experienced Unity developer working with a technical artist is 2–4 weeks for the playable visual slice and another 6–12 weeks for a bounded migration/polish pass. These are estimates, not commitments; asset cleanup, actual available hours, and regression gaps determine the schedule. Re-estimate after Stage 3.

Before paid generation or buying materials, set a small pilot allocation for the three representative assets and essential surfaces. Record accepted-candidate yield and cleanup time, then calculate the larger budget from that evidence. Do not assume one generation per final asset, and do not hard-code subscription prices into the plan.

## 7. Acceptance criteria

**Visual scorecard:** use the three saved camera positions at the same resolution and grade each item 1–5: architectural shape, machinery silhouette/detail, surface response, floral density/composition, lighting/atmosphere, and combat readability. Target at least 4 in each category; no average may hide an unreadable board. This is an art review rubric, not an automated fidelity metric.

**Proposed performance target:** 60 FPS at 1920×1080 in a release player build on a declared minimum PC; record CPU, GPU, VRAM and quality preset before claiming a pass. Start with a stress fixture of 100 towers and 200 active enemies or the measured shipping peak, whichever is larger. Record p95 frame time, simulation time, allocations, memory, draw calls, and overdraw over at least 60 seconds after warmup. Target p95 frame time at or below 16.7 ms and no sustained allocation stream from steady-state combat. Capture 4× speed and placement/path updates under load separately. These are proposed gates, not measured results.

**Gameplay gate:** port the existing regression scenarios into meaningful Unity EditMode/PlayMode tests. Cover maze validation, ground versus air targeting, branch behavior, armor/damage, economy transactions, leak/death events, boss phases, wave completion/victory, pause/speed, and glyph persistence. Existing JS source-inspection tests are useful clues but cannot prove the Unity player works.

**Save gate:** versioned atomic local saves, load validation, sensible recovery from corrupt data, and stable content IDs. Browser `localStorage` does not transfer automatically into a native player; if retaining existing progress is required, plan an explicit browser export → Unity import path.

**Delivery gate:** Unity project settings, packages, scenes, configured prefabs, legal asset references, documented external asset staging, a runnable build, screenshots/video, and honest validation results. The final runtime must not require live calls to either asset service. Rework the Electron-specific release workflow into a Unity player build workflow when the native replacement is ready.

The first concrete deliverable is **one playable Sanctuary Courtyard with one beautifully finished tower, one animated enemy, the Sanctum, dense perimeter flora, and the reference lighting**. That establishes both the visual language and the cost of reproducing it across the full game.
