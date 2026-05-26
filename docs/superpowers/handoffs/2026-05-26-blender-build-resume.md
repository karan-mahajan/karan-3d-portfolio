# Blender world-build — resume handoff

> **For a fresh Claude Code session.** Paste the prompt at the very bottom into a new session to continue from Phase 4 onward.

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

`git log --oneline world-v2-blender-build` to confirm.

## Phases remaining (each = one fresh subagent dispatch)

4. Projects workshop pavilion (E, +70m)
5. Skills observatory tower (S, -70m)
6. Experience cairn trail (N, +70m, rises +12m via NE ridge)
7. Contact cliff beacon (W, -70m, on the cliff edge)
8. Lighthouse + islet (offshore NW, world pos (-130, +35))
9. River + tributary + waterfall + bridges + ocean plane
10. Hiking trail (perimeter loop + 3 viewpoint detours)
11. Foliage (~130 trees + ~150 ground cover + 5 hero pines)
12. Mountain cardboard bands (4 quads — NEEDS user-painted PNGs)
13. Export `world.glb` + assertions

Phase 4–7 share a "section pattern" — fixes in Phase 4 should propagate to 5/6/7 via the dispatch prompt template.

## Locked conventions — DO NOT relitigate

These were settled during the live build. Re-explaining them costs the user time.

### Branch + commit policy
- All Phase work goes to `world-v2-blender-build`. NEVER directly to `main`. NEVER pushed without user OK.
- **NEVER commit without explicit user approval.** Subagents stage with `git add <specific paths>`; the human-running-Claude does the commit only after the user replies "Phase N approved".
- **NEVER use `Co-Authored-By: Claude` trailer** in commit messages. The user's memory `feedback_no_claude_coauthor` is explicit. The commit message body is fine, no trailer.
- Stage with explicit paths (e.g. `git add tools/blender/scripts/phase-NN.py tools/blender/world.blend`). NEVER `git add -A` — risks pulling in `world1.blend` accidents (see below).

### Coordinate system
- **Blender Z-up authoring.** Runtime is Three.js Y-up; Phase 13 exporter handles the swap.
- Mapping: Blender X = runtime X (east-west); Blender Y = runtime Z (north-south, +Y north); Blender Z = runtime Y (height).
- Helper `_lib.height_at(x, z)` takes runtime coords and returns runtime Y. Pass results directly to Blender's location as `(x, z, height)`.
- `_lib.ref_empty(name, location=(x, height, z), radius=...)` accepts runtime order — internally it places at Blender `(x, z, height)`. Confirm by reading `phase-02-terrain.py:_place_terrain_refs()`.

### Save pattern
- Every phase script ends with `bpy.ops.wm.save_as_mainfile(filepath=<absolute world.blend path>)`. NOT `save_mainfile()` — that saves to whatever's currently open, which silently misses if the user accidentally did Save As.
- Pattern: `blend_path = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "world.blend"))`.
- Phase 2's failure mode (Save As to `world1.blend`) was traced and fixed; do not regress.

### Script structure
- Each phase = one script `tools/blender/scripts/phase-NN-name.py`, idempotent (clears its own collection at start), self-contained, runs inside Blender 4.2+.
- All scripts share `_lib.py` + `_palette.py`. New helpers can be added to `_lib.py` if multiple phases need them (Phase 2 added `height_at()` this way). Don't fork helpers between phases.
- `_script_dir()` pattern from `phase-00-setup.py` handles Blender's bogus `__file__` (sets it to `/Text` when run from Text Editor). Copy that block verbatim.
- Comments only explain non-obvious WHY. No comments that restate the code. No emojis.
- bmesh for geometry construction, NOT `bpy.ops.mesh.primitive_*` (the latter is 10–100× slower and leaves modal state).

### Palette colors
- 25 locked colors in `_palette.PALETTE_COLORS`. Every face's UV must snap to one of these cells. No new colors without re-baking palette.png and updating the spec.
- Use `_palette.PALETTE_CELL_INDEX[color_key]` + `_palette.cell_uv(index)` for UV math.
- `_lib.palette_uv("rock_mid")` is the convenience wrapper.

### Collider naming (spec §11.2)
- `cuboid_*`, `tube_*`, `trimesh_*` prefixes. Phase 13 exporter parses by name.
- Colliders live in the same collection as their visible mesh, hidden via `obj.hide_viewport = True` + `obj.hide_render = True`.
- Bruno's `tube_*` convention: when sized via bbox, runtime treats Y as height first, X/Z as radius. For Blender authoring just create the cylinder mesh with correct visual dimensions; the importer parses bbox.

### Ref empties (spec §11.3)
- `refZoneBounding_<section>` (~12-14m radius), `refZoneFrustum_<section>` (~9-11m), `refInteractivePoint_<section>`, `refRespawn_<section>`, plus section-specific anchors like `refForge`, `refBrazier`, `refCairnLantern_<n>`, `refHeroTree_<n>`.
- Set radius via `_lib.ref_empty(... radius=N)` — that maps to Blender's uniform scale (the runtime parses scale-as-radius per Bruno's convention).
- Custom properties (userData) via the `userdata` arg.

### Asset rule (CLAUDE.md rule 1)
- Phases 0–11 + 13 are procedural — no external assets needed.
- Phase 12 (mountains) requires 4 user-painted PNGs in `static/textures/mountains/`. If they don't exist when Phase 12 runs, the script halts with a clear error. Do NOT generate procedural placeholders.
- If a phase needs an asset that doesn't exist, STOP, ask, wait.

### Verification flow
1. Implementer subagent writes the script, stages it, reports DONE.
2. Main session (the one driving the build) gives the user:
   - The success print line they should see.
   - A `Numpad 7` / `Numpad 1` / Material Preview walkthrough.
   - 1–2 Python console one-liners for mechanical checks (collection contents, ref positions, etc.).
   - A gate checklist (5–8 items).
3. User runs in Blender, reports back with screenshot.
4. Main session interprets, asks for fixes if needed, otherwise asks "Phase N approved?".
5. Only after explicit "approved" → commit.

### Common Blender quirks (already burned by these)
- `__file__` in Text Editor = `/Text`, not the disk path. Use the candidate-list `_script_dir()` from `phase-00-setup.py`.
- Multi-line `for` loops in the Python Console need a blank line to terminate before a follow-up statement. Use single-line list comprehensions or a `def + call` block for console verification.
- `_lib.py` reloading: when `_lib.py` is edited (e.g. Phase 2 added `height_at`), Blender's cached `_lib` module won't pick it up automatically. User must `importlib.reload(_lib)`. Mention this in verification walkthroughs.
- macOS Blender doesn't have System Console menu — `print()` output goes to Terminal (if Blender was launched from Terminal) or to the **Info Editor** (Window → toggle area type to Info).
- Default Collection: Phase 0 explicitly removes it via `bpy.data.collections.remove(...)`. Don't accumulate it on re-runs.

## Build-pattern templates Phase 4-7 will reuse

`phase-03-spawn.py` has helper functions that should be reused as-is (or lifted into `_lib.py`) for Phases 4-7:

- `_bm_add_cuboid(bm, uv_layer, center, half_extents, color_key)` → returns the 6 faces in order [bottom, top, -Y, +Y, -X, +X]. Bruno-style face ordering.
- `_bm_add_cylinder(bm, uv_layer, center, radius, height, color_key, segments=24)` → for tubes, columns, dome bases.
- `_bm_finalize_to_object(bm, mesh_name, obj_name, location, collection_name, material)` → final bmesh → mesh datablock → object → linked → material assigned.
- `_paint_face(face, uv_layer, color_key)` → set all 4 loop UVs of a face to a palette cell center.
- `_get_palette_material()` → reuse the `world_palette_material` from Phase 2 (or create stub if Phase 2 didn't run).

Phase 4's implementer prompt should reference these by name so they get reused, not reinvented.

## User memories (auto-memory) that informed this build

These are persistent across sessions. New session WILL load them automatically since they live at `~/.claude/projects/-Users-mahajankaran-Documents-Projects-karan-portfolio/memory/`:

- `feedback_no_claude_coauthor.md` — never add `Co-Authored-By: Claude` to commits.
- `feedback_no_coffee_jokes.md` — user doesn't drink coffee; avoid caffeine/coffee references.
- `feedback_audio_pause_on_blur.md` — audio pauses on tab blur (not relevant to Blender build, but persistent).
- `feedback_verify_layout_standing.md` — verification probes go in `.verify/scripts/` + `.verify/shots/<YYYY-MM-DD>/` (runtime verification only; Blender build verifies in-viewport).
- `feedback_verify_synthetic_ticks.md` — synthetic-tick pattern for runtime verify (irrelevant for Blender).
- `project_v2_world_design_complete.md` — the world-design brainstorm settled 2026-05-26; spec is at the path above.

## Open caveats / parked items

- **Phase 12 mountains** need user-painted PNGs before the script runs. Surface this at Phase 12 dispatch.
- **`world.blend1` file** is Blender's auto-backup. Gitignored. Don't commit.
- **Concern A (Phase 2 fjord trench)** is intentionally kept — provides depth under the waterfall, hidden by the ocean surface plane that Phase 9 will add at y≈0.
- **Inset_individual is uniform** — bmesh limitation. Phase 3 hit this on the wayfinder; if Phase 4–7 need asymmetric carved panels, plan loop cuts or accept uniform.
- The user is comfortable committing to `world-v2-blender-build` after approval, but **NOT pushing**. Push only after the user explicitly says so, probably after Phase 13 export.

## What to do first in the new session

1. Confirm branch state: `git branch --show-current` should print `world-v2-blender-build`. `git log --oneline -4` should show commits `3503d43`, `0fdbf9b`, `df27cb2`, `f7aee10`.
2. Read the plan's Phase 4 section: [`docs/superpowers/plans/2026-05-26-v2-world-blender-build.md`](../plans/2026-05-26-v2-world-blender-build.md).
3. Read `phase-03-spawn.py` to understand the section-build pattern (helpers, ref placement, collider naming).
4. Dispatch the Phase 4 implementer using the template in the next section.
5. Hand the verification walkthrough to the user. Wait for "approved". Commit.

---

## Resume prompt — paste into a fresh Claude Code session

```
Continue the v2 alpine-misty Blender world build. Full context is at
docs/superpowers/handoffs/2026-05-26-blender-build-resume.md.

Branch: world-v2-blender-build (already on it, do not switch).
Last commit: 3503d43 (Phase 3 spawn cluster).
Spec: docs/superpowers/specs/2026-05-26-world-design.md.
Plan: docs/superpowers/plans/2026-05-26-v2-world-blender-build.md.

We're picking up at Phase 4 — Projects workshop pavilion (E, +70m).
Workflow (locked):
- One fresh subagent per phase. Subagent writes the script, stages with
  `git add <specific paths>`, reports DONE. NEVER commits.
- I (the controller) translate the implementer report into a Blender
  viewport walkthrough for the user — how to run, what to verify, gate
  criteria, paste-into-console smoke tests.
- User runs in Blender, replies "Phase N approved" or flags fixes.
- Only after approval, I commit with a NO-TRAILER message (NEVER include
  Co-Authored-By: Claude — user memory feedback_no_claude_coauthor).

Read the handoff doc first for full conventions (Z-up authoring,
save_as_mainfile pattern, collider/ref naming, palette UV math, the
common Blender quirks list). Then dispatch the Phase 4 implementer.
```
