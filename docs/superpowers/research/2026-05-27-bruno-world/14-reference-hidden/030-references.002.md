# 030_references.002.py — 24 oak-trunk placement curves (VISIBLE)

**Path:** `folio-2025/scripts/blender_world_steps/steps/030_references.002.py`
**Lines:** 297
**Adds:** 24 objects (24× CURVE) to collection `references.002`
**Group:** [14-reference-hidden](../14-reference-hidden.md)

## What it does (code-level)
24 nearly-identical blocks creating CURVE objects `treeBody.013`, `.014`, `.005`, `.006`, …, `.071` (Blender auto-numbered, gaps reflect authoring history). Each:
- Wraps the SAME curve datablock `Plane.005` (the oak trunk-extrusion curve from `007_curves.py`).
- Hand-placed `ob.location = (x, y, 0±tiny)` — all at ground level (z ≈ 0).
- Per-instance `ob.rotation_euler = (0, -0, z_rot)` with z rotation values like `-6.7`, `-7.5`, `-4.9`, `-2.2` rad — these are WIDE values (>2π), so they're effectively `mod 2π` plus arbitrary spinning angles. Bruno is using these to randomize the trunk-rotation per tree.
- `scale = (1, 1, 1)`.
- Idempotent collection link.

24 trees scattered across the island (X from -85.85 to +82.30, Y from -85.75 to +77.25).

## Key data
- **Datablocks referenced**: curve `Plane.005` (oak trunk geometry, all 24 instances share it).
- **Materials assigned**: none on these curves directly — the curves are inputs to a downstream geometry-nodes setup that bakes them into visible meshes with `palette`.
- **Modifiers added**: NONE on these reference curves (modifiers live on the FINAL-instance objects in `oakTrees.001` collection).
- **Custom properties**: none.
- **World positions**: 24 trees scattered island-wide. Example positions:
  - `treeBody.013` at `(+46.28, -29.83)`
  - `treeBody.069` at `(-85.85, -85.75)` (far southwest)
  - `treeBody.071` at `(+82.30, +33.99)` (far east)
- **Object types breakdown**: 24 CURVE.
- **Parent collection**: `references.002` → parented under `oakTrees` in finalize. VISIBLE.

## Technique / recipe
- **Curve-as-placement-anchor pattern**: each curve object is a "where the oak goes." All 24 share the SAME curve datablock (`Plane.005`), so they share trunk geometry. The position/rotation of the object drives where the visible tree appears.
- The runtime / a geometry-nodes setup elsewhere reads these 24 curves (or the matching 24 final-instance objects in `oakTrees.001`) to render 24 oak trees.
- **Z-rotation as random seed**: values like `-6.727` rad (which `mod 2π` = ~5.84) and `-12.052` rad — Bruno used wildly large numbers (probably because Blender's rotation widget accumulated multiple spins) to give each tree a unique random-looking trunk orientation.
- **24 trees worth of scatter authored by HAND** — no procedural seed, just Bruno placing each tree where he wants it.

## Connections
- **Reads from**: `007_curves.py` (`Plane.005`).
- **Read by**: `136_oakTrees.001.py` (minimap-version oak trees use the same 24 placements), finalize.
- **Depends on**: 007, 013, `029_archives.001.py` (the template curve).
- **Depended on by**: 999_finalize, 136.

## Notable code patterns
- **All 24 use `Plane.005`** (oak template), NOT `Plane.010` (which `029_archives.001` wraps). So there are TWO oak curve datablocks: `Plane.010` (one source/template) and `Plane.005` (the placement-version). Probably they're slight variations (or `Plane.005` is the working copy and `Plane.010` is the archived original).
- Z-rotations include values like `-7.593414306640625` — clearly Bruno didn't normalize. Working as-is, Blender wraps them.
- All 24 entries are 12-line blocks of identical structure — Bruno's exporter does NOT loop, it writes out each block verbatim. Makes the script 297 lines for what is conceptually a 24-element list.
