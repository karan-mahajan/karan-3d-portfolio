# 118_poleLights.py — 13 streetlamp-style pole lights via template-stack instancing with smoothing

**Path:** `folio-2025/scripts/blender_world_steps/steps/118_poleLights.py`
**Lines:** 1494
**Adds:** 39 objects (26 MESH, 13 EMPTY) to collection `poleLights`
**Group:** [10-lighting](../10-lighting.md)

## What it does (code-level)

Creates `poleLights` collection (linked to scene root). Adds **13 pole lights**, each a triplet: `glass.NNN` MESH + `body.NNN` MESH + `poleLight.NNN` EMPTY anchor.

**Each pole light's structure:**

| Role | Object | Type | Mesh | Modifier |
|---|---|---|---|---|
| Glass (emissive) | `glass.NNN` | MESH | `Cube.054` (shared) | `Smooth by Angle.003` (Input_1=0.524 rad ≈30°) |
| Pole body | `body.NNN` | MESH | `Cube.052` (shared) | `Smooth by Angle.003` (Input_1=0.524 rad ≈30°) |
| Placement anchor | `poleLight.NNN` | EMPTY/PLAIN_AXES | — | — |

**Template-stack pattern (same as 117_lanterns, with smoothing added):**
- All 13 `glass.NNN` MESHes share staging position `(36.12, -40.54, 2.799)` — z=2.799 is taller than lanterns (the glass sits above the pole at lamp-height)
- All 13 `body.NNN` MESHes share staging position `(36.12, -40.54, 1.749)` — z=1.749 is the mid-pole height
- The **vertical offset between glass and body (Δz=1.05m)** is the only differentiation; runtime preserves this when applying the anchor's transform
- All 13 `poleLight.NNN` EMPTYs at unique world positions, all at z=1.749 (matches body staging z)

**13 pole-light placement positions:**

| Anchor | Location (x, y, z) | Notes |
|---|---|---|
| `poleLight.001` | (39.37, -40.58, 1.749) | East, near landing |
| `poleLight.002` | (48.29, -28.06, 1.749) | East-central |
| `poleLight.003` | (65.58, -21.43, 1.749) | Far east |
| `poleLight.004` | (10.94, -26.18, 1.749) | Center |
| `poleLight.005` | (19.45, -6.62, 1.749) | Center-north |
| `poleLight.006` | (50.39, 30.11, 1.749) | East-north |
| `poleLight.007` | (62.94, 3.98, 1.749) | Far east, mid |
| `poleLight.008` | (80.51, -6.53, 1.749) | Easternmost |
| `poleLight.009` | (37.40, -54.57, 1.749) | South |
| `poleLight.010` | (1.07, -14.12, 1.749) | Center-south |
| `poleLight.011` | (32.14, 12.49, 1.749) | Central-north |
| `poleLight.012` | (21.03, 6.55, 1.749) | Central |
| `poleLight.013` | (9.32, -54.16, 1.749) | South-west |

(`poleLight.000` is not used — anchors run .001 → .013)

## Key data

- **Datablocks referenced:** meshes `Cube.054` (glass, shared by 13), `Cube.052` (body, shared by 13); node-group `Smooth by Angle.003`
- **Materials assigned:** via mesh datablock — `palette` (on bodies), `emissiveOrangeRadialGradient` (on glass — same emissive amber as lanterns)
- **Modifiers added:** 26× `Smooth by Angle.003` (NODES, Input_1=0.524 rad ≈30°) — every mesh gets one
- **Custom properties:** none
- **World positions of key anchors:** see 13-row table above. **All anchors at exactly z=1.749** (with tiny float-precision variation) — pole lights stand on flat ground.
- **Object types breakdown:** 26 MESH (13 glass + 13 body), 13 EMPTY
- **Parent collection:** `poleLights` (also linked into scene root)

## Technique / recipe

**Template-stack instancing with vertical separation:**

1. **Two shared mesh datablocks** (`Cube.054` glass + `Cube.052` body). All 13 pole lights reuse them.
2. **26 mesh objects total** (13 glass + 13 body), all 26 stacked at the staging coordinate but with the glass mesh at z=2.799 and the body mesh at z=1.749 — preserving the **1.05m vertical offset** between glass and body. The runtime applies the anchor's transform, but presumably as an offset from a common origin, so the relative Δz is preserved.
3. **13 placement EMPTYs** at world positions, all at z=1.749 (same as the body staging z) — strongly suggesting the runtime treats the body mesh's staging position as the canonical anchor reference point.
4. **Every mesh gets Smooth-by-Angle.003** with a 30° threshold — softens the cylinder/cube geometry of the lamp body for a more "manufactured streetlamp" look. (Contrast: lanterns 117 have no smoothing modifier — they're crisp tin-box shapes.)

**Why all anchors at z=1.749 (and no rotation)?** Pole lights are **vertical, axis-aligned, and ground-mounted**. They look identical from any angle (rotationally symmetric around Z), so Bruno never bothered rotating them. The Z height is a constant because all 13 sit on flat ground (the heightmap's average level around the playable zone).

**Placement strategy — wayfinding pattern:**
- 13 pole lights cover a wider geographic range than lanterns (lanterns: 17 scattered; pole-lights: 13 along corridors)
- `poleLight.001`, `.009`, `.013` form a south-edge row (y ≈ -40 to -54)
- `poleLight.002`, `.004`, `.010`, `.011`, `.012` form a central row (y ≈ -28 to 12)
- `poleLight.003`, `.005`, `.006`, `.007`, `.008` mark the east corridor (x ≈ 48-80)
- This is **path-aligned lighting**: pole lights mark major routes between zones, while lanterns provide ambient cluster light.

**Smooth-by-Angle 30° threshold** — same as lightGenerators (050), tighter than the default 55° on most other props. This keeps the pole's silhouette crisp at the vertical edges while still smoothing the lamp-head curves.

## Connections

- **Reads from:** `005_meshes_*.py` (`Cube.054`, `Cube.052`), `003_node_groups.py` (`Smooth by Angle.003`)
- **Read by:** `999_finalize.py` (NOT re-parented under a zone — top-level world prop)
- **Depends on:** `013_collections.py`, `005_meshes_*.py`
- **Depended on by:** runtime emissive renderer + mesh-instancing system

## Notable code patterns

- **Same template-stack pattern as lanterns (117), with two key differences:**
  1. Smoothing modifiers added (lanterns don't have any) — gives pole lights a softer, more manufactured look vs lanterns' crisp tin-box style.
  2. Glass and body authored at different staging Z (Δz=1.05m) — preserves the vertical structure of the lamp (head above pole) without needing parenting in the .blend.
- **`use_pin_to_last = True`** on every Smooth-by-Angle modifier — keeps smoothing as the last operation in the stack (post-any-other-modifier).
- **All 26 mesh modifiers carry identical params** (Input_1=0.5236, Socket_1=False, _use_attribute=0, attribute_name='') — Bruno's exporter writes the modifier config verbatim per object, no abstraction.
- **`scene.collection.children.link(coll)`** — same top-level scene linking as lanterns. Pole lights are not zone-parented.
- **`poleLight.000` skipped** — numbering starts at `.001`. Pole lights don't use the unsuffixed name `poleLight` (whereas lanterns DO use unsuffixed `lantern` for the first instance). Inconsistency in Bruno's naming between the two scripts.
- **Z-height 1.749m for body mesh** = lamp anchor at chest height when a pole light "spawns". The mesh extends upward from the anchor (body height ~3.5m total based on the cube primitive scale, glass on top at +1.05m offset).
- **No `mass` or `physicalDynamic` props** — pole lights are static world props. Players can't push them.
