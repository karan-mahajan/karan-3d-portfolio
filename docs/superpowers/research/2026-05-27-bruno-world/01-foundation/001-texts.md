# 001_texts.py — embed 3 helper Python text blocks in the .blend

**Path:** `folio-2025/scripts/blender_world_steps/steps/001_texts.py`
**Lines:** 14
**Adds:** 3 `bpy.data.texts` datablocks (embedded code snippets, no scene objects)
**Group:** [01-foundation](../01-foundation.md)

## What it does (code-level)

Creates three Text datablocks via `bpy.data.texts.new(name)` and populates each with a small Python snippet using `t.from_string(...)`. Each gets `use_fake_user = True` so Blender keeps the text saved in the .blend even if nothing references it.

The three texts:

1. **`changeViewportColor`** — Loops every object in the active layer-collection and sets `obj.color = (0.229465, 1, 0.893311, 1)` (a teal-cyan tint). Used to color-tag a collection's contents for visual sorting in the viewport.
2. **`getRelativeLocation`** — Prints the active object's location relative to its parent: `local_matrix = obj.parent.matrix_world.inverted() @ obj.matrix_world; local_position = local_matrix.to_translation()`. Handy for reading out a child's offset when authoring scene scripts.
3. **`getWhispersForbiddenAreas`** — Body is the single character `'s'`. Looks like an empty stub or placeholder Bruno hasn't filled in yet. (The name suggests it would compute zones for an in-world "whispers" audio system.)

## Key data

- **Datablocks referenced**: none — pure creation
- **Materials assigned**: n/a
- **Modifiers added**: n/a
- **Custom properties**: n/a (texts themselves are the property)
- **Object types breakdown**: 0 — texts are datablocks, not scene objects
- **Parent collection**: n/a — text datablocks live in `bpy.data.texts`, not in any scene collection

## Technique / recipe

The "in-blend Python notebook" pattern:

- Treat the .blend as a self-contained authoring environment. Snippets you regularly run when editing the world ship with the file.
- `use_fake_user = True` is the key flag — without it, Blender garbage-collects any text not referenced by a script-controller or driver, and these would disappear on next save.
- Names act as a quick UI menu: open the Text editor in Blender, pick from the dropdown, hit "Run Script."
- No coupling: the texts are isolated dev tools. None of the 020+ scripts read or execute them.

## Connections

- **Reads from**: nothing
- **Read by**: nothing (in the build pipeline). They're for **the human editor** opening the .blend interactively.
- **Depends on**: 000_init.py wiping `bpy.data.texts` first
- **Depended on by**: nothing

## Notable code patterns

- **`use_fake_user = True`**: standard trick for keeping otherwise-unreferenced datablocks alive across saves.
- **`from_string()`**: the canonical API for populating a text block in one shot — alternative would be `t.write()` per line, more verbose.
- The script lives at script position 001 (very early in the pipeline) but is entirely orthogonal to world construction — it's pure dev-ergonomics. Anyone re-running the pipeline can keep or skip this script without affecting render output.
- **The stub `'s'` body** in `getWhispersForbiddenAreas` is worth flagging — Bruno ships unfinished helper text blocks in the public .blend. Suggests these are real, in-progress dev tools and not a polished "demo" set.
