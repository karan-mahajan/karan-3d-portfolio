# 108_timeMachine.py — time machine prop with split world positions

**Path:** `folio-2025/scripts/blender_world_steps/steps/108_timeMachine.py`
**Lines:** 146
**Adds:** 9 objects to collection `timeMachine`
**Group:** [06-buildings-structures](../06-buildings-structures.md)

## What it does (code-level)

Creates collection `timeMachine`. Adds 9 objects in two functional layers:

**Visible geometry** (2 MESH):
- `Cube.008` — mesh `Cube.014`, at (-54.53, 67.40, 1.32), rotation=(0.0, 0.0872, 0.0) rad — slight Y tilt
- `Cube.009` — mesh `Cube.014`, at (-54.53, 67.40, 1.32), rotation=(0.0, -0.0872, 0.0) rad — mirrored Y tilt

Both use the same mesh datablock `Cube.014`, positioned identically at the prop world location, with opposing tilts.

**Zone anchor empties** (7 EMPTY):
- `timeMachine` — PLAIN_AXES root, at (-54.53, 67.40, 0.0)
- `physicalFixed.010` — PLAIN_AXES, at (-54.53, 67.40, 1.0)
- `refInteractivePoint.003` — PLAIN_AXES, at (69.88, -9.72, 1.50)
- `refZoneBounding.003` — CIRCLE, at (69.88, -9.72, 3.27), scale=5.888 → r=5.89m
- `refZoneFrustum.003` — CIRCLE, at (69.88, -9.72, 3.27), scale=5.217 → r=5.22m
- `cuboid.220` — CUBE display, at (-28.42, 22.05, 1.97), scale=(0.54, 4.71, 3.98)
- `cuboid.221` — CUBE display, at (-25.10, 24.34, 2.50), scale=(0.54, 2.71, 4.90)

TimeMachine prop root: **(-54.53, 67.40)**. Zone anchor center: **(69.88, -9.72)**. These are two entirely different world positions.

## Key data

- **Datablocks referenced:** mesh `Cube.014`
- **Materials assigned:** `palette` (via mesh datablock)
- **Modifiers added:** none
- **World positions — split:** prop at (-54.53, 67.40), zone at (69.88, -9.72). Distance ≈ 155m apart.
- **Object types breakdown:** 2 MESH, 7 EMPTY
- **Parent collection:** `timeMachine`
- **CUBE empty dimensions:** cuboid.220 wall≈9.42m×7.97m, cuboid.221 wall≈5.42m×9.80m (same values as lab's cuboid.069/071)

## Technique / recipe

The two `Cube.008`/`Cube.009` meshes share the same mesh datablock `Cube.014` and are placed at identical coordinates, differentiated only by ±0.0872 rad (≈5°) Y-axis rotation. This is a symmetrical two-part prop: two slightly outward-tilted panels or fins forming a V or X shape — a classic sci-fi "machine" silhouette built from mirrored mesh instances.

The `physicalFixed.010` EMPTY at the prop root suggests the timeMachine object has physics (a dynamic rigid body that the runtime pins in place using this fixed anchor).

**Position split is the defining feature of this script:** the prop geometry (`timeMachine` root, `physicalFixed`, the two mesh objects) sits at (-54.53, 67.40) — far northwest/off-island — while the zone detection empties (`refInteractivePoint.003`, `refZoneBounding.003`, `refZoneFrustum.003`) sit at (69.88, -9.72) near the building. `999_finalize.py` presumably re-parents or repositions these when building the final scene, or the zone trigger is deliberately decoupled from the prop location (e.g., the zone triggers a cutscene that transports the player to the prop).

The CUBE empties (`cuboid.220`, `cuboid.221`) share the same values as `lab`'s `cuboid.069`/`cuboid.071` — suggesting a shared wall-collision template that the runtime repositions relative to whichever zone root it is parented under.

## Connections

- **Reads from:** `005_meshes_*.py` (`Cube.014`), `004_materials.py`
- **Read by:** `999_finalize.py` (resolves position split); runtime zone + physics systems
- **Depends on:** `013_collections.py`
- **Depended on by:** runtime interaction system (refInteractivePoint.003); runtime physics (physicalFixed.010)

## Notable code patterns

Using the same mesh datablock for two objects with opposing tilts is a zero-cost duplication — no extra mesh memory. The ±0.0872 rad Y tilt is the same value used on `refInteractivePoint` Z-rotation in `091_kiosk.py`, suggesting 0.0872 rad (≈5°) is a common precision-rotation unit in Bruno's authoring workflow.

The position split (prop vs. zone at 155m apart) is unique in this batch — no other zone script has such a large gap between root and zone anchors. This is either a late-placed prop authored while another area was active in Blender, or an intentional design where the interaction trigger is not co-located with the physical prop.
