# 090_controls.py — landing-zone interactive control kiosk with gizmo/gamepad/phone props

**Path:** `folio-2025/scripts/blender_world_steps/steps/090_controls.py`
**Lines:** 316
**Adds:** 14 objects (7 MESH, 7 EMPTY) to collection `controls`
**Group:** [11-furniture-displays-boards](../11-furniture-displays-boards.md)

## What it does (code-level)

Creates `controls` collection — the **landing-zone interactive controls kiosk** showing input-device demonstrations (gizmo control, gamepad, phone touchpad):

**Display panels:**

| Object | Type | Mesh | Location | Notes |
|---|---|---|---|---|
| `Plane.004` | MESH | `Plane.024` at (54.48, -29.70, 0.150) — rotX=0.175 (10°), rotZ=0.315 (≈18°), scale=0.581. Display panel 1 |
| `Plane.002` | MESH | `Plane.020` at (54.48, -29.70, 0.150) — same transform as Plane.004. Display panel 2 stacked on top |
| `body.002` | MESH | `Plane.066` at (16.11, -1.37, 0.558) — kiosk body at staging |

**Demo props (3 device demos):**

| Object | Type | Mesh | Notes |
|---|---|---|---|
| `gizmoPhysicalDynamic` | MESH | `sdfsdf` (yes, that's the mesh name) at (55.27, -30.88, 0.925) — rotX=-1.571, rotZ=-1.571. **`Smooth by Angle.001` (Input_1=0.914 rad ≈52°)** |
| `qosdjqosjd` | MESH | `Cylinder.026` at (17.37, -1.00, 1.380) — at staging. Mesh name is keyboard-mashed gibberish |
| `phonePhysicalDynamic` | MESH | `Circle.005` at (57.33, -30.29, 0.515) — rotX=0.169, rotZ=0.814 (≈47°). `Smooth by Angle.003` (Input_1=0.785 rad ≈45°) |
| `phonePhysicalDynamic.002` | MESH | `Circle.015` at (57.33, -30.29, 0.515) — same transform as `phonePhysicalDynamic`, also smoothed |

**Collider primitives:**

| Object | Type | Location | Scale | Notes |
|---|---|---|---|---|
| `cuboid.019` | EMPTY/CUBE | (16.86, 5.70, 1.62) | (1.72, 1.72, 1.72) | Large cube collider for gizmo |
| `cuboid.011` | EMPTY/CUBE | (18.35, 4.88, 0.451) | (3.18, 1.76, 0.76) | Body collider — wide flat platform |
| `cuboid.009` | EMPTY/CUBE | (57.32, -30.28, 0.414) | (1.77, 3.17, 0.26) | Phone-area collider — at actual world position (not staging) |
| `tube.014` | EMPTY/CUBE | (57.43, -30.38, 1.274) | (0.80, 0.80, 1.45) | Tube-collider for the phone stand |

**Anchor empties:**

| Object | Notes |
|---|---|
| `gamepadPhysicalDynamic.001` | EMPTY/PLAIN_AXES at (57.47, -32.31, 0.623). Gamepad physics anchor |
| `refControlsInteractivePoint` | EMPTY/PLAIN_AXES at (53.84, -32.53, 1.749). UI interaction prompt anchor |
| `phonePhysicalDynamic.001` | EMPTY/PLAIN_AXES at (57.33, -30.29, 0.515) — same position as the phone mesh |

## Key data

- **Datablocks referenced:** meshes `Plane.024`, `Plane.020`, `Plane.066`, `sdfsdf` (gizmo — gibberish mesh name!), `Cylinder.026`, `Circle.005`, `Circle.015`; node-groups `Smooth by Angle.001`, `Smooth by Angle.003`
- **Materials assigned:** `emissiveOrangeRadialGradient`, `palette` (per group .md)
- **Modifiers added:** 3× smoothing (1× `Smooth by Angle.001` on gizmo, 2× `Smooth by Angle.003` on the two phone meshes)
- **Custom properties:** none
- **World positions of key anchors:**
  - Display panels at (54.48, -29.70, 0.15) — landing zone kiosk position
  - Gizmo at (55.27, -30.88, 0.925) — 1.5m east of panels
  - Phone meshes at (57.33, -30.29, 0.515) — 3m east of panels
  - Gamepad anchor at (57.47, -32.31, 0.623) — south of phone
  - Body + qosdjqosjd at staging (16-18, -1 to 5)
- **Object types breakdown:** 7 MESH, 7 EMPTY
- **Parent collection:** `controls` (re-parented under `landing/` by finalize)

## Technique / recipe

**Triple-device interactive kiosk:**

1. **Two stacked display panels** at (54.48, -29.70) — rotated 10° around X (tilted backward) and 18° around Z. Likely a kiosk-style angled display. Both at the same transform, stacked (likely a backing + a screen layer).
2. **Three device demos** physically present on the kiosk:
   - **Gizmo** (`sdfsdf` mesh — the gibberish name suggests Bruno temped this and never renamed): a manipulator-cube prop demonstrating the "click and drag" gizmo control scheme
   - **Phone** (two co-located `Circle.005` + `Circle.015` meshes): two visible variants of the touchscreen demo (likely an iPhone-style flat circle + the screen highlight)
   - **Gamepad anchor** (no visible mesh in this script — the gamepad is anchor-only here; the actual gamepad model is elsewhere or runtime-spawned)
3. **Collider primitives** for each demo:
   - `cuboid.019` for gizmo (1.72m cube)
   - `cuboid.011` for body (wide flat — the kiosk platform)
   - `cuboid.009` + `tube.014` for phone (flat + tube stand)
4. **Multiple PhysicalDynamic anchors** for each demoable prop — runtime spawns dynamic bodies at these anchors so players can grab and interact.
5. **`refControlsInteractivePoint`** at z=1.749 (chest height, slightly elevated from the kiosk) — the "Press E to interact" UI prompt anchor.

**`sdfsdf` and `qosdjqosjd`** — placeholder mesh names that survived into production. Bruno was iterating in Blender, named these test-meshes with keyboard mashes, then committed before renaming. This is a peek at the pipeline's "work-in-progress" state — Bruno's exporter doesn't enforce mesh-name validation.

**Two phone meshes stacked** (`phonePhysicalDynamic` + `phonePhysicalDynamic.002`) at the same transform — likely the phone body + the screen highlight (so runtime can swap or animate one). Same trick as the input-device labels in 082.

**Different `Smooth by Angle.NNN` variants in one script:**
- `Smooth by Angle.001` (Input_1=0.914 rad ≈52°) — on gizmo (sharper)
- `Smooth by Angle.003` (Input_1=0.785 rad ≈45°) — on phones (softer)
Bruno picks the variant per-prop based on which preset best matches the geometry.

## Connections

- **Reads from:** `005_meshes_*.py` (7 meshes including `sdfsdf` and `qosdjqosjd`), `003_node_groups.py` (`Smooth by Angle.001`, `.003`)
- **Read by:** `999_finalize.py` (parents `controls/` under `landing/`)
- **Depends on:** `088_landing.py` (parent zone)
- **Depended on by:** runtime input-device demo system, interaction system

## Notable code patterns

- **Gibberish mesh names (`sdfsdf`, `qosdjqosjd`)** — Bruno's pipeline doesn't sanitize mesh names. These shipped to production as-is. Pattern: bypassed naming discipline.
- **3 distinct demoable props in one script** — the kiosk's purpose is to show off the 3 input methods (gizmo / phone / gamepad). One script bundles all 3 demos.
- **Stacked phone meshes** (`phonePhysicalDynamic` + `.002`) at identical transforms — visual layering pattern (body + screen overlay).
- **`tube.014` named EMPTY/CUBE** — Bruno's collider names mix `tube.NNN` and `cuboid.NNN`. They're both EMPTY/CUBEs in Blender; the name signals the runtime collision shape class (capsule vs box).
- **Multiple PhysicalDynamic anchors per script** — `gizmoPhysicalDynamic` + `phonePhysicalDynamic` + `phonePhysicalDynamic.001` + `gamepadPhysicalDynamic.001`. Four physics-active demoables in one kiosk.
- **`refControlsInteractivePoint`** singular — only ONE interactive prompt for the whole kiosk, even though it has 4 interactive props. The player triggers the kiosk as a unit.
- **No `mass` custom props on the demoable meshes** — runtime probably uses default masses for these.
- **Display panels at landing area (54.48, -29.70)** = the landing zone is at x ≈ 50-60, y ≈ -25 to -55. Controls kiosk is at the south edge.
