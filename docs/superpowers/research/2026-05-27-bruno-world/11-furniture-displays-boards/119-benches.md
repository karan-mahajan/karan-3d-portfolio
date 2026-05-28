# 119_benches.py — 7 world-scattered benches with 2-cuboid compound colliders each

**Path:** `folio-2025/scripts/blender_world_steps/steps/119_benches.py`
**Lines:** 320
**Adds:** 21 objects (7 MESH, 14 EMPTY) to collection `benches`
**Group:** [11-furniture-displays-boards](../11-furniture-displays-boards.md)

## What it does (code-level)

Creates `benches` collection (also linked into the scene root — top-level world prop). Adds **7 benches**, each a triplet: 1 visible MESH + 2 collider EMPTYs.

**Each bench's structure:**

| Role | Object | Type | Mesh | Notes |
|---|---|---|---|---|
| Bench body | `benchPhysicalDynamic[.NNN]` | MESH | `Cube.158` (shared by all 7) | Scale 1.092 uniform, rotation varies per bench |
| Seat collider | `cuboid.NNN` | EMPTY/CUBE | — | First collider — wider, higher z (seat plane) |
| Base/leg collider | `cuboid.NNN` | EMPTY/CUBE | — | Second collider — narrower (legs) |

**Template-stack pattern:** all 7 mesh objects reference the **same shared mesh datablock** `Cube.158`. Each bench is one MESH OBJECT (not a fresh mesh).

**7 bench placement positions:**

| Bench | Mesh location (x, y, z) | Rotation Z |
|---|---|---|
| `benchPhysicalDynamic` | (19.80, -33.05, 0.756) | -0.183 (-10°) |
| `benchPhysicalDynamic.001` | (37.97, -35.98, 0.756) | 0.742 (≈43°) |
| `benchPhysicalDynamic.002` | (further sample needed) | varies |
| `benchPhysicalDynamic.003` | varies | varies |
| `benchPhysicalDynamic.004` | varies | varies |
| `benchPhysicalDynamic.005` | varies | varies |
| `benchPhysicalDynamic.006` | varies | varies |

(All 7 at z=0.756 if on flat ground; small rotation variation per placement.)

**14 colliders (2 per bench):**

| Pair | Seat collider | Base collider |
|---|---|---|
| Bench 0 | `cuboid.014` (-33.66, 1.049) scale (2.30, 0.328, 0.813) | `cuboid.015` (-34.13, 0.311) scale (2.30, 1.295, 0.647) |
| Bench 1 | `cuboid.016` (same as .014 — staging share) | `cuboid.017` (same as .015 — staging share) |
| Bench 2 | `cuboid.050` | `cuboid.059` |
| Bench 3 | `cuboid.067` | `cuboid.068` |
| Bench 4 | `cuboid.070` | `cuboid.078` |
| Bench 5 | `cuboid.081` | `cuboid.193` |
| Bench 6 | `cuboid.217` | `cuboid.218` |

**All seat colliders at (-33.66, 1.049) scale (2.30, 0.328, 0.813)** — same staging position for the seat-plane collider across multiple benches. Similarly all base colliders at (-34.13, 0.311) scale (2.30, 1.295, 0.647). Pure template-stack.

## Key data

- **Datablocks referenced:** mesh `Cube.158` (shared by all 7 bench objects)
- **Materials assigned:** `palette` (per group .md)
- **Modifiers added:** none on any mesh — bench mesh data is pre-smoothed
- **Custom properties:** none observed (no `mass` — but `PhysicalDynamic` suffix suggests runtime makes them dynamic with default mass)
- **World positions of key anchors:** 7 bench positions scattered across the world (see table); all 14 collider positions at staging (-33.66 or -34.13, ...)
- **Object types breakdown:** 7 MESH, 14 EMPTY
- **Parent collection:** `benches` (also linked into `scene.collection.children` — top-level world prop, NOT zone-parented by finalize)

## Technique / recipe

**World-scattered benches via shared-mesh template-stack:**

1. **One mesh datablock** (`Cube.158`) shared by all 7 bench objects — same model, instanced 7 times.
2. **7 mesh objects** at unique world positions with unique rotations (each bench faces a different direction, matching its scenic vantage point).
3. **2 collider primitives per bench** (seat plane + leg base) at SHARED staging coordinates. Bruno reuses the same 2 collider positions across multiple benches — they're collider-template references, not per-bench colliders.
4. **All scaled to 1.092** uniform — slight oversize of the source bench mesh.
5. **Z=0.756** for all benches — they sit on flat ground (similar height).

**Compound collider** (seat + base):
- `cuboid.014/.016/.050/.067/.070/.081/.217`: **seat plane** — thin and wide (scale 2.30 × 0.328 × 0.813), at higher z (1.049) — the player can step/sit on this
- `cuboid.015/.017/.059/.068/.078/.193/.218`: **base/legs** — thicker (scale 2.30 × 1.295 × 0.647), at lower z (0.311) — the legs/skirt of the bench

This is **the cleanest compound-collider pattern in batch 4**: bench = thin-top + thick-bottom box stack.

**Top-level world parenting** — same as lanterns (117), pole-lights (118). Benches are world-wide ambient props, not zone-parented. They span the whole island as wayfinding/resting points.

**Different rotations per bench** — each at its scenic vantage point with the bench oriented to face the view. Bruno hand-placed and hand-oriented each.

**Shared collider staging positions across benches** — multiple cuboids at identical staging coords. The runtime applies each bench's transform to its 2 colliders, producing 7 distinct compound hitboxes from the 14 template-shared collider entries.

## Connections

- **Reads from:** `005_meshes_*.py` (`Cube.158`)
- **Read by:** `999_finalize.py` (NOT zone-parented — stays at scene root)
- **Depends on:** `013_collections.py` (collection skeleton), `005_meshes_*.py` (mesh)
- **Depended on by:** physics system, scattered-prop placement

## Notable code patterns

- **`scene.collection.children.link(coll)`** — top-level world-prop linking, same as lanterns/pole-lights. Benches are scattered across the whole world, not contained in zones.
- **Template-stack with shared mesh** — 7 mesh objects, 1 shared mesh datablock. Memory-efficient.
- **Shared staging for colliders** — `cuboid.014` and `cuboid.016` at the same staging coords; similar for the base colliders. Bruno reuses staging positions across multiple instances (runtime applies the per-bench transform).
- **2-piece compound collider per bench** — seat (thin/wide/high) + base (thick/narrow/low). 14 colliders total for 7 benches.
- **`PhysicalDynamic` suffix without `mass` custom prop** — benches are dynamic (pushable) at runtime's default mass.
- **All same z=0.756** — confirms placement on flat ground. Bruno didn't deal with elevation per bench (all at sea-level zones).
- **Numbering quirk:** colliders use `.014, .015, .016, .017, .050, .059, .067, .068, .070, .078, .081, .193, .217, .218` — non-sequential because Blender's global counter has been incremented by other props in between.
- **Most-instanced prop in batch 4** by per-instance count (7 instances), beating even most lighting fixtures in count per script.
