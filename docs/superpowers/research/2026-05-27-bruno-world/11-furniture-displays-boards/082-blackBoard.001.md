# 082_blackBoard.001.py — lab chalkboard with 3 swappable input-device label meshes

**Path:** `folio-2025/scripts/blender_world_steps/steps/082_blackBoard.001.py`
**Lines:** 121
**Adds:** 8 objects (4 MESH, 4 EMPTY) to collection `blackBoard.001`
**Group:** [11-furniture-displays-boards](../11-furniture-displays-boards.md)

## What it does (code-level)

Creates `blackBoard.001` collection (the lab's chalkboard with control-scheme labels):

| Object | Type | Mesh | Location | Notes |
|---|---|---|---|---|
| `refBlackBoard.001` | EMPTY/PLAIN_AXES | — | (-46.44, 14.93, 0.006) | "Ref" anchor at staging position for labels |
| `Cube.100` | MESH | `Cube.112` | (-29.91, 20.00, 0.967) | **The visible blackboard mesh** — rotY=-0.262 (-15° tilt) — leaned-back like a real chalkboard |
| `cuboid.064` | EMPTY/CUBE | — | (-30.37, 19.67, 0.891) | Collider, rotY=-0.258 (-15°), rotZ=3.141 (180°), scale (0.196, 1.349, 1.798) — one of the two slanted board legs |
| `cuboid.065` | EMPTY/CUBE | — | (-29.81, 19.67, 0.891) | Collider, rotY=0.260 (+15°), rotZ=3.141, scale (0.196, 1.349, 1.798) — the **mirror** of cuboid.064, forming an A-frame stand |
| `blackBoardPhysicalDynamic.001` | EMPTY/PLAIN_AXES | — | (8.99, -17.58, 0.006) | Physics-dynamic anchor — runtime creates a dynamic rigid body here |
| `refBlackboardLabelsGamepadPlaystation.001` | MESH | `Plane.113` | (-46.10, 14.92, 1.011) | PlayStation gamepad labels (X/circle/square/triangle) |
| `refBlackboardLabelsMouseKeyboard` | MESH | `Plane.126` | (-46.09, 14.97, 0.985) | Mouse + keyboard labels (WASD, etc.) |
| `refBlackboardLabelsGamepadXbox.001` | MESH | `Plane.091` | (-46.10, 14.92, 1.011) | Xbox gamepad labels (A/B/X/Y) |

The 3 label meshes are **co-located at the staging position** (-46.10, 14.92), all rotated identically (rotX=1.309 ≈75°, rotZ=1.571 ≈90°), scaled to 0.870. They stack precisely on top of each other.

## Key data

- **Datablocks referenced:** mesh `Cube.112` (blackboard body), `Plane.113`/`126`/`091` (3 label texture sheets)
- **Materials assigned:** `blackboardLabels` (on the labels), `palette` (on the board body)
- **Modifiers added:** none
- **Custom properties:** none on any object
- **World positions of key anchors:**
  - Blackboard mesh: (-29.91, 20.00, 0.967) — visible in lab zone
  - A-frame collider legs at (-30.37 / -29.81, 19.67) — close to mesh, real-world position
  - Ref anchor + 3 labels: at staging (-46.44 / -46.10, 14.93/14.92) — for runtime relocation
  - Physics-dynamic anchor: yet another position at (8.99, -17.58)
- **Object types breakdown:** 4 MESH, 4 EMPTY
- **Parent collection:** `blackBoard.001` (re-parented under `lab/` by finalize)

## Technique / recipe

**Bruno's input-device-swap pattern:**

1. **One visible blackboard mesh** (`Cube.100` ref → `Cube.112`) at the actual lab placement position, tilted 15° around Y to match a real chalkboard's lean.
2. **Two collider cubes** forming an A-frame stand — one rotated +15° around Y, the other -15° (with both flipped 180° around Z) — together they sketch the V-shaped legs of the stand.
3. **Three different label meshes** (PS gamepad / Mouse+Keyboard / Xbox gamepad) all **stacked at the same staging position**. The runtime hides 2 and shows the 1 matching the player's detected input device. This is **input-device-aware UI baked into the .blend**.
4. **Multiple ref anchors** for different runtime subsystems:
   - `refBlackBoard.001`: labels alignment anchor
   - `blackBoardPhysicalDynamic.001`: physics body anchor
   - The visible mesh and collider colliders at the actual lab position

**Mirror-pair collider legs** (cuboid.064 + .065) — the A-frame stand is achieved via two CUBE empties with mirrored rotY angles. This gives the player physical collision around the chalkboard legs without modeling them in mesh data.

**3 label meshes share material `blackboardLabels`** but reference 3 different mesh datablocks — each carries a different texture (PS / KB / Xbox). The runtime swaps mesh visibility based on the detected input device (gamepad detection on game start, or hot-swap if the player switches mid-session).

**Why so many anchors?** Bruno's runtime has multiple subsystems that each need their own placement reference:
- Labels system: where to display the input-device labels
- Physics system: where the dynamic body lives
- Render system: where the visible mesh sits
- A single object can't carry all 3 roles cleanly, hence the multi-anchor pattern.

## Connections

- **Reads from:** `005_meshes_*.py` (`Cube.112`, `Plane.113`, `Plane.126`, `Plane.091`), `004_materials.py` (`blackboardLabels`)
- **Read by:** `999_finalize.py` (parents `blackBoard.001/` under `lab/`)
- **Depends on:** `081_lab.py` (parent zone)
- **Depended on by:** runtime input-device detection system, physics system

## Notable code patterns

- **Input-device-aware UI baked into the .blend** — 3 label meshes for 3 device types, all stacked. The .blend is "ready" for any device; runtime picks one.
- **A-frame collider via 2 mirrored CUBE empties** — clever way to model a physical stand without mesh geometry. Both cuboids identical in scale (0.196 × 1.349 × 1.798) but mirror-rotated.
- **Multiple ref anchors per object** — `refBlackBoard.001` (label anchor) + `blackBoardPhysicalDynamic.001` (physics anchor) + the visible mesh. 3 anchors for one physical object.
- **`.001` suffix on the collection name** — the lab's chalkboard is `blackBoard.001`; the projects-section's chalkboard is `blackBoard.002` (095). Same template, different instances.
- **Co-located stacked labels** at exactly (-46.10, 14.92, 1.011) for PS and Xbox; the Mouse+Keyboard label at very slightly different z=0.985. Tiny variation may be intentional for the runtime to z-test which is visible without z-fighting.
