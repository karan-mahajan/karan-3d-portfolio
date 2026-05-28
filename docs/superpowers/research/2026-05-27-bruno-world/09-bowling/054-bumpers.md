# 054_bumpers.py — bowling lane bumpers: 2 collider rails + 1 visible mesh + anchor

**Path:** `folio-2025/scripts/blender_world_steps/steps/054_bumpers.py`
**Lines:** 81
**Adds:** 5 objects (2 MESH, 3 EMPTY) to collection `bumpers`
**Group:** [09-bowling](../09-bowling.md)

## What it does (code-level)

Creates `bumpers` collection. Adds 5 objects:

| Object | Type | Mesh / Display | Location | Scale |
|---|---|---|---|---|
| `refBumpersInteractivePoint.001` | EMPTY/PLAIN_AXES | — | (16.26, -71.04, 1.5) | (1, 1, 1) |
| `cuboid.093` | EMPTY/CUBE | — | (-46.54, -33.71, -0.40) | (28.59, 0.34, 0.82) |
| `refBumpersPhysicalKinematicPositionBased` | MESH | `Plane.119` | (13.62, -64.35, -0.82) | (1, 1, 1) |
| `cuboid.094` | EMPTY/CUBE | — | (-46.54, -40.23, -0.40) | (28.59, 0.34, 0.82) |
| `Cube.183` | MESH | `Cube.186` | (14.06, -71.04, -0.38) | (1, 1, 1) |

The two `cuboid.093/094` empties are far off-stage at x≈-46.5, with HUGE x-scale (28.6m long, 0.34m wide, 0.82m tall) — perfect lane-bumper rail dimensions. They're 6.5m apart (y=-33.7 and y=-40.2) — matching a typical bowling lane width. At runtime, they get placed flanking the lane.

The visible `refBumpersPhysicalKinematicPositionBased` mesh at (13.62, -64.35) is in the bowling zone area. `Cube.183` (mesh `Cube.186`) at (14.06, -71.04) is also in the zone.

## Key data

- **Datablocks referenced:** meshes `Plane.119`, `Cube.186`
- **Materials assigned:** via mesh datablocks — `darkGray`, `emissivePurpleRadialGradient` (per group .md) — gives the bumpers an arcade-style glow
- **Modifiers added:** none
- **Custom properties:** none in this script
- **World positions of key anchors:**
  - Interactive point at (16.26, -71.04, 1.5) — "press E to toggle bumpers on/off?"
  - Bumper collider rails off-stage at (-46.54, -33.71/-40.23) — runtime-bound to lane
  - Visible bumper mesh at (13.62, -64.35) and Cube.183 at (14.06, -71.04) — in the bowling zone
- **Object types breakdown:** 2 MESH, 3 EMPTY
- **Parent collection:** `bumpers` (re-parented under `bowling/` by finalize)

## Technique / recipe

**KinematicPositionBased physics body** — the bumpers are kinematic (the runtime drives their position) but they're collision-active. Suggests Bruno toggles them ON/OFF for "beginner mode" by hiding/showing them or moving them in/out of the lane.

**Two huge collider rails (28.6m long)** parked at (-46.54, -33.71) and (-46.54, -40.23) — 6.5m apart, runtime relocates them along the lane. Width 0.34m is a thin rail; height 0.82m matches the gutter wall.

**Interactive point** (PLAIN_AXES, no display orientation) at the bowling-area edge — UI prompt anchor for the bumpers toggle.

**`Cube.183` mesh with `Cube.186` datablock** at the entry — likely the "BUMPERS ON/OFF" visible button/sign next to the interactive point.

## Connections

- **Reads from:** `005_meshes_*.py` (`Plane.119`, `Cube.186`)
- **Read by:** `999_finalize.py` (parents `bumpers/` under `bowling/`)
- **Depends on:** `052_bowling.py` (bowling zone exists)
- **Depended on by:** runtime bowling game logic

## Notable code patterns

- **`refBumpersInteractivePoint.001`** — `.001` suffix suggests there might be another interactive point elsewhere (e.g., a different toggle, or a paired entry/exit point).
- **PhysicalKinematicPositionBased object naming class** — same as the obstacles in `071_obstacles.py`. Bruno's runtime physics-body classes: `PhysicalDynamic` (movable by forces — pins, barrels, ball), `PhysicalKinematicPositionBased` (driven by code — bumpers, obstacles), `PhysicalFixed` (immovable — walls, roads).
- **Two collider rails sharing identical dimensions** (28.59, 0.34, 0.82) — Bruno's "duplicate authored once" approach for symmetric props.
