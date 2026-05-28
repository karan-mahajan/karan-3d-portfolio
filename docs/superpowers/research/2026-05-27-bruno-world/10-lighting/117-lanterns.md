# 117_lanterns.py — 17 world-scattered lanterns via template-stack instancing

**Path:** `folio-2025/scripts/blender_world_steps/steps/117_lanterns.py`
**Lines:** 692
**Adds:** 51 objects (34 MESH, 17 EMPTY) to collection `lanterns`
**Group:** [10-lighting](../10-lighting.md)

## What it does (code-level)

Creates `lanterns` collection (also linked into `scene.collection.children` — top-level world). Adds **17 lanterns**, each composed of 3 objects: `base.NNN` MESH + `light.NNN` MESH + `lantern.NNN` EMPTY anchor. Total 51 objects.

**Each lantern's structure:**

| Role | Object | Type | Mesh |
|---|---|---|---|
| Body | `base[.NNN]` | MESH | `Cube.022` (shared datablock) |
| Emissive panel | `light[.NNN]` | MESH | `Cube.011` (shared datablock) |
| Placement anchor | `lantern[.NNN]` | EMPTY/PLAIN_AXES | — |

**Template-stack pattern (the critical detail):**
- All 17 `base.NNN` meshes share the SAME hardcoded location `(62.65, -45.66, 1.955)` — the staging coordinate
- All 17 `light.NNN` meshes share the SAME hardcoded location `(62.65, -45.66, 1.955)` — same staging coordinate
- Only the 17 `lantern.NNN` EMPTYs carry unique placement positions

**17 lantern placement positions (the EMPTY anchors, scattered across the world):**

| Anchor | Location (x, y, z) | Notes |
|---|---|---|
| `lantern` | (60.18, -47.14, 1.95) | East-south near bonfire, elevated |
| `lantern.001` | (64.86, -53.29, 0.48) | East-south, near-ground |
| `lantern.002` | (67.87, -63.00, 0.50) | Far east-south, has rotZ=-1.106 (~63°) |
| `lantern.003` | (73.80, -10.04, 0.51) | Far east, mid-y |
| `lantern.004` | (50.80, -21.38, 0.51) | East-mid |
| `lantern.005` | (33.52, -40.12, 0.52) | Central-south |
| `lantern.006` | (21.03, -54.36, 0.51) | South-central |
| `lantern.007` | (23.06, -31.85, 1.97) | South-central, elevated |
| `lantern.008` | (-0.24, -38.60, 0.51) | Center-south |
| `lantern.009` | (30.21, -12.64, 0.50) | Central |
| `lantern.010` | (16.40, -10.96, 0.52) | Central |
| `lantern.011` | (73.99, 24.29, 1.25) | Far east, north |
| `lantern.012` | (40.94, 33.89, 0.52) | East-north |
| `lantern.013` | (-56.81, 66.64, 0.47) | Far west-north |
| `lantern.014` | (-64.39, -26.71, 0.37) | Far west-south |
| `lantern.015` | (46.66, -31.22, 0.51) | East-central |
| `lantern.016` | (53.23, -39.91, 1.26) | East-south, elevated |

**Numbering quirk:** `base.015` is skipped — Bruno uses `base.014`, `base.016`, `base.017` (because `base.015` is already used by `089_bonfire.py` as the skull mesh, and Blender object names are global).

## Key data

- **Datablocks referenced:** meshes `Cube.022` (lantern body, shared by all 17 instances), `Cube.011` (emissive panel, shared by all 17). No node groups.
- **Materials assigned:** via mesh datablock — `palette` (on bodies), `emissiveOrangeRadialGradient` (on emissive panels)
- **Modifiers added:** **none** on any object — unlike pole-lights, lanterns don't get Smooth-by-Angle. The mesh data is pre-smoothed.
- **Custom properties:** none
- **World positions of key anchors:** see 17-row table above
- **Object types breakdown:** 34 MESH (17 base + 17 light), 17 EMPTY
- **Parent collection:** `lanterns` (also linked directly into scene root via `scene.collection.children`)

## Technique / recipe

**Template-stack instancing — Bruno's signature pattern for world-scattered identical props:**

1. **Two shared mesh datablocks** (`Cube.022` body + `Cube.011` emissive). All 17 lanterns reference the same two meshes.
2. **17 mesh OBJECTS per mesh datablock** (so 34 mesh objects total). Each lantern needs its own object pair because Blender objects carry the transform; the data is shared via the mesh reference.
3. **All 34 mesh objects are stacked at the staging coordinate** (62.65, -45.66, 1.955). In the .blend they pile on top of each other. Bruno relies on the runtime to reposition them.
4. **17 `lantern.NNN` EMPTYs at the real world positions** — the runtime reads each EMPTY's transform and applies it to the matching base/light pair (via name suffix matching).

**Why this odd structure?** Bruno's runtime appears to do **name-suffix instancing**: it iterates `lantern.NNN`, finds the matching `base.NNN` + `light.NNN`, parents them under that empty (or copies the transform), and renders 17 separate lantern objects at the 17 anchor positions.

Alternative interpretation: the meshes are **template references**, and the runtime spawns N visible mesh-instances using the empty as the local transform. The base/light mesh objects in Blender would never render directly — their staging position is irrelevant.

Either way, the **.blend file is NOT the rendered state**. Bruno's runtime synthesizes the final scene from `lantern.NNN` anchors + the two shared meshes.

**17 lantern positions show clear placement strategy:**
- **East cluster** (lanterns .000-.004, .015, .016): around the bonfire/landing zone (x ∈ [50, 75], y ∈ [-65, -20]) — densest
- **Central scatter** (.005-.010): the inner playable area (x ∈ [-1, 33], y ∈ [-54, -10])
- **Far outliers** (.013, .014): far west corners (x ∈ [-64, -56])
- **North-east** (.011, .012): far east-north (x ∈ [40, 75], y ∈ [24, 34])
- **Z values cluster around 0.5m** (ground level) with a few at 1.25-1.97m (elevated — likely on building roofs or platforms)

**No smoothing modifiers** — unlike the pole lights (118) which add `Smooth by Angle.003`, lanterns are crisp-edged. This is a deliberate aesthetic choice: lanterns look more "hand-made tin-box" with hard edges; pole lights look more "manufactured streetlamp" with soft edges.

## Connections

- **Reads from:** `005_meshes_*.py` (`Cube.022`, `Cube.011`)
- **Read by:** `999_finalize.py` (does NOT re-parent lanterns under a zone — they're top-level world props, linked directly into `scene.collection`)
- **Depends on:** `013_collections.py` (collection skeleton), `005_meshes_*.py` (meshes)
- **Depended on by:** runtime mesh-instancing system + emissive renderer

## Notable code patterns

- **`scene.collection.children.link(coll)`** — first appearance in batch 4 of explicit top-level linking. Most prop scripts only `coll.objects.link(ob)` per object; this script ALSO links the collection itself to the scene root. Reason: lanterns are world-wide, not parented under a zone (unlike furniture which finalize parents under specific section roots).
- **Shared mesh datablock + per-instance mesh object** — 17 mesh objects all reference `Cube.022`, but Blender treats them as 17 distinct objects with 17 distinct transforms. Memory cost is N objects × Object.transform (small) + 1 shared mesh data (large).
- **Template-stack at fixed staging** (62.65, -45.66) — the staging position is near lantern.000's actual world position (60.18, -47.14). This suggests the staging position was once a placement (lantern.000's original spot) that Bruno then froze as the staging anchor for all instances after switching to runtime-driven placement.
- **`base.015` skip** — global name collision with `base.015` in 089_bonfire.py. Bruno's export pipeline detects existing names and increments past them.
- **`empty_display_size = 1.0`** on all 17 lantern empties — they show as 1m-radius axes gizmos in Blender (visible reference points for the artist).
- **Rotation rare:** only `lantern.002` has a non-zero rotZ (-1.106 rad, ~-63°) and `lantern.001` has slight X+Y tilts. Most lanterns are axis-aligned — Bruno didn't bother rotating most of them because the lantern silhouette is rotationally symmetric.
