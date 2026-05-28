# 137_vehicle.001.py — full 41-object drivable car template (EXCLUDED)

**Path:** `folio-2025/scripts/blender_world_steps/steps/137_vehicle.001.py`
**Lines:** 579
**Adds:** 41 objects (29 MESH, 12 EMPTY) to collection `vehicle.001`
**Group:** [08-race-track](../08-race-track.md)

## What it does (code-level)

Creates `vehicle.001` collection. Adds 41 objects modeling a complete drivable vehicle (body, 4 wheels, lights, energy cells, cells/battery rack). All objects are authored at LOCAL coordinates (origin (0,0,0)) — the entire vehicle is positioned at world (0, 0, ~1) and would be re-positioned by runtime at spawn time.

### Anatomy of the vehicle

**Body parts** (all MESH with `booleans=[]` custom prop, all scaled 0.7353 uniform):
| Object | Mesh | Local Location |
|---|---|---|
| `blinkerLeft.002` | `Plane.001` | (0.027, 0.008, 0.889) |
| `blinkerRight.002` | `Plane.009` | (~0, ~0, 0.907) |
| `common.003` | `Plane.015` | (~0, ~0, 0.907) |
| `bodyPainted.002` | `Cube.005` | (~0, 0, 0.907) — the car body shell |
| `headlights.003` | `Cube.006` | (~0, 0, 0.907) |
| `stopLights.003` | `Cube.007` | (-0.553, 0, 1.499) |
| `energy.002` | `Plane.027` | (~0, ~0, 0.907) — energy/glow indicator |

**Root + cells** (EMPTY/PLAIN_AXES + battery MESHes):
| Object | Type / Mesh | Location |
|---|---|---|
| `chassis.002` | EMPTY | (~0, 0, 0.907) — vehicle root |
| `cellsCage.001` | MESH `Circle.001` | (-0.929, -0.289, 1.112) — battery ring |
| `cellsEnergy.001` | MESH `Cylinder.004` | same location |
| `cellsCage.002` | MESH `Circle.002` | (-0.929, -0.289, 1.143) — second battery |
| `cellsEnergy.002` | MESH `Cylinder.006` | same |
| `cellsCage.006` | MESH `Circle.003` | (-0.929, -0.289, 1.143) — third battery |
| `cellsEnergy.006` | MESH `Cylinder.007` | same |
| `cell1.002` / `cell2.002` / `cell3.002` | 3 EMPTY anchors | (0, 0, 1.107) — battery cell anchors |

**Wheels** (4 identical sets, each = 1 wheelContainer empty + wheelSuspension mesh + wheelCylinder empty + wheelPainted mesh + wheel mesh + wheelGuard mesh):

| Wheel | Container location | Suspension mesh | Painted/wheel/guard meshes | Notes |
|---|---|---|---|---|
| Front-left | (0.872, 0.699, -0.417) | `Cylinder.002` | `Plane.019`, `Plane.026`, `Cylinder.003` | rotZ=0 |
| Front-right (`.003`) | (-0.815, 0.699, -0.417) | `Cylinder.008` | `Plane.029`, `Plane.042`, `Cylinder.009` | rotZ=0 |
| Rear-left (`.004`) | (-0.815, -0.720, -0.417) | `Cylinder.010` | `Plane.047`, `Plane.052`, `Cylinder.012` | rotZ=π |
| Rear-right (`.005`) | (0.872, -0.720, -0.417) | `Cylinder.013` | `Plane.055`, `Plane.058`, `Cylinder.016` | rotZ=π |

Wheel cages span ±0.85m in X, ±0.72m in Y around the chassis center — vehicle footprint ≈ 1.7m wide × 1.4m long.

## Key data

- **Datablocks referenced:** ~24 unique mesh datablocks (each body part + cell + wheel suspension has its own mesh, wheelPainted/wheel/wheelGuard have their own per wheel)
- **Materials assigned:** via mesh datablocks — `darkGray`, `emissiveOrangeRadialGradient`, `emissivePurpleRadialGradient`, `palette`, `redGradient` (per group .md)
- **Modifiers added:** NONE on any mesh in this script — the vehicle is hand-modeled, normal-baked, ready-to-render
- **Custom properties:** `booleans=[]` on every BODY mesh (blinkerLeft, blinkerRight, common, bodyPainted, headlights, stopLights, wheelPainted×4, wheel×4, energy). Wheel containers and chassis empties have no booleans
- **World positions of key anchors:** all LOCAL (vehicle template at origin). Runtime parents at spawn position
- **Object types breakdown:** 29 MESH, 12 EMPTY
- **Parent collection:** `vehicle.001` (EXCLUDED from view layer; re-parented under `vehicle/` by finalize)

## Technique / recipe

**Hierarchical vehicle template:** chassis is the root empty; wheels are 4 sub-hierarchies each with `wheelContainer` empty + `wheelCylinder` empty (transform pivots) + 3 wheel meshes (painted/inner/guard) + 1 suspension cylinder mesh. The runtime can:
1. Read `chassis.002` as the vehicle root
2. Read each `wheelContainer.0NN` to know where the wheels attach
3. Rotate the `wheelCylinder.0NN` to spin the wheels
4. Translate `wheelSuspension` for travel

**`booleans=[]` custom prop on body meshes** — empty array suggests "this mesh's customization channels are unconfigured." At runtime, Bruno's editor or persisted user state might fill this array with mesh-swap or color-swap options (e.g., paint variants). The empty default = "use the base mesh as-is."

**Three battery cells (`cellsCage.001`, `.002`, `.006`)** — 3 visible battery rings stacked vertically, each with its own emissive-cylinder energy core. The `cell1.002`, `cell2.002`, `cell3.002` empties are mounting points for animated/state-driven battery indicators at runtime.

**EXCLUDED** from view layer — this template never renders directly. The runtime instantiates copies of this hierarchy when spawning the player vehicle.

**Body part naming with `.002`/`.003` suffixes** — this is the SECOND vehicle template (vehicle.001 = "vehicle variant 1"). The naming uses `.002` because the FIRST vehicle template (`vehicle.000`) probably exists elsewhere with `.001` suffixes on parts. Bruno's naming convention: vehicle.NNN templates have body parts named with `.NNN+1` suffixes.

## Connections

- **Reads from:** `005_meshes_*.py` (many — Plane.001, Plane.009, Plane.015, Cube.005-007, Cylinder.002-016, Circle.001-003, Plane.019/026/027/029/042/047/052/055/058)
- **Read by:** `999_finalize.py` (sets EXCLUDED state; re-parents `vehicle.001/` under `vehicle/`)
- **Depends on:** `005_meshes_*.py`, `123_vehicle.py` (umbrella exists)
- **Depended on by:** runtime vehicle-spawn code in `folio-2025/sources/`

## Notable code patterns

- **`booleans = []` (empty list)** as a custom property — Bruno's "this mesh participates in runtime customization" flag. Wheel structural parts (cylinders, guards) don't have it; painted/visible body parts do.
- **No modifiers at all** — unique among complex prop scripts. The vehicle mesh authoring handles its own smoothing and bevels at the .blend mesh level (vertex normal data probably baked).
- **Same scale (0.7353) on every body part** — uniform downsize applied consistently; the source mesh was authored at ~1.36× and Bruno scaled the whole vehicle down for the world.
- **EXCLUDED template + 3 vehicle child collections** (antenna, oldSchool, default) — the user can pick a vehicle variant at runtime; each variant is its own EXCLUDED template. Only the selected one becomes visible.
- **Local coordinates throughout** — the entire vehicle authored at world origin. Runtime instantiation translates the whole hierarchy to spawn point.
