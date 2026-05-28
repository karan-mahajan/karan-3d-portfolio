# 114_toilet.py — toilet zone with fallen rock prop and asymmetric bounding radii

**Path:** `folio-2025/scripts/blender_world_steps/steps/114_toilet.py`
**Lines:** 70
**Adds:** 4 objects to collection `toilet`
**Group:** [06-buildings-structures](../06-buildings-structures.md)

## What it does (code-level)

Creates collection `toilet`. Adds 4 objects:

**Visible geometry** (1 MESH):
- `rocks.001` — mesh `Cube.118`, at (66.72, -63.31, 0.0), rotation=(-2.130, 0.0, 0.0) rad — heavily tilted on X

**Zone anchor empties** (3 EMPTY):
- `refZoneBounding.007` — CIRCLE, at (66.88, -66.74, 3.27), scale=6.083 → r=6.08m
- `toilet` — PLAIN_AXES root empty, at (66.88, -66.74, 3.27) (co-located with bounding)
- `refZoneFrustum.007` — CIRCLE, at (66.88, -66.74, 3.27), scale=12.183 → r=12.18m

Zone center: **(66.88, -66.74)**. Southeast area of island.

## Key data

- **Datablocks referenced:** mesh `Cube.118`
- **Materials assigned:** `palette` (via mesh datablock)
- **Modifiers added:** none
- **World positions:** rock prop at (66.72, -63.31), zone root at (66.88, -66.74) — ~3.4m apart on Y
- **Object types breakdown:** 1 MESH, 3 EMPTY
- **Radii:** bounding r=6.08m, frustum r=12.18m — frustum is 2× bounding (unusual; most zones have frustum ≈ bounding)
- **No `refInteractivePoint`** — no direct player interaction trigger

## Technique / recipe

`rocks.001` uses `Cube.118` with a heavy X rotation of -2.13 rad (≈-122°, effectively 58° past horizontal = lying on its side). This is a fallen/overturned rock or toilet prop — the name `toilet` suggests this is a comedic outdoor/ruined toilet prop. The object name `rocks.001` implies the mesh `Cube.118` is a rock-shaped mesh, and the toilet zone may contain a hidden/ruined toilet indicated purely by context and placement.

The zone lacks a `refInteractivePoint` — the toilet is either a purely atmospheric zone (no player interaction) or its interaction point is authored in a companion script not yet analyzed.

**Radii asymmetry is notable:** `refZoneFrustum.007` at r=12.18m is exactly 2× `refZoneBounding.007` at r=6.08m. In the altar (048), frustum (12.87) ≈ bounding (12.35) — nearly equal. In the toilet, the frustum is dramatically larger, suggesting the runtime begins culling/loading the toilet zone much earlier than the "in zone" trigger fires.

The prop (`rocks.001` at y=-63.31) is 3.4m north of the zone root (y=-66.74) — consistent with the rock being placed in front of the toilet building entrance, while the zone center is the building interior.

## Connections

- **Reads from:** `005_meshes_*.py` (`Cube.118`), `004_materials.py`
- **Read by:** `999_finalize.py` (parents toilet zone); runtime zone system
- **Depends on:** `013_collections.py`
- **Depended on by:** nothing (no child collections identified)

## Notable code patterns

The 2:1 frustum-to-bounding ratio (12.18 : 6.08) is the widest gap in this batch — compare with behindTheScene (8.16 : 5.90 ≈ 1.38:1) and altar (12.87 : 12.35 ≈ 1.04:1). The toilet's large frustum preload radius may be due to its isolated southeast position far from other zones — the runtime starts loading its content early to avoid pop-in when the player rounds the island perimeter.

The X-rotation of -2.130 rad is very precise (not a round number like π/4 or π/6) — authored by physically dragging the rock in Blender's viewport and accepting the exact angle where it "looks right."
