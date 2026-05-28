# 066_checkpoints.py — 8 flat trigger planes along the race lap

**Path:** `folio-2025/scripts/blender_world_steps/steps/066_checkpoints.py`
**Lines:** 121
**Adds:** 8 MESH objects to collection `checkpoints`
**Group:** [08-race-track](../08-race-track.md)

## What it does (code-level)

Creates `checkpoints` collection. Adds 8 instances of the SAME mesh datablock `Plane.061` placed at 8 lap-segment positions on the track, with rotations matching the track direction at each point.

All 8 objects share:
- **Mesh datablock**: `Plane.061`
- **Scale**: `(10.0, 1.671, 1.671)` — long banner-like, 10m in X
- **Z**: `0.862` (sitting just above track surface)
- **Custom prop**: `preventFrustum=True`
- **NO** modifier (no Smooth-by-Angle — flat plane needs no normals work)

Positions and Z-rotations:

| # | (x, y) | rotZ (rad) |
|---|---|---|
| .000 | (-11.25, 0.47) | 0 |
| .001 | (37.06, 47.82) | -π/2 |
| .002 | (39.70, 80.26) | π/2 |
| .003 | (-15.45, 47.16) | π |
| .004 | (-61.81, 27.47) | π/2 |
| .005 | (-38.17, 66.28) | -π |
| .006 | (-60.84, -15.98) | π/2 |
| .007 | (-56.05, -70.52) | -π/2 |

Roughly a loop: south corner (.000), up the east edge (.001 → .002), back across (.003), west side (.004, .006, .007), top (.005).

## Key data

- **Datablocks referenced:** mesh `Plane.061` (instanced 8×)
- **Materials assigned:** via mesh datablock — likely transparent (these are invisible triggers in the runtime)
- **Modifiers added:** none
- **Custom properties:** `preventFrustum=True` on every checkpoint
- **World positions of key anchors:** 8 positions tracing the lap (see table above) — all at z=0.862
- **Object types breakdown:** 8 MESH, 0 EMPTY
- **Parent collection:** `checkpoints` (re-parented under `circuit/` by finalize)

## Technique / recipe

**Trigger-volume-as-mesh pattern.** Bruno uses a flat plane mesh (instead of an empty cube) to define each checkpoint, presumably because:
- The mesh has 4 verts/4 edges with a defined orientation — the runtime can compute "did the car cross this plane this frame?" by comparing prev-pos and curr-pos against the plane's normal
- A 10m × 1.67m plane is wide enough that any lateral car position counts as a valid lap crossing
- Reusing `Plane.061` means zero extra mesh data — only 8 transforms

**`preventFrustum=True` everywhere** — this flag tells the runtime "never cull this object by view frustum." Required because a checkpoint must fire whether or not the camera is pointing at it.

**Rotation encodes track direction** — each rotZ matches the direction the car is moving at that point on the track. The runtime probably uses the local Y-axis of the plane as the "crossing direction" for lap-counting.

**No mesh material smoothing** — the visible appearance is probably invisible/transparent in the runtime; the mesh exists for trigger-detection geometry only.

## Connections

- **Reads from:** `005_meshes_*.py` (`Plane.061`)
- **Read by:** `999_finalize.py` (parents `checkpoints/` under `circuit/`)
- **Depends on:** `062_circuit.py`
- **Depended on by:** runtime lap-counter

## Notable code patterns

- **Identical scale + identical mesh + 8 transforms** — extreme economy. The 8 checkpoints occupy ~600 bytes of .blend object overhead vs. ~kilobytes if each had its own mesh.
- **`refCheckpoints.NNN` naming** — `ref` prefix matches Bruno's runtime-referenced object convention.
- **The polar pattern** of checkpoints around the track suggests a circuit roughly 100m × 150m centered at (-15, 25) — confirming the race-track footprint estimated from `062_circuit.py`'s frustum radius (~55m around (-51, -12)).
