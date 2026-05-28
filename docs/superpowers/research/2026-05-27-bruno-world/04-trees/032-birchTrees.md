# 032_birchTrees.py — empty container collection for birch trees

**Path:** `folio-2025/scripts/blender_world_steps/steps/032_birchTrees.py`
**Lines:** 12
**Adds:** 0 objects to collection `birchTrees`
**Group:** [04-trees](../04-trees.md)

## What it does (code-level)

Creates the `birchTrees` collection and links it to the scene root. Adds zero objects. Identical pattern to `028_oakTrees.py` with name swapped.

## Key data

- **Datablocks referenced:** none
- **Materials assigned:** none
- **Modifiers added:** none
- **Object types breakdown:** 0 MESH, 0 EMPTY
- **Parent collection:** `birchTrees` (scene root)

## Technique / recipe

Same stub-container pattern as 028. `birchTrees` sub-collections (`archives.002`, `visual.002`, `references`) and instances (`birchTrees.001` from script 134) are populated by later scripts.

## Connections

- **Reads from:** nothing
- **Depended on by:** `134_birchTrees.001.py`, reference/visual/archive scripts in 14-reference-hidden

## Notable code patterns

See [028-oakTrees.md](028-oakTrees.md) — all three tree-parent scripts are clones of the same 12-line pattern.
