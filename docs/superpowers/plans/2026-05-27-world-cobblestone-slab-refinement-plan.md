# Cobblestone slab refinement — implementation runbook

> **EXECUTION MODE:** Hybrid runbook, not agentic. The assistant runs terminal commands, performs `Edit`/`Read`/`Bash`/`git` operations from a terminal session, and curates verification. The **user (Karan)** runs anything inside Blender — either `Alt+P` in the GUI Text Editor, or (preferred, as in sub-project A) headless via `Blender --background ... --python ...` so console output streams to a terminal. Assistant never opens Blender, never runs phase-XX scripts, never invokes `bpy.ops.wm.save_as_mainfile()`.

> **No intermediate commits.** Spec + plan + edited script + regenerated GLB get bundled into ONE commit at Task 9 — and only after the user types `commit go`. If any task fails, run Task 10 (rollback) immediately and revisit the spec; do NOT layer fixes on top.

**Goal:** Shrink cobblestone slab coverage to the cardinal paths only (drop meadow + ridge from slab assignment) and double the path tile density (`SLAB_UV_SCALE 0.175 → 0.35`), leaving Bruno's color stops untouched. Result: warm olive meadow + cold grey ridge visible between dense cobblestone strips on the 4 cardinal paths.

**Architecture:** Edit two constants + one comment block in `tools/blender/scripts/phase-02-terrain.py`. Re-run phase-02 in Blender to rebuild `terrain_mesh` with new face→material-slot assignments and doubled slab UVs. Re-run phase-13 to refresh `static/world/world.glb`. Restore the .blend (phase-13 saves it as side effect, no intentional edits). Verify via phase-02's existing `slabs:N / palette:M` log line, `npx gltf-transform inspect` for GLB primitive-count check, and Material Preview viewport spot-check (reliable for structural changes per the verify-via-pixel-diff memory's "structural visible at a glance" carve-out).

**Tech Stack:** Python 3 (`_palette.py`, `_lib.py`, phase-02 import surface). Blender 4.2+ for phase-02 + phase-13 (bpy mesh/UV manipulation, gltf-2.0 export). `@gltf-transform/cli` 4.3.0 (already a devDep) for the GLB primitive face-count check.

**Spec:** [`docs/superpowers/specs/2026-05-27-world-cobblestone-slab-refinement-design.md`](../specs/2026-05-27-world-cobblestone-slab-refinement-design.md) (uncommitted; will be bundled at Task 9).
**Roadmap:** [`docs/superpowers/specs/2026-05-27-world-overhaul-roadmap.md`](../specs/2026-05-27-world-overhaul-roadmap.md). Depends on sub-project A (committed `96a82e4`).

---

## At-a-glance summary

| Task | What it does | Where to run | Roughly how long |
|---|---|---|---|
| 0 | Pre-flight: clean tree on the 3 artifacts + constants match expected + import sanity | Terminal (assistant) | 2 min |
| 1 | Capture baseline `slabs:N / palette:M` from the current GLB build | User runs phase-02 once (headless) | 30 sec |
| 2 | Edit `phase-02-terrain.py` — comment block + 2 constants | Assistant (Edit tool) | 1 min |
| 3 | Re-verify diff is exactly the expected lines | Terminal (assistant) | 30 sec |
| 4 | Re-run phase-02 inside Blender | User (Alt+P or headless) | 5-30 sec |
| 5 | Re-run phase-13 inside Blender | User (Alt+P or headless) | 5-15 sec |
| 6 | GLB primitive face-count check via `npx gltf-transform inspect` | Terminal (assistant) | 30 sec |
| 7 | Visual sanity in Material Preview viewport | User (Blender 3D viewport) | 1-3 min |
| 8 | Restore world.blend (phase-13 side-effect; no intentional edits) | Terminal (assistant) | 5 sec |
| 9 | If PASS: bundle commit spec + plan + phase-02 + world.glb after user `commit go` | Terminal (assistant) | 1 min |
| — | If FAIL at any point: rollback (see end of doc) | Terminal (assistant) | 30 sec |

Total: about 15 minutes if all goes well.

---

## Task 0 — Pre-flight checks

**Files inspected (read-only):**
- `tools/blender/scripts/phase-02-terrain.py` (lines 124-130 specifically)
- `tools/blender/scripts/_palette.py` (rock_mid + dirt_path keys must still exist)
- `static/world/world.glb` (must still contain world_slabs_material)

Before any edit, confirm five things hold.

- [ ] **Step 0.1 — Working tree state**

Run from the project root:

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git status --short
```

Expected: the three artifacts this plan will touch (`tools/blender/scripts/phase-02-terrain.py`, `static/world/world.glb`, `tools/blender/world.blend`) must NOT be listed as modified.

There WILL be unrelated entries shown (spec file from the brainstorm, the two new memory files, the modified `MEMORY.md` — all expected, all to be kept). If any of the three slab-target artifacts show as `M`, stop and either commit or stash them before continuing — otherwise Task 10 rollback won't be clean.

- [ ] **Step 0.2 — Constants match expected current state**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
sed -n '124,130p' tools/blender/scripts/phase-02-terrain.py
```

Expected output (byte-exact):

```python
# Slabs cobblestone overlay (Bruno's slabs.png from folio-2025). Walkable
# faces (dirt_path + meadow_grass + rock_mid) get material slot 1 using a
# world-XZ tiled UV; sand_gravel and deeper_water keep palette (slot 0).
# UV scale matches Bruno's slabTextureFrequency=0.175 → ~5.7m per 256px
# repeat → ~44cm per cobblestone tile.
SLAB_UV_SCALE = 0.175
SLAB_COLOR_KEYS = {"dirt_path", "meadow_grass", "rock_mid"}
```

If anything differs — different constant value, reordered keys, missing comment lines — **stop**. The script has drifted from spec assumptions; revisit the spec before proceeding.

- [ ] **Step 0.3 — `rock_mid` + `dirt_path` palette keys still exist**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts
python3 -c "import _palette; idx = _palette.PALETTE_CELL_INDEX; assert 'dirt_path' in idx and 'rock_mid' in idx, 'palette key missing'; print('dirt_path=%d rock_mid=%d' % (idx['dirt_path'], idx['rock_mid']))"
```

Expected output:

```
dirt_path=23 rock_mid=5
```

If `KeyError` or different indices, the palette has changed unexpectedly since sub-project A. Stop and reconcile.

- [ ] **Step 0.4 — Current GLB still embeds `world_slabs_material`**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
npx gltf-transform inspect static/world/world.glb 2>&1 | grep -E "world_slabs_material|world_palette_material" | head -5
```

Expected: two rows, one for `world_palette_material` (~158 instances), one for `world_slabs_material` (1 instance). The instance count is the count of mesh primitives referencing the material. Both materials must exist before we shrink the slab coverage — if `world_slabs_material` is missing, the .glb already drifted from the .blend in a way the spec did not predict.

- [ ] **Step 0.5 — Confirm absolute path to user's Blender binary**

```bash
ls /Applications/Blender.app/Contents/MacOS/Blender
```

Expected: file exists (the path the user used in sub-project A's headless phase-13 run). If it doesn't exist, ask the user where their Blender 4.2+ binary lives before Task 4. Headless mode is required for the cleanest phase-02 log capture in Task 4.

---

## Task 1 — Capture baseline `slabs:N / palette:M` (BEFORE the edit)

**Files inspected:** none modified. Read-only Blender invocation to capture the script's own log output.

This task exists so we have an objective number to compare against in Task 4. Without it, Task 4's count is unanchored.

- [ ] **Step 1.1 — User runs phase-02 in headless mode against current `world.blend`**

User runs in their terminal:

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background \
  /Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world.blend \
  --python /Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/phase-02-terrain.py 2>&1 | tee /tmp/phase-02-before.log
```

Expected console output includes a line like:

```
[blender-build][phase-02] terrain materials assigned — slabs:NNNN / palette:MMMM
```

The exact `NNNN` and `MMMM` are what we capture as baseline. From the picker logic (slabs = dirt_path + meadow_grass + rock_mid), expect `slabs` to be a large fraction of the ~36,864 terrain faces (perhaps 10,000-25,000), `palette` to be the rest. The exact numbers don't matter — what matters is that we record them.

- [ ] **Step 1.2 — User reports the captured log line**

User pastes the `slabs:NNNN / palette:MMMM` line into chat. Assistant records it in memory of the session as `BASELINE_SLABS` / `BASELINE_PALETTE`.

⚠️ **IMPORTANT — undo phase-02's side effect before continuing:** phase-02 also saves `world.blend` at the end (`bpy.ops.wm.save_mainfile`). After Step 1.2, run from terminal:

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git restore tools/blender/world.blend
```

This restores the .blend to HEAD so Task 4's run starts from the same baseline (avoids "did phase-02 already overwrite the geometry?" confusion).

- [ ] **Step 1.3 — Tree should be clean of the three target artifacts again**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git status --short tools/blender/world.blend tools/blender/scripts/phase-02-terrain.py static/world/world.glb
```

Expected: no output (all three files match HEAD). If `world.blend` is still listed as modified, re-run the `git restore` — Step 1.2 above is idempotent.

---

## Task 2 — Edit `phase-02-terrain.py`

**Files:**
- Modify: `tools/blender/scripts/phase-02-terrain.py` (lines 124-130 — comment block rewrite + two constant value changes)

Before applying, the assistant MUST show the user the exact proposed diff in chat. Apply only after presenting the diff.

- [ ] **Step 2.1 — Assistant presents the proposed diff in chat (do NOT Edit yet)**

Assistant prints to chat (no tool call):

```diff
 # Slabs cobblestone overlay (Bruno's slabs.png from folio-2025). Walkable
-# faces (dirt_path + meadow_grass + rock_mid) get material slot 1 using a
-# world-XZ tiled UV; sand_gravel and deeper_water keep palette (slot 0).
-# UV scale matches Bruno's slabTextureFrequency=0.175 → ~5.7m per 256px
-# repeat → ~44cm per cobblestone tile.
-SLAB_UV_SCALE = 0.175
-SLAB_COLOR_KEYS = {"dirt_path", "meadow_grass", "rock_mid"}
+# faces (only dirt_path — the 3m cardinal corridors at r<=20) get material
+# slot 1 using a world-XZ tiled UV; meadow_grass + rock_mid + sand_gravel
+# + deeper_water all keep palette (slot 0). Meadow + ridge stay exposed
+# in their warm-shifted palette colors (sub-project A).
+# UV scale doubled from Bruno's 0.175 to 0.35 so the narrower path strip
+# reads as ~6 stones across (~2.86m per 256px repeat → ~22cm per tile).
+SLAB_UV_SCALE = 0.35
+SLAB_COLOR_KEYS = {"dirt_path"}
```

- [ ] **Step 2.2 — Apply the edit via the `Edit` tool**

Assistant calls `Edit` with `replace_all=false` and the following old_string / new_string:

`old_string` (lines 124-130 verbatim):

```
# Slabs cobblestone overlay (Bruno's slabs.png from folio-2025). Walkable
# faces (dirt_path + meadow_grass + rock_mid) get material slot 1 using a
# world-XZ tiled UV; sand_gravel and deeper_water keep palette (slot 0).
# UV scale matches Bruno's slabTextureFrequency=0.175 → ~5.7m per 256px
# repeat → ~44cm per cobblestone tile.
SLAB_UV_SCALE = 0.175
SLAB_COLOR_KEYS = {"dirt_path", "meadow_grass", "rock_mid"}
```

`new_string`:

```
# Slabs cobblestone overlay (Bruno's slabs.png from folio-2025). Walkable
# faces (only dirt_path — the 3m cardinal corridors at r<=20) get material
# slot 1 using a world-XZ tiled UV; meadow_grass + rock_mid + sand_gravel
# + deeper_water all keep palette (slot 0). Meadow + ridge stay exposed
# in their warm-shifted palette colors (sub-project A).
# UV scale doubled from Bruno's 0.175 to 0.35 so the narrower path strip
# reads as ~6 stones across (~2.86m per 256px repeat → ~22cm per tile).
SLAB_UV_SCALE = 0.35
SLAB_COLOR_KEYS = {"dirt_path"}
```

Indentation: no leading whitespace on any of these lines (they're module-level definitions / comments). The `→` characters are the same Unicode arrows already present in the file — copy/paste rather than retype.

The `Edit` tool will fail if either `old_string` doesn't match byte-exact or already matches `new_string`. If it fails, re-read the file region with `Read tool offset=120, limit=15` and reconcile.

---

## Task 3 — Verify the diff matches the proposal

**Files inspected:** `tools/blender/scripts/phase-02-terrain.py`

- [ ] **Step 3.1 — `git diff` the file**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git diff tools/blender/scripts/phase-02-terrain.py
```

Expected: a diff matching Step 2.1's proposed diff byte-for-byte. Specifically:
- Two minus lines for the changed comment lines + UV scale constant + SLAB_COLOR_KEYS constant (7 minus lines total).
- Seven plus lines for the replacement (matching the new content shown above).
- No other lines changed elsewhere in the file.

If extra lines appear changed (e.g. trailing whitespace, a tab vs space), revert with `git restore tools/blender/scripts/phase-02-terrain.py` and re-apply Step 2.2 with corrected old_string.

---

## Task 4 — Re-run phase-02 in Blender (user)

**Files written:** `tools/blender/world.blend` (phase-02 saves the .blend as a side effect — handled in Task 8).

**How to run — preferred (headless, matches sub-project A workflow):**

User runs in a terminal:

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background \
  /Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world.blend \
  --python /Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/phase-02-terrain.py 2>&1 | tee /tmp/phase-02-after.log
```

**Alternative — GUI (Alt+P):** Open `world.blend` in Blender 4.2+, switch to Scripting workspace, open `phase-02-terrain.py` in the Text Editor, press `Alt+P`. Watch the System Console / launching-terminal stdout for the relevant log line.

- [ ] **Step 4.1 — Watch for assertions / errors**

phase-02 has a triangle-budget assertion at its end. Expected console lines:

```
[blender-build][phase-02] building 193x193 grid (37249 verts) ...
[blender-build][phase-02] paint pass: NN faces / NN palette
[blender-build][phase-02] terrain materials assigned — slabs:NNNN / palette:MMMM
[blender-build][phase-02] done
```

Runtime: 5-30 seconds depending on machine.

If you see an `AssertionError` or `KeyError`, stop and report — most likely a palette key reference no longer resolves (unlikely with our edit, but possible if Step 0.3 missed something). Do NOT try to patch around it — that's Task 10 rollback territory.

- [ ] **Step 4.2 — User reports the AFTER `slabs:N / palette:M` line**

User pastes the line into chat. Assistant records as `AFTER_SLABS` / `AFTER_PALETTE`.

**Expected direction:** `AFTER_SLABS` is much smaller than `BASELINE_SLABS` (rough order: 10× shrink — only dirt_path corridors remain). `AFTER_PALETTE` grows by exactly `(BASELINE_SLABS - AFTER_SLABS)` because the total face count is constant (`AFTER_SLABS + AFTER_PALETTE == BASELINE_SLABS + BASELINE_PALETTE`).

Assistant computes and reports the delta:

```
slabs:   BASELINE_SLABS   →   AFTER_SLABS   (delta: -X faces)
palette: BASELINE_PALETTE →   AFTER_PALETTE (delta: +X faces)
total:   should be unchanged
```

If total faces changed, geometry is being rebuilt differently — investigate before Task 5.

If `AFTER_SLABS` shrank by less than 5× (i.e., shrink ratio is small), something is wrong — likely the SLAB_COLOR_KEYS edit didn't take. Stop and inspect.

---

## Task 5 — Re-run phase-13 in Blender (user)

**Files written:**
- `static/world/world.glb` — refreshed export with new material slot assignments + new UV values
- `tools/blender/world.blend` — phase-13 also saves the .blend (per auto-memory `project-phase13-saves-blend`; handled in Task 8)

**How to run — preferred (headless):**

User runs in their terminal:

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background \
  /Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world.blend \
  --python /Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/phase-13-export-glb.py
```

**Alternative — GUI (Alt+P):** With `world.blend` already loaded from Task 4 (and unsaved scene state still in memory), open `phase-13-export-glb.py` in the Text Editor and press `Alt+P`.

- [ ] **Step 5.1 — Watch for assertion failures**

phase-13 runs assertions FIRST. Expected console lines:

```
[blender-build][phase-13] running assertions...
[blender-build][phase-13] assertions OK (153124 triangles, budget 180000)
[blender-build][phase-13] exporting -> /Users/mahajankaran/Documents/Projects/karan-portfolio/static/world/world.glb
... glTF 2.0 export INFO lines ...
[blender-build][phase-13] exported static/world/world.glb (~8000 KB)
[blender-build][phase-13] saved -> /Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world.blend
```

Runtime: 5-15 seconds.

If you see `ABORT - N assertion failure(s)` followed by a list, **stop**. Those failures are independent of our slab edit (they cover triangle budget, section ref positions, etc.) — they indicate the .blend has drifted in a way the sub-project doesn't account for. Roll back via Task 10.

- [ ] **Step 5.2 — Confirm `world.glb` was rewritten**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
ls -lh static/world/world.glb && git status --short static/world/world.glb
```

Expected: `M static/world/world.glb`, mtime within the last minute, file size near the previous ~7.8M-8.0M range. If the size jumps dramatically (e.g., +50%) something unexpected is being embedded — investigate before Task 6.

---

## Task 6 — GLB primitive face-count check

**Files inspected:** `static/world/world.glb` (read-only)

- [ ] **Step 6.1 — Inspect material primitive table**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
npx gltf-transform inspect static/world/world.glb 2>&1 | grep -E "world_palette_material|world_slabs_material"
```

Expected: same two rows as Step 0.4 — `world_palette_material` instance count and `world_slabs_material` instance count should match the pre-edit values (typically 158 + 1). The instance counts are the count of mesh primitives referencing each material; we did NOT add or remove primitives, only reshuffle which faces inside the terrain primitive use which material slot.

If either row is missing entirely (e.g., `world_slabs_material` gone), something dropped the material when only its face count changed — that's a regression and the verification fails.

- [ ] **Step 6.2 — Check terrain mesh primitive face counts shifted in expected direction**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
npx gltf-transform inspect static/world/world.glb 2>&1 | sed -n '/^│ # │ name.*mode.*meshPrimitives/,/^└/p' | grep -E "terrain_mesh|trimesh_terrain" | head -5
```

Expected: `terrain_mesh` row shows `meshPrimitives: 2` (one primitive per material slot — same as before edit). The vertex/indices counts on the row reflect the totals across both primitives (unchanged). Per-primitive face counts aren't displayed by `inspect` by default — the `slabs:N / palette:M` log from phase-02 (Task 4) is the load-bearing primary signal; this step is supplementary structural confirmation.

If `meshPrimitives: 1` (or some other count != 2), the material slot setup broke. Roll back.

---

## Task 7 — Visual sanity in Blender Material Preview (user)

**Files inspected (visually):** Blender's 3D viewport against `world.blend`'s in-memory scene state from Tasks 4 + 5.

⚠️ **Per auto-memory `feedback-palette-verify-via-pixel-diff`:** Material Preview is unreliable for subtle hue shifts but very reliable for STRUCTURAL changes like "this whole region switched materials." Sub-project C's changes are exactly the latter category — easy to confirm at a glance.

- [ ] **Step 7.1 — Open the .blend in Blender GUI if not already**

If user ran Task 4 + 5 headless, open `tools/blender/world.blend` in Blender 4.2+ GUI. Switch viewport to Material Preview shading (3rd sphere icon top-right of viewport).

If user ran Task 4 + 5 in the GUI, the scene is already loaded — just confirm Material Preview shading is on.

- [ ] **Step 7.2 — Frame the spawn area**

Press `Numpad .` (period) to "view all", then orbit (middle-mouse drag) until you see: walkable plateau at center, all four cardinal paths radiating N/S/E/W, NE ridge in the +X/+Y area, outer shore + ocean.

- [ ] **Step 7.3 — Confirm structural changes**

In order:

1. **Cardinal paths** — visibly dense cobblestone strips (warm cream + brown grout). Stones noticeably smaller / more numerous than before (UV scale doubled).
2. **Meadow plateau between paths** — uniform warm olive (`#a8b870` from sub-project A). No cobblestone pattern visible.
3. **NE ridge top** — cold grey-blue rock outcrop (`#5d6770`), visibly different from the warm meadow surrounding it.

- [ ] **Step 7.4 — Confirm "must not change" surfaces**

In the SAME viewport view:

1. **Outer ring (sand band)** — warm tan `#b09778` (sub-project A's sand_gravel). Unchanged from before C.
2. **Ocean surface** — cold blue. Unchanged.
3. **Mountain backdrop** — cold alpine. Unchanged.
4. **Props** (signs, lighthouse, observatory, hearth, etc.) — sit on terrain at the same heights. No floating or buried props.

If any "must not change" surface visibly shifted, the geometry/UVs got disturbed in a way the spec didn't predict. Roll back.

- [ ] **Step 7.5 — Decide PASS or FAIL**

PASS = both Step 7.3 (all three changed) AND Step 7.4 (all four unchanged). User reports `task 7 pass` in chat.

FAIL = anything else. User reports `task 7 fail: <which step, what looked wrong>`. Assistant proceeds to Task 10 (rollback) immediately, NOT to Task 8 / 9.

---

## Task 8 — Restore `world.blend` (phase-13/phase-02 side-effect cleanup)

**Files:** `tools/blender/world.blend`

Per auto-memory `project-phase13-saves-blend`, both phase-02 (Task 4) and phase-13 (Task 5) save `world.blend` at the end of their `main()` via `bpy.ops.wm.save_as_mainfile` / `bpy.ops.wm.save_mainfile`. The user made no intentional .blend edits, so we discard those saves before commit-prep.

- [ ] **Step 8.1 — Restore world.blend to HEAD**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git restore tools/blender/world.blend
```

Non-destructive — restores to HEAD. The actual scene rebuild from phase-02 + the GLB export from phase-13 happened in-memory and emitted `world.glb` — those outputs are preserved.

- [ ] **Step 8.2 — Confirm world.blend is clean**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git status --short tools/blender/world.blend
```

Expected: no output. If `M tools/blender/world.blend` still appears, re-run Step 8.1 — restore is idempotent.

---

## Task 9 — Bundled commit (only after user `commit go`)

**Files staged (the full bundle):**

- `docs/superpowers/specs/2026-05-27-world-cobblestone-slab-refinement-design.md`
- `docs/superpowers/plans/2026-05-27-world-cobblestone-slab-refinement-plan.md`
- `tools/blender/scripts/phase-02-terrain.py`
- `static/world/world.glb`

**Files NOT in this commit** (they were committed earlier OR are out of scope OR are local-only):
- The two memory files + `MEMORY.md` modification — these live under `~/.claude/projects/` (outside the repo).
- Anything under `.superpowers/brainstorm/` — this is gitignored once `.superpowers/` is added to `.gitignore` (offer this as a pre-commit cleanup step below).

- [ ] **Step 9.1 — Optional pre-commit: gitignore the brainstorm session**

If `.superpowers/` isn't already in `.gitignore`, add it now so the brainstorm mockup HTML doesn't sneak into a commit. Assistant runs:

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
grep -q "^\.superpowers/" .gitignore 2>/dev/null || printf '\n# brainstorm visual-companion sessions\n.superpowers/\n' >> .gitignore
git status --short .gitignore
```

If `.gitignore` shows as modified after this, include it in the Task 9 commit too (it's a one-line append, low risk, makes future commits cleaner).

- [ ] **Step 9.2 — Confirm exactly the right files are staged-to-stage**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git status --short
```

Expected output (order may vary, unrelated lines elsewhere may exist):

```
 M static/world/world.glb
 M tools/blender/scripts/phase-02-terrain.py
?? docs/superpowers/plans/2026-05-27-world-cobblestone-slab-refinement-plan.md
?? docs/superpowers/specs/2026-05-27-world-cobblestone-slab-refinement-design.md
```

(`.gitignore` may also appear if Step 9.1 modified it.)

⚠️ `tools/blender/world.blend` MUST NOT appear in this list. If it does, repeat Task 8 — phase-XX's side-effect save snuck through.

- [ ] **Step 9.3 — Show user the `git diff --stat` preview**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git diff --stat tools/blender/scripts/phase-02-terrain.py static/world/world.glb
wc -l docs/superpowers/specs/2026-05-27-world-cobblestone-slab-refinement-design.md \
      docs/superpowers/plans/2026-05-27-world-cobblestone-slab-refinement-plan.md
```

Expected:
- `phase-02-terrain.py`: 7 minus lines + 9 plus lines (the comment block expanded from 5 lines to 7 lines, plus the 2 constants).
- `world.glb`: a `Bin X -> Y bytes` line (sizes likely within ~5% of each other since geometry is unchanged, only material/UV indices reshuffled).
- Spec + plan: byte-counts roughly matching what's expected for their content.

Assistant presents this preview in chat and pauses for user confirmation.

- [ ] **Step 9.4 — Wait for user `commit go`**

Assistant does NOT proceed past this point without the user typing `commit go` (or equivalent explicit approval). If the user says `change X` or `wait` or asks a question, address it before re-presenting Step 9.3.

- [ ] **Step 9.5 — Stage and commit the bundle**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git add docs/superpowers/specs/2026-05-27-world-cobblestone-slab-refinement-design.md \
        docs/superpowers/plans/2026-05-27-world-cobblestone-slab-refinement-plan.md \
        tools/blender/scripts/phase-02-terrain.py \
        static/world/world.glb
# .gitignore only if Step 9.1 modified it:
git add .gitignore || true
git commit -m "$(cat <<'EOF'
slabs: confine cobblestone to cardinal paths, double tile density

Sub-project C of the world.blend overhaul roadmap. Two phase-02
constants change:

  SLAB_COLOR_KEYS  {dirt_path, meadow_grass, rock_mid} -> {dirt_path}
  SLAB_UV_SCALE    0.175 -> 0.35

Color stops untouched (Bruno's #a87762 / #ffcf8b).

Visual effect:
  - Cardinal paths: visibly dense cobblestone strips (~6 stones
    across each 3m path vs ~3 before).
  - Meadow plateau between paths: warm olive #a8b870 exposed
    (was hidden under uniform cobblestone).
  - NE ridge top: cold rock_mid grey #5d6770 exposed.
  - Sand band + ocean unchanged.

Pipeline:
  1. Edited phase-02-terrain.py (2 constants + 5-line comment
     rewrite).
  2. Re-ran phase-02 in Blender — face-to-material-slot reassignment
     + slabs UV layer doubled. Baseline slabs:N / palette:M log
     captured before and after the edit; ratio shrank ~10x as
     predicted.
  3. Re-ran phase-13 to refresh static/world/world.glb.
  4. Verified via gltf-transform inspect (both materials still
     present, same primitive count) + Material Preview structural
     spot-check (meadow, ridge, paths all read as expected).

The exposed meadow is intentionally transitional. Bruno-density
foliage carpet + ground bushes will fill it in a future sub-project
(see auto-memory project-world-vision-bruno-density).

Spec: docs/superpowers/specs/2026-05-27-world-cobblestone-slab-refinement-design.md
Plan: docs/superpowers/plans/2026-05-27-world-cobblestone-slab-refinement-plan.md
EOF
)"
```

No `Co-Authored-By: Claude` trailer per auto-memory `feedback-no-claude-coauthor`.

- [ ] **Step 9.6 — Confirm commit landed**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git log -1 --stat
```

Expected:
- 4 files in the stat (5 if `.gitignore` was added).
- `phase-02-terrain.py`: 16 lines changed (7 minus + 9 plus).
- `world.glb`: binary diff with similar before/after byte counts.
- Two new files for spec + plan (full byte counts).
- No `Co-Authored-By:` line in the commit body.

Do NOT `git push` in this plan. Pushing is a separate, explicit decision left to the user.

---

## Task 10 — Rollback (only if any task in 0-7 fails)

If any verification in Tasks 0-7 fails, revert all four target artifacts before re-investigating. Do NOT layer "fix" edits on top — that compounds the unknown state.

- [ ] **Step 10.1 — Discard all four artifacts**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git restore tools/blender/scripts/phase-02-terrain.py \
            static/world/world.glb \
            tools/blender/world.blend
# Spec + plan files are uncommitted — delete them OR keep for re-iteration:
rm -i docs/superpowers/specs/2026-05-27-world-cobblestone-slab-refinement-design.md \
      docs/superpowers/plans/2026-05-27-world-cobblestone-slab-refinement-plan.md
```

The `rm -i` interactive prompt lets the user decide whether to keep spec+plan for revision or scrap them entirely. If user wants to keep them for revision, answer `n` (no) at the prompt — the files stay in the working tree until the next commit attempt.

- [ ] **Step 10.2 — Re-open `world.blend` in Blender (discard in-memory state)**

In Blender: File → Revert (or close + reopen). Discards any in-memory material assignment / UV state that might still hold the edited values.

- [ ] **Step 10.3 — Confirm rollback is clean**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git status --short tools/blender/scripts/phase-02-terrain.py \
                   static/world/world.glb \
                   tools/blender/world.blend
```

Expected: no output. If any of the three artifacts still show `M`, re-run Step 10.1 — restore is idempotent.

- [ ] **Step 10.4 — Report back what failed**

Hand back to assistant with:
- Which task in 0-7 failed (e.g., 0.4, 4.2, 7.3).
- What specifically went wrong (assertion error, unexpected face count, visual surprise).
- Whether you suspect a misread of the picker logic, a stale .blend, an unexpected upstream change, or a constant value typo.

Assistant will revise the spec (and possibly the plan) before re-running. Do NOT re-attempt the same edit from Task 2 without first reconciling the spec — that's what caused the loop in sub-project A's Task 3 phase-01 spot-check issue.

---

## Self-review (assistant-side, post-write)

**1. Spec coverage:**

| Spec section | Plan coverage |
|---|---|
| Goal — paths only + denser tiling, no color change | Task 2 (edit), Task 7 (visual verify) |
| Decision summary — Q1=B / Q2=A / Q3=B | Task 2's exact constant values + comment text |
| Non-goals — no color stops change, no refactor, no slabs.png change | Task 2 only touches SLAB_UV_SCALE + SLAB_COLOR_KEYS + comment block — no other diffs allowed |
| Architecture / data flow — phase-02 → terrain rebuild → phase-13 → GLB refresh | Tasks 4 + 5 |
| Files touched — exactly one source edit + one regenerated binary | Task 3 verifies, Task 9 stages |
| Behavioral effects — meadow exposed, ridge grey, paths denser | Task 7's checklist |
| Verification — phase-02 log diff, gltf-transform, Material Preview | Tasks 4.2 + 6.1 + 7.3 |
| Rollback | Task 10 |
| Future work deferred — Bruno-density items | Commit message body acknowledges; not in scope |

**2. Placeholder scan:** No "TBD" / "TODO" / "implement later" / "add appropriate" patterns in the plan body. References to memory files use the `auto-memory <name>` notation (memories live outside the repo).

**3. Type consistency:** `SLAB_UV_SCALE`, `SLAB_COLOR_KEYS`, `world_palette_material`, `world_slabs_material`, `dirt_path`, `meadow_grass`, `rock_mid`, `sand_gravel`, `deeper_water` — all spelled identically across spec, plan, and source. The hex values `#a8b870`, `#85715a`, `#b09778`, `#5d6770`, `#ffcf8b`, `#a87762` are byte-exact across documents. Cell indices `dirt_path=23`, `rock_mid=5` match `_palette.py` and the sub-project A verification.

---

## Execution handoff

This plan is a **hybrid runbook**, not an agentic-execution plan. Sub-skills like `superpowers:subagent-driven-development` / `superpowers:executing-plans` don't apply — they assume the agent can run every step, but Tasks 1, 4, 5, 7 require the user inside Blender (or driving Blender from their terminal).

The assistant + user proceed through Tasks 0 → 10 collaboratively. At each user-action task (1, 4, 5, 7), the assistant pauses; at each assistant-action task (0, 2, 3, 6, 8, 9, 10), the assistant runs the tool calls and pauses for user confirmation before advancing.

The plan is now ready for execution. Reply `plan approved, start execution` to begin Task 0.
