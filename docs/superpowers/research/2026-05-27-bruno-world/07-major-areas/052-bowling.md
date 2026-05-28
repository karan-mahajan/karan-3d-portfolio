# 052_bowling.py — bowling-alley root: entry sign + ball + zone anchors

**Path:** `folio-2025/scripts/blender_world_steps/steps/052_bowling.py`
**Lines:** 234
**Adds:** 13 objects (5 MESH, 8 EMPTY) to collection `bowling`
**Group:** [07-major-areas](../07-major-areas.md)

## What it does (code-level)

Creates `bowling` collection and adds 13 objects: the bowling ball mesh, the entry-sign frame + two decorative bowling pins, plus 8 anchor empties (zone bounds, ball respawn, physics colliders, sphere-trigger volumes).

| Object | Type | Mesh datablock | Location | Notes |
|---|---|---|---|---|
| `refBallPhysicalDynamic` | MESH | `Cube.181` | (11.83, -67.78, 0.97) | The runtime bowling ball |
| `Plane.043` | MESH | `Plane.139` | (25.08, -65.29, 2.58) | Entry-sign board (with `Smooth by Angle.003` GN, Input_1=0.785 rad ≈ 45°) |
| `Plane.042` | MESH | `Plane.135` | (25.28, -65.82, 2.56) | Entry-sign back/frame |
| `sign.001` | MESH | `refBowlingPin.003` | (25.28, -65.82, 5.33) | Decorative pin on the sign — top |
| `sign.002` | MESH | `refBowlingPin.001` | (25.28, -65.82, 5.33) | Decorative pin on the sign — variant |
| `ball.001` | EMPTY/SPHERE | — | (-33.91, -36.97, 0.97) | Far-away sphere empty (scale 1.94) — ball spawn point? |
| `refRestartInteractivePoint` | EMPTY/PLAIN_AXES | — | (17.16, -67.78, 1.5) | "Restart the alley" UI hotspot |
| `physicalFixed.007` | EMPTY/PLAIN_AXES | — | (5.25, -67.77, 0.03) | Anchor for runtime-spawned fixed colliders |
| `cuboid.113` | EMPTY/CUBE | — | (-31.72, -40.23, 0.63) | Trigger volume — bowling area approach |
| `tube.013` | EMPTY/CUBE | — | (-20.77, -34.20, 2.50) | Tall thin volume (scale Z=5.12) — maybe an air-dancer slot |
| `refZoneBounding.008` | EMPTY/CIRCLE | — | (2.31, -68.91, 3.27) | Bowling zone bounding radius ≈17.27 |
| `bowling` (root) | EMPTY/PLAIN_AXES | — | (2.31, -68.91, 3.27) | Zone origin (matches bounding center) |
| `refZoneFrustum.008` | EMPTY/CIRCLE | — | (5.84, -66.82, 3.27) | Frustum-culling radius ≈21.74 |

The bowling zone is centered around **(2.31, -68.91, 3.27)** — south-east of map origin. The entry sign (with the two `refBowlingPin` mesh decorations) is offset to (25.28, -65.82) — about 23m east of zone center, at the player's approach side.

## Key data

- **Datablocks referenced:** mesh `Cube.181` (ball), mesh `Plane.139` (sign frame), mesh `Plane.135` (sign back), mesh `refBowlingPin.003` and `refBowlingPin.001` (decorative pins on sign), node-group `Smooth by Angle.003`
- **Materials assigned:** via mesh datablocks (set in 004_materials.py) — likely `palette` on most, `emissive*` on sign
- **Modifiers added:** 1× `Smooth by Angle.003` (NODES, Input_1≈0.785 rad / 45°) on `Plane.043`
- **Custom properties:** none on these objects (ball physics props are on the runtime-spawned ball, not the template here)
- **World positions of key anchors:**
  - **Bowling zone center:** (2.31, -68.91, 3.27)
  - **Entry sign:** (25.28, -65.82, 5.33) — north-east of zone center
  - **Ball template:** (11.83, -67.78, 0.97)
  - **Restart point:** (17.16, -67.78, 1.5)
  - **Ball anchor empty `ball.001`:** (-33.91, -36.97, 0.97) — far west, possibly a "ball graveyard" or alternate spawn
- **Object types breakdown:** 5 MESH, 8 EMPTY
- **Parent collection:** `bowling` (re-parented under `areas/` by finalize)

## Technique / recipe

Mixes the canonical **zone-root anchor pattern** (bounding circle + frustum circle + zone-name PLAIN_AXES) with a few zone-specific MESH objects:

- The decorative **entry sign** (Plane.043 + Plane.042 + sign.001 + sign.002) lives in the root, not in a sub-collection. It's a stack of 4 meshes: a flat sign plane, its frame back, and two pin-shaped decorations sticking up. Both pin "signs" sit at the same XYZ (25.28, -65.82, 5.33) — they're either two variants (one shown, one swapped at runtime) or layered for an effect.
- The **ball template** (`refBallPhysicalDynamic`) is created here even though it's the "physical dynamic" runtime object. The `refXxx` prefix is Bruno's convention for "this object's name/mesh data is referenced by runtime spawning."
- **Anchor empties** include `physicalFixed.007` (PLAIN_AXES at the lane base — runtime spawns fixed colliders here?) and `cuboid.113` + `tube.013` (CUBE empties — collider/trigger volume primitives).
- The zone center (2.31, -68.91) defines the bowling area; the bounding radius (17.27m) covers the alley + furniture + pins. The frustum radius (21.74m) is slightly larger and offset to (5.84, -66.82) — accounting for the player's typical viewing angle.

## Connections

- **Reads from:** `004_materials.py` (materials on the 5 meshes), `003_node_groups.py` (`Smooth by Angle.003`), `005_meshes_*.py` (mesh datablocks `Cube.181`, `Plane.139`, `Plane.135`, `refBowlingPin.001`, `refBowlingPin.003`)
- **Read by:** `999_finalize.py` (parents bowling sub-collections — alley, pins, pinsPosition, bumpers, sign, screen, jukebox, furnitures, leaderboard, leaderboardReset — under `bowling/`; re-parents `bowling/` under `areas/`)
- **Depends on:** `044_areas.py` (umbrella exists), `005_meshes_*.py`, `003_node_groups.py`
- **Depended on by:** all 9 bowling child scripts (054-060, 069, 070) + `053_alley.py`

## Notable code patterns

- **Two pin decorations at identical position** (`sign.001` and `sign.002` both at (25.28, -65.82, 5.33)) — unusual. Either Bruno is using two pin mesh variants to layer for a parallax/depth trick, or one is a swap-on-strike alt. Worth investigating runtime code.
- **`refBowlingPin.001`/`refBowlingPin.003`** mesh datablocks are reused — these come from 005_meshes and are the same data used by `057_pins.py` for the in-game pins. Sign decorations and gameplay pins share geometry.
- **Single GN modifier (Smooth by Angle.003) only on Plane.043** — the other 4 meshes have no modifier in this script. Smooth-angle was likely applied earlier on those mesh datablocks themselves (mesh-level normals) or isn't needed for those geometries.
- **`ball.001` empty far from the bowling zone** (at -33.91, -36.97 vs zone center 2.31, -68.91) — 70m away. Hint at a "global ball storage" or possibly a non-bowling ball reused here.
