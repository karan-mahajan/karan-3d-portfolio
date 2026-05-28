# v3 — Blender world build (Bruno-informed)

A clean-slate rebuild of the Blender world, section by section, using
Bruno Simon's folio-2025 as a knowledge base. v3 is independent from
`tools/blender/scripts/phase-00..phase-13.py` (the legacy v2 build).
Old phases stay untouched as reference until v3 is finished.

The deep per-script analyses that drove each section live at
`docs/superpowers/research/2026-05-27-bruno-world/NN-section/`. The
session workflow is in that folder's `HANDOFF.md` (Phase 2/3).

---

## Layout — two parallel folders, each self-contained

```
tools/blender/scripts/v3/
├── README.md               (you are here)
├── bruno/                  Bruno's faithful reference
│   ├── 01-foundation-bruno-*.py  (20 step scripts, copied verbatim
│   │                              from folio-2025/scripts/blender_world_steps/steps/)
│   ├── 01-foundation-bruno-run-all.py    (runs all 20)
│   └── resources/          Bruno's 24 textures (palette + terrain
│                           masks + branded labels), mirroring his
│                           original folder layout
└── karan/                  Our customized version
    ├── 01-foundation-palette.py          (delta: swap palette image)
    ├── 01-foundation-run-all.py          (runs bruno then deltas)
    └── resources/          Our textures (palette.png — the sunset
                            16-color strip; more files added as we
                            customize later sections)
```

Each folder ships its own resources so it's portable. Run-all scripts
are absolute-path-hardcoded (single-developer project, no portability
concern).

`.blend` save targets (gitignored, regenerable from scripts):

- `tools/blender/world.blend` — legacy v2 build. **Don't overwrite.**
- `tools/blender/world-v3-bruno.blend` — auto-saved by `bruno/01-foundation-bruno-run-all.py` at the end of its run.
- `tools/blender/world-v3-karan.blend` — auto-saved by `karan/01-foundation-run-all.py` at the end of its run.

Both runners call `bpy.ops.wm.save_as_mainfile()` after their final step,
so you don't need to `File > Save As ...` manually — just open Blender
on any fresh empty file, run the script, and the result is written to
disk under the right name.

---

## Running a section

### Bruno-faithful version

1. Blender → `File > New > General` (fresh blank scene).
2. **Python Console** (more reliable than Text Editor `Alt+P`):
   ```python
   exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/01-foundation-bruno-run-all.py').read())
   ```
3. The script auto-saves to `tools/blender/world-v3-bruno.blend` when it
   finishes.

### Karan-customized version

1. Blender → `File > New > General`.
2. **Python Console:**
   ```python
   exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/01-foundation-run-all.py').read())
   ```
3. The script auto-saves to `tools/blender/world-v3-karan.blend` when it
   finishes.

(Or Text Editor + `Alt+P` if it works for you. The console form sidesteps
`__file__` resolution and execution-context issues we've hit.)

### Headless

```bash
/Applications/Blender.app/Contents/MacOS/Blender \
    --background --factory-startup \
    --python tools/blender/scripts/v3/karan/01-foundation-run-all.py
```

---

## Foundation note

`01-foundation-bruno-000-init.py` wipes every datablock category. **Don't
run it on a .blend you care about** — use a fresh empty file. Foundation
scripts populate datablocks but spawn no visible scene objects; the
viewport stays empty. Verification happens in the **Outliner** (display
mode `Current File` or `Blender File`). After a successful run:

| Category | Count |
|---|---:|
| Cameras | 2 |
| Collections | 120 |
| Images | 25 |
| Lights | 2 |
| Line Styles | 1 |
| Materials | 35 |
| Meshes | 368 |
| Worlds | 1 |
| Curves | 13 |
| Armatures | 6 |
| Metaballs | 2 |
| Texts | 3 |
| Node Groups | 9 |

### Karan-customized policy

Per the Phase 2/3 decision: **we don't drop anything from Bruno's
library yet.** All 368 meshes, 35 materials, 120 collections etc. stay
loaded. Sections that don't need a Bruno datablock simply don't reference
it. Later, if a Bruno-specific asset proves genuinely unused, we'll
remove it then.

The only substantive delta in this session is the **palette**:
`karan/01-foundation-palette.py` overrides Bruno's `palette` image
datablock to point at our `karan/resources/palette.png` — a 128×4 strip
of 16 sunset colors (dark warm browns → beach sands → sunset
peach/orange/red → warm golds → olive/forest greens → teal/ocean blues →
warm gray-brown).
