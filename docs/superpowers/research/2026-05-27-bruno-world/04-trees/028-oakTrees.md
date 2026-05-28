# 028_oakTrees.py — empty container collection for oak trees

**Path:** `folio-2025/scripts/blender_world_steps/steps/028_oakTrees.py`
**Lines:** 12
**Adds:** 0 objects to collection `oakTrees`
**Group:** [04-trees](../04-trees.md)

## What it does (code-level)

Creates the `oakTrees` collection with `bpy.data.collections.new('oakTrees')` and links it to the scene root. Adds zero objects. Prints "added 0 objects to oakTrees".

## Key data

- **Datablocks referenced:** none
- **Materials assigned:** none
- **Modifiers added:** none
- **Custom properties:** none
- **Object types breakdown:** 0 MESH, 0 EMPTY
- **Parent collection:** `oakTrees` (scene root)

## Technique / recipe

Pure stub. The collection is a named container bucket. Sub-collections (`archives.001`, `visual.004`, `references.002`) and the actual tree instances (`oakTrees.001` from script 136) are added by later scripts and parented here in `999_finalize.py`. This script just claims the name early in the run order so every other script can reference `oakTrees` by name without missing-collection errors.

## Connections

- **Reads from:** nothing
- **Read by:** `999_finalize.py` (parents sub-collections under `oakTrees`)
- **Depends on:** `013_collections.py` (general collection skeleton; but oakTrees is self-created here)
- **Depended on by:** `136_oakTrees.001.py`, reference/visual/archive scripts in 14-reference-hidden

## Notable code patterns

Minimal idempotent guard: `bpy.data.collections.get('oakTrees') or bpy.data.collections.new('oakTrees')`. All three tree-parent scripts (028, 032, 036) are exact clones of this 12-line pattern with the name swapped.
