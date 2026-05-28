# 111_playstation.py — retro PlayStation console with mirror + smoothing modifiers

**Path:** `folio-2025/scripts/blender_world_steps/steps/111_playstation.py`
**Lines:** 166
**Adds:** 4 objects (4 MESH) to collection `playstation`
**Group:** [11-furniture-displays-boards](../11-furniture-displays-boards.md)

## What it does (code-level)

Creates `playstation` collection. Adds 4 MESH objects (no empties — pure visual prop):

| Object | Type | Mesh | Location | Modifiers |
|---|---|---|---|---|
| `Cube.006` | MESH | `Cube.010` | (-54.51, 67.59, 0.148) | scale=1.182 uniform. `Smooth by Angle` (base variant, Input_1=0.848 rad ≈49°) |
| `Cylinder` | MESH | `Cylinder` | (-53.63, 67.48, 0.194) | rotX=-0.205, rotY=0.485, rotZ=-0.397, scale=0.857. **`MIRROR` modifier (X-axis)** + `Smooth by Angle` (Input_1=0.960 rad ≈55°) |
| `Cube.007` | MESH | `Cube.013` | (-55.05, 67.08, 0.277) | uniform scale 1.0 |
| `Plane.005` | MESH | `Plane.062` | (-54.72, 66.89, 0.059) | uniform scale 1.0 |

All 4 meshes cluster around (-54.5 to -55.0, 66.9 to 67.6, 0.06-0.28) — a ~0.6m × 0.7m × 0.22m volume. This is in the **far north-west** (the timeMachine zone area).

## Key data

- **Datablocks referenced:** meshes `Cube.010` (PS body), `Cylinder` (the controller cable/joysticks), `Cube.013` (front panel), `Plane.062` (logo/screen); node-group `Smooth by Angle` (base variant, NOT .001/.002/.003)
- **Materials assigned:** `emissiveGreenRadialGradient` (LED), `palette` (per group .md). **The ONLY use of green-emissive in batch 4** — the PS power LED.
- **Modifiers added:** 1× MIRROR (on Cylinder, X-axis mirror with `use_clip=True`, `use_mirror_merge=True`), 2× `Smooth by Angle` (on Cube.006 and Cylinder)
- **Custom properties:** none
- **World positions of key anchors:**
  - PS body at (-54.51, 67.59, 0.148) — timeMachine zone
  - Cylinder mirrored across X — produces 2 cylinders (likely the dual joystick stems or a single mirrored shape)
  - Plane.005 at z=0.059 — almost ground-level (logo/decal on the floor?)
- **Object types breakdown:** 4 MESH (no EMPTY)
- **Parent collection:** `playstation` (re-parented under `timeMachine/` by finalize)

## Technique / recipe

**A retro PlayStation console as a clustered 4-mesh prop:**

1. **Main body** (`Cube.006`/`Cube.010`) — the PS unit's main rectangular case, smoothed at 49°.
2. **Mirrored cylinder** (`Cylinder`) — has a MIRROR modifier on the X-axis (`use_axis=(True, False, False)`), meaning Bruno modeled ONE side of a symmetric feature (likely a joystick stem or controller cable curve) and let Blender generate the other side. `use_mirror_merge=True` welds the mirror seam.
3. **Front panel** (`Cube.007`/`Cube.013`) — slightly elevated (z=0.277, +0.13m above the main body) — the disc tray or top cover.
4. **Decal plane** (`Plane.005`/`Plane.062`) — flat at z=0.059, just above ground/console-base — probably a brand decal or screen-glow plane.

**MIRROR modifier** — first appearance in batch 4 of a `MIRROR` modifier. Bruno uses it to model bilaterally-symmetric features more efficiently:
- Author one side
- MIRROR (X-axis) generates the other side
- `use_clip=True` welds mid-line vertices
- `use_mirror_merge=True` with `merge_threshold=0.001` collapses overlapping verts at the seam

**`Smooth by Angle` (no suffix variant)** — Bruno uses the BASE smoothing node-group here, not `.001/.002/.003`. Different threshold (Input_1 varies: 0.848 on cube, 0.960 on cylinder). The base variant has unique panel settings (`show_manage_panel=False`).

**No EMPTYs** — the PS is purely visual. No physics-dynamic anchor, no interaction prompt, no collider. The player can't interact with it (it's an environment-only retro decoration).

**Cylinder's complex rotation** (rotX=-0.205, rotY=0.485, rotZ=-0.397) — Bruno tweaked all 3 axes by eye to angle the cylinder naturally (drooping cord or angled stick).

## Connections

- **Reads from:** `005_meshes_*.py` (`Cube.010`, `Cylinder`, `Cube.013`, `Plane.062`), `003_node_groups.py` (`Smooth by Angle`)
- **Read by:** `999_finalize.py` (parents `playstation/` under `timeMachine/`)
- **Depends on:** `108_timeMachine.py` (parent zone)
- **Depended on by:** none

## Notable code patterns

- **First MIRROR modifier in batch 4** — Bruno's bilateral-symmetry shortcut. `use_axis=(True, False, False)` mirrors across X only.
- **Uses base `Smooth by Angle` (unsuffixed)** — different node-group than the typical `.001/.002/.003` variants. Bruno has 4 smoothing variants in 003_node_groups.py and picks one per prop's needs.
- **Different smoothing thresholds on the two smoothed meshes** (0.848 rad / 0.960 rad) — Bruno hand-tunes per-mesh.
- **No EMPTYs at all** — pure visual mesh prop. Contrast: most furniture has 1-4 anchor/collider EMPTYs.
- **Tight cluster** around (-54.5, 67.5) — the PS is a small prop in a localized timeMachine cluster. All 4 meshes within ~0.7m of each other.
- **`emissiveGreenRadialGradient` use** — only the PS uses green emissive in batch 4. The PS power LED is the iconic green dot that distinguishes the brand from other emissive-orange props.
- **`Cylinder` as mesh name** (unsuffixed) — Bruno keeps the default Blender primitive name. The mesh data is also literally named `Cylinder`. No renaming discipline.
- **`Plane.005` at z=0.059** — very close to ground level. Likely a decal that lies under the PS body for visual grounding (a shadow plane or brand mark).
