# 005_meshes_04.py — mesh datablock chunk 5 of 7 (60 datablocks)

**Path:** `folio-2025/scripts/blender_world_steps/steps/005_meshes_04.py`
**Lines:** 770
**Adds:** 60 mesh datablocks
**Group:** [01-foundation](../01-foundation.md)

## What it does

Same template as [005-meshes-00.md](005-meshes-00.md).

## Mesh datablocks in this chunk (60)

Continues the `Plane.NNN` sequence:

`Plane.029..063`, `Plane.065..073`, `Plane.075..079`, `Plane.081..084`, `Plane.087`, `Plane.088`, `Plane.090`, `Plane.091`, `Plane.093..095`.

All 60 are `Plane.*`. Bruno's world is **heavy on planes** — flat decals, screens, signs, billboards, road segments, water-surface decals, carpet quads, blackboard panels, billboard placards. The "Plane" primitive is the most-reused datatype after Cube.

## Key data

- **Materials touched**: `blackboardLabels`, `careerTextHetic`, `careerTextImmersive`, `careerTextOnlineTeacher`, `emissiveOrangeRadialGradient`, `emissivePurpleRadialGradient`, `emissiveWhiteRadialGradient`, `gray`, `palette`, `projectsLabels`, `redGradient`.
  - First chunk with `careerText*` materials: this chunk holds the **career-text label planes** — small framed plaques displaying each career artifact (Hetic, ImmersiveGarden, OnlineTeacher).
  - `blackboardLabels` and `projectsLabels` here = blackboard prop's text decal + the projects-area label plane.
- **Modifiers**: none.
- **Custom properties**: none on meshes.
- **World positions**: baked.
- **Object types**: 0.
- **Parent collection**: n/a.

## Technique / recipe

See [005-meshes-00.md](005-meshes-00.md#technique--recipe).

For the career-text and label planes, the UVs are crafted to fit each PNG label exactly. Each plane is one quad with 4 UV corners mapped to (0,0)-(1,1) of its texture image — visible because each `me.materials.append(careerText<name>)` is paired with a Plane whose UVs span the full image.

## Connections

- **Reads from**: 004_materials.
- **Read by**: career-text scripts (the career artifacts under behindTheScene, scripts in the 11-furniture-displays-boards group), labels in projects + blackboard sections.
- **Depends on**: 000_init, 004_materials.
- **Depended on by**: 020-139.

## Notable code patterns

- **All-Plane chunk**: 60 planes in a row demonstrates how many flat surfaces Bruno's world needs.
- **Three careerText materials in this chunk** (Hetic, Immersive, OnlineTeacher) — the other three careerText materials (Freelancer, IRLTeacher, Uzik) attach to planes in chunk 05.
- All other patterns from [chunk 00](005-meshes-00.md) apply.
