# 103_social.py — social-zone root with curved-arc collider chain and zone bounds

**Path:** `folio-2025/scripts/blender_world_steps/steps/103_social.py`
**Lines:** 243
**Adds:** 15 objects (2 MESH, 13 EMPTY) to collection `social`
**Group:** [12-workshop-portfolio-icons](../12-workshop-portfolio-icons.md)

## What it does (code-level)

Creates `social` collection — the **social-zone root**. Parents the icons (104) and statue (105) collections at finalize.

**Anchor structure:**

| Object | Type | Notes |
|---|---|---|
| `physicalFixed.002` | EMPTY/PLAIN_AXES at (25.95, 18.09, 0.0) | Floor physics anchor |
| `refZoneBounding.002` | EMPTY (likely CIRCLE) | Social zone bounds |
| `refZoneFrustum.002` | EMPTY (likely CIRCLE) | Frustum culling region |
| `social` | EMPTY/PLAIN_AXES | Zone root parent (finalize parents `icons` 104 + `statue` 105 here) |
| `hull` | MESH | The social-zone main hull mesh (a small visible structure) |
| `Cube.133` | MESH | The kiosk or pedestal mesh |

**9 collider arc (`cuboid.041` → `cuboid.049`):**

A series of 9 EMPTY/CUBE colliders forming a **curved arc** through space. Each rotated incrementally to follow the curve. Same scale (1.61, 1.61, 0.50) across all 9.

| Cuboid | Location (x, y, z) | rotZ |
|---|---|---|
| `cuboid.041` | (-5.29, 55.36, 0.082) | 0.0 |
| `cuboid.042` | (-6.07, 58.77, 0.082) | 0.449 (26°) |
| `cuboid.043` | (-8.25, 61.51, 0.082) | 0.900 (51°) |
| `cuboid.044` | (-11.42, 63.02, 0.082) | 1.351 (77°) |
| `cuboid.045` | (-14.90, 63.01, 0.082) | 1.798 (103°) |
| `cuboid.046` | (further along arc) | ≈ 2.25 |
| `cuboid.047` | (further) | ≈ 2.69 |
| `cuboid.048` | (further) | ≈ 3.14 |
| `cuboid.049` | (last) | ≈ 3.59 |

The 9 colliders increment by ~0.45 rad (~26°) per step → 9 × 26° = ~230° arc → roughly a **half-circle ring of platform colliders** at z=0.082 (just above ground).

## Key data

- **Datablocks referenced:** mesh `hull`, `Cube.133` (and their underlying mesh data)
- **Materials assigned:** `darkGray`, `palette` (per group .md)
- **Modifiers added:** none
- **Custom properties:** none
- **World positions of key anchors:**
  - 9 collider arc spans (x ∈ [-15, -5], y ∈ [55, 63]) — north-west area
  - physicalFixed.002 at (25.95, 18.09) — far away (east-central)
  - Two visible meshes at unspecified positions
- **Object types breakdown:** 2 MESH, 13 EMPTY (9 cuboid arc + physicalFixed.002 + bounding + frustum + social root)
- **Parent collection:** `social` (re-parented under `areas/`; the `social` EMPTY becomes parent of `icons` 104 + `statue` 105)

## Technique / recipe

**Social zone with curved-arc platform colliders:**

1. **9 cuboid colliders in a half-circle arc** at z=0.082 — Bruno carefully placed each empty to follow a curve through space. Each increments ~26° around a center point, sweeping ~230° total.
2. **All 9 colliders at the same scale** (1.61, 1.61, 0.50) — uniform platform tiles.
3. **Same Z (0.082)** for all 9 — flat curving walkway.
4. **`social` empty as zone parent** at finalize, the `icons` and `statue` collections nest under this.
5. **Zone bounding + frustum** (`refZoneBounding.002`, `refZoneFrustum.002`) — circular zone definition.
6. **Two visible meshes**: `hull` (the small social-zone structure) + `Cube.133` (possibly the kiosk/podium).

**The 9-collider arc** = a curved walkable platform leading to the social-icon display. Bruno wants players to walk along a curving arc to reach the social icons, not a straight path. This is **wayfinding via geometry**.

**The arc's center** can be back-calculated from 2 cuboids' positions and angles — but it's roughly at (cuboid.041 position + the curve sweeping toward the icons in 104). Likely centered around a north-west area where the social icons are arranged.

**Zone root pattern** matches projects (093) and achievements (045) — but social's content is in 2 child collections (icons + statue), not directly in this script.

**`hull` mesh** — single mesh for the social-zone building/structure. Bruno's "one mesh for the zone visual" pattern (also seen in 045 achievements with `hull.004`).

**`darkGray` material** — first appearance in batch 4. Used on the social hull or kiosk. Differentiates the social-zone aesthetic from other zones.

## Connections

- **Reads from:** `005_meshes_*.py` (hull mesh, Cube.133)
- **Read by:** `999_finalize.py` (parents `icons` 104 + `statue` 105 under the `social` EMPTY)
- **Depends on:** `044_areas.py` (parent zone)
- **Depended on by:** `104_icons.py`, `105_statue.py`, runtime social-platform-walking physics

## Notable code patterns

- **Curved-arc collider chain** — 9 EMPTY/CUBEs each incrementally rotated to follow a curve. Bruno's pattern for non-straight walkable platforms.
- **Uniform scaling across an arc** — all 9 cuboids share (1.61, 1.61, 0.50). The arc is a tiled platform.
- **`darkGray` material** — first non-`palette` material on a zone hull. Bruno gives the social zone a distinct dark-gray aesthetic.
- **9 evenly-spaced colliders** — Bruno's discretization of a curved path. Each empty's rotation matches its position on the arc (rotZ increment ≈ 0.45 rad/cuboid).
- **`physicalFixed.002` at (25.95, 18.09)** — different XY from the colliders' arc area. Bruno's "floor physics anchor lives at a different spot from the platform colliders" pattern.
- **Zone root parent pattern** — same as `projects` (093). 9 child collections in projects vs 2 here (icons + statue).
- **`hull` mesh name** echoes `hull.004` in achievements (045) — Bruno uses `hull` as a generic name for the zone's main visible structure.
- **CIRCLE-typed empties for bounds + frustum** — consistent zone-definition convention.
