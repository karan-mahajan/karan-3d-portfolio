# 05 — Foliage, Flowers, Fences, Brick Paving

**Bruno categories:** 🌿 Foliage & Flowers + 🧱 Boundaries & Paving
**Scripts:** 4 (040, 041, 042, 043)
**Total objects:** 300 (130 bushes + 108 flowers + 32 fences + 30 bricks)
**Status:** all VISIBLE

---

## Purpose

The "carpet" of small props that gives the world its density — bushes scattered across grass areas, flowers in clusters, fences enclosing zones, brick tiles paving certain sections. None of these are gameplay-interactive; they're pure visual density.

---

## Scripts

| # | File | Objs | Types | Material | Geometry | What it adds |
|---:|---|---:|---|---|---|---|
| 040 | `040_bushes.py` | 130 | 130×MESH | `palette` | 1,560 verts · 2,600 polys total (12 verts · 20 polys per bush avg) | 130 small bush meshes. Per memory `reference-bruno-bushes-are-sdf`, at runtime Bruno routes these as anchor points to his `Foliage.js` SDF cloud system — yellow-green palette `#b4b536`/`#d8cf3b` |
| 041 | `041_flowers.py` | 108 | 108×MESH | `palette` | 972 verts · 432 polys total (9 verts · 4 polys per flower) | 108 flower meshes. Very lightweight per-flower geometry — Bruno keeps them simple |
| 042 | `042_fences.py` | 32 | 32×MESH | `palette` | 640 verts · 480 polys (20 verts · 15 polys per fence) | 32 fence-segment meshes. Likely hand-placed to enclose specific areas (race track, bowling, lab edges) |
| 043 | `043_bricks.py` | 30 | 30×MESH | `palette` | 1,680 verts · 1,620 polys (56 verts · 54 polys per brick) | 30 brick-tile meshes — probably paving accents inside specific areas (forge, lab) |

---

## Relationships

- All 4 collections are top-level (not nested under any area). They scatter ACROSS the world rather than belonging to one section.
- Likely sit alongside `trees` in the visual hierarchy.
- Fences and bricks are probably parented under SPECIFIC area roots in `999_finalize.py` (so moving the area also moves the enclosing fence).

---

## Notable patterns

- **Bushes are mesh anchors, not visible meshes at runtime.** Per memory `reference-bruno-bushes-are-sdf`: Bruno's runtime routes the bush positions to `Foliage.js`, which renders SDF-alpha foliage clouds. The .blend mesh is just the anchor.
- **130 bushes is a lot of density.** Karan-portfolio is targeting Bruno-level density per memory `project-world-vision-bruno-density`.
- **Flower count > fence count.** Bushes + flowers (238) outnumber path/structural props (62 = 32 + 30). Density skew toward soft greenery.
- **All four use `palette` material.** No special-case mats. Visual variety from vertex colors only.
- **Fences are LOAD-BEARING for atmosphere.** 32 short fence segments break up sight lines — they're how Bruno makes the world feel "enclosed" without walls.

---

## Role in Bruno's world

These 4 scripts deliver the **density layer** that makes Bruno's world read as "full" instead of "empty island with props":

- **Bushes (130) + flowers (108) = 238 small-prop instances** scattered across the grass-meadow zones. They fill the visual gap between trees (sparse landmarks) and grass blades (microscopic). Without this layer, the meadow looks like an empty lawn between trees.
- **Bushes are SDF foliage anchors at runtime, not solid meshes.** Per memory `reference-bruno-bushes-are-sdf`, Bruno's `Foliage.js` consumes the 130 anchor positions and renders SDF-alpha leaf clouds — same system that draws tree canopies. The .blend mesh is placeholder for authoring; runtime swaps it.
- **Flowers ARE solid meshes** — 4 polys each, plus vertex color. They render as-is.
- **Fences (32 segments) act as soft zone-borders.** They aren't load-bearing geometry the player collides with — they're visual barriers that tell the player "this area is separate." Likely placed around the race-track perimeter, lab edges, the landing zone, and bowling alley boundaries.
- **Bricks (30 tiles) are paving accents inside specific zones.** Forge and lab probably have brick floors visible through grass; the cookie/landing area might use brick borders. They give "indoor" zones a different floor texture than grass.
- **All four groups use the `palette` material exclusively** — Bruno's density layer has zero unique materials. Visual variation is 100% vertex color. This is what makes the dense world cheap to render.
- **Geographic placement spans the whole island** — these aren't section-bound props like furniture or banners. They sit at the world level, not under any gameplay area. (Their final parenting in 999_finalize may bucket some bushes under specific area roots for hide/show control during transitions, but the authoring is world-scale.)
- **Density gradient:** Bruno places higher bush+flower density near gameplay sections (lab perimeter, landing) and lower density at the open-meadow center. This creates "approach corridors" that visually funnel the player toward zones.

---

## Source pointers

- Step scripts: `folio-2025/scripts/blender_world_steps/steps/040_bushes.py` through `043_bricks.py`
- Bruno runtime foliage: `folio-2025/sources/Game/World/Foliage.js` (consumes bush anchors)
- Bruno foliage SDF atlas: `folio-2025/static/foliage/foliageSDF.png`
- Karan-portfolio's `Foliage.js` already exists for tree canopies — bushes would extend the same class
- Related memories: `reference-bruno-bushes-are-sdf`, `project-world-vision-bruno-density`
