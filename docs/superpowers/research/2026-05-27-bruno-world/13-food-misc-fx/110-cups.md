# 110_cups.py — 3 dynamic cups inside the time-machine room

**Path:** `folio-2025/scripts/blender_world_steps/steps/110_cups.py`
**Lines:** 204
**Adds:** 6 objects (3× MESH, 3× EMPTY) to collection `cups`
**Group:** [13-food-misc-fx](../13-food-misc-fx.md)

## What it does (code-level)
3 alternating MESH/EMPTY pairs. Pattern repeats 3 times:

1. `cupPhysicalDynamic[.001/.002]` (MESH `Cube.015`) — dynamic cup mesh with a **NODES `Smooth by Angle`** modifier (the basic 0.85 rad smoothing variant, not `.003`).
2. `tube.033/041/042` (EMPTY `CUBE`, scale `(0.444, 0.444, 0.549)`) at the same root position — collision tube/volume.

Cup positions:
- Cup #0: `(-54.02, 69.15, 2.23)` rot 0.
- Cup #1: `(-54.47, 69.39, 2.23)` rot 0.
- Cup #2: `(-53.27, 69.08, 0.15)` rot `(-0.123, 0.107, -0.072)` — fallen/tilted on the floor.

All 3 `tube.NNN` empties share the SAME world position `(-54.02, 69.15, 2.25)` — they're meant to be parented under different cup parents in finalize and offset there.

## Key data
- **Datablocks referenced**: mesh `Cube.015` (the cup geometry, shared by all 3 cups).
- **Materials assigned**: `palette` (via mesh data).
- **Modifiers added**: NODES `Smooth by Angle` × 3 (one per cup, with `Input_1 = 0.848` rad ≈ 48.6° smoothing threshold).
- **Custom properties**: none.
- **World positions**: cluster around `(-54, +69)` — far northwest, inside the `timeMachine` building.
- **Object types breakdown**: 3 MESH, 3 EMPTY.
- **Parent collection**: `timeMachine` (per group index).

## Technique / recipe
- **Three cups, one mesh**: all 3 share `Cube.015` — vary by position/rotation only. Cup #2 has a randomized rotation suggesting "this one fell over."
- **Per-instance collider EMPTY** (`tube.NNN`) — the runtime physics needs an explicit collider per cup; the EMPTY's scale gives it the cup's cylindrical bounds.
- **`Smooth by Angle` (no `.003` suffix)** — uses the simpler smoothing variant. Different from the title's `Smooth by Angle.003` (which has more shading detail). Bruno picks per-object based on rendering goal.

## Connections
- **Reads from**: `005_meshes_*` (`Cube.015`), `003_node_groups.py` (`Smooth by Angle` node group), `004_materials.py` (palette).
- **Read by**: `999_finalize.py` (parents cups under `timeMachine`, tubes under their respective cup).
- **Depends on**: foundation 001-013, `108_timeMachine.py` (parent zone).
- **Depended on by**: 999_finalize.

## Notable code patterns
- `Input_1 = 0.848 rad ≈ 48.6°` — a softer smoothing angle than the 30° (0.524) used on title letters. Cups have curved sides so they want more aggressive smoothing.
- All 3 cups share `Cube.015` — Bruno's mesh-data sharing is consistent. Three "cups" but one mesh datablock in the .blend.
- The tilted cup (#2) shows Bruno hand-tunes "natural disorder" — not just translating an axis-aligned grid of cups but actually tipping one over for visual story.
