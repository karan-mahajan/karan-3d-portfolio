# 139_whispersForbiddenAreas.py — 12 audio-only forbidden-zone markers

**Path:** `folio-2025/scripts/blender_world_steps/steps/139_whispersForbiddenAreas.py`
**Lines:** 204
**Adds:** 12 objects (12× EMPTY) to collection `whispersForbiddenAreas`
**Group:** [13-food-misc-fx](../13-food-misc-fx.md)

## What it does (code-level)
1. Gets/creates collection `whispersForbiddenAreas`; explicitly links to scene root.
2. Creates 12 EMPTY objects `forbidden.000` through `forbidden.011`, all with:
   - `empty_display_type='CIRCLE'`, `empty_display_size=1.0`.
   - `rotation_euler=(-π/2, 0, 0)` — circle lies flat on the XY plane (visible from above).
   - `scale=(s, s, s)` where s varies per zone (1.81 to 4.45 — defines the zone radius).
   - `z=3.2733683586120605` (zone-anchor altitude).
   - Per-zone hand-tuned X/Y.

Zone list:
| # | (X, Y) | Scale (radius) |
|---|---|---|
| 0 | (45.19, -33.13) | 2.35 |
| 1 | (39.62, -37.83) | 3.41 |
| 2 | (54.97, -31.86) | 3.41 |
| 3 | (55.24, -46.39) | 2.96 |
| 4 | (69.65, -16.98) | 2.96 |
| 5 | (53.22, 10.81) | 3.55 |
| 6 | (25.93, 18.14) | 1.81 |
| 7 | (39.39, 31.05) | 1.73 |
| 8 | (12.87, -16.10) | 4.37 |
| 9 | (35.77, -11.37) | 4.45 |
| 10 | (16.64, -69.22) | 2.78 |
| 11 | (24.33, -56.57) | 2.09 |

## Key data
- **Datablocks referenced**: NONE.
- **Materials assigned**: N/A.
- **Modifiers added**: none.
- **Custom properties**: none.
- **World positions**: 12 anchors scattered across south/east half of island, mostly clustered around the eastern/southern landmass (forbidden-knowledge themed zones).
- **Object types breakdown**: 12 EMPTY (CIRCLE display).
- **Parent collection**: `whispersForbiddenAreas` (scene-root, EXCLUDED in finalize).

## Technique / recipe
- **CIRCLE-display empties = activation rings**. The empty's `scale` IS the trigger radius — the runtime reads the empty's scale and treats it as a sphere radius. `empty_display_type='CIRCLE'` makes it visible in the Blender editor as a circle for layout.
- **Audio-only triggers**: no mesh, no material, no children — just position + radius. When the player enters a circle's radius, the runtime plays whispers/ambient audio.
- The scale variation (1.73 to 4.45) lets each zone have its own size — small intense zones vs big sweeping ambiences.

## Connections
- **Reads from**: nothing.
- **Read by**: `999_finalize.py` (sets view-layer EXCLUDE on `whispersForbiddenAreas`).
- **Depends on**: `013_collections.py` (collection skeleton).
- **Depended on by**: runtime audio system in `folio-2025/sources/Game/` (probably `Audio/Forbidden/` or `Triggers/Audio/`).

## Notable code patterns
- **CIRCLE empty as runtime zone trigger** — Bruno uses this consistently across the world (see also `refZoneFrustum.005` in [079_cookie.md](079-cookie.md), `refZoneBounding.005` etc.). The display type encodes the runtime behavior.
- Rotation `-π/2` on X — flips the circle from vertical (XZ plane default) to horizontal (XY plane). Standard for top-down zone triggers.
- 12 anchors-only script, same pattern as [138_tornado.md](138-tornado.md). Both demonstrate Bruno's "no mesh needed → empty-only script."
- All EXCLUDED from view-layer — the player never sees the circles directly, only experiences the audio when crossing them.
