# 029_archives.001.py — oak trunk source curve (EXCLUDED template)

**Path:** `folio-2025/scripts/blender_world_steps/steps/029_archives.001.py`
**Lines:** 21
**Adds:** 1 object (1× CURVE) to collection `archives.001`
**Group:** [14-reference-hidden](../14-reference-hidden.md)

## What it does (code-level)
Three-step boilerplate:
1. Gets/creates collection `archives.001`.
2. Creates ONE object `treeBody.074` (type=CURVE) wrapping curve datablock `Plane.010`, at origin `(0, 0, 0)` with identity rotation and scale.
3. Idempotently links into the collection.

That's the whole file.

## Key data
- **Datablocks referenced**: curve `Plane.010` (loaded by `007_curves.py`).
- **Materials assigned**: none on the curve directly; the visible oak trees that USE this curve apply `palette` via geometry-nodes resolution.
- **Modifiers added**: none.
- **Custom properties**: none.
- **World positions**: at origin (0, 0, 0) — this is a TEMPLATE curve, not a placed visible asset.
- **Object types breakdown**: 1 CURVE.
- **Parent collection**: `archives.001`, which is parented under `oakTrees` collection by finalize and EXCLUDED from view layer.

## Technique / recipe
- **"Template curve at origin" pattern**: this is the SOURCE curve geometry for oak tree trunks. Bruno authored one trunk shape (`Plane.010` curve) and uses it as the "source of truth" for all oak trunk extrusions.
- Other oak-tree scripts ([030_references.002.py](030-references.002.md) and [134_oakTrees.001](../04-trees/) — the visible final-instance trees) reference this curve through their geometry-nodes modifiers OR by duplicating curve objects pointing at the same datablock.
- **EXCLUDED from view layer** — Bruno doesn't want this raw template visible at runtime; it only exists in the .blend for editability. Modify `Plane.010` and ALL oak trees regenerate.

## Connections
- **Reads from**: `007_curves.py` (curve `Plane.010`).
- **Read by**: `030_references.002.py` (24 oak trunk scatter curves all reference `Plane.010`), `136_oakTrees.001.py` (minimap-ready oak trees), finalize.
- **Depends on**: 007 (curves), 013 (collections).
- **Depended on by**: 030, 136 (per the tree-template pattern).

## Notable code patterns
- **Naming `treeBody.074`** despite this being a TEMPLATE — the `.074` suffix is from Bruno's authoring history (Blender auto-suffixes on duplication). Naming inconsistency is fine because runtime references curves by their data, not their object name.
- The CURVE datablock name `Plane.010` is a Blender auto-name (started as a Plane mesh, was converted to curve, kept the name). Bruno doesn't rename datablocks systematically.
- **Tree-template trinity per species**: `archives.NNN` (1 curve) + `references.NNN` (20-26 placement instances) + `visual.NNN` (7 leaf-cluster meshes). This same trinity exists for oak (029/030/031), birch (033/034/035), cherry (037/038/039).
