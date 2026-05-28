# 127_archives.003.py — rigged Bruno (bruno.001) reference + mesh

**Path:** `folio-2025/scripts/blender_world_steps/steps/127_archives.003.py`
**Lines:** 191
**Adds:** 2 objects (1× ARMATURE, 1× MESH) to collection `archives.003`
**Group:** [14-reference-hidden](../14-reference-hidden.md)

## What it does (code-level)
1. Gets/creates collection `archives.003`, **links to scene root** (top-level collection).
2. Creates `bruno.001` (ARMATURE, references `metarig.001`) at `(-13.12, 55.72, 3.18)` scale 0.865.
3. Creates `brunoMesh.001` (MESH `Cube.193`) at `(-19.12, 0, 4.07)`. Defines **35+ vertex groups** with detailed bone names matching a humanoid metarig: `spine`, `spine.001..006`, `shoulder.L`, `shoulder.R`, `upper_arm.R`, `forearm.R`, `hand.R`, `hand.R.001..007`, `breast.L`, `breast.R`, `pelvis.L`, `pelvis.R`, `thigh.R`, `shin.R`, `foot.R`, `toe.R`, `heel.02.R`, and their L mirror counterparts. Per-bone inline weight arrays.
4. Attaches `ARMATURE` modifier on `brunoMesh.001` → `bpy.data.objects.get('bruno.001')`.
5. Attaches **NODES `Auto Smooth`** modifier on `brunoMesh.001` (different from `Smooth by Angle.003` — uses `Socket_2 = 0.524 rad`).

## Key data
- **Datablocks referenced**: armature `metarig.001` (Bruno's humanoid metarig from `008_armatures.py`), mesh `Cube.193`.
- **Materials assigned**: via mesh data.
- **Modifiers added**: ARMATURE (target `bruno.001`), NODES `Auto Smooth` (`Socket_2 = 0.524`).
- **Custom properties**: none.
- **World positions**:
  - Armature `bruno.001` at `(-13.12, 55.72, 3.18)` — in the northwest near social zone.
  - Mesh `brunoMesh.001` at `(-19.12, 0, 4.07)` — but this is the AUTHORING location; finalize parents it under the armature with `matrix_parent_inverse` that brings it visually to the armature's position.
- **Object types breakdown**: 1 ARMATURE, 1 MESH.
- **Parent collection**: `archives.003` (scene-root, EXCLUDED in finalize).

## Technique / recipe
- **The full humanoid Bruno rig**, with all named bones from Blender's metarig add-on (spine.001-006, fingers as hand.R.001-007, etc.). This is the SOURCE rigged character — others (boy, sudo, baguira in 106/128) derive from this.
- **Auto Smooth node group** (vs Smooth by Angle.003) — different geometry-nodes setup, possibly older API. `Socket_2` is its only key parameter. Used for character meshes.
- **`archives.003` parents the `sudo` collection** (per 128) — the `sudo` script lives inside this collection's hierarchy, using this script's rig as the parent skeleton.

## Connections
- **Reads from**: `008_armatures.py` (metarig.001), `005_meshes_*` (`Cube.193`), `003_node_groups.py` (`Auto Smooth`).
- **Read by**: `128_sudo.py` (uses this archives.003 collection as parent), `106_default.py` (the statue character uses similar rig pattern), `999_finalize.py`.
- **Depends on**: 008, 005, 003, 013.
- **Depended on by**: 128, 999.

## Notable code patterns
- **Bone names match Blender's Rigify metarig** (`spine.001-006`, `hand.R.001-007`, etc.) — Bruno used the Rigify metarig add-on as the base for character rigging. Standard pipeline.
- **`metarig.001`** specifically (not `metarig`) — there's a versioning: `metarig` for `bruno`, `metarig.001` for `bruno.001`. The runtime uses the data-block name to bind the right rig.
- The mesh location `(-19.12, 0, 4.07)` is FAR from the armature `(-13.12, 55.72)` — only makes sense once parenting+matrix_parent_inverse is applied. The runtime fixes this in finalize.
