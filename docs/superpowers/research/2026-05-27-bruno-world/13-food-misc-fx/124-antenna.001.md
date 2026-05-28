# 124_antenna.001.py — futuristic antenna prop (EXCLUDED)

**Path:** `folio-2025/scripts/blender_world_steps/steps/124_antenna.001.py`
**Lines:** 205
**Adds:** 9 objects (5× MESH, 4× EMPTY) to collection `antenna.001`
**Group:** [13-food-misc-fx](../13-food-misc-fx.md)

## What it does (code-level)
Builds a small antenna prop. Hierarchy of anchors + 5 meshes:
- `antennaHead` (EMPTY PLAIN_AXES) at `(-0.67, 0.42, 1.96)` rot z=2.67 — head reference.
- `axle` (EMPTY PLAIN_AXES) at `(-0.65, 0.38, 1.95)` — rotation pivot.
- `Plane.010` (MESH `Plane.013`) at `(-0.65, 0.38, 1.95)` rot `(π/2, π/2, 0)` — antenna dish?
- `Sphere` (MESH `Sphere.001`) at same position rot `(π/2, π/2, 0)` — antenna ball; carries a **NODES `Smooth by Angle.003`** modifier (`Input_1 = 0.524 rad ≈ 30°`).
- `antenna` (EMPTY PLAIN_AXES) at origin — root anchor.
- `antennaHeadReference` (EMPTY PLAIN_AXES) at `(-0.69, 0.34, 1.95)` rot `(-3.9e-08, -0.698, -π/2)` — second head reference.
- `Cube.036` (MESH `Cube.041`) at `(-0.69, 0.49, 1.83)` scale 0.0296 — tiny detail cube, with a **MIRROR** modifier mirroring on Y axis (`use_axis = (False, True, False)`).
- `Cylinder.008` (MESH `Cylinder.001`) at origin — the antenna pole.
- `Cylinder.012` (MESH `Cylinder.005`) at origin — additional pole segment.

## Key data
- **Datablocks referenced**: meshes `Plane.013`, `Sphere.001`, `Cube.041`, `Cylinder.001`, `Cylinder.005`.
- **Materials assigned**: `palette`, `emissivePurpleRadialGradient` (per group index — applied via mesh data, probably on the Sphere or one cylinder).
- **Modifiers added**: NODES `Smooth by Angle.003` (on Sphere); MIRROR (on Cube.036, Y axis, merge=True, threshold=0.001).
- **Custom properties**: none.
- **World positions**: all near origin `(0, 0, 1.95)` plus small offsets — this is a self-contained small prop authored at origin, expected to be parented under another zone in finalize and translated.
- **Object types breakdown**: 5 MESH, 4 EMPTY.
- **Parent collection**: `archives.003`/sudo-related per group index — but the script just adds to `antenna.001`, view-layer EXCLUDED.

## Technique / recipe
- **Authored at origin, placed via parenting** — the antenna's components all sit at near-origin (offsets <1.0). 999_finalize parents the whole thing under another zone's empty (the `antennaHead` ref empty is the natural root) and the parent's transform moves it to its final world location.
- **MIRROR modifier on the cube detail** — Bruno modeled one half of a symmetric detail and used MIRROR to get both. Standard Blender modeling pattern, encoded as a runtime modifier rather than an applied bake.
- **Two head references** (`antennaHead` + `antennaHeadReference`) — the runtime probably reads BOTH; one is the static head pose, the other might be the animated/target pose for tweens.
- The mesh `Sphere.001` is the only one with Smooth-by-Angle — Bruno wants the sphere to look smooth while keeping the cylinder/plane visible facets.

## Connections
- **Reads from**: `005_meshes_*` (5 datablocks), `003_node_groups.py` (`Smooth by Angle.003`), `004_materials.py` (palette, emissivePurpleRadialGradient).
- **Read by**: `999_finalize.py` (parents under whatever owner empty; sets view-layer EXCLUDE).
- **Depends on**: foundation 001-013.
- **Depended on by**: 999_finalize.

## Notable code patterns
- **MIRROR modifier example** — only place in batch 5 using MIRROR. Settings: `use_axis=(False, True, False)`, `use_mirror_merge=True`, `merge_threshold=0.001`. Reusable pattern for symmetric detail props.
- Identity-like rotations on cylinders (`euler=(0,-0,0)`, location at origin) — these are placed by parenting, not by manual transform.
- Naming uses `.001` suffix on the collection but not all object names — Blender's auto-numbering during duplication.
