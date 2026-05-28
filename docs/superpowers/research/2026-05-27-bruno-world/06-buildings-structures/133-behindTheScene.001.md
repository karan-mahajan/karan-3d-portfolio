# 133_behindTheScene.001.py — map-altar emissive plane at the altar location

**Path:** `folio-2025/scripts/blender_world_steps/steps/133_behindTheScene.001.py`
**Lines:** 21
**Adds:** 1 object to collection `EXCLUDED`
**Group:** [06-buildings-structures](../06-buildings-structures.md)

## What it does (code-level)

Retrieves collection `EXCLUDED` (already created by `132_altar.001.py`). Adds 1 MESH object:

- `behindTheSceneEmissive` — mesh `Plane.006`, at **(75.34, 27.94, 0.0)**, scale=(3.104, 3.104, 3.104). Material assigned via mesh datablock: `mapAltar`.

World position (75.34, 27.94) is the **altar zone center**, not the behindTheScene zone center (52.46, 11.96).

## Key data

- **Datablocks referenced:** mesh `Plane.006`
- **Materials assigned:** `mapAltar` (via mesh datablock)
- **Modifiers added:** none
- **World position:** **(75.34, 27.94)** — altar location (compare: altar root at 75.34, 27.95 in 048_altar.py — Y differs by 0.01m, floating-point precision)
- **Scale:** 3.104 uniform → effective footprint ≈ 6.21m × 6.21m
- **Object types breakdown:** 1 MESH, 0 EMPTY
- **Parent collection:** `EXCLUDED`

## Technique / recipe

Mirror of `132_altar.001.py`. Where 132 placed `altarEmissive` (mapPortal material) at the behindTheScene location, this script places `behindTheSceneEmissive` (mapAltar material) at the altar location.

Both scripts use distinct mesh datablocks (`Plane.004` vs `Plane.006`) and distinct materials (`mapPortal` vs `mapAltar`), both added to the same `EXCLUDED` collection. The minimap renderer picks up both from `EXCLUDED` and renders them as 2D icons on the map.

Scale 3.104 (≈6.2m diameter) is smaller than the 132 marker (3.844, ≈7.7m). The two icons have different visual sizes on the minimap — perhaps "altar" is a larger/more prominent landmark than "behindTheScene" or vice versa, and the scales encode relative map icon prominence.

The Y alignment to the altar root (75.34, 27.94 vs. 75.34, 27.95 in 048) is a 0.01m float epsilon — these are effectively co-located. This precision confirms the cross-placement is intentional: Bruno manually set the position to match the altar center, not an accident.

## Connections

- **Reads from:** `004_materials.py` (`mapAltar`), `005_meshes_*.py` (`Plane.006`)
- **Read by:** runtime minimap system; `999_finalize.py`
- **Depends on:** `013_collections.py`; `132_altar.001.py` (must run first to create `EXCLUDED` collection)
- **Depended on by:** minimap overlay; see also `132_altar.001.py`

## Notable code patterns

The 21-line script is one line shorter than 132's 22 lines — the only difference is that 133 omits the collection creation block (since `EXCLUDED` already exists after 132 runs). This ordering dependency is implicit: Bruno's build scripts are numbered sequentially and run in order, so 132 always precedes 133.

Together 132 + 133 establish the full minimap icon pattern for Bruno's world: two cross-positioned EXCLUDED-collection plane meshes with zone-specific emissive materials, scaled to indicate relative map prominence. Any new zone wanting a minimap marker would follow this two-script pattern.
