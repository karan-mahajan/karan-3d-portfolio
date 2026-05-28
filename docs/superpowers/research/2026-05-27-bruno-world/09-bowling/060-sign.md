# 060_sign.py — hidden bezier-curve reference for the "Bowling" entry sign

**Path:** `folio-2025/scripts/blender_world_steps/steps/060_sign.py`
**Lines:** 27
**Adds:** 1 CURVE object to collection `sign`
**Group:** [09-bowling](../09-bowling.md)

## What it does (code-level)

Creates `sign` collection. Adds 1 CURVE object — hidden in all three modes (viewport, render, select):

```
signReference CURVE(refBowlingPin.001)
  at (-20.629, -34.843, 5.329)
  hide_viewport=True, hide_render=True, hide_select=True
```

The curve uses datablock `refBowlingPin.001` — which (despite the "Pin" name) is a CURVE datablock, not a mesh. The same datablock name appears in `bowling` root (052) where it's used as a MESH datablock for `sign.002`. Bruno reuses the name across data types: there's both a MESH `refBowlingPin.001` AND a CURVE `refBowlingPin.001` in his data.

## Key data

- **Datablocks referenced:** curve `refBowlingPin.001` (NOT the same as the mesh of the same name)
- **Materials assigned:** none on this object
- **Modifiers added:** none
- **Custom properties:** none
- **World positions of key anchors:** (-20.629, -34.843, 5.329) — far west of the bowling zone, at z=5.33 (elevated like other sign anchors)
- **Object types breakdown:** 1 CURVE
- **Parent collection:** `sign` (re-parented under `bowling/` by finalize)

## Technique / recipe

**Hidden curve as reference data:** the curve isn't rendered (hidden three ways). It serves as a template/source data block that the runtime instantiates or references when building the bowling sign.

Possible uses:
- The runtime extrudes 3D text along the curve to spell "BOWLING"
- The runtime instances pin-shaped meshes along the curve to spell out the sign
- It's a Z-position alignment guide for the entry signage

**`signReference` naming** — `Reference` suffix = "this is a source/template, not for direct render." Matches the `archive*` prefix pattern (see 073_rails.py, 070_leaderboardReset.py).

**Position 5.33m elevated** — same height as `sign.001`/`sign.002` in `052_bowling.py` (which sits at (25.28, -65.82, 5.33)). Bruno uses z≈5.3 consistently for sign mountings.

**Smallest script in the bowling section** (27 lines, 1 object). Demonstrates extreme minimalism — one hidden data anchor is all the sign collection needs because the visible sign meshes already live in `bowling` root.

## Connections

- **Reads from:** `007_curves.py` (curve datablock `refBowlingPin.001`)
- **Read by:** `999_finalize.py` (parents `sign/` under `bowling/`)
- **Depends on:** `052_bowling.py` (bowling zone exists, has the visible sign meshes)
- **Depended on by:** runtime sign-building logic (probably reads this curve template)

## Notable code patterns

- **Mesh and curve sharing the SAME datablock name (`refBowlingPin.001`)** — Blender's name-spacing per data type allows this. The mesh and curve are entirely separate datablocks despite the matching string name.
- **`hide_viewport=True, hide_render=True, hide_select=True`** — Bruno's full-hide combo. The `hide_select=True` prevents accidental selection in the viewport even if it were ever shown.
- **Single CURVE object** — the only "sign" Bruno needs at this level is the curve template. The visible mesh-based pin signs are in `bowling` root collection.
- **Tiny script (27 lines)** — efficient minimalism. Bruno's scripts scale to the actual content; they don't dump boilerplate.
