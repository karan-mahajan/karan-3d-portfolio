# 11 — Furniture, Displays & Boards

**Bruno categories:** 🪑 Furniture & Seating + 📺 Displays & Screens + 📝 Boards & Signage
**Scripts:** 16 (064, 072, 082, 083, 085, 086, 087, 090, 095, 096, 099, 111, 112, 113, 116, 119)
**Total objects:** 153
**Status:** all VISIBLE

---

## Purpose

The **interior contents** of zones. Tables, stools, benches (seating), TVs, scroller displays, controls panels (interactive screens), blackboards, signage boards, podiums, banners (information / decoration). These don't belong to the open world — they live INSIDE specific zones (lab, projects, time-machine, race podium area).

---

## Scripts — Furniture & Seating (6)

| # | File | Objs | Types | Material | Where it sits |
|---:|---|---:|---|---|---|
| 085 | `085_mainTable.py` | 6 | 4×MESH, 2×EMPTY | `emissiveOrangeRadialGradient`, `palette` | Inside lab (081) — the main lab work table |
| 087 | `087_sideTable.py` | 4 | 2×EMPTY, 2×MESH | `emissiveOrangeRadialGradient`, `palette` | Inside lab (081) — a smaller side table |
| 099 | `099_mainTable.001.py` | 4 | 2×MESH, 2×EMPTY | `palette`, `projectsCarpet` | Inside projects (093) — the projects-section main table, with branded carpet |
| 112 | `112_stool.001.py` | 2 | 1×MESH, 1×EMPTY | `palette` | Inside timeMachine (108) — a stool in the retro room |
| 116 | `116_stool.py` | 8 | 4×MESH, 4×EMPTY | `palette` | Inside toilet (114) — 4 stools (??), `mass`-tagged (pushable) |
| 119 | `119_benches.py` | 21 | 14×EMPTY, 7×MESH | `palette` | World-scattered benches — 7 unique meshes, 14 placement empties. Seating along paths / at scenic viewpoints |

## Scripts — Displays & Screens (4)

| # | File | Objs | Types | Material | What it adds |
|---:|---|---:|---|---|---|
| 086 | `086_scroller.py` | 14 | 11×MESH, 3×EMPTY | `palette` | A scrolling text/info display inside lab. 3 ARRAY modifiers (text-tile repetition) |
| 090 | `090_controls.py` | 14 | 7×MESH, 7×EMPTY | `emissiveOrangeRadialGradient`, `palette` | An interactive controls panel at landing. 3 NODES modifiers |
| 111 | `111_playstation.py` | 4 | 4×MESH | `emissiveGreenRadialGradient`, `palette` | A PlayStation console (retro!) — 2 NODES + 1 MIRROR modifier. Inside timeMachine (108) |
| 113 | `113_tv.py` | 6 | 3×MESH, 3×EMPTY | `emissiveOrangeRadialGradient`, `palette` | A TV — 1 NODES modifier. Inside timeMachine (108) |

## Scripts — Boards & Signage (6)

| # | File | Objs | Types | Materials | What it adds |
|---:|---|---:|---|---|---|
| 064 | `064_banners.py` | 2 | 2×MESH | `circuitBrand` | 2 branded banners at the race circuit |
| 072 | `072_podium.py` | 7 | 6×EMPTY, 1×MESH | `circuitThreejs`, `circuitWebgl`, `circuitWebgpu`, `palette` | The race podium — 1 mesh + 6 anchor empties for award positions. Branded with circuit tech-stack mats |
| 082 | `082_blackBoard.001.py` | 8 | 4×EMPTY, 4×MESH | `blackboardLabels`, `palette` | Lab's blackboard — 4 meshes + 4 label anchors |
| 083 | `083_board.001.py` | 14 | 8×MESH, 6×EMPTY | `palette` | Lab's secondary board — 8 meshes + 6 empties. preventFrustum (always rendered) |
| 095 | `095_blackBoard.002.py` | 8 | 4×EMPTY, 4×MESH | `blackboardLabels`, `palette` | Projects-section blackboard (matches 082 in structure) |
| 096 | `096_board.py` | 38 | 19×MESH, 19×EMPTY | `palette` | Projects-section main board — 19 meshes + 19 empties. The biggest board in the world — possibly the project-cards display |

---

## How these interlock with zone roots

```
lab (081)
  ├── mainTable (085)        ← main work surface
  ├── sideTable (087)        ← secondary
  ├── scroller (086)         ← scrolling text display
  ├── blackBoard.001 (082)   ← chalkboard
  ├── board.001 (083)        ← cork/info board
  ├── cauldron (084)         ← see workshop file
  └── (mainTable.001 (099) parented to PROJECTS, not lab — there's a name clash)

projects (093)
  ├── mainTable.001 (099)    ← projects work table
  ├── board (096)            ← THE big projects board (19 meshes)
  ├── blackBoard.002 (095)   ← chalkboard for projects
  ├── pole, distinctions, oven, anvil, grinder, quench, blackBoard.002
  └── (projects is structured like a workshop — see [12-workshop-portfolio-icons.md])

timeMachine (108)
  ├── tv (113)               ← retro television
  ├── playstation (111)      ← PS console
  ├── stool.001 (112)
  ├── cups (110)             ← see food/misc file
  └── archives.004 (109)

toilet (114)
  ├── cabin (115)
  └── stool (116)            ← 4 stools, pushable

circuit (062) — race track
  ├── banners (064)          ← branded race-track banners
  ├── podium (072)           ← winner's podium
  └── (16 other race-track collections)

landing (088)
  └── controls (090)         ← interactive controls panel for the player
```

**`benches (119)` is the only outlier** — 21 benches scattered world-wide along paths/scenic spots, not inside any zone. They're public seating.

---

## Why this design works for Bruno

- **Furniture is `palette`-only except where it needs an emissive glow.** Tables (085, 087, 099) use the orange emissive on their lamps / surface highlights. Stools (116, 112) are plain palette.
- **Boards drive narrative density.** Lab has 2 boards (082 + 083). Projects has 2 boards (095 + 096). That's where Bruno places branded portfolio content (project thumbnails, achievement notes, blackboard equations).
- **`board (096)` is the biggest** at 19 meshes — probably the main projects-card grid players read. The 19 empties are likely individual project-slot positions.
- **Scrolling text uses ARRAY modifier** (3 in `086_scroller`) — tile-and-shift to create the scrolling effect. Pure modifier trick.
- **Race podium has 6 empties for 6 award positions** — supports a real race-result display. Custom mats `circuitThreejs`/`circuitWebgl`/`circuitWebgpu` brand each podium with the tech the race winner used.
- **Controls panel (090) at landing is interactive** — emissive-orange highlights on the panel surfaces, sits next to the kiosk. First-touch tutorial UI.
- **`stool` (116) has 4 pushable stools in the toilet zone** — Bruno's whimsy. A toilet area with pushable stools is its own visual joke.
- **`mainTable` name clash:** Bruno has both `mainTable` (085, in lab) and `mainTable.001` (099, in projects). Same concept, different zone — Blender's `.001` suffix convention.
- **`benches (119)` placed world-wide** = Bruno wants players to be ABLE to rest visually. The fact that there are 21 of them (more than any single section's furniture count) shows benches are part of world ambient, not zone furniture.

---

## Materials worth knowing

- **`palette`** — used on everything's body
- **`emissiveOrangeRadialGradient`** — table lamps, TV screen glow, controls panel highlights
- **`emissiveGreenRadialGradient`** — playstation power LED (specific arcade-green)
- **`blackboardLabels`** — texture atlas for chalkboard writing (used by both blackboards)
- **`circuitBrand`/`circuitThreejs`/`circuitWebgl`/`circuitWebgpu`** — race-podium and banner branding for Bruno's tech stack
- **`projectsCarpet`** — flooring under the projects-section's main table

---

## Source pointers

- Step scripts: 16 files (see Scripts tables above)
- Geometry-nodes used: `Smooth by Angle.001`, `Smooth by Angle.002`, `Smooth by Angle.003`, `Smooth by Angle` (cups uses base variant)
- ARRAY modifier: `086_scroller.py` (3 of them)
- MIRROR modifier: `111_playstation.py`, `087_sideTable.py`
