# 056_jukebox.py — interactive musical jukebox with collider and UI anchor

**Path:** `folio-2025/scripts/blender_world_steps/steps/056_jukebox.py`
**Lines:** 92
**Adds:** 3 objects (1 MESH, 2 EMPTY) to collection `jukebox`
**Group:** [09-bowling](../09-bowling.md)

## What it does (code-level)

Creates `jukebox` collection. Adds 3 objects:

| Object | Type | Mesh | Location | Notes |
|---|---|---|---|---|
| `refJukeboxPhysicalDynamic` | MESH | `Plane.143` | (24.01, -55.10, 1.45) | rotZ=0.175 (≈10°), `mass=5.0`, `Smooth by Angle.003` GN (Input_1=1.134 rad ≈65°) |
| `cuboid.112` | EMPTY/CUBE | — | (-25.27, -26.54, 1.68) | Off-stage collider, scale (2.67, 1.85, 3.36) — large jukebox box collider |
| `refJukeboxInteractivePoint` | EMPTY/PLAIN_AXES | — | (24.30, -56.66, 1.50) | "Press E to play music" UI hotspot, right next to the jukebox |

## Key data

- **Datablocks referenced:** mesh `Plane.143`, node-group `Smooth by Angle.003`
- **Materials assigned:** via mesh datablock — `emissiveOrangeRadialGradient`, `emissivePurpleRadialGradient`, `palette` (per group .md) — orange/purple arcade glow
- **Modifiers added:** 1× `Smooth by Angle.003` (NODES, Input_1=1.134 rad ≈65° — softer than the usual 55° for a more rounded jukebox shape)
- **Custom properties:** `mass=5.0` on the jukebox mesh — heaviest physics-dynamic object in the bowling zone (5× the barrels' mass)
- **World positions of key anchors:**
  - Jukebox at (24.01, -55.10, 1.45) — rotated 10° around Z, slightly off the lane axis
  - Off-stage collider at (-25.27, -26.54) — runtime-bound to jukebox
  - Interactive point at (24.30, -56.66, 1.5) — 1.5m offset from jukebox center, where the player stands to interact
- **Object types breakdown:** 1 MESH, 2 EMPTY
- **Parent collection:** `jukebox` (re-parented under `bowling/` by finalize)

## Technique / recipe

**Three-object interactive prop pattern:**
1. **Visible mesh** — the jukebox itself
2. **Collider primitive** off-stage — runtime binds to the mesh
3. **Interactive point** at the player-standing position — UI prompt anchor

**`mass=5.0`** is significantly heavier than barrels (1.0), couches (0.35), sauces (0.05). The jukebox is heavy enough to barely move when bumped (gives a "this is a permanent fixture" feel) but still movable.

**Smooth-by-Angle threshold 65°** (vs the universal 55° default) — softens the jukebox's curved edges. Bruno's per-prop tuning of smoothing creates visual variety.

**Rotation 0.175 rad (10°)** — gives the jukebox a slight angle (not facing perfectly head-on to the camera/player). Adds visual interest.

**Collider scale (2.67, 1.85, 3.36)** — the jukebox's hitbox: 2.67m wide × 1.85m deep × 3.36m tall. Roughly matches a vintage jukebox cabinet.

## Connections

- **Reads from:** `005_meshes_*.py` (`Plane.143`), `003_node_groups.py` (`Smooth by Angle.003`)
- **Read by:** `999_finalize.py` (parents `jukebox/` under `bowling/`)
- **Depends on:** `052_bowling.py`
- **Depended on by:** runtime music-player system, interaction system

## Notable code patterns

- **Mesh from `Plane.143` datablock** — the jukebox is built from a single Plane-source mesh (low-poly, billboard-style geometry probably with painted-on details from the texture).
- **`refJukeboxInteractivePoint`** without an `.NNN` suffix — Bruno only suffixes when there are multiple of the same kind. Since there's exactly one jukebox, no suffix.
- **Three emissive materials** (orange + purple + palette) — the most colorful single-prop in the bowling zone. Arcade aesthetic.
- **mass=5.0** is the heaviest dynamic object in batch 3 — gives the jukebox a "permanent landmark" feel despite being technically physics-active.
