# 14 — Reference / Template / Hidden Backups

**Bruno category:** 🗃️ Reference / Backup (Hidden)
**Scripts:** 15 (029, 030, 031, 033, 034, 035, 037, 038, 039, 046, 106, 109, 125, 127, 131)
**Total objects:** 135 (mix of curve sources, mesh templates, the statue rig, and the minimap rig)
**Status:** mostly EXCLUDED; some VISIBLE (visual variants, references collections, statue default)

---

## Purpose

This group splits into FIVE distinct backup/template purposes — they're all "not in the player-facing world directly" but each serves a different role:

1. **Tree source templates** — the `archives.*`, `visual.*`, `references.*` per-species collections (covered partially in [04-trees.md](04-trees.md))
2. **The map rig** — minimap cameras + lights + map-only altar/behindTheScene stand-ins
3. **The statue character** — `default` (rigged mesh) + `archive.001` (a metaball reference)
4. **The vehicle templates** — `default.001` (the runtime vehicle source), `archives.003` (a rigged sub-vehicle reference)
5. **Plain curve archives** — `archives` / `archives.001` / `archives.002` / `archives.004` (single-curve splines used by parent collections)

---

## Scripts — Tree references (per-species 4-collection pattern)

| # | File | Objs | Types | Materials | What it adds | Status | For |
|---:|---|---:|---|---|---|---|---|
| 029 | `029_archives.001.py` | 1 | 1×CURVE | — | Source curve for oak tree trunk | EXCLUDED | oakTrees |
| 030 | `030_references.002.py` | 24 | 24×CURVE | — | 24 scatter-anchor curves for oak placement | VISIBLE | oakTrees |
| 031 | `031_visual.004.py` | 7 | 7×MESH | `palette` | 7 oak leaf-cluster mesh variants | VISIBLE | oakTrees |
| 033 | `033_archives.002.py` | 1 | 1×CURVE | — | Source curve for birch tree trunk | EXCLUDED | birchTrees |
| 034 | `034_references.py` | 26 | 26×MESH | — | 26 birch scatter-reference meshes | VISIBLE | birchTrees |
| 035 | `035_visual.002.py` | 7 | 7×MESH | `palette` | 7 birch leaf-cluster mesh variants | VISIBLE | birchTrees |
| 037 | `037_archives.py` | 1 | 1×CURVE | — | Source curve for cherry tree trunk | EXCLUDED | cherryTrees |
| 038 | `038_references.003.py` | 20 | 20×CURVE | — | 20 cherry scatter-anchor curves | VISIBLE | cherryTrees |
| 039 | `039_visual.005.py` | 7 | 7×MESH | `palette` | 7 cherry leaf-cluster mesh variants | VISIBLE | cherryTrees |

**Pattern recap:** each tree species has (archives = 1 source curve) + (visual = 7 variant meshes) + (references = 20-26 scatter anchors). The `.001` collections (134-136, see [04-trees.md](04-trees.md)) are the final instanced placements.

## Scripts — Map / minimap rig

| # | File | Objs | Types | Materials | What it adds |
|---:|---|---:|---|---|---|
| 131 | `131_map.py` | 4 | 2×CAMERA, 2×LIGHT | — | The minimap rendering rig: `cameraTerrain` (ortho camera at z=55.7), `cameraVehicle` (ortho camera, hidden), `day` light (area light), `night` light (area light). All EXCLUDED from main render. Parents `altar.001`, `behindTheScene.001`, `birchTrees.001`, `oakTrees.001`, `cherryTrees.001`, `vehicle.001` |
| 132 | `132_altar.001.py` | 1 | 1×MESH | `mapPortal` | Map-only altar stand-in (see [06-buildings-structures.md](06-buildings-structures.md)) |
| 133 | `133_behindTheScene.001.py` | 1 | 1×MESH | `mapAltar` | Map-only behindTheScene stand-in (see [06](06-buildings-structures.md)) |

**The minimap rig is its own self-contained world.** The minimap camera renders a top-down view using:
- The terrain (visible to both cameras)
- The `.001` tree copies (134, 135, 136 — visible to minimap, excluded from main)
- The `altar.001` + `behindTheScene.001` stand-ins (132, 133)
- The `vehicle.001` template (137)
- Lit by `day` and `night` area lights (controlled by time-of-day)

## Scripts — Statue character

| # | File | Objs | Types | Materials | What it adds |
|---:|---|---:|---|---|---|
| 046 | `046_archive.001.py` | 1 | 1×META | — | A single metaball — referenced by the statue/achievement system. EXCLUDED and HIDDEN |
| 106 | `106_default.py` | 15 | 7×EMPTY, 5×MESH, 3×ARMATURE | `palette` | THE statue character — 5 meshes + 3 armatures (bone rigs) + 7 empties. 3 ARMATURE modifiers + 1 MIRROR modifier. 1,489 verts. VISIBLE. Parented under `statue` (105) |

The statue is Bruno himself (or his avatar), rigged with 3 armatures probably for separable body parts (head, torso, accessories). Holds the FWA award badges from script 107.

## Scripts — Vehicle templates

| # | File | Objs | Types | Materials | What it adds |
|---:|---|---:|---|---|---|
| 125 | `125_default.001.py` | 24 | 18×MESH, 6×EMPTY | `darkGray`, `emissiveOrangeRadialGradient`, `emissivePurpleRadialGradient`, `palette`, `redGradient` | THE main runtime vehicle — 18 meshes (body, wheels, exhaust, lights, etc.) + 6 empties. Custom prop `booleans` (probably modifier-state flags). VISIBLE. Parented under `vehicle` (123) |
| 127 | `127_archives.003.py` | 2 | 1×ARMATURE, 1×MESH | — | A rigged sub-vehicle reference — 1 armature + 1 mesh (likely a hand or a separable vehicle component). 1 ARMATURE + 1 NODES modifier (Auto Smooth). EXCLUDED. Parents `sudo` (128) |

## Scripts — Plain curve archives

| # | File | Objs | Types | What it adds |
|---:|---|---:|---|---|
| 109 | `109_archives.004.py` | 1 | 1×CURVE | A single curve — used by `timeMachine` (108). EXCLUDED. |

(`archives` / `archives.001` / `archives.002` are listed in the tree-references table above — they're the per-species trunk curves.)

---

## Why this design works for Bruno

### Template/instance pattern
- **`archives.*` + `visual.*` + `references.*` per tree species** lets Bruno tweak the trunk curve once and re-bake all 20-26 instances per species. Editing the source in `archives.001` updates every oak tree.
- **`.001` collections are the "fully baked" instances**, the parent collections (oakTrees/birchTrees/cherryTrees) are the template registry.

### Map portal trick
- The minimap renders a SEPARATE scene composition using its own dedicated meshes (`altar.001`, `behindTheScene.001`) with map-only materials (`mapPortal`, `mapAltar`).
- This means the minimap doesn't try to render the in-world altar (which has emissive flames + 15 sub-objects) — instead it renders a stylized stand-in that reads cleanly at small scale.
- The view-layer exclusion is what enables this: main camera sees `altar`, minimap camera sees `altar.001`.

### Rigged content (statue + vehicle)
- **Statue (`default`, 106)** is Bruno's avatar showing off FWA awards inside the social zone.
- **Vehicle (`default.001`, 125)** is the runtime-controlled car (lives under `vehicle/`).
- **Sudo character (`sudo`, 128, see [13](13-food-misc-fx.md))** uses `archives.003` (127) as its rig reference — `sudo` is the hidden admin/developer character.

### Custom prop `booleans` on vehicle
- Likely modifier-state flags (which lights are on, antenna up/down, etc.) consumed by the runtime to switch vehicle appearance.

---

## The full map collection's children

`131_map.py` parents these collections (all EXCLUDED from main render, all visible to minimap camera):
- `altar.001` (132) — minimap altar
- `behindTheScene.001` (133) — minimap backstage
- `birchTrees.001` (134) — 26 minimap-ready birch trees
- `oakTrees.001` (136) — 24 minimap-ready oak trees
- `cherryTrees.001` (135) — 20 minimap-ready cherry trees
- `vehicle.001` (137) — minimap-ready vehicle template

The minimap renders this isolated subset — a clean stylized top-down of the world's key features.

---

## Cross-references

- **Tree visual breakdown:** [04-trees.md](04-trees.md) — the visible final-instance trees use the templates here
- **Statue narrative:** [12-workshop-portfolio-icons.md](12-workshop-portfolio-icons.md) — statue is part of the `social` zone
- **Vehicle in race:** [08-race-track.md](08-race-track.md) — `vehicle.001` template referenced from there
- **Map portal materials:** [06-buildings-structures.md](06-buildings-structures.md) — `altar.001` and `behindTheScene.001` belong to map system but described in buildings

---

## Source pointers

- Step scripts: 15 files (see tables above)
- Materials specific to this group: `mapPortal`, `mapAltar`
- Modifiers: ARMATURE (default, sudo references), MIRROR (default vehicle parts), NODES (Auto Smooth on archives.003)
- Bruno's runtime minimap renderer: `folio-2025/sources/Game/UI/` or `folio-2025/sources/Game/Map/`
- Bruno's runtime vehicle controller: `folio-2025/sources/Game/Vehicle/`
