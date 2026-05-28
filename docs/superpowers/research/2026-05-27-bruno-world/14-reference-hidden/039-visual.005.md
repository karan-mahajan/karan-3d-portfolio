# 039_visual.005.py — 7 cherry leaf-cluster mesh variants

**Path:** `folio-2025/scripts/blender_world_steps/steps/039_visual.005.py`
**Lines:** 93
**Adds:** 7 objects (7× MESH) to collection `visual.005`
**Group:** [14-reference-hidden](../14-reference-hidden.md)

## What it does (code-level)
Same structure as [031_visual.004.md](031-visual.004.md) (oak) and [035_visual.002.md](035-visual.002.md) (birch):
1. `treeBody.015` (MESH `Plane.002`) at origin — cherry trunk MESH variant.
2. 6 leaf-cluster meshes `treeLeaves.013/014/015/016/017/018` all wrapping `Icosphere.005` (the cherry-specific icosphere) with per-instance:
   - XY offsets within ±3.5m (slightly wider than oak's ±2, suggesting cherry has a wider canopy).
   - Z from 1.96 to 5.00m (lower canopy than oak's 2.8-6.9).
   - Scales 0.53 to 1.05.

## Key data
- **Datablocks referenced**: mesh `Plane.002` (cherry trunk), mesh `Icosphere.005` (cherry leaf-cluster).
- **Materials assigned**: `palette` (via mesh data — cherry's pink-blossom shade variant).
- **Modifiers added**: none.
- **Custom properties**: none.
- **World positions**: at origin.
- **Object types breakdown**: 7 MESH.
- **Parent collection**: `visual.005` → under `cherryTrees`. VISIBLE.

## Technique / recipe
- Same per-species visual recipe: 1 trunk MESH + 6 leaf-spheres at varied XY/Z/scale.
- **Cherry canopy is wider/lower** (XY ±3.5 vs ±2 for oak, Z 1.96-5.0 vs 2.8-6.9). Visually distinct silhouette: lower, sprawling vs oak's tall narrow crown.
- The leafLeaves XY-position spread `(±3.5)` lets the cherry sphere overlap visually with the trunk base, making it look like a fluffy "bushy" cherry-blossom shape rather than a tall canopy.

## Connections
- **Reads from**: `005_meshes_*` (`Plane.002`, `Icosphere.005`), `004_materials.py` (palette).
- **Read by**: `134_cherryTrees.001.py`, runtime renderer.
- **Depends on**: 005, 004, 013.
- **Depended on by**: 134.

## Notable code patterns
- **Cherry icosphere `Icosphere.005`** vs oak `Icosphere.003` vs birch `Icosphere.001` — 3 distinct mesh datablocks (likely different subdivision levels or shape tweaks).
- Per-species visual identity comes from icosphere shape + leaf-cluster spatial distribution, NOT from materials. All 3 species share `palette` material; the species-specific look is geometric.
