# 074_road.py — 13 cuboid road-surface colliders defining the drivable area

**Path:** `folio-2025/scripts/blender_world_steps/steps/074_road.py`
**Lines:** 233
**Adds:** 14 objects (14 EMPTY — 13 cuboids + 1 PLAIN_AXES anchor) to collection `road`
**Group:** [08-race-track](../08-race-track.md)

## What it does (code-level)

Creates `road` collection. Adds 14 empties total — **zero meshes**. 13 are large flat CUBE colliders (the drivable road surface) + 1 PLAIN_AXES anchor.

All 13 cuboids share:
- **z = -0.48** (slightly sunk below ground surface — the collider top sits flush with terrain)
- **Z scale = 1.0** (the collider is 1m tall from -0.48 to +0.52, providing a flat 0.52m-thick driving surface)
- `empty_display_type='CUBE'`, `empty_display_size=0.5`

Locations + XY scales (the 13 cuboids define a polygonal road region):

| Cuboid | Location (x, y) | Scale (sx, sy) | rotZ (rad) |
|---|---|---|---|
| .138 | (-13.37, 32.26) | (19.05, 112.75) | π |
| .139 | (7.28, 32.63) | (15.55, 52.17) | 2.44 |
| .140 | (29.56, 80.34) | (67.04, 14.86) | π |
| .141 | (54.06, 64.07) | (22.23, 18.19) | π |
| .142 | (-78.56, 54.74) | (15.76, 69.43) | π |
| .143 | (-58.47, 82.23) | (24.83, 14.78) | π |
| .144 | (-46.78, 27.65) | (48.19, 16.81) | π |
| .145 | (-49.05, -68.46) | (40.57, 17.59) | π |
| .146 | (-19.74, -43.69) | (58.29, 21.13) | -2.18 |
| .147 | (37.10, 47.76) | (15.04, 52.17) | π/2 |
| .152 | (-38.43, 33.24) | (15.50, 112.75) | π |
| .155 | (-66.48, -15.79) | (40.88, 19.45) | π |
| .156 | (-78.17, -51.19) | (52.17, 17.59) | -π/2 |

Plus `refRoadPhysicalFixed` PLAIN_AXES at (-17.74, -7.07, 3.27) — same XY as the `circuit` root anchor — this is the runtime-anchor for the road's physical-fixed body.

## Key data

- **Datablocks referenced:** none (all empties)
- **Materials assigned:** none — the visible road surface is painted into the terrain mesh's `terrainData` texture (per the group .md). These cuboids are pure collision geometry.
- **Modifiers added:** none
- **Custom properties:** none
- **World positions of key anchors:** see table — 13 boxes form an L-shaped + branching drivable area covering most of the race track's footprint (~y range -68 to +80, x range -84 to +50)
- **Object types breakdown:** 14 EMPTY, 0 MESH
- **Parent collection:** `road` (re-parented under `circuit/` by finalize)

## Technique / recipe

**Box-union as drivable area:** Bruno defines the road as a UNION of 13 large flat boxes. The runtime checks "is the car's wheel inside any of these boxes?" to determine "is the car on the road or off-track?" Sinking the boxes 0.48m below origin and giving them a 1.0m Z-scale puts the box top at +0.52m above origin — flush with the terrain's surface paint.

**Why boxes and not a mesh?** Boxes have simpler collision tests (AABB intersection) and let the runtime quickly enumerate "list of drivable polygons." A single irregular road mesh would require ray-casts or BVH lookups.

**Each box is wide (15-67m) and oriented** — most are rotated π (180°), a few use 2.44 / -2.18 / ±π/2. The rotations are intentional: the rotated boxes follow corners of the track. For instance, `cuboid.146` at rotZ=-2.18 rad (≈-125°) handles the southwest hairpin.

**Roads + visible surface separation** — the actual visual track texture is on the terrain (see Phase-1 batch-1 docs for terrain), and these boxes provide ONLY the collision/grip surface. The two systems are decoupled — Bruno can re-paint the track without changing collision and vice versa.

**The 1 PLAIN_AXES anchor `refRoadPhysicalFixed`** at the circuit's anchor location — runtime probably reads "all collider boxes in `road/`" and creates one combined PhysicalFixed body parented at this anchor.

## Connections

- **Reads from:** nothing (all empties)
- **Read by:** `999_finalize.py` (parents `road/` under `circuit/`)
- **Depends on:** `062_circuit.py` (circuit zone exists)
- **Depended on by:** runtime — drivable-surface detection, "on-track / off-track" gameplay logic

## Notable code patterns

- **Pure-empty script with non-trivial geometry purpose** — proves Bruno's data is heavily empty-driven. 14 empties define a 200m × 150m drivable area without any mesh data.
- **`cuboid.NNN` indices skip** (.138-.156, missing some like .150, .151, .153, .154) — Bruno's cuboid index space is shared globally; gaps mean those indices live in OTHER scripts (e.g., .144 is here, .145 too, but .150/.151 belong elsewhere).
- **Z-scale uniformly 1.0** — Bruno standardized on a 1m-thick collider for the road. This makes runtime cast/test logic uniform.
- **Boxes sunk into ground (z=-0.48)** rather than placed flush — the small overlap with the terrain mesh helps avoid floating-point gaps where the car could fall through.
