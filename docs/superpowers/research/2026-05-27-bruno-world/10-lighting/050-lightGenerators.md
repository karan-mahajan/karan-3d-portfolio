# 050_lightGenerators.py — 2 backstage light-generator props with collider compounds

**Path:** `folio-2025/scripts/blender_world_steps/steps/050_lightGenerators.py`
**Lines:** 341
**Adds:** 12 objects (4 MESH, 8 EMPTY) to collection `lightGenerators`
**Group:** [10-lighting](../10-lighting.md)

## What it does (code-level)

Creates `lightGenerators` collection. Adds **two complete light-generator instances**, each composed of 6 objects (2 meshes + 1 placement empty + 3 collider primitives). Total: 12 objects.

**Instance 1 (the `.001` suffix family):**

| Object | Type | Mesh | Location | Notes |
|---|---|---|---|---|
| `common.001` | MESH | `Plane.011` | (52.13, 18.50, 0.39) | Staging position. Smooth by Angle.003 modifier (Input_1=0.524 rad ≈30°). `booleans=[]` custom prop |
| `emissive.001` (named `emissive.002`) | MESH | `Plane.014` | (52.13, 18.50, 0.39) | Same staging position. Same smoothing modifier + `booleans=[]` |
| `lightGeneratorPhysicalDynamic.001` | EMPTY/PLAIN_AXES | — | (54.18, 16.06, 1.86) | Actual placement anchor — physics-dynamic light generator |
| `cuboid.194` | EMPTY/CUBE | — | (47.28, 9.04, 0.93) | Collider, scale (1.73, 1.40, 1.86) — large body box |
| `cuboid.195` | EMPTY/CUBE | — | (48.34, 9.04, 1.63) | Collider, scale (0.34, 0.32, 3.22) — tall narrow part |
| `cuboid.196` | EMPTY/CUBE | — | (48.34, 9.04, 3.52) | Collider, scale (0.34, 1.98, 0.39) — wide flat top |

**Instance 2 (the `.003` suffix family):**

| Object | Type | Mesh | Location | Notes |
|---|---|---|---|---|
| `common.002` | MESH | `Plane.011` | (52.13, 18.50, 0.39) | Same staging — rotZ=-1.571 (-90°). Same smoothing + `booleans=[]` |
| `emissive.003` | MESH | `Plane.014` | (52.13, 18.50, 0.39) | Same staging, same rotation. Same smoothing + `booleans=[]` |
| `lightGeneratorPhysicalDynamic.003` | EMPTY/PLAIN_AXES | — | (47.49, 9.05, 1.86) | Placement anchor — rotZ=1.484 (~85°) |
| `cuboid.111` | EMPTY/CUBE | — | (47.28, 9.05, 0.93) | Collider with slight rotZ=-0.087 (-5°), scale (1.73, 1.40, 1.86) |
| `cuboid.171` | EMPTY/CUBE | — | (48.34, 9.04, 1.63) | Collider, scale (0.34, 0.32, 3.22) |
| `cuboid.197` | EMPTY/CUBE | — | (48.34, 9.04, 3.52) | Collider, scale (0.34, 1.98, 0.39) |

**Key observation:** Both instances' colliders sit at the same world coordinates (~(47.28, 9.04) etc.) — the colliders are LOCAL collider shapes, runtime-bound to each light generator's placement anchor.

## Key data

- **Datablocks referenced:** meshes `Plane.011` (common), `Plane.014` (emissive); node-group `Smooth by Angle.003`
- **Materials assigned:** via mesh datablock — `emissiveOrangeRadialGradient` (on emissive.*), `palette` (on common.*)
- **Modifiers added:** 4× `Smooth by Angle.003` (NODES, Input_1=0.524 rad ≈30° — gentler than the typical 55° threshold)
- **Custom properties:** `booleans=[]` on every mesh (empty list — no CSG operations active; placeholder for runtime)
- **World positions of key anchors:**
  - Instance 1 placement: (54.18, 16.06, 1.86)
  - Instance 2 placement: (47.49, 9.05, 1.86) — both at z=1.86 (waist height)
  - All meshes at shared staging (52.13, 18.50, 0.39)
  - All colliders at shared local origin (47.28, 9.04) — runtime-relative
- **Object types breakdown:** 4 MESH, 8 EMPTY
- **Parent collection:** `lightGenerators` (re-parented under `behindTheScene` by finalize)

## Technique / recipe

**Bruno's "template + placement empty + compound collider" pattern, in its simplest form:**

1. Each light generator is **2 mesh objects** (the visible body + the emissive panel) referencing 2 shared mesh datablocks.
2. The 2 meshes are **stacked at a shared staging location** (52.13, 18.50) — they don't render meaningfully in Blender, only their data references the runtime needs.
3. A **placement EMPTY** (PLAIN_AXES) defines where in the world this generator actually sits. Runtime reads the empty's transform to position the meshes.
4. **3 collider EMPTY/CUBEs** stacked at a shared local origin (47.28, 9.04) form the compound collision shape: large body cuboid + tall narrow neck + wide flat top. Roughly a "tower with an awning" silhouette.
5. The pattern repeats for instance 2 — same recipe, different placement empty, different name suffixes.

**The `booleans=[]` custom prop** on every mesh is a placeholder for runtime CSG operations — Bruno's engine supports applying booleans at runtime, and this list is the slot.

**Smooth-by-Angle threshold 30°** (much tighter than the 55° default seen elsewhere) — preserves crisp edges on the geometric generator shape rather than softening it.

**Both placement empties at z=1.86** — they sit at waist height, suggesting these are floor-standing props (legs reaching down to ground from the anchor height).

**Instance 2 rotated ~85° around Z** while instance 1 is unrotated — gives the two generators different visual angles even though they share the same mesh data.

## Connections

- **Reads from:** `005_meshes_*.py` (`Plane.011`, `Plane.014`), `003_node_groups.py` (`Smooth by Angle.003`)
- **Read by:** `999_finalize.py` (parents `lightGenerators/` under `behindTheScene/`)
- **Depends on:** `049_behindTheScene.py` (the parent zone collection)
- **Depended on by:** runtime physics + emissive rendering system

## Notable code patterns

- **Template-stack instance pattern:** N visible meshes all at the same staging coordinate, plus N placement empties at actual world positions. The Blender file looks "wrong" (everything stacked) but is correct after runtime reads the placement anchors. This is THE pattern Bruno uses across lanterns (117), poleLights (118), and other instanced light fixtures.
- **`booleans=[]` empty-list custom prop** — first observed in batch 4. Common.* and emissive.* both carry it. The runtime probably checks `len(ob['booleans'])` to decide whether to perform CSG.
- **`physicalDynamic` suffix on the placement empty** — naming convention Bruno reuses across props that runtime-spawns as Rapier dynamic bodies. The suffix tells the runtime "this anchor's transform → dynamic rigid body."
- **Compound collider via 3 stacked cuboids** — same compound-collider pattern as cones (067) or pins (057), but for a more box-shaped silhouette. Each cuboid is its own EMPTY/CUBE; scale carries the half-extents (e.g., 1.73 → 3.46m wide collider).
- **Idempotent guard:** every mesh and empty is fetched with `bpy.data.objects.get('name') or bpy.data.objects.new(...)`, then `if ob.name not in {o.name for o in coll.objects}: coll.objects.link(ob)`. Re-running the script doesn't duplicate.
- **`use_pin_to_last = True`** on every modifier — keeps the Smooth-by-Angle as the LAST modifier in the stack (important for normal computation to see the fully-processed mesh).
