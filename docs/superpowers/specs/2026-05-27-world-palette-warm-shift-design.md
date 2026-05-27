# Palette controlled-warmth shift — design

**Date:** 2026-05-27
**Scope:** Sub-project **A** of the world.blend overhaul roadmap. Warm-shift three palette cells (`meadow_grass`, `dirt_path`, `sand_gravel`) without changing palette cell indices, re-bake `static/textures/palette.png` via `phase-01-palette-texture.py`, and re-export `static/world/world.glb` via `phase-13-export-glb.py` so the GLB's embedded palette image refreshes.
**Roadmap:** [`docs/superpowers/specs/2026-05-27-world-overhaul-roadmap.md`](2026-05-27-world-overhaul-roadmap.md). Blocks sub-projects B, C, D.

## Goal

Shift three palette cells from cold to warm tones while preserving the project's alpine identity. The shifts are deliberately *halfway* between our current cold values and Bruno Simon's full-warm references — alpine-with-warm-foreground, not full Bruno-coastal.

| Cell | Index | Current | Target | Reads as |
|---|---|---|---|---|
| `meadow_grass` | 16 | `#94a978` (muted sage) | `#a8b870` | olive-warm meadow |
| `dirt_path` | 23 | `#6e6256` (cold grey-brown) | `#85715a` | warm dirt path |
| `sand_gravel` | 24 | `#9a8a72` (cold tan) | `#b09778` | warm sand at the shore |

Bruno's matching references — used as a directional anchor, deliberately *not* copied:

| Bruno hex | Source | Why we stop short |
|---|---|---|
| `#b8b62e` | `Game/Terrain.js:85` — saturated yellow-olive grass | Too yellow for an alpine meadow; we land halfway to keep the grass reading as meadow, not Bruno's sun-bleached coastal grass. |
| `#a87762` | `Game/World/Floor.js:48` — terracotta slab-low | Full terracotta reads as "tile", not "dirt". We stop earlier so the path still reads as compacted earth. |
| `#ffcf8b` | `Game/World/Floor.js:47` — warm peach slab-high | Way too bright and saturated for our beach band. Skipped entirely. |

## Non-goals

- Changing palette **cell indices** or adding/removing keys in `PALETTE_COLORS`. Insertion order is load-bearing — every downstream terrain UV unwrap depends on it.
- Touching `pine_canopy` / `sunlit_pine` / any tree-adjacent cell. Trees are user-validated per project memory (`feedback_trees_already_fixed.md`).
- Touching mountain / snow / water / sky cells. Those carry the alpine identity and stay cold by design.
- Any change under `src/`, `static/textures/*` (other than the regenerated `palette.png`), `static/models/`, or `.verify/`. This is a Blender-side palette refresh only.
- Painting / authoring new textures. The 25 palette cells are the only color source.

## Architecture / data flow

```
_palette.py (3 hex edits)
        |
        |  phase-01-palette-texture.py
        v
static/textures/palette.png   (128x4 sRGB RGBA, 3 cells refreshed, 22 byte-identical)
        |
        |  phase-13-export-glb.py  (runs inside Blender)
        v
static/world/world.glb        (palette image embedded as binary buffer; terrain UVs unchanged)
```

Phase 13 exports with `export_format="GLB"`, so palette.png is embedded inside `world.glb` as a binary chunk. Reading the PNG from disk at runtime is irrelevant — the GLB's embedded copy wins. This is why phase-13 must re-run after phase-01.

## Files touched

**Edited (one file):**
- `tools/blender/scripts/_palette.py` — three string changes inside `PALETTE_COLORS`:
  - `"meadow_grass":         "#94a978",` → `"meadow_grass":         "#a8b870",`
  - `"dirt_path":            "#6e6256",` → `"dirt_path":            "#85715a",`
  - `"sand_gravel":          "#9a8a72",` → `"sand_gravel":          "#b09778",`

**Regenerated (two binaries):**
- `static/textures/palette.png` — produced by `phase-01-palette-texture.py`.
- `static/world/world.glb` — produced by `phase-13-export-glb.py`.

**Untouched:**
- Every other phase script and Blender artifact.
- Every other texture/model under `static/`.
- All runtime code under `src/`.
- All verification scripts under `.verify/`.

## Cell-index invariant

The implementation plan must explicitly assert these indices both before and after the edit (and the spec records them here as the contract):

| Cell | Index |
|---|---|
| `meadow_grass` | `16` |
| `dirt_path` | `23` |
| `sand_gravel` | `24` |

`PALETTE_CELL_INDEX` is computed from `PALETTE_COLORS` insertion order (Python 3.7+ guarantees dict order). If any other contributor re-orders, adds, or removes keys, every terrain UV pick in `phase-02-terrain.py` (and downstream phases) silently shifts to a wrong cell. The plan will include a one-liner `python3 -c "from _palette import PALETTE_CELL_INDEX; assert PALETTE_CELL_INDEX['meadow_grass'] == 16 ..."` after the edit to fail fast if anyone violated this.

## Execution order

Four sequential steps. User runs each manually; assistant never runs Blender.

1. **Edit `_palette.py`** — three hex string changes per the table above. Save.
2. **Run `phase-01-palette-texture.py`** — terminal at project root: `python3 tools/blender/scripts/phase-01-palette-texture.py`. Produces refreshed `static/textures/palette.png`. < 1 second.
3. **Run `phase-13-export-glb.py`** — open `tools/blender/world.blend` in Blender 4.2+; Scripting workspace → Text Editor → Open → select `phase-13-export-glb.py` → `Alt+P`. Pre-flight assertions run first; if they pass, GLB writes. 5-15 seconds.
4. **Visual verify in Blender** — see "Verification" below.

Phase 13's pre-flight assertions (triangle budget, section positions, etc.) are pre-existing — they do not depend on the palette edit. If they fail, that's an unrelated pre-existing issue; stop and report rather than bypass.

## Verification (visual, inside Blender)

After step 3 completes, while still in Blender:

a. Set the 3D viewport to **Material Preview** shading (top-right of the viewport).
b. Frame the spawn area (walkable plateau + cardinal paths).
c. Confirm three positive changes:
   - The walkable grass band reads visibly warmer/more olive (not yellow — olive).
   - The cardinal paths read as warmer "sun-baked dirt", less cold grey-brown.
   - The shore/beach band reads as warm sand.
d. Confirm three "must NOT change" surfaces:
   - Mountain bands look identical to before.
   - Snow caps look identical to before.
   - Any river / lake / water surface looks identical to before.
e. Inspect the palette PNG. Three cells visibly warmer; 22 cells unchanged.

Pass criteria: (c) all three changed as expected AND (d) all three unchanged. If any (d) surface shifted, palette ordering broke — roll back via `git restore tools/blender/scripts/_palette.py static/textures/palette.png static/world/world.glb` and re-investigate.

The implementation plan will require the user to commit only AFTER step (e) passes; no commit happens during the brainstorm phase.

## Rollback

If verification fails:

```bash
git restore tools/blender/scripts/_palette.py \
            static/textures/palette.png \
            static/world/world.glb
```

That cleanly reverts the three artifacts to the last committed state. Re-open `world.blend` in Blender to discard any in-memory state; do not save.

## Open items

- **GLB embedding format double-check.** The plan should verify (via `gltf-transform inspect static/world/world.glb` or equivalent) that the GLB does embed palette.png as a binary chunk — confirming our load-bearing assumption that phase-13 is mandatory after phase-01. Out-of-scope for this spec; flagged as an early plan step.
- **Memory update.** Per the project's "don't auto-update memory until I confirm" rule, no memory entry until the user confirms visual verification passes.
