# 034_references.py — 26 birch-trunk placement meshes (VISIBLE)

**Path:** `folio-2025/scripts/blender_world_steps/steps/034_references.py`
**Lines:** 321
**Adds:** 26 objects (26× MESH) to collection `references`
**Group:** [14-reference-hidden](../14-reference-hidden.md)

## What it does (code-level)
26 nearly-identical blocks creating MESH objects `treeBody.002`, `.003`, `.004`, ..., `.070`. Each:
- Wraps mesh datablock `Plane.008` (the birch trunk MESH — Bruno baked the birch curve into a mesh for these placements).
- Hand-placed location with `z ≈ 0` (ground level, with tiny float-precision noise like `-7.45e-09`).
- `rotation_euler = (0, -0, z_rot)` with `z_rot` in range `-9.14` to `-0.67` rad — random-looking spin.
- `scale = (1, 1, 1)`.
- `display_type='TEXTURED'`.

26 trees scattered across the island. Examples:
- `treeBody.002` at `(28.73, -48.63)` rot z=-0.92
- `treeBody.034` at `(-76.83, -0.18)` rot z=-7.63 (far west)
- `treeBody.045` at `(24.36, 27.98)` rot z=-3.58

## Key data
- **Datablocks referenced**: mesh `Plane.008` (birch trunk MESH, shared by all 26 instances).
- **Materials assigned**: `palette` (via mesh data; palette's bark variant).
- **Modifiers added**: NONE.
- **Custom properties**: none.
- **World positions**: 26 trees scattered island-wide.
- **Object types breakdown**: 26 MESH (note: this is MESH not CURVE, unlike the oak [030_references.002](030-references.002.md) which used CURVE).
- **Parent collection**: `references` → under `birchTrees`. VISIBLE.

## Technique / recipe
- **Note the difference from oak (030)**: oak uses CURVE, birch uses MESH for the placements. Cherry (038) is also CURVE. So Bruno has different tree types using different placement representations — birch was baked to mesh, oak/cherry stayed as curves. Probably because birch's trunk needed mesh-specific authoring (bark detail) that curves couldn't represent.
- **26 hand-placed birch trees** — like oak (24) but slightly more numerous. Same scatter-pattern approach.

## Connections
- **Reads from**: `005_meshes_*` (`Plane.008`), `004_materials.py` (palette).
- **Read by**: `135_birchTrees.001.py` (minimap version uses same 26 placements).
- **Depends on**: 005, 004, 013, 033 (birch template registration).
- **Depended on by**: 135, runtime renderer.

## Notable code patterns
- **MESH placements instead of CURVE** — different from oak. The runtime renderer probably has TWO code paths (one for curve-trunk trees that get extruded at runtime, one for mesh-trunk trees that are direct geometry). Birch chose mesh.
- All 26 z-rotation values are unique floats — Bruno hand-tuned each tree's trunk orientation.
- Y-range -56.35 to +61.33 — birches span the whole island N-S. X-range -76.83 to +81.03 — also full E-W spread. Density: roughly 1 birch per 600 sq.m of island.
