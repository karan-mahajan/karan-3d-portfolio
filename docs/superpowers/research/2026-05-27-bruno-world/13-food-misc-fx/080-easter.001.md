# 080_easter.001.py — easter hunt set: eggs + basket + zone

**Path:** `folio-2025/scripts/blender_world_steps/steps/080_easter.001.py`
**Lines:** 317
**Adds:** 21 objects (7× MESH, 14× EMPTY) to collection `easter.001`
**Group:** [13-food-misc-fx](../13-food-misc-fx.md)

## What it does (code-level)
Builds the `easter.001` collection — the egg-hunt mini-game's gameplay objects (eggs, basket, hit-boxes, zone trigger). Status: EXCLUDED (revealed at runtime).

Sequence of objects:
1. `eggPhysicalDynamic` (MESH `Sphere`) at `(53.35, -36.62, 0.96)`, scale 0.503 — dynamic egg #0.
2. `easter` (EMPTY `PLAIN_AXES`) at `(53.47, -36.41, 0.90)` — zone root anchor.
3. `ball.002` (EMPTY `SPHERE`, scale 0.529) — collision sphere for egg #0.
4. `refInteractivePoint.007` (EMPTY) at `(56.16, -36.63, 1.75)` — pickup interaction trigger.
5. `refZoneFrustum.013` (EMPTY `CIRCLE`, scale 4.01) at `(54.05, -36.80, 3.27)` rot x=-π/2 — activation ring.
6. `basketPhysicalDynamic` (MESH `Cylinder.019`) at `(53.53, -36.18, 0.89)` — the collection basket.
7. `cuboid.089/090/091/232` (EMPTY `CUBE` × 4) — basket walls (rotated 0/π/2/π/3π/2 around z, all at local-offset position ~0.87 from origin, scale (0.21, 2.12, 1.07)) — these form a "box of cubes" cage around the basket.
8. `cuboid.233` (EMPTY `CUBE`) at local `(0, 0, -0.81)` scale `(1.83, 1.83, 0.15)` — basket floor.
9. Eggs 1-5: `eggPhysicalDynamic.001..005` (MESH × 5, using `Sphere.002/004/006/008/011`) at hand-tuned spawn positions near the basket, with per-egg rotations.
10. Each egg followed by `ball.003..007` (EMPTY `SPHERE`) — runtime physics-sphere stand-ins for each egg.

## Key data
- **Datablocks referenced**: meshes `Sphere`, `Sphere.002`, `Sphere.004`, `Sphere.006`, `Sphere.008`, `Sphere.011` (six unique egg meshes — slight variations), `Cylinder.019` (basket).
- **Materials assigned**: via mesh data (`palette` on eggs).
- **Modifiers added**: none.
- **Custom properties**: none.
- **World positions**:
  - Zone root `easter` at `(53.47, -36.41, 0.90)` — central-east at far south.
  - 6 eggs scattered around `(53, -36)` with z varying 0.43–1.45 (some on ground, some on lip of basket).
  - Basket walls (cuboid.089-091, 232) at LOCAL `(0.87, 0, -0.33)` etc. — they'll be parented to `eggPhysicalDynamic` in finalize and rotated to form 4 walls.
- **Object types breakdown**: 7 MESH, 14 EMPTY.
- **Parent collection**: `easter` (collection 129) which itself is excluded from view layer.

## Technique / recipe
- **Egg+collider pair pattern**: each egg has a sibling `ball.NNN` empty (SPHERE display) at a NEAR-IDENTICAL position. The empty is the runtime physics collider stand-in; the mesh is the visual. They share scale ≈ 0.529.
- **Basket walls as parented cuboids**: 4 EMPTY cubes positioned at LOCAL offsets (not world) — they're meant to be parented to `eggPhysicalDynamic` (the basket-as-anchor) in 999_finalize, then rotated around z to form 4 sides. This is a "parent-relative collision cage" pattern.
- **Per-egg unique mesh**: each of the 6 eggs uses a DIFFERENT Sphere mesh — Bruno authored slight shape variations rather than scaling one mesh. (Same idea as tree leaf variants in `04-trees`.)

## Connections
- **Reads from**: `005_meshes_*` (Sphere variants + Cylinder.019), `004_materials.py` (palette).
- **Read by**: `129_easter.py` (parents `easter.001` collection under the `easter` empty), `999_finalize.py` (object parenting + view-layer EXCLUDE).
- **Depends on**: foundation 001-013, plus easter root collection (129).
- **Depended on by**: 999_finalize.

## Notable code patterns
- `refZoneFrustum.013` z=3.273 — the same "anchor altitude" used by [tornado](138-tornado.md), [forbidden zones](139-whispersForbiddenAreas.md), and [cookie](079-cookie.md). Bruno's runtime treats z=3.273 as the "zone marker plane."
- Naming pattern: dynamic physics objects suffix `PhysicalDynamic`, fixed-body suffix `PhysicalFixed`, generic empties `cuboid.NNN`.
- All 14 empties share the same z (3.273 for zone, 0.97 for collision spheres, -0.33 for basket walls) — Bruno consistently snaps anchors to discrete "layers."
