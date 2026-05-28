# 005_meshes_06.py — mesh datablock chunk 7 of 7 (8 datablocks, the tail)

**Path:** `folio-2025/scripts/blender_world_steps/steps/005_meshes_06.py`
**Lines:** 109
**Adds:** 8 mesh datablocks
**Group:** [01-foundation](../01-foundation.md)

## What it does

Final chunk in the 005_meshes_* series. Uses the same construction template as [005-meshes-00.md](005-meshes-00.md). Tiny file (109 lines) because only 8 meshes — they're the leftover `Text.*` glyph meshes after chunk 05's `Text.001..003`.

## Mesh datablocks in this chunk (8)

All `Text.*`: `Text.004`, `Text.005`, `Text.006`, `Text.007`, `Text.008`, `Text.009`, `Text.020`, `Text.021`.

Numbering jumps from `.009 → .020` — `.010..019` either never existed or were deleted (don't appear in any chunk).

Each Text.* mesh is **a Blender Text object converted to mesh** (extruded letter geometry):
- **`Text.004`** — 32 verts, 44 quads. Probably a letter with hole(s) like "B", "P", "R" or "O".
- **`Text.005`** — 8 verts, 8 quads. A simple rectangular letter like "I" or "L".
- **`Text.006`** — ~125 verts, ~190 quads. Complex letter / multi-glyph string.
- ...etc.

All face counts vary because each Text.* holds a different letter or short string.

## Key data

- **Materials touched**: `palette` only. **Every Text.* mesh uses a single shared material** (`palette`).
- **Modifiers**: none.
- **Custom properties**: none on meshes.
- **World positions**: baked.
- **Object types**: 0.
- **Parent collection**: n/a.

## Technique / recipe

See [005-meshes-00.md](005-meshes-00.md#technique--recipe).

**The "single UV coordinate for every loop" trick**: in `Text.004`, every loop's UV is exactly `(0.7356297969818115, 0.5)` — the same value, repeated ~146 times.

```python
_u = [[0.7356297969818115, 0.5], [0.7356297969818115, 0.5], ..., [0.7356297969818115, 0.5]]
```

This is Bruno's **"color pick from the palette strip"** technique made explicit:

- The mesh is geometry only (extruded letter)
- The material is `palette` (sampling the 128×4 PNG strip)
- All UVs map to a single point on the strip → the whole letter draws as one solid color
- Different Text.* meshes can pick different colors by changing the constant UV. Text.005 also uses `(0.7356297969818115, 0.5)` — same warm column.

**Result**: every letter in Bruno's world that uses `palette` displays as a uniform warm clay tone. No vertex colors, no per-letter material — just a constant UV.

## Connections

- **Reads from**: 004_materials (palette).
- **Read by**: scripts that place letters/text in the world (signs, billboards, navigation labels, decorative spelled-out strings).
- **Depends on**: 000_init, 004_materials.
- **Depended on by**: per-section scripts using Text.* meshes.

## Notable code patterns

- **Single-UV trick**: every loop has the **same** UV → the mesh samples one pixel from the palette PNG. This is the most explicit demonstration of the "palette as color picker" technique in the entire 005 set.
- **No `UVMap.001`**: this chunk's meshes only use one UV layer. They don't need a second UV — they have no branded texture to overlay.
- **Tiny file = end-of-series**: 005_meshes_* was designed for ~60 meshes per chunk; the last chunk has whatever's left (8 here). The chunking is a file-size budget, not a semantic group.
- All other patterns from [chunk 00](005-meshes-00.md) apply.

## Cross-chunk summary (only stated here once)

- **Total meshes across all 7 chunks: 60 × 6 + 8 = 368** ✓ (matches the index.html stat).
- **Naming families across the whole set**: Cube.* (heaviest), Plane.* (heavy), Cylinder.* (moderate), Sphere.* (12), Text.* (11), BézierCircle.*/Circle.* (~20), and the specially-named meshes (`bumpersRefrenceMesh.006`, `Mesh`, `Curve`, `Gear.*`, `Icosphere.*`, `post_skull_skull.001`, `refBowlingPin.*`, `roof.*`, `qsdqsdqsd`, `sdfsdf`).
- **Total material variants used across chunks**: roughly the full 35 from 004_materials, with `palette` overwhelmingly dominant.
- **`Plane.134`** (the terrain) is just mesh #324 (or so) in the alphabetical ordering — gets no special treatment in this stage; its 16641 verts + 16384 polys are inline like any other.
- **Chunk boundaries don't follow primitive boundaries** — they're file-size budgets that split families mid-stream (e.g., Plane.* spans chunks 03-05).
