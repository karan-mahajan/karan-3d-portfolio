# 071_obstacles.py — 5 beveled cube obstacles with paired colliders

**Path:** `folio-2025/scripts/blender_world_steps/steps/071_obstacles.py`
**Lines:** 432
**Adds:** 11 objects (5 MESH, 6 EMPTY) to collection `obstacles`
**Group:** [08-race-track](../08-race-track.md)

## What it does (code-level)

Creates `obstacles` collection. Adds 5 beveled-cube obstacles (paired with colliders) + 1 extra empty.

**Obstacle meshes** — all reuse `Cube.201`. All at z=1.001. All x≈18-34, y=80.24 (a row along the northern straight). Each gets a BEVEL modifier (width=0.15, segments=2, angle_limit=30°, profile=0.5 superellipse) — gives the cubes rounded edges for stylized look.

| Object | Location |
|---|---|
| `refObstaclesPhysicalKinematicPositionBased.001` | (34.44, 80.24, 1.00) |
| `refObstaclesPhysicalKinematicPositionBased.002` | (26.44, 80.24, 1.00) |
| `refObstaclesPhysicalKinematicPositionBased.003` | (18.44, 80.24, 1.00) |
| `.004` and `.005` | (also along that y-line) |

(5 cubes spaced 8m apart along the row.)

**Collider empties** — 5 CUBE empties named `cuboid.148`-`cuboid.154`. All at OFF-STAGE anchor (-4.64, 117.51, 2.19). Sizes vary slightly:
- 4 colliders at scale (0.846, 1.700, 1.850) — match an obstacle's bounding box
- 1 collider at scale (0.846, 4.797, 1.850) — wider; for the larger combined obstacle?
- 1 collider at scale (0.846, 4.820, 1.850) — similar width

(Total: 6 collider/anchor empties.)

## Key data

- **Datablocks referenced:** mesh `Cube.201` (instanced 5×)
- **Materials assigned:** via mesh datablock — `palette`
- **Modifiers added:** 5× BEVEL (width=0.15, segments=2, limit_method='ANGLE', angle_limit=0.524 rad ≈30°, profile=0.5 superellipse, miter='SHARP', loop_slide=True, use_clamp_overlap=True). NO Smooth-by-Angle
- **Custom properties:** `restitution` mentioned in the group .md but I didn't see explicit `restitution` on these specific obstacles — may be on the cuboid empties or elsewhere
- **World positions of key anchors:**
  - 5 obstacles in a 32m row at y=80.24 (north straight of the track)
  - 6 colliders parked off-stage at (-4.64, 117.51) — outside the track frustum entirely
- **Object types breakdown:** 5 MESH, 6 EMPTY
- **Parent collection:** `obstacles` (re-parented under `circuit/` by finalize)

## Technique / recipe

**BEVEL modifier instead of Smooth-by-Angle** — unique for obstacles. The 0.15m bevel with 2 segments produces visible rounded edges on the cube (a stylized "soft block" look). Smooth-by-Angle would just blend normals; BEVEL actually adds new geometry. The choice suggests Bruno wanted the obstacles to read as "soft / forgiving" visually.

**`refObstaclesPhysicalKinematicPositionBased.NNN`** — long object-name prefix encodes the runtime physics body type: **kinematic position-based**. Kinematic ≠ dynamic; the obstacles don't fall but they do collide. "Position-based" means the runtime moves them by setting position (animated obstacles), not by applying forces. So these may sway/bob/move along a path at runtime.

**Linear arrangement** of 5 cubes at y=80.24 — a row of stationary (or path-following) obstacles the car must dodge.

**Same off-stage collider park pattern** as cones/barrels/jump — colliders are runtime-bound to their MESH partners.

## Connections

- **Reads from:** `005_meshes_*.py` (`Cube.201`)
- **Read by:** `999_finalize.py` (parents `obstacles/` under `circuit/`)
- **Depends on:** `062_circuit.py`
- **Depended on by:** runtime physics — kinematic-position-based animation

## Notable code patterns

- **BEVEL with `superellipse` profile, miter=SHARP, loop_slide=True, clamp_overlap=True** — Bruno's preferred bevel settings: rounded but not too organic, sharp miters at corners. This is the only zone-child script in the race track that uses BEVEL.
- **Object-name encodes runtime physics class** (`PhysicalKinematicPositionBased`) — this is the longest, most expressive object naming in the analysis so far. Bruno's runtime probably has a registry `if obj.name.startsWith('refObstaclesPhysicalKinematicPositionBased')` to wire up the right physics body type.
- **Cuboid sizes vary** (0.846 vs 4.797 vs 4.820 in the Y axis) — suggests some obstacles are "wider" (longer in Y) than others, even though they share the same `Cube.201` mesh. The runtime likely scales the visible mesh to match the collider's Y-scale (or different obstacle Y-scales were set on each instance and the collider matches).
