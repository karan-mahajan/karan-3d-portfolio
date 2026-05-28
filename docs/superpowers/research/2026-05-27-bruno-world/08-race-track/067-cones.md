# 067_cones.py — 7 traffic cones with 2-cuboid box colliders each

**Path:** `folio-2025/scripts/blender_world_steps/steps/067_cones.py`
**Lines:** 590
**Adds:** 21 objects (7 MESH, 14 EMPTY) to collection `cones`
**Group:** [08-race-track](../08-race-track.md)

## What it does (code-level)

Creates `cones` collection. Adds 7 repetitions of a triplet: **1 cone MESH + 2 cuboid collider EMPTY** = 21 objects total.

**Cone meshes** — all reuse `Cylinder.042`. All have `Smooth by Angle.003` GN modifier (Input_1=0.96 rad ≈55°) and `mass=1.0` custom prop. Z=0.530 (cone base on track). Each has its own location and slight Z-rotation:

| # | Location | rotZ (rad) |
|---|---|---|
| .020 | (-19.93, -31.54) | 0.128 |
| .019 | (-20.12, -34.55) | -0.092 |
| .018 | (-21.42, -37.51) | 1.048 |
| ... and 4 more arranged along that southern edge | | |

**Collider cuboid empties** — 14 CUBE empties arranged in 7 pairs. Every pair is at the SAME OFF-TRACK ANCHOR `(-54.35, 57.40)` (the same exotic off-stage location used for `barrels` tubes). Each pair has two shapes:

- **"shaft" cuboid** at z≈0.834, scale (0.35, 0.35, 1.03) — the narrow tall cone shaft
- **"base" cuboid** at z≈0.351, scale (0.88, 0.88, 0.097), rotated π around Z — the wide flat cone base

Same exact scales repeat across all 7 pairs.

## Key data

- **Datablocks referenced:** mesh `Cylinder.042` (instanced 7×), node-group `Smooth by Angle.003`
- **Materials assigned:** via mesh datablock — `palette` (warm orange-yellow likely vertex-colored on Cylinder.042)
- **Modifiers added:** 7× `Smooth by Angle.003` (NODES, Input_1≈0.96 rad)
- **Custom properties:** `mass=1.0` on every cone mesh
- **World positions of key anchors:**
  - Cones along southern arc of track at y ≈ -31 to -37
  - Collider stack at (-54.35, 57.40) — same off-stage point used by `barrels`
- **Object types breakdown:** 7 MESH, 14 EMPTY (2 per cone)
- **Parent collection:** `cones` (re-parented under `circuit/` by finalize)

## Technique / recipe

**Compound collider via 2 stacked boxes:** unlike the barrels (single cuboid collider per barrel), each cone gets a **two-piece collider** — a tall narrow box for the cone's shaft and a wide flat box for the cone's base. This approximates the cone's truncated-cone shape better than one box and prevents the car from "snagging" on the narrow tip.

The base box is rotated π so its local axes match Bruno's runtime convention (likely "down-facing").

**All collider pairs at the same anchor location** — same trick as barrels: collider primitives parked off-track at `(-54.35, 57.40)`, runtime binds them to cones by index.

**Slight Z-rotation per cone** — the cones aren't perfectly axis-aligned. Each has a hand-placed yaw to look natural ("kicked over by an earlier car?"). The collider boxes share the parent cone's rotation at runtime.

**`Cylinder.042` is the cone, `Cylinder.044` is the barrel** — Bruno chose adjacent mesh datablock indices. Look at index pattern: 042 = cones, 044 = barrels.

## Connections

- **Reads from:** `005_meshes_*.py` (`Cylinder.042`), `003_node_groups.py` (`Smooth by Angle.003`)
- **Read by:** `999_finalize.py` (parents `cones/` under `circuit/`)
- **Depends on:** `062_circuit.py`
- **Depended on by:** runtime physics — cone/collider binding

## Notable code patterns

- **Shared `refObjectsPhysicalDynamic` prefix** with `barrels` (065) — both use the runtime "ObjectsPhysicalDynamic" category. Index continues: barrels are `.000`-`.007`, cones are `.008` upward. Cone indices in this script start at `.020` and go down (.020, .019, .018, ...), suggesting a different sub-range allocated.
- **Two cuboids per cone instead of one** — first compound-collider pattern seen in the analysis. Compare to `barrels` (1 cuboid per barrel) and `obstacles` (1 cuboid per obstacle).
- **No `tube` empty used** — `cones` uses `cuboid.NNN` exclusively. The `tube` vs `cuboid` distinction probably reflects shape semantics (tube = tall cylinder-like collider, cuboid = generic box).
