# 04 — Trees (3 species + reference variants)

**Bruno category:** 🌳 Trees
**Scripts:** 6 (028, 032, 036, 134, 135, 136) — plus their archives/references/visual variants in [14-reference-hidden.md](14-reference-hidden.md)
**Total objects:** 70 visible trees (24 oak + 26 birch + 20 cherry) + 3 parent containers
**Status:** parents VISIBLE, `*.001` variants EXCLUDED (template/source copies)

---

## Purpose

Three tree species (oak, birch, cherry) scattered across the island. The visible runtime trees live in `*.001` collections (excluded from view layer in Blender — they're picked up by the runtime via instancing). The plain collections (`oakTrees`, `birchTrees`, `cherryTrees`) are **empty container parents** that hold three sub-collections each: `archives.*` (the curve/spline source), `visual.*` (mesh variants), `references.*` (instance reference points / scatter anchors).

---

## Scripts (visible runtime trees)

| # | File | Objs | Material | Geometry | What it adds |
|---:|---|---:|---|---|---|
| 028 | `028_oakTrees.py` | 0 | — | — | Empty parent — holds `archives.001`, `visual.004`, `references.002` |
| 032 | `032_birchTrees.py` | 0 | — | — | Empty parent — holds `archives.002`, `visual.002`, `references` |
| 036 | `036_cherryTrees.py` | 0 | — | — | Empty parent — holds `archives`, `visual.005`, `references.003` |
| 134 | `134_birchTrees.001.py` | 26 MESH | `palette` | 7,488 verts · 6,864 polys | 26 birch instances. EXCLUDED from view layer |
| 135 | `135_cherryTrees.001.py` | 20 MESH | `palette` | 5,600 verts · 5,440 polys | 20 cherry instances. EXCLUDED |
| 136 | `136_oakTrees.001.py` | 24 MESH | `palette` | 8,256 verts · 7,488 polys | 24 oak instances. EXCLUDED |

---

## The 4-collection pattern per tree species

Bruno uses the same 4-collection structure for each species:

```
oakTrees/                          (parent, empty)
├── archives.001/                  (1 CURVE — the source spline for trunk shape)
├── visual.004/                    (7 MESH — leaf/branch variant meshes)
└── references.002/                (24 CURVE — scatter anchor splines)

birchTrees/
├── archives.002/                  (1 CURVE)
├── visual.002/                    (7 MESH)
└── references/                    (26 MESH — instance reference geometry)

cherryTrees/
├── archives/                      (1 CURVE)
├── visual.005/                    (7 MESH)
└── references.003/                (20 CURVE)

oakTrees.001/ ← VISIBLE? excluded   24 MESH instances
birchTrees.001/                     26 MESH instances
cherryTrees.001/                    20 MESH instances
```

The `*.001` collections (134-136) hold the actually-placed instanced trees. The parent + sub-collections (`archives`, `visual`, `references`) act as a **template registry** Bruno hand-authored once, then instanced via curves+modifiers into the `.001` copies.

The reference/visual/archives collections are covered in [14-reference-hidden.md](14-reference-hidden.md).

---

## Notable patterns

- **All trees use the `palette` material.** Vertex colors do all the work (trunk brown, leaf yellow-green-orange).
- **Cherry trees are pink** (visually) — coloring comes from vertex attribute on `135_cherryTrees.001`'s meshes, not a separate material.
- **No leaf alpha-cut, no SDF.** Bruno's tree leaves are solid mesh polys with hand-baked vertex color. (Bushes are a different system — they use SDF foliage. See [05-foliage-flowers-boundaries.md](05-foliage-flowers-boundaries.md).)
- **`.001` excluded from view layer** = Bruno renders trees via instance-on-curve in production. In the .blend they're hidden to keep the viewport fast.
- **Tree geometry is generous** — 21,344 verts total across all 70 trees. Karan-portfolio's tree count is similar but we use foliage-cloud canopies, not solid meshes.

---

## Role in Bruno's world

Trees are the **vertical landmark layer** — the only props that rise high enough to block long sight-lines and create the feeling of zones-within-the-island:

- **3 species, 3 visual moods:**
  - **Oak** (24 instances) — broad-canopy, classic tree silhouette. Carries the warm yellow-orange autumn palette via vertex colors.
  - **Birch** (26 instances) — slim, lighter, taller-feeling. Forms loose clusters in open areas.
  - **Cherry** (20 instances) — pink-tinted blossoms (vertex colors), visually distinct. Used as accent trees, not background — likely near specific zones (lab? altar?).
- **Density: 70 trees across an island roughly the size of Bruno's playable area** — that's enough to **break up the meadow visually without crowding the player**. Bruno's vision is "no empty space" but also "no forest" — trees are landmarks, not walls.
- **The 4-collection-per-species pattern is a Blender-native template/instance system.** `archives.*` holds the source curve (trunk shape), `visual.*` holds 7 leaf-cluster mesh variants per species, `references.*` holds the scatter anchor points/splines. The `.001` collections (134-136) are the fully-instanced final placements that get rendered. This separation lets Bruno tweak the source once and re-bake all instances.
- **Trees integrate with terrain via vertex-color baking** — the warm-cool tonal gradient on each tree (darker at base, brighter at canopy) is hand-painted to match the `terrainGradient` palette so trees feel "grown from" the ground, not pasted on.
- **No tree has its own material** — all 70 use `palette`. The pink cherry blossom and orange oak leaves are vertex-color attributes on the mesh.
- **No leaf-alpha or SDF for tree leaves** — these are solid-poly canopies. Bushes (040) use a completely different SDF foliage-cloud system. This is intentional separation: trees = landmarks (need silhouette), bushes = density (need softness).
- **Trees sit ABOVE bushes/flowers in layering** — fences and bricks are placed AROUND trees, not under them. The `references.*` scatter points likely have exclusion radii so smaller props don't clip into trunks.

---

## Source pointers

- Visible tree scripts: `folio-2025/scripts/blender_world_steps/steps/134_birchTrees.001.py`, `135_cherryTrees.001.py`, `136_oakTrees.001.py`
- Parent container scripts: `028_oakTrees.py`, `032_birchTrees.py`, `036_cherryTrees.py`
- Sub-collection scripts (in [14-reference-hidden.md](14-reference-hidden.md)): 029, 030, 031, 033, 034, 035, 037, 038, 039
- Bruno's runtime tree rendering: `folio-2025/sources/Game/World/` (Foliage.js handles canopy clouds)
- Karan-portfolio's tree system: `src/World/Nature.js`, `src/World/Foliage.js` (do NOT touch without asking — memory `feedback-trees-already-fixed`)
