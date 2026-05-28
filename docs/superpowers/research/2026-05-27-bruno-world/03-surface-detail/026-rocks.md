# 026_rocks.py — single large rock at the south-east corner

**Path:** `folio-2025/scripts/blender_world_steps/steps/026_rocks.py`
**Lines:** 21
**Adds:** 1 MESH object (`Cube.157`) in collection `rocks`
**Group:** [03-surface-detail](../03-surface-detail.md)

## What it does (code-level)

```python
coll = bpy.data.collections.get('rocks') or bpy.data.collections.new('rocks')

ob = bpy.data.objects.get('Cube.157') or bpy.data.objects.new('Cube.157', bpy.data.meshes.get('Cube.070'))
ob.location = (57.463, -50.010, -0.142)
ob.rotation_mode = 'XYZ'
ob.rotation_euler = (0.9388, 0.6182, -1.2237)    # ~53.8°, 35.4°, -70.1°
ob.scale = (0.9429, 0.9429, 0.9429)
ob.display_type = 'TEXTURED'

if ob.name not in {o.name for o in coll.objects}:
    coll.objects.link(ob)

print('  added 1 objects to rocks')
```

One MESH object: **a single rock**.

## Key data

- **Datablocks referenced**:
  - Mesh: `Cube.070` (from [005-meshes-00](../01-foundation/005-meshes-00.md)) — 696 verts per the group .md.
- **Materials assigned**: `palette` via the mesh's material slot (set in 005).
- **Modifiers added**: none.
- **Custom properties**: none.
- **World positions of key anchors**: `(57.46, -50.01, -0.14)` — far south-east corner of the world.
- **Object types breakdown**: 1 MESH.
- **Parent collection**: `rocks` (child of `scenery.002`, mounted by 022).

## Technique / recipe

The "lonely landmark rock" pattern:

- **One rock, far from origin**: `(+57, -50, ~0)` is well outside the central play area. Acts as a horizon landmark — visible from far but not blocking the player.
- **Tilted rotation `(0.94, 0.62, -1.22)` rad** ≈ (54°, 35°, -70°) — a quirky 3-axis tilt giving the rock an off-axis posture. Reads as "naturally tumbled" rather than perfectly upright.
- **Slight scale-down 0.94×** — uniform shrink, probably to fit a desired aesthetic size after Bruno modeled the mesh slightly larger than needed.
- **No collision hull** — unlike basaltRocks where each visible rock has a paired `hull.NNN`, this rock relies on the underlying terrain heightfield for collision (or it's intentionally non-collidable, decorative-only).
- **No physics tag** in the object name (no "PhysicalStatic"/"PhysicalFixed" suffix) — confirms it's likely a non-collider decoration.

## Connections

- **Reads from**:
  - 005-meshes-00 (`Cube.070`)
  - 004-materials (`palette` via mesh slot)
  - 013-collections (`rocks` collection exists)
  - 022_scenery.002.py (parent mounted)
- **Read by**: 999_finalize.
- **Depends on**: 005, 004, 013, 022.
- **Depended on by**: 999_finalize.

## Notable code patterns

- **Smallest non-empty surface-detail script** (21 lines).
- **Object name `Cube.157` is the original authoring name** even though it doesn't suggest "rock." Bruno didn't rename it.
- **3-axis Euler rotation is rare** — most props in surface-detail use single-axis Z-only rotation. This rock's tumbled pose is hand-set.
- **Uniform scale 0.94×** suggests Bruno authored the mesh slightly larger then dialed down — easier than re-modeling.
- **Position at `(+57, -50)` puts it within `~75 m` from origin** — outside the central island but probably still visible from spawn. A horizon-defining prop, not a navigation obstacle.
