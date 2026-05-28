# Bruno folio-2025 — World Analysis (Index)

**Source of truth:** `/Users/mahajankaran/Documents/Projects/folio-2025/scripts/blender_world_steps/`
**Browsable HTML index:** `scripts/blender_world_steps/index.html` (per-script breakdown, filterable)
**Date started:** 2026-05-27

---

## ⚠️ Status: this file + the 15 group `.md` files are GROUP-LEVEL NAVIGATION ONLY

The 16 `.md` files at this level (00-INDEX, 01-foundation, …, 15-finalize) were initially written as a high-level survey from `index.html` metadata, NOT from reading Bruno's Python code. They're useful for finding which scripts belong to which theme — they are **not** the source of truth for what Bruno's code actually does.

**The source of truth is the per-script deep `.md` files in the subfolders** (e.g., `01-foundation/000-init.md`, `02-ground-grass/020-terrain.md`, etc.). Those are written by Phase-1 sessions that actually open each Python file and document its construction.

See [HANDOFF.md](HANDOFF.md) for the Phase-1 batch queue and per-script `.md` format.

---

## What this whole analysis is for

Bruno's 142 Python scripts rebuild his entire folio-2025 world from a clean Blender scene. We are reading every script in depth so that we can **plan and build our own world** (Phase 2/3), using Bruno's techniques as a knowledge base. We are NOT comparing to karan-portfolio's existing code in this phase, and we are NOT planning what to keep/modify yet — that's Phase 2.

---

## World stats (Bruno's full world)

| Metric | Count |
|---:|---|
| Objects | 1,507 |
| Mesh datablocks | 368 |
| Materials | 35 |
| Node groups | 9 (geometry-nodes + shader + compositor) |
| Collections | 120 |
| Images / textures | 25 |
| Total verts | 72,169 |
| Total polys | 57,626 |
| Scripts | 142 (000-013 foundation + 020-139 per-collection + 999 finalize) |

---

## The big picture — how Bruno builds the world

```
000_init               wipe scene
001-013                FOUNDATION:  textures → mats → node-groups → mesh data
                                    → curves → armatures → lights → cameras
                                    → world shader → empty 120-collection skeleton
020_terrain            one mesh (Plane.134) + GeometryNodes modifier. THE island.
021_grass              one 3-vert mesh + GeometryNodes scatter. Covers the island.
022-139                ONE SCRIPT PER COLLECTION, in narrative order:
                       surface detail → trees → bushes → flowers → fences →
                       sections (bowling, race, lab, forge, landing, projects, …) →
                       props inside sections (jukebox, pins, tables, anvil, …) →
                       lighting (lanterns, poleLights) → benches → respawns →
                       vehicles → easter eggs → tornado → reference/hidden backups
999_finalize           applies parenting (all 1,507 objs) + view-layer excludes +
                       compositor link + active camera
```

**Every step script is additive and idempotent.** Re-running it doesn't dup objects (uses `bpy.data.X.get()` lookups). Each adds one collection's worth of objects.

---

## Cross-cutting patterns (read this once, applies everywhere)

### Materials — "palette" is THE main material
- **`palette`** is used by almost every visible mesh (terrain, rocks, slabs, trees, bushes, flowers, fences, bricks, furniture, tables, props, lanterns…). It's a single shader-graph material with per-vertex color attributes driving warm clay/olive/yellow-green tints. Looks varied because of the vertex-color baking, not because of many materials.
- **`emissive*RadialGradient`** variants (Orange, Blue, Green, Purple, White) for all light-emitting surfaces (lanterns, screens, signage glow, jukebox, etc.).
- **Branded content** has its own atlas-style material per artifact: `careerText*`, `cookieBanner`, `bowlingLabelStrike`, `circuitBrand/Webgl/Webgpu/Threejs`, `projectsLabels/Carpet`, `labCarpet`, `blackboardLabels`, `stylizedMap`.
- **Special**: `airDancer` (the inflatable tube guys), `waterfall` (animated water shader), `redGradient`, `gray`, `darkGray`, `black`, `mapPortal`, `mapAltar`.
- Total: 35 materials. Most sections only touch 1-3.

### Geometry — empties as anchors
- Many objects are `EMPTY` (no mesh) used as **anchors** for game logic (pin positions, respawn points, checkpoint volumes, light-emitter origins). They show up in counts but contribute zero geometry.
- A typical section script reads: `N×MESH + M×EMPTY` — the meshes are the visible props, the empties are the game-logic hooks.
- **Custom properties** on empties carry data: `mass`, `restitution`, `preventFrustum`, `preventAutoAdd`, `booleans`, `category`, `color`, `hasEnd`, `size`, `texture`. The runtime app reads these.

### Geometry-nodes modifiers
- **`Smooth by Angle.001/.002/.003`** — auto-smooth normals, applied widely.
- **`Geometry Nodes`** — terrain's procedural island.
- **`Geometry Nodes.001`** — grass scatter (used on the 3-vert grass mesh).
- **`Geometry Nodes.002`** — rails-along-curve, used in race track.
- **`Auto Smooth`** — variant of smoothing.

### Parenting model (applied in 999_finalize.py)
- Big "container" collections (`areas`, `scenery.002`, `oakTrees/birchTrees/cherryTrees`, `behindTheScene`, `bowling`, `circuit`, `landing`, `lab`, `projects`, `social`, `statue`, `timeMachine`, `toilet`, `vehicle`) are EMPTIES or skeleton collections that hold many child collections.
- Object parenting is real — props sit under their section's root empty, so moving the empty translates the whole section.
- View-layer excludes (23 collections) hide the "reference/backup" template copies from render.

### Visible vs hidden
- **`VISIBLE`** badge: in the live render.
- **`EXCLUDED`** badge: in the .blend but excluded from the view layer (template copies, archived variants, the minimap-camera setup, hidden easter eggs).
- **`HIDDEN`** badge: hidden in viewport (rare).

---

## Folder guide — group indexes + per-script subfolders

Each row has a **group index `.md`** (high-level navigation, written from `index.html` metadata — STALE for code details) and a **per-script subfolder** (deep `.md` per Bruno script — written by Phase-1 sessions reading each Python file).

| # | Group index | Per-script subfolder | Bruno scripts in group |
|---:|---|---|---|
| 01 | [01-foundation.md](01-foundation.md) | `01-foundation/` | 000-013 (20 actual files since 005 is 7 mesh chunks) |
| 02 | [02-ground-grass.md](02-ground-grass.md) | `02-ground-grass/` | 020, 021 |
| 03 | [03-surface-detail.md](03-surface-detail.md) | `03-surface-detail/` | 022-027, 051, 075 |
| 04 | [04-trees.md](04-trees.md) | `04-trees/` | 028, 032, 036, 134-136 |
| 05 | [05-foliage-flowers-boundaries.md](05-foliage-flowers-boundaries.md) | `05-foliage-flowers-boundaries/` | 040-043 |
| 06 | [06-buildings-structures.md](06-buildings-structures.md) | `06-buildings-structures/` | 047, 048, 049, 081, 091, 105, 108, 114, 115, 132, 133 |
| 07 | [07-major-areas.md](07-major-areas.md) | `07-major-areas/` | 044, 052, 053, 062, 088 |
| 08 | [08-race-track.md](08-race-track.md) | `08-race-track/` | 065-068, 071, 073, 074, 076-078, 120, 122, 123, 137 |
| 09 | [09-bowling.md](09-bowling.md) | `09-bowling/` | 054-060, 069, 070 |
| 10 | [10-lighting.md](10-lighting.md) | `10-lighting/` | 050, 089, 117, 118 |
| 11 | [11-furniture-displays-boards.md](11-furniture-displays-boards.md) | `11-furniture-displays-boards/` | 064, 072, 082, 083, 085-087, 090, 095, 096, 099, 111-113, 116, 119 |
| 12 | [12-workshop-portfolio-icons.md](12-workshop-portfolio-icons.md) | `12-workshop-portfolio-icons/` | 045, 061, 084, 093, 094, 097, 098, 100, 102, 103, 104 |
| 13 | [13-food-misc-fx.md](13-food-misc-fx.md) | `13-food-misc-fx/` | 063, 079, 080, 092, 101, 107, 110, 121, 124, 126, 128, 129, 130, 138, 139 |
| 14 | [14-reference-hidden.md](14-reference-hidden.md) | `14-reference-hidden/` | 029-031, 033-035, 037-039, 046, 106, 109, 125, 127, 131 |
| 15 | [15-finalize.md](15-finalize.md) | `15-finalize/` | 999 |

**Total: 142 scripts to deep-analyze across 5 batches of 3 groups each. See [HANDOFF.md](HANDOFF.md) for the batch queue and per-script `.md` format.**

---

## What's NOT in scope for Phase 1

- **Karan-portfolio code, paths, assets, or comparison.** Off-limits until Phase 2.
- **TSL/runtime shader code from `folio-2025/sources/`.** Blender build scripts only.
- **Bruno's Three.js game runtime.** Out of scope.
- **Decisions about what to adopt/modify/skip.** That's Phase 2 planning.

---

## Pointers

- Bruno's repo: `/Users/mahajankaran/Documents/Projects/folio-2025/`
- Step scripts: `folio-2025/scripts/blender_world_steps/steps/000_init.py` through `999_finalize.py`
- HTML index (browse-in-browser): `folio-2025/scripts/blender_world_steps/index.html` (navigation aid, NOT source of truth)
- Bruno's build-script README: `folio-2025/scripts/blender_world_steps/README.md`
- Related memories: `reference-folio2025-path`, `reference-bruno-ground-systems`, `reference-bruno-bushes-are-sdf`, `reference-bruno-world-analysis`
