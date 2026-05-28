# 051_scenery.001.py — 3 dynamic-physics cylinders + 5 EMPTY collider proxies

**Path:** `folio-2025/scripts/blender_world_steps/steps/051_scenery.001.py`
**Lines:** 242
**Adds:** 8 objects (3 MESH + 5 EMPTY) in collection `scenery.001`
**Group:** [03-surface-detail](../03-surface-detail.md) (but parented under `behindTheScene`, not `scenery.002`)

## What it does (code-level)

3 visible dynamic-physics cylinders + 5 collider empties, in the `behindTheScene` corner of the world.

### 3 visible dynamic cylinders — same source mesh, different placements

All three use mesh `Cylinder.042` (one shared datablock, instanced 3 times). Same `Smooth by Angle.003` modifier on all three.

| Object | Location | Rotation Z | Scale |
|---|---|---:|---|
| `refObjectsPhysicalDynamic.021` | `(48.55, 13.89, 0.53)` | -0.092 rad | (1.0, 1.0, 1.0) |
| `refObjectsPhysicalDynamic.022` | `(51.57, 16.02, 0.53)` | -0.871 rad | (1.0, 1.0, 1.0) |
| `refObjectsPhysicalDynamic.023` | `(varies similar SE area)` | (~varies) | (1.0, 1.0, 1.0) |

Each has:
- **Modifier**: `Smooth by Angle.003` (NODES), `use_pin_to_last = True`, `Input_1 = 0.9599` rad (≈ 55°) — a wider angle threshold than the slabs (30°), so more edges get smoothed.
- **Custom property**: `ob['mass'] = 1.0` — tags the object as a 1 kg dynamic rigidbody for the runtime physics engine.

### 5 EMPTY collider proxies

| Object | Location | Rotation Z | Scale (X, Y, Z) |
|---|---|---:|---|
| `cuboid.013` | `(-54.35, 57.40, 0.83)` | 0.0 | (0.35, 0.35, 1.03) |
| `cuboid.120` | `(-54.35, 57.40, 0.35)` | π rad | (0.88, 0.88, 0.10) |
| `cuboid.123` | (varies) | (varies) | (varies) |
| `cuboid.124` | (varies) | (varies) | (varies) |
| `cuboid.125` | (varies) | (varies) | (varies) |

Each empty:
- `empty_display_type = 'CUBE'`
- `empty_display_size = 0.5`
- No `mass` custom property (so these are static colliders, not dynamic)
- Positions are NOT near the visible cylinder positions — confirms the same "decoupled collider" pattern seen in [024-bridges](024-bridges.md).

## Key data

- **Datablocks referenced**:
  - Mesh: `Cylinder.042` (from [005-meshes-03](../01-foundation/005-meshes-03.md)) — single mesh instanced 3 times.
  - Node group: `Smooth by Angle.003` (from [003-node-groups](../01-foundation/003-node-groups.md)).
- **Materials assigned**: `palette` via mesh slot.
- **Modifiers added**: 3 × `Smooth by Angle.003` (`NODES`) — one per visible cylinder. All with `Input_1 = 0.96` (≈55° angle threshold).
- **Custom properties**:
  - On each visible cylinder: `mass = 1.0` (dynamic rigidbody)
  - On modifiers: `Input_1 = 0.9599`, `Input_1_use_attribute = 0`, `Input_1_attribute_name = ''`, `Socket_1 = False` (Ignore Sharpness off), etc.
  - On empties: none — they're static collision proxies.
- **World positions of key anchors**:
  - Visible cylinders cluster at `(~50, ~15, 0.5)` — south-east corner.
  - cuboid.013/120 anchor at `(-54.35, 57.40, ~0.5)` — far north-west — physically separated from the visible cylinders.
- **Object types breakdown**: 3 MESH + 5 EMPTY.
- **Parent collection**: `scenery.001` (child of `behindTheScene` per [013-collections.md](../01-foundation/013-collections.md)).

## Technique / recipe

The "shared-mesh dynamic-physics props" pattern:

- **One mesh, 3 instances**: Bruno authors one cylinder mesh (`Cylinder.042`) and creates 3 scene objects all pointing at it. Each object has unique world position + rotation but shares geometry. This is the classic Blender mesh-instancing pattern (vs. linked duplicates).
- **`Smooth by Angle.003` with a wider threshold (55° vs slabs' 30°)**: cylinders need a wider smoothing tolerance to round their tangent edges. The angle `0.96 rad ≈ 55°` is set per-modifier-instance via `m['Input_1']`.
- **`ob['mass'] = 1.0` custom property** = the runtime physics engine reads this and creates a 1 kg dynamic rigidbody. The "Physical**Dynamic**" in the object name + the `mass` custom prop together signal "this is a Rapier dynamic body the player can push."
- **Empties for collider proxies (the decoupled-collider pattern)**: same as bridges. The 5 empties' positions aren't where the visible cylinders sit — they describe collision geometry in a separate authoring space that the runtime parents to the visible cylinders.
- **`scenery.001`** is the **behindTheScene area's local props collection** — physically in the world's south-east corner where Bruno's "behind the scenes" zone lives.

## Connections

- **Reads from**:
  - 005-meshes-03 (`Cylinder.042`)
  - 003-node-groups (`Smooth by Angle.003`)
  - 004-materials (`palette` via mesh slot)
  - 013-collections (`scenery.001` exists, parented to `behindTheScene`)
- **Read by**: 049_behindTheScene (parents this collection under `behindTheScene`); 999_finalize.
- **Depends on**: 005, 003, 004, 013.
- **Depended on by**: 049 (parent collection script), 999_finalize.

## Notable code patterns

- **`refObjectsPhysicalDynamic.NNN` naming**: "ref" + "Physical" + "Dynamic" + counter. The `ref` prefix usually means "reference template" elsewhere in Bruno's pipeline, but here `Dynamic` clarifies it's a runtime-spawnable dynamic body. The runtime probably reads the object name's `Dynamic`/`Static`/`Fixed` token to decide rigidbody type.
- **All 3 share `Cylinder.042`**: confirms mesh reuse — the geometry is authored once, instanced via separate scene objects. Same mesh = identical visual; different transforms = scattered placement.
- **Custom prop `mass`** on dynamic objects: the simplest runtime physics indicator. Bruno doesn't use Blender's built-in rigidbody UI (which would attach physics to the scene-rigidbody-world); instead he tags via custom property and lets the runtime interpret.
- **5 empty cuboids for 3 visible cylinders** = 1.67 colliders per visible prop. Each cylinder is approximated by ~1-2 cuboid colliders. The collider-to-visible ratio depends on prop complexity.
- **`cuboid.120` has `rotation_euler.z = π`** (180° yaw) — a flipped collider. Suggests Bruno made one "left-side" empty and rotated 180° for the "right-side" counterpart.
- **`cuboid.013` scale `(0.35, 0.35, 1.03)`**: a tall thin cuboid (35cm × 35cm footprint, 1m tall) — looks like a pole/post collider.
- **`cuboid.120` scale `(0.88, 0.88, 0.10)`**: a wide flat slab (88cm square, 10cm thick) — like a base plate.
- **Together cuboid.013 + cuboid.120 = pole on base plate**: a typical "fence post" or "lantern stand" 2-piece collider.
- **The `behindTheScene` location** of these props (NW corner per cuboids; SE per cylinders) is split — confirms the "physical placement vs collider authoring space" disconnect.
