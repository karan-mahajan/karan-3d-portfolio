# 115_cabin.py — cabin zone with hidden metaball moss, dynamic physics anchor, and moon prop

**Path:** `folio-2025/scripts/blender_world_steps/steps/115_cabin.py`
**Lines:** 85
**Adds:** 5 objects to collection `cabin`
**Group:** [06-buildings-structures](../06-buildings-structures.md)

## What it does (code-level)

Creates collection `cabin`. Adds 5 objects across three types:

**META object** (1):
- `metaMoss` — metaball `Mball.004`, at (0.0, 0.0, 0.0). `hide_viewport=True`, `hide_render=True`, `hide_select=True` — fully invisible in all contexts.

**EMPTYs** (2):
- `refCabinPhysicalDynamic` — PLAIN_AXES, at (some world position). Custom property: `ob['mass'] = 5.0`
- `cuboid.079` — CUBE display type (wall collision box)

**Visible geometry** (2 MESH):
- `refMoon` — mesh `Cube.153`, position and rotation not specified in summary
- `wood.002` — mesh `Cube.135`, position not specified

## Key data

- **Datablocks referenced:** metaball `Mball.004`, meshes `Cube.153`, `Cube.135`
- **Materials assigned:** `palette` (via mesh datablocks); metaball material set via `Mball.004` datablock
- **Modifiers added:** none
- **Object types breakdown:** 2 MESH, 2 EMPTY, 1 META
- **Parent collection:** `cabin`
- **Custom properties:** `refCabinPhysicalDynamic['mass'] = 5.0`

## Technique / recipe

**`metaMoss` is the most unusual object in this script.** Metaballs (`bpy.data.metaballs`) are Blender's SDF primitive: they define smooth implicit surfaces that merge with other metaballs in the same family. `Mball.004` at origin with all hide flags set means it is:
1. Never visible in viewport, render, or selection
2. Used as an SDF reference shape — the runtime reads its position/radius data to generate smooth moss coverage on the cabin geometry procedurally

This is the only META object seen in the entire batch. Bruno uses it as a data carrier for the moss VFX rather than as a rendered mesh — the actual moss visuals are generated at runtime from the metaball parameters.

**`refCabinPhysicalDynamic` is the only dynamic physics EMPTY in this batch.** The `mass=5.0` custom property tells the runtime Rapier physics system to create a dynamic rigid body at this position with 5 kg mass — the cabin prop or a specific part of it (a door? a box?) will be physically simulated and can be pushed. This contrasts with `physicalFixed` empties (static bodies) seen in the lab and timeMachine.

**`cuboid.079`** follows the wall-collision CUBE empty pattern from the lab (`cuboid.069`/`cuboid.071`) and timeMachine (`cuboid.220`/`cuboid.221`).

**`refMoon`** with `Cube.153` — a named `refMoon` suggests this is a glowing moon prop or a round sphere-like mesh used as a decorative light source near the cabin.

## Connections

- **Reads from:** `005_meshes_*.py` (`Cube.153`, `Cube.135`), `004_materials.py`; metaball `Mball.004` sourced from mesh/materials setup
- **Read by:** `999_finalize.py`; runtime physics (refCabinPhysicalDynamic mass=5.0); runtime moss VFX (metaMoss)
- **Depends on:** `013_collections.py`
- **Depended on by:** runtime zone system; physics simulation

## Notable code patterns

Three unique patterns in one script:
1. **META object as SDF data carrier** — `metaMoss` at origin, fully hidden, used by runtime to shape moss. Only META in the batch.
2. **Dynamic physics EMPTY with `mass` custom property** — `refCabinPhysicalDynamic` with `mass=5.0`. The `Dynamic` suffix in the name encodes the physics body type, consistent with `fencePhysicalDynamic` in `042_fences.py`.
3. **`refMoon` naming** — implies a moon-shaped prop visible at the cabin; likely emissive or used as a point light proxy.

The object-name prefix `ref` appears on both `refCabinPhysicalDynamic` (EMPTY) and `refMoon` (MESH) — Bruno uses `ref` on objects that the runtime references by name, not just for zone anchors. The plain name `wood.002` (no `ref`) is a purely decorative prop the runtime ignores.
