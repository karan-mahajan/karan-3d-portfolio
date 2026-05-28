# Bruno-World Python Analysis — Session Handoff

**Read this FIRST in any new session continuing this work. ~5 minutes.**

---

## The arc

1. 🟡 **Phase 1 — Deep Python analysis of Bruno's folio-2025 build scripts** (IN PROGRESS, 5 batches)
   Output: one deep `.md` per script in subfolders under `docs/superpowers/research/2026-05-27-bruno-world/`. Bruno's 142 Python scripts construct a complete Blender world from a blank `.blend`; this phase reads every script and documents what code actually does.

2. ⏳ **Phase 2 — Plan our own world** (later, after Phase 1 complete)
   Now that I "have all the knowledge," design our world from scratch. May adopt some Bruno techniques, modify many, skip the rest. **No code yet.**

3. ⏳ **Phase 3 — Spec + plan + implement** (later, per-section sub-projects)
   For each section we plan: spec → plan → bundle commit. Hybrid (user runs Blender, assistant edits Python + verifies).

**Karan-portfolio code is NOT analyzed in Phase 1.** We are studying Bruno's blank-file world reconstruction only. The existing portfolio repo is untouched until Phase 3.

---

## What "deep Python analysis" means

For every Python script in `/Users/mahajankaran/Documents/Projects/folio-2025/scripts/blender_world_steps/steps/`:

- **Open the file** (don't just rely on the `index.html` description)
- **Document what the code actually does** — Blender API calls, mesh/curve datablock references, materials assigned, modifiers added (with the specific node-group bindings), custom properties set, world-space positions for anchor empties, parent collections, object-type breakdown
- **Capture the technique** — how is Bruno constructing this thing? What's reusable, what's hand-authored? Are there geometry-nodes templates, instance patterns, curve-driven extrusions?
- **Cross-references** — which earlier scripts' datablocks does this script depend on (e.g., "uses `bpy.data.meshes.get('Plane.134')` loaded in 005_meshes_00.py")? Which later scripts will parent things under what this script creates?

Goal: after Phase 1, **I should be able to re-create any Bruno section from memory using the .md alone**. The .md is the recipe.

---

## Output structure

```
docs/superpowers/research/2026-05-27-bruno-world/
├── HANDOFF.md                          (you are here)
├── 00-INDEX.md                         (overview + folder map)
├── 01-foundation.md                    (group index, links to subfolder)
├── 01-foundation/                      (NEW — deep per-script)
│   ├── 000-init.md
│   ├── 001-texts.md
│   ├── 002-images.md
│   ├── 003-node-groups.md
│   ├── 004-materials.md
│   ├── 005-meshes-00.md
│   ├── 005-meshes-01.md
│   ├── ... (one per chunk)
│   ├── 005-meshes-06.md
│   ├── 006-metaballs.md
│   ├── 007-curves.md
│   ├── 008-armatures.md
│   ├── 009-lights.md
│   ├── 010-cameras.md
│   ├── 011-linestyles.md
│   ├── 012-world.md
│   └── 013-collections.md
├── 02-ground-grass.md                  (group index)
├── 02-ground-grass/
│   ├── 020-terrain.md
│   └── 021-grass.md
├── 03-surface-detail.md
├── 03-surface-detail/
│   ├── 022-scenery-002.md
│   ├── 023-basaltRocks.md
│   ├── ... (one per script)
│   └── 075-scenery.md
├── 04-trees.md
├── 04-trees/
│   └── ...
├── ... (15 subfolders total)
├── 15-finalize.md
└── 15-finalize/
    └── 999-finalize.md
```

The 16 existing group `.md` files (00-INDEX through 15-finalize) act as **group-level indexes** — they describe what's in each theme and link to the per-script deep `.md` files in the matching subfolder. They are NOT the deep analysis themselves.

---

## Per-script `.md` format (every deep file follows this)

```markdown
# NNN_scriptname.py — <one-line purpose>

**Path:** `folio-2025/scripts/blender_world_steps/steps/NNN_scriptname.py`
**Lines:** XX
**Adds:** N objects of type X to collection `coll-name`
**Group:** [NN-group-name](../NN-group-name.md)

## What it does (code-level)
<Step-by-step in plain English of what the Python script actually does.
 Reference specific Blender API patterns (`bpy.data.objects.new`,
 `coll.objects.link`, `modifier.node_group = ...`, etc.)>

## Key data
- **Datablocks referenced** (from foundation scripts): mesh `Plane.134`, material `palette`, node-group `Smooth by Angle.003`, ...
- **Materials assigned**: ...
- **Modifiers added**: NODES (Smooth by Angle.003), BEVEL, ARRAY, ...
- **Custom properties**: mass=10.0, restitution=0.8, ...
- **World positions of key anchors**: (extract `ob.location = (...)` for the load-bearing empties)
- **Object types breakdown**: 5 MESH, 8 EMPTY, 0 CURVE
- **Parent collection**: `circuit` (set in 062 or finalize)

## Technique / recipe
<How would we build this from scratch? What's the pattern?
 - Hand-placed empties driving a scatter?
 - Curve-driven extrusion via Geometry Nodes?
 - Array modifier for repeated patterns?
 - Just N hardcoded `ob.location` calls?>
<Pure observation of Bruno's approach — no recommendations.>

## Connections
- **Reads from**: 005_meshes_03.py (specific mesh), 004_materials.py (palette), ...
- **Read by**: 999_finalize.py (parents these objects under `circuit`)
- **Depends on** (must run before this): 013_collections.py (collection skeleton), 005 meshes
- **Depended on by** (must run after this): none / specific scripts

## Notable code patterns
<Anything quirky or reusable in this script — a clever idempotent guard,
 a custom-prop pattern, an array-modifier trick, etc. Quote code only if
 it's load-bearing.>
```

Keep each file **50-200 lines depending on script complexity**. A 12-line stub script (e.g., 044_areas.py) gets a 30-line .md; a 1500-line script (e.g., 040_bushes.py) gets a 150-line .md focused on the technique, not a line-by-line dump.

---

## Workflow rules (apply throughout — DO NOT violate)

- **NO `Co-Authored-By: Claude` trailer in any commit message.** (memory: `feedback-no-claude-coauthor`)
- **NO intermediate commits during Phase 1.** All Phase 1 analysis docs can be committed as one bundle at the very end (after Batch 5), or left uncommitted until Phase 2 starts. Confirm with user before committing. (memory: `feedback-no-intermediate-commits`)
- **NO karan-portfolio code is touched, read, or compared.** Phase 1 is pure Bruno-world Python study.
- **Read the actual Python files.** Don't summarize from `index.html` alone — that was the prior session's mistake.
- **The 16 group `.md` files in this folder are STALE group indexes** — they were written from index.html metadata, not from reading the Python. They're fine for navigation but should NOT be treated as the source of truth. The per-script subfolder files are the source of truth for Phase 1.

---

## Batch queue — Phase 1 (5 sessions × 3 thematic groups each)

| Batch | Groups | Scripts to deep-read | Output subfolders |
|---:|---|---|---|
| 1 | 01-foundation, 02-ground-grass, 03-surface-detail | 20 + 2 + 8 = **30 scripts** | `01-foundation/`, `02-ground-grass/`, `03-surface-detail/` |
| 2 | 04-trees, 05-foliage-flowers-boundaries, 06-buildings-structures | 6 + 4 + 11 = **21 scripts** | `04-trees/`, `05-foliage-flowers-boundaries/`, `06-buildings-structures/` |
| 3 | 07-major-areas, 08-race-track, 09-bowling | 5 + 14 + 9 = **28 scripts** | `07-major-areas/`, `08-race-track/`, `09-bowling/` |
| 4 | 10-lighting, 11-furniture-displays-boards, 12-workshop-portfolio-icons | 4 + 16 + 11 = **31 scripts** | `10-lighting/`, `11-furniture-displays-boards/`, `12-workshop-portfolio-icons/` |
| 5 | 13-food-misc-fx, 14-reference-hidden, 15-finalize | 15 + 15 + 1 = **31 scripts** | `13-food-misc-fx/`, `14-reference-hidden/`, `15-finalize/` |

**Total: 5 batches, 142 deep `.md` files, ~5 sessions.**

After Batch 5, Phase 1 is complete. The user will then decide what world to build (Phase 2 planning).

---

## What to do in any Phase-1 session (the recipe)

1. **Read HANDOFF.md** (you're doing it now).
2. **Read 00-INDEX.md** for the world's big-picture composition.
3. **Read this batch's 3 group `.md` files** (for navigation context — they list which scripts are in each group).
4. **For each script in the 3 groups:**
   a. Open the Python file at `folio-2025/scripts/blender_world_steps/steps/<script>.py`
   b. Read it fully (or in chunks for the heavy ones — `005_meshes_*.py`, `040_bushes.py`, `055_furnitures.py`)
   c. Write a per-script `.md` in the matching subfolder using the format above
5. **At end:** report a short summary (which subfolders + files were created, what surprised you about Bruno's code patterns, any cross-cutting techniques you noticed) and stop. Don't commit. Don't start the next batch.

For heavy scripts (lots of empties + lots of meshes), use **multiple parallel agent calls** if useful — but each per-script `.md` should be written by you (the lead session) to keep voice consistent.

---

## What's NOT covered in Phase 1

- **Karan-portfolio code, paths, assets, or comparison.** Off-limits.
- **TSL / runtime shader code from `folio-2025/sources/`.** Phase 1 is Blender-build scripts only.
- **Bruno's Three.js game code.** Same — out of scope.
- **Spec, plan, or implementation of our own scripts.** That's Phase 2/3.
- **Decisions about what we'll adopt.** Pure description in Phase 1.

---

## Phase 2/3 — Build our world (BUILD SESSIONS, after Phase 1 is complete)

Once all 142 per-script `.md` files exist, Phase 2/3 begins: actually constructing OUR Blender world. **One build session per thematic section.** Each session does the full loop: recreate Bruno → user reviews → brainstorm modifications → implement custom version → verify → bundle commit.

### Per-section session workflow

1. **Recreate** — write Python that mirrors Bruno's setup for this section. File: `tools/blender/scripts/v3/NN-section-bruno.py`. Read the per-script `.md` deep analyses in `docs/superpowers/research/2026-05-27-bruno-world/NN-section/` as the recipe.
2. **User runs in Blender, sees Bruno's faithful version.**
3. **Brainstorm** — interactive with user: skip whole section? change layout? different theme? fewer instances? combine with another section? The user might decide they don't want this section at all — that's fine, see below.
4. **Modify** — write customized version: `tools/blender/scripts/v3/NN-section.py` (side-by-side with `bruno.py`).
5. **User verifies** the custom version in Blender. Iterate if needed.
6. **Bundle commit** at session end — confirm message with user, NO co-author trailer.

### Build session order

| # | Section | Required? | Notes |
|---:|---|---|---|
| 1 | 01-foundation | **REQUIRED** | Textures, mats, node groups, mesh data, curves, collections — everything depends on this |
| 2 | 02-ground-grass | **REQUIRED** | Terrain canvas + grass scatter |
| 3 | 03-surface-detail | likely keep | Rocks, slabs, roads, bridges |
| 4 | 04-trees | likely keep | 3 species |
| 5 | 05-foliage-flowers-boundaries | likely keep | Bushes, flowers, fences, bricks |
| 6 | 06-buildings-structures | optional | Building, altar, cabin, lab anchors |
| 7 | 07-major-areas | required if any sections kept | Zone-anchor architecture |
| 8 | 08-race-track | optional (probably skip) | Full race mini-game |
| 9 | 09-bowling | optional (probably skip) | Full bowling alley |
| 10 | 10-lighting | likely keep | Lanterns + poleLights + bonfire |
| 11 | 11-furniture-displays-boards | partial | Furniture/screens/boards per section kept |
| 12 | 12-workshop-portfolio-icons | likely keep | Career/projects/social — your actual portfolio content |
| 13 | 13-food-misc-fx | partial | Cookie, title, airDancers — pick what you want |
| 14 | 14-reference-hidden | partial | Tree-template, statue, minimap rig, vehicle template |
| 15 | 15-finalize | **REQUIRED** | Parenting + view-layer wiring (must come last) |

Sections #1, #2, #15 are mandatory. Order between them is up to you, but build dependencies suggest: trees + foliage before structures that exclude them; areas/anchors before furniture that lives inside them; lighting + finalize last.

### Skipped sections

If you decide to skip a section entirely during the brainstorm:
- Session writes a SHORT `NN-section-bruno.py` (placeholder + comment explaining what Bruno had and why we skipped) — useful as a marker.
- No `NN-section.py` is written.
- Bundle commit notes the skip.

### Naming convention

- `NN-section-bruno.py` — faithful Bruno recreation, never re-edited after first commit
- `NN-section.py` — your customized version (modified from -bruno)
- For sections needing multiple .py files (e.g., foundation), split as: `01-foundation-bruno-01-images.py`, `01-foundation-bruno-02-materials.py`, etc. — keep the `-bruno-` infix consistent.

### What goes in v3/

```
tools/blender/scripts/v3/
├── README.md                         (sub-project intro; written in Build Session 1)
├── 01-foundation-bruno-*.py          (split into chunks if large)
├── 01-foundation-*.py
├── 02-ground-grass-bruno.py
├── 02-ground-grass.py
├── ...
└── 15-finalize-bruno.py
    15-finalize.py
```

`v3/` is a clean slate — does NOT touch existing `tools/blender/scripts/phase-00..phase-13.py`. Old build remains as reference; v3 becomes the new canonical build once finalized.

### Build-session prompt (template — copy into a new chat to start a section)

```
I'm continuing a multi-session project to build our own Blender world
using Bruno Simon's folio-2025 as a knowledge base.
Phase 1 (deep Python analysis of all 142 Bruno scripts) is done.

THIS SESSION = BUILD SECTION [NN-section-name]
(e.g., "01-foundation", "04-trees", "10-lighting")

START HERE — read in order:
1. docs/superpowers/research/2026-05-27-bruno-world/HANDOFF.md
   (workflow, session split, naming, rules — Phase 2/3 section)
2. The per-script deep analyses for THIS section at
   docs/superpowers/research/2026-05-27-bruno-world/[NN-section]/
   (these are the recipe for what to recreate)
3. docs/superpowers/research/2026-05-27-bruno-world/[NN-section].md
   (group navigation — optional context)

DO THE FULL LOOP THIS SESSION (per HANDOFF.md Phase 2/3 workflow):
  Part 1: Recreate Bruno's version → tools/blender/scripts/v3/[NN-section]-bruno-*.py
  Part 2: Ask user to run it in Blender, wait for them to confirm.
  Part 3: Brainstorm what they want different (use brainstorming skill
          if helpful — invoke superpowers:brainstorming).
  Part 4: Write customized version → tools/blender/scripts/v3/[NN-section]-*.py
  Part 5: User verifies the custom version. Iterate.
  Part 6: Bundle commit — confirm message with user, NO Co-Authored-By.

Constraints (do not violate):
- NO commits before Part 6. All section work = ONE bundled commit.
- NO karan-portfolio src/ or static/ code is touched.
- ONLY write inside tools/blender/scripts/v3/. Don't modify the
  existing phase-00 through phase-13 scripts.
- world.blend may be touched by scripts that call save_as_mainfile —
  `git restore tools/blender/world.blend` if no intentional .blend edit.
- If user wants to skip this entire section, write a placeholder bruno.py
  with a comment explaining the skip, then bundle commit and stop.

When section is done (Part 6 committed), report a short summary and
stop. Don't start the next section — user opens a new chat for that.
```

---

## Pointers

- **Bruno's repo:** `/Users/mahajankaran/Documents/Projects/folio-2025/`
- **Bruno's build scripts folder:** `folio-2025/scripts/blender_world_steps/steps/`
- **Bruno's browsable script index (HTML):** `folio-2025/scripts/blender_world_steps/index.html` — use as a navigation aid, NOT the source of truth
- **Bruno's README for the build scripts:** `folio-2025/scripts/blender_world_steps/README.md`
- **karan-portfolio project root:** `/Users/mahajankaran/Documents/Projects/karan-portfolio/` (cwd in sessions, but DO NOT analyze its code in Phase 1)
- **Auto-memory:** `/Users/mahajankaran/.claude/projects/-Users-mahajankaran-Documents-Projects-karan-portfolio/memory/MEMORY.md`
- **Related memories**: `reference-folio2025-path`, `reference-bruno-ground-systems`, `reference-bruno-bushes-are-sdf`, `reference-bruno-world-analysis`
