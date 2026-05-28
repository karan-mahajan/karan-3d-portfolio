# 055_furnitures.py — restaurant/bar furnishings around the bowling alley

**Path:** `folio-2025/scripts/blender_world_steps/steps/055_furnitures.py`
**Lines:** 1027 (longest in this batch)
**Adds:** 43 objects (18 MESH, 25 EMPTY) to collection `furnitures`
**Group:** [09-bowling](../09-bowling.md)

## What it does (code-level)

Creates `furnitures` collection. Adds 43 objects: physics-dynamic restaurant furniture (sauce bottles, tables, couches, stools) + matching collider primitives. The set is clearly a **bowling-alley snack-bar/lounge** — not bowling-game equipment.

### Visible furniture meshes (18 MESH objects)

All with `mass` custom prop (range 0.05 - 0.35). Most have `Smooth by Angle.003` GN modifier.

Examples observed:
| Object | Mesh | Location | mass | Notes |
|---|---|---|---|---|
| `sauceKetchupPhysicalDynamic` | `Cylinder.024` | (0.65, -59.50, 1.60) | 0.05 | Light tabletop bottle |
| `tablePhysicalDynamic.001` | `Plane.110` | (0.65, -59.50, 1.17) | 0.35 | Heavier; smooth-by-angle Input_1=π/4 ≈45° |
| `couchPhysicalDynamic` | `Plane.131` | (-1.18, -59.47, 1.11) | 0.35 | No GN modifier (couch is hand-smoothed) |
| `couchPhysicalDynamic.002` | `Plane.131` | (8.50, -59.47, 1.11) | 0.35 | Reuses same `Plane.131` couch mesh |
| `sauceMustardPhysicalDynamic.001` | `Cylinder.038` | (10.59, -59.43, 1.60) | 0.05 | Mustard counterpart |
| `stoolPhysicalDynamic.003` | `Plane.120` | (7.28, -73.80, 0.82) | 0.30 | Bar stool, no GN modifier |

Furniture meshes use `Smooth by Angle.003` (mostly Input_1≈0.96 rad ≈55°, some at π/4 ≈45° for tables) but only when needed.

### Collider primitives (25 EMPTY objects)

Mix of `tube.0NN` (small CUBE empties — circular furniture: bottles, stools), `cuboid.NNN` (large CUBE empties — tables, couches). Examples:
- `cuboid.103` at (-45.09, -28.69, 1.27) scale (1.82, 1.82, 0.24) — table-top collider
- `cuboid.104` at (-45.09, -28.69, 0.70) scale (1.32, 1.32, 1.32) — table-base cube
- `tube.009` at (-45.09, -28.69, 1.71) scale (0.19, 0.19, 0.69) — sauce-bottle cylinder collider
- `cuboid.105` at (-46.87, -28.66, 0.45) scale (1.70, 2.05, 0.87) — couch seat collider
- `cuboid.100` at (7.22, -78.10, 0.78) scale (1.03, 1.03, 1.54) — stool collider (THIS one in-zone, not off-stage)

Mix of off-stage parked colliders (most at x≈-45 to -47) and in-zone direct colliders (e.g., `cuboid.100` at (7.22, -78.10) flush with stool position).

## Key data

- **Datablocks referenced:** ~10+ unique meshes: `Cylinder.024` (sauce ketchup), `Cylinder.038` (sauce mustard), `Plane.110` (table top), `Plane.131` (couch), `Plane.120` (stool), and more
- **Materials assigned:** via mesh datablocks — `emissiveOrangeRadialGradient` (probably on sauce labels), `palette` (most)
- **Modifiers added:** ~10× `Smooth by Angle.003` (NODES, Input_1=π/4 or 0.96 rad) — on the GN-smoothed pieces
- **Custom properties:**
  - **`mass`** on every visible furniture mesh — 0.05 (sauce bottles), 0.30 (stools), 0.35 (tables/couches). Mass ladder: tiny tipping-prone bottles → bumpable stools → heavy tables/couches
- **World positions of key anchors:**
  - In-zone furniture along y≈-59 (a row of tables/couches/sauces) and y≈-74 (a row of stools)
  - Off-stage colliders parked at x≈-45 to -47, y≈-28 (the bowling-zone "collider depot")
- **Object types breakdown:** 18 MESH, 25 EMPTY
- **Parent collection:** `furnitures` (re-parented under `bowling/` by finalize)

## Technique / recipe

**Restaurant/bar zone, not bowling equipment:** the items here are eating-area props (sauce bottles, tables, couches, stools) suggesting Bruno's bowling alley has an attached diner-style seating area. This is decorative gameplay-flavored content, not lane gear.

**Physics-dynamic mass ladder:**
- 0.05 (sauce bottles) — easily knockable
- 0.30 (stools) — bumpable but stable
- 0.35 (tables, couches) — heavy, requires real force to move

The runtime probably uses Rapier or similar with mass-driven rigidbody simulation.

**Mixed collider strategies:** some colliders are parked off-stage at (-45 to -47, -28) and runtime-bound; others (like `cuboid.100` for stools) are placed directly at the prop's world position. The mix suggests Bruno experimented with both approaches.

**Same mesh reused for symmetric props:** the couch (`Plane.131`) is used by both `couchPhysicalDynamic` (at x=-1.18) and `couchPhysicalDynamic.002` (at x=8.50). The two stand on opposite sides of the seating area. Saves mesh data.

**Sauce + table pairing:** ketchup at (0.65, -59.50) sits ON the table at (0.65, -59.50, 1.17). The sauce's Z=1.60 places it 0.43m above the table top. Per-sauce mass=0.05 lets the player knock them off.

## Connections

- **Reads from:** `005_meshes_*.py` (many: Cylinder.024, Cylinder.038, Plane.110, Plane.120, Plane.131, and more), `003_node_groups.py` (`Smooth by Angle.003`)
- **Read by:** `999_finalize.py` (parents `furnitures/` under `bowling/`)
- **Depends on:** `052_bowling.py`
- **Depended on by:** runtime physics simulation

## Notable code patterns

- **Mix of `tube.NNN` and `cuboid.NNN` colliders in one collection** — Bruno uses both shapes for the variety of furniture geometries (cylindrical bottles → tubes; rectangular tables/couches → cuboids).
- **In-zone vs off-stage colliders** mixed — for some props (like the stool `cuboid.100`), the collider is at the same XY as the mesh. For most others, it's off-stage at the (-45-47, -28) cluster. This inconsistency suggests Bruno was iterating on the binding approach across the script.
- **No `bowling` prefix** on object names despite being in the bowling section — they use generic `tablePhysicalDynamic`, `couchPhysicalDynamic`, etc. This may mean the runtime treats them as generic restaurant assets, not bowling-specific.
- **Smooth-by-Angle at π/4 (45°)** on tables — sharper edge crease than the universal 55° default. Tables have visible square corners; the smoothing threshold keeps edges crisp.
- **Longest script in batch 3** — 1027 lines for 43 objects. By volume, this single script alone defines about a third of the bowling zone's visible content.
