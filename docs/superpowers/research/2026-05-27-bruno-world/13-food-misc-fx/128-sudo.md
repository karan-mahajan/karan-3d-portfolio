# 128_sudo.py — hidden rigged developer-mode character

**Path:** `folio-2025/scripts/blender_world_steps/steps/128_sudo.py`
**Lines:** 235
**Adds:** 4 objects (2× ARMATURE, 2× MESH) to collection `sudo`
**Group:** [13-food-misc-fx](../13-food-misc-fx.md)

## What it does (code-level)
Builds a hidden rigged "sudo" character + a `baguira` companion (the panther). Both share the same authoring pattern: armature object + a mesh with vertex-group skin weights + ARMATURE modifier.

1. `sudo.002` (ARMATURE, references `Armature.001`) at `(-14.11, 54.91, 1.41)` scale 0.865. No vertex groups (armatures don't have them).
2. `sudoMesh.002` (MESH `Cube.122`) at `(-14.11, 54.72, 1.45)` — defines 31 vertex groups by name (`'Bone'`, `'Bone.001'`, … `'Bone.025'`) and adds per-vertex weights via inline `_w` lists like `[[vertex_index, weight], …]`. Then attaches an `ARMATURE` modifier targeting `bpy.data.objects.get('sudo.002')`.
3. `baguiraMesh` (MESH `Cube.123`) at `(-11.38, 54.72, 1.45)` — same pattern but with **even more vertex groups + larger weight arrays** (panther rig). ARMATURE modifier targets `baguira` armature.
4. `baguira` (ARMATURE, references `Armature.002`) at `(-11.38, 54.91, 1.41)` scale 0.865.

## Key data
- **Datablocks referenced**: armatures `Armature.001` (sudo skeleton), `Armature.002` (baguira skeleton); meshes `Cube.122` (sudo body), `Cube.123` (baguira body).
- **Materials assigned**: via mesh data.
- **Modifiers added**: 2× ARMATURE (one per mesh, each binding to its sibling armature object).
- **Custom properties**: none.
- **World positions**: both clustered at `(-13, +55, 1.4)` — far north-northwest, social/statue zone. EXCLUDED until sudo command triggers.
- **Object types breakdown**: 2 ARMATURE, 2 MESH.
- **Parent collection**: `archives.003` (the rig source) per finalize.

## Technique / recipe
- **Inline vertex-group weights as Python literals** — Bruno's exporter dumped each `(vertex_index, weight)` pair into a `_w = [[vi, wt], …]` list and ran `for _vi, _wt in _w: vg.add([_vi], _wt, 'REPLACE')` per group. This recreates the entire skin-deformation rig without needing `.fbx` import — pure Python.
- **30+ vertex groups per mesh** (e.g., `Bone`, `Bone.001`, …, `Bone.025`) — full body rig including fingers (`hand.R.001..007`), spines, breasts, pelvis, etc.
- **ARMATURE modifier binding**: `m.object = bpy.data.objects.get('sudo.002')` — modifier explicitly looks up the sibling armature at run-time. Critical: the armature object must already exist before the mesh (it's defined first in the same script).
- **Two characters at once** (sudo + baguira) — sudo is the developer-character (hidden admin avatar), baguira is the panther companion. Both EXCLUDED from main render; visible only after sudo command.

## Connections
- **Reads from**: `008_armatures.py` (`Armature.001`, `Armature.002`), `005_meshes_*` (`Cube.122`, `Cube.123`).
- **Read by**: `999_finalize.py` (parents `sudoMesh.002`, `baguiraMesh` under their respective armatures; parents armatures under `archives.003`; sets view-layer EXCLUDE for `sudo`).
- **Depends on**: 008 (armature datablocks), 005 (mesh datablocks), 013 (collection skeleton), `127_archives.003.py` (parent collection).
- **Depended on by**: 999_finalize.

## Notable code patterns
- **Empty vertex groups created at end of sudo block**: `vg = ob.vertex_groups.new(name='Bone.019')` etc., with NO `for _vi, _wt …` loop following. These are placeholder groups (bones that exist on the armature but have no influenced verts on this mesh). The exporter preserves group ordering by creating empties to keep bone-index alignment.
- **Weight arrays are LONG**: sudoMesh `Bone.007` has 57 entries, `Bone.015` has 60. Baguira has even longer arrays (`Bone.007` has 100+ entries). Bruno's character meshes have deep weight painting.
- **Last bones use empty groups**: `Bone.020`, `Bone.021`, `Bone.022` etc. — likely tail/extra bones with no skin influence on the body mesh. The runtime still receives them for completeness.
- The 235-line script body is ~95% inline weight data, ~5% Blender API calls.
