# 021_grass.py — instantiate the grass-scatter MESH object with Geometry Nodes modifier

**Path:** `folio-2025/scripts/blender_world_steps/steps/021_grass.py`
**Lines:** 49
**Adds:** 1 MESH object (`Plane.003`) in collection `grass`
**Group:** [02-ground-grass](../02-ground-grass.md)

## What it does (code-level)

```python
# Ensure 'grass' collection exists and is linked under scene root
coll = bpy.data.collections.get('grass') or bpy.data.collections.new('grass')
if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
    bpy.context.scene.collection.children.link(coll)

# Create the object using mesh 'Plane.012' but name the object 'Plane.003'
ob = bpy.data.objects.get('Plane.003') or bpy.data.objects.new('Plane.003', bpy.data.meshes.get('Plane.012'))
ob.location = (0.0, 0.0, 0.0)
ob.rotation_mode = 'XYZ'
ob.rotation_euler = (0.0, 0.0, 0.0)
ob.scale = (1.0, 1.0, 1.0)
ob.display_type = 'TEXTURED'

# Add Geometry Nodes modifier bound to 'Geometry Nodes.001' (the grass-scatter group)
m = ob.modifiers.new('GeometryNodes', 'NODES')
m.node_group = bpy.data.node_groups.get('Geometry Nodes.001')
m.bake_target = 'PACKED'
# + UI panel flags

coll.objects.link(ob)
```

**Notable mismatch**: the object is **named** `Plane.003` but its **data is** `Plane.012`. Object name and mesh datablock name do NOT correspond. This is fine in Blender (object name is independent of mesh datablock name), but worth flagging.

## Key data

- **Datablocks referenced**:
  - Mesh: `Plane.012` (loaded in [005-meshes-03](../01-foundation/005-meshes-03.md)) — the small grass-blade source mesh. Per the group .md, this is a 3-vert triangle (1 face). The Geometry Nodes group instances it tens of thousands of times.
  - Node group: `Geometry Nodes.001` (built in [003-node-groups](../01-foundation/003-node-groups.md)) — the grass scatter graph: `Grid 192×192m@512×512verts → Distribute Points → Image Texture(terrainGrass) → Separate Color.g → LESS_THAN 0.4 → Instance on Points → Realize Instances`. ~78k grass blades distributed across the island where the EXR's G channel is below 0.4.
- **Materials assigned**: none here — material `grass` (from 004) lives on the mesh's material slot.
- **Modifiers added**: one — `GeometryNodes` (`NODES`) bound to `Geometry Nodes.001`.
- **Custom properties**: none.
- **World positions**: `(0, 0, 0)` — same world origin as the terrain.
- **Object types breakdown**: 1 MESH (single object, but the modifier produces ~78k visible instances at render time).
- **Parent collection**: `grass` (top-level under scene root).

## Technique / recipe

The "geometry-nodes scatter on a 3-vert source mesh" pattern:

- **Source mesh = 3-vert triangle**: the smallest possible visible mesh, because the actual scatter doesn't need a complex source. One triangle, 3 verts, 1 face. The grass material does all the work of making the triangle look like a yellow-tipped blade.
- **The grass material's UV.y mix** (see [004-materials.md](../01-foundation/004-materials.md#vertexuv-driven-gradients-2)) tints blade base dark olive and blade tip yellow — UV.y of the triangle's verts drives the gradient.
- **Geometry-Nodes group does all heavy lifting**: a 192×192 m grid samples `terrainGrass.exr.g` at every grid vert; cells where green < 0.4 produce a scatter point; each point gets an Instance of the 3-vert triangle. `Realize Instances` flattens for export.
- **Output mesh in viewport ≈ ~78k blades** (count is approximate; depends on the EXR mask coverage). This is **expensive** to render at full fidelity; Bruno mitigates by:
  - Only rendering this in Blender for preview (`Grass.js` runtime uses a different system — camera-billboarded shader, not actual scatter mesh)
  - The `Realize Instances` output is what gets baked into the GLB; the GLB is exported once and never re-scattered
- **Object at world origin** with no scaling — relies on the Geometry-Nodes group's internal 192 × 192 m grid for world placement.

## Connections

- **Reads from**:
  - 005-meshes-03 (`Plane.012`)
  - 003-node-groups (`Geometry Nodes.001`)
  - 002-images (`terrainGrass` EXR sampled by the group)
  - 004-materials (`grass` material on mesh slot)
  - 013-collections (`grass` collection)
- **Read by**: runtime (`Grass.js` reads scattered baked data from the exported GLB, but in Blender the modifier produces the live preview).
- **Depends on**: 005, 003, 002, 004, 013.
- **Depended on by**: any visual check / bake of the grass field.

## Notable code patterns

- **Object name vs mesh name mismatch**: object `Plane.003` ↔ mesh `Plane.012`. Bruno's authoring kept the source mesh's original number; the object was renamed for clarity ("Plane.003" suggests it's the third grass-source plane variant Bruno tried). The mismatch is invisible at runtime — only Blender users notice.
- **Same modifier-panel boilerplate as 020_terrain**: identical sequence of `m.open_*_panel` and `m.bake_*` flags. This is auto-emitted scaffolding common to every NODES-modifier-adding script in the pipeline.
- **No alpha/transparency settings on the object**: the alpha is handled in the `grass` material (HASHED blend mode). Object-level transparency irrelevant.
- **The `grass` collection is `color_tag = COLOR_04` (green)** per [013-collections.md](../01-foundation/013-collections.md) — Bruno color-codes ground/world-system collections green in the Outliner.
- **78k+ grass blades on a 3-vert source = ~234k visible verts before LOD**. Manageable in Blender's GN viewport, but the runtime renderer needs to handle this differently — confirmed by the group .md's note that Bruno's `Grass.js` re-implements this with camera-billboarded triangles rather than baked scatter geometry.
- **Idempotency** via the same `get() or new()` + set-membership-guard patterns as 020_terrain.
