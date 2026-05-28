# 095_blackBoard.002.py — projects-zone chalkboard (template-twin of 082)

**Path:** `folio-2025/scripts/blender_world_steps/steps/095_blackBoard.002.py`
**Lines:** 121
**Adds:** 8 objects (4 MESH, 4 EMPTY) to collection `blackBoard.002`
**Group:** [11-furniture-displays-boards](../11-furniture-displays-boards.md)

## What it does (code-level)

Creates `blackBoard.002` collection — the **projects-section's chalkboard**. Structural mirror of `082_blackBoard.001.py`:

| Object | Type | Mesh | Location | Notes |
|---|---|---|---|---|
| `refBlackBoard.002` | EMPTY/PLAIN_AXES | — | (-46.44, 14.93, 0.006) | **Same staging position as `refBlackBoard.001` in 082** |
| `cuboid.057` | EMPTY/CUBE | — | (-7.73, 24.86, 0.891) | A-frame leg #1, rotY=-0.258 (-15°), rotZ=3.141 (180°), scale (0.196, 1.349, 1.798) |
| `cuboid.058` | EMPTY/CUBE | — | (-7.16, 24.86, 0.891) | A-frame leg #2, rotY=+0.260 (+15°), rotZ=3.141, scale (0.196, 1.349, 1.798) — **mirror of cuboid.057** |
| `blackBoardPhysicalDynamic` | EMPTY/PLAIN_AXES | — | (31.64, -12.39, 0.006) | Physics-dynamic anchor at staging |
| `Cube.082` | MESH | `Cube.182` | (-29.92, 19.77, 0.967) | The visible blackboard mesh. rotY=-0.262 (-15° tilt) — same lean as 082 |
| `refBlackboardLabelsGamepadPlaystation` | MESH | `Plane.127` | (-29.85, 19.77, 0.956) | PS gamepad labels |
| `refBlackboardLabelsMouseKeyboard.001` | MESH | `Plane.128` | (-29.86, 19.81, 0.977) | Mouse+Keyboard labels |
| `refBlackboardLabelsGamepadXbox` | MESH | `Plane.109` | (-29.85, 19.77, 0.956) | Xbox gamepad labels |

## Key data

- **Datablocks referenced:** mesh `Cube.182` (blackboard body — **DIFFERENT mesh from `Cube.112` in 082**, suggesting the projects board has different baked content), labels `Plane.127`, `Plane.128`, `Plane.109` (different from 082's `Plane.113`, `Plane.126`, `Plane.091`)
- **Materials assigned:** `blackboardLabels`, `palette`
- **Modifiers added:** none
- **Custom properties:** none
- **World positions of key anchors:**
  - Blackboard mesh at (-29.92, 19.77, 0.967) — projects zone (note: this is INSIDE the projects zone area, near the projects' main interactive cluster)
  - A-frame legs at (-7.73, 24.86) and (-7.16, 24.86) — at projects' staging area (different from 082's lab staging)
  - Physics-dynamic anchor at (31.64, -12.39) — different from 082's (8.99, -17.58)
  - Labels at staging (-29.85, 19.77 / 19.81) — co-located in projects area
- **Object types breakdown:** 4 MESH, 4 EMPTY
- **Parent collection:** `blackBoard.002` (re-parented under `projects/` by finalize)

## Technique / recipe

**Direct structural twin of `082_blackBoard.001.py` — same recipe, different placement and content:**

1. **Same 8-object structure:** 1 ref anchor + 2 mirror collider legs + 1 physics anchor + 1 visible board mesh + 3 stacked input-device labels.
2. **Different mesh datablocks:** `Cube.182` (vs `Cube.112` in 082) for the body, `Plane.127/.128/.109` (vs `Plane.113/.126/.091` in 082) for the labels. Bruno baked **different content per blackboard** — the projects chalkboard shows different controls or annotations than the lab one.
3. **Same rotation/tilt** (-15° rotY on the board) — visual consistency between the two chalkboards.
4. **Same A-frame collider trick** (two mirror-rotated CUBE empties) — Bruno's reusable collision pattern.
5. **Same input-device-swap labels** — 3 stacked at the same XY, ready for runtime to pick the right one based on detected device.

**The two blackboards (082 in lab, 095 in projects) are intentional twins.** Bruno builds **paired sister-screens** across zones — both rooms have a chalkboard with control hints, but with content tailored to that room's interactive props.

**`refBlackBoard.002` at the same staging position** (-46.44, 14.93) **as `refBlackBoard.001`** — both anchor empties literally overlap in the .blend. They're distinguished by name, not position. Runtime reads them by name suffix.

## Connections

- **Reads from:** `005_meshes_*.py` (`Cube.182`, `Plane.127/.128/.109`)
- **Read by:** `999_finalize.py` (parents `blackBoard.002/` under `projects/`)
- **Depends on:** `093_projects.py` (projects parent zone)
- **Depended on by:** runtime input-device detection, physics system

## Notable code patterns

- **Pure template duplication** — 082 and 095 are nearly line-for-line identical, only object names, mesh datablock IDs, and a few collider positions differ. Bruno's template-reuse approach for paired props.
- **Same staging position** for two different ref anchors (082's `refBlackBoard.001` and 095's `refBlackBoard.002`) — naming distinguishes them; physically they overlap. The runtime never confuses them because it looks up by name.
- **Different mesh data per twin** — `Cube.112` (lab) vs `Cube.182` (projects). Both blackboards are visually the same shape but carry different surface content (different chalkboard equations / diagrams baked in).
- **`.001` and `.002` suffix convention** — sister-objects get incremented suffixes. The same convention applies to `mainTable` (085) and `mainTable.001` (099).
- **A-frame legs at DIFFERENT staging** — 082's legs at (-30.37, 19.67); 095's legs at (-7.73, 24.86). Bruno didn't reuse the staging position even though the collider scale is identical. Suggests staging positions are local to each prop's instance, not globally shared.
- **`refBlackboardLabelsMouseKeyboard.001`** has the `.001` suffix only on the MK variant — not on PS/Xbox. Bruno's suffix discipline is inconsistent.
