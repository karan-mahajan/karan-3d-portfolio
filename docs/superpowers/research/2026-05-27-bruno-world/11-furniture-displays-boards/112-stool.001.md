# 112_stool.001.py — single timeMachine stool with one tube-shaped collider

**Path:** `folio-2025/scripts/blender_world_steps/steps/112_stool.001.py`
**Lines:** 37
**Adds:** 2 objects (1 MESH, 1 EMPTY) to collection `stool.001`
**Group:** [11-furniture-displays-boards](../11-furniture-displays-boards.md)

## What it does (code-level)

Creates `stool.001` collection. Adds 2 objects:

| Object | Type | Mesh | Location | Notes |
|---|---|---|---|---|
| `stoolPhysicalDynamic.004` | MESH | `Cylinder.017` | (-54.52, 65.54, 1.037) | The visible stool mesh. rotX=-0.104, rotY=0.025, rotZ=0.751 (≈43°) |
| `cuboid.219` | EMPTY/CUBE | — | (-54.52, 65.54, 0.550) | Collider directly below stool (same XY), scale (1.0, 1.0, 1.148). z=0.550 is at the stool's mid-height |

## Key data

- **Datablocks referenced:** mesh `Cylinder.017`
- **Materials assigned:** `palette` (per group .md)
- **Modifiers added:** none
- **Custom properties:** none
- **World positions of key anchors:**
  - Stool at (-54.52, 65.54, 1.037) — timeMachine zone, near the PlayStation prop
  - Collider directly under stool — XY identical, z=0.550 (between ground and stool top)
- **Object types breakdown:** 1 MESH, 1 EMPTY
- **Parent collection:** `stool.001` (re-parented under `timeMachine/` by finalize)

## Technique / recipe

**Minimal stool prop — 1 mesh + 1 collider:**

1. **Cylinder mesh** (`Cylinder.017`) — a stylized stool, rotated 43° around Z (visual variety).
2. **One CUBE collider** at the same XY as the stool, at the stool's mid-height. Half-extents (1.0, 1.0, 1.148) — covers approximately the stool's full body.

**`PhysicalDynamic.004` suffix** — the .004 is a global Blender name-collision counter (other stools elsewhere use .001-.003). The stool is dynamic (pushable by the player).

**Companion to `stool` (116, in the toilet)** — both stools are simple cylinder meshes with one cube collider, just placed in different zones. This is the **template** for stool props throughout the world.

**Slight rotation on multiple axes** (rotX=-0.104, rotY=0.025) — Bruno gives the stool a subtle "wobble" tilt instead of perfectly axis-aligned. Adds visual liveliness.

**Co-located collider** (same XY as the stool) — Bruno places the collider at the actual world position, not at a staging area. Unusual for batch 4 — most props use staging. Possibly because this stool is so simple it doesn't need template-stack.

## Connections

- **Reads from:** `005_meshes_*.py` (`Cylinder.017`)
- **Read by:** `999_finalize.py` (parents `stool.001/` under `timeMachine/`)
- **Depends on:** `108_timeMachine.py` (parent zone)
- **Depended on by:** physics system (dynamic body)

## Notable code patterns

- **Smallest furniture script in batch 4** (37 lines, 2 objects).
- **`PhysicalDynamic.004`** — the suffix indicates Bruno had 4+ prior PhysicalDynamic objects with the same base name. Naming collisions are resolved by Blender's auto-numbering.
- **Collider at the actual world position** (not staging) — the .NNN-suffixed cuboid is co-located with the mesh, unlike most props that have colliders at staging coordinates. The simplest possible collider setup.
- **Twin of 116_stool.py** — both stool scripts use the same pattern, with 116 having more variation (4 stools + 3 paper rolls).
- **`Cylinder.017`** — Bruno's library has many Cylinder.NNN meshes; this is the 17th. Likely shares geometry with similar cylindrical props elsewhere.
- **rotZ=0.751** (43°) — gives the stool a non-axis-aligned look despite the cylinder's rotational symmetry. Probably affects the wood-grain texture orientation.
