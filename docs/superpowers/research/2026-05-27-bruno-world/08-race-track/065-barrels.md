# 065_barrels.py — 8 destructible barrels along the race track

**Path:** `folio-2025/scripts/blender_world_steps/steps/065_barrels.py`
**Lines:** 545
**Adds:** 16 objects (8 MESH, 8 EMPTY) to collection `barrels`
**Group:** [08-race-track](../08-race-track.md)

## What it does (code-level)

Creates `barrels` collection. Then 8× alternating `refObjectsPhysicalDynamic.NNN` MESH + `tube.0NN` EMPTY pairs.

**The 8 mesh barrels** — all reuse mesh datablock `Cylinder.044`. All at z=0.977 (resting on track). All carry `mass=1.0` custom prop. All carry GN modifier `Smooth by Angle.003` with `Input_1=0.96 rad (≈55°)`. Positions scatter across (x, y) of the track:

| Object | Location (x, y, z=0.977) |
|---|---|
| `refObjectsPhysicalDynamic.000` | (-5.16, 15.76) |
| `refObjectsPhysicalDynamic.001` | (-4.43, 23.77) |
| `refObjectsPhysicalDynamic.002` | (2.23, 23.82) |
| `refObjectsPhysicalDynamic.003` | (0.67, 30.71) |
| `refObjectsPhysicalDynamic.004` | (10.50, 30.48) |
| `refObjectsPhysicalDynamic.005` | (10.54, 33.24) |
| `refObjectsPhysicalDynamic.006` | (10.67, 40.09) |
| `refObjectsPhysicalDynamic.007` | (6.12, 32.16) |

**The 8 tube.0NN empties** — ALL placed at the SAME location: **(-53.60, 57.88, 0.65)**, with the SAME scale **(0.91, 0.91, 1.53)**, CUBE display type. They are stacked on top of each other off-track.

## Key data

- **Datablocks referenced:** mesh `Cylinder.044` (reused 8× for all barrels), node-group `Smooth by Angle.003`
- **Materials assigned:** via mesh datablock — `palette` on `Cylinder.044`
- **Modifiers added:** 8× `Smooth by Angle.003` (NODES, Input_1=0.9599 rad ≈ 55°, Socket_1=False) — one per barrel mesh
- **Custom properties:** `mass=1.0` on EVERY barrel mesh. Tubes have none
- **World positions of key anchors:**
  - All 8 barrels along the start of the race track between y≈15 and y≈40
  - All 8 collider tubes stacked at (-53.60, 57.88, 0.65) — off-track, near the time-machine area
- **Object types breakdown:** 8 MESH (barrels), 8 EMPTY (collider tubes)
- **Parent collection:** `barrels` (re-parented under `circuit/` by finalize)

## Technique / recipe

**The "1 mesh datablock, 8 instance objects" pattern** — every barrel re-uses `Cylinder.044`, so the same vertex data is rendered 8 times at different locations. Zero duplicated mesh data.

**The "off-track collider tube" pattern** — the 8 `tube.0NN` CUBE empties parked far from the track at (-53.60, 57.88) are clearly NOT placed at the barrel positions. They have identical scale (0.91, 0.91, 1.53) describing **the collider primitive for ONE barrel** (a CUBE-shaped collider 0.91m×0.91m wide × 1.53m tall, slightly larger than the barrel cylinder to be forgiving). At runtime, the engine reads each `tube.0NN`, parents it to the corresponding `refObjectsPhysicalDynamic.00N` barrel as its collider, and the bone-cluster of empties off-stage becomes irrelevant.

This is a remarkably memory-efficient setup: 1 mesh + 1 collider-shape × 8 transform-only instances = a destructible barrel field.

**Smooth-by-Angle 55° threshold** — standard Bruno default for "round-ish" props.

## Connections

- **Reads from:** `005_meshes_*.py` (`Cylinder.044`), `003_node_groups.py` (`Smooth by Angle.003`), `004_materials.py` (palette on Cylinder.044)
- **Read by:** `999_finalize.py` (parents `barrels/` under `circuit/`)
- **Depends on:** `062_circuit.py` (zone root exists)
- **Depended on by:** runtime physics — barrel/tube binding happens in `folio-2025/sources/`

## Notable code patterns

- **Refs prefix `refObjectsPhysicalDynamic.NNN`** — same prefix used in `067_cones.py` (cones share the prefix). "ObjectsPhysicalDynamic" is the runtime category for "Rapier-dynamic physics body, can be knocked"; `.000`-`.007` are barrels, `.008`-`.0NN` cones (continuing index sequence).
- **All 8 tubes at exactly the same transform** — no jitter, no offset; perfectly stacked. This makes them invisible to the eye in the .blend viewport but easy to find programmatically.
- **`mass = 1.0`** — the barrel feels heavy enough to roll but light enough to be hit by the car. Compared to `furniture` (mass 0.05–0.35) and `jukebox` (mass 5.0).
- **Two-tier ref system:** mesh datablock named one way (`Cylinder.044`), object named another (`refObjectsPhysicalDynamic.NNN`) — the runtime reads `obj.name`, not `obj.data.name`.
