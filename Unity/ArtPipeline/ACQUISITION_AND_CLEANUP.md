# Art acquisition and cleanup record

This workflow treats Meshy and Poliigon as offline authoring sources. The shipped Unity project must use local, reviewed files and must not require either service account at runtime. No paid calls, downloads, generated assets, task IDs, or credentials are represented by the current manifest. Existing GLBs are prototypes; their presence is not evidence of provenance or acceptance.

## Before acquiring anything

1. Review the reference images listed in `asset-manifest.json` and isolate one complete object per reference crop. Keep the original project reference path in the manifest.
2. Confirm account access, current service terms, and the project's applicable license before starting work. This repository authorizes no purchases or credit consumption.
3. Set a private staging directory outside the repository, such as `~/aegis-art-staging/`. Store original exports, restricted source textures, invoices/license records, prompts, and task receipts there. Never stage Poliigon raw downloads or restricted derivatives under the public repository.
4. For every acquisition, record provider, account/license record identifier (never credentials), date, allowed use, redistribution limits, source asset name, and private raw path. Keep secrets out of the manifest and version control.

## Meshy pilot generation

Start with one pilot each: Petal Gatling, Diesel Walker, and a single Corinthian ruin module. Use Image-to-3D with the project's own object reference where available. The written briefs and neutral reference-view prompt live in `UNITY_VISUAL_MIGRATION_PROMPT.md` under “Meshy asset briefs.” Save the exact prompt as used, input image path, model/version, settings, task ID, and candidate selection notes in the private staging record. Do not upload Poliigon files or derivatives to Meshy.

Download candidates only after inspection. Keep an immutable raw export in private staging and create a separate Blender working copy. A reference image remains a reference; do not relabel it as a generated or approved 3D model. Do not generate a complete environment mesh as a substitute for a modular scene.

## Poliigon surface acquisition

Acquire a small coherent family from the manifest's search briefs: warm marble/limestone, worn paving, patinated brass/copper, dark iron, soil/moss, rock, and an outdoor HDRI. Save the asset identifier and license record, and capture the applicable license text/version in private records. Apply the material after geometry generation and cleanup.

The current project plan treats Poliigon source downloads and derived texture files as restricted raw material that must remain private. Before a file is copied into the repository, verify that the specific license permits that form of redistribution and collaboration. If uncertain, keep it private and use a project-authored replacement for public builds. The manifest records status and destinations; it does not replace the license record.

## Blender cleanup checklist

For each raw geometry export, record a separate cleanup copy and then:

- Check units, scale, orientation, origin, and intended pivot against the 2-unit logical grid.
- Remove internal faces and nonmanifold geometry; repair normals; reduce excessive density while preserving gameplay-distance silhouette.
- Separate moving Gatling pedestal/yaw mount/barrel group and walker torso/limbs/joints. Check walker deformations through the intended gait before acceptance.
- Unwrap UVs, bake high-frequency detail into maps, and use shared trim sheets/materials where that keeps the set coherent. Do not bake concept lighting or shadows into base color.
- Author simple collision proxies, LODs for repeated assets, and practical material-slot counts. Keep project budget targets provisional until measured in the target view.
- Normalize pivots and dimensions, then export a clean FBX or a GLB supported by the pinned Unity importer.

Texture channel convention for URP Lit:

| Suffix | Meaning | Unity import rule |
| --- | --- | --- |
| `_BaseColor` or `_Albedo` | Base color | sRGB color texture |
| `_Normal` | Tangent-space normal | Normal Map importer; inspect green-channel orientation |
| `_Metallic` | Metallic in red | Linear data |
| `_Roughness` | Roughness | Linear data; invert to smoothness during packing |
| `_Smoothness` | Already inverted roughness | Linear data; pack to metallic alpha for metallic workflow |
| `_AO` or `_Occlusion` | Ambient occlusion in green | Linear data |
| `_Height` or `_Data` | Height/other scalar data | Linear data; preserve source, use only in a deliberate shader/bake |
| `_EmissionMask` | Emission mask | Linear data; set emission color separately |

Do not connect a roughness texture directly to a smoothness slot. In the URP Lit metallic workflow, pack metallic into red, smoothness into alpha, and AO into green of an occlusion map according to the pinned shader's documented channel interpretation. Check this packing on a neutral material ball and verify normal orientation under a rotating light.

## Stage, import, and review

1. From the repository root, run `python3 Unity/ArtPipeline/validate_manifest.py`. It checks required manifest fields, selected enumerated values, safe repository-relative paths, and that every listed reference/prototype file exists. It is a standard-library project checker, not a full JSON Schema evaluator.
2. Keep raw source files in private staging. Copy only the reviewed, license-permitted runtime files into the matching `Unity/Assets/Aegis/Art/` subdirectory. Record their hashes and source relationship in the staging record.
3. Name texture maps with the suffixes above. Keep maps for one material under one stable material stem, for example `CourtyardLimestone_BaseColor.png`, `CourtyardLimestone_Normal.png`, and `CourtyardLimestone_Roughness.png`.
4. In Unity, run **Aegis > Art Pipeline > Apply Texture Import Presets**. This editor action is restricted to `Assets/Aegis/Art/Textures/`; it sets color/data/normal import modes and metadata labels. It does not copy, overwrite, generate, or change assets elsewhere.
5. Run **Aegis > Art Pipeline > Validate Art Textures** and fix errors/warnings before creating materials. Review generated material channel packing manually; importer validation does not approve visual quality or licenses.
6. Update the manifest from `not_acquired` / `prototype_only` through `staged_private`, `cleanup`, `review`, and `accepted` only as evidence is recorded. Acceptance requires source/license record, final path, dimensions/pivot, LOD triangle counts where applicable, texture sizes, collision/rig status, reviewer, and review date.
7. Compare the asset in the ArtReview lighting setup with bloom disabled and at ordinary gameplay zoom. Capture evidence and note silhouette, scale, tactical readability, material response, and performance concerns.

## Current pilot state

The repository has reference images for each pilot and prototype GLBs for Gatling, Walker, Sanctum, ruins, and flora. The actual creation prompts are available in `UNITY_VISUAL_MIGRATION_PROMPT.md`; the pilot production files, Meshy jobs, Poliigon downloads, verified licenses, cleanup records, and approvals remain outstanding. See `asset-manifest.json` for per-item source paths and status.
