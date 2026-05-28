# 116_stool.py — toilet's stool + 3 pushable toilet-paper rolls

**Path:** `folio-2025/scripts/blender_world_steps/steps/116_stool.py`
**Lines:** 238
**Adds:** 8 objects (4 MESH, 4 EMPTY) to collection `stool`
**Group:** [11-furniture-displays-boards](../11-furniture-displays-boards.md)

## What it does (code-level)

Creates `stool` collection. Despite the name, this contains 1 stool + **3 pushable toilet-paper rolls** in the toilet zone:

**The stool:**

| Object | Type | Mesh | Location | Notes |
|---|---|---|---|---|
| `stoolPhysicalDynamic` | MESH | `Cube.151` | (67.51, -64.70, 0.659) | rotZ=-0.606 (-35°). The visible stool itself |
| `cuboid.080` | EMPTY/CUBE | — | (-12.47, -19.34, 0.377) | Stool collider, rotZ=-0.606, scale (0.734, 0.734, 0.734) — at staging |

**Three toilet paper rolls:**

| Object | Type | Mesh | Location | Custom prop | Collider |
|---|---|---|---|---|---|
| `paperPhysicalDynamic` | MESH | (cylinder mesh) | (65.01, -65.39, 1.385) | — | `tube.003` at (-14.97, -20.03, 1.210) |
| `paperPhysicalDynamic.001` | MESH | (cylinder mesh) | (65.09, -65.75, 1.378) | — | `tube.002` at (-14.89, -20.38, 1.203) |
| `paperPhysicalDynamic.002` | MESH | `Cylinder.028` | (65.02, -65.56, 1.711) | **`mass=0.02`** | `tube.001` at (-14.96, -20.20, 1.536). `Smooth by Angle.002` (Input_1=1.442 rad ≈83°) |

(The 3 paper rolls cluster within (~65.0-65.1, ~-65.4 to -65.7, varying z=1.378 to 1.711) — a small 0.4m volume.)

## Key data

- **Datablocks referenced:** mesh `Cube.151` (stool), `Cylinder.028` (paper roll — at least for the .002 variant); node-group `Smooth by Angle.002`
- **Materials assigned:** `palette` (per group .md)
- **Modifiers added:** 1× `Smooth by Angle.002` (NODES, Input_1=1.442 rad ≈83°) on `paperPhysicalDynamic.002` only
- **Custom properties:** **`mass=0.02`** on `paperPhysicalDynamic.002` — extremely light (20g), very pushable
- **World positions of key anchors:**
  - Stool at (67.51, -64.70, 0.659) — toilet zone (far east, far south)
  - 3 paper rolls clustered at (65.0-65.1, -65.4 to -65.7), z=1.378 to 1.711 — on a shelf inside the toilet
  - Stool collider at staging (-12.47, -19.34, 0.377)
  - 3 paper roll colliders at staging (-14.96, -20.0 to -20.4, 1.2 to 1.5)
- **Object types breakdown:** 4 MESH (1 stool + 3 paper rolls), 4 EMPTY (1 stool collider + 3 paper roll colliders)
- **Parent collection:** `stool` (re-parented under `toilet/` by finalize)

## Technique / recipe

**Stool + 3 pushable paper rolls bundled in one collection (collection misnamed, contains 4 props):**

1. **The stool** (Cube.151 mesh) — pushable, with a cube collider sized to its visible footprint.
2. **Three paper rolls** — each is a cylinder mesh with a matching `tube.NNN` cylindrical collider (note the naming difference: stool gets `cuboid` for box collider, papers get `tube` for cylinder colliders).
3. **`mass=0.02`** (20g) on at least one paper roll — extremely light. Players can knock them around easily. Bruno's whimsy: pushable toilet paper.
4. **Smooth-by-Angle 83°** on the .002 paper — very aggressive smoothing to make the cylinder look perfectly round.

**`tube.NNN` collider names** — `tube.001/.002/.003`. Same EMPTY/CUBE type in Blender, but the name signals to the runtime that the collision shape should be a cylinder/capsule (matching the paper roll's actual shape), not a box. This is **Bruno's name-driven collider-shape pattern**:
- `cuboid.NNN` → box collider
- `tube.NNN` → cylinder/capsule collider
Both stored as EMPTY/CUBE in Blender (Blender doesn't have a cylinder EMPTY type, so CUBE is the universal display). The runtime reads the name to pick the right Rapier shape.

**Stool collider at uniform scale 0.734** (vs the typical (1.16, 2.42, 0.98) table colliders) — the stool's collider is roughly cubic. Makes sense for a round stool: square hitbox.

**`mass=0.02`** is light enough to make the rolls behave like real toilet paper — easy to nudge, slight tumbling effect.

**The collection is named `stool`** but contains 4 distinct props (1 stool + 3 paper rolls). Bruno bundled them because they share the toilet zone. The group .md misreads this as "4 stools."

**3 paper rolls clustered at slightly different Z** (z=1.378, 1.385, 1.711) — they're stacked on a small shelf, the higher one (1.711) above the lower two (1.378-1.385) which are side-by-side.

## Connections

- **Reads from:** `005_meshes_*.py` (`Cube.151`, `Cylinder.028`, etc), `003_node_groups.py` (`Smooth by Angle.002`)
- **Read by:** `999_finalize.py` (parents `stool/` under `toilet/`)
- **Depends on:** `114_toilet.py` (parent zone)
- **Depended on by:** physics system (4 dynamic bodies)

## Notable code patterns

- **`cuboid.NNN` vs `tube.NNN` collider naming** — Bruno's name-driven collider-shape pattern. Both stored as EMPTY/CUBE in Blender; the runtime reads the name suffix to pick the collision shape (box vs cylinder).
- **`mass=0.02`** — lightest dynamic body in batch 4. Bruno's whimsy: pushable toilet paper is intentionally absurd.
- **Misleading collection name** — `stool` actually contains 1 stool + 3 paper rolls. Bundled by zone, not by prop type.
- **Each paper roll has its own collider** — `tube.001/.002/.003`. No template-share. 3 colliders for 3 paper rolls.
- **Only ONE paper roll gets the smoothing modifier** (the .002 variant). The other two don't. Bruno inconsistently applies smoothing — possibly because they were authored at different times or the .002 has a different mesh data needing more smoothing.
- **Twin of `stool.001` (112, in timeMachine)** — same template, but with 3 paper rolls added. The toilet zone gets the more elaborate version.
- **No interaction prompts, no `ref` empties** — players push these, they don't interact with prompts. Pure physics-driven whimsy.
- **Stool rotation 35° around Z** — same idea as stool.001 (112)'s 43° — non-axis-aligned for visual variety.
