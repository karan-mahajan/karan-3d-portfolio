# 040_bushes.py — 130 SDF foliage anchor spheres scattered world-wide

**Path:** `folio-2025/scripts/blender_world_steps/steps/040_bushes.py`
**Lines:** 1573
**Adds:** 130 objects to collection `bushes`
**Group:** [05-foliage-flowers-boundaries](../05-foliage-flowers-boundaries.md)

## What it does (code-level)

Creates collection `bushes` and links it to the scene root. Adds 130 MESH objects named `Icosphere.001` through `Icosphere.130` (non-contiguous; many numbers skipped, shared icosphere namespace). Every object uses the same mesh datablock: `bpy.data.meshes.get('Icosphere.002')`.

Per object:
- `ob.location = (x, y, z)` — z floats between 0.39–3.07, typically 0.84–1.44 (terrain height)
- `ob.rotation_euler = (0.0, 0.0, z_angle)` — Z-only rotation (a few discrete values: 0, ±0.43, ±0.48, ±0.56, ±0.77, ±1.55, ±1.75 rad)
- `ob.scale = (s, s, s)` — uniform, varies ~0.745–1.091 for size variety
- `ob.display_type = 'TEXTURED'`

No modifiers. No material assigned in this script — comes from the mesh datablock.

## Key data

- **Datablocks referenced:** mesh `Icosphere.002` (small icosphere, from 005_meshes scripts)
- **Materials assigned:** `palette` (via mesh — yellow-green bush tint `#b4b536`/`#d8cf3b`)
- **Modifiers added:** none
- **Custom properties:** none
- **World position range:** x: -78 to +86, y: -81 to +92. Full island coverage with higher density near gameplay zones (race, bowling perimeter, landing, lab edges)
- **Object types breakdown:** 130 MESH, 0 EMPTY
- **Parent collection:** `bushes` (scene root level)

## Technique / recipe

At runtime Bruno's `Foliage.js` reads the 130 `Icosphere.002` world positions and replaces each with an SDF alpha-leaf cloud using `foliageSDF.png`. The Blender mesh is a proxy — its only job is to record (x, y, z, rotation, scale) for the scatter authoring. The slight scale variation (±10%) plus the handful of discrete Z-rotations give each bush a visually distinct orientation without full random rotation.

Placement is fully hand-authored — 130 hardcoded `ob.location` calls across ~1500 lines of Python. No procedural scattering. The terrain z-sampling is approximate (the values were baked from the terrain height at authoring time, not computed).

The scale clusters reveal implicit zones: some bushes near (71–80, -6 to +3) have scale≈1.079, others near the shore have scale≈0.96. This was probably done by visual feel in the viewport.

## Connections

- **Reads from:** `005_meshes_*.py` (loads `Icosphere.002`), `004_materials.py` (palette)
- **Read by:** `999_finalize.py` (parent collection assignment); runtime `Foliage.js` (SDF cloud scatter)
- **Depends on:** `013_collections.py`
- **Depended on by:** nothing in Blender; runtime reads positions

## Notable code patterns

`Icosphere.002` vs `Icosphere.004` (trees): different mesh datablocks from the same icosphere family. Bushes use the smaller `.002` variant (probably 1–2 subdivision), trees use `.004` (more subdivisions / larger). The z-values for each bush are likely pre-sampled from the Blender terrain mesh at authoring time — they follow the gentle terrain contour of the island (higher z at rocky outcrops, ~0.84 on flat meadow).
