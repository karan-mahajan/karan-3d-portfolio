# 068_jump.py — single jump ramp with collider and anchor

**Path:** `folio-2025/scripts/blender_world_steps/steps/068_jump.py`
**Lines:** 53
**Adds:** 3 objects (1 MESH, 2 EMPTY) to collection `jump`
**Group:** [08-race-track](../08-race-track.md)

## What it does (code-level)

Creates `jump` collection. Adds 3 objects: the jump-ramp mesh + 1 collider empty + 1 anchor empty.

| Object | Type | Mesh | Location | Scale | rotEuler (rad) |
|---|---|---|---|---|---|
| `jump` | MESH | `Cube.154` | (-38.20, 36.25, 0.01) | (5.0, 2.73, 1.0) | (-0.349, 0, 0) |
| `cuboid.131` | EMPTY/CUBE | — | (-77.28, 73.52, 0.01) | (12.77, 5.47, 2.01) | (2.79, 0, 0) |
| `physicalFixed.004` | EMPTY/PLAIN_AXES | — | (-25.29, 3.78, 0.01) | (1, 1, 1) | (0, 0, 0) |

- The visible ramp at (-38.2, 36.25) tilted ≈20° forward (-0.349 rad ≈ -20°).
- The collider cuboid is off-track at (-77.28, 73.52) — same "park off-stage" pattern, but rotated 2.79 rad ≈ 160° around X (almost upside down). Runtime binds this collider to the ramp.
- `physicalFixed.004` PLAIN_AXES at (-25.29, 3.78) — anchor for a runtime-spawned static fixed body (probably the landing zone trigger or runtime-instantiated padding).

## Key data

- **Datablocks referenced:** mesh `Cube.154`
- **Materials assigned:** via mesh datablock — `palette` likely
- **Modifiers added:** none on this mesh (any auto-smooth would be baked into the mesh data)
- **Custom properties:** none in this script
- **World positions of key anchors:**
  - Ramp at (-38.2, 36.25, 0.01) with -20° forward tilt (so the car launches up and forward)
  - Off-stage collider at (-77.28, 73.52) — to be parented onto the ramp at runtime
  - Loose physicalFixed anchor at (-25.29, 3.78) — unrelated to ramp position
- **Object types breakdown:** 1 MESH, 2 EMPTY
- **Parent collection:** `jump` (re-parented under `circuit/` by finalize)

## Technique / recipe

**One-piece prop:** unlike cones/barrels (which scatter many instances), the jump is a single hand-placed ramp. No GN modifier needed — the mesh's normals are already correct.

**Tilted ramp via rotation_euler X = -0.349** (≈-20°) creates the takeoff angle. Scale (5, 2.73, 1) makes it broad and long (10m × 5.5m base when accounting for empty extent convention) — wide enough for the car to drive onto from any approach angle.

**Off-stage rotated collider** — the `cuboid.131` collider is upside-down (rotated 160°) at runtime-bind anchor (-77.28, 73.52). The rotation might be intentional (the runtime applies the inverted transform to flip the collider's "up" face to match the ramp's slanted top).

**`physicalFixed.004`** is the 4th in a sequence of "physically fixed" runtime anchor empties — these scatter across many zone scripts (088_landing has `physicalFixed.003` and `.009`, 052_bowling has `physicalFixed.007`). Each is a target for a runtime-spawned static collider.

## Connections

- **Reads from:** `005_meshes_*.py` (`Cube.154`)
- **Read by:** `999_finalize.py` (parents `jump/` under `circuit/`)
- **Depends on:** `062_circuit.py`
- **Depended on by:** runtime physics — ramp/collider binding

## Notable code patterns

- **3 objects, 53 lines** — the simplest zone-child script in the race track. A counterpoint to 067_cones (590 lines for 21 objects).
- **`empty_display_size=0.5` on `physicalFixed.004`** — smaller than the default 1.0 used elsewhere (e.g., on `refTimer`). The smaller size keeps the viewport less cluttered.
- **No `Smooth by Angle` modifier** on `Cube.154` — Bruno only adds Smooth-by-Angle when needed. For a faceted ramp with hard edges, vertex-normal handling at the mesh level is fine.
