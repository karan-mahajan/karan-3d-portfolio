# 000_init.py — wipe the scene clean before rebuilding

**Path:** `folio-2025/scripts/blender_world_steps/steps/000_init.py`
**Lines:** 20
**Adds:** 0 objects — destructive operation that empties the .blend file
**Group:** [01-foundation](../01-foundation.md)

## What it does (code-level)

The whole script is a single `run()` function that iterates a tuple of `bpy.data.*` collections and tries to `coll.remove(item)` for every datablock it finds. Order of wipe (from the tuple):

1. `bpy.data.objects` — scene objects
2. `bpy.data.meshes` — mesh datablocks
3. `bpy.data.materials` — material datablocks
4. `bpy.data.curves` — curve / font datablocks
5. `bpy.data.armatures` — bone hierarchies
6. `bpy.data.lights` — light datablocks
7. `bpy.data.cameras` — camera datablocks
8. `bpy.data.images` — image / texture datablocks
9. `bpy.data.node_groups` — geometry-nodes / shader / compositor groups
10. `bpy.data.collections` — collection hierarchy
11. `bpy.data.worlds` — world (environment) datablocks
12. `bpy.data.metaballs` (only if attribute exists)
13. `bpy.data.linestyles` (only if attribute exists)
14. `bpy.data.actions` (only if attribute exists)
15. `bpy.data.texts` (only if attribute exists)

Each removal is wrapped in `try/except` and silently swallows failures. Print banners `[01_init] wiping scene` and `[01_init] done` bookend the work (note the script is filed as `000` but the print tag says `01_init` — a tiny inconsistency).

`list(coll)` is used to snapshot the collection before iterating, so the live `.remove()` calls don't mutate the iterator.

## Key data

- **Datablocks referenced**: none — only deletes
- **Materials assigned**: n/a
- **Modifiers added**: n/a
- **Custom properties**: n/a
- **World positions of key anchors**: n/a
- **Object types breakdown**: 0
- **Parent collection**: n/a — scene root is left intact (only its children are nuked)

## Technique / recipe

The "blank slate" pattern for a script-driven .blend build:

- Don't try to selectively patch — just wipe every datablock category and let the next 141 scripts rebuild from scratch.
- Iterate `bpy.data` collections with `list()` to avoid the "modify-while-iterating" RNA crash.
- Wrap removals in `try/except` because some datablocks (e.g., the default world, the scene's own master collection) can refuse removal and would otherwise abort the script.
- Use `hasattr(bpy.data, 'xxx')` guards for collections that may not exist in all Blender versions (`metaballs`, `linestyles`, `actions`, `texts`). This makes the script cross-version safe.
- Scene and view-layer datablocks are intentionally **not** in the wipe list — Bruno keeps the scene container itself and only clears its contents.

The script is fully **idempotent**: running it on an already-empty file is a no-op (every `for item in list(coll)` loop is empty).

## Connections

- **Reads from**: nothing
- **Read by**: no later script reads its output directly — but every subsequent script (001 → 999) relies on starting from a clean .blend
- **Depends on**: nothing
- **Depended on by**: the entire pipeline. If 000 didn't wipe first, re-running the build would dup every datablock under suffixed names (`Plane.134.001`, `palette.001`, etc.) and break every lookup that follows

## Notable code patterns

- **Variable-version safety via `hasattr`**: lets the same script work on a Blender 3.x file (no `metaballs` attr in older minors) and 4.x without branching.
- **Tuple-of-collections + nested loop**: a compact way to wipe many categories without repeating the same `try/except` block 15 times.
- **Silent except**: appropriate here because the goal is "best effort empty"; any datablock that refuses removal can just be ignored and the rest of the wipe proceeds.
- **CLI entrypoint**: `if __name__ == '__main__': run()` — every step script in Bruno's pipeline ends with this same idiom, so they're individually runnable from `blender --python <script>.py` for debugging.
