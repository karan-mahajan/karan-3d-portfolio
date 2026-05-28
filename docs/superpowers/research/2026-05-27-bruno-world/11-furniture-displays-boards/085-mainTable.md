# 085_mainTable.py — lab's main work table with billiard balls, candle, and physics-dynamic anchor

**Path:** `folio-2025/scripts/blender_world_steps/steps/085_mainTable.py`
**Lines:** 126
**Adds:** 6 objects (4 MESH, 2 EMPTY) to collection `mainTable`
**Group:** [11-furniture-displays-boards](../11-furniture-displays-boards.md)

## What it does (code-level)

Creates `mainTable` collection. Adds the lab's main table + its decorative props:

| Object | Type | Mesh | Location | Notes |
|---|---|---|---|---|
| `refBalls` | MESH | `Sphere.007` | (-43.11, 15.82, 1.380) | Ball #1 (billiard?) sitting on the table |
| `refBalls.001` | MESH | `Sphere.003` | (-43.11, 15.46, 1.380) | Ball #2 — 0.36m to the south of ball #1, same z |
| `refCandleFlame` | MESH | `Plane.025` | (-41.43, 15.72, 1.395) | Candle flame plane, rotZ=0.785 (45°) — at the south end of the table |
| `table.004` | MESH | `Cube.067` | (-42.19, 15.85, 0.494) | **The table itself**. rotZ=-1.309 (-75°), `Smooth by Angle.003` modifier (Input_1=0.785 rad ≈45° — softer smoothing than usual) |
| `mainTablePhysicalDynamic.001` | EMPTY/PLAIN_AXES | — | (13.18, -16.69, 0.533) | Physics-dynamic anchor at staging position |
| `cuboid.063` | EMPTY/CUBE | — | (-25.91, 20.58, 0.533) | Collider, rotZ=1.833 (≈105°), scale (1.16, 2.42, 0.98) — table-top collider |

## Key data

- **Datablocks referenced:** meshes `Sphere.007`, `Sphere.003` (the two balls), `Plane.025` (candle flame), `Cube.067` (table); node-group `Smooth by Angle.003`
- **Materials assigned:** `emissiveOrangeRadialGradient` (on the candle flame), `palette` (on table + balls per group .md)
- **Modifiers added:** 1× `Smooth by Angle.003` (NODES, Input_1=0.7854 rad ≈45°) — ONLY on `table.004`. The balls and candle flame are not smoothed.
- **Custom properties:** none
- **World positions of key anchors:**
  - Table at (-42.19, 15.85, 0.494) — lab zone
  - Balls at (-43.11, 15.46 / 15.82, 1.380) — z=1.380 = on top of the table (table at z=0.494 + table height ≈0.9m = ~1.4m for ball surface)
  - Candle at (-41.43, 15.72, 1.395) — also on the table top, ~1.7m to the east of the balls
  - Physics anchor at staging (13.18, -16.69, 0.533)
  - Table-top collider at (-25.91, 20.58, 0.533) — at staging
- **Object types breakdown:** 4 MESH, 2 EMPTY
- **Parent collection:** `mainTable` (re-parented under `lab/` by finalize)

## Technique / recipe

**A still-life table with 3 decorative props + 1 collider:**

1. **Table mesh** (`Cube.067`) — the visible table, rotated -75° around Z to align with the lab's diagonal layout. Smoothed with a 45° threshold (gentler than the typical 30-55° elsewhere) — keeps the table's geometric form but softens the wood-edge transitions.
2. **Two billiard-style balls** (`Sphere.007`, `Sphere.003`) — sitting on the table. Two different mesh datablocks for different ball variants (likely different colors via per-vertex palette assignment).
3. **Candle flame plane** (`Plane.025`) at z=1.395, rotated 45° around Z — a flat billboard plane for the flame texture. Sits on the table next to the balls.
4. **Table-top collider** (cuboid.063) at the lab's coordinates but z=0.533 (≈table-top height + some) — sized to match the table's footprint so the player can place props on top.
5. **Physics-dynamic anchor** at staging — runtime spawns a dynamic body here.

**The candle flame is decorative — no actual emissive light source.** It uses `emissiveOrangeRadialGradient` (the same material as lanterns and bonfire), so it visually glows.

**`Smooth by Angle 45°` (1.047 rad)** on the table — this is much wider than the 30° (0.524 rad) on lanterns/pole-lights, meaning more aggressive smoothing. The table's edges blend more.

**Two balls at near-identical positions** (Δy=0.36m) — they look like a billiard cluster on the table. The names `refBalls` and `refBalls.001` suggest the runtime treats them as a collection (refBalls system?).

**`refCandleFlame` ref-prefix** — the runtime knows to attach the flame's flicker animation to this object by name.

## Connections

- **Reads from:** `005_meshes_*.py` (4 meshes), `003_node_groups.py` (`Smooth by Angle.003`)
- **Read by:** `999_finalize.py` (parents `mainTable/` under `lab/`)
- **Depends on:** `081_lab.py` (parent zone)
- **Depended on by:** runtime flame-animation system, physics system

## Notable code patterns

- **Decoration via 3 props on a single table** — balls + flame + table. Bruno doesn't model the candle stem, only the flame plane. Suggests the candle stem is baked into the table mesh OR is implied by the flame.
- **Smoothing modifier ONLY on the table** — the spheres are pre-smoothed (they're sphere primitives), the flame is a flat plane (no smoothing needed). Bruno doesn't waste modifiers on irrelevant meshes.
- **`mainTable.001` (script 099) parallels this** — same template, but in the projects zone with a `carpet` instead of balls/candle.
- **`PhysicalDynamic` anchor exists for the table** — surprising for furniture. Suggests the table CAN be pushed/moved by the player at runtime. The collider is sized for the table-top so props placed on it ride along.
- **Z-stacking math:** table at z=0.494 (object origin = ~mid-leg), table-top at ~z=0.99, balls at z=1.380 (~0.4m above the table top) → likely the ball mesh has its origin at the ball's center (radius ~0.39m → bottom at z=0.99 = table-top). Consistent.
- **45° rotation on the candle flame** — visual variety (the flame texture is not axis-aligned), but the flame plane is still vertical (no X/Y rotation).
