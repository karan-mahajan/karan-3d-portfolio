# 007_curves.py — 13 curve + font datablocks (race-track lines, bowling silhouettes, text)

**Path:** `folio-2025/scripts/blender_world_steps/steps/007_curves.py`
**Lines:** 1503
**Adds:** 13 curve/font datablocks (no scene objects)
**Group:** [01-foundation](../01-foundation.md)

## What it does (code-level)

Builds 13 datablocks via `bpy.data.curves.new(name, type='CURVE'|'FONT')`. Two distinct types:

- **CURVE** (11 datablocks) — splines with POLY or BEZIER control points used for race-track boundaries, bowling-pin silhouettes, decorative lines.
- **FONT** (2 datablocks) — Blender Text objects with `cu.body = 'BRUNO SIMON'` / `'RESET'` and font sizing.

For every CURVE datablock the pattern is:

```python
cu = bpy.data.curves.new('<name>', type='CURVE')
cu.dimensions = '3D'
cu.resolution_u = N        # bevel/spline sample resolution
cu.resolution_v = 12
cu.bevel_depth = 0.0
cu.bevel_resolution = 4
cu.extrude = <float>       # !!! key parameter: how far to extrude the spline into a flat ribbon
cu.offset = 0.0
cu.use_fill_caps = False
cu.fill_mode = 'FULL'
# Then for each spline:
sp = cu.splines.new('POLY' | 'BEZIER')
sp.points.add(N) | sp.bezier_points.add(N)
# loop setting .co (and for BEZIER: handle_left/right + handle_left_type/right_type)
sp.order_u = 4             # NURBS-ish order, only meaningful for POLY/NURBS not Bezier
sp.use_cyclic_u = False    # open or closed loop
cu.name = '<name>'         # redundant terminal naming
```

For FONT:

```python
cu = bpy.data.curves.new('Text.NNN', type='FONT')
cu.dimensions = '2D'
cu.resolution_u = N
cu.bevel_depth = 0.0
cu.extrude = <float>       # gives the text 3D depth if > 0
cu.fill_mode = 'BOTH'      # fill both sides of the extruded letter
cu.body = 'BRUNO SIMON'    # the actual string
cu.size = <float>
cu.space_character = <float>
cu.space_word = 1.0
cu.space_line = 1.0
cu.align_x = 'LEFT'
cu.align_y = 'TOP_BASELINE'
```

## The 13 datablocks

| # | Name | Type | Splines | Key extrude | Use |
|---|---|---|---|---:|---|
| 1 | `bumpersRefrenceMesh.001` | CURVE | 2 POLY splines (34 + 102 points) | `extrude=0.39` | Race-track outer & inner bumper edges, extruded 0.39 m vertically into thin walls |
| 2 | `bumpersRefrenceMesh.002` | CURVE | (similar large POLY) | `extrude≈similar` | Second race-track bumper layer |
| 3 | `BézierCircle.001` | CURVE | 1 BEZIER (27 control pts), open | `extrude=5.0` | A meandering bezier curve — the **road / circuit spine**, extruded 5 m vertically to form a tall surface (probably a track edge) |
| 4 | `BézierCurve` | CURVE | (BEZIER, smaller) | `extrude=0.0` | A simple bezier line; usable as a generic spline (used by 025_road.001 or as a tree-scatter spline?) |
| 5 | `Plane.003` | CURVE | POLY | (small extrude) | Decorative path / boundary curve named like a plane |
| 6 | `Plane.004` | CURVE | POLY | | (similar role) |
| 7 | `Plane.005` | CURVE | POLY | | |
| 8 | `Plane.007` | CURVE | POLY | | |
| 9 | `Plane.010` | CURVE | POLY | | |
| 10 | `Plane.011` | CURVE | POLY | | |
| 11 | `refBowlingPin.001` | CURVE | POLY (23 points, 3D coords) | (small) | Bowling-pin **silhouette curve** — likely revolved or used by a screw modifier into the 3D pin shape |
| 12 | `Text.001` | FONT | n/a | extrude=0.0 | `cu.body = 'BRUNO SIMON'`, `size = 2.5`, `align = LEFT/TOP_BASELINE` — Bruno's name on a sign somewhere |
| 13 | `Text.005` | FONT | n/a | extrude=0.05 | `cu.body = 'RESET'`, `size = 0.75`, `space_character = 1.06` — a "RESET" button label (probably a bowling-reset or vehicle-reset prop) |

## Key data

- **Datablocks referenced**: none directly (curves are referenced by name from later scripts).
- **Materials assigned**: none here (materials are set on objects that point at these curves in 020+).
- **Modifiers added**: none (the curve's own `bevel_*` and `extrude` props ARE the implicit "modifier" for spline-to-mesh).
- **Custom properties**: none on the curve datablock.
- **World positions**:
  - `bumpersRefrenceMesh.001` control points are around `(-44, 71-112, 0)` to `(95, 105, 0)` — covers an area ~140 m wide. This is in **world space**; the race track lives in this region.
  - `BézierCircle.001` has bezier points across `(-51, -34, 0)` to `(85, 119, 0)` — covering a similar large region (the race-track circuit), and the bezier handles span ~6 m around each control point for smooth curvature.
- **Object types breakdown**: 0 (no scene objects yet).
- **Parent collection**: n/a.

## Technique / recipe

The "curve-as-pathing-primitive" pattern:

- **Curves are not visible by themselves** — they only render when (a) their `extrude > 0`, giving them a vertical "ribbon" of geometry, (b) their `bevel_depth > 0`, giving them a tube, (c) a converted mesh references them, or (d) a Geometry-Nodes modifier samples them (see [003-node-groups.md](003-node-groups.md), `Geometry Nodes.002`).
- **`extrude=0.39` for race bumpers** — turns each POLY spline into a flat wall 0.39 m tall along its path. The same trick is used for the `BézierCircle.001` at `extrude=5.0` (a 5 m tall vertical strip, probably a fence-style wall).
- **POLY vs BEZIER**: POLY (no handles) is used for race-track boundary outlines where the polygon-approx fidelity is fine; BEZIER for road / decorative curves where smooth curvature matters.
- **Z = 0.0099 baked-in**: every `bumpersRefrenceMesh` POLY point sits at exactly `Z = 0.0099` (just above terrain to avoid Z-fighting). Bruno's "0.01 lift" is the standard offset for path/sign props in his world.
- **`refBowlingPin.001`**: a single open POLY spline of 23 points with X/Y coords clustered tightly (range ~1 m) and Z spanning ~-1.6 to ~0 — this is the **profile silhouette** of a bowling pin. Probably revolved 360° around Z by a `bpy.ops.object.modifier_add(type='SCREW')` somewhere, or imported as the source for a converted mesh `Cylinder.NNN` in 005.
- **Font extrude small (`0.05`) for "RESET"** vs `0.0` for "BRUNO SIMON": the RESET label is 3D-extruded slightly so it has thickness when seen edge-on; Bruno's name is flat.
- **Two FONT datablocks total**: the rest of the world's "text" is actually 3D mesh letters (the Text.* meshes in 005). FONT curves are only used for these two specific labels.

## Connections

- **Reads from**: nothing.
- **Read by**:
  - `bumpersRefrenceMesh.*` → race-track bumper objects (in 08-race-track group, 065-078).
  - `BézierCircle.001` → the road / circuit centerline (used by `025_road.001` and/or rails-along-curve modifier from 003's `Geometry Nodes.002`).
  - `BézierCurve` + `Plane.003/.004/.005/.007/.010/.011` → various decorative spline meshes in 022/025/051.
  - `refBowlingPin.001` → bowling area scripts (054-060, 069, 070).
  - `Text.001` ('BRUNO SIMON') → a sign object in landing or behindTheScene.
  - `Text.005` ('RESET') → bowling area reset-button or vehicle-respawn prop.
- **Depends on**: 000_init wipe of `bpy.data.curves`.
- **Depended on by**: 020+ scripts referencing these curves by name.

## Notable code patterns

- **Per-point inline `.co` assignment**: `sp.points[N].co = (x, y, z, w)` for each point. The 4th value is `w` (the rational weight; defaults to 0.0 here — NURBS-style, not used for POLY rendering).
- **Bezier control-point trick**: each `bezier_points[N]` requires three values — `.co`, `.handle_left`, `.handle_right`, plus `handle_left_type` / `handle_right_type` (typically `'ALIGNED'` for smooth curvature). Bruno sets all three per point.
- **Spline.order_u = 4**: only meaningful for NURBS; on POLY splines it's effectively a no-op but still serialized.
- **`use_cyclic_u = False` everywhere**: no closed loops in this set. Even `BézierCircle.001` despite the name is an open curve — the "Circle" is just Blender's default name for the first bezier you create.
- **`bumpersRefrenceMesh` misspelling**: "Refrence" not "Reference" — typo preserved across the .blend, the mesh datablocks in 005, and the curves here. Searchable as a strong identifier.
- **Race-track-relevant world dimensions** revealed: bumpers span X from `-44` to `+95`, Y from `+64` to `+124` — the race track is roughly 140 × 60 m, located off-center (positive Y). This is the first concrete spatial scale we've seen for any section.
- **`cu.name = '<name>'` at end of block**: same redundant naming as metaballs / materials — almost certainly the export tool always writes a terminal `.name = ...` regardless of whether it's needed.
