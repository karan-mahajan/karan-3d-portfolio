# 008_armatures.py — 6 armature (bone hierarchy) datablocks

**Path:** `folio-2025/scripts/blender_world_steps/steps/008_armatures.py`
**Lines:** 919
**Adds:** 6 armature datablocks (no scene objects yet)
**Group:** [01-foundation](../01-foundation.md)

## What it does (code-level)

Each armature follows this construction pattern:

```python
arm = bpy.data.armatures.new('<name>')
_tmp = bpy.data.objects.new('__arm_tmp__', arm)        # temp object to enter EDIT mode
bpy.context.scene.collection.objects.link(_tmp)
bpy.context.view_layer.objects.active = _tmp
bpy.ops.object.mode_set(mode='EDIT')                    # bones can only be edited in EDIT mode
# for each bone:
eb = arm.edit_bones.new('<boneName>')
eb.head = (x, y, z); eb.tail = (x, y, z)
import mathutils as _mu
try: eb.matrix = _mu.Matrix([(row0), (row1), (row2), (row3)])
except Exception: pass
# ... parenting:
arm.edit_bones['<child>'].parent = arm.edit_bones['<parent>']
# ...
bpy.ops.object.mode_set(mode='OBJECT')                  # exit EDIT
bpy.context.scene.collection.objects.unlink(_tmp)
bpy.data.objects.remove(_tmp)                           # destroy the temp object — armature data persists
arm.name = '<name>'
```

The `__arm_tmp__` temp object dance is required because **Blender only allows editing armature bones via `arm.edit_bones` while an object referencing the armature is in EDIT mode**. Bruno creates a throwaway object, enters EDIT mode on it, builds all the bones, exits to OBJECT mode, then deletes the temp object — leaving just the named armature datablock in `bpy.data.armatures`.

## The 6 armatures

| # | Name | Bones | Notes |
|---|---|---:|---|
| 1 | `Armature.001` | 19 | Generic-named bones (`Bone`, `Bone.001..018`). Hierarchy: chain of spine `Bone → .001 → .002 → .007` with branches at `.007` going `.015 → .016` (left arm?) and `.017 → .018` (right arm?), plus dual leg-ish branches off `.001` (`.008 → .010 → .012` and `.009 → .011 → .013`), and head/tail-ish bones (`.003 → .005`, `.004 → .006`, `.014`). Topology suggests a small bipedal critter rig (15+4 = 19 bones total). |
| 2 | `Armature.002` | 26 | Similar generic-named bone set, more bones — likely a more detailed character variant. |
| 3 | `Armature.003` | 19 | Same bone count as `.001`; probably a duplicate/variant pose. |
| 4 | `Armature.006` | 19 | Same bone count again; another duplicate/variant. |
| 5 | `Armature.007` | 61 | Big rig with many bones — full-body, possibly with fingers. |
| 6 | `metarig.001` | 144 | **Rigify metarig** — Blender's standard human starting rig. Has named bones: `spine`, `spine.001..006`, `shoulder.L/R`, `upper_arm.L/R`, `upper_arm.R.001`, `forearm.L/R`, `hand.L/R`, `hand.R.001..007` (= 7 finger joints), `breast.L/R`, and ~120+ more. The `.001..007` suffixes on `hand.R` are finger-joint chains. This metarig hasn't been processed by Rigify yet (no `MCH-`/`DEF-`/`ORG-` prefixes) — Bruno just authored the metarig with intent to either generate a Rigify rig or use as-is. |

## Key data

- **Datablocks referenced**: none (pure data creation).
- **Materials assigned**: n/a (armatures don't have materials).
- **Modifiers added**: none.
- **Custom properties**: none set on armature or bone datablocks in this script (Rigify usually adds them on the rig output, which doesn't exist yet).
- **World positions of key anchors**:
  - `Armature.001`'s root `Bone` head is `(~0, -0.045, 0.014)` — near origin, slight Y/Z offset.
  - `metarig.001`'s `spine` bone head is `(0.0007, 0.153, -0.245)` — near origin, hip-height (~25cm below).
  - Both are at the world origin. Their owner objects (in 020+) will translate them to final placement.
- **Object types breakdown**: 0 (no permanent scene objects — the `__arm_tmp__` objects are cleaned up).
- **Parent collection**: n/a.

## Technique / recipe

The "armature datablock pre-bake" pattern:

- **Bones can only be added in EDIT mode**, but EDIT mode requires an object selected. Solution: create a throwaway object, enter EDIT, build bones, exit, delete the object. The bones persist on the armature datablock alone.
- **`eb.head` + `eb.tail` define the bone's position and direction**. Both in armature-local space.
- **`eb.matrix` overrides the default head→tail orientation** — gives the bone an arbitrary 4×4 transform (rotation + position). The 4th row is always `(0, 0, 0, 1)`. This is how Bruno preserves exact rotations from the source .blend (some bones rotate around an axis the head→tail vector wouldn't capture).
- **Parenting via `eb.parent = ...`**: must happen AFTER all bones are created (forward references would otherwise fail).
- **`bpy.ops.object.mode_set(mode='EDIT')` requires `bpy.context.view_layer.objects.active = _tmp`**: Blender's mode-switch operates on the active object. Hence the explicit `active = _tmp` before mode-switching.
- **Rigify metarig conventions**: `spine`, `spine.001..006` (6 spine segments + base = 7), `shoulder.L/R`, `upper_arm.L/R + .001`, `forearm.L/R + .001`, `hand.L/R + .001..007` (7 finger bones), `breast.L/R`. Each `.L` and `.R` suffix tells Rigify to mirror the bone during rig generation. The `metarig.001` here is a fully-authored human metarig ready to be processed by Rigify into a full IK/FK rig. Whether Bruno actually runs Rigify isn't visible from this script alone.

## Connections

- **Reads from**: nothing.
- **Read by**: scripts that create scene objects with `type='ARMATURE'` and bind one of these armatures as the object's data. The group .md says these are used by:
  - **statue character** (script 106) — likely uses one of `Armature.001..006`
  - **sudo character** (script 128) — likely uses another
  - **metarig.001** is probably the source rig for any character that's been Rigify-processed
- **Depends on**: 000_init (wipe of `bpy.data.armatures`).
- **Depended on by**: 106 (statue), 128 (sudo), other character scripts.

## Notable code patterns

- **EDIT-mode dance for armature creation**: this is the canonical Blender Python idiom for armature datablock construction. The throwaway object pattern is unavoidable.
- **`import mathutils as _mu` inside the loop**: imported once per bone. Slightly wasteful (re-imports are cached after the first), but kept for readability — every bone block is self-contained.
- **Custom bone matrices preserve exact rotations**: instead of computing rotation from head→tail (which gives Blender's default Y-up bone orient), Bruno feeds the full 4×4. This means some bones have non-Y-aligned roll/yaw that the head/tail vector alone can't express.
- **Bone naming irregularity**: `Armature.001` uses generic `Bone`, `Bone.001`, ..., `Bone.018` with skips (`.001 → .002 → .007 → .015 → ...`). Like meshes, gaps reflect deleted-and-never-compacted state.
- **`metarig.001` is a 144-bone Rigify metarig** — by far the largest armature. This single datablock is most of the 919-line file.
- **No animations / no actions assigned in this script**: armatures hold bone hierarchies only. Actions live in `bpy.data.actions` — wiped by 000 but not created by 008. Bruno's runtime characters likely don't have Blender-baked animations; movement comes from game-engine animation in JS.
- **`bpy.ops.object.mode_set`**: one of the few operators (vs raw API calls) Bruno uses anywhere in the build scripts. He avoids `bpy.ops.*` elsewhere because they depend on context; here it's mandatory for mode switching.
- **Six armatures suggests multiple character variants**: 1 metarig + 5 finished armatures could be the metarig plus 5 character pose variants (e.g., statue idle / statue pose A / sudo idle / sudo pose A / extra). Worth confirming when reading 106/128 in batch 4.
