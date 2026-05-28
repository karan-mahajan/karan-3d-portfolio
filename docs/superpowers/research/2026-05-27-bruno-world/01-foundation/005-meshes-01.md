# 005_meshes_01.py — mesh datablock chunk 2 of 7 (60 datablocks)

**Path:** `folio-2025/scripts/blender_world_steps/steps/005_meshes_01.py`
**Lines:** 770
**Adds:** 60 mesh datablocks
**Group:** [01-foundation](../01-foundation.md)

## What it does

Same construction template as [005-meshes-00.md](005-meshes-00.md). The "frozen mesh library" pattern: each mesh is built via `from_pydata` with vertex/polygon arrays, per-poly `material_index`/`use_smooth`, per-loop UVs, optional `UVMap.001`, then `me.materials.append(...)` for slot assignment.

## Mesh datablocks in this chunk (60)

Continues the `Cube.NNN` series from chunk 00:

`Cube.083`, `Cube.085`, `Cube.087`, `Cube.088`, `Cube.090`, `Cube.092`, `Cube.095`, `Cube.098`, `Cube.106`, `Cube.107`, `Cube.110..112`, `Cube.116..118`, `Cube.121..123`, `Cube.127`, `Cube.129`, `Cube.131..133`, `Cube.135`, `Cube.136`, `Cube.141`, `Cube.142`, `Cube.145..151`, `Cube.153`, `Cube.154`, `Cube.156`, `Cube.158`, `Cube.159`, `Cube.165`, `Cube.170..173`, `Cube.175`, `Cube.177..182`, `Cube.184..189`, `Cube.191`, `Cube.193`.

All 60 are `Cube.*` — this whole chunk is one slice of the cube-family library. Probable use: walls, furniture, blockouts, building blocks for the lab/altar/projects rooms.

## Key data

- **Materials touched** (from `me.materials.append` calls in this chunk): `emissiveOrangeRadialGradient`, `emissivePurpleRadialGradient`, `palette`, `redGradient`. Smaller material set than chunk 00 — these meshes are mostly palette-colored with occasional emissive accents.
- **Modifiers added**: none (modifiers are attached to objects later, in 020+).
- **Custom properties**: none on mesh datablocks.
- **World positions**: same convention — verts in world space inside `from_pydata`, mesh-origin offset baked into the data.
- **Object types**: 0.
- **Parent collection**: n/a.

## Technique / recipe

See [005-meshes-00.md](005-meshes-00.md#technique--recipe) for the full pattern.

This chunk extends Bruno's cube library — the index gaps (`.083 → .085 → .087`) mirror chunk 00's pattern (deletions never compacted). The cubes here likely cover the "blocky" props of the build: bowling alley walls, lab benches, jukebox bodies, altar steps, signs.

## Connections

- **Reads from**: 004_materials.
- **Read by**: per-section scripts 020+ that do `bpy.data.objects.new(name, bpy.data.meshes.get('Cube.NNN'))` to instance these into the scene.
- **Depends on**: 000_init, 004_materials.
- **Depended on by**: all 020-139 per-section scripts referencing any of this chunk's mesh names.

## Notable code patterns

- **Pure cube library**: 60/60 are `Cube.*`. Splitting by mesh-type+suffix-range makes each chunk's footprint roughly even (~770 lines).
- **Smaller material set than chunk 00**: only 4 distinct materials referenced. Suggests this chunk's meshes are largely interchangeable in palette role.
- All other patterns from [chunk 00](005-meshes-00.md) apply identically.
