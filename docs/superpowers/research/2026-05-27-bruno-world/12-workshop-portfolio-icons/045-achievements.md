# 045_achievements.py — achievement-zone interaction point, 16 cuboid platforms, and zone bounds

**Path:** `folio-2025/scripts/blender_world_steps/steps/045_achievements.py`
**Lines:** 377
**Adds:** 23 objects (1 MESH, 22 EMPTY) to collection `achievements`
**Group:** [12-workshop-portfolio-icons](../12-workshop-portfolio-icons.md)

## What it does (code-level)

Creates `achievements` collection. Adds a centerpiece visible mesh (`hull.004`) plus 22 EMPTYs forming a complete zone definition with platforms, bounds, and interactivity hooks.

**Anchor structure:**

| Object | Type | Notes |
|---|---|---|
| `refInteractivePoint.005` | EMPTY/PLAIN_AXES at (69.66, -16.93, 1.749) | "Press E" interaction hotspot |
| `refZoneBounding.011` | EMPTY/CIRCLE at (70.77, -9.63, 3.27) | scale 10.08 — **circular zone boundary** (10m radius) marking the achievement zone |
| `refZoneFrustum.011` | EMPTY (CIRCLE) | Camera-frustum culling region for the achievement zone |
| `physicalFixed.008` | EMPTY/PLAIN_AXES at (69.66, -12.41, 0.0) | `category='floor'` custom prop — anchors the floor physics surface |
| `refWaterfallZone` | EMPTY | Marks a waterfall effect zone within achievements |
| `achievements` | EMPTY/PLAIN_AXES | The zone's root parent empty |
| `hull.004` | MESH | The visible hull/building mesh (the achievement building centerpiece) |

**Collider platforms (16× `cuboid.NNN` EMPTY/CUBE):**

| Range | Notes |
|---|---|
| `cuboid.201` | (69.66, -12.41, 0.592), scale (2.0, 2.0, 1.12) — lower floor platform |
| `cuboid.202` | (69.66, -12.41, 2.90), scale (1.31, 1.31, 3.62) — tall thin upper element |
| `cuboid.203` | (69.66, -11.93, 0.110), scale (7.04, 4.92, 0.18) — wide flat floor #1 |
| `cuboid.204` | (67.54, -14.37, 0.110), rotZ=0.785 (45°), scale (1.95, 1.95, 0.18) — corner ramp #1 |
| `cuboid.205` | (71.79, -14.37, 0.110), rotZ=0.785, scale (1.95, 1.95, 0.18) — corner ramp #2 (mirror) |
| `cuboid.206` | (69.66, -9.71, 0.110), scale (4.23, 12.07, 0.18) — large floor extension (north strip) |
| `.207-.216` | various positions — additional floor/wall pieces forming the zone's walkable layout |

## Key data

- **Datablocks referenced:** mesh `hull.004` (which references some Cube.NNN datablock)
- **Materials assigned:** `palette` (the hull) — no materials on EMPTYs
- **Modifiers added:** none
- **Custom properties:** `category='floor'` on `physicalFixed.008`
- **World positions of key anchors:**
  - Achievement zone center at (69.66, -12.41, 0.0)
  - Zone bounds circle at (70.77, -9.63, 3.27) with 10.08m radius
  - Interactive point at (69.66, -16.93, 1.749) — south side of zone
- **Object types breakdown:** 1 MESH, 22 EMPTY
- **Parent collection:** `achievements` (NOT zone-parented under `areas/`; achievements is its OWN parent containing `archive.001` and `building`)

## Technique / recipe

**Full-zone definition pattern — boundary + platform colliders + interactive hooks:**

1. **Zone boundary** via `refZoneBounding.011` (CIRCLE empty, scale=10.08) — runtime uses this to test "is the player in the achievement zone?" via radius check.
2. **Camera frustum region** via `refZoneFrustum.011` — runtime uses this for frustum-culling and "what to draw when player is in this zone."
3. **Physics floor anchor** via `physicalFixed.008` with `category='floor'` — runtime creates a fixed/static collider here with the floor classification. The `category` custom prop is the runtime contract.
4. **16 cuboid collider platforms** forming the walkable surface — floor pieces (.203, .206), corner ramps (.204, .205 mirrored), tall blocks (.202), and various flooring extensions. Together they sculpt the achievement zone's terrain.
5. **One visible MESH** (`hull.004`) — the achievement building centerpiece. Single mesh for the whole structure.
6. **Interactive point** at (69.66, -16.93, 1.749) — chest-height UI prompt anchor at the south entrance.
7. **`refWaterfallZone`** — marks a sub-region within achievements for waterfall effect spawning.

**`category='floor'`** — first appearance in batch 4 of the `category` custom prop. It's runtime's way of classifying physics colliders into types (floor / wall / ramp / decorative). The runtime applies appropriate physics responses based on category.

**Achievement zone is parented at the TOP level** — the `achievements` empty is NOT under `areas/`. It contains `archive.001` (a curve) and `building` (the centerpiece). This is the achievement-as-collectible-system: a dedicated top-level branch.

**16 platform colliders** is a LOT for one zone. The achievement zone has a complex walkable surface — likely multi-level (lower floor + upper element + ramps + extensions).

## Connections

- **Reads from:** `005_meshes_*.py` (hull mesh data)
- **Read by:** `999_finalize.py` (parents `archive.001` + `building` under `achievements`)
- **Depends on:** `013_collections.py` (collection skeleton)
- **Depended on by:** runtime achievement system, waterfall effect spawning, frustum-culling

## Notable code patterns

- **`category` custom prop** — runtime contract for physics classification. First appearance in batch 4.
- **CIRCLE-typed EMPTYs for zone bounds + frustum regions** — Bruno uses `empty_display_type='CIRCLE'` to represent 2D radial bounds. The scale property is the radius.
- **Single visible MESH (`hull.004`) for the entire zone's geometry** — the achievement building is one mesh, no template-stack here.
- **22 EMPTYs to 1 MESH ratio** — extreme. Achievement zones are mostly "physics + game-logic markers" rather than visual props.
- **`refZoneBounding.011` and `refZoneFrustum.011`** both at index `.011` — Bruno has 11 zones with matching bounds+frustum pairs across the world.
- **Naming pattern: `cuboid.201` through `cuboid.216`** — sequential numbering. Easy for the artist to add/remove platforms.
- **`physicalFixed.008` suffix** — there are 8+ other physicalFixed.NNN objects elsewhere (e.g., 093's physicalFixed.001, 103's physicalFixed.002). Global counter.
- **Achievement zone is BIG** (10m radius bounding) — one of the larger zones in the world. Bruno gave it room.
- **No `mass` props** — all colliders are static. The achievement zone is for player traversal, not for physics-active props.
