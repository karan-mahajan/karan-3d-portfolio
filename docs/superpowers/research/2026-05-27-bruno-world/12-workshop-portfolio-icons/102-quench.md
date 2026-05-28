# 102_quench.py — projects-zone quench-water tank (smallest forge prop)

**Path:** `folio-2025/scripts/blender_world_steps/steps/102_quench.py`
**Lines:** 37
**Adds:** 2 objects (1 MESH, 1 EMPTY) to collection `quench`
**Group:** [12-workshop-portfolio-icons](../12-workshop-portfolio-icons.md)

## What it does (code-level)

Creates `quench` collection. Adds 2 objects — the visible quench-water mesh + a collider:

| Object | Type | Mesh | Location | Notes |
|---|---|---|---|---|
| `quenchPhysicalDynamic.001` | MESH | `Plane.060` | (40.04, -7.57, 1.152) | The quench water plane at the **actual projects-zone position** (not staging). No rotation. scale=1.0 |
| `cuboid.056` | EMPTY/CUBE | — | (40.04, -7.56, 0.730) | Quench collider, rotZ=-1.571 (-90°), scale (0.658, 0.674, 1.42) — directly below the water plane |

## Key data

- **Datablocks referenced:** mesh `Plane.060` (the water surface plane)
- **Materials assigned:** `palette` (likely with a water-shader; the group .md says `palette`)
- **Modifiers added:** none
- **Custom properties:** none
- **World positions of key anchors:**
  - Water plane at (40.04, -7.57, 1.152) — projects zone, top of quench tank
  - Collider at (40.04, -7.56, 0.730) — same XY, z=0.730 (tank body below water level)
- **Object types breakdown:** 1 MESH, 1 EMPTY
- **Parent collection:** `quench` (re-parented under `projects/` by finalize)

## Technique / recipe

**Minimal forge-tool — just a water surface + collider:**

1. **One flat plane mesh** (`Plane.060`) representing the quench water surface. Sits at z=1.152 (tank-top height).
2. **One CUBE collider** directly below at z=0.730 — represents the tank's body (0.658 × 0.674 × 1.42 m volume).
3. **Both at the actual projects-zone position** (40.04, -7.57) — NOT at staging. The collider is co-located with the mesh.

**Smallest forge-tool script in batch 4** — 37 lines, 2 objects. Bruno's minimum-viable prop for a quench tank.

**`quenchPhysicalDynamic.001`** — `.001` suffix suggests there was a `quenchPhysicalDynamic` earlier (perhaps removed or renamed). The current one is the only quench in the world.

**`PhysicalDynamic` on a flat plane** — the water surface is physics-active. Why dynamic? Probably so the runtime can detect when items are dropped INTO the water (collision detection) for the "cool the hot iron" gameplay. Or for water ripple physics.

**No interactive prompt, no `refQuench` empty** — players don't directly interact with the quench tank. It might be implicit: drop the forged item from the anvil/oven into the quench → triggers the cooling.

**Co-located mesh + collider** (rare in batch 4) — Bruno didn't bother with staging for this prop because it's so simple. The collider lives right under the mesh.

## Connections

- **Reads from:** `005_meshes_*.py` (`Plane.060`)
- **Read by:** `999_finalize.py` (parents `quench/` under `projects/`)
- **Depends on:** `093_projects.py` (projects parent)
- **Depended on by:** runtime collision detection (item-in-water), water-shader system

## Notable code patterns

- **Smallest script in batch 4** — 37 lines, 2 objects.
- **`.001` suffix without an unsuffixed sibling** — Bruno's exporter incremented the suffix from a now-deleted predecessor.
- **Co-located mesh + collider** at actual world coordinates — no staging trick. Simpler props use this pattern.
- **`PhysicalDynamic` on a flat surface** — physics-active water plane for collision-with-items detection.
- **Plane.060 mesh data** — a flat plane, probably with the special water shader. The mesh has no thickness; the collider underneath defines the tank's body volume.
- **Z-stack:** water at z=1.152 (top), tank body collider at z=0.730 (middle). The tank extends from z=0 (ground) to z≈1.45 (slightly above water plane). Bruno's clean vertical layout.
- **Quench is the workflow-cleanup tool** — anvil hammers, oven heats, grinder refines, quench cools. The 4 forge tools form the project-making metaphor.
