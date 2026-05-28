# 024_bridges.py — 2 visible bridge meshes + 6 EMPTY-cube collider anchors

**Path:** `folio-2025/scripts/blender_world_steps/steps/024_bridges.py`
**Lines:** 129
**Adds:** 8 objects (2 MESH + 6 EMPTY) in collection `bridges`
**Group:** [03-surface-detail](../03-surface-detail.md)

## What it does (code-level)

Two visible bridge meshes, each surrounded by 3 EMPTY "cuboid" anchors (likely collision boxes).

### Bridge 1 (north-east area, near (47, -22))
- `bridgePhysicalFixed` — MESH using `Cube.211`, location `(47.08, -22.28, -0.12)`, rotation `(0, 0, 7.363)` rad (~+421° → ~+61° unwrapped).
- `cuboid` — EMPTY, location `(5.27, 16.46, -1.00)`, scale `(3.67, 10.30, 2.18)`, rotation Z=`1.075` rad. Big footprint cuboid.
- `cuboid.021` — EMPTY, location `(5.98, 18.44, 0.06)`, scale `(0.285, 8.60, 2.18)`. Thin rail.
- `cuboid.020` — EMPTY, location `(4.00, 14.76, 0.06)`, scale `(0.285, 8.60, 2.18)`. Thin rail.

### Bridge 2 (south area, near (23, -40))
- `bridgePhysicalFixed.001` — MESH using `Cube.156`, location `(23.40, -39.83, -0.12)`, rotation `(0, 0, 4.396)` rad (~252°).
- `cuboid.022` — EMPTY, location `(-12.74, -3.54, -1.00)`, scale `(3.67, 10.30, 2.18)`, rotation Z=`-1.892` rad. Big footprint cuboid.
- `cuboid.024` — EMPTY, location `(-13.10, -5.61, 0.06)`, scale `(0.285, 8.60, 2.18)`. Thin rail.
- `cuboid.023` — EMPTY, location `(-11.78, -1.65, 0.06)`, scale `(0.285, 8.60, 2.18)`. Thin rail.

Each bridge follows the same authoring template: **1 visible mesh + 1 big cuboid + 2 thin rails**. The big cuboid is likely the walkable deck collider; the two thin rails are side-rail colliders.

## Key data

- **Datablocks referenced**:
  - Meshes: `Cube.156`, `Cube.211` (from [005-meshes-01](../01-foundation/005-meshes-01.md) / [005-meshes-02](../01-foundation/005-meshes-02.md)).
  - No node groups, no curves.
- **Materials assigned**: `palette` via mesh material slots (set in 005, not here).
- **Modifiers added**: none.
- **Custom properties**: none on bridge objects in this script.
- **World positions of key anchors**:
  - Bridge 1 visible mesh: `(47.08, -22.28, -0.12)`
  - Bridge 1 anchors clustered around `(5, 16, 0)` — note: the anchors are far from the visible mesh! The empties are at different world positions than the meshes. This suggests the anchors are NOT bridge-foot positions for these specific bridges — they're probably the **canonical bridge collider proxies** that get RE-USED via the runtime's instance-by-name lookup or get re-translated.
  - Bridge 2 visible mesh: `(23.40, -39.83, -0.12)`
  - Bridge 2 anchors clustered around `(-12, -3, 0)` — same mismatch.
- **Object types breakdown**: 2 MESH + 6 EMPTY.
- **Parent collection**: `bridges` (child of `scenery.002`, mounted by 022).

## Technique / recipe

The "visible bridge mesh + decoupled collider empties" pattern:

- **Each bridge = 1 mesh + 3 empties**. The 3 empties together describe a flat deck + two side rails as 6-DOF cuboid colliders, but their positions are **NOT** near the bridge mesh's world position.
- **The mismatch suggests indirection**: the empties might be **collider templates** in a separate "physics-canonical" space. The runtime likely reads their scale + rotation but applies them at the corresponding bridge's mesh location (the parent transform handles it).
- **EMPTY with scale `(3.67, 10.30, 2.18)`** for the deck: a 3.67 × 10.30 × 2.18 m cuboid (since `empty_display_type='CUBE'` displays a unit cube scaled by these values, the runtime interprets the scale as collider half-extent). The deck is a long rectangular box.
- **EMPTY with scale `(0.285, 8.60, 2.18)`** for the rails: 0.29 m thin, 8.60 m long, 2.18 m tall — clearly a side-rail collider.
- **Rotation Z (yaw) values are odd**: `7.36` rad and `4.40` rad → those are >2π and indicate the rotations went around the circle multiple times during authoring (Bruno didn't normalize them when authoring). Runtime treats them mod-2π anyway.
- **`empty_display_type = 'CUBE'`** + `empty_display_size = 0.5` (Blender displays the empty as a half-meter cube wireframe in the viewport). The scale multiplies this to give the actual collider extent.
- **No mesh, no rendered geometry on empties** (`ob = bpy.data.objects.new('cuboid', None)`). They're pure transform anchors.

## Connections

- **Reads from**:
  - 005-meshes-01/02 (Cube.156, Cube.211)
  - 004-materials (palette via mesh slots)
  - 013-collections (`bridges` exists, parented to `scenery.002`)
  - 022_scenery.002.py (scenery.002 is mounted)
- **Read by**: 999_finalize (parenting).
- **Depends on**: 005, 004, 013, 022.
- **Depended on by**: 999_finalize; runtime physics that reads empties as collider proxies.

## Notable code patterns

- **3 empties per bridge** = "deck + 2 rails" pattern. Same scaling values repeat across the two bridges (within rounding error): deck `(3.67, 10.30, 2.18)`, rails `(0.285, 8.60, 2.18)`. Suggests bridges share an authoring template.
- **Anchor empties NOT collocated with visible meshes**: hints at a runtime indirection step. Either (a) the runtime parents anchors to the bridge object before applying transforms, or (b) Bruno's authoring tool exports anchors in a normalized space.
- **`palette` material** for the bridge mesh (via 005 slot) — bridges share the world's universal palette tone, not a special bridge material.
- **No physics tags as custom properties**: unlike basaltRocks' "PhysicalStatic" suffix, here the type is encoded in object name (`bridgePhysicalFixed`). "Fixed" probably means rigidbody pinned in place — distinguishes from "Static" (true static collider).
- **EMPTY-as-collider-proxy** is a recurring Bruno pattern: he uses Blender empties with `empty_display_type='CUBE'` to author physics collision boxes outside the visual mesh, then exports their transform to the runtime physics engine.
- **The script doesn't mount `bridges` to scene root** because `bridges` is already linked under `scenery.002` (in 013) and `scenery.002` is mounted by 022.
