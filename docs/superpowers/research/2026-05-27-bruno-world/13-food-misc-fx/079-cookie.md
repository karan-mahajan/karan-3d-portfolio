# 079_cookie.py — interactive cookie kiosk + zone setup

**Path:** `folio-2025/scripts/blender_world_steps/steps/079_cookie.py`
**Lines:** 359
**Adds:** 24 objects (9× MESH, 15× EMPTY) to collection `cookie`
**Group:** [13-food-misc-fx](../13-food-misc-fx.md)

## What it does (code-level)
Builds the `cookie` collection — an interactive multi-stage area. Pattern: linear sequence of `bpy.data.objects.get(...) or bpy.data.objects.new(...)`, each setting `ob.location`/`rotation_euler`/`scale`, sometimes `ob.empty_display_type`/`empty_display_size`, and optional custom props. No modifiers used.

Key objects added (in order):
1. `refCookie` (MESH `Cube.092`) — at `(10.43, -34.00, 1.28)`; **custom prop `preventAutoAdd = True`** (runtime won't auto-spawn until trigger fires).
2. `Cube.135` (MESH `Cube.065`) — the oven body at `(-4.04, 26.57, 0.35)`, scale (1.89, 1.30, 1.30).
3. `lava` (MESH `Cube.110`) — at `(-1.82, 28.32, 1.22)`, rot z=π/2; the visible "lava glow" inside the oven.
4. `refBanner` (MESH `Plane.018`) — at `(2.58, 27.02, 1.63)` rot z≈22° — uses the `cookieBanner` material.
5. `refChimney`, `refSpawner`, `refInteractivePoint.002`, `refTable` (EMPTY × 4) — anchor markers for chimney smoke spawn, cookie spawn point, interaction trigger, table position.
6. `refCounterPanel` (MESH `Cube.037`) — angled counter face at `(-2.83, 27.88, 2.54)` with bespoke X/Y/Z rotation.
7. `refCounterLabel` (EMPTY) — companion anchor for the label.
8. `cookiePhysicalFixed` (EMPTY) — fixed-body anchor.
9. `cuboid.006/004/005/008/001` (EMPTY×5, display_type='CUBE') — collision/trigger volumes with scale-encoded extents (e.g., `cuboid.006.scale = (2.02, 2.10, 1.77)`).
10. `tablePhysicalDynamic` (MESH `Cube.071`) at `(13.67, -39.00, 0.49)` — the dynamic table prop.
11. `refZoneBounding.005` (EMPTY `CIRCLE`, scale 7.34) — outer activation ring at `(11.44, -34.19, 3.27)` rot x=-π/2.
12. `Cube.054` (MESH `Cube.072`) at `(-27.95, 18.70, 0.09)` — a long thin slab (scale 0.76, 3.93, 0.52), the kiosk counter beam.
13. `refBlower.001` (MESH `Cube.077`) at `(33.38, -13.27, 0.28)` rot z=π — blower fan model.
14. `blowerPhysicalDynamic.001` (EMPTY `PLAIN_AXES`, size 2.0) at `(13.08, -31.00, 0.53)` — runtime dynamic blower anchor.
15. `cookie` (EMPTY `PLAIN_AXES`) at `(12.25, -35.25, 3.27)` — the area's root anchor.
16. `refZoneFrustum.005` (EMPTY `CIRCLE`, scale 4.32) — camera frustum trigger zone.

## Key data
- **Datablocks referenced**: meshes `Cube.092`, `Cube.065`, `Cube.110`, `Plane.018`, `Cube.141`, `Cube.037`, `Cube.071`, `Cube.072`, `Cube.077`.
- **Materials assigned**: via mesh data (`palette`, `cookieBanner`, `emissiveOrangeRadialGradient` on the lava/oven heat).
- **Modifiers added**: NONE in this script.
- **Custom properties**: `refCookie['preventAutoAdd'] = True` (sole CP in this script).
- **World positions of key anchors**:
  - Zone root `cookie`: `(12.25, -35.25, 3.27)`
  - Outer zone bounding ring: `(11.44, -34.19)` scale 7.34
  - Frustum trigger: `(9.75, -30.00)` scale 4.32
  - Oven counter cluster around `(-2.8 to -4.0, +27 to +28)` (probably the cookie shop interior elsewhere on the island).
  - Cookie spawn/table cluster around `(+10 to +13, -30 to -39)`.
- **Object types breakdown**: 9 MESH, 15 EMPTY.
- **Parent collection**: `areas` (via 999_finalize parenting under `cookie` empty + section-level).

## Technique / recipe
- **Two clusters in one collection**: an oven/counter group at `(-2.8, +27)` and a table/cookie group at `(+11, -36)`. These look distant in world space but belong to the same gameplay zone — Bruno may be using the runtime to teleport players between them or to render them in different camera views.
- **Anchor naming convention**: `refXxx` for runtime-readable references (spawner, chimney, table, interactive point), `cuboid.XXX` for collision/trigger volumes (display_type='CUBE', scale encodes half-extents), `refZoneBounding/Frustum` for activation rings (display_type='CIRCLE'). This is a consistent vocabulary across many of Bruno's scripts.
- **`preventAutoAdd`** custom prop — runtime-only flag, hides the object until the cookie-collection event triggers it.
- No modifiers — all visual styling comes from material assigned at the mesh-data level.

## Connections
- **Reads from**: `005_meshes_*` (9 mesh datablocks), `004_materials.py` (`cookieBanner` material).
- **Read by**: `999_finalize.py` (parents the 24 objects under the section's empties — `cookie`, `tablePhysicalDynamic`, etc., and ultimately under `areas/cookie`).
- **Depends on**: foundation 001-013.
- **Depended on by**: 999_finalize.

## Notable code patterns
- Empty display types as **encoded data**: `CIRCLE` for zone rings, `CUBE` for collision volumes, `PLAIN_AXES` for spawn anchors. The runtime reads the empty's `display_type` to know "what is this anchor."
- Counter rotation `(-0.232, -0.020, 0.264)` rad — a hand-tuned tilt, not axis-aligned. Bruno isn't afraid of arbitrary orientations.
- The `cookie` empty (zone root) sits at z=3.27 while most other props are at z<2 — z=3.27 is a recurring "zone anchor altitude" used across many scripts (see also tornado.000 through 016 all at z=3.273). This is Bruno's "anchor plane" — sits above the terrain so it doesn't snap to ground.
