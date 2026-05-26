# Blender world-build — resume handoff

> **For a fresh Claude Code session.** Paste the prompt at the very bottom into a new session to continue from Phase 12 (mountains, asset-gated) onward.

## Where the work is

- Repo: `/Users/mahajankaran/Documents/Projects/karan-portfolio`
- Branch: `world-v2-blender-build` (NOT pushed — local only)
- Spec: [`docs/superpowers/specs/2026-05-26-world-design.md`](../specs/2026-05-26-world-design.md)
- Plan: [`docs/superpowers/plans/2026-05-26-v2-world-blender-build.md`](../plans/2026-05-26-v2-world-blender-build.md)
- This doc: handoff so a fresh session can pick up without dragging in the prior conversation context.

## Phases completed

| Phase | Commit | What it produced |
|---|---|---|
| 0 | `f7aee10` | Scene scaffolding: collections per spec §11.5, `_palette.py` (25 colors), `_lib.py` (helpers), `phase-00-setup.py`, `tools/blender/world.blend` seed |
| 1 | `df27cb2` | `static/textures/palette.png` (128×4 sRGB, pure stdlib encoder) |
| 2 | `0fdbf9b` | Terrain (193×193-vert sculpted heightfield, NE ridge, W cliff trench under waterfall) + `trimesh_terrain` collider + `_lib.height_at()` helper |
| 3 | `3503d43` | Spawn cluster (wayfinder obelisk + hearth ring + lectern + 4 path stubs) + colliders + refs |
| 4 | `d367346` | Projects workshop pavilion at +70 east — open-front stone+timber pavilion, anvil, forge + chimney, 5-tool wall, 4m showcase panel for runtime billboard. **Lifted Phase 3's bmesh helpers into `_lib.py`** (`bm_add_cuboid`, `bm_add_cylinder`, `bm_finalize_to_object`, `paint_face`, `replace_object`, `attach_palette_material`, `get_palette_material`). |
| 5 | `5b1ad2f` | Skills observatory tower at -70 south — banded stone shaft, copper half-sphere dome (added local `_bm_add_dome` helper), cupola lantern with `_emissive` suffix, brass telescope on wooden tripod, 4 artifacts (lectern, scrolls, books, chest) ringing the base. **Door on the NORTH face** (player approaches from spawn). |
| 6 | `36ff5f8` | Experience cairn trail at +70 north — Catmull-Rom bezier from spawn bridge up to summit (+15, +95), 80-sample 3-strip ribbon (sand_gravel edges, dirt_path center), 5 stepping stones at steep mid-section, 7 cairns (stones 3/4/5/4/3/4/3) each with copper lantern + emissive cap, refCairnLantern_1..7. |
| 7 | `7b1a024` | Contact cliff beacon at -70 west — 3×3m stone platform with sand_gravel rim lip, 3-leg iron tripod brazier (dark_rock_shadow legs splayed 22.5°), bowl + 8-sided warm flame cone (`brazier_flame_emissive`), inscription plinth. |
| 8 | `1f5452c` | Lighthouse + islet offshore at (-130, +35) — top-level `lighthouse` collection. Irregular 3m islet, 8m tapered tower with 3 white bands, glass cupola (new `world_palette_glass_material` clone), warm lamp, 20m beam parented to `refLighthouseBeamPivot` (runtime sweeps via Z rotation). 0 colliders (past r=120 soft-clamp). |
| 9 | `4f4ec70` | River + tributary + waterfall + ocean + bridges. 12-control-point Catmull-Rom main river (variable 2-5m width, 120 samples), 4-control tributary (1.5m). 3 new material clones: `world_palette_ocean_material`, `world_palette_water_material`, `world_palette_waterfall_material` (runtime detects by `*ocean*`/`*water*`/`*waterfall*` name tokens). 200×200m ocean plane at y=-1.5. Main bridge (8 planks + 2 cylinder supports) anchored to closest-to-z=+4 river sample. 3 stepping stones over tributary. |
| 10 | `02b37eb` | Hiking trail loop + 3 viewpoint detours. Closed-loop Catmull-Rom perimeter (12 control points at ~80m radius, 180 samples) avoiding the 4 cardinal sections. 3 open-spur detours: NW cliff (-76, +45), summit (+15, +95) sharing the cairn trail terminus, SE (+45, -85). 3 rock_mid waystones with tangent-derived carved-face painting + `refViewpoint_*` empties carrying `{ "viewpoint": "<key>" }` userData. |
| 11 | `0f9d408` | Foliage + props pass. **3 implementer iterations:** initial pass → tree variety revamp → bench/sign placement fix. Final state: 10 pine variants (classic / tall-narrow / short-wide / leaning / bushy / autumn / deep-shade / meadow-green) using stacked icosphere clumps (NOT cone-stacks); 5 birch variants with branches + multi-clump foliage; 1 hero pine. 4 bush variants (NEW). Boulders sized 0.35m→2.25m. Density bumped +20% (110 pines + 42 birches + 5 hero + 48 ferns + 96 flowers + 40 boulders + 50 bushes). New top-level `props/` collection: 3 wooden benches (offset to perimeter-side of waystones), 5 trail signs (thicker post + larger plank after fix), 6 hand-placed boulder clusters. 5 `refHeroTree_*` + 3 `refBench_*`. |

`git log --oneline world-v2-blender-build` to confirm.

## Phases remaining (each = one fresh subagent dispatch)

12. Mountain cardboard bands (4 quads — **NEEDS user-painted PNGs**, see below)
13. Export `world.glb` + assertions

## Phase 12 asset gate — CRITICAL FIRST STEP

**The user committed to painting the 4 PNGs themselves** (not procedural placeholders). Phase 12 cannot dispatch until these files exist:

- `static/textures/mountains/mountain-front-ridge.png`
- `static/textures/mountains/mountain-mid-peaks.png`
- `static/textures/mountains/mountain-far-snow.png`
- `static/textures/mountains/mountain-foothills-east.png`

Specs:
- Dimensions: 2048×512 px each
- sRGB
- PNG with alpha channel (sky portion = transparent)
- Use only the 25 palette colors (snow caps in `#fff5dc`)
- Save to: `static/textures/mountains/` (dir already exists, empty)

The user has `static/textures/palette.png` (128×4) as a color-picker reference — they can eyedrop the exact palette colors from there.

**Color guidance per file** (provided to user):
- `mountain-front-ridge.png`: rock body `#5d6770`, snow caps `#fff5dc`, shadow `#4a525c`. Sharpest contrast (closest layer).
- `mountain-mid-peaks.png`: rock `#7e898d`, snow `#fff5dc`+`#d8c8d6`, shadow `#4a525c`. Prominent snow caps.
- `mountain-far-snow.png`: rock `#9ea7ab`, snow `#c8c8d4`+`#fff5dc`. Heavily faded.
- `mountain-foothills-east.png`: `#5d6770` + `#6e6256` + `#94a978` lower. Shorter silhouette, no snow.

**When the user says "PNGs ready" or similar → dispatch Phase 12 implementer.** Phase 12 script must assert all 4 files exist before building geometry; halt with clear error if any missing.

## Locked conventions — DO NOT relitigate

These were settled during the live build. Re-explaining them costs the user time.

### Branch + commit policy
- All Phase work goes to `world-v2-blender-build`. NEVER directly to `main`. NEVER pushed without user OK.
- **NEVER commit without explicit user approval.** Subagents stage with `git add <specific paths>`; the human-running-Claude does the commit only after the user replies "Phase N approved" (or "approved" / "looks good commit it").
- **NEVER use `Co-Authored-By: Claude` trailer.** User memory `feedback_no_claude_coauthor` is explicit. Commit message body fine, no trailer.
- Stage with explicit paths. NEVER `git add -A`.

### Coordinate system
- **Blender Z-up authoring.** Runtime is Three.js Y-up; Phase 13 exporter handles the swap.
- Mapping: Blender X = runtime X (E-W); Blender Y = runtime Z (N-S, +Y north); Blender Z = runtime Y (height).
- Helper `_lib.height_at(runtime_x, runtime_z)` returns runtime Y. Pass to Blender location as `(x, z, height)`.
- `_lib.ref_empty(name, location=(x, height, z), radius=...)` accepts runtime order — internally places at Blender `(x, z, height)`.

### Save pattern
- Every phase script ends with `bpy.ops.wm.save_as_mainfile(filepath=<abs world.blend path>)`. NOT `save_mainfile()`.
- `_script_dir()` block from `phase-00-setup.py` handles Blender's bogus `__file__` — copy verbatim every script.

### Script structure
- Each phase = one script `tools/blender/scripts/phase-NN-name.py`, idempotent (clears its own collection at start).
- All scripts share `_lib.py` + `_palette.py`. Lift new helpers into `_lib.py` only when 2+ phases need them (Phase 2 added `height_at`; Phase 4 lifted the bmesh helpers).
- Comments only explain non-obvious WHY. No emojis. No comments restating code.
- bmesh for geometry; NOT `bpy.ops.mesh.primitive_*`.

### Palette colors
- 25 locked colors in `_palette.PALETTE_COLORS`. Every face's UV must snap to one of these cells. No new colors without re-baking palette.png.
- `_lib.palette_uv("rock_mid")` is the convenience wrapper. `_lib.bm_add_*` helpers take a `color_key` arg directly.

### Collider naming (spec §11.2)
- `cuboid_*`, `tube_*`, `trimesh_*` prefixes. Phase 13 exporter parses by name.
- Colliders live in the same collection as their visible mesh, hidden via `obj.hide_viewport = True` + `obj.hide_render = True`. Palette material attached for consistency.

### Ref empties (spec §11.3)
- `refZoneBounding_<section>` (~12-14m), `refZoneFrustum_<section>` (~9-11m), `refInteractivePoint_<section>`, `refRespawn_<section>`, plus anchors like `refForge`, `refBrazier`, `refCairnLantern_<n>`, `refHeroTree_<n>`, `refBench_<key>`, `refViewpoint_<key>`, `refShowcaseMount`, `refLighthouseBeamPivot`, `refWaterfallSpray`, `refRiverSource`.
- Custom properties via `_lib.ref_empty(... userdata={...})`.

### Emissive name suffix contract
- Any mesh whose name ends `_emissive` is detected by the runtime and gets its material swapped to the emissive variant. Examples already in scene: `hearth_embers_emissive`, `forge_embers_emissive`, `cupola_lantern_emissive`, `brazier_flame_emissive`, `lighthouse_lamp_emissive`, all `experience_cairn_lantern_*_emissive`. **Keep this contract for any new emissive objects.**

### Material name tokens
- Three special materials so far (created by cloning `world_palette_material` via `bpy.data.materials.copy()` + rename):
  - `world_palette_glass_material` → cupola (runtime detects `*glass*` for transparency)
  - `world_palette_water_material` → river + tributary (runtime detects `*water*` for shader)
  - `world_palette_waterfall_material` → waterfall (runtime detects `*waterfall*` for stripe shader)
  - `world_palette_ocean_material` → ocean plane (runtime detects `*ocean*` for shader)
  - `world_palette_beam_material` → lighthouse beam (runtime detects `*beam*` for opacity)
- Phase 12 needs `*mountain*` token (likely `world_palette_mountain_material` clone with mountain texture as image input).

### Instancing pattern (Phase 11 onward)
- Multiple `bpy.data.objects.new(name, source_mesh)` share the SAME `bpy.data.meshes` datablock.
- The Phase 13 exporter detects shared mesh datablocks via `len(obj.data.users) > 1` and emits `InstancedMesh` per source.
- Foliage uses this for trees + ground cover; cluster boulders share the existing 5 boulder source meshes.

### Asset rule (CLAUDE.md rule 1)
- Phases 0–11 + 13 are procedural — no external assets.
- **Phase 12 requires 4 user-painted PNGs in `static/textures/mountains/`.** Script halts with clear error if any missing. Do NOT generate procedural placeholders without user buy-in.
- If a phase needs an asset that doesn't exist: STOP, ask, wait.

### Verification flow
1. Implementer subagent writes the script, stages it, reports DONE.
2. Controller gives the user:
   - The success print line they should see.
   - A `Numpad 7` / `Numpad 1` / Material Preview walkthrough.
   - 1-2 single-line Python Console smoke tests (multi-line for-loops break the Console without a blank line terminator).
   - A gate checklist (5-8 items).
3. User runs in Blender, replies with screenshots.
4. Controller interprets, dispatches fixes if needed, otherwise asks "Phase N approved?".
5. Only after explicit "approved" → commit.

### Common Blender quirks (already burned by these)
- `__file__` in Text Editor = `/Text`, not the disk path. Use the candidate-list `_script_dir()`.
- Multi-line `for` loops in Python Console need a blank line to terminate before a follow-up. Use list comprehensions or `def + call`.
- `_lib.py` reloading: when `_lib.py` is edited, Blender's cached `_lib` won't pick it up. User must `import importlib, _lib; importlib.reload(_lib)`.
- **Nested collection names**: `bpy.data.collections['trail/perimeter']` does NOT work — collections are stored by LEAF name only. Use `bpy.data.collections['perimeter']` etc. The `_lib.place_in("trail/perimeter", obj)` creates `trail` + `perimeter` collections; the leaf is what `bpy.data.collections[...]` finds. This burned Phase 10 and 11 verifications.
- macOS Blender has no System Console menu — `print()` output goes to Terminal (if Blender launched from Terminal) or to the **Info Editor**.
- `bpy_prop_collection` doesn't support `+` — can't concatenate two collection `.objects` lists. Use list comprehension.

## Build-pattern templates Phase 12-13 reuse

- `_script_dir()` — copy from any prior phase script.
- `_lib.clear_collection("foo")` — idempotent clear at start.
- `_lib.bm_add_cuboid/cylinder/finalize_to_object/paint_face/get_palette_material/replace_object/attach_palette_material`.
- `_lib.height_at(x, z)` — NOT used by Phase 12 (mountains are offshore visual planes) or Phase 13 (export).
- `bpy.ops.wm.save_as_mainfile(filepath=blend_path)` at end.
- Material clone pattern (for `*mountain*` token): `bpy.data.materials.remove(...)` → `bpy.data.materials.copy(source)` → rename → attach to target objects.
- Loading user PNGs (Phase 12 only): `bpy.data.images.load(filepath=abs_path, check_existing=True)` then attach as image texture node.

## User memories (auto-memory) that informed this build

Persistent across sessions, live at `~/.claude/projects/-Users-mahajankaran-Documents-Projects-karan-portfolio/memory/`:

- `feedback_no_claude_coauthor.md` — never add `Co-Authored-By: Claude` to commits.
- `feedback_no_coffee_jokes.md` — user doesn't drink coffee.
- `feedback_audio_pause_on_blur.md` — audio pauses on tab blur (not relevant to Blender build).
- `feedback_verify_layout_standing.md` — verification probes go in `.verify/scripts/` + `.verify/shots/<YYYY-MM-DD>/` (runtime verification only; Blender verifies in-viewport).
- `feedback_verify_synthetic_ticks.md` — synthetic-tick pattern for runtime verify (irrelevant for Blender).
- `project_v2_world_design_complete.md` — the world-design brainstorm settled 2026-05-26.

## Open caveats / parked items

- **Phase 12 PNGs** must exist before dispatching the implementer. User is painting them.
- **`world.blend1` file** is Blender's auto-backup. Gitignored. Don't commit.
- **`static/world/world.glb`** showed up untracked at some point during the build (probably an accidental export or test). NOT staged. Phase 13 will produce the canonical `world.glb`.
- **Concern A (Phase 2 fjord trench)** is intentionally kept — provides depth under the waterfall, hidden by the ocean plane at y=-1.5.
- **`inset_individual` is uniform** — bmesh limitation. Phase 3 hit this on the wayfinder; if any future phase needs asymmetric carved panels, plan loop cuts or accept uniform.
- The user is comfortable committing to `world-v2-blender-build` after approval, but **NOT pushing**. Push only after the user explicitly says so, probably after Phase 13 export.
- **Runtime systems** that already exist independently of Blender (don't duplicate in `.blend`): `StreetLights.js`, `Signs.js`, `Grass.js`, particle effects, water shaders, wind, day/night, etc. Blender authors geometry + refs; runtime attaches lights/shaders/animations.

## User's design feedback (Phase 11 informed this)

The user compared the world to Bruno Simon's portfolio. Key takeaways for any remaining phases / iterations:
- **Pines were originally cone-stacks → revamped to icosphere clumps** (matches birch quality). Don't regress to cone-stacks.
- **User likes color variety in foliage** — autumn warm-brown, deep-shade dark, meadow-green pine variants are desirable. Add more if asked.
- **Bench placement on slopes**: legs sink uphill / float downhill. The fix was to place benches on the perimeter-trail (approach) side of each waystone, not the view side. Same logic should apply to any future furniture on uneven terrain.
- **The Blender preview is not the final look**: runtime adds sky, fog, wind, water shader, fireflies, grass blades, streetlights, signs, day/night, particles. Don't over-engineer the .blend trying to match Bruno's preview brightness — Bruno's `.blend` has lights/HDRi/Eevee setup that ours doesn't.

## What to do first in the new session

1. Confirm branch state: `git branch --show-current` should print `world-v2-blender-build`. `git log --oneline -12` should show commits ending in `0f9d408` (Phase 11).
2. Check `static/textures/mountains/` for the 4 PNG files. If they exist → proceed with Phase 12 dispatch. If not → wait for user to confirm they're ready.
3. Read the plan's Phase 12 section: [plans/2026-05-26-v2-world-blender-build.md](../plans/2026-05-26-v2-world-blender-build.md) lines 560-594.
4. Dispatch the Phase 12 implementer using the section pattern (`tools/blender/scripts/phase-12-mountain-bands.py`).
5. Hand the verification walkthrough to the user. Wait for "approved". Commit (no Claude trailer).
6. Then Phase 13: export `world.glb` + assertions. After approval, the build is done.

---

## Resume prompt — paste into a fresh Claude Code session

```
Continue the v2 alpine-misty Blender world build. Full context is at
docs/superpowers/handoffs/2026-05-26-blender-build-resume.md.

Branch: world-v2-blender-build (already on it, do not switch).
Last commit: 0f9d408 (Phase 11 foliage + props).
Spec: docs/superpowers/specs/2026-05-26-world-design.md.
Plan: docs/superpowers/plans/2026-05-26-v2-world-blender-build.md.

We're picking up at Phase 12 — Mountain cardboard bands.

CRITICAL: Phase 12 is asset-gated. The user is painting 4 PNGs and dropping
them in static/textures/mountains/. Check that directory first:
  ls static/textures/mountains/

Expected files:
  mountain-front-ridge.png
  mountain-mid-peaks.png
  mountain-far-snow.png
  mountain-foothills-east.png

If all 4 exist → dispatch Phase 12 implementer (one fresh subagent).
If any are missing → ASK the user if their PNGs are ready before dispatching.
Per CLAUDE.md rule 1, do NOT generate procedural placeholder PNGs without
explicit user buy-in.

Workflow (locked, from the handoff doc):
- One fresh subagent per phase. Subagent writes the script, stages with
  `git add <specific paths>`, reports DONE. NEVER commits.
- I (the controller) translate the implementer report into a Blender
  viewport walkthrough for the user — how to run, what to verify, gate
  criteria, paste-into-console smoke tests.
- User runs in Blender, replies "Phase N approved" or flags fixes.
- Only after approval, I commit with a NO-TRAILER message (NEVER include
  Co-Authored-By: Claude — user memory feedback_no_claude_coauthor).

Read the handoff doc FIRST for full conventions:
- Z-up authoring, save_as_mainfile pattern
- Collider/ref naming, palette UV math, emissive suffix contract
- Material name tokens for shaders (*glass*, *water*, *waterfall*, *ocean*,
  *beam*, *mountain*)
- Instancing pattern via shared bpy.data.meshes datablocks
- Nested collection name access (use leaf names: `perimeter`, not
  `trail/perimeter`)
- Common Blender quirks list

After Phase 12 approval, Phase 13 is the final phase: export world.glb +
boot-time assertions. Then the runtime can start using the new .glb.
```
