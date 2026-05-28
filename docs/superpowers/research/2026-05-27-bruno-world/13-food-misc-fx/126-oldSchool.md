# 126_oldSchool.py — retro car-shaped prop (EXCLUDED)

**Path:** `folio-2025/scripts/blender_world_steps/steps/126_oldSchool.py`
**Lines:** 117
**Adds:** 8 objects (5× MESH, 3× EMPTY) to collection `oldSchool`
**Group:** [13-food-misc-fx](../13-food-misc-fx.md)

## What it does (code-level)
Builds a retro "old school" car-shaped prop. Pattern mirrors the vehicle template ([125_default.001.py](../14-reference-hidden/125-default.001.md)):

- `chassis` (EMPTY PLAIN_AXES) at `(0, 0, 0.907)` — body root.
- `wheelContainer` (EMPTY PLAIN_AXES) at `(0.87, 0.70, -0.42)` — wheel parent.
- `wheelCylinder` (EMPTY PLAIN_AXES) at same position — wheel pivot.
- `wheel` (MESH `Cylinder.081`) at same position, `rotation_mode='QUATERNION'`, `rotation_quaternion=(0.0018, 0.711, 0.0025, -0.703)` — wheel mesh tilted 90° via quat.
- `bodyBlack.002` (MESH `Cube.231`) at `(-0.167, 0, 1.171)` rot quat (0.5,-0.5,-0.5,0.5) — body in `black` material per name.
- `bodyPainted` (MESH `Cube.240`) at same body position — main color layer.
- `headlights.002` (MESH `Cube.228`) at same body position — headlight cluster.
- `backLights.002` (MESH `Cube.215`) at same body position — taillight cluster.

## Key data
- **Datablocks referenced**: meshes `Cylinder.081`, `Cube.231`, `Cube.240`, `Cube.228`, `Cube.215`.
- **Materials assigned**: `palette`, `emissiveOrangeRadialGradient` (headlights), `redGradient` (taillights), per the group index.
- **Modifiers added**: none.
- **Custom properties**: none.
- **World positions**: all near origin — same "authored at origin, parented in finalize" pattern.
- **Object types breakdown**: 5 MESH, 3 EMPTY.
- **Parent collection**: EXCLUDED collection `oldSchool`; per finalize, parented under another zone.

## Technique / recipe
- **Vehicle component pattern**: chassis + wheel + body + paint + headlights + backlights as separate meshes — same anatomy as 125_default.001 (the runtime vehicle). The runtime probably uses this same data layout for "any car-shaped thing."
- **Quaternion rotations on wheel + body** — required because wheels rotate around their own axis at runtime (quaternion avoids gimbal lock during continuous spin) and the body uses quat for clean 90° rotations.
- **Two separate body meshes** (`bodyBlack` + `bodyPainted`) — Bruno authors black trim and painted color as DIFFERENT mesh datablocks rather than as one mesh with a multi-material setup. Simpler runtime material binding.

## Connections
- **Reads from**: `005_meshes_*` (5 datablocks), `004_materials.py` (palette + emissive + redGradient).
- **Read by**: `999_finalize.py` (parents under hidden owner, sets view-layer EXCLUDE).
- **Depends on**: foundation 001-013.
- **Depended on by**: 999_finalize.

## Notable code patterns
- **Anatomically mirrors [125_default.001](../14-reference-hidden/125-default.001.md)** but is smaller (8 vs 24 objects). 125 is the full runtime car; 126 is a stylized retro "trophy" version.
- Wheel quat `(0.0018, 0.711, 0.0025, -0.703)` is approximately a 90° rotation around Y — turns the cylinder mesh from upright into a "wheel" orientation.
- All meshes use sequential `Cube.215, .228, .231, .240` — proximity in the meshes array suggests Bruno authored these together (vehicle-prop session in Blender).
