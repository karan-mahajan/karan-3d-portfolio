# 005_meshes_02.py — mesh datablock chunk 3 of 7 (60 datablocks)

**Path:** `folio-2025/scripts/blender_world_steps/steps/005_meshes_02.py`
**Lines:** 790
**Adds:** 60 mesh datablocks
**Group:** [01-foundation](../01-foundation.md)

## What it does

Same template as [005-meshes-00.md](005-meshes-00.md). Per-mesh: `from_pydata` → polygon material/smooth arrays → UV layers → `me.materials.append(...)`.

## Mesh datablocks in this chunk (60)

End of the Cube series, plus all Cylinder primitives, plus the bare `Curve` mesh:

`Cube.194`, `Cube.195`, `Cube.197..202`, `Cube.205`, `Cube.207`, `Cube.208`, `Cube.210..212`, `Cube.214..217`, `Cube.220`, `Cube.222`, `Cube.223`, `Cube.225`, `Cube.227`, `Cube.228`, `Cube.230`, `Cube.231`, `Cube.234`, `Cube.236`, `Cube.238`, `Cube.240`, `Cube.243`, `Curve`, `Cylinder`, `Cylinder.001..024`, `Cylinder.026..028`.

This chunk straddles two primitive families — the tail of `Cube.*` and the start of `Cylinder.*`.

## Key data

- **Materials touched**: `circuitThreejs`, `circuitWebgl`, `circuitWebgpu`, `darkGray`, `emissiveBlueRadialGradient`, `emissiveOrangeRadialGradient`, `emissivePurpleRadialGradient`, `palette`, `redGradient`, `waterfall`.
  - Wider material set than chunks 00/01 — this chunk includes meshes for the **race-circuit branded signs** (the three circuit logos) and probably the **waterfall** column mesh.
- **Modifiers**: none here.
- **Custom properties**: none.
- **World positions**: in `from_pydata` arrays, mesh-origin offsets baked.
- **Object types**: 0.
- **Parent collection**: n/a.

## Technique / recipe

See [005-meshes-00.md](005-meshes-00.md#technique--recipe).

`Cylinder` and `Cylinder.001` are likely the heavy-use cylinder templates Bruno reuses for **pillars, lanterns, bowling pins, pole bases, can/cup props**. The Cylinder primitives have radial UV layouts naturally — the cap and side are unwrapped to separate UV islands by Blender's default cylinder unwrap.

`Curve` (as a mesh, not a curve datablock!) is unusual — most curves live in `007_curves.py`. A mesh named exactly `Curve` is likely the converted/applied output of a curve-to-mesh operation Bruno baked at some point.

## Connections

- **Reads from**: 004_materials.
- **Read by**: per-section scripts (notably race-track scripts that look up `circuitWebgl/Threejs/Webgpu` materials and bind them to specific meshes here).
- **Depends on**: 000_init, 004_materials.
- **Depended on by**: 020-139.

## Notable code patterns

- **First chunk with circuit-branded materials in the slot list**: the circuit-logo meshes are in this chunk, so they're the ones with `circuitWebgl/Threejs/Webgpu` in their `me.materials.append(...)`.
- **`waterfall` material appears here**: the waterfall column mesh — exact mesh name not surfaced, but one of the cylinders/cubes in this chunk has the waterfall material attached.
- All other patterns from [chunk 00](005-meshes-00.md) apply.
