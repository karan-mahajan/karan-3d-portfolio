# 01 — Foundation (datablocks + skeleton)

**Bruno category:** Foundation
**Scripts:** 20 (000–013)
**Total objects:** 0 (these load DATA, not scene objects — objects appear in 020+)
**Status:** required prerequisite for everything

---

## Purpose

These 20 scripts populate Blender's datablock library — textures, materials, mesh data, node groups, curves, armatures, lights/cameras, the world shader, and a 120-collection empty skeleton. **Nothing visible appears yet.** All later per-collection scripts (020+) reference these datablocks by name (`bpy.data.meshes.get('Plane.134')`, etc.).

---

## Scripts

| # | File | What it adds | Size |
|---:|---|---|---:|
| 000 | `000_init.py` | Wipes the scene (all objects, meshes, materials, node groups, collections, images, lights, cameras, curves, armatures, metaballs, linestyles, actions, texts, worlds) | 0.9 KB |
| 001 | `001_texts.py` | 3 embedded Python text-blocks stored in the .blend | 1.1 KB |
| 002 | `002_images.py` | 25 textures from disk: blackboardLabels, bowlingLabelStrike, careerFreelancer/Hetic/IRLTeacher/ImmersiveGarden/OnlineTeacher/Uzik, cookieBanner, distinctions, FWA, glow, projectsLabels, **terrainData** (Bruno's PNG mask!), **terrainGradient**, etc. | 21.6 KB |
| 003 | `003_node_groups.py` | 9 node groups: Auto Smooth, Geometry Nodes (terrain), Geometry Nodes.001 (grass scatter), Geometry Nodes.002 (rails-along-curve), Smooth by Angle.001/.002/.003, terrain (CompositorNodeTree) | 42.6 KB |
| 004 | `004_materials.py` | 35 materials, full shader graphs. Big ones: `palette` (the universal vertex-color material), all `emissive*RadialGradient` variants, `terrain`, `grass`, `waterfall`, `airDancer`, all branded textures | 160.2 KB |
| 005 | `005_meshes_00..06.py` | 368 mesh datablocks across 7 chunks. **Includes** `Plane.134` (the terrain mesh) and every prop mesh in the world | 9.7 MB total |
| 006 | `006_metaballs.py` | 2 metaballs (`azeazeaze`, `metaMoss`) — used by cabin moss | 21.4 KB |
| 007 | `007_curves.py` | 13 curve + font datablocks: `BézierCircle.001`, `BézierCurve`, `Plane.003/.004/.005/.007/.010/.011`, + 5 more (used by road, rails, sign, decorative arcs) | 111.4 KB |
| 008 | `008_armatures.py` | 6 armatures (bone hierarchies) for character rigs (statue, sudo character) | 90.1 KB |
| 009 | `009_lights.py` | 2 area lights (`Area`, `Area.001`) — both used by the minimap rig (day/night) | 1.4 KB |
| 010 | `010_cameras.py` | 2 orthographic cameras (`Camera`, `Camera.001`) — minimap (cameraTerrain) + vehicle-cam | 1.5 KB |
| 011 | `011_linestyles.py` | 1 freestyle line style | 0.3 KB |
| 012 | `012_world.py` | World shader (sky/ambient environment node tree) | 1.1 KB |
| 013 | `013_collections.py` | Empty 120-collection skeleton + parent/child hierarchy + color tags + visibility flags | 24.8 KB |

---

## Notable patterns

- **`terrainData`** texture in `002_images.py` is the painted PNG mask we previously tried (and abandoned) to author ourselves. Bruno's version is hand-painted and ships baked into the blend. We can **read his PNG directly** if we adopt his floor system.
- **`terrainGradient`** (also in `002_images.py`) is the warm-cool color ramp Bruno samples by terrain height. This is the source of the world's tonal warmth.
- **`palette` material** (in 004) — single material, vertex-color-driven, used by ~80% of all meshes. Avoids needing 30+ materials.
- **3 `Smooth by Angle` variants** in geometry-nodes — different angle thresholds for different prop classes (sharp props like crates vs round props like cauldrons).
- **9 node groups total** — small number, heavy reuse. Suggests our implementation can mirror with similarly few shared groups.

---

## Role in Bruno's world

Foundation scripts don't render anything — they're the **library** every later script reads from:
- **All meshes everywhere** (3,500+ visible mesh instances across 1,507 objects) reference the 368 mesh datablocks loaded here.
- **`palette` material** loaded in 004 is referenced by ~80% of all visible meshes — it's the single biggest shared resource.
- **`terrainData` + `terrainGradient` images** loaded in 002 are the single source of truth for the whole island's surface decisions (where paths are, where grass scatters, where water is, what tonal warmth the ground takes).
- **Node groups in 003** are reused across collections: `Smooth by Angle.003` smooths normals on most props (slabs, scenery, race cones/barrels, lanterns); `Geometry Nodes.001` is the grass scatter (used once but defines the entire grass field); `Geometry Nodes.002` is the rails-along-curve generator (used by the race track).
- **Curves loaded in 007** are referenced by the road (025), bowling sign (060), race-track scenery, and the tree-reference scatter splines.
- **Armatures in 008** are only used by the statue character (106 `default`) and the sudo character (128).
- **Cameras in 010** are minimap-only — neither is the main player camera. The main camera in Bruno's runtime is built in three.js, not Blender.
- **Lights in 009** are both used by the minimap day/night rig — Bruno's in-world lighting is all emissive materials, not Blender lights.
- **Collection skeleton (013)** is the "shelf" — every later script links its objects into a pre-existing named collection rather than creating it ad-hoc.

The whole foundation acts like a **shared asset registry**. Per-section scripts don't define new datablocks; they only place instances and connect them.

---

## Source pointers

- Step scripts: `folio-2025/scripts/blender_world_steps/steps/000_init.py` → `013_collections.py`
- Mesh chunks (heavy): `005_meshes_00.py` (1.5 MB) through `005_meshes_06.py`
- Materials (heaviest read): `004_materials.py` (160 KB — ~30 shader graphs)
