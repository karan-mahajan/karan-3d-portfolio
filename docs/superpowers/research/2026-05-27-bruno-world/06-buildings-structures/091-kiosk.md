# 091_kiosk.py — kiosk zone interaction point only

**Path:** `folio-2025/scripts/blender_world_steps/steps/091_kiosk.py`
**Lines:** 26
**Adds:** 1 object to collection `kiosk`
**Group:** [06-buildings-structures](../06-buildings-structures.md)

## What it does (code-level)

Creates collection `kiosk`. Adds 1 EMPTY object:

- `refKioskInteractivePoint` — PLAIN_AXES, at (45.18, -33.14, 1.50), rotation Z=0.0872 rad (≈5°)

No mesh, no zone bounding/frustum circles, no physics anchor.

## Key data

- **Datablocks referenced:** none (all EMPTYs)
- **Materials assigned:** none
- **Modifiers added:** none
- **World position:** kiosk at **(45.18, -33.14)**. Southern half of island, southeast area.
- **Object types breakdown:** 0 MESH, 1 EMPTY
- **Parent collection:** `kiosk`
- **Child collections (populated by later scripts):** none listed

## Technique / recipe

Absolute minimum zone script: a single interaction point EMPTY, no zone bounding volume, no physics. This is a stripped-down zone scaffold — the kiosk either has no enter/exit detection or its bounding/frustum circles live in a different script (possibly in the finalize or a companion prop script not yet in this batch).

The `z=1.50` places the interaction trigger at player eye height — consistent with all other `refInteractivePoint` empties in the codebase (lab: 1.50, behindTheScene: 1.50). The 5° Z-rotation fine-tunes the player approach direction.

## Connections

- **Reads from:** nothing
- **Read by:** `999_finalize.py`; runtime interaction system reads `refKioskInteractivePoint`
- **Depends on:** `013_collections.py`
- **Depended on by:** runtime interaction system (triggers kiosk interaction modal at this position)

## Notable code patterns

Smallest building-structures script after the stub scripts (105, 028, 032, 036). The absence of `refZoneBounding` / `refZoneFrustum` is unique in this group — either the kiosk is treated as always-loaded or the detection volume is authored inline in the kiosk mesh script (not in this batch). This is the only script in group 06 where the zone anchor set is incomplete relative to Bruno's 5-empty zone pattern.
