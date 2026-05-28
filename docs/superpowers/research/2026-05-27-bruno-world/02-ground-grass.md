# 02 — Ground & Grass (the floor of everything)

**Bruno category:** 🏝️ Ground & Foundation
**Scripts:** 2 (020, 021)
**Total objects:** 2 (1 terrain mesh + 1 grass scatter mesh)
**Status:** VISIBLE — the entire ground plane

---

## Purpose

The **island** the world sits on, plus the **procedural grass field** that covers it. Together they're the entire ground layer.

---

## Scripts

| # | File | Objs | Mesh | Modifier | Material | Geometry | What it adds |
|---:|---|---:|---|---|---|---|---|
| 020 | `020_terrain.py` | 1 MESH | `Plane.134` | `GeometryNodes` → node-group `Geometry Nodes` | `terrain` | 16,641 verts · 16,384 polys | THE island. Single 128×128-subdivided plane at origin, scaled to world extent. Procedural displacement + color sampling driven by the `terrainData` PNG + `terrainGradient` ramp via the node-group |
| 021 | `021_grass.py` | 1 MESH | (3-vert triangle) | `GeometryNodes` → node-group `Geometry Nodes.001` | `grass` | 3 verts · 1 poly | A single triangle. The geometry-nodes group scatters this thousands of times across the terrain, masked by the `terrainData` G channel. (At runtime, this is replaced by Bruno's `Grass.js` camera-billboarded shader system — see [reference-bruno-ground-systems](../../../.claude/projects/...))) |

---

## Notable patterns

- **The terrain is one plane.** Not a heightfield, not a sculpted mesh — a flat subdivided plane with GeometryNodes doing the displacement/coloring procedurally based on the `terrainData` PNG.
- **The grass is one triangle.** GeometryNodes does ALL the work (scatter density, position-jitter, height-from-PNG, color from terrain gradient). This is a Blender-side preview of what `Grass.js` does at runtime — the 3D viewport shows scattered grass for development convenience.
- **`terrainData` PNG** is the source of truth: R-channel = paths/slabs mask, G-channel = grass mask, B-channel = water depth. (This is exactly the technique we previously tried to author ourselves in the abandoned G1 sub-project — Bruno's hand-painted version is the reference.)
- **`terrainGradient`** is a 1D color ramp sampled by height. The warm/cool/sand transitions come from this single texture.

---

## How it connects to other groups

- **Provides ground for everything else.** All 120 other collections place objects ON this terrain plane.
- **Grass is masked by `terrainData.g`** — paths (`027_slabs`, `025_road.001`, `043_bricks`) show through because their pixels are 0 in the green channel.
- **The plane's UV** maps directly to the `terrainData` PNG — UV (0,0) = pixel (0,0), edge-clamp. This is the key fact for any runtime that reads the PNG.

---

## Role in Bruno's world

The terrain + grass pair is the **canvas everything else paints on**.
- **Terrain provides the height profile** every prop snaps to. There are no flat-floored sub-zones in Bruno's world — even the bowling alley, race track, and lab sit on terrain whose Y is read from this mesh.
- **`terrainData` PNG is the world's "blueprint."** Every system that needs to know "is this spot a path / grass / water?" reads it:
  - Grass scatter (021) reads G channel — bushes appear where G is high
  - Paths (027 slabs, 025 road.001, 043 bricks) live where R is non-zero
  - Bridges (024) cross water bodies — B channel is high there
  - Runtime `Floor.js` colors the ground based on which channel wins per pixel
- **Grass density gates the visual identity** — Bruno's "yellow meadow" look is entirely from the 78k-blade scatter the geometry-nodes group does on the 3-vert grass mesh. Without it, the terrain is just colored dirt.
- **The terrain mesh is a 128×128 subdivided plane** — coarse enough to be cheap, fine enough that the PNG-driven displacement reads as smooth hills.
- **No water mesh in this group.** Water is a runtime shader (Bruno's `Water.js`) sampled where `terrainData.b > 0`. The terrain itself contains the depressions for ponds; the shader paints water on top.

These two scripts establish **the lowest layer of the world hierarchy** — every other group's objects live in the space defined by terrain height + the `terrainData` mask.

---

## Source pointers

- `folio-2025/scripts/blender_world_steps/steps/020_terrain.py` (50 lines)
- `folio-2025/scripts/blender_world_steps/steps/021_grass.py` (50 lines)
- Node groups (in 003): `Geometry Nodes` (terrain), `Geometry Nodes.001` (grass scatter)
- Materials (in 004): `terrain`, `grass`
- Images (in 002): `terrainData`, `terrainGradient`
- Runtime grass: `folio-2025/sources/Game/World/Grass.js`
- Runtime terrain sampling: `folio-2025/sources/Game/World/Terrain.js` (look for the PNG-sample code)
