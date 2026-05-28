# 037_archives.py — cherry trunk source curve (EXCLUDED template)

**Path:** `folio-2025/scripts/blender_world_steps/steps/037_archives.py`
**Lines:** 21
**Adds:** 1 object (1× CURVE) to collection `archives`
**Group:** [14-reference-hidden](../14-reference-hidden.md)

## What it does (code-level)
Identical pattern to [029_archives.001.md](029-archives.001.md) and [033_archives.002.md](033-archives.002.md): one CURVE object `treeBody.073` wrapping curve datablock `Plane.004` at origin.

## Key data
- **Datablocks referenced**: curve `Plane.004` (cherry trunk source curve, from `007_curves.py`).
- **Materials assigned**: none on curve directly.
- **Modifiers added**: none.
- **Custom properties**: none.
- **World positions**: origin.
- **Object types breakdown**: 1 CURVE.
- **Parent collection**: `archives` → under `cherryTrees` in finalize. EXCLUDED.

## Technique / recipe
Same template pattern as oak/birch archives. The plain `archives` name (no `.NNN` suffix) suggests it was created FIRST during authoring (Blender's auto-naming gives the first collection its bare name, then `.001`, `.002` for duplicates) — so cherry was the first species Bruno set up, then he duplicated for oak (`archives.001`) and birch (`archives.002`).

## Connections
- **Reads from**: `007_curves.py` (`Plane.004`).
- **Read by**: `038_references.003.py`, `134_cherryTrees.001.py`.
- **Depends on**: 007, 013.
- **Depended on by**: 038, 134.

## Notable code patterns
- Per-species curve naming: oak=`Plane.010`, birch=`Plane.011`, cherry=`Plane.004`. Non-sequential because Bruno created them at different times. The runtime doesn't care about names — only datablock identity.
