# 08 — Race Track Gameplay

**Bruno category:** 🏁 Race Track Gameplay
**Scripts:** 14 (065, 066, 067, 068, 071, 073, 074, 076, 077, 078, 120, 122, 123, 137)
**Total objects:** 188 (very dense — full racing-game world)
**Status:** mostly VISIBLE; `vehicle.001` (137) EXCLUDED (template car)

---

## Purpose

A complete racing-game zone with drivable vehicle, full obstacle course, checkpoints, timer, podium, and respawn system. This is the most gameplay-rich zone in Bruno's world — it's essentially **a tiny racing game embedded inside the portfolio**. The race track is parented under `circuit` (062, see [07-major-areas.md](07-major-areas.md)).

---

## Scripts

| # | File | Objs | Types | Materials | What it adds | Notes |
|---:|---|---:|---|---|---|---|
| 065 | `065_barrels.py` | 16 | 8×MESH, 8×EMPTY | `palette` | 8 visible barrels + 8 anchor empties. 8 NODES modifiers (Smooth by Angle.003). Custom prop `mass` (physics interactable — pushable barrels) | Roll when hit |
| 066 | `066_checkpoints.py` | 8 | 8×MESH | — | 8 checkpoint volumes (32 verts, 8 polys — flat trigger planes). Custom prop `preventFrustum` (always rendered, even off-screen, for gameplay reliability) | Lap detection |
| 067 | `067_cones.py` | 21 | 14×EMPTY, 7×MESH | `palette` | 7 unique cone meshes + 14 placement empties. 7 NODES modifiers. Custom prop `mass` (knockable) | Track edges |
| 068 | `068_jump.py` | 3 | 2×EMPTY, 1×MESH | `palette` | A jump ramp (1 mesh) + 2 takeoff/landing anchors | Aerial section |
| 071 | `071_obstacles.py` | 11 | 6×EMPTY, 5×MESH | `palette` | 5 obstacle meshes + 6 placement empties. 5 BEVEL modifiers. Custom prop `restitution` (bouncy collisions) | Mid-track hazards |
| 073 | `073_rails.py` | 8 | 5×MESH, 3×CURVE | `gray`, `palette` | Track-edge railings — 3 bezier curves + 5 meshes. 2 NODES modifiers (`Geometry Nodes.002` = rails-along-curve generator) | Bumpers along the track |
| 074 | `074_road.py` | 14 | 14×EMPTY | — | 14 anchor empties only — the race track's road centerline. The visible road surface is on the terrain itself (R-channel of `terrainData`), these empties mark path waypoints for game logic | AI/path markers |
| 076 | `076_startingLights.py` | 1 | 1×MESH | `emissiveGreenRadialGradient` | The starting-line light tree (Christmas-tree style green/red signal). preventFrustum | Race start signal |
| 077 | `077_timer.py` | 2 | 1×EMPTY, 1×MESH | `palette` | Timer display — 1 mesh (the panel) + 1 empty (mounting anchor). 1 NODES modifier. preventFrustum | Lap time display |
| 078 | `078_zigzag.py` | 10 | 9×EMPTY, 1×MESH | `palette` | A zigzag chicane section — 1 mesh + 9 anchor empties along the zigzag. Custom prop `restitution` | Slalom section |
| 120 | `120_explosiveCrates.py` | 23 | 23×MESH | `palette` | 23 explosive crates scattered on the track. Parents `fwa` (121) collection | Hit to explode (`fwa` likely the badges revealed by destroying crates) |
| 122 | `122_respawns.py` | 17 | 17×EMPTY | — | 17 respawn anchor empties along the track. Each is a "if you fall off, come back here" point | Safety net |
| 123 | `123_vehicle.py` | 0 | — | — | Empty parent — holds 3 vehicle child collections | antenna.001, oldSchool, default.001 |
| 137 | `137_vehicle.001.py` | 41 | 29×MESH, 12×EMPTY | `darkGray`, `emissiveOrangeRadialGradient`, `emissivePurpleRadialGradient`, `palette`, `redGradient` | EXCLUDED template vehicle — 29 meshes (body, wheels, lights, antenna, etc.) + 12 anchor empties. Custom prop `booleans` (probably modifier-state flags) | Source template; runtime instantiates from this |

---

## How the race track is composed

**Track surface:** the road is not a separate mesh — it's painted into the terrain's `terrainData` R channel. The 14 empties in `074_road.py` only mark waypoints for game logic (AI driving, path-following, distance-along-track calculations).

**Track edges:** `073_rails.py` uses 3 curves driven through `Geometry Nodes.002` to extrude rail meshes along the curves. The 5 visible meshes are baked rail segments at intersections.

**Race props (physics interactable):**
- `barrels` (16) — mass-tagged, roll when hit
- `cones` (21) — mass-tagged, knockable
- `obstacles` (11) — restitution-tagged, bouncy hazards
- `zigzag` (10) — restitution-tagged, slalom obstacles
- `explosiveCrates` (23) — destructible, contain FWA badges

**Race UI/game-logic objects:**
- `checkpoints` (8) — flat trigger planes, preventFrustum so frustum culling doesn't disable them when player is on the other side of the track
- `startingLights` (1) — emissive green/red signal tree, preventFrustum
- `timer` (2) — display panel, preventFrustum
- `respawns` (17) — anchor empties for "where to drop the car after a crash"
- `road` (074) — 14 path-waypoint empties

**The vehicle itself:** 41 objects across `137_vehicle.001.py` (EXCLUDED template) — body, wheels, lights, antenna, exhaust glow. The visible runtime vehicle is instantiated from this template at runtime; the .blend version is hidden.

---

## Why this design works for Bruno

- **The race track is the most gameplay-engaging zone.** All those mass/restitution custom props + 8 checkpoints + 17 respawns mean the player can actually drive laps, hit things, and recover from crashes. It's a real mini-game, not a decoration.
- **`preventFrustum` on checkpoints/timer/startingLights** keeps gameplay-critical objects always active even when off-screen — the timer must run, the lights must signal, regardless of camera angle.
- **Separation of road surface (terrain PNG) from road waypoints (empties)** means Bruno can re-paint the track on terrain WITHOUT touching the 14 waypoint empties. The two systems are decoupled.
- **Heavy use of "anchor empties + few visible meshes" pattern.** 14 cones placed but only 7 unique cone meshes. 8 barrels placed but only 8 unique meshes (1:1 here but each could have been reused). Saves mesh data, allows easy re-placement.
- **`circuitBrand`/`circuitWebgl`/`circuitWebgpu`/`circuitThreejs` materials** (used by `075_scenery.py` and `072_podium.py`) brand the race-track scenery with Bruno's tech-stack signatures. The race track is also self-aware portfolio content — it advertises Bruno's own work.
- **Explosive crates + FWA badges** turn destruction into reward — destroying the 23 crates reveals the 6 FWA badges (script 121). The race track is also where Bruno shows off his award history.

---

## Source pointers

- Step scripts: 14 files in `folio-2025/scripts/blender_world_steps/steps/` — `065_barrels.py`, `066_checkpoints.py`, `067_cones.py`, `068_jump.py`, `071_obstacles.py`, `073_rails.py`, `074_road.py`, `076_startingLights.py`, `077_timer.py`, `078_zigzag.py`, `120_explosiveCrates.py`, `122_respawns.py`, `123_vehicle.py`, `137_vehicle.001.py`
- Geometry-nodes used: `Geometry Nodes.002` (rails-along-curve), `Smooth by Angle.003` (cones, barrels)
- Materials: `gray`, `palette`, `emissiveGreenRadialGradient`, `darkGray`, `emissiveOrangeRadialGradient`, `emissivePurpleRadialGradient`, `redGradient`
- Related: `072_podium.py` (podium for race winners — covered in [11-furniture-displays-boards.md](11-furniture-displays-boards.md)), `075_scenery.py` (race-track branded billboards — covered in [03-surface-detail.md](03-surface-detail.md))
- Bruno's runtime racing code: `folio-2025/sources/Game/` (likely in `Vehicle/`, `Race/` or similar)
