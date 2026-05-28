# 101_pole.py — projects-zone signage pole

**Path:** `folio-2025/scripts/blender_world_steps/steps/101_pole.py`
**Lines:** 181
**Adds:** 13 objects (9× MESH, 4× EMPTY) to collection `pole`
**Group:** [13-food-misc-fx](../13-food-misc-fx.md)

## What it does (code-level)
Builds a small signage pole at the projects-workshop zone. Mix of stacked label meshes and word-anchor empties.

Object types and roles:
- `cube.021/026/033` (MESH × 3, using `Cube.079/088/106`) — 3 cube segments forming the pole's body, stacked vertically at z=3.51, 1.96, 2.76. Each at `(-23.4, +24.3)`, rotated z≈0.52 rad (~30°).
- `role`, `at`, `with`, `refAttributes` (EMPTY × 4, PLAIN_AXES) — word anchors at z=3.31, 2.57, 1.83 (top/mid/bottom) and one off-position attribute reference at `(37.85, -7.96)`.
- `text`, `text.001`, `text.002` (MESH × 3, using `Plane.037/039/041`, display='WIRE') — the actual text panels at z=3.18, 2.44, 1.69. Rotated x=π/2 so they face up (read horizontally from above).
- `refel`, `refel.001`, `refel.002` (MESH × 3, using `Plane.034/035/040`) — refel = the decorative "REFEL" mesh (Bruno's project label, branded with `projectsLabels`).

## Key data
- **Datablocks referenced**: meshes `Cube.079`, `Cube.088`, `Cube.106` (cube body), `Plane.037/039/041` (text), `Plane.034/035/040` (refel labels).
- **Materials assigned**: `palette`, `projectsLabels` (atlas-style branded material used on refel planes).
- **Modifiers added**: none.
- **Custom properties**: none.
- **World positions**:
  - Pole base around `(-23.44, +24.34)` — at the projects workshop on the east side.
  - 3-level stack at z=3.31, 2.57, 1.83 (`role`, `at`, `with` word anchors).
  - `refAttributes` at `(37.85, -7.96, 2.55)` — far from pole, likely a reference target for parenting/UI binding.
- **Object types breakdown**: 9 MESH, 4 EMPTY.
- **Parent collection**: `projects` (via 999_finalize).

## Technique / recipe
- **Stacked-cube body**: 3 identical-position cube meshes at different z, scale 0.54 each — creates a segmented pole.
- **Per-word EMPTY anchors**: `role`, `at`, `with` are word semantics — the runtime probably reads these to place dynamic text or UI overlays. Naming the EMPTY by its semantic word is Bruno's pattern for "named anchor."
- **Wire-display text meshes** (`display_type = 'WIRE'`) — meant to be invisible at render but visible in Blender viewport as a layout aid. The runtime probably uses the underlying mesh data for label geometry but suppresses any solid rendering.
- **Branded labels** via `projectsLabels` material on the refel planes — this is Bruno's atlas-texture material for project icons/text.

## Connections
- **Reads from**: `005_meshes_*` (9 mesh datablocks), `004_materials.py` (`palette`, `projectsLabels`).
- **Read by**: `999_finalize.py` (parents word anchors + meshes under projects/pole hierarchy).
- **Depends on**: foundation 001-013.
- **Depended on by**: 999_finalize.

## Notable code patterns
- 25-degree z-rotation on the pole body (~0.52 rad) — matches the title's 25° rotation. Bruno uses 25/30° tilts consistently across landing/projects content for visual rhythm.
- Cubes use scale 0.541 — a recurring magic scale shared with other small-prop scripts.
- The `refAttributes` empty is placed FAR from the pole (37.85, -7.96 vs pole at -23.44, +24.34) — confirms it's a runtime reference target (probably points the pole at a focus location, or is parented to the pole as a leaf for UI binding).
