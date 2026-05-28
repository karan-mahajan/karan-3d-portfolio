# 15 — Finalize (parenting + view-layer + scene wiring)

**Bruno category:** Finalize
**Scripts:** 1 (999)
**Total objects:** 0 (this script only modifies relationships, doesn't add objects)
**Status:** required final step

---

## Purpose

After all 141 prior scripts have placed objects into collections, **`999_finalize.py` wires the whole world together**:
- Applies object parenting for all 1,507 objects (+ matrix_parent_inverse so transforms stay correct)
- Sets view-layer collection excludes (which 23 collections are hidden from main render — the EXCLUDED status seen in the index)
- Links the scene compositor
- Sets the active camera
- Fixes up node-tree datablock references (e.g., object/collection sockets in geometry nodes)
- Sets the frame range and render engine

This is the script that makes the world "feel like one thing" instead of 120 disconnected collections.

---

## What it does (per the index)

| Step | Count | What |
|---|---:|---|
| Object parenting | 1,507 objs | Each object gets its `parent`, `parent_type`, `parent_bone` (if any), and `matrix_parent_inverse` set. This is the BIG one — sections become movable as wholes |
| View-layer excludes | 23 collections | Hides reference/backup collections (`*.001` tree copies, `map`, `altar.001`, etc.) from the main camera but keeps them visible to the minimap rig |
| Compositor link | 1 | Hooks the compositor node tree into the scene |
| Active camera | 1 | Sets which camera the scene renders from |
| Node-ref fixups | many | Geometry-nodes modifiers have sockets that point at specific objects/collections — these refs can be lost during the additive-build process; finalize re-binds them |
| Frame range, render engine | — | Sets playback range, ensures the right render engine is active |

---

## File stats

- **4,381 lines, 321 KB.** This is by far the biggest single script in the world (next-biggest is `005_meshes_05.py` at 4.4 MB but mostly raw mesh data).
- Why so large? **1 line per parenting relationship**, times 1,507. Plus matrix corrections, plus all the node-ref fixups.

---

## Why this script is critical

### Parenting drives the visual hierarchy
- Before finalize, every object sits at its world-space transform but has no parent.
- After finalize, props are parented under their zone's empty (`mainTable` → `lab`, `pins` → `bowling`, `cones` → `circuit`, etc.).
- This means **moving a zone's anchor empty translates the entire zone's contents**. Bruno can pick up `bowling` and drop it anywhere on the island without re-positioning 13+ props.

### View-layer excludes drive what's visible
- Without finalize, all 142 scripts' contents would be visible — the world would look broken (template trees overlapping real trees, minimap altar floating next to real altar, etc.).
- Finalize sets 23 collections to "excluded" from the main view layer:
  - The `.001` tree copies (134, 135, 136) — only minimap should see these
  - `archives.*` curve sources (029, 033, 037) — invisible templates
  - `altar.001`, `behindTheScene.001` — map-portal stand-ins
  - `vehicle.001` (137) — template vehicle source
  - The easter/egg/tornado/whispers/sudo content — hidden until runtime-triggered
  - `map` (131) — the minimap rig itself
- Result: the main camera sees a clean composed scene; the minimap camera sees its specific subset.

### Node-ref fixups (the subtle one)
- Bruno's geometry-nodes modifiers (terrain, grass, rails) have "input sockets" that point at specific scene objects or collections (e.g., the grass-scatter modifier needs to know which object IS the grass mesh).
- During the additive build, those refs may be `None` until both the source AND target exist. Finalize re-binds them after every object is in place.

### Compositor link
- The compositor's `terrain` CompositorNodeTree (loaded in 003) is wired into the scene's compositor output here. This is what gives the rendered output its final color-grading/post-processing pass.

---

## What happens if you skip finalize?

- Sections don't move as units (no parenting)
- Template/reference content is visible in the main camera (overlapping geometry, double trees)
- Geometry-nodes modifiers may show "missing reference" errors
- The compositor isn't wired (raw renderer output, no post-processing)
- No active camera set

The build LOOKS broken without it. Bruno's README explicitly says: "End with `999_finalize.py` to apply parenting and view-layer visibility."

---

## Why this is interesting for the Bruno-world picture

- **The world is "fragile" until finalize runs.** This means the additive build is decoupled from the final scene composition — Bruno can re-run any single script (e.g., 057 to update pins) without touching the parenting/visibility setup. Only finalize touches those.
- **Re-running finalize is idempotent** (per the README) — safe to run multiple times.
- **The parenting tree is the SECOND organizing axis of the world.** Collections are the first axis (groupings by category), parenting is the second (zone-based hierarchies). Both matter, and finalize defines the second.

---

## Source pointers

- Step script: `folio-2025/scripts/blender_world_steps/steps/999_finalize.py` (4,381 lines, 321 KB)
- Compositor node tree (in 003): `terrain` CompositorNodeTree
- View-layer behavior: Blender's `View Layer → Collection Exclude` panel
- Bruno's runtime equivalent: vanilla three.js scene composition in `folio-2025/sources/Game/`
