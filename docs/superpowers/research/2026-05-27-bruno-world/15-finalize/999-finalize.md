# 999_finalize.py — parenting + view-layer + compositor + scene settings

**Path:** `folio-2025/scripts/blender_world_steps/steps/999_finalize.py`
**Lines:** 4,381 (321 KB)
**Adds:** 0 objects. Modifies relationships and scene-level settings only.
**Group:** [15-finalize](../15-finalize.md)

## What it does (code-level)
Single `run()` function divided into 5 well-marked sections:

### 1. Parent relationships (lines 6 → ~4302, ~859 `_o.parent =` statements)
For every parent-child relationship in the world, repeats:
```python
_o = bpy.data.objects.get('<child name>')
if _o is not None:
    _o.parent = bpy.data.objects.get('<parent name>')
    _o.parent_type = 'OBJECT'
    _o.matrix_parent_inverse = _mu.Matrix([(...row0...), (...row1...), (...row2...), (...row3...)])
```
The `matrix_parent_inverse` is the inverse of the parent's transform at the moment parenting was applied (Blender's standard "preserve world-space pose when parenting" pattern). 859 of these blocks. They're sorted ALPHABETICALLY by child name (Bruno's exporter sorted before emitting).

Examples from the file:
- `antenna` → `chassis` (under vehicle).
- `axle` → `antennaHead`.
- `awwwards` → `refDistinctions` (under projects).
- `backLights` → `chassis.001` (under vehicle).
- `ball.001` → `refBallPhysicalDynamic` (under bowling).
- `ball.002..007` → 6 different `eggPhysicalDynamic.NNN` (under easter.001 — egg+ball pairs).
- `baguiraMesh.001` → `baguiraPhysicalDynamic` (statue character meshes under their armature).
- `wings` → `sudoPhysicalDynamic` (winged character).
- `tableHall.001` → various zone empties.
- All zone empties like `bowling`, `circuit`, `lab`, `social`, `projects`, etc. are parents that hold the contents of their zone.

### 2. View-layer collection settings (lines 4303-4321)
Defines `_vl_settings = {'ViewLayer': {<collection name>: {'exclude': bool, 'hide_viewport': bool, 'holdout': bool, 'indirect_only': bool}}}` for every named collection. Then walks the view-layer collection tree and applies these settings to each `LayerCollection`.

EXCLUDED collections from the dict (status=True):
- `archives.003`, `sudo`, `antenna.001`, `oldSchool`, `easter`, `egg`, `map`, `altar.001`, `behindTheScene.001`, `birchTrees.001`, `oakTrees.001`, `cherryTrees.001`, `vehicle.001`, `tornado`, `whispersForbiddenAreas`, `FWA`, `fwa`, `archives.001`, `archives.002`, `archives` (cherry template), `archive.001`, `archives.004`, `easter.001`.
- Total: 23 collections excluded from main render.

VISIBLE collections (exclude=False): everything else, including the visible-instance copies of trees (`oakTrees`, `birchTrees`, `cherryTrees`), areas (`landing`, `lab`, `projects`, `social`, `bowling`, `circuit`, `cookie`, `cabin`, `timeMachine`, etc.), and all the props inside them.

`archive.001` is also `hide_viewport=True` (in addition to exclude — the metaball reference is double-hidden).

### 3. Scene settings (lines 4323-4357)
```python
sc = bpy.context.scene
sc.frame_start = 1
sc.frame_end = 250
sc.frame_current = 148
sc.frame_step = 1
sc.render.engine = 'CYCLES'
sc.render.resolution_x = 512
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
sc.render.fps = 24
sc.render.fps_base = 1.0
sc.render.film_transparent = True
sc.unit_settings.system = 'METRIC'  # meters/kilograms/seconds
sc.camera = bpy.data.objects.get('cameraTerrain')   # active camera
```

### 4. Compositor link (line 4360)
```python
sc.compositing_node_group = bpy.data.node_groups.get('terrain')
```
Wires the `terrain` CompositorNodeTree (loaded in 003) into the scene's compositor.

### 5. Node-tree datablock-ref fixup (lines 4364-4378)
List of `_fixups` tuples — each describes a node-input socket that needs a specific datablock reference re-bound after the additive build:
```python
_fixups = [
    ('ng', 'Geometry Nodes',   'Image Texture', 0, 'images', 'terrainWater'),
    ('ng', 'Geometry Nodes.001', 'Image Texture', 0, 'images', 'terrainGrass'),
    ('ng', 'Geometry Nodes.002', 'Object Info', 0, 'objects', 'archivePoleInstance'),
    ('ng', 'terrain', 'Image', 'image', 'images', 'terrainFurnitures'),
    ('ng', 'terrain', 'Image.001', 'image', 'images', 'terrainGrass'),
    ('ng', 'terrain', 'Image.002', 'image', 'images', 'terrainWater'),
    ('ng', 'terrain', 'Image.003', 'image', 'images', 'terrainAlpha'),
    ('mat', 'airDancer', 'Image Texture', 'image', 'images', 'circuitAirDancerFace.png'),
    ('mat', 'blackboardLabels', 'Image Texture', 'image', 'images', 'blackboardLabels.png'),
    # ... ~30 entries
    ('mat', 'palette', 'Image Texture', 'image', 'images', 'palette'),
    # ...
]
```
Tuple format: `(kind, owner, node_name, socket_key, container, datablock_name)`. Kind is `'ng'` (node-group), `'mat'` (material), `'world'` (world shader).

Loop walks each tuple, resolves the owner node-tree, finds the named node, and sets either an INPUT index (`node.inputs[key].default_value = target`) OR a named ATTRIBUTE (`setattr(node, key, target)`).

## Key data
- **~859 parenting statements** — covering all 1,507 objects (only objects that need parenting; some are at scene root).
- **~115+ collections in the view-layer dict** — every named collection in the world has explicit exclude/hide/holdout/indirect_only settings.
- **23 EXCLUDED collections** — hides templates/backups/runtime-revealed content.
- **~30 node-ref fixups** — covers Geometry Nodes (4 groups: `Geometry Nodes`, `.001`, `.002`, `terrain`) and material image textures (palette, airDancer, blackboardLabels, careerText*, circuitBrand/Threejs/Webgl/Webgpu, cookieBanner, labCarpet, projectsCarpet, projectsLabels, stylizedMap, terrain).

## Technique / recipe
- **Sorted parenting blocks**: Bruno's exporter alphabetizes parent statements — easier to diff between exports, no logical meaning to the order.
- **`matrix_parent_inverse` baked at export**: each parenting statement includes the exact 4x4 matrix that Bruno's authoring saved. This means the parent's world transform AT EXPORT TIME is encoded. Re-running 999_finalize repeatedly produces the same hierarchy.
- **View-layer settings as a dict**: nested `{layer_name: {collection_name: {flags}}}` structure lets one file describe the visibility rules for an entire scene. Generic enough to support multiple view layers (Bruno only uses one, `'ViewLayer'`).
- **Node fixups as a tuple list**: each tuple is data-driven; the loop is generic. Adding a new shader-image-binding = adding one tuple. Bruno's pipeline avoids per-shader if/else.
- **Scene units = metric meters/kg/sec**: explicit. Camera = `cameraTerrain` (the minimap camera). Frame range 1-250 = 10 seconds at 24 fps.
- **Render engine = CYCLES, resolution 512×512** — small render output (Bruno's web game renders at viewport scale, not the .blend's render settings; the 512×512 is for any preview renders).

## Connections
- **Reads from**: every prior script (000-139). Needs all objects, collections, node groups, images, materials to already exist.
- **Read by**: nothing — this is the last script.
- **Depends on**: all 141 prior scripts.
- **Depended on by**: the runtime Blender → game pipeline (the exported world's scene composition).

## Notable code patterns
- **The whole script is essentially a giant data dump with a small executor**: ~99% of the bytes are coordinates/matrices/names; ~1% is loop logic.
- **Idempotent**: every operation is `_o = get(...) if _o is not None: ...`. Re-running 999_finalize on an already-finalized .blend re-applies the same relationships (no duplicates).
- **`_mu.Matrix([...])` for matrix_parent_inverse**: uses `mathutils as _mu` (the underscore prefix avoids polluting any global namespace). Each row is a tuple of 4 floats.
- **Compositor goes through `sc.compositing_node_group`** — Bruno notes "Blender 5.x" in a comment, implying this API path is new and the script needs Blender 5+.
- **Node-ref fixup is ESSENTIAL**: without it, the terrain's geometry-nodes setup would have `None` image-texture inputs (broken) because the additive build doesn't preserve cross-object node refs. Re-binding here fixes everything.
- **Why 4,381 lines?** ~6 lines per parenting block × 859 blocks ≈ 5,154; minus shared boilerplate, roughly correct. The bulk is parenting (~4,290 lines), with the last ~80 lines being settings/fixups.
- The exclusion of the minimap-specific collections (`*.001` trees, `altar.001`, `behindTheScene.001`, `vehicle.001`) PLUS the main `map` collection means the runtime needs a DIFFERENT view-layer (or override) to render the minimap — Bruno's runtime must be flipping the layer settings at minimap-render time.
