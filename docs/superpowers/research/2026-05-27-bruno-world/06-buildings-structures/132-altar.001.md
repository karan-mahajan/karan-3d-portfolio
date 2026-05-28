# 132_altar.001.py — map-portal emissive plane at the behindTheScene location

**Path:** `folio-2025/scripts/blender_world_steps/steps/132_altar.001.py`
**Lines:** 22
**Adds:** 1 object to collection `EXCLUDED`
**Group:** [06-buildings-structures](../06-buildings-structures.md)

## What it does (code-level)

Creates or retrieves collection `EXCLUDED` and links it to the scene root. Adds 1 MESH object:

- `altarEmissive` — mesh `Plane.004`, at **(52.75, 11.10, 0.0)**, scale=(3.844, 3.844, 3.844). Material assigned via mesh datablock: `mapPortal`.

World position (52.75, 11.10) is the **behindTheScene zone center**, not the altar zone center (75.34, 27.95).

## Key data

- **Datablocks referenced:** mesh `Plane.004`
- **Materials assigned:** `mapPortal` (via mesh datablock)
- **Modifiers added:** none
- **World position:** **(52.75, 11.10)** — behindTheScene location
- **Scale:** 3.844 uniform → effective footprint ≈ 7.69m × 7.69m (plane default 2m × 2m × scale)
- **Object types breakdown:** 1 MESH, 0 EMPTY
- **Parent collection:** `EXCLUDED`

## Technique / recipe

This script places a flat emissive plane named `altarEmissive` at the **wrong** (behindTheScene) location. The companion script `133_behindTheScene.001.py` places `behindTheSceneEmissive` at the altar location. The two scripts are deliberately cross-positioned.

The `EXCLUDED` collection is a special Bruno convention: objects here exist in the Blender scene but are excluded from the main scene rendering. They are minimap-only markers — the runtime minimap renderer renders this collection separately (probably with a different camera or layer) to draw zone icons on the 2D map overlay.

The `mapPortal` material is the visual icon style for this emissive marker. "Portal" may refer to the visual appearance (a glowing ring) or a runtime route mechanic. The cross-placement (altar name at behindTheScene location, vice versa) may be intentional to swap the icons' map positions for UX clarity, or it could be an authoring error that was retained because the runtime references objects by name rather than position.

Scale 3.844 gives a ≈7.7m diameter map marker — large enough to be visible on the minimap at world scale.

## Connections

- **Reads from:** `004_materials.py` (`mapPortal`), `005_meshes_*.py` (`Plane.004`)
- **Read by:** runtime minimap system (renders EXCLUDED collection separately); `999_finalize.py`
- **Depends on:** `013_collections.py`
- **Depended on by:** minimap overlay; companion script `133_behindTheScene.001.py` (mirrored pattern)

## Notable code patterns

The `EXCLUDED` collection name is a Blender scene-level exclude flag convention: Bruno excludes it from the main viewport/render but includes it for the minimap camera layer. This avoids minimap markers appearing in the 3D world view while still making them available to a secondary render pass.

Name/position swap between 132 and 133 is the most intentional-seeming quirk in this group — if it were an error, the minimap would show both icons in the wrong locations. One possibility: the runtime lookups go `altarEmissive → mapPortal icon` and `behindTheSceneEmissive → mapAltar icon`, with the position being the actual map position, so the names encode the icon *style* and the positions encode the *location* — making the naming a style tag, not a location tag.
