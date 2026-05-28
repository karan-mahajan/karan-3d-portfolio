# 046_archive.001.py — single metaball reference (EXCLUDED + HIDDEN)

**Path:** `folio-2025/scripts/blender_world_steps/steps/046_archive.001.py`
**Lines:** 21
**Adds:** 1 object (1× META) to collection `archive.001`
**Group:** [14-reference-hidden](../14-reference-hidden.md)

## What it does (code-level)
- Gets/creates collection `archive.001`.
- Creates ONE object `azeazeaze` (placeholder/keysmash name — clearly Bruno's prototyping artifact) of type **META** (Metaball), wrapping metaball datablock `Mball.005`.
- Location `(71.16, -11.01, 5.96)`, rotation `(0, -0, 0.262)` (~15° z-rotation), scale (1, 1, 1).

## Key data
- **Datablocks referenced**: metaball `Mball.005` (from `006_metaballs.py`).
- **Materials assigned**: via metaball data.
- **Modifiers added**: none.
- **Custom properties**: none.
- **World positions**: `(71.16, -11.01, 5.96)` — far east, elevated. Distinctive location, but EXCLUDED and HIDDEN so not visible.
- **Object types breakdown**: 1 META.
- **Parent collection**: `archive.001` (note: SINGULAR `archive`, distinct from the `archives.NNN` tree templates). Per finalize, EXCLUDED with `hide_viewport=True`.

## Technique / recipe
- **Metaball as data anchor**: Bruno keeps a metaball in the .blend (maybe used during authoring for sculpting reference, or as the source of a baked mesh). Now hidden+excluded — it's an archived prop, kept for traceability but not rendered.
- The keysmash name `azeazeaze` is a Bruno trademark — appears in some test/temp objects in his world. He didn't clean it up before exporting. (Equivalent to leaving `console.log('TEST')` in code.)

## Connections
- **Reads from**: `006_metaballs.py` (`Mball.005`).
- **Read by**: `999_finalize.py` (sets view-layer EXCLUDE + HIDE).
- **Depends on**: 006, 013.
- **Depended on by**: nothing.

## Notable code patterns
- **Singular `archive` collection** (no `.NNN`) vs the plural `archives.NNN` trees — naming distinction Bruno preserves but might confuse readers. Watch the singular vs plural.
- Metaball is the ONLY type=META object in the world. It's a rare datatype.
- HIDDEN status (in finalize view-layer settings: `hide_viewport=True`) is rare — most EXCLUDED collections are simply excluded, this one is doubly hidden.
