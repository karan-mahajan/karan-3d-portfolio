# 023_basaltRocks.py — 13 basalt rock objects (5 visible + 8 collision hulls)

**Path:** `folio-2025/scripts/blender_world_steps/steps/023_basaltRocks.py`
**Lines:** 181
**Adds:** 13 MESH objects in collection `basaltRocks`
**Group:** [03-surface-detail](../03-surface-detail.md)

## What it does (code-level)

For each of 13 objects:

```python
ob = bpy.data.objects.get('<name>') or bpy.data.objects.new('<name>', bpy.data.meshes.get('<meshName>'))
ob.location = (x, y, z)
ob.rotation_mode = 'XYZ'
ob.rotation_euler = (0.0, ±0.0, 0.0)   # mostly identity
ob.scale = (1.0, 1.0, 1.0)
# For collision hulls: ob.hide_render = True; ob.display_type = 'WIRE'
# For visible rocks: ob.display_type = 'TEXTURED'
if ob.name not in {o.name for o in coll.objects}:
    coll.objects.link(ob)
```

**No modifiers added.** **No collection-mounting** (relies on 022_scenery.002.py having mounted the parent already).

## The 13 objects

**5 visible basalt rocks** (`display_type='TEXTURED'`, rendered):

| Object | Mesh datablock | World position (X, Y, Z) |
|---|---|---|
| `basaltRocksPhysicalStatic` | `Cylinder.022` | (..., ..., ...) — see file |
| `basaltRocksPhysicalStatic.001` | `Cylinder.011` | varies |
| `basaltRocksPhysicalStatic.002` | `Cylinder.015` | `(36.97, -45.29, -0.48)` |
| `basaltRocksPhysicalStatic.003` | `Cylinder.014` | varies |
| `basaltRocksPhysicalStatic.004` | `Cylinder.040` | varies |

**8 collision hulls** (`display_type='WIRE'`, `hide_render=True`):

| Hull object | Mesh datablock | World position |
|---|---|---|
| `hull.001` | `Cylinder.018` | varies |
| `hull.002` | `Cylinder.021` | varies |
| `hull.011` | `Cylinder.032` | `(-2.71, -10.69, -0.57)` |
| `hull.012` | `Cylinder.033` | `(-1.61, -4.73, -0.01)` |
| `hull.013` | `Cylinder.037` | `(16.30, 22.08, 0.05)` |
| `hull.014` | `Cylinder.036` | `(10.18, 23.64, -0.50)` |
| `hull.015` | `Cylinder.035` | `(-14.70, 9.07, -0.23)` |
| `hull.016` | `Cylinder.034` | `(-16.20, 5.22, -0.27)` |

## Key data

- **Datablocks referenced**: 13 mesh datablocks from `Cylinder.011/.014/.015/.018/.021/.022/.032..037/.040` (loaded in [005-meshes-02](../01-foundation/005-meshes-02.md) and [005-meshes-03](../01-foundation/005-meshes-03.md)).
- **Materials assigned**: none in this script — material `palette` is attached to each mesh's material slot in 005, not the object.
- **Modifiers added**: none. No `Smooth by Angle` or other GN modifiers on basalt rocks.
- **Custom properties**: none on the objects in this script.
- **World positions of key anchors**:
  - Visible basaltRocksPhysicalStatic.002 at `(37, -45, -0.5)` — far SE corner.
  - Hulls clustered around `(-16, 5, 0)` to `(16, 23, 0)` — central island area.
- **Object types breakdown**: 13 MESH.
- **Parent collection**: `basaltRocks` (child of `scenery.002`, mounted by 022).

## Technique / recipe

The "visible mesh + collision hull twin" pattern:

- **Two objects per logical rock prop**: one for visual (textured, rendered), one for collision (WIRE display, render-hidden). They share the same world placement (roughly) and are paired by Bruno during authoring.
- **Why convex `hull.*` separate from `basaltRocksPhysicalStatic.*`?** The visible mesh has lots of triangles for a chunky basalt look; the collision hull is a low-poly cylinder approximation for fast physics. Bruno authors the hull in Blender manually and tags it with `hide_render = True` so it never shows but stays in the .blend for runtime export.
- **Hulls displayed as WIRE in Blender's viewport**: helps Bruno see them while authoring without obscuring the visible rocks.
- **`basaltRocksPhysicalStatic.*` naming convention**: PhysicalStatic = a static rigidbody in the runtime physics engine. The 5 visible rocks are static colliders the player can stand on / walk into.
- **The 8:5 hull-to-visible ratio is asymmetric** — some visible rocks must have 2+ hulls (a single basalt cluster broken into multiple convex hulls for better collision).
- **All positions are world-absolute**: `ob.location` is directly the world coordinate. Bruno doesn't use parent-relative offsets for these.
- **Rotation = identity** for almost all rocks: variety comes from picking different mesh datablocks (each Cylinder.NNN has a unique shape), not from rotating a single source.

## Connections

- **Reads from**:
  - 005-meshes-02/03 (Cylinder.011, .014, .015, .018, .021, .022, .032..037, .040)
  - 004-materials (`palette` via mesh material slots)
  - 013-collections (`basaltRocks` collection exists and is child of `scenery.002`)
  - 022_scenery.002.py (mounts parent at scene root)
- **Read by**: 999_finalize (applies object parenting / view-layer excludes).
- **Depends on**: 005, 004, 013, 022.
- **Depended on by**: 999_finalize.

## Notable code patterns

- **No modifiers, no custom properties**: this script is "pure placement." The visual character of each rock is baked into its mesh datablock (vertex positions, palette material, per-loop UVs).
- **Idempotency**: every object follows `get() or new()` + `if ob.name not in {o.name for o in coll.objects}: coll.objects.link(ob)`.
- **`ob.scale = (1, 1, 1)` everywhere**: rocks are "real-size" in mesh data; no per-object scaling.
- **Asymmetric counts (5 visible, 8 hull)**: hints that hull modeling is more granular than visible mesh modeling — each rock can have multiple collision pieces.
- **The basalt rocks were placed clustered around origin**: ~70% are within ±20 m of (0, 0). Two outliers (`basaltRocksPhysicalStatic.002` at `(37, -45)`) are placed in the SE area. Suggests a small basalt outcrop near spawn + scattered specimen further out.
- **No spline-based scatter** — every position is hand-placed by Bruno. Despite the geometry-nodes tooling available, surface-detail rocks are hand-placed for art-directed composition.
