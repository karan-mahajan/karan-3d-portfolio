# 098_grinder.py — projects-zone grinding wheel with horizontal-axis rotation

**Path:** `folio-2025/scripts/blender_world_steps/steps/098_grinder.py`
**Lines:** 118
**Adds:** 5 objects (2 MESH, 3 EMPTY) to collection `grinder`
**Group:** [12-workshop-portfolio-icons](../12-workshop-portfolio-icons.md)

## What it does (code-level)

Creates `grinder` collection. Adds the grinding wheel + base + 3 anchors:

| Object | Type | Mesh | Location | Notes |
|---|---|---|---|---|
| `Cylinder.031` | MESH | `Cylinder.051` | (-22.05, 22.96, 0.961) | **The grinding wheel.** rotX=1.047 (60°), rotY=1.571 (90°) — wheel tilted to spin around a horizontal axis. `Smooth by Angle.002` (Input_1=0.524 rad ≈30°) |
| `Cube.073` | MESH | `Cube.170` | (-22.03, 22.96, 0.494) | The grinder base, rotZ=-1.047 (-60°). z=0.494 (table-top height) |
| `refGrinder` | EMPTY/PLAIN_AXES | — | (-22.05, 22.96, 0.961) | Co-located with the grinding wheel — runtime hook for the rotation |
| `grinderPhysicalDynamic` | EMPTY/PLAIN_AXES | — | (39.80, -9.20, 0.961) | Physics-dynamic anchor at actual projects-zone position. `empty_display_size=2.0` |
| `cuboid.055` | EMPTY/CUBE | — | (0.70, 28.07, 0.743) | Grinder collider at staging, rotZ=-1.047, scale (1.16, 1.68, 1.44) |

## Key data

- **Datablocks referenced:** `Cylinder.051` (wheel), `Cube.170` (base); node-group `Smooth by Angle.002`
- **Materials assigned:** `palette`
- **Modifiers added:** 1× `Smooth by Angle.002` (NODES, Input_1=0.524 rad ≈30°) on the grinding wheel only
- **Custom properties:** none
- **World positions of key anchors:**
  - Grinding wheel + base + refGrinder anchor at staging (-22.05, 22.96, 0.961 / 0.494)
  - grinderPhysicalDynamic at actual projects-zone position (39.80, -9.20, 0.961)
  - Collider at separate staging (0.70, 28.07, 0.743)
- **Object types breakdown:** 2 MESH, 3 EMPTY
- **Parent collection:** `grinder` (re-parented under `projects/` by finalize)

## Technique / recipe

**Grinding wheel with rotation-driven animation:**

1. **Grinding wheel** (`Cylinder.031` / `Cylinder.051`) with **dual-axis rotation** (rotX=1.047, rotY=1.571) — this orients the cylinder so it spins around the HORIZONTAL axis (the wheel's axis is along the X+Y plane, not vertical). Authentic grinder geometry.
2. **Grinder base** (`Cube.073` / `Cube.170`) at z=0.494 (table-top) — the support stand.
3. **`refGrinder` anchor** co-located with the wheel — runtime probably reads this anchor's rotation each frame and applies a spin animation around it (or animates the wheel's rotation property directly).
4. **PhysicalDynamic anchor** at the actual zone position — runtime spawns physics here.
5. **One CUBE collider** for the grinder body at staging.

**Horizontal-axis rotation pattern** — the grinding wheel is a cylinder oriented to spin around X (or roughly so). When the runtime increments the rotation around this axis, the wheel spins like a real grinder.

**`refGrinder` co-located with the wheel mesh** — same XY position (-22.05, 22.96, 0.961). The empty serves as the rotation anchor; runtime probably parents the wheel to this empty and animates the empty's rotation.

**Smooth-by-Angle 30°** on the wheel — sharpens the cylinder's edges. The wheel's tooth/grit silhouette stays crisp.

**No smoothing on the base** — Cube.170 base is unsmoothed; either pre-smoothed or intentionally faceted.

## Connections

- **Reads from:** `005_meshes_*.py` (`Cylinder.051`, `Cube.170`), `003_node_groups.py` (`Smooth by Angle.002`)
- **Read by:** `999_finalize.py` (parents `grinder/` under `projects/`)
- **Depends on:** `093_projects.py` (projects parent)
- **Depended on by:** runtime grinder spin-animation, particle/spark effects, physics

## Notable code patterns

- **Dual-axis rotation** (rotX=1.047 + rotY=1.571) — Bruno tilts the cylinder via Euler XYZ to orient it for horizontal spinning. This is intentional geometry orientation, not a small tweak.
- **`refGrinder` co-located with the wheel** — runtime anchor pattern: a named empty at the same position as the mesh becomes the spin anchor.
- **Smallest forge-tool script in batch 4** (118 lines, 5 objects) — Bruno's minimum-viable grinder.
- **`Cylinder.031` and `Cube.073` named with Blender defaults** — no renaming. The mesh names are `Cylinder.051` and `Cube.170` (likewise auto-named).
- **`grinderPhysicalDynamic` at actual zone position** while the visible wheel is at staging — runtime relocates the wheel to the physics-anchor position.
- **No `mass` prop** — runtime uses defaults.
- **3 EMPTYs : 2 MESH ratio** — high anchor density for a simple prop. Bruno's forge tools have multiple runtime hooks (visible, physics, spin animation).
