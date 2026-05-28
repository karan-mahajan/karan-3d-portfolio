# 041_flowers.py — 108 flat-plane flower patches scattered world-wide

**Path:** `folio-2025/scripts/blender_world_steps/steps/041_flowers.py`
**Lines:** 1309
**Adds:** 108 objects to collection `flowers`
**Group:** [05-foliage-flowers-boundaries](../05-foliage-flowers-boundaries.md)

## What it does (code-level)

Creates collection `flowers` and links it to the scene root. Adds 108 MESH objects named `flowers` through `flowers.108` (non-contiguous). Every object uses mesh `Plane.010`.

Per object:
- `ob.location = (x, y, ~0.384)` — z is almost constant at **0.3839...** (≈0.384m above world origin). No terrain sampling — all flowers share the same hardcoded z.
- `ob.rotation_euler = (0.0, 0.0, 0.0)` — **zero rotation on all axes, for every instance**
- `ob.scale = (3.1426..., 3.1426..., 3.1426...)` — **constant π-ish scale for every instance**
- `ob.display_type = 'TEXTURED'`

No modifiers. No material assignment in script.

## Key data

- **Datablocks referenced:** mesh `Plane.010` (a flat quad/plane with flower texture data)
- **Materials assigned:** `palette` (via mesh — flower color encoded in vertex attribute)
- **Modifiers added:** none
- **World position range:** x: -85 to +88, y: -86 to +88. Entire island + some beyond borders
- **Object types breakdown:** 108 MESH, 0 EMPTY
- **Parent collection:** `flowers` (scene root level)

## Technique / recipe

`Plane.010` is a flat horizontal quad. At scale 3.14 it becomes a ~3.14m × 3.14m patch. The plane carries vertex-color data for a flower atlas (white dots, yellow centers, etc.). Since all 108 instances use the same mesh with the same rotation=(0,0,0), all flowers point straight up with the same orientation — they're flat ground decals, not 3D flowers.

The constant z=0.384m is interesting: this is the approximate terrain height at flat island meadow (not zero because the island floor is slightly above sea level). Bruno baked one fixed z value and used it for all 108 flowers, trusting that the terrain variation is small enough to not matter visually.

The π-scale (3.142...) appears to be the natural size that makes the flower patches read well at play distance — possibly a backward-derivation from the texture atlas pixel size.

## Connections

- **Reads from:** `005_meshes_*.py` (loads `Plane.010`), `004_materials.py`
- **Read by:** `999_finalize.py`
- **Depends on:** `013_collections.py`
- **Depended on by:** nothing (render-only geometry)

## Notable code patterns

All 108 instances share `scale=(π, π, π)` and `rotation=(0,0,0)` — unlike bushes which have scale/rotation variation. Flowers are maximally uniform. The constant z≈0.384 shows Bruno didn't terrain-sample flower positions; he trusted the flat-ish meadow to absorb the error. Some far-shore flowers (x=-85, y=-85.6) are clearly off the island, suggesting they were placed without terrain clipping.
