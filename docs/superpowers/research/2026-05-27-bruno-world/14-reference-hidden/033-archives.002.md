# 033_archives.002.py — birch trunk source curve (EXCLUDED template)

**Path:** `folio-2025/scripts/blender_world_steps/steps/033_archives.002.py`
**Lines:** 21
**Adds:** 1 object (1× CURVE) to collection `archives.002`
**Group:** [14-reference-hidden](../14-reference-hidden.md)

## What it does (code-level)
Identical structure to [029_archives.001.py](029-archives.001.md). One CURVE object `treeBody.075` wrapping curve datablock `Plane.011`, at origin with identity rotation/scale.

## Key data
- **Datablocks referenced**: curve `Plane.011` (birch trunk geometry, from `007_curves.py`).
- **Materials assigned**: none on curve directly.
- **Modifiers added**: none.
- **Custom properties**: none.
- **World positions**: origin.
- **Object types breakdown**: 1 CURVE.
- **Parent collection**: `archives.002` → under `birchTrees` in finalize. EXCLUDED.

## Technique / recipe
Same template pattern as `029_archives.001` but for birch species. Holds the editable source trunk curve; modify `Plane.011` and all birch trunks regenerate.

## Connections
- **Reads from**: `007_curves.py` (`Plane.011`).
- **Read by**: `034_references.py` and `135_birchTrees.001.py` (the visible/minimap birch trees use this curve).
- **Depends on**: 007, 013.
- **Depended on by**: 034, 135.

## Notable code patterns
- **Per-species curve datablock**: oak=`Plane.010`/`Plane.005`, birch=`Plane.011`/`Plane.008`, cherry=`Plane.004`/`Plane.007`. Each species has TWO planes: an "archive" template and a "placement" copy.
- Identical 21-line script structure — Bruno's exporter generates identical boilerplate per species.
