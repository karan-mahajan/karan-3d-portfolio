# 005_meshes_00.py — mesh datablock chunk 1 of 7 (60 datablocks)

**Path:** `folio-2025/scripts/blender_world_steps/steps/005_meshes_00.py`
**Lines:** 769
**Adds:** 60 mesh datablocks (no scene objects yet)
**Group:** [01-foundation](../01-foundation.md)

## What it does (code-level)

Single `run()` that creates 60 mesh datablocks via `bpy.data.meshes.new(name)`. Each mesh follows the same per-mesh pattern (this template is shared by all 7 chunks):

```python
# --- <meshName> ---
me = bpy.data.meshes.get('<name>') or bpy.data.meshes.new('<name>')
me.clear_geometry()
me.from_pydata([[x,y,z], ...], [], [[i,j,k], [i,j,k,l], ...])  # verts, [], polys
me.update()
_mi = [matIndex, matIndex, ...]   # one per polygon
_sm = [1, 1, ...]                 # use_smooth flag per polygon
for _i, _p in enumerate(me.polygons):
    _p.material_index = _mi[_i]
    _p.use_smooth = bool(_sm[_i])
_uv = me.uv_layers.new(name='UVMap')
_u = [[u,v], ...]                 # one per mesh loop (per face-corner)
for _i, _d in enumerate(_uv.data): _d.uv = _u[_i]
# optional second UV layer:
_uv = me.uv_layers.new(name='UVMap.001')
_u = [[u,v], ...]
for _i, _d in enumerate(_uv.data): _d.uv = _u[_i]
me.materials.append(bpy.data.materials.get('<mat1>'))
# 0..N additional `me.materials.append(...)` calls
```

This is the canonical "fully exported mesh datablock from Blender's Python" idiom: `from_pydata(verts, edges, polys)` (passing `[]` for edges → Blender derives edges from polygon loops) and then explicit per-poly material/smooth and per-loop UV assignments.

## Mesh datablocks in this chunk (60)

`bumpersRefrenceMesh.006`, `BézierCircle`, `BézierCircle.003`, `BézierCircle.005`, `Circle.001`, `Circle.002`, `Circle.003`, `Circle.004`, `Circle.005`, `Circle.006`, `Circle.007`, `Circle.008`, `Circle.010`, `Circle.011`, `Circle.015`, `Circle.016`, `Circle.019`, `Circle.025`, `Circle.028`, `Cube`, `Cube.001..016`, `Cube.022`, `Cube.026`, `Cube.035`, `Cube.037`, `Cube.039`, `Cube.041`, `Cube.043`, `Cube.049`, `Cube.052..054`, `Cube.056`, `Cube.062`, `Cube.063`, `Cube.065`, `Cube.067`, `Cube.068`, `Cube.070..072`, `Cube.074`, `Cube.077`, `Cube.079`, `Cube.081`.

Sorting is **lexicographic on Blender's default-suffix naming** (`Cube`, `Cube.001`, `Cube.002`, …) — these are leftover authoring names, never renamed. The non-sequential numbering (`.072 → .074 → .077`) is Bruno deleting / merging meshes during authoring and never compacting indices.

The lone outlier `bumpersRefrenceMesh.006` is the only meaningfully-named mesh in this chunk — almost certainly a **reference template** for race-track barrier instances (see `referenceBumpers` collection, finalized in race-track scripts).

## Key data

- **Datablocks referenced**: only materials (added via `me.materials.append(bpy.data.materials.get(...))`). The materials seen in this chunk's `me.materials.append(...)` calls: `black`, `emissiveGreenRadialGradient`, `emissiveOrangeRadialGradient`, `palette`, `redGradient`, `waterfall`.
- **Materials assigned (per chunk)**: 6 materials touched. `palette` dominates (most meshes); emissive variants on a few.
- **Modifiers added**: none here (modifiers attach to objects in 020+ scripts).
- **Custom properties**: none on the mesh datablock; props live on scene objects later.
- **World positions of key anchors**: each `me.from_pydata` call lists vertex coords in **world space** (Bruno didn't reset origins). Example: `bumpersRefrenceMesh.006`'s first vert is `(-17.61, 71.25, 0.50)` — far from origin. When 020+ scripts create an object pointing at this mesh, the object's `location = (0, 0, 0)` and the mesh's verts carry the actual placement. (Equivalent to "applied transforms" at export time.)
- **Object types breakdown**: 0 (no scene objects in this script).
- **Parent collection**: n/a — meshes are not yet linked to objects.

## Technique / recipe

The "frozen mesh library" pattern, common to all 7 chunks (this `.md` documents it once; chunks 01-06 reference back here):

- **`from_pydata(verts, [], polys)` is the universal mesh constructor.** Passing `[]` for edges lets Blender auto-compute them from the polygon loops. Polygons can be tris (3 indices) or quads (4 indices) interleaved — Bruno does this freely.
- **Per-polygon material_index + use_smooth**: stored as two parallel int arrays (`_mi`, `_sm`). `_sm[i] = 1` is universal in the chunks I sampled — every face is shade-smooth. `_mi[i]` indexes into the mesh's `me.materials` slot list.
- **Per-loop UVs**: `_u[i]` is set on `me.uv_layers['UVMap'].data[i].uv`. Loops count = sum of polygon-loop-counts (≈ verts × valence). For a quad-only mesh: 4 UVs per quad.
- **Optional second UV layer (`UVMap.001`)** when a mesh needs two different texture coordinates — typical for props that have both a palette-coord (which color from the strip) AND a texture-coord (for stuff like circuit logos).
- **Material indexing scheme**: `me.materials.append(palette)` first → `palette` is slot 0. Most polygons get `material_index = 0` to use it. Polygons that need a different material get a higher index pointing at one of the additional appends. So a mesh that's mostly palette-colored with a few emissive accents has `palette` at slot 0 and one emissive at slot 1.
- **The "palette color pick" trick**: all UV.x values for a mesh's `palette`-mapped faces are set to a constant value, picking a single color from the 128×4 strip. Different meshes pick different columns, giving Bruno visual variety with no per-vertex color authoring.
- **Mesh-name reuse**: meshes are *datablocks*, separate from objects. Bruno can later instance the same mesh (e.g., `Cube.043`) under many objects to reuse geometry — and does, heavily, in the per-section scripts (multiple objects share one mesh).
- **No `me.attributes` calls in this chunk**: vertex colors aren't authored here. Color comes entirely from palette material × UV. Confirms the "vertex-color baking" claim in the group .md was a misread — Bruno doesn't bake vertex colors; he per-loop-UVs onto a 128-pixel strip.

## Connections

- **Reads from**: 004_materials (materials looked up by name when appending to the mesh's material slot).
- **Read by**: every per-section script from 020+. They do `ob = bpy.data.objects.new(name, bpy.data.meshes.get('<chunkMesh>'))` to instantiate the mesh into scene objects.
- **Depends on**: 000_init (wipe), 004_materials (material names must resolve).
- **Depended on by**: all 020-139 per-section scripts. Without 005-* chunks, every later `bpy.data.meshes.get(...)` returns None and the object becomes mesh-less.

## Notable code patterns

- **Massive per-mesh inline arrays**: each mesh's `from_pydata` call has all its verts AND polys as Python list literals on one line. For a 1000-vert mesh, this is a 30-50 KB line. Vite-style "I am literally serialized data" code.
- **No mesh deduplication**: 368 mesh datablocks for ~1,507 scene objects means roughly 4× reuse on average. The reuse is implicit (later objects share mesh datablocks) — this script just creates the unique meshes.
- **Non-sequential indexing**: gaps in `.NNN` suffixes (`.072 → .074`) signal mesh deletions in the source .blend that were never compacted. Doesn't break anything because the names are referenced literally, not computed.
- **Quads + tris mixed**: e.g., `bumpersRefrenceMesh.006`'s polygon list interleaves 3-index and 4-index entries: `[[0,1,6,5],[0,2,1],[0,3,2],[0,4,3],[4,0,5,9],...]`. Blender handles both fine in `from_pydata`.
- **`me.update()` after `from_pydata`**: standard idiom to refresh internal state before assigning material indices / UVs. Skipping it leaves the mesh in an inconsistent state.
- **`_mi`, `_sm`, `_u`, `_uv` are throw-away locals** reused per-mesh. The single-letter underscore names keep the script smaller and signal "this is generated code, not human-authored."
