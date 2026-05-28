# 06 — Buildings & Structures

**Bruno category:** 🏠 Buildings & Structures
**Scripts:** 11 (047, 048, 049, 081, 091, 105, 108, 114, 115, 132, 133)
**Total objects:** 56 (10 visible-built + 5 anchor + 7 timeMachine + 4 toilet + 5 cabin + 11 lab + 1 kiosk + 1 statue parent + 132/133 templates)
**Status:** most VISIBLE, `altar.001` + `behindTheScene.001` (132/133) EXCLUDED (map-portal template copies)

---

## Purpose

The named built objects in Bruno's world — actual architecture (`building`, `cabin`, `lab`, `kiosk`), ritual structures (`altar`), gameplay-area anchors (`behindTheScene`, `statue`, `timeMachine`, `toilet`), plus EXCLUDED template copies used by the minimap (`altar.001`, `behindTheScene.001`).

---

## Scripts

| # | File | Objs | Types | Materials | What it adds | Children populated later |
|---:|---|---:|---|---|---|---|
| 047 | `047_building.py` | 6 | 6×MESH | `emissiveBlueRadialGradient`, `palette`, `waterfall` | The main "building" — 6 meshes incl. a waterfall material. 3 NODES modifiers (Smooth by Angle.003) | — |
| 048 | `048_altar.py` | 15 | 9×MESH, 6×EMPTY | `emissiveOrangeRadialGradient`, `palette` | Ritual altar — 9 meshes + 6 anchor empties (probably candle/effect positions). 1,712 verts | — |
| 049 | `049_behindTheScene.py` | 5 | 5×EMPTY | — | Just 5 anchor empties. Parents `lightGenerators`, `scenery.001` | lightGenerators (050), scenery.001 (051) |
| 081 | `081_lab.py` | 11 | 8×EMPTY, 3×MESH | `labCarpet`, `palette` | Lab room — 3 meshes (probably floor/walls/carpet) + 8 anchor empties for prop placement | mainTable, scroller, board.001, blackBoard.001, cauldron, sideTable |
| 091 | `091_kiosk.py` | 1 | 1×EMPTY | — | Just one empty — the kiosk lives in the `landing` area | — |
| 105 | `105_statue.py` | 0 | — | — | Empty parent — holds `default`, `FWA` | default (106), FWA (107) |
| 108 | `108_timeMachine.py` | 9 | 7×EMPTY, 2×MESH | `palette` | Time-machine anchor + 2 small structural meshes. Parents 5 child collections | archives.004, tv, playstation, stool.001, cups |
| 114 | `114_toilet.py` | 4 | 3×EMPTY, 1×MESH | `palette` | Toilet room — 1 mesh + 3 empties. Parents cabin + stool | cabin (115), stool (116) |
| 115 | `115_cabin.py` | 5 | 2×EMPTY, 2×MESH, 1×META | `emissiveOrangeRadialGradient`, `palette` | The cabin — 2 meshes + 1 METABALL (moss?) + 2 anchors. Custom prop `mass` (interactable cabin?) | — |
| 132 | `132_altar.001.py` | 1 | 1×MESH | `mapPortal` | Map portal mesh — EXCLUDED. Used for minimap rendering / portal effect | — |
| 133 | `133_behindTheScene.001.py` | 1 | 1×MESH | `mapAltar` | Map altar mesh — EXCLUDED. Map-only stand-in for the altar | — |

---

## Relationships

```
behindTheScene/                 (5 empties; parents scenery.001 + lightGenerators)
├── lightGenerators/            (12 objects — emissive mesh lights)
└── scenery.001/                (8 props)

statue/                         (empty parent)
├── default/                    (15 — the statue mesh + 3 armatures, see 14-reference-hidden.md)
└── FWA/                        (4 — FWA award badges)

timeMachine/                    (7 empties + 2 meshes; parents 5 collections)
├── archives.004/               (1 curve)
├── tv/                         (6)
├── playstation/                (4)
├── stool.001/                  (2)
└── cups/                       (6)

toilet/                         (3 empties + 1 mesh)
├── cabin/                      (5)
└── stool/                      (8)

lab/                            (8 empties + 3 meshes; parents 6 sub-areas)
├── mainTable/                  (6)
├── scroller/                   (14)
├── board.001/                  (14)
├── blackBoard.001/             (8)
├── cauldron/                   (5)
└── sideTable/                  (4)
```

Note: `lab` and `timeMachine` and `toilet` are themselves under `areas` (see [07-major-areas.md](07-major-areas.md)).

---

## Notable patterns

- **Most buildings are EMPTY+MESH composites.** `lab` has 8 empties — these are the prop slot positions. Add `mainTable`, `scroller`, etc., and they parent to those empties.
- **`waterfall` material in `building`** — there's an animated water feature on the main building. Notable shader.
- **`metaball` in cabin** — Bruno uses a metaball (probably for moss growth on the cabin walls). One of only 2 metaballs in the entire world.
- **`mapPortal` + `mapAltar` materials** — the 132/133 EXCLUDED meshes use special materials only the minimap camera renders. This is Bruno's minimap portal-effect trick.
- **`labCarpet` is a section-specific material** — only the lab has this. Branded floor.

---

## Role in Bruno's world

This group splits into **three structural roles**:

### 1. The architectural set pieces (visible buildings)
- **`building` (047)** is the world's centerpiece — a tall structure with a waterfall feature. Likely the dominant silhouette on the island, used as a wayfinding landmark from anywhere.
- **`cabin` (115)** is a smaller wooden structure with metaball-driven moss growth and an emissive orange glow (lantern? fire inside?). Sits inside the `toilet` zone (yes — Bruno's collection naming is deliberately whimsical).
- **`altar` (048)** is a ritual structure with 9 mesh pieces + 6 anchor empties (likely candle/flame positions glowing emissive-orange). A focal point for one of the named zones.
- **`lab` (081)** is the **interior of the lab zone** — 3 meshes (floor/walls/labCarpet) + 8 prop-slot empties that later scripts fill with cauldron, blackboard, scroller, sideTable, mainTable. This is Bruno's pattern: zone-script defines the room, prop-scripts furnish it.

### 2. Zone-anchor containers (no visible geometry, just parents)
- **`behindTheScene` (049)** — 5 empties + child collections `lightGenerators` + `scenery.001`. Hosts an unrendered backstage area.
- **`statue` (105)** — empty parent for `default` (the statue mesh + 3 armatures) and `FWA` (award badges around the statue).
- **`timeMachine` (108)** — 7 empties + 2 small meshes, parents the retro-room interior (`tv`, `playstation`, `stool.001`, `cups`, `archives.004`).
- **`toilet` (114)** — 3 empties + 1 mesh, parents `cabin` + `stool`. Despite the name, it's a small private nook with a cabin inside.
- **`kiosk` (091)** — single empty, the kiosk physical mesh lives in the `landing` zone (script 088).

### 3. Minimap-only stand-ins (excluded from main render)
- **`altar.001` (132)** — single mesh with `mapPortal` material. Only the minimap camera (in `map` collection) renders this. It's the altar's symbol on the minimap.
- **`behindTheScene.001` (133)** — single mesh with `mapAltar` material. Minimap-only stand-in for the behind-the-scene zone.

### Cross-cutting observations
- **Empties drive Bruno's zone architecture.** A zone is "an empty + a bag of child collections parented under it." Moving the empty translates the entire zone. This is why he uses `behindTheScene`, `statue`, `timeMachine`, `toilet`, `lab`, `landing` as parent containers — they're handles for transform groups.
- **Emissive materials anchor the eye.** `building` (blue gradient), `altar` (orange), `cabin` (orange) — each landmark has a distinct emissive accent so players can navigate by glow at distance.
- **Lab is the most populated zone by far.** 11 own objects + 6 child collections (cauldron, scroller, board.001, blackBoard.001, mainTable, sideTable). Suggests lab is one of the longer-engagement zones.

---

## Source pointers

- Step scripts: `folio-2025/scripts/blender_world_steps/steps/047_building.py`, `048_altar.py`, `049_behindTheScene.py`, `081_lab.py`, `091_kiosk.py`, `105_statue.py`, `108_timeMachine.py`, `114_toilet.py`, `115_cabin.py`, `132_altar.001.py`, `133_behindTheScene.001.py`
- Special materials: `waterfall`, `labCarpet`, `mapPortal`, `mapAltar`, `emissiveBlueRadialGradient`, `emissiveOrangeRadialGradient`
- Karan-portfolio sections: `src/Portfolio/` (Billboards, Signs, Interactables — no real buildings yet)
