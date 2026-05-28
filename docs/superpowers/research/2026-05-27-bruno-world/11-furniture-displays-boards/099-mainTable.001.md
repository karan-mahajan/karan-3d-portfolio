# 099_mainTable.001.py — projects-zone main work table with branded carpet

**Path:** `folio-2025/scripts/blender_world_steps/steps/099_mainTable.001.py`
**Lines:** 65
**Adds:** 4 objects (2 MESH, 2 EMPTY) to collection `mainTable.001`
**Group:** [11-furniture-displays-boards](../11-furniture-displays-boards.md)

## What it does (code-level)

Creates `mainTable.001` collection — the **projects-section's main work table** (parallel to `mainTable` 085 in the lab):

| Object | Type | Mesh | Location | Notes |
|---|---|---|---|---|
| `carpet` | MESH | `Plane.022` | (37.25, -14.19, 0.019) | **The branded floor carpet** under the table. rotZ=0.262 (≈15°). z=0.019 (just above ground) |
| `Cube.090` | MESH | `Cube.121` | (-26.42, 20.19, 0.890) | The table mesh at the projects-zone position. rotZ=0.262 (≈15° — matches the carpet) |
| `mainTablePhysicalDynamic` | EMPTY/PLAIN_AXES | — | (36.61, -12.15, 0.533) | Physics-dynamic anchor at staging |
| `cuboid.051` | EMPTY/CUBE | — | (-2.47, 25.12, 0.533) | Table collider, rotZ=-1.309 (-75°), scale (1.16, 2.42, 0.98) — **identical scale to `cuboid.063` in 085** |

## Key data

- **Datablocks referenced:** mesh `Plane.022` (carpet), `Cube.121` (table mesh — DIFFERENT from `Cube.067` in 085)
- **Materials assigned:** `palette`, `projectsCarpet` (the branded carpet material — projects-section-only)
- **Modifiers added:** **none** — even the table mesh skips Smooth-by-Angle (unlike 085's table which has it). Suggests `Cube.121` is pre-smoothed in the mesh data.
- **Custom properties:** none
- **World positions of key anchors:**
  - Carpet at (37.25, -14.19, 0.019) — projects zone area, at floor level (z just above ground)
  - Table at (-26.42, 20.19, 0.890) — projects-section coordinates, z=0.890 (table-top height)
  - Physics anchor at staging (36.61, -12.15, 0.533)
  - Collider at (-2.47, 25.12, 0.533) — staging area for projects
- **Object types breakdown:** 2 MESH, 2 EMPTY
- **Parent collection:** `mainTable.001` (re-parented under `projects/` by finalize)

## Technique / recipe

**Twin of `085_mainTable.py` but with a carpet instead of balls/candle:**

1. **Table mesh** (`Cube.121`) — uses a different mesh datablock than the lab's table (`Cube.067` in 085). Same role, different content (the projects table is workshop-themed; the lab's is alchemy-themed).
2. **Branded carpet** (`Plane.022`) — a flat plane just above ground level (z=0.019) using the special `projectsCarpet` material. The carpet visually defines the "projects workshop floor" area.
3. **Physics anchor + collider** — same scale as 085 (`cuboid.051` scale (1.16, 2.42, 0.98) is identical to `cuboid.063` in 085). Bruno reuses the table-top collider sizing across both tables.
4. **No decorative props** on this table — unlike 085 (balls + candle), the projects table is bare. Reason: the workshop tools (anvil 094, grinder 098, oven 100, quench 102) sit AROUND the table in the projects zone. The table itself is the workspace, not a still-life.

**Branded `projectsCarpet` material** — first per-section material in batch 4. Bruno brands the projects floor with a custom carpet texture. Compare: 11-furniture-displays-boards.md mentions `projectsCarpet` flooring is part of the projects section's identity.

**Same 15° rotation on table + carpet** (both rotZ=0.262) — they share an axis. The carpet is sized to extend slightly past the table footprint (it's the visible boundary of the workshop area).

**No `Smooth by Angle` modifier** — the table mesh ships pre-smoothed. Bruno doesn't always add smoothing modifiers; depends on whether the source mesh data already encodes smoothing.

## Connections

- **Reads from:** `005_meshes_*.py` (`Plane.022`, `Cube.121`), `004_materials.py` (`projectsCarpet`, `palette`)
- **Read by:** `999_finalize.py` (parents `mainTable.001/` under `projects/`)
- **Depends on:** `093_projects.py` (parent zone)
- **Depended on by:** physics system

## Notable code patterns

- **`mainTable.001` is the projects-zone twin of `mainTable` (085, in lab)** — identical Blender pattern, different content.
- **`carpet` (no `.001` suffix)** — the carpet is unique to projects, no lab equivalent. Bruno only assigns suffix when there are siblings.
- **No decorative props** — projects table is empty (the workshop tools sit nearby, not on the table).
- **Shorter script than 085** (65 lines vs 126) — because there are no balls or candle to set up.
- **`projectsCarpet` material is section-specific** — first appearance in batch 4. Bruno's per-zone branding materials (also: `circuitBrand`, `careerText*`, `bowlingLabel*`).
- **Identical collider scale** to 085's collider — Bruno reused the exact half-extents because both tables have the same physical footprint despite different mesh content.
- **Carpet at z=0.019** — just above ground (terrain at z=0). Avoids z-fighting with the floor.
