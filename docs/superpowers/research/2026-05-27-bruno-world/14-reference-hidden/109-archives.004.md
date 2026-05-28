# 109_archives.004.py — single curve used by timeMachine (EXCLUDED)

**Path:** `folio-2025/scripts/blender_world_steps/steps/109_archives.004.py`
**Lines:** 21
**Adds:** 1 object (1× CURVE) to collection `archives.004`
**Group:** [14-reference-hidden](../14-reference-hidden.md)

## What it does (code-level)
Same boilerplate as other archives scripts (029/033/037). One CURVE object `Plane.001` wrapping curve datablock `Plane.003`, at `(-54.72, +66.89, 0.06)` rot 0 scale 1.

Note: location is NOT origin like the tree archives — it's at the timeMachine zone in the northwest. So this isn't a TEMPLATE at origin, it's a PLACED curve at the timeMachine room.

## Key data
- **Datablocks referenced**: curve `Plane.003`.
- **Materials assigned**: none on curve directly.
- **Modifiers added**: none.
- **Custom properties**: none.
- **World positions**: `(-54.72, 66.89, 0.06)` — at the timeMachine zone.
- **Object types breakdown**: 1 CURVE.
- **Parent collection**: `archives.004` → parented under `timeMachine` in finalize. EXCLUDED.

## Technique / recipe
- **Placed-curve archive** — unlike the tree `archives.*` curves (at origin, template-only), this one is at a specific world position. It's likely a curve that drives a runtime spline-extrusion ON the timeMachine prop (e.g., the time-portal swirl, an antenna spiral, the lever path).
- EXCLUDED from view layer — the raw curve isn't visible, but its data drives a visible geometry-nodes setup elsewhere.

## Connections
- **Reads from**: `007_curves.py` (`Plane.003`).
- **Read by**: `108_timeMachine.py` (which presumably has a geometry-nodes modifier reading this curve). Finalize parents it under the timeMachine zone.
- **Depends on**: 007, 013.
- **Depended on by**: timeMachine zone + finalize.

## Notable code patterns
- Different role from the tree archives: this is a SPECIFIC LOCATION reference curve, not a template. Naming pattern (`archives.004`) is reused for "any single curve we need to keep around" rather than strictly "tree-template."
- The curve datablock `Plane.003` is also potentially used by other props — Bruno reuses these "generic Plane.NNN" curves across the world.
