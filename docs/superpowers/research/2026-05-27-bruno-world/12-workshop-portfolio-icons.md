# 12 — Workshop Tools + Portfolio Sections + Icons

**Bruno categories:** 🔨 Workshop / Tools + 🏆 Portfolio & Icons
**Scripts:** 11 (045, 061, 084, 093, 094, 097, 098, 100, 102, 103, 104)
**Total objects:** 144 (24 workshop + 120 portfolio/icons)
**Status:** all VISIBLE

---

## Purpose

This is where Bruno's **actual portfolio content lives**:
- **Portfolio sections** — `career` (work timeline), `projects` (built things, themed as a forge/workshop), `social` (social-icons hub), `achievements`, `distinctions`, `icons` (interactable category markers).
- **Workshop tools** — anvil, oven, cauldron, grinder, quench. These are the forge's working tools, all parented under `projects` (because projects IS a workshop in Bruno's metaphor).

The combination matters because **Bruno frames "projects" as a forge**: anvil + grinder + oven + cauldron + quench are the verbs (build, refine, heat, mix, cool) for project-making.

---

## Scripts — Portfolio Sections (6)

| # | File | Objs | Types | Materials | What it adds |
|---:|---|---:|---|---|---|
| 045 | `045_achievements.py` | 23 | 22×EMPTY, 1×MESH | — | 23 achievement anchors (22 empties + 1 mesh). Custom prop `category`. Parents `archive.001`, `building` |
| 061 | `061_career.py` | 32 | 22×MESH, 10×EMPTY | `careerTextFreelancer`, `careerTextHetic`, `careerTextIRLTeacher`, `careerTextImmersive`, `careerTextOnlineTeacher`, `careerTextUzik`, `emissiveBlueRadialGradient`, `emissiveOrangeRadialGradient`, + 3 more | The career timeline — 22 meshes showing Bruno's work history (Freelancer, Hetic, IRL Teacher, Immersive Garden, Online Teacher, Uzik). Custom props: `color`, `hasEnd`, `size`, `texture` |
| 093 | `093_projects.py` | 9 | 8×EMPTY, 1×MESH | `palette` | The projects-zone root — 8 prop-slot empties + 1 mesh. Parents 9 child collections (workshop tools) |
| 097 | `097_distinctions.py` | 8 | 7×MESH, 1×EMPTY | `palette`, `projectsLabels` | 7 distinction/award meshes — branded with `projectsLabels` material. Inside `projects` (093) |
| 103 | `103_social.py` | 15 | 13×EMPTY, 2×MESH | `darkGray`, `palette` | The social-section root — 13 anchor empties + 2 meshes (likely the kiosk + base). Parents `icons` + `statue` |
| 104 | `104_icons.py` | 23 | 13×EMPTY, 10×MESH | `palette` | The social icons — 10 unique icon meshes + 13 placement empties. 6 NODES modifiers (Auto Smooth, Smooth by Angle variants). preventAutoAdd (runtime-managed visibility) |

## Scripts — Workshop Tools (5) — all parented under projects (093)

| # | File | Objs | Types | Materials | What it adds |
|---:|---|---:|---|---|---|
| 084 | `084_cauldron.py` | 5 | 3×MESH, 2×EMPTY | `emissiveOrangeRadialGradient`, `palette` | Cauldron with glowing-orange contents — 2 NODES modifiers. Inside lab (NOT projects — lab has its own cauldron) |
| 094 | `094_anvil.py` | 5 | 3×MESH, 2×EMPTY | `palette` | Anvil for hammering projects — 3 meshes (anvil top, base, surrounding tools?) |
| 098 | `098_grinder.py` | 5 | 3×EMPTY, 2×MESH | `palette` | Grinder — 2 meshes + 3 empties (probably the grinding wheel + base + shavings spawn) |
| 100 | `100_oven.py` | 9 | 5×MESH, 4×EMPTY | `emissiveOrangeRadialGradient`, `palette` | Oven with glowing interior — 5 meshes + 4 anchor empties |
| 102 | `102_quench.py` | 2 | 1×MESH, 1×EMPTY | `palette` | Quench water bucket — 1 mesh + 1 anchor |

---

## How Bruno's portfolio content interlocks

```
areas/
├── career/                        (061 — 22 meshes, branded text per role)
│   └── Custom props: color, hasEnd, size, texture
│       — each timeline entry has its own visual config
├── projects/                      (093 — empty parent with 8 slot empties)
│   ├── board (096, see file 11)   ← 19 project-display meshes (THE main projects board)
│   ├── pole (101, see file 13)    ← signage pole
│   ├── distinctions (097)         ← 7 award meshes
│   ├── mainTable.001 (099, see file 11)  ← workspace
│   ├── blackBoard.002 (095, see file 11) ← chalkboard
│   ├── anvil (094)                ← forge tools
│   ├── grinder (098)              ← forge tools
│   ├── oven (100)                 ← forge tools
│   └── quench (102)               ← forge tools
└── social/                        (103 — empty parent with 13 slot empties)
    ├── icons (104)                ← 23 social-icon objects
    └── statue (105)               ← parent for default + FWA
        ├── default (106)          ← statue mesh + 3 armatures
        └── FWA (107)              ← FWA award badges

achievements/                       (045 — 23 anchors, not under areas)
                                    parents archive.001 + building
```

**Two cauldrons** — `084_cauldron` is in lab (alchemy theme), and lab is a separate zone from projects/forge. Bruno reuses the cauldron mesh + material in two contexts.

---

## Why this design works for Bruno

### Career section (061)
- **Each role has its own branded text material** (`careerText*`) — 6 jobs = 6 textures. Logos baked-in.
- **Custom props (color, hasEnd, size, texture)** drive per-entry visual variation — same mesh template, different look per entry.
- **`hasEnd` boolean** tells the timeline renderer if this job has ended or is current.
- **Mixed blue + orange emissives** suggests current jobs glow blue, ended jobs glow orange (or similar contrast).

### Projects section as a forge
- **Bruno's metaphor: building projects = blacksmithing.** The projects zone has anvil + grinder + oven + cauldron + quench — the verbs of metalwork. This is a **narrative reframe** of "look at my projects" into "watch me make things."
- **The 19-mesh `board` (096, see file 11) is the gallery.** 19 project slots, each a visible mesh.
- **`projectsLabels` material** brands the distinctions/award meshes with project names.
- **`projectsCarpet`** flooring under the workshop tools (see file 11's mainTable.001).

### Social section
- **Statue centerpiece** (105+106+107) — a rigged character (3 armatures) holding FWA badges. The statue is Bruno's avatar showing off his achievements.
- **23 icons (104)** — likely social platform logos (Twitter/X, GitHub, LinkedIn, Mastodon, BlueSky, etc.). The empties are placement slots.
- **preventAutoAdd on icons** means runtime decides which icons to show (perhaps based on Bruno's currently-active platforms).

### Achievements (045)
- **23 achievement anchors, parented OUTSIDE `areas/`** — these are scattered across the whole world, not contained in one zone. Custom prop `category` groups them (collectibles? milestones?).
- Parents `archive.001` (a curve) and `building` (the centerpiece) — suggesting the building IS an achievement-related landmark.

---

## Cross-references

- **The projects zone is BIG.** It pulls in 9 child collections + uses the largest non-foundation script (`096_board` at 38 objects). See [11-furniture-displays-boards.md](11-furniture-displays-boards.md) for the boards and tables that fill out the workshop.
- **Social statue:** see [14-reference-hidden.md](14-reference-hidden.md) for the `default` (statue mesh + 3 armatures) breakdown.
- **Branded textures** (`careerText*`, `projectsLabels`, `projectsCarpet`): all loaded in foundation script 002, materials defined in 004.

---

## Source pointers

- Step scripts: `folio-2025/scripts/blender_world_steps/steps/045_achievements.py`, `061_career.py`, `084_cauldron.py`, `093_projects.py`, `094_anvil.py`, `097_distinctions.py`, `098_grinder.py`, `100_oven.py`, `102_quench.py`, `103_social.py`, `104_icons.py`
- Career textures (in 002): `careerFreelancer.png`, `careerHetic.png`, `careerIRLTeacher.png`, `careerImmersiveGarden.png`, `careerOnlineTeacher.png`, `careerUzik.png`
- Materials (in 004): `careerText*` family, `projectsLabels`, `projectsCarpet`, `emissiveBlueRadialGradient`, `emissiveOrangeRadialGradient`
