# 138_tornado.py — 17 anchor empties for the tornado event path

**Path:** `folio-2025/scripts/blender_world_steps/steps/138_tornado.py`
**Lines:** 284
**Adds:** 17 objects (17× EMPTY) to collection `tornado`
**Group:** [13-food-misc-fx](../13-food-misc-fx.md)

## What it does (code-level)
1. Gets/creates collection `tornado`; **explicitly links it to the scene root** (`bpy.context.scene.collection.children.link(coll)` if not already).
2. Creates 17 EMPTY objects named `tornado.000` through `tornado.016`, all:
   - `empty_display_type='PLAIN_AXES'`, `empty_display_size=1.0`.
   - `scale=(1, 1, 1)`, `rotation_euler=(0, 0, 0)`.
   - `z=3.2733683586120605` (the "zone anchor altitude" shared with cookie/easter/forbiddenAreas).
   - Hand-tuned X/Y positions tracing a path across the world.

Tornado path (in order, X then Y):
1. `(63.66, 0.24)` — east
2. `(75.44, 14.11)` — east-northeast
3. `(58.40, 21.56)` — north
4. `(38.93, 25.04)` — center-north
5. `(38.93, 13.63)` — center
6. `(26.83, 11.82)` — center-west
7. `(24.60, -14.05)` — center-south
8. `(12.92, -22.81)` — west-southwest
9. `(16.53, -36.44)` — far south
10. `(2.21, -53.82)` — far southwest
11. `(3.04, -67.87)` — beyond south
12. `(23.07, -65.23)` — far south-east
13. `(32.81, -47.15)` — south-east-curve
14. `(51.45, -45.62)` — east curve
15. `(58.40, -32.68)` — back toward east
16. `(72.73, -23.50)` — far east
17. `(62.57, -12.93)` — back to east-center

## Key data
- **Datablocks referenced**: NONE (all empties have `bpy.data.objects.new(name, None)` — no mesh data).
- **Materials assigned**: N/A.
- **Modifiers added**: none.
- **Custom properties**: none.
- **World positions**: 17 hand-placed empties tracing a roughly figure-8/spiral path around the south/east half of the island, all at z=3.273.
- **Object types breakdown**: 17 EMPTY.
- **Parent collection**: `tornado` (scene-root, EXCLUDED in finalize).

## Technique / recipe
- **Pure positional data** — no geometry, no materials, no modifiers. Bruno is using EMPTIES as a serialized point cloud that the runtime reads to drive a particle/effect path. When the tornado event triggers, the TSL/runtime code walks `tornado.000` → `tornado.016` and spawns particle effects, sound, and physics impulses along that route.
- **17 anchors = 16 segments** — gives the runtime enough waypoints to interpolate smooth tornado motion across ~150m of world space.
- **`empty_display_type='PLAIN_AXES'`** — minimal display in Blender; doesn't visually clutter the editing scene.
- All at SAME z=3.273 — tornado moves on a flat horizontal plane. Vertical motion presumably added by runtime (sine/turbulence).

## Connections
- **Reads from**: nothing.
- **Read by**: `999_finalize.py` (does NOT add parenting between these — they're loose empties — but does set view-layer EXCLUDE).
- **Depends on**: `013_collections.py` (collection skeleton).
- **Depended on by**: runtime tornado event in `folio-2025/sources/Game/` (probably under `Events/Tornado/`).

## Notable code patterns
- **EMPTY-only script** — same pattern as `139_whispersForbiddenAreas.py` (12 forbidden-zone anchors, also empties-only). When the runtime needs positional metadata, Bruno uses EMPTIES instead of inventing a JSON sidecar.
- Position naming `.000`/`.001`/…/`.016` (zero-padded) — sortable, predictable. The runtime can iterate `for i in range(17): obj = scene.getObjectByName(f'tornado.{i:03d}')`.
- All 17 objects in ONE collection, one collection in ONE scene — flat hierarchy. The runtime gets the collection by name and iterates its children.
