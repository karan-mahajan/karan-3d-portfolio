# 049_behindTheScene.py — zone anchor container for "behind the scene" area

**Path:** `folio-2025/scripts/blender_world_steps/steps/049_behindTheScene.py`
**Lines:** 90
**Adds:** 5 objects to collection `behindTheScene`
**Group:** [06-buildings-structures](../06-buildings-structures.md)

## What it does (code-level)

Creates collection `behindTheScene`. Adds 5 EMPTY objects:

- `refCenter.001` — PLAIN_AXES, at (52.75, 11.10, 0.0) — the zone center reference
- `refInteractivePoint.004` — PLAIN_AXES, at (53.36, 10.31, 1.5) — player interaction trigger at eye height
- `refZoneBounding.010` — CIRCLE, at (52.46, 11.96, 3.27), scale=8.157 → r=8.16m bounding circle
- `behindTheScene` — PLAIN_AXES root empty, at (52.46, 11.96, 3.27) (co-located with bounding circle)
- `refZoneFrustum.010` — CIRCLE, at (52.62, 11.48, 3.27), scale=5.905 → r=5.90m frustum circle

Zone center: **(52.46, 11.96)**. This is in the northeastern area of the island, near the building.

## Key data

- **Datablocks referenced:** none (all EMPTYs)
- **Materials assigned:** none
- **Object types breakdown:** 0 MESH, 5 EMPTY
- **Parent collection:** `behindTheScene`
- **Child collections (populated by later scripts):** `lightGenerators` (050), `scenery.001` (051)

## Technique / recipe

Pure zone scaffold — no geometry, just the 5-empty zone pattern: center ref + interaction point + bounding circle + root empty + frustum circle. The two CIRCLE empties are rotated -90° on X and scaled to their respective radii — this is Bruno's standard zone volume encoding.

The `behindTheScene` root empty serves as the transform handle for the entire zone: `999_finalize.py` parents all child collections under it.

## Connections

- **Reads from:** nothing
- **Read by:** `999_finalize.py` (parents lightGenerators + scenery.001 under behindTheScene); runtime zone system
- **Depends on:** `013_collections.py`
- **Depended on by:** `050_lightGenerators.py`, `051_scenery.001.py` (not in this batch)

## Notable code patterns

`refZoneBounding` (r=8.16) > `refZoneFrustum` (r=5.90) — reversed from what you'd expect if "bounding" = outer. Looking at the altar: bounding (12.35) < frustum (12.87). The naming convention seems: `ZoneBounding` = the "loaded" radius; `ZoneFrustum` = the frustum-culling radius. The runtime may use them in different ways than the names imply. Worth noting across all zone scripts.
