# 092_title.001.py — knockable welcome-title letters + interaction cuboids

**Path:** `folio-2025/scripts/blender_world_steps/steps/092_title.001.py`
**Lines:** 752
**Adds:** 21 objects (10× MESH, 10× EMPTY, 1× FONT) to collection `title.001`
**Group:** [13-food-misc-fx](../13-food-misc-fx.md)

## What it does (code-level)
Builds the welcome title at the landing zone. 10 separate **letter meshes** (already converted from text — they reference `bpy.data.meshes.get('Text.002')` through `Text.021`), 1 FONT source object, and 10 cuboid EMPTY collision boxes.

Pattern per letter (10 copies, lines ~8-590):
- Create `refLettersPhysicalDynamic.010..019` from meshes `Text.002`, `Text.003`, …, `Text.021`.
- All located at `z=0.745`, rotated euler z=0.4363 rad (~25°) — the title is rotated to face spawn.
- Each gets a NODES modifier `'Smooth by Angle.003'` (the auto-smooth geometry-nodes group with `Input_1` = 0.5236 rad ≈ 30° angle threshold).
- Each gets custom prop `ob['mass'] = 0.2` — small mass so player can knock letters around.
- X positions step from 49.7 down to 38.4 along a 25° diagonal (the title reads diagonally across spawn).

After the letters, lines 60-130 add the FONT source object:
- `Text.003` (FONT type, wraps curve `Text.001`) at `(36.88, -39.80, -0.004)` rot x=π/2.
- Hidden (`hide_viewport=True, hide_render=True, hide_select=True`) — keeps the editable source curve in the file but invisible.
- Carries a SOLIDIFY modifier (thickness 0.46, offset -1.0, use_rim=True) — this is the modifier that gave the letters their depth when Bruno generated them from text.

Lines ~590-750: 10 EMPTY cuboids (`cuboid.222` through `cuboid.231`) at LOCAL positions (-1.09, -5.82) through (10.24, -0.54), all with z=0.719 and the same 25° rotation. Scale x varies (0.36 to 1.48) — these are per-letter collision boxes sized to each letter's width.

## Key data
- **Datablocks referenced**: meshes `Text.002` through `Text.021` (10 letter meshes), curve `Text.001` (the FONT source).
- **Materials assigned**: `palette` (via mesh data).
- **Modifiers added**: NODES `Smooth by Angle.003` on every letter (10 instances); SOLIDIFY on `Text.003` FONT source (thickness 0.46, EXTRUDE mode, use_rim).
- **Custom properties**: `mass = 0.2` on every letter mesh — runtime knock-physics.
- **World positions**:
  - Letters in world: X 38.4→49.7, Y -38.9→-44.2, Z=0.745 — a diagonal text line.
  - Source FONT object at `(36.88, -39.80, -0.004)`.
  - Cuboids in LOCAL space (-1.09, -5.82, 0.72) to (10.24, -0.54, 0.72) — parented to letters in 999_finalize.
- **Object types breakdown**: 10 MESH, 10 EMPTY, 1 FONT.
- **Parent collection**: `landing` (parented by 999_finalize under landing's empty anchor).

## Technique / recipe
- **One letter = one MESH** with its own per-letter `Smooth by Angle.003` modifier and `mass=0.2` custom prop. 10 visible letters, 10 cuboid collision boxes.
- **Letter generation pipeline (deduced from artifacts in this script)**: Bruno started with `Text.001` curve (font) → ran SOLIDIFY (thickness 0.46) to get depth → converted to mesh (yielding 10 `Text.NNN` meshes per glyph) → exported each as a refLetter. The FONT source is preserved but hidden — re-runnable pipeline.
- **Knockable + mass**: `mass=0.2` means player ramming into title scatters letters. The 25° rotation gives the title visual rhythm (not axis-aligned).
- **Per-letter collision sizing**: cuboid.227 has scale.x=0.36 (narrow letter, probably "I"), cuboid.229 has 1.48 (wide letter, probably "M") — width-fit collision rather than uniform.

## Connections
- **Reads from**: `001_texts.py` (curve `Text.001`), `005_meshes_*` (Text.NNN letter meshes), `003_node_groups.py` (Smooth by Angle.003).
- **Read by**: `999_finalize.py` (parents 10 letters under the landing zone root + parents 10 cuboids under their letter siblings).
- **Depends on**: foundation 001-013.
- **Depended on by**: 999_finalize.

## Notable code patterns
- **`m.show_manage_panel = True`** — Bruno consciously keeps the modifier panel open in the UI for these (vs the default False on simpler `Smooth by Angle` uses). Suggests these are hand-tuned.
- All modifier socket assignments wrapped in `try/except Exception: pass` — defensive coding against changes in Blender's modifier socket API between versions.
- Letter mesh names are `Text.002..Text.021` (mostly continuous but skipping). The skip pattern suggests Bruno deleted some glyphs from the original "TOO MANY YEARS" or similar phrase, keeping only what's used.
- The cuboid empties are at LOCAL coords near origin while their visible letter siblings are at X≈40+ in world — confirms parenting will reposition them under their letter parent.
