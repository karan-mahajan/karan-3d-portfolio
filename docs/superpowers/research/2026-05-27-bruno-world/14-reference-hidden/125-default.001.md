# 125_default.001.py — the runtime vehicle template (the car you drive)

**Path:** `folio-2025/scripts/blender_world_steps/steps/125_default.001.py`
**Lines:** 341
**Adds:** 24 objects (18× MESH, 6× EMPTY) to collection `default.001`
**Group:** [14-reference-hidden](../14-reference-hidden.md)

## What it does (code-level)
The full runtime-controlled vehicle (the car you drive in Bruno's folio). Hierarchical authoring all at near-origin, intended to be parented under the `vehicle` zone at runtime.

Order of objects (sampled from grep — full list):
1. `chassis.001` (EMPTY PLAIN_AXES) at `(~0, 0, 0.907)` — body root anchor.
2. `blinkerLeft.001`, `blinkerRight.001`, `common` (MESH × 3 from `Plane.144/145/146`) — turn-signal lights + common emissive plane. Each carries custom prop `ob['booleans'] = []` (empty list — runtime fills with bool flags for "is on/off").
3. `bodyPainted.001` (MESH `Cube.216`) — painted body shell.
4. `headlights.001` (MESH `Cube.223`) + `stopLights.001` (MESH `Cube.225`) — front/rear lights.
5. `wheelContainer.001` + `wheelCylinder.001` (EMPTY × 2) — wheel parent/pivot.
6. `wheelSuspension.002` (MESH `Cylinder.072`) — suspension cylinder, rot z=-π/8 (offset for visual lean).
7. `wheelPainted` + `wheel.006` (MESH × 2 from `Plane.150/151`) — wheel visible halves (with `booleans` flag).
8. `wheelGuard.001` (MESH `Cylinder.073`) — wheel fender.
9. `cellsCage.003`/`004`/`005` (MESH × 3 from `Circle.019` + variants) + `cellsEnergy.003`/`004`/`005` (MESH × 3) — energy cell visualizations (3 layered cages around 3 energy cores).
10. `cell1.001`, `cell2.001`, `cell3.001` (EMPTY × 3) — cell positions.
11. `energy.001` (MESH) + `backLights` (MESH) — additional emissive layers with `booleans` flag.

(Per the line count there are more — total 24 objects with 18 MESH + 6 EMPTY.)

## Key data
- **Datablocks referenced**: meshes `Plane.144/145/146/150/151`, `Cube.216/223/225`, `Cylinder.072/073`, `Circle.019` + variants. About 18 unique meshes.
- **Materials assigned**: `darkGray`, `emissiveOrangeRadialGradient`, `emissivePurpleRadialGradient`, `palette`, `redGradient` (per group index). Mixed materials — vehicle is the most material-diverse single prop.
- **Modifiers added**: none in this script (the vehicle uses no Smooth-by-Angle; runtime renders it with hard edges).
- **Custom properties**: `ob['booleans'] = []` on ~8 meshes — runtime-mutable flag list for headlights/blinkers/etc state.
- **World positions**: all near origin (offsets <1m). The whole vehicle is authored at origin and parented under `vehicle` zone in finalize.
- **Object types breakdown**: 18 MESH, 6 EMPTY.
- **Parent collection**: `default.001` → parented under `vehicle` (script 123) in finalize. VISIBLE.

## Technique / recipe
- **Authored at origin, parented in finalize**: same pattern as other props but at fuller complexity. The runtime translates the whole `chassis.001` empty to put the car wherever the player is.
- **`booleans=[]` custom prop convention** — runtime mutates this list to toggle which emissive layers are on (e.g., `[True, False, True]` = headlights on, blinker off, stoplights on). Reading the `.blend` at runtime preserves the empty list, runtime populates per-frame.
- **3-layered cellsCage/cellsEnergy** — visual layers for fuel/energy/glow. Each cell has its own scale + position empty marker (`cell1.001`, etc.).
- **No armature**, the vehicle is NOT rigged. Wheel rotation = parent transform of `wheelContainer.001` (runtime spins the empty, wheel mesh follows).

## Connections
- **Reads from**: `005_meshes_*` (~18 datablocks), `004_materials.py` (5 materials).
- **Read by**: `999_finalize.py` (full parenting tree under `vehicle` zone), `137_vehicle.001.py` (minimap version), runtime vehicle controller.
- **Depends on**: 005, 004, 013.
- **Depended on by**: 137, 999.

## Notable code patterns
- **`booleans` empty list pattern** — Bruno's way to declare "this object has a runtime-mutable boolean state." Sets up the shape; runtime fills in values.
- The vehicle is INSIDE the world's `.blend` (not loaded as a GLTF) — emphasizes that Bruno authored EVERYTHING in Blender, even the player-controlled vehicle.
- **Per-light dedicated mesh** (headlights, stopLights, backLights, blinkerLeft, blinkerRight) — separate MESH objects, each gets its own emissive material. Bruno didn't UV-pack them onto one body.
- The wheel uses TWO plane meshes (`wheelPainted` + `wheel.006`) — separate paint layer + base. Same pattern as oldSchool.
