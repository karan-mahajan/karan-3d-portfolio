# 038_references.003.py — 20 cherry-trunk placement curves (VISIBLE)

**Path:** `folio-2025/scripts/blender_world_steps/steps/038_references.003.py`
**Lines:** 249
**Adds:** 20 objects (20× CURVE) to collection `references.003`
**Group:** [14-reference-hidden](../14-reference-hidden.md)

## What it does (code-level)
20 nearly-identical blocks creating CURVE objects `treeBody.016/017/022/.../025` (Blender auto-numbered gaps). Each:
- Wraps curve datablock `Plane.007` — the cherry trunk-extrusion curve.
- Hand-placed `ob.location = (x, y, ~0)`.
- `rotation_euler` z values are typically positive (`+0.11`, `+0.51`, `+1.16`, `+2.41`, `+3.04`, `+3.42`) — DIFFERENT from oak's negative range. Probably reflects authoring history (Bruno spun in the opposite direction this session).
- `scale = (1, 1, 1)`.

Examples:
- `treeBody.016` at `(34.12, -71.00)` z-rot=-2.99
- `treeBody.067` at `(-63.20, -83.23)` z-rot=+3.33 (far south-southwest)
- `treeBody.072` at `(60.51, -14.58)` z-rot=+3.29

## Key data
- **Datablocks referenced**: curve `Plane.007` (cherry trunk geometry).
- **Materials assigned**: none on curves; cherry trees get cherry-pink leaf material elsewhere.
- **Modifiers added**: none.
- **Custom properties**: none.
- **World positions**: 20 cherry trees, mostly in south/southeast and northwest quadrants (Bruno's geography for spring blossoms).
- **Object types breakdown**: 20 CURVE.
- **Parent collection**: `references.003` → under `cherryTrees`. VISIBLE.

## Technique / recipe
- **CURVE placements** (like oak) — different from birch (MESH).
- **Note**: `Plane.007` is the curve datablock here — but in [035_visual.002.md](035-visual.002.md) `Plane.007` is the BIRCH trunk MESH. So datablock NAMES collide between curves and meshes (different `bpy.data.X` types). Confusing but valid in Blender.
- Bruno authored 20 cherry trees vs 24 oak vs 26 birch — birch is the most numerous species. Cherry is rarest, likely visual punctuation rather than canopy.

## Connections
- **Reads from**: `007_curves.py` (`Plane.007` curve).
- **Read by**: `134_cherryTrees.001.py` (minimap version).
- **Depends on**: 007, 013, 037 (template registration).
- **Depended on by**: 134, runtime renderer.

## Notable code patterns
- Z-rotations all positive (cherry) vs all negative (oak) — Bruno's authoring sessions can be detected by rotation sign conventions.
- Smaller count than oak/birch — 20 trees, suggesting cherry is decorative/focal not fill.
