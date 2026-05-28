# 020_terrain.py — instantiate THE island as a single MESH object with Geometry Nodes modifier

**Path:** `folio-2025/scripts/blender_world_steps/steps/020_terrain.py`
**Lines:** 49
**Adds:** 1 MESH object (`terrain`) in collection `terrain`
**Group:** [02-ground-grass](../02-ground-grass.md)

## What it does (code-level)

```python
# Ensure 'terrain' collection exists and is linked under scene root
coll = bpy.data.collections.get('terrain') or bpy.data.collections.new('terrain')
if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
    bpy.context.scene.collection.children.link(coll)

# Create the object, using the terrain mesh datablock 'Plane.134' loaded in 005_meshes_05
ob = bpy.data.objects.get('terrain') or bpy.data.objects.new('terrain', bpy.data.meshes.get('Plane.134'))
ob.location = (0.0, 0.0, 0.0)
ob.rotation_mode = 'XYZ'
ob.rotation_euler = (0.0, 0.0, 0.0)
ob.scale = (1.0, 1.0, 1.0)
ob.display_type = 'TEXTURED'

# Add Geometry Nodes modifier and bind the 'Geometry Nodes' node group
m = ob.modifiers.new('GeometryNodes', 'NODES')
m.use_pin_to_last = False
m.use_apply_on_spline = False
m.node_group = bpy.data.node_groups.get('Geometry Nodes')   # from 003_node_groups
m.bake_directory = ''
m.bake_target = 'PACKED'
# + many open_*_panel flags (UI-only, no render effect)

# Link object to the collection
coll.objects.link(ob)
```

The script also sets the panel UI defaults for the modifier (`open_manage_panel = False`, `open_warnings_panel = True`, etc.) — irrelevant to render output.

## Key data

- **Datablocks referenced**:
  - Mesh: `Plane.134` (loaded in [005-meshes-05](../01-foundation/005-meshes-05.md)) — 16641 verts × 16384 polys (129² × 128² subdivided plane).
  - Node group: `Geometry Nodes` (built in [003-node-groups](../01-foundation/003-node-groups.md)) — samples `terrainWater` EXR, separates R, multiplies by −1.5, offsets Z. Carves the river / pond depressions.
- **Materials assigned**: none here — material `terrain` (from 004) is on the mesh's material slot, attached during the mesh's `005_meshes_05` block, not this script.
- **Modifiers added**: one — `GeometryNodes` (`NODES` type) bound to the `Geometry Nodes` node group.
- **Custom properties**: none on the terrain object.
- **World positions of key anchors**: `(0.0, 0.0, 0.0)` — the island sits at world origin. The mesh's verts carry any local extent.
- **Object types breakdown**: 1 MESH.
- **Parent collection**: `terrain` (top-level under scene root).

## Technique / recipe

The "single-mesh island with procedural displacement" pattern:

- **One MESH object, one mesh datablock, one modifier**. Bruno's terrain is not a heightfield + collider — it's a flat plane that gets pushed down where the EXR mask is dark, and otherwise stays flat.
- **No baking step in this script** — the modifier runs live every time Blender re-evaluates. The runtime captures the deformed mesh by other means (Bruno's Three.js code reads the terrain from the GLB export, which bakes the modifier output).
- **`Plane.134` is the world's biggest mesh** (16641 verts). Subdivision is 128 × 128 quads; resolution is fine enough that the EXR-driven displacement reads as smooth hills/ponds, coarse enough to be cheap.
- **`bake_target = 'PACKED'`**: when the modifier's bake panel runs, it embeds the result in the .blend. Bruno never explicitly bakes here.
- **`display_type = 'TEXTURED'`**: viewport shows the textured material preview, so Bruno sees the terrain colors while authoring.
- **The terrain plane at scale (1, 1, 1) and origin (0, 0, 0)** means the world's coordinate frame is the mesh's local frame too — no transform pivots required.

## Connections

- **Reads from**:
  - 005-meshes-05 (`Plane.134` mesh datablock)
  - 003-node-groups (`Geometry Nodes` node-group)
  - 004-materials (`terrain` material — attached to Plane.134's material slot, not in this script)
  - 002-images (`terrainWater` EXR sampled by the Geometry Nodes group)
  - 013-collections (`terrain` collection exists)
- **Read by**:
  - 021_grass (the grass-scatter object uses the same world frame; in runtime, scatters samples the deformed terrain Z).
  - All later prop scripts implicitly assume the terrain exists at origin.
- **Depends on**: 005, 003, 004, 013.
- **Depended on by**: every later script's spatial assumption.

## Notable code patterns

- **Idempotency**:
  - Object: `bpy.data.objects.get('terrain') or bpy.data.objects.new('terrain', ...)` — re-run-safe.
  - Collection link: `if coll.name not in {c.name for c in bpy.context.scene.collection.children}` — guards against re-linking.
  - Object → collection: same set-membership guard.
- **Object name `'terrain'` matches collection name `'terrain'`** — Blender allows this; they're separate datablocks (object vs collection), no conflict.
- **`scale = (1, 1, 1)`** — no scaling on the visible terrain. Anything that needs to "scale the world" has to scale every prop, not this object.
- **The script is the world's smallest "section" file** — 49 lines for what's arguably the most important object. The smallness reveals just how much logic lives in the Geometry-Nodes group rather than the script.
- **No collider / physics property attached**: the terrain has zero gameplay metadata here. Runtime collision in karan-portfolio's analog is a Rapier heightfield — Bruno's runtime handles its terrain collider some other way (probably a separate world-load step in Three.js).
- **Future-proof modifier panel flags**: `open_warnings_panel = True` ensures Bruno sees any modifier warnings (e.g., missing node-group input bindings). Helpful while authoring; harmless at runtime.
