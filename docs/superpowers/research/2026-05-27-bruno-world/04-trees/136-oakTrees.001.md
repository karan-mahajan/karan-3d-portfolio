# 136_oakTrees.001.py — 24 placed oak tree instances (excluded from view layer)

**Path:** `folio-2025/scripts/blender_world_steps/steps/136_oakTrees.001.py`
**Lines:** 297
**Adds:** 24 objects to collection `oakTrees.001`
**Group:** [04-trees](../04-trees.md)

## What it does (code-level)

Creates collection `oakTrees.001`. Adds 24 MESH objects named `treeBody.103` through `treeBody.126`. Each uses mesh `Plane.017`. Per object: location (x, y, z≈0), Z-only rotation (arbitrary yaw, range 0–7+ rad), scale=(1,1,1). No modifiers.

## Key data

- **Datablocks referenced:** mesh `Plane.017` (from 005_meshes scripts)
- **Materials assigned:** `palette` (via mesh — warm autumn orange/yellow vertex color)
- **Modifiers added:** none
- **Object types breakdown:** 24 MESH, 0 EMPTY
- **Parent collection:** `oakTrees.001` (EXCLUDED from view layer in 999_finalize)
- **World position range:** x: 20–82, y: -80–27. Broadly distributed, densest in northeast quad.

## Technique / recipe

Oak trees use `Plane.017` — a flat plane mesh, same approach as cherry (`Plane.023`). Oak is the most numerous species (24) and the broadest in area coverage, which matches their role as the primary meadow landmark layer.

All three species (birch `Icosphere.004`, oak `Plane.017`, cherry `Plane.023`) use the same technique: one shared mesh datablock per species, 12–26 hand-placed instances, z≈0, Z-only yaw rotation. The mesh carries the canopy shape and vertex color; runtime SDF cloud from `Foliage.js` handles the actual visual.

## Connections

- **Reads from:** `005_meshes_*.py` (loads `Plane.017`), `004_materials.py`
- **Read by:** `999_finalize.py` (parents under `oakTrees`, excludes from view layer)
- **Depends on:** `028_oakTrees.py`
- **Depended on by:** runtime `Foliage.js`

## Notable code patterns

Z rotation values like `-6.727`, `-7.593` — these are > 2π, meaning Blender accumulated multiple full rotations in the authoring session. Functionally equivalent to their modulo-2π values but indicate the trees were rotated interactively in the viewport. This is a Blender authoring artifact, not meaningful geometry data.
