# 129_easter.py — empty parent collection for the egg

**Path:** `folio-2025/scripts/blender_world_steps/steps/129_easter.py`
**Lines:** 12
**Adds:** 0 objects to collection `easter`
**Group:** [13-food-misc-fx](../13-food-misc-fx.md)

## What it does (code-level)
Tiny boilerplate script:
1. Gets or creates collection `easter`.
2. Links it into the scene's root collection (`bpy.context.scene.collection.children.link(coll)`) if not already a child.
3. Prints "added 0 objects to easter."

That's it — no objects added. This script exists purely to **register `easter` as a top-level scene collection** so that subsequent scripts (like `130_egg.py`) can hang their objects under it.

## Key data
- **Datablocks referenced**: none.
- **Materials assigned**: none.
- **Modifiers added**: none.
- **Custom properties**: none.
- **World positions**: N/A.
- **Object types breakdown**: 0 objects.
- **Parent collection**: `easter` itself becomes a scene-root collection here.

## Technique / recipe
- **"Skeleton collection" pattern**: when an upcoming script (130) needs to add objects to a collection, the collection must exist AND be linked to the scene. This script does only that linkage — separates the collection-creation concern from the object-addition concern, so each script stays narrowly responsible.
- Sets up the parent for `egg` (130) to attach its 2 visible meshes.

## Connections
- **Reads from**: nothing.
- **Read by**: `130_egg.py` (adds `egg` + `beams` meshes under this collection at runtime), `999_finalize.py` (sets view-layer EXCLUDE on `easter`).
- **Depends on**: `013_collections.py` (collection skeleton).
- **Depended on by**: 130, 999.

## Notable code patterns
- **Why the link guard?** `if coll.name not in {c.name for c in bpy.context.scene.collection.children}` — idempotent guard against re-linking. Most other scripts (like 079_cookie) also create their own collection but only check `bpy.data.collections.get(...)`; this script ALSO links to scene root because it's a top-level collection that wasn't part of 013's skeleton.
- Some other scripts also explicitly link to scene root: `138_tornado.py`, `139_whispersForbiddenAreas.py`, `127_archives.003.py`, `131_map.py`. Pattern: scripts that create a NEW top-level collection (not pre-built by 013) link it explicitly.
- Compare to `130_egg.py`: that script does NOT explicitly link `egg` collection — because finalize will parent `egg` under `easter`, which IS scene-linked here.
