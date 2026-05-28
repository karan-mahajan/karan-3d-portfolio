# 048_altar.py — ritual altar with physics collision shapes and zone anchors

**Path:** `folio-2025/scripts/blender_world_steps/steps/048_altar.py`
**Lines:** 230
**Adds:** 15 objects to collection `altar`
**Group:** [06-buildings-structures](../06-buildings-structures.md)

## What it does (code-level)

Creates collection `altar`. Adds 15 objects in three functional layers:

**Physics collision shapes** (7 MESH + 1 MESH = 8, all `hide_render=True`, `display_type='WIRE'`):
- `trimesh.001` — mesh `Cylinder.020`, at (27.62, 27.77, -0.18). Cylinder collision volume.
- `cuboid.072`–`cuboid.077` — all use mesh `Cube.039`. Cuboid shapes at varying positions around the altar (22–33, 22–33, 1.3–2.3). Each has distinct scale encoding half-extents: e.g. cuboid.074 scale=(2.12, 2.15, 5.01) = tall pillar.

**Zone anchor empties** (6 EMPTY):
- `physicalFixed.005` — at (75.35, 27.94, 0.94)
- `refAltar` — at (75.34, 27.95, 0.0)
- `refCounter` — at (79.98, 22.93, 1.64) — rotated 0.52 rad
- `refZoneBounding.006` — CIRCLE display, at (76.09, 24.83, 3.27), scale=12.35 (r=12.35m bounding circle)
- `altar` — root empty at (75.34, 27.95, 0.0)
- `refZoneFrustum.006` — CIRCLE display, scale=12.87 (frustum detection r=12.87m)

**Visible geometry** (2 MESH):
- `refSkullEyes5` — mesh `Plane.016`, at (75.50, 32.27, 0.99), Z-rotation 0.999 rad. Likely a small decorative skull face plane on the altar.
- `Cube.173` — mesh `Cube.083`, at (71.19, 24.86, -0.14), scale=0.662. A small structural cube, slightly below ground (z=-0.14).

## Key data

- **Datablocks referenced:** `Cylinder.020`, `Cube.039`, `Cube.083`, `Plane.016`
- **Materials assigned:** `emissiveOrangeRadialGradient` + `palette` (via mesh datablocks)
- **Modifiers added:** none
- **World positions — root:** altar at **(75.34, 27.95)**, refZoneBounding radius 12.35m
- **Object types breakdown:** 10 MESH (8 wire + 2 visible), 5 EMPTY (but print says 15 = 9+6... actually: 7 wire cuboids + 1 wire trimesh + 2 visible MESH = 10 MESH; 5 EMPTY types = 15 total ✓)
- **Parent collection:** `altar`

## Technique / recipe

Altar zone uses the full Bruno zone pattern: root empty + bounding CIRCLE + frustum CIRCLE + interactive point + physics anchor. The 8 wire mesh shapes (cuboid/trimesh) define the collision geometry for the altar structure — they outline the stepped platform shape. The `refZoneBounding` CIRCLE at r=12.35 defines the zone enter/exit radius for the runtime zone system.

The physics shapes (cuboid.072–077) are scaled to approximate the altar's multi-level stepped platform — each cuboid covers one structural face/wall. The `trimesh.001` (cylinder shape at z=-0.18, below floor) is probably a ground-level collision disk.

Note: the physics shapes are positioned around (22–33, 22–33) — different from the zone empties at (75–80, 22–33). This suggests the physics collision is authored in a separate "local" coordinate space that `999_finalize.py` offsets when parenting.

## Connections

- **Reads from:** `005_meshes_*.py` (all mesh datablocks), `004_materials.py`
- **Read by:** `999_finalize.py` (parents altar under its section; zones system reads refZoneBounding/Frustum)
- **Depends on:** `013_collections.py`
- **Depended on by:** runtime zone system, runtime physics

## Notable code patterns

CIRCLE-type empties (`empty_display_type='CIRCLE'`, rotated -90° on X, scaled to radius) are Bruno's canonical pattern for zone detection volumes. The frustum CIRCLE (r=12.87) is slightly larger than the bounding CIRCLE (r=12.35) — the runtime uses the smaller one to determine "in zone" and the larger to begin loading/transition. `physicalFixed` empties mark fixed-body anchor points for physics simulation.
