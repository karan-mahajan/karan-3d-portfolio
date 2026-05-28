# 063_airDancers.py — the 2 inflatable tube-guys at race entrance

**Path:** `folio-2025/scripts/blender_world_steps/steps/063_airDancers.py`
**Lines:** 33
**Adds:** 2 objects (2× MESH) to collection `airDancers`
**Group:** [13-food-misc-fx](../13-food-misc-fx.md)

## What it does (code-level)
- Gets/creates collection `airDancers` via `bpy.data.collections.get`/`new`.
- Creates `refAirDancers` and `refAirDancers.001`, both wrapping the SAME mesh datablock `Cylinder.059` (so the two share geometry — material on the mesh data is `airDancer`, the dedicated wave-animation shader).
- Sets `ob.location`, `ob.rotation_euler`, `ob.scale`; flips `display_type` to `'TEXTURED'`.
- Idempotently links each object into the collection if not already present.

## Key data
- **Datablocks referenced**: mesh `Cylinder.059` (loaded by foundation `005_meshes_*`; carries `airDancer` material).
- **Materials assigned**: `airDancer` (animated wave shader; via mesh, not object override).
- **Modifiers added**: none.
- **Custom properties**: none.
- **World positions**:
  - `refAirDancers` at `(-1.73, -15.73, 1.00)` rot z≈0.
  - `refAirDancers.001` at `(-27.81, 0.50, 1.00)` rot z≈0.339 rad (~19.4°).
- **Object types breakdown**: 2 MESH.
- **Parent collection**: linked into `scenery` by `999_finalize.py` (under race-circuit ambience).

## Technique / recipe
Two hand-placed instances of one cylinder mesh at the race-track entrance. The visual interest comes ENTIRELY from the `airDancer` material shader (runtime wave animation in TSL), not from geometry. Bruno is using mesh-sharing (both objects → same `Cylinder.059`) as a deliberate optimization: edit the source mesh once, both dancers update.

The `refAirDancers` naming prefix `ref…` marks this as a runtime-spawn template — the game runtime probably uses these as positional/orientation references and may either reveal them directly or instantiate further at-runtime copies.

## Connections
- **Reads from**: `005_meshes_*` (mesh `Cylinder.059`), `004_materials.py` (material `airDancer`).
- **Read by**: `999_finalize.py` (parents both under `scenery` empty).
- **Depends on**: foundation 005 + 013 (collection skeleton).
- **Depended on by**: nothing direct.

## Notable code patterns
- Two identical object blocks differing only in location/rotation — no loop. Bruno's exporter unrolls instances rather than iterating.
- Mesh-sharing via `bpy.data.meshes.get('Cylinder.059')` lookup; both `ob.data` point at the same datablock.
- `try/except` around `display_type` — defensive against headless/CI Blender variants where the prop may not exist.
