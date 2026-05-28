# 135_cherryTrees.001.py — 20 placed cherry tree instances (excluded from view layer)

**Path:** `folio-2025/scripts/blender_world_steps/steps/135_cherryTrees.001.py`
**Lines:** 249
**Adds:** 20 objects to collection `cherryTrees.001`
**Group:** [04-trees](../04-trees.md)

## What it does (code-level)

Creates collection `cherryTrees.001`. Adds 20 MESH objects named `treeBody.127` through `treeBody.146`. Each uses mesh `Plane.023` — a flat plane mesh, not an icosphere like birch. Per object: location (x, y, z≈0), Z-only rotation (arbitrary yaw), scale=(1,1,1). No modifiers.

## Key data

- **Datablocks referenced:** mesh `Plane.023` (from 005_meshes scripts)
- **Materials assigned:** `palette` (via mesh datablock — pink/blossom vertex color)
- **Modifiers added:** none
- **Object types breakdown:** 20 MESH, 0 EMPTY
- **Parent collection:** `cherryTrees.001` (EXCLUDED from view layer in 999_finalize)
- **World position range:** x: 15–82, y: -71–6. Concentrated in northeast and east meadow areas.

## Technique / recipe

Cherry trees use a **flat `Plane.023` mesh** rather than an icosphere. `Plane.023` is likely a large horizontal plane or a billboard plane that carries pink vertex-color blossom data — or it's a large flat blossom canopy shape. The runtime `Foliage.js` replaces this with an SDF cloud anyway; the plane is just the Blender anchor geometry with world position and yaw baked in.

This is the only tree species using a Plane mesh as the anchor. Birch uses `Icosphere.004`, oak uses `Plane.017`, cherry uses `Plane.023`. The plane meshes are likely "flat tree silhouettes" that give a rough canopy profile even in Blender viewport.

## Connections

- **Reads from:** `005_meshes_*.py` (loads `Plane.023`), `004_materials.py`
- **Read by:** `999_finalize.py` (parents under `cherryTrees`, excludes from view layer)
- **Depends on:** `036_cherryTrees.py`
- **Depended on by:** runtime `Foliage.js`

## Notable code patterns

Uses `Plane.023` not `Icosphere.XXX` — cherry trees differ from birch in base mesh type. All three species use the same scale=(1,1,1) / Z-only rotation / z≈0 placement pattern. The `cherryTrees.001` collection is excluded from the view layer so it doesn't appear in Blender renders.
