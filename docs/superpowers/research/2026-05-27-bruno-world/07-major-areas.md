# 07 — Major Gameplay Areas (zone anchors)

**Bruno category:** 🎯 Major Gameplay Areas
**Scripts:** 5 (044, 052, 053, 062, 088)
**Total objects:** 31 (mostly empties — these are anchors, not content)
**Status:** VISIBLE

---

## Purpose

This group is Bruno's **zone-anchor backbone**. None of these scripts add much visible geometry on their own — they create the EMPTY collections + parent containers that all the other section scripts (bowling props, race-track elements, landing pieces, etc.) parent UNDER. Think of these as the "rooms" in the world's hierarchy, with subsequent scripts being the "furniture" in each room.

---

## Scripts

| # | File | Objs | Types | Material | What it adds | Children populated later |
|---:|---|---:|---|---|---|---|
| 044 | `044_areas.py` | 0 | — | — | Top-level `areas` parent collection. Holds 14 child collections (landing, career, social, projects, lab, cookie, altar, toilet + 6 more) | landing, career, social, projects, lab, cookie, altar, toilet, +6 more |
| 052 | `052_bowling.py` | 13 | 8×EMPTY, 5×MESH | `emissiveBlueRadialGradient`, `emissiveOrangeRadialGradient`, `emissiveWhiteRadialGradient`, `palette` | Bowling-alley root — 5 structural meshes (floor, walls?) + 8 prop-slot empties. 1 NODES modifier (Smooth by Angle.003). 1,058 verts | pins (057), screen (059), bumpers (054), sign (060), furnitures (055), jukebox (056), pinsPosition (058), alley (053) |
| 053 | `053_alley.py` | 0 | — | — | Empty collection. Contains no children. Probably reserved for runtime-spawned alley elements (the actual lane?) | — |
| 062 | `062_circuit.py` | 5 | 5×EMPTY | — | Race-circuit root — 5 anchor empties. Parents 16 child collections | checkpoints, cones, barrels, startingLights, timer, road, zigzag, obstacles, +8 more (jump, rails, podium, banners, scenery, leaderboard, leaderboardReset, sign) |
| 088 | `088_landing.py` | 13 | 11×EMPTY, 2×MESH | `palette`, `stylizedMap` | Landing-zone root — the spawn area / hub. 2 meshes (probably the stylized-map terrain + a kiosk pedestal) + 11 prop-slot empties. Parents 4 child collections | title.001 (092), controls (090), kiosk (091), bonfire (089) |

---

## The zone-anchor pattern (Bruno's core architecture)

Bruno organizes his world hierarchy like this:

```
Scene
├── terrain                      (the canvas)
├── grass                        (the carpet)
├── scenery.002                  (surface detail container)
├── trees container collections
├── bushes, flowers              (density layer)
├── fences, bricks               (zone borders / paving)
└── areas/                       ← THIS GROUP'S parent
    ├── landing/                 (088 — spawn zone)
    │   ├── title.001            (092 — welcome title)
    │   ├── controls             (090 — controls display)
    │   ├── kiosk                (091 — kiosk structure)
    │   └── bonfire              (089 — campfire)
    ├── career/                  (061 — career timeline)
    ├── social/                  (103 — social-icons section)
    │   ├── icons                (104)
    │   └── statue               (105 + 106 default + 107 FWA)
    ├── projects/                (093 — projects section)
    │   ├── board, pole, distinctions, mainTable.001,
    │   │   oven, anvil, grinder, quench, blackBoard.002
    │   └── (workshop tools — the projects zone is a forge)
    ├── lab/                     (081 — lab zone)
    │   └── mainTable, scroller, board.001,
    │       blackBoard.001, cauldron, sideTable
    ├── cookie/                  (079 — interactive cookie sequence)
    ├── altar/                   (048 — ritual altar)
    ├── toilet/                  (114 — small private nook)
    │   ├── cabin                (115)
    │   └── stool                (116)
    ├── bowling/                 (052 — bowling alley)
    │   └── pins, screen, bumpers, sign, furnitures,
    │       jukebox, pinsPosition, alley
    ├── circuit/                 (062 — race track)
    │   └── 16 race-track sub-collections
    └── 4 more area children
```

**Takeaway:** `areas/` is the umbrella holding all 14 gameplay zones. Each zone is its own collection whose ROOT script (this group) creates the anchors + skeleton, and whose ROOT-script's "children populated later" notes point at the prop-scripts that furnish it.

---

## Why this matters for the world's feel

- **Spatial separation by container.** Each zone has its OWN root empty, so the player can "leave" one zone and "enter" another even though the terrain is continuous. The collection hierarchy mirrors the player's mental model.
- **Bowling root has 5 meshes** — the alley structure (walls, floor) is here, but the pins, jukebox, sign, etc. live in their own collections so they can be hidden/shown/recolored independently.
- **Race circuit root has ZERO meshes** — circuit (062) is purely a parent anchor; ALL geometry lives in the 16 child collections (cones, barrels, checkpoints, etc.). Each of those is a separately-toggleable prop type.
- **Landing has the `stylizedMap` material** — there's a small flat-map terrain at the landing zone (probably the kiosk's display showing the world layout). This is one of Bruno's few branded materials outside of advertising.
- **`alley` (053) is empty** — the alley lane itself is probably runtime-generated (lane planks placed dynamically) or part of the bowling root's 5 meshes.

---

## The 14 "areas" children (from 044's hint)

The full list of zones under `areas/`: landing, career, social, projects, lab, cookie, altar, toilet, + 6 more (likely: behindTheScene, bowling, circuit, statue, timeMachine, easter or similar). Each is documented in its own file in this analysis.

---

## Source pointers

- Step scripts: `folio-2025/scripts/blender_world_steps/steps/044_areas.py`, `052_bowling.py`, `053_alley.py`, `062_circuit.py`, `088_landing.py`
- Special materials: `emissiveBlueRadialGradient`, `emissiveOrangeRadialGradient`, `emissiveWhiteRadialGradient`, `stylizedMap`
- Bruno's runtime zone-management logic: `folio-2025/sources/Game/` (likely in `Areas/` or `World/`)
