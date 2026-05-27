# Palette Controlled-Warmth Shift — Implementation Runbook

> **EXECUTION MODE:** **User runbook**, not agentic. The user (Karan) follows this plan top-to-bottom in one sitting — editing `_palette.py` in any text editor, running one Python script in a terminal, running one phase script inside Blender, and visually verifying in Blender's Material Preview viewport. The assistant never opens Blender, never runs phase scripts, never executes any task below. Report back when verification passes (or fails); we'll commit + move to sub-project B together.

**Goal:** Warm-shift three palette cells (`meadow_grass`, `dirt_path`, `sand_gravel`) without changing cell indices, re-bake `static/textures/palette.png`, re-export `static/world/world.glb` (palette is embedded inside GLB), and verify visually in Blender.

**Architecture:** Edit `_palette.py` (the 25-color source of truth) → `phase-01-palette-texture.py` re-bakes the PNG → `phase-13-export-glb.py` re-exports the GLB with refreshed embedded palette → Material Preview viewport inspection confirms only the three target surfaces shifted.

**Tech Stack:** Python 3 (no Blender for phase-01), Blender 4.2+ (for phase-13 + visual verify), `@gltf-transform/cli` 4.3.0 (already a devDep) for the pre-flight GLB inspection.

**Spec:** [docs/superpowers/specs/2026-05-27-world-palette-warm-shift-design.md](../specs/2026-05-27-world-palette-warm-shift-design.md) (commit `0d337af`).
**Roadmap:** [docs/superpowers/specs/2026-05-27-world-overhaul-roadmap.md](../specs/2026-05-27-world-overhaul-roadmap.md).

---

## At-a-glance summary

| Task | What it does | Where to run | Roughly how long |
|---|---|---|---|
| 0 | Pre-flight: clean tree + GLB embeds palette + cell indices = 16/23/24 | Terminal | 2 min |
| 1 | Edit `_palette.py` — three hex changes | Any editor | 1 min |
| 2 | Re-verify cell indices unchanged | Terminal | 30 sec |
| 3 | Run `phase-01-palette-texture.py` | Terminal | < 1 sec |
| 4 | Run `phase-13-export-glb.py` inside Blender | Blender Text Editor → Alt+P | 5-15 sec |
| 5 | Visual verify in Material Preview viewport | Blender 3D viewport | 3-5 min |
| 6 | If pass: stage + commit three artifacts | Terminal | 1 min |
| — | If fail at any point: rollback (see end of doc) | Terminal | 30 sec |

Total: about 15 minutes if all goes well.

---

## Task 0 — Pre-flight checks

**Files inspected (read-only):**
- `tools/blender/scripts/_palette.py`
- `static/world/world.glb`

Before touching anything, confirm three things hold.

- [ ] **Step 0.1 — Working tree is in a known-clean state**

Run from the project root:

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git status --short
```

Expected output: no modified files for the three artifacts this plan will touch (`tools/blender/scripts/_palette.py`, `static/textures/palette.png`, `static/world/world.glb`). Other unrelated modifications are fine — leave them alone.

If any of those three are listed as modified (`M `), stop. Either commit or stash them first so rollback at the end of this plan is a clean revert.

- [ ] **Step 0.2 — Confirm GLB embeds the palette PNG**

Run from the project root:

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
npx gltf-transform inspect static/world/world.glb 2>&1 | grep -A 1 "Textures\|palette\|name" | head -40
```

Expected: an entry referencing the palette texture inside the GLB's texture table. The fact that it appears in `inspect`'s output (without an external file path) is the proof that `phase-13` baked it INTO the binary buffer. This is the load-bearing assumption that requires us to re-run phase-13 after phase-01.

If you see NO palette-named texture in the output, stop and report — the embedding assumption is wrong and the plan needs revision.

- [ ] **Step 0.3 — Confirm cell indices are 16 / 23 / 24**

Run from the project root:

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts
python3 -c "import _palette; idx = _palette.PALETTE_CELL_INDEX; print('meadow_grass=%d  dirt_path=%d  sand_gravel=%d' % (idx['meadow_grass'], idx['dirt_path'], idx['sand_gravel'])); assert idx['meadow_grass'] == 16 and idx['dirt_path'] == 23 and idx['sand_gravel'] == 24, 'CELL INDEX INVARIANT BROKEN'"
```

Expected output:

```
meadow_grass=16  dirt_path=23  sand_gravel=24
```

If you get `CELL INDEX INVARIANT BROKEN` or different numbers, **stop**. Someone re-ordered `PALETTE_COLORS` without updating the world bake. Fix the ordering BEFORE editing palette hexes — otherwise every downstream UV unwrap silently shifts to the wrong color cell.

- [ ] **Step 0.4 — Confirm the world.blend you'll open matches the GLB on disk**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
ls -lh tools/blender/world.blend static/world/world.glb
```

Both files should exist. The .blend timestamp should be at-or-before the .glb timestamp — meaning the GLB was exported from the current .blend state. If the .blend is *newer* than the .glb, the .blend has un-exported edits in it that phase-13 will re-export. That's not catastrophic, but call it out in the commit message so the diff is understood.

---

## Task 1 — Edit `_palette.py`

**Files:**
- Modify: `tools/blender/scripts/_palette.py` (lines 34, 43, 44 — three hex value changes)

Three changes. Open the file in any editor.

- [ ] **Step 1.1 — Change `meadow_grass`**

In `tools/blender/scripts/_palette.py`, find this line (currently line 34):

```python
    "meadow_grass":        "#94a978",
```

Replace with:

```python
    "meadow_grass":        "#a8b870",
```

Whitespace must stay identical (4-space indent, 8 spaces between the colon and the value) — `phase-01` doesn't care about alignment, but the file's column-aligned style does.

- [ ] **Step 1.2 — Change `dirt_path`**

Find this line (currently line 43):

```python
    "dirt_path":           "#6e6256",
```

Replace with:

```python
    "dirt_path":           "#85715a",
```

(11 spaces between the colon and the value — preserve.)

- [ ] **Step 1.3 — Change `sand_gravel`**

Find this line (currently line 44):

```python
    "sand_gravel":         "#9a8a72",
```

Replace with:

```python
    "sand_gravel":         "#b09778",
```

(9 spaces between the colon and the value — preserve.)

- [ ] **Step 1.4 — Save the file. Do NOT commit yet.**

The plan ties the three artifacts (`_palette.py`, `palette.png`, `world.glb`) into a single commit at Task 6. Don't stage anything until Task 5 verification passes.

- [ ] **Step 1.5 — Confirm the diff is exactly three lines**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git diff tools/blender/scripts/_palette.py
```

Expected: exactly three `-`/`+` line pairs. The minus lines show `#94a978` / `#6e6256` / `#9a8a72`; the plus lines show `#a8b870` / `#85715a` / `#b09778`. No other changes.

If you see other lines changed, undo and re-edit precisely — anything else changed risks breaking the cell-index invariant or unrelated palette cells.

---

## Task 2 — Re-verify cell indices unchanged

**Files inspected:** `tools/blender/scripts/_palette.py`

- [ ] **Step 2.1 — Re-run the cell-index assertion**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts
python3 -c "import _palette; idx = _palette.PALETTE_CELL_INDEX; print('meadow_grass=%d  dirt_path=%d  sand_gravel=%d' % (idx['meadow_grass'], idx['dirt_path'], idx['sand_gravel'])); assert idx['meadow_grass'] == 16 and idx['dirt_path'] == 23 and idx['sand_gravel'] == 24, 'CELL INDEX INVARIANT BROKEN'"
```

Expected output (unchanged from Step 0.3):

```
meadow_grass=16  dirt_path=23  sand_gravel=24
```

If `CELL INDEX INVARIANT BROKEN` appears now but didn't in Step 0.3, the edit accidentally re-ordered keys. Re-open the file and confirm only hex strings changed — not the dict's insertion order. Re-run Step 1.5 (`git diff`) to spot the structural mistake.

---

## Task 3 — Re-bake the palette PNG (phase-01, terminal)

**File path:** `tools/blender/scripts/phase-01-palette-texture.py`
**How to open:** the script is plain Python — no Blender needed for this step.
**How to run:** Python 3 on the command line. Phase-01 is intentionally stdlib-only so it works outside Blender.

**Files written:**
- `static/textures/palette.png` — 128×4 sRGB RGBA PNG

- [ ] **Step 3.1 — Run phase-01 from the project root**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
python3 tools/blender/scripts/phase-01-palette-texture.py
```

Expected output: a log line confirming the palette PNG was written, with the 25-color count verified. Something like:

```
[blender-build][phase-01] wrote static/textures/palette.png (25 cells)
```

Runtime: well under 1 second.

If the script errors with a 25-color-count mismatch, the dict was edited beyond the three lines this plan touches. Revert via `git restore tools/blender/scripts/_palette.py` and start over from Task 1.

- [ ] **Step 3.2 — Inspect the diff of the generated PNG (sanity)**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git status --short static/textures/palette.png
```

Expected: ` M static/textures/palette.png` (modified). If it's listed as untracked or absent, the script didn't write where you expected — verify the script's `_output_path()` logic resolved to the right place.

Optional: open `static/textures/palette.png` in any image viewer (it's tiny — 128×4). You should see three 5px-wide vertical bands warmer than the previous PNG. Looking at the PNG side-by-side with HEAD's version:

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git show HEAD:static/textures/palette.png > /tmp/palette-before.png
open /tmp/palette-before.png static/textures/palette.png
```

(Mac `open` will launch both side-by-side in Preview's "Multiple Documents" mode by default. Eyeball cells 16, 23, 24 — they should be visibly warmer in the new file.)

---

## Task 4 — Re-export the world GLB (phase-13, in Blender)

**File path:** `tools/blender/scripts/phase-13-export-glb.py`
**How to open:**
1. Launch Blender 4.2 or newer.
2. File → Open → navigate to `/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world.blend`.
3. After it loads, switch to the **Scripting** workspace (workspace tabs across the top — Layout / Modeling / Sculpting / … / **Scripting**).
4. In the Scripting workspace's Text Editor panel: **Open** (folder icon, or `Text → Open`) → navigate to `tools/blender/scripts/phase-13-export-glb.py` → select and load.

**How to run:** with the script loaded, with the Text Editor panel focused, press **`Alt+P`** (or use the **Run Script** button in the Text Editor header).

**Files written:**
- `static/world/world.glb` — produced by `bpy.ops.export_scene.gltf(...)` with `export_format="GLB"` (embeds the now-refreshed palette PNG inside the binary buffer)

- [ ] **Step 4.1 — Watch the System Console (or Blender's stdout)**

Phase-13 runs pre-flight assertions FIRST. The console emits progress prints like:

```
[blender-build][phase-13] running assertions...
[blender-build][phase-13] OK - 0 assertion failure(s)
[blender-build][phase-13] exporting GLB to .../static/world/world.glb
[blender-build][phase-13] done
```

Runtime: 5-15 seconds depending on machine.

If the assertions phase prints an `ABORT` line + a list of assertion failures (triangle budget, section positions, etc.) — **stop here, do not bypass.** Those failures predate our palette edit and indicate the .blend has drifted from what phase-13 expects. Roll back the palette change (`git restore tools/blender/scripts/_palette.py static/textures/palette.png`) and report. Do NOT edit the assertion code to "make it pass."

- [ ] **Step 4.2 — Confirm the GLB on disk was rewritten**

In a second terminal:

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git status --short static/world/world.glb
```

Expected: ` M static/world/world.glb`. The mtime should be very recent (within the last minute).

- [ ] **Step 4.3 — Confirm the embedded palette refreshed**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
npx gltf-transform inspect static/world/world.glb 2>&1 | grep -A 1 "Textures\|palette" | head -20
```

Expected: same palette texture row as in Step 0.2, but the byte size or hash may differ slightly because the underlying PNG changed. The important thing: the texture is still listed as embedded (no external URI path), confirming the new PNG bytes went into the binary buffer.

---

## Task 5 — Visual verify in Blender's Material Preview viewport

**Files inspected (visually):**
- The 3D viewport in Blender, showing `world.blend`'s scene.
- Optionally: `static/textures/palette.png` opened in any image viewer.

This is the **only** check that confirms the warm-shift looks right. The script-side checks above only confirm that artifacts updated; they don't confirm the colors LOOK correct on the actual terrain.

- [ ] **Step 5.1 — Switch viewport shading to Material Preview**

In Blender's 3D viewport, find the four shading-mode icons in the top-right of the viewport (wireframe / solid / **material preview** / rendered). Click the **third** one (Material Preview).

If the viewport goes completely dark, the .blend's Material Preview HDRI might be set to the studio default but with brightness 0. Find a Material Preview icon in the same row → World tab → ensure HDRI brightness > 0.

- [ ] **Step 5.2 — Frame the spawn area**

Press `Numpad .` (period) with no object selected to "view all". Then orbit (middle-mouse-button drag) until you can see:
- The walkable plateau at the world center (where the player spawns)
- All four cardinal paths radiating from spawn (refPath_N / refPath_E / refPath_S / refPath_W)
- The shore band at the outer rim
- The mountain backdrop on the horizon

Optionally save the current view as a numpad camera shortcut for repeat-checks.

- [ ] **Step 5.3 — Confirm three positive surface changes**

Eyeball, in this order:

1. **Walkable grass band** — the broad area of the plateau between paths. Should read visibly warmer / more olive than it did before the edit. Not "yellow" (that would be over-warm); a warm meadow olive.
2. **Cardinal paths** — the lighter strips running outward from spawn to each cardinal section. Should read as warm sun-baked dirt, not the cold grey-brown they were before.
3. **Shore / beach band** — the outer ring just before the ocean. Should read as warm sand.

If any of these three did NOT change, the edit didn't take effect in this .blend. Re-load the .blend (File → Revert) and re-run phase-13. The GLB-on-disk has the new palette, but the Blender material in-memory may have cached the old image.

- [ ] **Step 5.4 — Confirm three "must not change" surfaces**

In the SAME viewport view, check that these surfaces look **identical** to how they did before:

1. **Mountain bands** — distant ridges should still read as cold blue-grey alpine.
2. **Snow caps** — bright white-with-a-blue-cast highlights on mountains.
3. **Water surface** — glacial river / pond / ocean should still read as cold blue.

If any of those three shifted in tone, the cell-index invariant broke and the wrong cells were re-colored. Roll back immediately (see Task 7 "Rollback") and re-investigate before continuing.

- [ ] **Step 5.5 — Inspect the palette PNG itself (optional but quick)**

Open `static/textures/palette.png` (and optionally `git show HEAD:static/textures/palette.png > /tmp/palette-before.png` side-by-side as in Step 3.2). The PNG is 128×4 — viewed at native size it looks like a horizontal strip of 25 colored cells.

Cells 16 (`meadow_grass`), 23 (`dirt_path`), 24 (`sand_gravel`) should be visibly warmer. Cells 0-15, 17-22 should be byte-identical to the previous PNG.

If any cell outside {16, 23, 24} appears different, stop and re-investigate.

- [ ] **Step 5.6 — Decide: PASS or FAIL**

PASS = both 5.3 (all three changed) AND 5.4 (all three unchanged) AND 5.5 (only three cells shifted). Proceed to Task 6.

FAIL = anything else. Proceed to Task 7 (Rollback).

---

## Task 6 — Commit (only if Task 5 passed)

**Files staged:**
- `tools/blender/scripts/_palette.py`
- `static/textures/palette.png`
- `static/world/world.glb`

- [ ] **Step 6.1 — Confirm exactly those three files are modified, nothing else**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git status --short
```

Expected output (unrelated other lines are fine, but the three palette-relevant lines must be exactly):

```
 M static/textures/palette.png
 M static/world/world.glb
 M tools/blender/scripts/_palette.py
```

If anything else is listed under the new-modifications you're staging next, stop and inspect — Blender sometimes writes incidental .blend1 backups or modifies the .blend's "last save time" metadata. .blend1 files are ignored by .gitignore already; the .blend itself should NOT appear modified unless you saved it (we did NOT save it in this plan).

If `tools/blender/world.blend` shows as modified, that means Blender auto-saved or you hit `Ctrl+S` accidentally. Decide: include the .blend in this commit (only if there's no functional change — Blender saves are noisy binary diffs), or `git restore tools/blender/world.blend` if no edits were intended.

- [ ] **Step 6.2 — Stage the three artifacts**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git add tools/blender/scripts/_palette.py \
        static/textures/palette.png \
        static/world/world.glb
```

- [ ] **Step 6.3 — Commit**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git commit -m "$(cat <<'EOF'
palette: warm-shift meadow / dirt / sand cells

Sub-project A of the world.blend overhaul roadmap. Three cells
shift cold -> warm without changing cell indices:
  meadow_grass  #94a978 -> #a8b870   (cell 16)
  dirt_path     #6e6256 -> #85715a   (cell 23)
  sand_gravel   #9a8a72 -> #b09778   (cell 24)

Halfway between our alpine palette and Bruno's full-warm refs.
Mountains / snow / water / pine / sky cells unchanged — alpine
identity preserved.

Pipeline:
  1. _palette.py edited (3 hex changes)
  2. phase-01-palette-texture.py re-baked static/textures/palette.png
  3. phase-13-export-glb.py re-exported static/world/world.glb
     (palette is embedded inside GLB; phase-13 mandatory)
  4. Visual verified in Blender's Material Preview viewport:
     meadow / paths / shore read warmer; mountains / snow /
     water unchanged.

Unblocks roadmap sub-projects B, C, D.

Spec: docs/superpowers/specs/2026-05-27-world-palette-warm-shift-design.md
Plan: docs/superpowers/plans/2026-05-27-world-palette-warm-shift-plan.md
EOF
)"
```

- [ ] **Step 6.4 — Confirm commit landed**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git log -1 --stat
```

Expected: one commit, three files changed:
- `static/textures/palette.png` — small binary diff
- `static/world/world.glb` — larger binary diff
- `tools/blender/scripts/_palette.py` — 6 lines (3 changed = 3 minuses + 3 pluses)

Do **not** push to remote in this plan — local commit only. Pushing is a separate decision.

---

## Task 7 — Rollback (only if Task 5 failed)

If verification fails at any point in Task 5, revert everything before re-investigating.

- [ ] **Step 7.1 — Discard all three artifacts**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git restore tools/blender/scripts/_palette.py \
            static/textures/palette.png \
            static/world/world.glb
```

This is a non-destructive revert — restores all three files to their last committed state. Any uncommitted edits to those files are lost; this is intended.

- [ ] **Step 7.2 — Re-open `world.blend` in Blender (discard in-memory state)**

In Blender: File → Revert (or close the file without saving + reopen). This discards any in-memory texture caches that might still hold the warm-shifted palette image.

- [ ] **Step 7.3 — Confirm rollback is clean**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git status --short
```

Expected: no `M` lines for the three artifacts. If any still show modified, re-run Step 7.1 — the restore should be idempotent.

- [ ] **Step 7.4 — Report back what failed**

Hand back to the assistant with:
- which Step in Task 5 failed (e.g., 5.3, 5.4, 5.5);
- which surface looked wrong;
- whether you suspect cell-ordering drift, a stale embed, or a hex-target choice that doesn't read as expected on the actual terrain;

The assistant will then either revise the hex targets (in the visual companion) or re-investigate the pipeline.

---

## Self-review (assistant-side, post-write)

**1. Spec coverage**

| Spec section | Plan coverage |
|---|---|
| Goal — three cells, halfway between cold and Bruno-warm | Task 1 (exact hex changes) |
| Non-goals — no cell-index changes, no other cells | Task 0.3 + Task 2 (cell-index assertions); Step 1.5 (diff-must-be-3-lines check) |
| Architecture / data flow — `_palette.py` → phase-01 → phase-13 | Tasks 1 → 3 → 4 |
| Files touched — 1 source edit, 2 regenerated binaries | Tasks 1, 3, 4 produce exactly these |
| Untouched list | Covered by Step 6.1 diff check |
| Cell-index invariant — meadow_grass 16, dirt_path 23, sand_gravel 24 | Steps 0.3, 2.1, and the spec text inside Step 1.5 |
| Execution order | Tasks 0 → 6 in order |
| Verification — three changed, three unchanged, palette PNG inspect | Steps 5.3, 5.4, 5.5 |
| Rollback | Task 7 |
| Open item — GLB-embedding double-check | Step 0.2 + Step 4.3 (`gltf-transform inspect`) |

**2. Placeholder scan:** no "TBD" / "implement later" / "add appropriate" patterns in the plan body. The only literal "TODO" is the rollback message Task 7.4 mentions ("hand back to the assistant") — not a placeholder, just a directive.

**3. Type consistency:** hex strings are byte-exact across spec, swatch screen, and plan (`#a8b870`, `#85715a`, `#b09778`). Cell indices are byte-exact (16, 23, 24). Script paths, working-directory commands, and commit-message contents are consistent.
