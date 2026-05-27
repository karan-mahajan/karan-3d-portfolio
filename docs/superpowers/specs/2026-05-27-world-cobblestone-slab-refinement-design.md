# Cobblestone slab refinement — design

**Date:** 2026-05-27
**Scope:** Sub-project **C** of the world.blend overhaul roadmap. Refine the cobblestone slab material's terrain coverage and tiling density to fit the warm-shifted meadow from sub-project A. Color stops (Bruno's `#a87762` grout + `#ffcf8b` slab face) stay untouched.
**Roadmap:** [`docs/superpowers/specs/2026-05-27-world-overhaul-roadmap.md`](2026-05-27-world-overhaul-roadmap.md). Depends on sub-project A (committed `96a82e4`). Does not block subsequent sub-projects.

## Goal

After sub-project A warm-shifted `meadow_grass` (cell 16) to `#a8b870`, the slab material — which currently paints OVER three palette cells (`dirt_path`, `meadow_grass`, `rock_mid`) with a uniform cream-and-brown cobblestone — was hiding most of that meadow shift. The goal is to **expose the meadow and ridge as their natural palette colors and confine the cobblestone to the cardinal paths only**, then make the path tiling denser so it reads as a clearly mosaiced path rather than a sparse stepping-stone effect.

The end-state is that the spawn area reads as:
- **Cardinal paths** — visibly dense warm cobblestone (Bruno's `#a87762` / `#ffcf8b` ColorRamp, ~6 stones across each 3m path).
- **Meadow plateau** — uniform warm olive `#a8b870` from sub-project A, exposed across the rest of the walkable plateau between paths.
- **NE ridge top** (`ridge_h > 8m`, peak at +12m) — cold rock grey `rock_mid` `#5d6770`, reading as exposed alpine outcrop against the warm meadow.

## Decision summary

Three knobs were live during brainstorm; outcomes and rationale recorded here as the load-bearing record:

| Knob | Decision | Constant change |
|---|---|---|
| **Slab coverage** | Paths only — meadow and ridge expose their palette cells | `SLAB_COLOR_KEYS = {"dirt_path", "meadow_grass", "rock_mid"}` → `{"dirt_path"}` |
| **Slab colors** | Keep Bruno's exact pair | No change to `SLAB_LOW_COLOR` / `SLAB_HIGH_COLOR` |
| **Tile density** | Denser — ~6 stones across each 3m path | `SLAB_UV_SCALE = 0.175` → `0.35` |

**Why "paths only" (not "everywhere" or "kill the material"):** The roadmap framing says "slabs read as warm-paved path against the new warm meadow." That phrasing presumes meadow is visible. Keeping the slab material in place but shrinking its coverage to one cell preserves the option to add cells back later without un-refactoring; killing the material would force a re-add if any future surface should be slabbed (e.g., a paved spawn plaza in a later sub-project).

**Why Bruno's exact colors (not palette-derived or stone-grey):** The `#ffcf8b` / `#a87762` pair was tuned by Bruno against a *warm* palette and our destination palette is now warm — they still read as paved-paths-against-meadow. Re-deriving slab colors from palette cells (e.g. `sun_glow` + `wood_lantern_body`) was a real alternative; rejected because (a) Bruno's pair has a wider luma gap that produces crisper stripe contrast, and (b) future palette tweaks shouldn't auto-propagate into the slab material — slabs are a deliberate creative choice, not a derived value.

**Why denser tiling (0.35, not 0.175 or 0.10):** Bruno's `0.175` was tuned for his full-plateau cobblestone courtyard (~6m-wide UV-tile, viewed across an open paved area). Our paths are only 3m wide; at `0.175` the player sees roughly half a PNG-tile width across the path, which reads as visually sparse. Doubling to `0.35` puts ~6 stones across the path width — a clearly mosaiced cobblestone strip without becoming visual noise.

## Non-goals

- Changing the slab material's color stops (`SLAB_LOW_COLOR` / `SLAB_HIGH_COLOR`). The ColorRamp recipe stays Bruno's recipe.
- Changing the `slabs.png` source texture under `static/textures/ground/stone/`. The PNG is Bruno's verbatim; tile density change is a UV-scale change, not a texture change.
- Refactoring `SLAB_COLOR_KEYS` from a `set` to a singular `SLAB_KEY` string. Brainstorm explicitly chose "Approach 1 — minimal edit" over the refactor; leaves room for future slab-coverage experiments without un-refactoring.
- Removing the slab material entirely. Material slot 1 stays attached to `terrain_mesh`; only the face-to-slot assignment loop reassigns most faces back to slot 0 at bake time.
- Cleaning up the wasteful "paint slabs UV layer on every face" loop at [phase-02-terrain.py:369-371](../../tools/blender/scripts/phase-02-terrain.py#L369-L371). Most faces now drop their slabs-UV after bake (slot 0 doesn't read it), but writing it costs no runtime and keeps the bake path simple. Defer cleanup.
- Any change under `src/`, `static/models/`, `static/textures/` (other than the regenerated `world.glb` which incidentally embeds the palette PNG; that PNG is unchanged from A).
- Touching any other phase script. Only `phase-02-terrain.py` is edited; `phase-13-export-glb.py` is invoked (to refresh `world.glb`) but not modified.

## Architecture / data flow

```
phase-02-terrain.py (2 constant edits + 1 comment update)
        |
        |  Re-run inside Blender (Alt+P) OR headless via Blender --background
        v
terrain_mesh (rebuilt in world.blend):
        - 193x193 heightfield (unchanged geometry)
        - palette UV layer (unchanged values)
        - slabs UV layer (every face's UV doubled: SLAB_UV_SCALE 0.175 -> 0.35)
        - material_index per face REASSIGNED:
              dirt_path faces -> slot 1 (slabs)
              meadow_grass / rock_mid / sand_gravel / deeper_water -> slot 0 (palette)
        |
        |  phase-13-export-glb.py (in Blender)
        v
static/world/world.glb (rebuilt):
        - terrain primitives reshuffled: slabs-primitive triangle count shrinks,
          palette-primitive triangle count grows
        - palette.png + slabs.png + mountain band PNGs all re-embedded (unchanged
          bytes, same materials)
```

`phase-02-terrain.py` does not change the heightfield itself — only the per-face material slot assignment + UV scale on the slabs layer. The geometry, ref empties, trimesh collider, and `height_at` helper are unaffected.

Phase 13 then re-exports `world.glb` with `export_format="GLB"`, embedding the unchanged palette and slabs PNGs into the binary buffer. The GLB-side change is purely in the mesh data (material indices + UV values), not in any image.

## Files touched

**Edited (one file):**

- `tools/blender/scripts/phase-02-terrain.py`:
  - Comment block at lines 124-128 — rewrite to reflect new coverage (paths only) and new UV-scale math (`0.35 → ~2.86m per 256px repeat → ~22cm per cobblestone tile`).
  - `SLAB_UV_SCALE = 0.175` → `SLAB_UV_SCALE = 0.35` (line 129).
  - `SLAB_COLOR_KEYS = {"dirt_path", "meadow_grass", "rock_mid"}` → `SLAB_COLOR_KEYS = {"dirt_path"}` (line 130).

**Regenerated (one binary):**

- `static/world/world.glb` — produced by `phase-13-export-glb.py` after `phase-02-terrain.py` is re-run.

**Modified-then-restored (one file):**

- `tools/blender/world.blend` — `phase-13-export-glb.py` calls `bpy.ops.wm.save_as_mainfile()` at end of export, modifying the .blend metadata. Per auto-memory `project-phase13-saves-blend` this is a known side-effect; we `git restore` the .blend at end of execution unless intentional .blend edits were made (none in this sub-project).

**Untouched (referenced for clarity):**

- `tools/blender/scripts/_palette.py` — palette cell hexes from sub-project A stay.
- `tools/blender/scripts/_lib.py` — `palette_uv()`, `paint_face()`, `attach_palette_material()` unchanged.
- `static/textures/palette.png` — unchanged from sub-project A.
- `static/textures/ground/stone/slabs.png` — unchanged (Bruno's verbatim).
- All other `phase-*.py` scripts — unchanged.

## Behavioral effects

### Visual changes in the spawn area

1. **Walkable plateau exposed** — the broad meadow area between paths, previously hidden under cobblestone, now shows `meadow_grass` (`#a8b870`, warm olive from A). This intentionally creates "empty meadow" that Bruno-density future work (foliage carpet, ground bushes per auto-memory `project-world-vision-bruno-density`) will fill in later sub-projects. Calling this out as deliberate transitional state.
2. **NE ridge top now cold rock grey** — high-ridge faces (`ridge_h_at_face > 8.0`, peak +12m along (0,0)→(15,95)) revert to `rock_mid` palette `#5d6770`. Reads as exposed alpine outcrop punctuating the warm meadow.
3. **Cardinal paths visibly denser cobblestone** — each 3m-wide path now shows ~6 stones across vs ~3 before. Mosaic-feeling, paved-trail aesthetic.
4. **Sand transition + ocean unchanged** — `sand_gravel` (cell 24, warm tan) and `deeper_water` (cell 18, cold blue) were already palette slot 0 before C. Their colors come straight from sub-project A's palette and read identically.

### Code/data structural changes in `world.glb`

- `world_palette_material` primitive grows: now contains meadow + ridge + sand + water faces (was only sand + water).
- `world_slabs_material` primitive shrinks: now contains only the ~3m-wide cardinal corridor faces inside r=20 (was meadow + paths + ridge across the whole plateau).
- Both primitive counts in `gltf-transform inspect` stay at 1 each (no primitive added or removed; just face redistribution).
- Total terrain triangle count unchanged (~36k quads, ~72k tris).
- `slabs` UV layer values doubled across every face (consequence of `SLAB_UV_SCALE` 0.175→0.35); only the 1 slab primitive actually reads this layer at render time.

### What does NOT change

- Heightfield (no terrain re-sculpt).
- `trimesh_terrain` collider (still derived from `terrain_mesh`, geometry unchanged).
- Ref empties (`refSpawnPoint`, `refPath_*`, `refRespawn_origin`) — positions sampled from unchanged heightfield.
- `height_at(x, z)` helper output (unchanged, used by phases 3-11 for prop placement).
- Phases 3-12's prop placements (signs, billboards, lighthouse, observatory, etc.) — they sit on `height_at` which is unchanged.
- Palette PNG, mountain band PNGs, slabs PNG — all bytes-for-bytes identical to current state.

## Verification

Three independent signals, mirroring the multi-source approach validated in sub-project A. None of them rely on Material Preview HDRI for color judgments.

### 1. Pre-edit pipeline check

Same shape as sub-project A's Task 0:
- `git status --short` clean for the three artifacts about to change.
- `phase-02-terrain.py` lines 124-130 match expected current state (sanity that we're not editing against a drifted file).
- `phase-13-export-glb.py` still imports `_palette` + `_lib` and runs assertions on triangle budget etc. (already proven during sub-project A — listed here for completeness, not to re-run).

### 2. Post-edit structural verification

- **Phase-02 log diff**: `phase-02-terrain.py` already prints `slabs:N / palette:M` at line 540-541. Capture before-vs-after counts. Expected direction: `slabs` count shrinks ~10x (only the ~3m-wide cardinal corridors), `palette` count absorbs the difference.
- **GLB primitive inspect**: `npx gltf-transform inspect static/world/world.glb` should still show both materials with `instances: 1`. The `Meshes` table will show the slab primitive's triangle count dropping and the palette primitive's growing. Total triangle count for the terrain mesh stays the same.
- **Phase-02 self-assertions**: triangle budget check at end of phase-13 still passes (no geometry change).

### 3. Visual sanity (Blender Material Preview)

Material Preview is *unreliable for subtle hue shifts* (per auto-memory `feedback-palette-verify-via-pixel-diff`) but *very reliable for structural changes like "this whole region switched material"*. The C changes are structural — meadow surface flips from cobblestone to flat olive, ridge from cobblestone to flat grey. These are obviously visible at a glance and don't need pixel-level verification.

Checklist (in Material Preview, top-down view of spawn area):
- Cardinal paths: visibly dense cobblestone stripes ✓
- Meadow between paths: uniform warm olive ✓
- NE ridge top: cold grey rock outcrop ✓
- Outer ring (sand) and ocean: unchanged ✓

## Rollback

If any verification step fails (script error, unexpected geometry shift, visual surprise the user rejects):

```
git restore tools/blender/scripts/phase-02-terrain.py \
            static/world/world.glb \
            tools/blender/world.blend
```

This is non-destructive — restores all three files to HEAD. Since the spec + plan files are **un-committed at execution time** (per auto-memory `feedback-no-intermediate-commits`), they stay in the working tree for re-iteration without needing a git operation.

## Future work explicitly deferred

These follow the same principle ("separate tasks") that the user reinforced during C's brainstorm. They are **not** prerequisites for C and **not** consequences of C; they are forward-looking Bruno-density items per auto-memory `project-world-vision-bruno-density`:

- **Foliage carpet on the now-exposed meadow** — Bruno's SDF Foliage system covering the walkable plateau. Highest priority once C lands, because C deliberately exposes empty meadow that this fills.
- **Animated grass with wind motion** — runtime/shader work, not Blender.
- **Inner ponds / small disconnected water bodies** — terrain-resculpt territory, fits sub-project E.
- **Organic island outline (non-circular)** — also sub-project E.
- **Warm halo / aura around vegetation + water** — runtime post-processing or world-lighting pass.
- **Multiple "zones" with distinct surface treatments** — depends on inner ponds + foliage existing; later.

## Open questions

None as of this writing. The brainstorm closed all three knob decisions; no architectural unknowns remain; verification path uses already-validated patterns from sub-project A.
