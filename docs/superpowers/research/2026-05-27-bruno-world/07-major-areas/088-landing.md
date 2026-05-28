# 088_landing.py — spawn-zone root: roofs + cuboid colliders + zone anchors

**Path:** `folio-2025/scripts/blender_world_steps/steps/088_landing.py`
**Lines:** 283
**Adds:** 13 objects (2 MESH, 11 EMPTY) to collection `landing`
**Group:** [07-major-areas](../07-major-areas.md)

## What it does (code-level)

Creates `landing` collection (the spawn zone / hub) and adds 13 objects: 2 angled roof meshes + 7 cuboid-collider empties + 4 zone-anchor empties.

**Meshes** (both with `Smooth by Angle.001` GN modifier, Input_1≈0.9145 rad ≈ 52.4°):
| Object | Mesh | Location | Rotation (rad) | Scale |
|---|---|---|---|---|
| `physicalFixed.009` | `roof.001` | (46.15, -30.79, 3.27) | (0.494, ~0, -0.346) | (1,1,1) |
| `physicalFixed.003` | `roof.002` | (44.57, -31.77, 1.51) | (0.494, ~0, -0.354) | (1.088,1.088,1.088) |

Both roofs are tilted ≈28° around X (0.494 rad), slightly twisted around Z (-20°), and offset along Y by 1m and Z by 1.76m — these are the **stacked roof sections of the spawn kiosk** (one large above, one smaller below acting as eaves).

**Cuboid empties** (7× empty_display_type=CUBE, varying scales — these are collision/trigger boxes):
| Empty | Location | Scale | Rotation (rad) |
|---|---|---|---|
| `cuboid.018` | (44.44, -31.65, 1.75) | (3.11, 0.53, 3.46) | (~0, ~0, 0.423) |
| `cuboid.012` | (54.65, -30.21, -0.09) | (4.08, 2.42, 0.52) | (0.18, ~0, 0.323) |
| `cuboid.010` | (56.40, -47.05, 1.47) | (0.68, 0.68, 4.41) | (-0.27, 0.19, -0.10) |
| `cuboid.082` | (42.51, -41.47, 0.87) | (0.34, 0.44, 1.44) | (~0, ~0, 0.436) |
| `cuboid.083` | (42.81, -41.33, 1.13) | (0.99, 0.44, 0.92) | (~0, ~0, 0.436) |
| `cuboid.084` | (44.29, -40.64, 0.87) | (1.76, 0.44, 1.44) | (~0, ~0, 0.436) |
| `cuboid.085` | (45.72, -39.97, 0.33) | (1.22, 0.44, 0.36) | (~0, ~0, 0.436) |
| `cuboid.086` | (45.72, -39.97, 1.00) | (0.44, 0.44, 1.15) | (~0, ~0, 0.436) |

(8 cuboids total — 5 of them at y≈-40 share rotation 0.436 rad ≈ 25° around Z, forming a tight cluster — probably a "physical fixed" wall or fence structure near the kiosk.)

**Zone anchors** (4 empties — canonical zone-root pattern):
| Empty | Type | Location | Scale |
|---|---|---|---|
| `landing` (root) | PLAIN_AXES | (49.25, -38.52, 3.27) | (1,1,1) |
| `refZoneBounding` | CIRCLE | (45.61, -36.44, 3.27) | (17.23)³ |
| `refZoneFrustum` | CIRCLE | (49.25, -38.52, 3.27) | (13.23)³ |

(Note: NO `refStart` or `refInteractivePoint` here — spawn zone uses `controls`/`title.001`/`kiosk`/`bonfire` child collections for those.)

## Key data

- **Datablocks referenced:** meshes `roof.001`, `roof.002`, node-group `Smooth by Angle.001`
- **Materials assigned:** via mesh datablocks — `palette` on the roofs (the group-index claim of `stylizedMap` material is not visible in this script's bindings; if applied, it's on a child mesh in 090/091/092)
- **Modifiers added:** 2× `Smooth by Angle.001` (NODES, Input_1=0.9145 rad ≈ 52.4°) — note this is `.001` here, not `.003` as on most other scripts. Bruno uses different smoothing thresholds in different zones
- **Custom properties:** none
- **World positions of key anchors:**
  - **Landing zone origin:** (49.25, -38.52, 3.27) — far north-east of map origin (the spawn hub)
  - **Bounding center:** (45.61, -36.44, 3.27) radius ≈17.23m
  - **Roof apex cluster:** around (45, -31, 1.5-3.3) — the kiosk roofs are ~7m north of bounding center
  - **Cuboid cluster** at y≈-40, x≈42-46 — wall/fence structures defining the kiosk footprint
- **Object types breakdown:** 2 MESH, 11 EMPTY
- **Parent collection:** `landing` (re-parented under `areas/` by finalize)

## Technique / recipe

The landing zone is **architectural-heavy** — it's the spawn hub, so it has visible physical structures (roofs) right at the root level rather than only anchors. Pattern:

1. **Roofs are MESH children of root, not of `kiosk/`** — Bruno keeps the most-visible structural pieces in the root collection so they always render even when child collections might be deferred/culled.
2. **`physicalFixed.NNN` naming** — these are runtime-static physics colliders. The mesh form is `physicalFixed.NNN` with a `roof.NNN` mesh datablock. Suggests Bruno's runtime reads "physicalFixed*" objects to register them as Rapier/Cannon static rigidbodies.
3. **Cuboid-empties as collider primitives** — 8 CUBE empties with non-uniform scale = box colliders. The scale gives the half-extents; the rotation gives the orientation. No mesh; the runtime spawns physics boxes at these transforms.
4. **Yawed cluster of 5 cuboids at z=0.87-1.13** (cuboid.082-086) — same Z-rotation of 0.436 rad, varying X-scales (0.34, 0.99, 1.76, 1.22, 0.44) — looks like wall segments laid out in a row, forming a fence-line.
5. **Roof tilt 0.494 rad ≈ 28.3°** — gives the kiosk roofs a steep pitched-shingle look. Both roofs share the angle; the smaller (physicalFixed.003) is scaled up 8.8% and offset slightly to act as an eaves layer above the larger.

## Connections

- **Reads from:** `005_meshes_*.py` (`roof.001`, `roof.002`), `003_node_groups.py` (`Smooth by Angle.001`), `004_materials.py` (palette on roofs)
- **Read by:** `999_finalize.py` (parents 4 landing child collections — title.001 (092), controls (090), kiosk (091), bonfire (089) — under `landing/`; re-parents `landing/` under `areas/`)
- **Depends on:** `044_areas.py`, `005_meshes_*.py`, `003_node_groups.py`
- **Depended on by:** `089_bonfire.py`, `090_controls.py`, `091_kiosk.py`, `092_title.001.py`

## Notable code patterns

- **Mesh objects named `physicalFixed.NNN`** but mesh datablocks named `roof.NNN` — the object name encodes the runtime role (static collider), the mesh name encodes the asset type (roof). This decouples gameplay metadata from asset reuse.
- **8 CUBE empties** as collider primitives — Bruno's preferred way to add invisible box colliders without authoring mesh geometry. Scale carries half-extents (note: scale 0.5 on a default 1m cube gives a 0.5m total = 0.25m half-extent, so Bruno's "scale = half-extent" only works if the cube empty's default display is 1m. The `empty_display_size = 0.5` setting puts the wireframe at 0.5m for visual clarity in viewport).
- **No `refInteractivePoint` here** — landing's interactivity is handled by the `controls/` and `kiosk/` child collections, not zone-level.
- **Different `Smooth by Angle` index (.001 vs .003)** — Bruno has 3+ variants of the auto-smooth GN; `.003` is the universal default (45°-55°), `.001` here uses 52.4°. The variants likely have different node-group internals (e.g., different sharpness on edges marked as creases).
