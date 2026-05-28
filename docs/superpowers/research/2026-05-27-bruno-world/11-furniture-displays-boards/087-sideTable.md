# 087_sideTable.py — lab's side table with candle, physics-dynamic anchor, and round-shape collider

**Path:** `folio-2025/scripts/blender_world_steps/steps/087_sideTable.py`
**Lines:** 102
**Adds:** 4 objects (2 MESH, 2 EMPTY) to collection `sideTable`
**Group:** [11-furniture-displays-boards](../11-furniture-displays-boards.md)

## What it does (code-level)

Creates `sideTable` collection. Adds 4 objects:

| Object | Type | Mesh | Location | Notes |
|---|---|---|---|---|
| `sideTablePhysicalDynamic` | EMPTY/PLAIN_AXES | — | (15.61, -15.46, 0.533) | Physics-dynamic anchor (at staging). rotZ=-0.611 (-35°) — table runtime-rotation |
| `cuboid.066` | EMPTY/CUBE | — | (-23.48, 21.80, 0.533) | Collider, rotZ=2.514 (≈144°), scale (1.16, 2.42, 0.98) — at staging. Same shape as `cuboid.063` in mainTable (085) |
| `Circle.006` | MESH | `Circle.008` | (-40.51, 16.49, 1.000) | **The visible round table mesh**. `Smooth by Angle.002` modifier (Input_1=1.396 rad ≈80° — very soft) |
| `refCandleFlame.002` | MESH | `Plane.067` | (-39.29, 17.84, 1.228) | Candle flame on the table, rotZ=0.785 (45°) |

## Key data

- **Datablocks referenced:** mesh `Circle.008` (round table), `Plane.067` (candle flame); node-group `Smooth by Angle.002`
- **Materials assigned:** `emissiveOrangeRadialGradient` (candle flame), `palette` (table)
- **Modifiers added:** 1× `Smooth by Angle.002` (NODES, Input_1=1.396 rad ≈80°) on the Circle table only
- **Custom properties:** none
- **World positions of key anchors:**
  - Table at (-40.51, 16.49, 1.000) — lab zone, 2.7m east of mainTable
  - Candle on table at (-39.29, 17.84, 1.228) — table-top + 0.23m
  - Physics anchor at staging (15.61, -15.46, 0.533)
  - Collider at staging (-23.48, 21.80, 0.533)
- **Object types breakdown:** 2 MESH, 2 EMPTY
- **Parent collection:** `sideTable` (re-parented under `lab/` by finalize)

## Technique / recipe

**A round side-table with a candle — the simpler companion to mainTable (085):**

1. **Round table mesh** from `Circle.008` (a circle/disc primitive) — gets a `Smooth by Angle.002` modifier with **80° threshold** (very soft). This aggressively smooths the circle's edge tessellation into a near-perfect round shape.
2. **Candle flame plane** placed on the table top (z=1.228, just above the table at z=1.000). Same `emissiveOrangeRadialGradient` material as the mainTable's flame.
3. **PhysicalDynamic anchor + collider** at staging positions (-23.48, 21.80) — same physical setup as mainTable (cuboid.063 in 085 has identical scale (1.16, 2.42, 0.98)). The collider is rotated to match the table's orientation.

**Notable: uses `Smooth by Angle.002` (not .003 as elsewhere)** — variant of the smoothing node. The 80° threshold (1.396 rad) is the widest seen in batch 4, ensuring the circle's polygon edges blend completely into a smooth ring.

**No second prop or balls** (vs mainTable which has 2 balls + candle) — this is the "side" table, deliberately less decorated. The candle is the only object on it.

**Mirror collider scale:** `cuboid.066` (this script) and `cuboid.063` (085) have identical scales (1.16, 2.42, 0.98) but different rotations. Bruno reused the table-top collider sizing across both tables — they have the same footprint despite one being round and one rectangular.

## Connections

- **Reads from:** `005_meshes_*.py` (`Circle.008`, `Plane.067`), `003_node_groups.py` (`Smooth by Angle.002`)
- **Read by:** `999_finalize.py` (parents `sideTable/` under `lab/`)
- **Depends on:** `081_lab.py` (parent zone)
- **Depended on by:** runtime flame animation, physics system

## Notable code patterns

- **Circle.008 as table mesh** — Bruno reuses Blender's circle primitive for the round table. With aggressive smoothing (80° threshold), the polygon facets become invisible.
- **`Smooth by Angle.002`** vs the typical `.003` — Bruno has multiple smoothing node-group variants and picks one per prop. `.002` is the softer variant (high-threshold).
- **Companion to mainTable** — same collider shape, same candle material, similar physics anchor. Bruno's table-pair pattern (one round, one rectangular) in the lab.
- **`refCandleFlame.002`** suffix — there's also `refCandleFlame` in 085_mainTable (no suffix) and `refCandleFlame.002` here. So `.001` is used elsewhere (maybe the cauldron or oven — `084_cauldron`, `100_oven`).
- **Z-stacking math:** table at z=1.000, candle at z=1.228 → candle has its origin 0.228m above the table's origin, which is presumably the candle mesh's BOTTOM (the flame sits on the table).
- **Smallest table-furniture script** (102 lines) — Bruno's minimum-viable round-table pattern.
