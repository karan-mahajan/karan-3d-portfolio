# 047_building.py — the main building with animated waterfall feature

**Path:** `folio-2025/scripts/blender_world_steps/steps/047_building.py`
**Lines:** 192
**Adds:** 6 objects to collection `building`
**Group:** [06-buildings-structures](../06-buildings-structures.md)

## What it does (code-level)

Creates collection `building` (no scene-root link call — must be linked by `999_finalize.py`). Adds 6 MESH objects:

**Waterfall meshes** (3 objects with `Smooth by Angle.003` GN modifier):
- `refWaterfallStill` — mesh `Cube.026`, at (69.66, -8.41, 1.078). Gets NODES modifier `Smooth by Angle.003` with `Input_1=0.9599` (≈55° threshold), `Socket_1=False`
- `refWaterfallDrop` — mesh `Cube.208`, same location (69.66, -8.41, 1.078). Same modifier params.
- `refWaterfallParticles` — mesh `Cube.212`, at (69.66, -7.35, 0.366). Same modifier params.

**Structural meshes** (3 objects, no modifier):
- `Cube.089` — mesh `Cube.236`, at (69.66, -8.41, 1.0)
- `refPillar` — mesh `Cube.238`, at (69.66, -12.41, 0.0)
- `Cube.110` — mesh `Cube.243`, at (69.66, -12.41, 0.748)

Building center: **(69.66, -8.41)**. All 6 objects share the same X.

## Key data

- **Datablocks referenced:** meshes `Cube.026`, `Cube.208`, `Cube.212`, `Cube.236`, `Cube.238`, `Cube.243` (all from 005_meshes)
- **Materials assigned:** `palette` (structural), `waterfall` (on waterfall meshes — assigned via mesh datablock)
- **Modifiers added:** `Smooth by Angle.003` (NODES GN modifier, Input_1=0.96 rad) on the 3 waterfall meshes
- **Custom properties:** none
- **Object types breakdown:** 6 MESH, 0 EMPTY
- **Parent collection:** `building` (linked to scene via finalize)

## Technique / recipe

The building's waterfall is split into 3 distinct meshes: `refWaterfallStill` (the still water face — frame geometry), `refWaterfallDrop` (the falling water sheet — animated in TSL shader), `refWaterfallParticles` (splash basin at base). All three carry the `Smooth by Angle.003` modifier for correct normal smoothing on the waterfall mesh geometry.

The `waterfall` material (set on these meshes via the datablock, not in this script) is an animated TSL shader. The split into Still/Drop/Particles allows different shader behavior on each mesh part.

The structural pillar (`refPillar` at y=-12.41) is offset 4m behind the waterfall (y=-8.41), suggesting the building footprint runs from y≈-12.4 to y≈-7.4.

## Connections

- **Reads from:** `005_meshes_*.py` (all 6 mesh datablocks), `003_node_groups.py` (`Smooth by Angle.003`), `004_materials.py` (`waterfall`, `palette`)
- **Read by:** `999_finalize.py` (parents building under its section root)
- **Depends on:** node group `Smooth by Angle.003` must exist
- **Depended on by:** nothing Blender-side; runtime renders waterfall via TSL shader

## Notable code patterns

`m.use_pin_to_last = True` on the GN modifier — pins it as the last modifier in the stack. `m['Input_1'] = 0.9599...` (≈55°) is the smoothing angle threshold in radians. The `Smooth by Angle.003` node-group-as-modifier pattern appears throughout Bruno's world for auto-smoothing without applying normals permanently.
