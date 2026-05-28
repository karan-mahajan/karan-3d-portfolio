# 053_alley.py — empty placeholder collection for the bowling alley lane

**Path:** `folio-2025/scripts/blender_world_steps/steps/053_alley.py`
**Lines:** 9
**Adds:** 0 objects to collection `alley`
**Group:** [07-major-areas](../07-major-areas.md)

## What it does (code-level)

The smallest script in the entire pipeline. Two functional lines:

```python
coll = bpy.data.collections.get('alley')
if coll is None: coll = bpy.data.collections.new('alley')
```

Note: does NOT call `scene.collection.children.link(coll)`. The collection is created in `bpy.data.collections` but is never linked to the scene by this script — `999_finalize.py` handles linking it under `bowling/` later.

## Key data

- **Datablocks referenced:** none
- **Materials assigned:** none
- **Modifiers added:** none
- **Custom properties:** none
- **World positions:** none
- **Object types breakdown:** 0 objects
- **Parent collection:** Created un-parented; finalize re-parents under `bowling`

## Technique / recipe

A placeholder slot. The alley itself (the lane planks the ball rolls on) is either:
- Part of `bowling` (052) — see the two `Plane.043`/`Plane.042` meshes there, which are the sign meshes, not the lane
- Part of `055_furnitures.py` (43 objects, the bulk of bowling-zone meshes — lane planks probably live here)
- Runtime-generated (the lane could be procedural — laid down by the bowling game-logic in `folio-2025/sources/`)

Why bother creating an empty collection? **It reserves the hierarchy slot** so the finalize step's parenting graph has a stable target. Even though zero meshes live in `alley/` at script time, the runtime can target this collection name to spawn lane planks, debug visualizers, etc.

## Connections

- **Reads from:** nothing
- **Read by:** `999_finalize.py` (parents under `bowling/`)
- **Depends on:** `052_bowling.py` should have run first to create the `bowling` collection
- **Depended on by:** nothing Blender-side; runtime bowling-logic may spawn objects here

## Notable code patterns

The "empty slot" pattern shows up again later (e.g., `123_vehicle.py` does the same — empty parent for vehicle child collections). Bruno reserves hierarchy slots even when the script has nothing to add.
