# 134_birchTrees.001.py — 26 placed birch tree instances (excluded from view layer)

**Path:** `folio-2025/scripts/blender_world_steps/steps/134_birchTrees.001.py`
**Lines:** 321
**Adds:** 26 objects to collection `birchTrees.001`
**Group:** [04-trees](../04-trees.md)

## What it does (code-level)

Creates collection `birchTrees.001`. Adds 26 MESH objects named `treeBody.044` through `treeBody.101` (non-contiguous numbering — some numbers skipped, shared namespace with oak/cherry). Each object uses the same mesh datablock: `bpy.data.meshes.get('Icosphere.004')`.

Per object:
- `ob.location = (x, y, 0.0)` — all trees placed at z≈0 (ground level)
- `ob.rotation_euler = (0.0, 0.0, z_angle)` — Z-only rotation for facing direction (varies widely, range roughly 0–7 rad = arbitrary yaw)
- `ob.scale = (1.0, 1.0, 1.0)` — uniform scale, no size variation
- `ob.display_type = 'TEXTURED'`

No modifiers, no material assignment in this script — material comes from the mesh datablock loaded in the foundation scripts.

## Key data

- **Datablocks referenced:** mesh `Icosphere.004` (from 005_meshes scripts)
- **Materials assigned:** `palette` (via mesh datablock, not set here)
- **Modifiers added:** none
- **Custom properties:** none
- **Object types breakdown:** 26 MESH, 0 EMPTY
- **Parent collection:** `birchTrees.001` (EXCLUDED from view layer in 999_finalize)
- **World position range:** x: 22–79, y: -67–27. Distributed across the northeast meadow and some south areas.

## Technique / recipe

Single-mesh instancing: all 26 trees share one mesh datablock `Icosphere.004`. The mesh is a low-poly icosphere with vertex-color baked canopy (white bark + yellow-green leaves encoded in vertex color attribute). The runtime `Foliage.js` renders the canopy as an SDF cloud on top of this mesh anchor — the solid icosphere is Blender's proxy, not what the player sees in-game.

Placement is hand-authored — 26 hardcoded `ob.location` calls with individually tuned positions. No procedural scattering, no geometry nodes. Z rotation varies arbitrarily to give each birch a unique facing direction.

## Connections

- **Reads from:** `005_meshes_*.py` (loads `Icosphere.004` mesh data), `004_materials.py` (palette material baked into mesh)
- **Read by:** `999_finalize.py` (parents under `birchTrees`, excludes collection from view layer)
- **Depends on:** `013_collections.py`, `032_birchTrees.py` (parent collection must exist)
- **Depended on by:** runtime `Foliage.js` reads tree positions from the collection

## Notable code patterns

The `Icosphere.004` mesh differs from the bush mesh (`Icosphere.002`) — different LOD/shape. All trees use scale=(1,1,1) with no variation, unlike bushes which have ±10% scale jitter. The z values hover at exactly 0.0 or ε (floating-point near-zero: `1.19e-07`) — trees are not terrain-sampled; they rely on the mesh having enough height to visually sit on the ground.
