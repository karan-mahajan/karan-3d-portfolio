# 005_meshes_05.py — mesh datablock chunk 6 of 7 (60 datablocks)

**Path:** `folio-2025/scripts/blender_world_steps/steps/005_meshes_05.py`
**Lines:** 803
**Adds:** 60 mesh datablocks
**Group:** [01-foundation](../01-foundation.md)

## What it does

Same template as [005-meshes-00.md](005-meshes-00.md).

## Mesh datablocks in this chunk (60)

The end of `Plane.*`, several specially-named meshes, the start of `Sphere.*`, and the start of `Text.*`:

`Plane.096..098`, `Plane.102..105`, `Plane.108..110`, `Plane.112..116`, `Plane.119..121`, `Plane.123`, `Plane.124`, `Plane.126..131`, `Plane.133`, **`Plane.134`** (= the terrain!), `Plane.135`, `Plane.139`, `Plane.143..146`, `Plane.150..152`, `post_skull_skull.001`, `qsdqsdqsd`, `refBowlingPin.001`, `refBowlingPin.003`, `roof.001`, `roof.002`, `sdfsdf`, `Sphere`, `Sphere.001..012`, `Text.001..003`.

**Special named meshes:**
- **`Plane.134`** — THE terrain mesh. The single subdivided plane that 020_terrain.py binds the Geometry-Nodes modifier to. Lives in this chunk.
- **`post_skull_skull.001`** — clearly a Halloween/spooky prop (probably for the skull-decorated lamp posts).
- **`refBowlingPin.001/.003`** — bowling-pin reference mesh templates (used by the bowling area script).
- **`roof.001/.002`** — roof mesh templates (used by buildings).
- **`Sphere` + `Sphere.001..012`** — 13 sphere meshes (lanterns, light bulbs, decorative balls).
- **`Text.001..003`** — first three text glyph meshes; the rest run into chunk 06.

**Authoring leftovers:**
- **`qsdqsdqsd`** and **`sdfsdf`** — keyboard-mash placeholder names. These are unfinished / WIP / scratch meshes that Bruno never renamed. They survived through to the published .blend and out into the per-script export. Whether they're actually used by any later script is worth confirming via grep.

## Key data

- **Materials touched**: `blackboardLabels`, `bowlingLabelStrike`, `careerTextFreelancer`, `careerTextIRLTeacher`, `careerTextUzik`, `circuitBrand`, `darkGray`, `emissiveBlueRadialGradient`, `emissiveOrangeRadialGradient`, `emissivePurpleRadialGradient`, `emissiveWhiteRadialGradient`, `palette`, `redGradient`.
  - Three more `careerText*` materials here (Freelancer, IRLTeacher, Uzik) — completing the 6-material career set across chunks 04+05.
  - `bowlingLabelStrike` is in this chunk → the bowling-strike-label plane is one of the Plane.* meshes here.
- **Modifiers**: none.
- **Custom properties**: none on meshes.
- **World positions**: baked.
- **Object types**: 0.
- **Parent collection**: n/a.

## Technique / recipe

See [005-meshes-00.md](005-meshes-00.md#technique--recipe).

**The terrain mesh `Plane.134` is created here exactly like every other Plane** — `from_pydata([vert array of 16641 verts], [], [poly array of 16384 quads])`. The huge embedded vert/poly arrays for `Plane.134` are most of this chunk's file size. The mesh is a 128×128-subdivided plane (16641 = 129² verts, 16384 = 128² polys). No modifier or scatter happens here — that's bound in 020_terrain.

## Connections

- **Reads from**: 004_materials.
- **Read by**: 020_terrain (binds modifier to `Plane.134`); bowling scripts (`refBowlingPin.001/.003`); building scripts (`roof.001/.002`); skull-lamp prop scripts (`post_skull_skull.001`); any later script needing the listed Plane.* meshes.
- **Depends on**: 000_init, 004_materials.
- **Depended on by**: 020 (terrain), bowling area (054-060), buildings (047, 049), street lights / spooky props.

## Notable code patterns

- **Terrain mesh lives here, in chunk 05**: `Plane.134` is just one of 60 in the list. No special treatment at this stage. All the magic happens in 020_terrain's modifier binding.
- **Scratch-name meshes (`qsdqsdqsd`, `sdfsdf`) survive the pipeline**: Bruno's published build script exports unfinished placeholders. They're either truly unused or wired up under similarly-rough names later. Either way, this confirms Bruno doesn't aggressively clean before exporting.
- **First Sphere chunk + first Text chunk**: this is the multi-family chunk (Plane → Sphere → Text). Mesh-type boundaries don't align with file-chunk boundaries.
- All other patterns from [chunk 00](005-meshes-00.md) apply.
