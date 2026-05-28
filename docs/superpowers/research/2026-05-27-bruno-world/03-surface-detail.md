# 03 — Surface Detail (rocks, roads, bridges, slabs, scenery)

**Bruno category:** 🪨 Surface Detail
**Scripts:** 8 (022, 023, 024, 025, 026, 027, 051, 075)
**Total objects:** 92 (across all 8)
**Status:** VISIBLE

---

## Purpose

The hard things that sit ON TOP of the terrain. Rocks (regular + basalt), bridges spanning waterways, the main road network, the cobblestone slab paths, and two scenery sub-collections (`scenery.001` for behind-the-scene props, `scenery.py` for the race-circuit corner). These are not gameplay zones — they're decoration + traversal surfaces.

---

## Scripts

| # | File | Objs | Types | Material | What it adds | Children |
|---:|---|---:|---|---|---|---|
| 022 | `022_scenery.002.py` | 0 | — | — | Empty parent collection. Holds `bridges`, `rocks`, `basaltRocks`, `slabs`, `road.001` as child collections | bridges, rocks, basaltRocks, slabs, road.001 |
| 023 | `023_basaltRocks.py` | 13 | 13×MESH | `palette` | 13 dark hexagonal-column rock formations. ~781 verts · 595 polys total | — |
| 024 | `024_bridges.py` | 8 | 6×EMPTY, 2×MESH | `palette` | 2 visible bridge meshes + 6 anchor empties (probably bridge endpoint markers for game logic) | — |
| 025 | `025_road.001.py` | 14 | 13×MESH, 1×CURVE | `black`, `palette` | The main road network: 13 mesh segments + 1 bezier curve (probably the spline the segments follow) | — |
| 026 | `026_rocks.py` | 1 | 1×MESH | `palette` | A single large rock mesh (696 verts) | — |
| 027 | `027_slabs.py` | 3 | 3×MESH | `palette` | The 3 cobblestone slab paths — modifier: `Smooth by Angle.003`. (Karan-portfolio's slabs.py mirrors this — we have cobble slabs along cardinal paths) | — |
| 051 | `051_scenery.001.py` | 8 | 5×EMPTY, 3×MESH | `palette` | Misc scenery props in the behind-the-scene corner — 3 NODES modifiers, custom prop `mass` (interactable) | — |
| 075 | `075_scenery.py` | 43 | 33×EMPTY, 10×MESH | `circuitBrand`, `circuitWebgl`, `circuitWebgpu`, `palette` | The race-circuit's decorative scenery (33 anchor empties + 10 meshes incl. branded signs) — 4 NODES + 3 BEVEL modifiers | — |

---

## Relationships

- **`scenery.002`** is a "container" — its 5 children are the surface-detail collections. Likely parented under the world root, not under any gameplay area.
- **`slabs`** + **`road.001`** + **`bridges`** form the traversal network. Together they define where the player CAN walk vs. just terrain.
- **`scenery.001`** (script 051) is under `behindTheScene` (script 049) — see [06-buildings-structures.md](06-buildings-structures.md).
- **`scenery`** (script 075) is under `circuit` (script 062) — see [08-race-track.md](08-race-track.md).

---

## Notable patterns

- **Bridges = 2 mesh + 6 empty.** The 6 empties are probably bridge-foot/keystone positions. Custom-prop bridges in karan-portfolio's `Paths.js` follow a similar empty-anchor pattern.
- **`road.001` uses 1 CURVE + 13 MESH.** The curve is likely the centerline; meshes are pre-decimated segments along it. Could also be that the curve drives the meshes via geometry nodes.
- **`slabs` has Smooth-by-Angle.003** — softens the cobblestone normals so each tile reads as round-corner rather than sharp.
- **Two `scenery.*` collections are stowed under DIFFERENT gameplay parents** — `scenery.001` is behindTheScene's, `scenery` (no suffix) is circuit's. Bruno separates per-section scenery from world-level rocks.

---

## Role in Bruno's world

These 8 scripts together form Bruno's **traversal + decoration layer** sitting on top of the terrain canvas:

- **Slabs (027) + road (025) + bridges (024) define the player's path network.** The terrain says "where can you walk geographically"; this group says "where is the FORMAL walking surface." Cobblestone slabs mark the main paths; the road is a curved meander; bridges cross water bodies (terrainData B-channel depressions).
- **Rocks (026) + basaltRocks (023) are the "hardscape" Bruno scatters across the open terrain** — visual landmarks that aren't bushes or trees. Basalt's hexagonal-column shape gives it a distinct geological character (volcanic), used in specific corners (likely behind-the-scene area or near water).
- **`scenery.002` (022)** is the **container parent** for everything in this group — bridges, rocks, basaltRocks, slabs, road.001 all sit underneath it in the collection tree. Moving `scenery.002` moves the entire surface-detail layer.
- **`scenery.001` (051)** is the **behindTheScene section's local props** — 8 mass-tagged objects (interactable), parented under `behindTheScene` (049). These are inside-the-zone decoration.
- **`scenery` (075)** is the **race-circuit's branded scenery** — 43 objects including circuit-branded signs (`circuitBrand`, `circuitWebgl`, `circuitWebgpu` materials). Parented under `circuit` (062). This is the race track's billboards/advertising.
- **Geographic layering:** the world goes terrain → grass scatter → this surface-detail layer → trees → bushes/flowers → fences/bricks → buildings → in-section props. Surface detail is layer 3.
- **No single material switch tells you "this is hardscape."** Bruno reuses `palette` for almost everything; the visual distinction between rock, slab, road, and bridge comes from per-vertex coloring + the geometry-nodes smoothing settings.

---

## Source pointers

- Step scripts: `folio-2025/scripts/blender_world_steps/steps/022_scenery.002.py` through `027_slabs.py`, plus `051_scenery.001.py` and `075_scenery.py`
- Materials (in 004): `palette`, `black`, `circuitBrand`, `circuitWebgl`, `circuitWebgpu`
- Geometry-nodes used: `Smooth by Angle.003`
