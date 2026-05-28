# 044_areas.py — top-level umbrella collection for all gameplay zones

**Path:** `folio-2025/scripts/blender_world_steps/steps/044_areas.py`
**Lines:** 12
**Adds:** 0 objects to collection `areas` (collection-creation only)
**Group:** [07-major-areas](../07-major-areas.md)

## What it does (code-level)

Three-line stub that does exactly one thing: `bpy.data.collections.new('areas')` if it doesn't exist, then `scene.collection.children.link(coll)` if not already linked. No objects added.

```python
coll = bpy.data.collections.get('areas')
if coll is None: coll = bpy.data.collections.new('areas')
if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
    try: bpy.context.scene.collection.children.link(coll)
    except Exception: pass
print('  added 0 objects to areas')
```

## Key data

- **Datablocks referenced:** none
- **Materials assigned:** none
- **Modifiers added:** none
- **Custom properties:** none
- **World positions of key anchors:** none — pure collection container
- **Object types breakdown:** 0 objects
- **Parent collection:** linked directly under `scene.collection` (scene root)

## Technique / recipe

The "skeleton-first" pattern: create the umbrella collection EARLY in the script order so all later zone-root scripts (052_bowling, 062_circuit, 088_landing, 061_career, 081_lab, 093_projects, 103_social, 048_altar, 079_cookie, 114_toilet, 049_behindTheScene, 108_timeMachine, 105_statue, 092_title.001) can be re-parented under `areas/` during `999_finalize.py`. Bruno NEVER does `coll.children.link(child_coll)` in the zone scripts themselves — they all link the child collection to `scene.collection`, then finalize moves them under `areas`.

Same idempotency pattern used everywhere: `get() or new()`, membership check before `link()`, swallow exceptions on link.

## Connections

- **Reads from:** nothing
- **Read by:** `999_finalize.py` — moves the 14 zone collections (landing, career, social, projects, lab, cookie, altar, toilet, bowling, circuit, statue, timeMachine, behindTheScene, easter — names approximate) into `areas/`
- **Depends on:** `013_collections.py` only insofar as the master collection-skeleton has run
- **Depended on by:** every zone-root script downstream

## Notable code patterns

- The `if name not in {c.name for c in children}` guard is Bruno's universal idempotency pattern — it appears in every single script in the build pipeline.
- No try/except on `collections.new()` — Blender's `new()` is always safe.
- The `print('  added N objects')` line is the convention used in EVERY script for build-log visibility.
