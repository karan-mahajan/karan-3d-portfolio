# 036_cherryTrees.py — empty container collection for cherry trees

**Path:** `folio-2025/scripts/blender_world_steps/steps/036_cherryTrees.py`
**Lines:** 12
**Adds:** 0 objects to collection `cherryTrees`
**Group:** [04-trees](../04-trees.md)

## What it does (code-level)

Creates the `cherryTrees` collection and links it to the scene root. Adds zero objects. Identical pattern to `028_oakTrees.py`.

## Key data

- **Datablocks referenced:** none
- **Materials assigned:** none
- **Modifiers added:** none
- **Object types breakdown:** 0 MESH, 0 EMPTY
- **Parent collection:** `cherryTrees` (scene root)

## Technique / recipe

Same stub-container pattern as 028/032. `cherryTrees.001` (20 instances, script 135) populates the actual placed trees later.

## Connections

- **Reads from:** nothing
- **Depended on by:** `135_cherryTrees.001.py`, reference/visual/archive scripts in 14-reference-hidden

## Notable code patterns

See [028-oakTrees.md](028-oakTrees.md).
