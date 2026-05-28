# 011_linestyles.py — 1 freestyle linestyle datablock (placeholder)

**Path:** `folio-2025/scripts/blender_world_steps/steps/011_linestyles.py`
**Lines:** 10
**Adds:** 1 linestyle datablock (no scene objects)
**Group:** [01-foundation](../01-foundation.md)

## What it does (code-level)

```python
if 'LineStyle' not in bpy.data.linestyles:
    ls = bpy.data.linestyles.new('LineStyle')
else:
    ls = bpy.data.linestyles['LineStyle']
ls.use_fake_user = True
```

Creates (or reuses) a single freestyle line-style datablock named `LineStyle` with `use_fake_user = True` (persists in the .blend even when nothing references it).

**Nothing else is set.** All line-style properties (color, thickness, dash pattern, alpha curve, geometry modifiers) keep Blender's defaults.

## Key data

- **Datablocks referenced**: none.
- **Materials assigned**: n/a.
- **Modifiers added**: n/a.
- **Custom properties**: none.
- **World positions**: n/a.
- **Object types breakdown**: 0.
- **Parent collection**: n/a.

## Technique / recipe

This is essentially a **stub / placeholder**. Bruno's runtime renderer is Three.js, not Cycles/EEVEE — freestyle line styles only matter for Blender-side rendering of stylized outlines. The script's only purpose is to keep a `LineStyle` datablock in the .blend so the file's freestyle settings (which may reference it from a view layer) don't error out.

## Connections

- **Reads from**: nothing.
- **Read by**: nothing visible in the build scripts — but the .blend's freestyle view-layer settings may reference it.
- **Depends on**: 000_init (wipe of `bpy.data.linestyles`).
- **Depended on by**: nothing concrete in the per-section scripts. The runtime ignores freestyle entirely.

## Notable code patterns

- **Smallest non-trivial script in the pipeline** (10 lines).
- **`use_fake_user`** is the only meaningful flag — without it, Blender would garbage-collect the unreferenced linestyle on next save.
- **`'LineStyle'` name is Blender's default** — Bruno never renamed it. Confirms placeholder status.
- **Idempotency via `if 'LineStyle' not in ...`** rather than the `get() or new()` pattern used elsewhere. Slightly different idiom but same effect.
- This script tells us: **Bruno doesn't render outlines via freestyle.** Any stylized outlines visible in-game come from the Three.js runtime (probably a post-process shader, not freestyle).
