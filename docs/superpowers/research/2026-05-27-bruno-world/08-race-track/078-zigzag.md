# 078_zigzag.py — slalom chicane: 4 tube + 4 cuboid collider empties + 1 block mesh

**Path:** `folio-2025/scripts/blender_world_steps/steps/078_zigzag.py`
**Lines:** 167
**Adds:** 10 objects (1 MESH, 9 EMPTY) to collection `zigzag`
**Group:** [08-race-track](../08-race-track.md)

## What it does (code-level)

Creates `zigzag` collection. Adds 10 objects representing a slalom chicane at the **far western edge** of the race track (all at x≈-114 to -122).

**4 `tube.0NN` CUBE empties** (small narrow upright posts):
| Empty | Location |
|---|---|
| `tube.023` | (-119.58, -14.04, 0.71) |
| `tube.024` | (-117.55, -6.86, 0.71) |
| `tube.025` | (-119.45, 0.17, 0.71) |
| `tube.026` | (-117.36, 7.25, 0.71) |

All share scale (1.0, 1.0, 1.394) — narrow upright box, 1.4m tall. They zigzag in X between x=-117 and x=-120 across a 21m Y span — classic slalom layout.

**4 `cuboid.13X` CUBE empties** (larger blocks):
| Empty | Location |
|---|---|
| `cuboid.132` | (-122.60, -14.46, 0.71) |
| `cuboid.133` | (-114.57, -7.29, 0.71) |
| `cuboid.136` | (-122.47, -0.26, 0.71) |
| `cuboid.137` | (-114.60, 6.82, 0.71) |

All share scale (6.03, 1.81, 1.39) — wide, low blocks at the END of each slalom segment. They alternate sides (4 paired with each tube, on opposite x sides).

**1 mesh + 1 anchor:**
- `bumpersPhysicalFixed.001` EMPTY/PLAIN_AXES at (-80.86, -40.96, 0.01) with `restitution=1.0` custom prop — runtime anchor for the slalom's bouncy bumpers
- `blocks` MESH with `Cube.207` datablock at (-77.55, -31.06, -0.32) scaled (0.87, 0.92, 0.92) — the visible slalom geometry?

## Key data

- **Datablocks referenced:** mesh `Cube.207`
- **Materials assigned:** via mesh datablock — `palette`
- **Modifiers added:** none
- **Custom properties:** `restitution=1.0` on `bumpersPhysicalFixed.001` — perfectly bouncy
- **World positions of key anchors:**
  - Slalom posts at x≈-117 to -122, y=-14 to +7 (a 21m chicane in the far west of the track)
  - Block mesh at (-77.55, -31.06, -0.32) — quite far from the slalom
  - Bumpers anchor at (-80.86, -40.96, 0.01)
- **Object types breakdown:** 1 MESH, 9 EMPTY
- **Parent collection:** `zigzag` (re-parented under `circuit/` by finalize)

## Technique / recipe

**Slalom by alternating colliders:** 4 narrow upright "tube" posts at x≈-118 (alternating between -117 and -120) paired with 4 large flat "cuboid" blocks at opposite x≈-118 sides (alternating between -114 and -122). The car must thread between them in a zigzag pattern.

**Restitution=1.0 on the anchor** — the slalom bumpers act as elastic bouncers. Hitting one transfers energy back to the car (a soft slam, not a stop).

**Tubes vs cuboids size split:** tubes are tall thin posts (1×1×1.4 m), cuboids are large flat blocks (12×3.6×2.8m using full extent including empty_display_size). Together they form an asymmetric slalom — narrow posts on one side, wide walls on the other.

**`blocks` mesh far from the rest** — at (-77, -31), this mesh is ~40m away from the chicane. Either it's part of the slalom that's not at the same location, or the mesh's authored origin is offset and it visually renders near the slalom. Probably the latter: scale 0.87×0.92×0.92 implies the mesh data is sized to fit, with the visible geometry centered around the colliders.

## Connections

- **Reads from:** `005_meshes_*.py` (`Cube.207`)
- **Read by:** `999_finalize.py` (parents `zigzag/` under `circuit/`)
- **Depends on:** `062_circuit.py`
- **Depended on by:** runtime physics

## Notable code patterns

- **Mixed `tube.NNN` (small upright) + `cuboid.NNN` (large flat) collider classes** — first script with both shape categories in the same prop group. The naming distinction probably maps to runtime classification: tubes → cylinder colliders, cuboids → box colliders.
- **All slalom colliders at z=0.71** — same Z elevation so the car bumps against them all at the same height.
- **No `Smooth by Angle` modifier** — the `Cube.207` block mesh handles its own normals.
- **Bumpers anchor `bumpersPhysicalFixed.001`** with `restitution` — Bruno's first encountered explicit restitution prop in the race-track scripts.
