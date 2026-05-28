# 035_visual.002.py — 7 birch leaf-cluster mesh variants

**Path:** `folio-2025/scripts/blender_world_steps/steps/035_visual.002.py`
**Lines:** 93
**Adds:** 7 objects (7× MESH) to collection `visual.002`
**Group:** [14-reference-hidden](../14-reference-hidden.md)

## What it does (code-level)
Same structure as [031_visual.004.py](031-visual.004.md) but for the birch species:
1. `treeBody` (MESH `Plane.007`) at origin — birch trunk MESH (NOTE: `Plane.007`, but [034](034-references.md) uses `Plane.008` for the placement instances. So birch has TWO trunk meshes? Or .007 is the "canonical visual" and .008 is the bulk placement geometry).
2. 6 leaf-cluster meshes `treeLeaves.003/001/002/004/005/019` (all wrapping `Icosphere.001` — the birch icosphere, different from oak's `Icosphere.003`).
   - Per-instance XY offsets within ±1.3m, Z from 3.2 to 7.8m.
   - Scales 0.59 to 1.03.
   - `display_type='SOLID'`.

## Key data
- **Datablocks referenced**: mesh `Plane.007` (birch trunk visual MESH), mesh `Icosphere.001` (birch leaf-cluster, 6 instances share).
- **Materials assigned**: `palette` (via mesh data).
- **Modifiers added**: none.
- **Custom properties**: none.
- **World positions**: all at origin offsets.
- **Object types breakdown**: 7 MESH (1 trunk + 6 leaves).
- **Parent collection**: `visual.002` → under `birchTrees`. VISIBLE.

## Technique / recipe
Identical recipe to [031_visual.004.md](031-visual.004.md) — author one canonical tree at origin, instantiate via runtime/scatter. Per-species variation: oak uses `Icosphere.003`, birch uses `Icosphere.001`, cherry uses `Icosphere.005`. Distinct datablocks per species let Bruno tune leaf shape per tree type.

## Connections
- **Reads from**: `005_meshes_*` (`Plane.007`, `Icosphere.001`), `004_materials.py` (palette).
- **Read by**: `135_birchTrees.001.py`, runtime renderer.
- **Depends on**: 005, 004, 013.
- **Depended on by**: 135.

## Notable code patterns
- The trunk mesh name `Plane.007` here vs `Plane.008` in [034](034-references.md) — Bruno authored TWO birch trunk meshes (one for the visual template, one for placement instances). Probably `.007` has more detail (used for the template) and `.008` is simpler (used for the 26 placements).
- Similar 7-mesh layout to oak ([031](031-visual.004.md)) — birch tree canopy uses 6 leaf-spheres at varied scale/z to make a realistic crown.
