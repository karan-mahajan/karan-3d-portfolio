# 031_visual.004.py — 7 oak leaf-cluster mesh variants

**Path:** `folio-2025/scripts/blender_world_steps/steps/031_visual.004.py`
**Lines:** 93
**Adds:** 7 objects (7× MESH) to collection `visual.004`
**Group:** [14-reference-hidden](../14-reference-hidden.md)

## What it does (code-level)
7 objects:
1. `treeBody.012` (MESH `Plane.005`) at origin — the **trunk MESH** version of the oak (yes, same name as the curve datablock from script 030, but here as MESH data — Bruno baked the curve into a mesh too).
   - `display_type='TEXTURED'`.
2. `treeLeaves.006/007/008/009/010/011` (MESH × 6, all wrapping `Icosphere.003`) — six leaf-cluster spheres placed around the trunk's canopy zone.
   - Each at a slightly different XY offset (within ±1m) and Z (2.8 to 6.9m — canopy height range).
   - Per-instance scale 0.42 to 1.0 (so leaf clusters are varied sizes).
   - `display_type='SOLID'`.

## Key data
- **Datablocks referenced**: mesh `Plane.005` (oak trunk MESH), mesh `Icosphere.003` (the leaf-cluster icosphere — all 6 leaves share this single icosphere mesh).
- **Materials assigned**: `palette` (via mesh data; the foliage variant of palette gives the warm-green tint).
- **Modifiers added**: none.
- **Custom properties**: none.
- **World positions**: all at origin offsets (within (±2, ±2, 2.8-6.9)). Not placed in world — they're template instances.
- **Object types breakdown**: 7 MESH (1 trunk + 6 leaves).
- **Parent collection**: `visual.004` → parented under `oakTrees` in finalize. VISIBLE.

## Technique / recipe
- **"Author one oak tree at origin, instance it 24 times" pattern**: this script creates the canonical oak tree at origin (trunk + 6 leaf spheres). The runtime/game probably uses this as a TEMPLATE — for each of the 24 placement curves in `references.002`, it instantiates a copy of these 7 meshes at the curve's location/rotation.
- **6 leaf clusters of varied scale**: 0.42, 0.53, 0.85, 0.90, 1.00, 1.03 — creates organic-looking canopy with size variation. All 6 use the same icosphere data (so they share geometry, vary by transform only).
- **Display type difference**: trunk is TEXTURED (visible normally), leaves are SOLID (visible in solid-mode viewport, allows palette material to render the foliage tint). Different `display_type` per role.

## Connections
- **Reads from**: `005_meshes_*` (`Plane.005` mesh and `Icosphere.003`), `004_materials.py` (palette).
- **Read by**: `136_oakTrees.001.py` (minimap-version), runtime tree-instancing logic that places these at each scatter anchor.
- **Depends on**: 005, 004, 013.
- **Depended on by**: 136, runtime renderer.

## Notable code patterns
- **Mesh-name reuse**: `Plane.005` appears as both a CURVE datablock (in 029-030) and a MESH datablock — Blender allows this; they're different `bpy.data.X` types. Bruno keeps the name consistent so the curve→mesh relationship is traceable.
- All leaf XY positions are TINY (±2m): leaves cluster directly above the trunk. The z-spread (2.8 to 6.9m) gives the canopy vertical depth.
- 6 leaves per tree × 24 trees = 144 leaf instances in the visible world.
- 7-object pattern matches [035_visual.002.py](035-visual.002.md) (birch, 1 trunk + 6 leaves) and [039_visual.005.py](039-visual.005.md) (cherry, 1 trunk + 6 leaves). Three species, identical structure.
