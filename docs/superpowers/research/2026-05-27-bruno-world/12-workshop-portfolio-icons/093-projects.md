# 093_projects.py — projects-zone root with interactive point, 3 colliders, and circular bounding

**Path:** `folio-2025/scripts/blender_world_steps/steps/093_projects.py`
**Lines:** 149
**Adds:** 9 objects (1 MESH, 8 EMPTY) to collection `projects`
**Group:** [12-workshop-portfolio-icons](../12-workshop-portfolio-icons.md)

## What it does (code-level)

Creates `projects` collection — the **projects-zone root** with the interactive point, zone bounding, and floor structure. This collection is also the **parent** of all forge-tool collections (anvil, grinder, oven, quench, etc.).

| Object | Type | Notes |
|---|---|---|
| `refInteractivePoint` | EMPTY/PLAIN_AXES at (37.24, -14.26, 1.5), rotZ=0.286 (16°) | "Press E to enter projects zone" anchor at player chest height |
| `physicalFixed.001` | EMPTY/PLAIN_AXES at (36.70, -12.15, ≈0.0) | Floor physics anchor for the projects zone |
| `cuboid.060` | EMPTY/CUBE at (-2.11, 27.59, 0.522), rotZ=-1.396 (-80°), scale (1.10, 2.28, 1.0) | Floor/wall collider at staging |
| `cuboid.061` | EMPTY/CUBE at (-5.78, 27.62, 2.105), rotZ=-0.873 (-50°), scale (0.508, 4.65, 4.14) | Tall wall collider |
| `cuboid.062` | EMPTY/CUBE at (-1.63, 29.27, 1.744), rotZ=-1.047 (-60°), scale (0.508, 1.25, 3.52) | Tall narrow collider |
| `refZoneBounding.003` | EMPTY/CIRCLE at (35.76, -13.41, 3.27), rotX=-1.571, scale=7.22 | **Circular zone boundary** (7.22m radius) — smaller than achievement zone's 10m |
| `Cube.065` | MESH (`Cube.049`) at (33.33, -9.69, 0.10), rotZ=0.698 (40°), scale=1.0 | The visible zone-floor mesh / decorative slab |
| `projects` | EMPTY/PLAIN_AXES at (35.76, -13.41, 3.27) | **Zone root parent empty** — finalize parents all forge-tool collections to this |
| `refZoneFrustum.003` | EMPTY/CIRCLE at (34.80, -9.93, 3.37), rotX=-1.571, scale=6.25 | Camera frustum region |

## Key data

- **Datablocks referenced:** mesh `Cube.049` (Cube.065)
- **Materials assigned:** `palette` (per group .md)
- **Modifiers added:** none
- **Custom properties:** none on any object
- **World positions of key anchors:**
  - Zone center at (35.76, -13.41, 3.27) — projects-zone coordinates
  - Interactive point at (37.24, -14.26, 1.5)
  - Visible mesh at (33.33, -9.69, 0.10) — at ground level inside zone
  - 3 colliders at staging (-1 to -6, 27.5 to 29.3, ...)
- **Object types breakdown:** 1 MESH, 8 EMPTY
- **Parent collection:** `projects` (the COLLECTION) — at finalize, the EMPTY `projects` becomes parent of 9 child collections (anvil 094, grinder 098, oven 100, quench 102, distinctions 097, board 096, blackBoard.002 095, mainTable.001 099, pole 101)

## Technique / recipe

**Zone-root pattern — projects is a parent zone with child collections:**

1. **`projects` EMPTY** at the zone center is the **parent anchor**. At finalize, all forge tools (anvil, grinder, oven, quench) + UI props (board, blackBoard.002, mainTable.001, distinctions, pole) get parented under this empty. Moving `projects` translates the whole projects zone.
2. **`refZoneBounding.003`** (7.22m radius CIRCLE) + **`refZoneFrustum.003`** (6.25m radius CIRCLE) — sphere bounds for runtime player-in-zone tests and frustum culling.
3. **3 collider EMPTYs** (.060, .061, .062) form the projects-zone walkable bounds — likely walls or floor extensions.
4. **`refInteractivePoint`** at the zone entrance — "Press E to enter the workshop."
5. **One visible mesh** (`Cube.065` at 33.33, -9.69) — the zone's signature floor or decorative slab (the `projectsCarpet` material may be on this, or it's a separate detail mesh).
6. **`physicalFixed.001`** — anchors a static collider for the zone floor.

**Compared to `achievements` (045) — 9 objects vs 23.** Projects zone is the "parent" — most of its content lives in child collections. Achievements is self-contained.

**Single visible mesh** suggests the projects-zone floor is mostly inferred from the carpet (in 099_mainTable.001) + the surrounding forge tools' footprints. Bruno didn't model the whole projects floor here.

**`Cube.065` rotZ=0.698 (≈40°)** — matches the rotation of most projects-zone props (board, blackBoard.002, etc., all at ~40°). The whole projects zone is rotated as one unit.

## Connections

- **Reads from:** `005_meshes_*.py` (`Cube.049`)
- **Read by:** `999_finalize.py` (parents 9 child collections to the `projects` empty)
- **Depends on:** `044_areas.py` (parent zone)
- **Depended on by:** child collections (anvil, grinder, oven, quench, board, blackBoard.002, mainTable.001, distinctions, pole)

## Notable code patterns

- **Zone-root parent EMPTY** — the `projects` empty is THE anchor that contains 9 child collections. Bruno's zone-organization pattern.
- **`projects` empty has the same location as `refZoneBounding.003`** — (35.76, -13.41, 3.27). The bounding circle and the zone parent share a position; runtime tests "is the player within bounding-circle radius of the projects anchor?"
- **CIRCLE empties for bounds + frustum** — Bruno's standard zone-marking pattern (also seen in 045 achievements with `.011` suffix).
- **`.003` suffix on bounds/frustum** — the projects zone is index 3. Other zones use .001 (career), .002 (social), .003 (projects), .011 (achievements).
- **No materials in this script** — projects is mostly EMPTYs (anchors) with one decorative mesh. The visual content lives in child collections.
- **`physicalFixed.001`** (vs achievements' `physicalFixed.008` and social's `physicalFixed.002`) — global counter across zones.
- **Smallest "zone root" script in batch 4** (149 lines) — Bruno's zone roots are lean, mostly anchors.
