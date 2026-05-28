# 077_timer.py — anchor empty (preventFrustum) + offset display mesh

**Path:** `folio-2025/scripts/blender_world_steps/steps/077_timer.py`
**Lines:** 76
**Adds:** 2 objects (1 EMPTY, 1 MESH) to collection `timer`
**Group:** [08-race-track](../08-race-track.md)

## What it does (code-level)

Creates `timer` collection. Adds:

1. **`refTimer`** EMPTY/PLAIN_AXES at (-11.23, -13.19, 2.99) — with `preventFrustum=True` custom prop
2. **`Cube.048`** MESH with mesh datablock `Cube.035` at (-53.29, 49.65, 2.06) — Smooth by Angle.003 GN modifier (Input_1=0.96 rad ≈55°)

Notably the empty anchor (`refTimer`) and the mesh (`Cube.048`) are in **completely different locations** (~70m apart). The mesh is far north-west; the empty is at the race start (near `refInteractivePoint.003`).

## Key data

- **Datablocks referenced:** mesh `Cube.035`, node-group `Smooth by Angle.003`
- **Materials assigned:** via mesh datablock — `palette` (per group .md)
- **Modifiers added:** 1× `Smooth by Angle.003` (NODES, Input_1=0.96 rad) on the mesh
- **Custom properties:** `preventFrustum=True` on `refTimer` empty (not on the mesh)
- **World positions of key anchors:**
  - `refTimer` at (-11.23, -13.19, 2.99) — race-start area, runtime anchor
  - `Cube.048` mesh at (-53.29, 49.65, 2.06) — far away, probably the visible timer panel
- **Object types breakdown:** 1 EMPTY, 1 MESH
- **Parent collection:** `timer` (re-parented under `circuit/` by finalize)

## Technique / recipe

**Two-object split:** the empty is the "logical anchor" (where the timer UI is read from in the runtime — likely also where the timer's HUD origin sits) and the mesh is the visible-panel artwork floating off in the world.

**Why split them?** The mesh might be a hidden template (although `hide_*` flags aren't set here, so it does render at its location). One possibility: the mesh is parented to `refTimer` at runtime, moving with the anchor — the .blend just shows the template at its source-edit location.

Another possibility: the visible timer panel at (-53.29, 49.65) is mounted on a far structure (e.g., a billboard), and `refTimer` is the gameplay-logic anchor at the start line where lap-completion is detected.

**`preventFrustum` on the EMPTY** (not the mesh) — interesting. The empty is the runtime hook; if the empty gets culled, the timer system might not tick. The mesh's visibility is a separate concern.

## Connections

- **Reads from:** `005_meshes_*.py` (`Cube.035`), `003_node_groups.py` (`Smooth by Angle.003`)
- **Read by:** `999_finalize.py` (parents `timer/` under `circuit/`)
- **Depends on:** `062_circuit.py`
- **Depended on by:** runtime timer system

## Notable code patterns

- **`preventFrustum` on empty** is unusual — Bruno's other uses (checkpoints, startingLights) put it on meshes. Here, the runtime probably reads `refTimer`'s presence to keep the timer-update loop alive.
- **Empty + mesh at different locations** — first example seen of that mismatch in the race-track scripts. Either: (a) the mesh is hand-placed for editing convenience and parented to the empty at runtime, (b) the visible timer panel really is far away on a billboard structure.
- **`Smooth by Angle.003` (the universal 55° default)** — Bruno's go-to smoothing for stylized solid props.
