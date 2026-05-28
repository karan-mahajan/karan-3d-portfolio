# 062_circuit.py — race-track root: zone anchors only, no visible geometry

**Path:** `folio-2025/scripts/blender_world_steps/steps/062_circuit.py`
**Lines:** 89
**Adds:** 5 EMPTY objects to collection `circuit`
**Group:** [07-major-areas](../07-major-areas.md)

## What it does (code-level)

Creates collection `circuit` (no scene-link call), then adds 5 EMPTY objects — all zone-management anchors. Zero meshes. Zero modifiers. Pure hierarchy/anchor data:

| Empty | Type | Location | Scale | Rotation (rad) |
|---|---|---|---|---|
| `refInteractivePoint.003` | PLAIN_AXES | (-11.47, -7.39, 1.5) | (1,1,1) | (0,0,0) |
| `refStart` | ARROWS | (-9.23, -5.74, 0.5) | (1,1,1) | (0, 0, π/2) |
| `refZoneBounding.009` | CIRCLE | (-17.74, -7.07, 3.27) | (19.48)³ | (-π/2, 0, 0) |
| `circuit` (root anchor) | PLAIN_AXES | (-17.74, -7.07, 3.27) | (1,1,1) | (0,0,0) |
| `refZoneFrustum.009` | CIRCLE | (-51.02, -12.09, 3.27) | (55.16)³ | (-π/2, 0, 0) |

The bounding circle (radius ≈19.5m at center -17.74, -7.07) defines the race-track zone for entry/exit detection. The frustum circle (radius ≈55m at -51, -12) is much larger — likely defines the "always-render this zone's contents even if behind the player camera" volume.

## Key data

- **Datablocks referenced:** none (all empties)
- **Materials assigned:** none
- **Modifiers added:** none
- **Custom properties:** none
- **World positions of key anchors:**
  - **Race-track center:** (-17.74, -7.07, 3.27) — `circuit` root anchor + bounding zone
  - **Race start line:** (-9.23, -5.74, 0.5) — `refStart` (ARROWS pointing along +Y)
  - **Interactive point:** (-11.47, -7.39, 1.5) — probably the "Press E to start race" hotspot
  - **Frustum culling center:** (-51.02, -12.09, 3.27) — wider zone for streaming/render
- **Object types breakdown:** 5 EMPTY, 0 MESH
- **Parent collection:** `circuit` (re-parented under `areas/` by finalize)

## Technique / recipe

This is Bruno's **canonical zone-root anchor pattern**, repeated for every gameplay zone:

1. **`<zoneName>` PLAIN_AXES empty** — the zone's logical origin, sits at the bounding-circle center
2. **`refZoneBounding.NNN` CIRCLE empty** — large flat circle (rotated -π/2 around X to lay flat), scale = bounding radius. The runtime uses this to detect when the player has "entered" the zone
3. **`refZoneFrustum.NNN` CIRCLE empty** — even larger flat circle. Likely controls aggressive frustum-culling — "if the player is inside this radius, keep all zone children renderable"
4. **`refStart` ARROWS empty** (optional, race-specific) — direction-indicating arrows for AI/player spawn orientation
5. **`refInteractivePoint.NNN` PLAIN_AXES empty** (optional) — UI interaction hotspot

The `circuit` collection is intentionally empty of geometry — ALL race-track props live in 16 child collections (cones, barrels, checkpoints, startingLights, timer, road, zigzag, obstacles, jump, rails, podium, banners, scenery, leaderboard, leaderboardReset, sign) that finalize parents under `circuit/`.

## Connections

- **Reads from:** nothing
- **Read by:** `999_finalize.py` (parents 16 child race-track collections under `circuit/`; re-parents `circuit/` under `areas/`)
- **Depends on:** `044_areas.py` must have created the `areas` umbrella
- **Depended on by:** All race-track child scripts (065-068, 071-078, 120, 122, 123, 137)

## Notable code patterns

- `empty_display_type` values selected to *communicate intent in the Blender viewport*: `ARROWS` for directional anchors, `CIRCLE` for zone radii, `PLAIN_AXES` for logical origins, `CUBE` for collider volumes (not used here but seen in 088_landing). This is visual documentation in the .blend itself.
- The dual bounding/frustum circles (`refZoneBounding` ≈19m vs `refZoneFrustum` ≈55m) imply a two-tier visibility/culling system: bounding is "player is here," frustum is "player is close enough to care."
- Indices `.009` and `.008` (bowling) etc. on `refZoneBounding`/`refZoneFrustum` mean there's a global scheme — each zone gets its own bounding/frustum pair with a sequential index.
