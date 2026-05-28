# 005_meshes_03.py — mesh datablock chunk 4 of 7 (60 datablocks)

**Path:** `folio-2025/scripts/blender_world_steps/steps/005_meshes_03.py`
**Lines:** 759
**Adds:** 60 mesh datablocks
**Group:** [01-foundation](../01-foundation.md)

## What it does

Same template as [005-meshes-00.md](005-meshes-00.md). Per-mesh: `from_pydata` → polygon material/smooth arrays → UV layers → `me.materials.append(...)`.

## Mesh datablocks in this chunk (60)

The most heterogeneous chunk — cylinders, gears, icospheres, the special `Mesh` datablock, and the start of the Plane series:

`Cylinder.029`, `Cylinder.030`, `Cylinder.032..038`, `Cylinder.040`, `Cylinder.042`, `Cylinder.044`, `Cylinder.051`, `Cylinder.054`, `Cylinder.059`, `Cylinder.061`, `Cylinder.069`, `Cylinder.072`, `Cylinder.073`, `Cylinder.075..077`, `Cylinder.081`, `Gear.005`, `Gear.008`, `Gear.015`, `Icosphere.001..005`, `Mesh`, `Plane.001..028`.

Notable named meshes:
- **`Gear.005/.008/.015`** — three gear-shaped meshes (probably used by a gear prop in the lab or workshop area).
- **`Icosphere.001..005`** — five icosphere meshes (rounded balls — possible uses: marbles, lanterns, head shapes, low-poly fruits).
- **`Mesh`** — a single mesh datablock with the literal name "Mesh". Unusual. Likely a placeholder or one-off prop.
- **`Plane.001..028`** — beginning of the heavy Plane.NNN sequence. Planes are flat surfaces — used for billboards, signs, road segments, ground decals, projection masks.

## Key data

- **Materials touched**: `airDancer`, `circuitBrand`, `circuitWebgpu`, `cookieBanner`, `darkGray`, `emissiveOrangeRadialGradient`, `emissivePurpleRadialGradient`, `grass`, `labCarpet`, `mapAltar`, `mapPortal`, `palette`, `projectsCarpet`.
  - **Widest material set of any chunk so far** — touches the lab area (`labCarpet`, `mapAltar`, `mapPortal`), the projects area (`projectsCarpet`), the circuit branding (`circuitBrand`, `circuitWebgpu`), the cookie banner, the air dancer face, and standard palette + emissive.
  - First chunk with `grass` material assigned — possibly to a foliage or grass-blade mesh template.
- **Modifiers**: none.
- **Custom properties**: none on meshes.
- **World positions**: baked into vert arrays.
- **Object types**: 0.
- **Parent collection**: n/a.

## Technique / recipe

See [005-meshes-00.md](005-meshes-00.md#technique--recipe).

This chunk likely contains many "feature" meshes — meshes that drive specific sections rather than being generic palette-cube reuse. The presence of `mapAltar`, `mapPortal`, `labCarpet`, `projectsCarpet`, and `cookieBanner` materials means several "screen" or "carpet" Plane meshes live here, each unwrapped to fit its branded texture.

## Connections

- **Reads from**: 004_materials.
- **Read by**: lab area (053), projects area (062), circuit area (075), cookie-banner prop (in misc scripts).
- **Depends on**: 000_init, 004_materials.
- **Depended on by**: 020-139.

## Notable code patterns

- **Heterogeneous primitives**: combines four primitive families (Cylinder, Gear, Icosphere, Plane) plus the singleton `Mesh`. The chunk is a "junction" between primitive types in the alphabetical sort.
- **First chunk to reference area-specific materials** (labCarpet, projectsCarpet, mapAltar/Portal): the meshes those materials are bound to are the **screen/carpet planes** for those sections.
- All other patterns from [chunk 00](005-meshes-00.md) apply.
