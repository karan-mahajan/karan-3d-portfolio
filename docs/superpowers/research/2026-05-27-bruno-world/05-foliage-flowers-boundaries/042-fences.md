# 042_fences.py — 16 fence panels + 16 matching physics-collider cuboids

**Path:** `folio-2025/scripts/blender_world_steps/steps/042_fences.py`
**Lines:** 429
**Adds:** 32 objects to collection `fences`
**Group:** [05-foliage-flowers-boundaries](../05-foliage-flowers-boundaries.md)

## What it does (code-level)

Creates collection `fences` and links it to the scene root. Adds 32 MESH objects in alternating pairs:

**Visible fence panels** (`fencePhysicalDynamic.001`–`.018`, 16 instances):
- Mesh: `Cube.200` (elongated fence plank shape)
- `ob.display_type = 'TEXTURED'`
- `ob.location` varies per fence (various island positions)
- `ob.rotation_euler = (0.0, 0.0, z_angle)` — various Z rotations to match terrain path
- `ob.scale = (1.0, 1.0, 1.0)` — uniform, all same size

**Physics collider cuboids** (`cuboid.114`–`cuboid.200`, 16 instances):
- Mesh: `Cube.056` (generic cuboid collision shape)
- `ob.hide_render = True` — not visible in render
- `ob.display_type = 'WIRE'` — visible only as wireframe in viewport
- All share the **same hardcoded location** `(5.337, 4.819, 0.621)`, rotation `(0, 0, 0.750)`, scale `(2.135, 0.293, 1.250)` — they're a single template cuboid duplicated 16 times but positioned identically at world origin area, relying on runtime physics to clone the shape onto each fence.

## Key data

- **Datablocks referenced:** meshes `Cube.200` (fence), `Cube.056` (cuboid)
- **Materials assigned:** `palette` (via mesh datablocks)
- **Modifiers added:** none
- **Custom properties:** none (but objects named `fencePhysicalDynamic` → runtime reads `PhysicalDynamic` for physics type)
- **Object types breakdown:** 32 MESH (16 visible + 16 wire), 0 EMPTY
- **Parent collection:** `fences` (scene root level)
- **Fence positions:** clustered in two zones: (8–63, -76 to -14) = east/southeast meadow; (57–75, +7 to +13) = northeast near building

## Technique / recipe

Bruno pairs every visible fence with a hidden wire cuboid. The fence mesh carries the visual; the cuboid carries the collision. The naming convention `fencePhysicalDynamic` signals to the runtime physics system that this object should be a dynamic (movable) Rapier body — fences are knockable.

The 16 cuboid colliders all store the same world position — this appears to be a template-bake artifact where Bruno defined one collision shape and the runtime is responsible for reading the fence's actual position and applying the collision at that location.

## Connections

- **Reads from:** `005_meshes_*.py` (loads `Cube.200`, `Cube.056`)
- **Read by:** `999_finalize.py`
- **Depends on:** `013_collections.py`
- **Depended on by:** runtime physics system (reads `fencePhysicalDynamic` name prefix)

## Notable code patterns

Object name convention `fencePhysicalDynamic` encodes physics type directly in the name — Bruno's runtime parses object names to configure Rapier bodies. The wire cuboid collocated at the authoring template position (5.34, 4.82) is a signature of Bruno's pipeline: physics shapes are positioned by the runtime, not by the Blender bake.
