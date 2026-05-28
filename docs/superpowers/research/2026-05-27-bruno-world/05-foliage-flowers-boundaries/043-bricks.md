# 043_bricks.py — 30 scattered brick-block props

**Path:** `folio-2025/scripts/blender_world_steps/steps/043_bricks.py`
**Lines:** 373
**Adds:** 30 objects to collection `bricks`
**Group:** [05-foliage-flowers-boundaries](../05-foliage-flowers-boundaries.md)

## What it does (code-level)

Creates collection `bricks` and links it to the scene root. Adds 30 MESH objects (`Cube.042` through `Cube.170`, non-contiguous). All use mesh `Cube.062` (a brick-shaped cuboid).

Per object:
- `ob.location = (x, y, z)` — z varies: 0.18, 0.25, 0.29, 0.37, 0.96, 1.12, 1.18, 1.70 = two and sometimes three height layers, suggesting stacked piles
- `ob.rotation_euler = (rx, ry, rz)` — most have x=y=0 with varying z; some have slight x/y tilts (`-0.025`, `-0.058`, `-0.149`, `-0.587` rad) = slightly tilted bricks, scattered look
- `ob.scale = (1.0, ~1.0, 1.0)` — mostly (1, 0.9999998, 1), occasional (1, 1, 1)
- `ob.display_type = 'TEXTURED'`

No modifiers. No material assignment in script.

## Key data

- **Datablocks referenced:** mesh `Cube.062` (elongated brick/slab)
- **Materials assigned:** `palette` (via mesh)
- **Modifiers added:** none
- **Object positions (key clusters):**
  - ~(35, -21.7) — 5 bricks, z=0.375 and 1.14, two-layer pile
  - ~(25, -51) — 3 bricks, z=0.375 and 1.12, two-layer
  - ~(66, 38) — 3 bricks, slight terrain tilt on x
  - ~(17, -5.7) — 3 bricks, z=0.375 and 1.14
  - ~(52, -40.6) — 3 bricks
  - ~(60, -46.5) — 6 bricks, complex pile with tilted pieces (x-tilt -0.15)
  - ~(-8.5, 27.8) — 3 bricks
  - ~(50, -50.2) — 2 bricks
- **Object types breakdown:** 30 MESH, 0 EMPTY
- **Parent collection:** `bricks` (scene root)

## Technique / recipe

Individual hardcoded `ob.location` calls — no procedural placement. The bricks appear to be scattered in small clusters of 2–6 at various positions, deliberately placed to read as fallen/loose brick piles. Each cluster uses 2–3 z-height layers to simulate stacking. A few bricks have non-zero x/y tilts for a "knocked over" look.

`Cube.062` is a single brick mesh scaled and positioned. The constant y-scale of 0.9999998 (effectively 1.0) is a floating-point artifact from Blender's UI snapping.

## Connections

- **Reads from:** `005_meshes_*.py` (loads `Cube.062`), `004_materials.py`
- **Read by:** `999_finalize.py`
- **Depends on:** `013_collections.py`
- **Depended on by:** nothing (static decorative props)

## Notable code patterns

The position cluster at (60, -46 to -47) has 6 bricks with complex multi-layer arrangement and slight x-tilt on some — most elaborate brick group in the script. Likely placed around a specific gameplay feature (the race track turning area at ~x=60, y=-46). The `Cube.062` mesh is a different datablock from `Cube.056` (used for fence colliders) — different aspect ratio.
