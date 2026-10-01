# Aegis Florae — implementation and asset prompts

Use the master prompt with this repository available to the implementation agent or developer. The companion [migration plan](UNITY_VISUAL_MIGRATION_PLAN.md) supplies rationale, source links, production stages, and review criteria. These prompts describe intended work; they do not mean that any model has already been generated or any Unity build validated.

## Master implementation prompt

```text
Act as a senior Unity gameplay engineer and technical artist. Migrate Aegis
Florae from its Three.js/Electron runtime into a native Unity game, and make
the playable scene visually match the project's existing concept art.

Read UNITY_VISUAL_MIGRATION_PLAN.md first. Execute its staged plan, beginning
with a runnable project and a playable visual slice. Work in the existing
Unity/ directory. Preserve the browser build as a reference during migration.
Do not replace the requested deliverable with documentation alone.

PRODUCT AND SOURCE OF TRUTH
This is an open-grid mazing tower defense game in an overgrown Greco-Roman
sanctuary. Players create routes with living brass-and-stone defense engines
against dieselpunk automata. Keep the player-authored maze and tower defense
identity while rebuilding the runtime and artwork.

Audit game.html and tests/ before coding. Extract a port contract containing
live grid, economy, tower/branch, enemy, wave, damage, ability, input, tutorial,
settings and progression behavior. Resolve stale documentation explicitly.
The inspected baseline is a 36x20 logical grid with 2-unit cells, 50 waves,
20 starting scrap, 15 lives, and 0.75 sell rate before applicable progression
modifiers. Confirm these against current source. Do not copy older README
balance tables or the Unity starter's defaults without checking them.

Review all seven existing Unity scripts. They are starting material, not a
complete port: the folder lacks configured project settings, packages, scenes
and prefabs. Keep useful behavior and repair or replace incomplete systems.
Preserve the four established tower roles; additional concept imagery can
inform their visuals without silently adding new gameplay archetypes.

VISUAL AUTHORITIES — OPEN AND INSPECT THESE FILES
- assets/aegis_master.jpg: palette, atmosphere and floral framing.
- assets/battlefield_map.jpg: courtyard, carving, paving and distant landscape.
- assets/sanctum_core.jpg: rotunda, armillary rings and cyan crystal.
- assets/3d_turret_pbr.jpg: detailed brass Gatling on carved stone.
- assets/3d_walker_pbr.jpg: believable riveted mechanical enemy.
- assets/concepts/tower_heliostat_orchid.png: botanical solar machinery.
- Other relevant assets/concepts/ and tower/enemy references.
- Existing gameplay poster and Blender renders: baseline for improvement.

ART DIRECTION
Create a living classical sanctuary with the drama of a Romantic landscape:
warm veined marble and limestone, deeply carved capitals, worn brass filigree,
dark riveted iron, golden chrysanthemums, pink peonies, draping ivy/wisteria,
deep teal atmosphere, sculptural storm clouds and distant alpine peaks.
Friendly energy is selective cyan; enemy optics are restrained amber/red.
Build coherent materials and proportions across every imported asset.

Match silhouette and composition before adding surface detail and effects.
Use geometry for visible outlines and baked maps for shallow detail. Group
flowers naturally with varied scale and layered density. Keep a clear combat
floor and tall ruins at the perimeter. Fade scenery that obscures units.
Avoid carrying the current chunky/toy scaling instruction into final assets.
Do not bake concept-art shadows into albedo. Do not use bloom to hide weak
geometry. The battlefield must still look convincing with bloom disabled.

UNITY FOUNDATION
Use Unity 6.3 LTS with an available supported patch, URP and Linear color.
Pin exact compatible Editor/package versions in version control. Establish
Packages/, ProjectSettings/, required metadata, a bootstrap scene, gameplay
scene, ArtReview scene, quality assets, and a repeatable native build command.
Use Input System, uGUI/TextMeshPro and the Unity Test Framework. Use a tested
glTFast package for existing GLBs, or convert them to FBX in Blender. Add
other packages only for a concrete need. Verify imports in a player build.

Default platform is Windows x64 desktop/Steam; keep later macOS/Linux support
possible. Treat browser/WebGL as a separately scoped target. Replace the
Electron runtime with a Unity player when the native port is release-ready.

Separate fixed-step simulation and runtime state from render/animation views.
Use immutable ScriptableObject definitions, stable content IDs, shared
pathfinding, pooled combat objects and measured quality scaling. Preserve
ground/air rules. Validate proposed occupancy before spending scrap or
placing a tower; all active ground units and spawn points must retain a route.
Use the live game's neighbor rules, not assumptions about diagonals. Keep
the logical board stable beneath visually uneven or richly detailed paving.
Implement pause and 1x/2x/4x speeds consistently across the whole simulation.

ASSET WORKFLOW
Use Meshy as an offline authoring tool for concept-based geometry drafts.
Start with Image-to-3D from our own isolated object references, using text
prompts to reinforce material/shape intent where the chosen workflow allows.
Generate a Petal Gatling, a ruin module and a Diesel Walker as pilot assets.
Save references, exact prompts, generator settings, task IDs and raw exports.
Inspect candidates before committing to batch production. Do not generate
the complete map as one mesh or claim AI output is production-ready.

Clean approved drafts in Blender: repair topology, retopologize when needed,
separate moving components, set pivots, normalize units, unwrap, bake detail,
author collisions, LODs, rigs and animations. Mechanical walkers need checked
joint motion; dense foliage needs an optimized atlas/instancing workflow.

Use Poliigon for a controlled family of marble, paving, brass, iron, soil,
rock and HDRI resources. Apply Poliigon materials after Meshy generation;
do not upload its downloads or derived textures into AI tools under standard
terms. Keep restricted asset files out of public source and record licenses.
Do not spend money, consume paid generation credits, or assert account access
unless the session authorizes it. If access is unavailable, continue project
and gameplay work with labeled placeholders and provide exact acquisition
instructions and an asset manifest. Record the final-art dependency honestly.

Use explicit URP material conversion: sRGB base color, Normal Map import,
linear metallic/occlusion data, smoothness = 1 - roughness. Configure metallic
red, metallic-alpha smoothness and occlusion green against the pinned shader.
Verify normal orientation and surface scale under neutral lighting. Do not
copy HDRP masks, subsurface, tessellation or sky-volume instructions into URP.

Start near 12-25k LOD0 triangles per tower, 8-18k per repeat enemy, and 35-60k
for the Sanctum or boss. Use mostly 2K maps, shared materials/trim sheets,
limited material slots and at least three LODs for repeated meshes. These are
provisional budgets: revise them using projected size and crowd profiling.

LIGHTING AND PRESENTATION
Set warm directional sunlight against cool ambient shadows. Use environment
bakes, dynamic probe lighting, reflection probes, restrained SSAO and bloom,
a controlled exposure/color grade, and layered atmosphere. Validate the
selected features in the pinned URP version. More elaborate volumetrics are
a separately measured addition, not assumed built-in switches.

Default to a readable orthographic tactical camera. Save matched overview,
combat-distance and close-up cameras for comparisons. Add a perspective
showcase mode later. Keep default gameplay free of obstructive depth of
field and excessive camera shake. Include scalable clarity/effect settings.

Make weapons mechanically expressive: barrel spin and recoil, mortar arcs
and telegraphs, focused beams with clear impacts, and timed resonance pulses.
Pool/cap debris, casings, particles, temporary decals and extra lights. Units
need believable gait/rotor/tread animation and readable hit/death feedback.

Rebuild the dark teal/brass HUD using actual prefab portraits, legible type,
resource/life/wave displays, build dock, minimap, selection/upgrade panel,
abilities, tutorial, pause/settings and end screens. UI interaction must not
place towers through the HUD. Preserve keyboard/gamepad behavior from source.
Implement Unity audio mixing and versioned local saves. Browser localStorage
requires an explicit export/import bridge if existing progress is to migrate.

EXECUTION ORDER AND PROOF
1. Commit the audited port contract, asset manifest and project foundation.
2. Deliver a complete short match using one tower and one enemy: build, wave,
   combat, leak/reward, defeat/victory, pause, restart and a minimal HUD.
3. Polish one Sanctuary Courtyard slice with an approved Gatling, animated
   Walker, Sanctum, ruin kit, rich perimeter flowers and reference lighting.
   Capture three matched in-engine shots and a playable clip. Improve the
   weakest visual categories before producing the full asset library.
4. Port remaining towers/branches, enemies/bosses, 50-wave behavior, abilities,
   progression, tutorial, settings and input. Complete production artwork.
5. Verify full gameplay, performance, saves and native distribution.

Use meaningful EditMode/PlayMode tests for maze validity, air/ground targeting,
branch effects, armor, currency, leaks, boss phases, waves, pause/speed and
persistence. JS string-inspection checks do not validate Unity execution.

Name the actual minimum test hardware before reporting performance. Proposed
gate: 1080p/60 FPS, p95 frame time <=16.7ms in a release player over a 60-second
post-warmup stress run with 100 towers and 200 enemies or shipping peak,
whichever is greater. Measure 4x speed and live placement separately. Record
CPU/GPU time, allocation behavior, memory, draw calls and overdraw. Treat
these as targets until measured. A clean project build and real gameplay
evidence are required; label checks that could not run due to missing Editor,
build modules, hardware or external assets.

Deliver runnable scenes and builds, configured prefabs, reproducible project
settings/dependencies, import presets, asset provenance, screenshots/video,
and concise verification results. The game must play offline without asset
service credentials. Work through authorized steps autonomously, and keep
the user informed of material findings and unresolved dependencies.
```

## Meshy asset briefs

Prefer Image-to-3D with the named reference. The text below is an asset brief or Text-to-3D fallback; field names and available controls depend on Meshy's chosen workflow. Desired moving-part separation and topology still require inspection and Blender work.

### Petal Gatling — reference `assets/3d_turret_pbr.jpg`

```text
One complete solarpunk mechanical Gatling defense tower, three-quarter view,
isolated and fully visible. Weathered warm marble Corinthian pedestal with
deep carved acanthus leaves and a stable square base. An intricate antique
brass gun carriage supports a six-barrel dark-steel rotary assembly. Visible
gear teeth, substantial axle supports, overlapping engraved brass plates,
mechanical linkages and a single faceted cyan energy crystal. Light ivy and
small pink peonies accent the base without concealing the weapon silhouette.
Believable engineered proportions, strong medium-distance readability,
subtle wear and restrained patina, consistent PBR materials, neutral lighting.
No background architecture, projectiles, muzzle flash, smoke, lettering or
cast shadows painted into textures. Preserve clear boundaries between the
stationary pedestal, rotating mount and barrel group for later separation.
```

### Diesel Walker — reference `assets/3d_walker_pbr.jpg`

```text
One complete bipedal dieselpunk automaton, isolated, full body, neutral stance
with arms slightly separated from torso for rigging. Broad rounded boiler
torso made from layered dark cast-iron armor plates with brass edging,
regular rivets and twin small amber optics. Visible hydraulic pistons,
functional knee and elbow joints, reinforced feet and paired exhaust stacks.
An imposing industrial machine with believable mass and mechanical anatomy,
readable at strategy-game camera distance. Worn brass, pitted iron, restrained
soot near exhaust outlets, coherent physical materials and neutral lighting.
No environment, pedestal, text, baked smoke, floating effects or weapon fire.
Keep gaps around moving joints and avoid fusing limbs into the torso.
```

### Ruin kit module — reference crop from `assets/battlefield_map.jpg`

```text
One freestanding classical Corinthian column on a square plinth, complete
and isolated. Warm ivory limestone with fluted shaft, deeply carved acanthus
capital, layered circular base and small asymmetric weathered chips. Strong
architectural silhouette with plausible load-bearing proportions. Subtle
stone veins and roughness variation, neutral lighting, consistent scale.
No adjoining building, terrain, backdrop, text or dense foliage. Clean top
and base boundaries suitable for assembling a modular temple colonnade.
```

Create separate briefs for arch, pediment, broken shaft, wall, stair, rubble, and paving. Repeated modules need authored dimensions and snapping; independent generation will not guarantee matching measurements.

### Sanctum assembly — reference `assets/sanctum_core.jpg`

```text
A classical sanctuary rotunda assembled from fluted Corinthian columns,
carved warm stone entablature and circular stepped foundation. Open interior
with an antique brass armillary mechanism surrounding a floating faceted
cyan crystal. Rich sculptural detail and restrained carved floral ornaments.
Match the reference architecture and proportions. Isolate the assembly with
neutral light and full silhouette visible; omit landscape, sky, fog, beams,
lettering and baked illumination. Clearly distinguish stone structure,
metal rings and crystal as components for later separation and animation.
```

For final production, build this from the accepted column/trim kit and separately authored rings/crystal. Use whole-assembly generation primarily to explore proportions, since merged parts can make animation and material assignment costly.

## Neutral reference-view brief

Use this when preparing object views for image-based generation:

```text
Create a consistent reference sheet for [ASSET], preserving the supplied
concept's exact design, proportions, material regions and ornament placement.
Show front, side, back and three-quarter views of the same object at the same
scale. Neutral background, diffuse studio lighting, complete uncropped
silhouette, no perspective exaggeration, atmosphere, captions or effects.
Show component boundaries clearly. Do not invent different designs per view.
```

Check agreement between views manually and export each view separately if the selected workflow accepts multiple images. A collage is not a guaranteed multi-view input, and invented rear geometry must be reviewed.

## First execution task

```text
Execute Stages 0-3 of UNITY_VISUAL_MIGRATION_PLAN.md: create a runnable Unity
project and a playable Sanctuary Courtyard slice with one tower, one enemy,
Sanctum, polished environment and reference lighting. Begin by extracting the
actual game contract and checking local Unity/tool availability. Prove a
short complete match and provide in-engine visual comparisons. Record missing
external assets and continue all independent work with labeled placeholders.
```
