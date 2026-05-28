# 105_statue.py — statue collection stub

**Path:** `folio-2025/scripts/blender_world_steps/steps/105_statue.py`
**Lines:** 9
**Adds:** 0 objects to collection `statue`
**Group:** [06-buildings-structures](../06-buildings-structures.md)

## What it does (code-level)

Creates collection `statue` and links it to the scene root. Adds no objects.

```python
col = bpy.data.collections.get('statue') or bpy.data.collections.new('statue')
if col.name not in bpy.context.scene.collection.children:
    bpy.context.scene.collection.children.link(col)
```

No geometry, no EMPTYs, no zone anchors.

## Key data

- **Datablocks referenced:** none
- **Materials assigned:** none
- **Object types breakdown:** 0 MESH, 0 EMPTY
- **Parent collection:** `statue` (scene root)
- **World position:** unknown — no objects placed

## Technique / recipe

Pure collection-creation stub — identical pattern to the tree scaffolding scripts (028/032/036). The `statue` collection is reserved for content authored in a separate script (not in this batch) or placed manually in Blender and then organized under this collection by `999_finalize.py`.

This pattern appears when Bruno wants a named slot in the scene hierarchy before the actual content script is ready, or when the statue geometry is added via a separate process (e.g., imported from another file, placed by a later finalize step).

## Connections

- **Reads from:** nothing
- **Read by:** `999_finalize.py`
- **Depends on:** `013_collections.py`
- **Depended on by:** unknown (no dependents identified in this batch)

## Notable code patterns

Same 9-line stub as `028_oakTrees.py`, `032_birchTrees.py`, `036_cherryTrees.py`, and `091_kiosk.py` (26 lines, slightly larger). The recurrence of this stub in group 06 alongside the tree group stubs suggests Bruno's build pipeline pre-allocates named collection slots early in the numbering scheme even when content is authored later or externally.
