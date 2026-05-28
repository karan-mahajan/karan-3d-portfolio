# 075_scenery.py — the race-circuit's branded scenery (10 visible + 33 collider proxies)

**Path:** `folio-2025/scripts/blender_world_steps/steps/075_scenery.py`
**Lines:** 963
**Adds:** 43 objects (10 MESH + 33 EMPTY) in collection `scenery`
**Group:** [03-surface-detail](../03-surface-detail.md) (but parented under `circuit`, not `scenery.002`)

## What it does (code-level)

This script lives in collection `scenery` (no `.001`/`.002` suffix), which is the **race-circuit's local scenery** per the parent link in [013-collections.md](../01-foundation/013-collections.md): `circuit → scenery`.

43 objects in three structural categories:

### 10 visible MESH props
- `refObjectsPhysicalDynamic.008` — mesh `Cylinder.069` (dynamic physics)
- `refObjectsPhysicalDynamic.009` — mesh `Cylinder.069` (shared with .008/.010)
- `refObjectsPhysicalDynamic.010` — mesh `Cylinder.069`
- `refObjectsPhysicalDynamic.011` — mesh `Cube.220`
- `refObjectsPhysicalDynamic.012` — mesh `Cube.234`
- `refObjectsPhysicalDynamic.013` — mesh `Plane.130` (has **BEVEL** modifier — width 0.05, angle 30°)
- `Cube.088` — mesh `Cube.217` (anchored at the road-segment anchor `(-1.73, -15.73, +1.00)`)
- `Cylinder.039` — mesh `Cylinder.061`
- `Cylinder.022` — mesh `Cylinder.027`, at `(-21.28, 7.84, 3.68)` (3.7 m above ground — flagpole-height)
- `Cylinder.037` — mesh `Cylinder.054` (at the same world position as `Cylinder.022`, has **BEVEL** modifier — width 0.10, angle 30°)

### 33 EMPTY collider proxies, two flavors:
- **`cuboid.NNN`** (~18 of them): `empty_display_type='CUBE'`, scaled to act as box colliders. Examples: `cuboid.013/.110/.120/.123-125/.170-186/.191/.192`.
- **`tube.NNN`** (~15 of them): also `empty_display_type='CUBE'` (no separate "tube" empty type in Blender — naming convention only). Examples: `tube.027-040`.
- **1 `physicalFixed.006`**: a static-rigidbody empty marker.

### Modifiers
- 7 modifiers added in this script. Examples:
  - `refObjectsPhysicalDynamic.013` → **BEVEL** modifier (`width=0.05`, `segments=1`, `affect='EDGES'`, `limit_method='ANGLE'`, `angle_limit=0.524 rad ≈ 30°`, `profile_type='SUPERELLIPSE'`, `profile=0.5`, `miter_outer/inner='MITER_SHARP'`, `use_clamp_overlap=True`). Bevels every edge whose angle is below 30°.
  - `Cylinder.037` → **BEVEL** modifier (width 0.10, otherwise identical).
  - Several others have `Smooth by Angle.003` (NODES) — same as bridges/slabs pattern.

### Materials
Per [03-surface-detail.md](../03-surface-detail.md), this collection uses `circuitBrand`, `circuitWebgl`, `circuitWebgpu`, `palette`. The branded materials live on the mesh datablock slots (set in 005), not added in this script.

## Key data

- **Datablocks referenced**:
  - Meshes: `Plane.130`, `Cube.217`, `Cube.220`, `Cube.234`, `Cylinder.027`, `Cylinder.054`, `Cylinder.061`, `Cylinder.069` (from foundation 005 chunks).
  - Node group: `Smooth by Angle.003` (003-node-groups).
- **Materials assigned**: `circuitBrand`, `circuitWebgl`, `circuitWebgpu`, `palette` via mesh slots.
- **Modifiers added**: 7 — mix of `BEVEL` (Blender built-in) and `NODES` (`Smooth by Angle.003`).
- **Custom properties**: none surfaced in my sample read of the script. `refObjectsPhysicalDynamic.NNN` naming alone is the dynamic-physics signal — runtime probably reads the name suffix.
- **World positions of key anchors**:
  - Visible props cluster around `(-23, +2, 0.5)` (the western edge of the race circuit).
  - Tall vertical poles: `Cylinder.022/.037` at `(-21.28, 7.84, 3.68)` (3.7 m elevation suggests these are flagpoles or banner poles).
  - Empties scattered from `(-64, +41)` to `(-21, +18)` — the race-circuit's outer arc.
- **Object types breakdown**: 10 MESH + 33 EMPTY.
- **Parent collection**: `scenery` (child of `circuit`).

## Technique / recipe

The "circuit branded-prop placement + heavy collider authoring" pattern:

- **`scenery` (no suffix) is the circuit's local scenery** — not the world's. Note the naming hazard: `scenery` ≠ `scenery.001` (behindTheScene) ≠ `scenery.002` (world-level rocks/bridges/road/slabs container).
- **BEVEL modifier** (Blender built-in, not Geometry-Nodes) for selective edge-rounding on branded planes/cylinders. The Smooth-by-Angle group can't bevel geometry — it only changes normals. For visible rounded edges (like a beveled signpost), Bruno uses the real BEVEL modifier.
  - All BEVEL params are identical except width: profile=0.5 (round bevel), miter=SHARP, angle=30°. The width difference (0.05 vs 0.10 m) tunes how chunky the bevel is per-prop.
- **`refObjectsPhysicalDynamic.NNN` for dynamic physics**: same convention as 051. The runtime spawns these as Rapier dynamic bodies.
- **`cuboid.NNN` (box colliders) + `tube.NNN` (cylindrical colliders)**: naming convention encodes collider shape. Both use `empty_display_type='CUBE'` in Blender (since "tube" isn't an empty type), but the runtime probably reads the name prefix and creates a cylinder collider for `tube.*`.
- **Same world-anchor `(-1.73, -15.73, +1.00)`** for `Cube.088` as the road-segment cubes in [025-road-001.md](025-road-001.md) — this object is part of the same "baked from curve" pipeline (likely a road-side scenery piece extruded along the road curve).
- **`Cylinder.022/.037` at the same world position** `(-21.28, 7.84, 3.68)` — co-located, like the slabs script's pair. One is a visible mesh, the other has a BEVEL modifier — possibly a layered authoring trick (one for outline, one for fill).

## Connections

- **Reads from**:
  - 005-mesh chunks (Plane.130, Cube.217/.220/.234, Cylinder.027/.054/.061/.069)
  - 003-node-groups (Smooth by Angle.003)
  - 004-materials (circuitBrand, circuitWebgl, circuitWebgpu, palette via mesh slots)
  - 013-collections (`scenery` exists, parented to `circuit`)
- **Read by**: 062_circuit (the circuit area's parent script) parents this collection under `circuit`; 999_finalize.
- **Depends on**: 005, 003, 004, 013.
- **Depended on by**: 062_circuit, 999_finalize.

## Notable code patterns

- **Largest surface-detail script** at 963 lines for 43 objects — about 22 lines per object on average (visible meshes have more lines due to modifier params).
- **Two modifier flavors mixed**: BEVEL (built-in) for visible edge rounding, Smooth by Angle (NODES) for normal smoothing. Bruno picks the right tool per use case.
- **Identical BEVEL parameter set across the file** (only width changes) — confirms Bruno has a single bevel recipe he reuses everywhere; the width is the one knob.
- **`tube.027-.040` block (15 tubes)** suggests a series of vertical poles (flagpoles, banner posts, fence supports) along the race-circuit's edge — Bruno authored one tube collider then duplicated/translated for the row.
- **18 `cuboid.NNN` + 15 `tube.NNN` = 33 empties** — 3.3 colliders per visible prop. Higher ratio than basaltRocks (1.6) or 051_scenery (1.7); the circuit's scenery has more complex collision than simple rocks.
- **BEVEL on a Plane mesh**: `refObjectsPhysicalDynamic.013` (Plane.130) gets BEVEL even though planes have very few edges. Probably to round the rectangular outline of a billboard prop slightly.
- **`refObjectsPhysicalDynamic.NNN` numbering skips and overlaps with 051's**: 051 used .021-.023; 075 uses .008-.013. The numbering is per-Bruno authoring order; not contiguous.
