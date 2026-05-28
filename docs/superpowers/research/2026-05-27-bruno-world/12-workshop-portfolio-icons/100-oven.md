# 100_oven.py — projects-zone oven with stacked-mesh body, blower, and charcoal layers

**Path:** `folio-2025/scripts/blender_world_steps/steps/100_oven.py`
**Lines:** 133
**Adds:** 9 objects (5 MESH, 4 EMPTY) to collection `oven`
**Group:** [12-workshop-portfolio-icons](../12-workshop-portfolio-icons.md)

## What it does (code-level)

Creates `oven` collection. Adds 9 objects — 5 visible meshes (oven body + stacked interior layers + blower) + 4 anchor/collider EMPTYs:

| Object | Type | Mesh | Location | Notes |
|---|---|---|---|---|
| `Cube.121` | MESH | `Cube.136` | (-27.95, 18.70, 0.086) | **The oven's main body slab** (`scale=(0.759, 3.928, 0.519)` — extremely wide, narrow Y-axis, low Z. A LONG flat slab). rotZ=-2.094 (-120°) |
| `Cube.092` | MESH | `Cube.131` | (-27.55, 19.42, 1.152) | The oven's upper body. rotZ=-2.094. scale=1.294 uniform |
| `Cube.101` | MESH | `Cube.132` | (-27.55, 19.42, 1.152) | **Co-located with `Cube.092`** — same transform. Stacked layer (likely a different material slot or shader pass) |
| `refBlower` | MESH | `Cube.165` | (33.38, -13.27, 0.276) | **The blower at actual projects position**. rotZ=3.141 (180° — flipped). scale=1.0 |
| `refCharcoal` | MESH | `Cube.188` | (-27.55, 19.42, 1.168) | **Co-located with Cube.092/.101** but Δz=+0.016. The charcoal inside the oven (emissive orange glow) |
| `blowerPhysicalDynamic` | EMPTY/PLAIN_AXES | — | (33.46, -13.59, 0.527) | Blower physics anchor at projects position. empty_display_size=2.0 |
| `cuboid.052` | EMPTY/CUBE | — | (-5.40, 23.45, 0.527) | Blower collider, rotZ=-0.524, scale (1.13, 1.51, 0.94) |
| `refOvenPhysicalDynamic` | EMPTY/PLAIN_AXES | — | (34.52, -12.97, 0.566) | Oven physics anchor at projects position. empty_display_size=2.0 |
| `cuboid.053` | EMPTY/CUBE | — | (-4.79, 24.52, 0.566) | Oven collider, rotZ=-0.524, scale (1.36, 0.75, 1.10) |

## Key data

- **Datablocks referenced:** `Cube.136` (slab body), `Cube.131` (upper body), `Cube.132` (stack layer), `Cube.165` (blower), `Cube.188` (charcoal)
- **Materials assigned:** `emissiveOrangeRadialGradient` (charcoal glow), `palette` (body parts)
- **Modifiers added:** none
- **Custom properties:** none
- **World positions of key anchors:**
  - Oven body mesh at (-27.95, 18.70, 0.086) — staging, very flat slab orientation
  - Upper body + charcoal at (-27.55, 19.42, ~1.16) — staging, ~0.7m above slab
  - Blower at (33.38, -13.27, 0.276) — actual projects-zone position
  - 2 physics anchors at projects-zone positions
  - 2 colliders at separate staging (-5.40/-4.79, 23.45/24.52)
- **Object types breakdown:** 5 MESH, 4 EMPTY
- **Parent collection:** `oven` (re-parented under `projects/` by finalize)

## Technique / recipe

**Oven with 2 separately-physics-active components (oven + blower) and a 3-layer body stack:**

1. **Bottom slab** (`Cube.121` with extreme Y-scale 3.928) — the long flat oven floor.
2. **Upper body stack** at the same XY (-27.55, 19.42):
   - `Cube.092` (frame block)
   - `Cube.101` (co-located stacked layer — different material slot or rendering pass)
   - `refCharcoal` (Δz=+0.016, the emissive orange charcoal inside)
   - All 3 share scale 1.294 uniform
3. **Blower** (`refBlower`) at a SEPARATE position (33.38, -13.27) — actual projects-zone. The blower is a distinct physics object from the main oven.
4. **2 separate PhysicalDynamic anchors**:
   - `refOvenPhysicalDynamic` at (34.52, -12.97) — oven body
   - `blowerPhysicalDynamic` at (33.46, -13.59) — blower body, 1.2m offset
5. **2 separate cuboid colliders** at staging — one per dynamic body.

**Stacked-mesh body** (`Cube.092` + `Cube.101` + `refCharcoal` all at the same XYZ, Δz=tiny) — Bruno layers 3 meshes to compose the visible oven:
- `Cube.092`: outer frame
- `Cube.101`: middle layer (maybe inner wall or detail)
- `refCharcoal`: emissive inner glow (the orange charcoal coal effect)

**Why two separate physics bodies?** The blower can be operated INDEPENDENTLY of the oven — Bruno separates them so the player can interact with the blower (turn it on, see fire intensify) without moving the whole oven.

**Different orientation Z values:** the bottom slab is at z=0.086 (ground level), the upper body is at z=1.152, charcoal at z=1.168. Bruno carefully stacks the oven vertically.

**`Cube.121` is also the projects-table mesh in 099** — different object same mesh data? No — `Cube.121` here REFERENCES mesh `Cube.136`, while in 099 the object `Cube.090` references mesh `Cube.121`. Different objects/data; the name `Cube.121` is just Blender's auto-numbering coincidence.

**`empty_display_size=2.0`** on both PhysicalDynamic anchors — Bruno made these visible-large in Blender for the artist.

## Connections

- **Reads from:** `005_meshes_*.py` (5 cube meshes)
- **Read by:** `999_finalize.py` (parents `oven/` under `projects/`)
- **Depends on:** `093_projects.py` (projects parent)
- **Depended on by:** runtime fire-effect system, physics

## Notable code patterns

- **Two separate physics bodies in one collection** — oven + blower are independent. Bruno's pattern for compound props with separable interactivity.
- **3-layer mesh stack at same XYZ** — outer frame + middle layer + emissive interior. Bruno's standard for compounded emissive props (also seen in cauldron 084).
- **Extreme Y-scale on the slab** (`scale=(0.759, 3.928, 0.519)`) — a flat oven-floor by hyperscaling Y. The mesh source is 1×1×1 cube; scaling produces the elongated slab.
- **rotZ=-2.094 (-120°)** — non-cardinal rotation. Bruno tilts the oven for visual angle.
- **`refBlower` at projects-zone position** while the oven body is at staging — different placement strategies in the same script.
- **Blower flipped 180°** (rotZ=3.141) — orients its blow-direction away from the oven mouth (or toward, depending on layout).
- **Mass-less dynamic bodies** — runtime defaults.
