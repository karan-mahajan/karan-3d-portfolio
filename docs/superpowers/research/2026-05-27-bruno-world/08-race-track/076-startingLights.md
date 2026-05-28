# 076_startingLights.py — single starting-line signal mesh

**Path:** `folio-2025/scripts/blender_world_steps/steps/076_startingLights.py`
**Lines:** 23
**Adds:** 1 MESH object to collection `startingLights`
**Group:** [08-race-track](../08-race-track.md)

## What it does (code-level)

Creates `startingLights` collection. Adds a single MESH:

```
refStartingLights MESH(Circle.006) at (-11.45, 1.10, 3.90) preventFrustum=True
```

That's it. No modifier, no scale, no rotation. The mesh is at z=3.90 — significantly elevated above the track, consistent with a tree-mounted signal panel.

## Key data

- **Datablocks referenced:** mesh `Circle.006`
- **Materials assigned:** via mesh datablock — `emissiveGreenRadialGradient` (per group .md). The runtime probably swaps colors (red → yellow → green) by changing the material's emission or by swapping meshes
- **Modifiers added:** none
- **Custom properties:** `preventFrustum=True` — the light must run/signal regardless of camera angle
- **World positions of key anchors:** (-11.45, 1.10, 3.90) — at the race start area, elevated 3.9m. Note: x≈-11.45 matches the `refInteractivePoint.003` position in `062_circuit.py` (-11.47) — same starting area
- **Object types breakdown:** 1 MESH
- **Parent collection:** `startingLights` (re-parented under `circuit/` by finalize)

## Technique / recipe

**Minimal "signal post" pattern:** one mesh, one custom prop, no modifier. The visible behavior (red/yellow/green animation) happens entirely in the runtime shader.

**`Circle.006` mesh datablock** — likely a flat disc geometry (signal-light icon) that faces the start line. The material's emission masks (radial gradient) make it glow.

**preventFrustum=True is essential** — when the car is approaching the start line from far away, the lights need to be already in the "red" state before the player can see them. Frustum-culling them would freeze the signal-state machine.

**Elevated mesh (z=3.90)** — high enough to be visible to the player car driver from across the line. Bruno's choice of single elevated mesh vs. a tree-of-meshes for separate R/G/Y bulbs suggests the signal is a single panel with shader-driven state.

## Connections

- **Reads from:** `005_meshes_*.py` (`Circle.006`), `004_materials.py` (`emissiveGreenRadialGradient`)
- **Read by:** `999_finalize.py` (parents `startingLights/` under `circuit/`)
- **Depends on:** `062_circuit.py`
- **Depended on by:** runtime race-state machine (controls the signal color/sequence)

## Notable code patterns

- **One of the smallest scripts in the race track** (23 lines, 1 object). Demonstrates how compact Bruno's scripts can be when only one object is needed.
- **`preventFrustum` appears here, on `077_timer`, and on every checkpoint in `066`** — these are the "gameplay-critical, must always be live" objects.
- **Single emissive material** — the runtime applies the color shift programmatically via shader, NOT by swapping meshes.
- **No rotation specified** — the mesh's authored normal direction (probably +Y) faces the start line by default.
