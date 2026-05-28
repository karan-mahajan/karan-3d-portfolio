# 086_scroller.py — chain-and-gears scrolling display with ARRAY-modifier mechanism

**Path:** `folio-2025/scripts/blender_world_steps/steps/086_scroller.py`
**Lines:** 296
**Adds:** 14 objects (11 MESH, 3 EMPTY) to collection `scroller`
**Group:** [11-furniture-displays-boards](../11-furniture-displays-boards.md)

## What it does (code-level)

Creates `scroller` collection — the **lab's animated scrolling info display** with mechanical chains and gears:

**Display frame:**

| Object | Type | Mesh | Notes |
|---|---|---|---|
| `panel.001` | MESH | `Cube.177` at (-41.03, 18.56, 2.81) — backing panel |
| `Cube.166` | MESH | `Cube.178` at (-41.00, 18.63, 3.19) — title/header block above the panel |
| `image` | MESH | `Cube.142` at (-41.00, 18.62, 3.19) — image plane co-located with `Cube.166` |
| `text.008` | MESH | `Plane.069` at (-40.99, 19.34, 2.85), rotX=1.571, rotZ=0.524 — body text |
| `intersect` | MESH | `Plane.070` at (-41.83, 19.20, 3.30), rotX=1.571, rotZ=0.524, scale=0.707 — interactive raycast plane |

**Chain mechanism** (ARRAY-modifier chains):

| Object | Type | Mesh | Modifier |
|---|---|---|---|
| `refChainRight` | MESH | `Cube.172` at (14.43, -12.68, 0.0), rotZ=0.524 | **ARRAY count=9**, relative_offset_z=0.8 — creates a 9-link vertical chain |
| `refChainLeft` | MESH | `Cube.173` at (13.54, -13.20, 0.0), rotZ=0.524 | **ARRAY count=9**, relative_offset_z=0.8 — second 9-link chain (mirrored) |
| `refChainPulley` | MESH | `Cube.184` at (13.98, -12.94, 4.05), rotZ=0.524 | **ARRAY count=6** with `use_object_offset=True`, `offset_object=chainPulleyArrayReference` — 6 pulley wheels arrayed around an empty's transform |

**Pulley + gears mechanism:**

| Object | Type | Mesh | Notes |
|---|---|---|---|
| `chainPulleyArrayReference` | EMPTY/PLAIN_AXES | — | (13.98, -12.94, 4.05), rotY=-1.047 (-60°) — used as the ARRAY offset reference for refChainPulley |
| `refMini` | EMPTY/PLAIN_AXES | — | (13.47, -13.33, 2.84) — "miniature" anchor (smaller debug pulley?) |
| `refMecanism` | EMPTY/PLAIN_AXES | — | (13.99, -12.99, 2.20) — main mechanism anchor |
| `refGearA` | MESH | `Gear.005` at (14.15, -13.24, 4.045), rotX=1.571 — first gear with **vertex groups Tips + Valleys** (12 Tips verts paired) |
| `refGearB` | MESH | `Gear.008` at (13.66, -13.53, 4.045), rotX=1.571, rotY=-0.253 — second gear with **larger vertex groups** (36 Tips pairs) |
| `refGearC` | MESH | `Gear.015` at (13.28, -13.86, 4.322), rotX=1.571 — third gear with **largest vertex groups** (47 Tips pairs) |

## Key data

- **Datablocks referenced:** 8 meshes (Cube.142, Cube.166→Cube.178, Cube.172/.173/.184, Plane.069/.070, Gear.005/.008/.015) and 1 empty as ARRAY offset reference
- **Materials assigned:** `palette` (per group .md, the only material across all 14 objects)
- **Modifiers added:** **3× ARRAY** (on refChainRight, refChainLeft, refChainPulley) — Bruno's signature scrolling/repeating technique
- **Custom properties:** none
- **World positions of key anchors:**
  - Visible scroller panel at (-41.03, 18.56) — lab zone
  - Chain + gear meshes at staging (13-14, -12 to -14, varying z) — runtime applies the lab transform
- **Object types breakdown:** 11 MESH, 3 EMPTY
- **Parent collection:** `scroller` (re-parented under `lab/` by finalize)

## Technique / recipe

**Animated chain-driven scrolling display:**

1. **Display frame at the lab position** (-41.03, 18.56) — backing panel + title block + image + text + invisible click plane.
2. **Two parallel chains** (refChainLeft + refChainRight), each created by an ARRAY modifier with **count=9, relative_offset_z=0.8** — 9 chain links stacked vertically with 80% Z spacing between each. Result: a 7.2-link-height chain (each link's Z extent counted minus the 20% overlap).
3. **Pulley chain** (refChainPulley) using a **DIFFERENT array mode**: `use_object_offset=True` with `offset_object=chainPulleyArrayReference` (rotated -60° around Y). This rotates each subsequent pulley link around the empty's pivot — creates an **arced/curved chain wrapping around a virtual pulley wheel** (6 links around a hex-arc).
4. **Three gears** (refGearA/B/C) of escalating tooth counts (12 / 36 / 47 vertex-pairs). Each gear has a `Tips` vertex group (the outer points of each tooth) and a `Valleys` vertex group — the runtime likely animates these for tooth-meshing.
5. **`chainPulleyArrayReference` empty** is the **rotation center** for the curved pulley chain. By rotating this empty in the runtime, the chain links wrap differently → the chain can be animated to scroll.

**ARRAY-modifier mechanism scrolling:**
- The two straight chains (refChainRight, refChainLeft) form a vertical "belt"
- The curved pulley chain wraps around the gears at the top
- Three gears with `Tips`/`Valleys` vertex groups likely drive the animation: rotating the gear updates the curve along which the chain follows

**Vertex groups `Tips` and `Valleys`** on gears — the runtime knows where the gear teeth and gear valleys are. This is for **mesh deformation** (chain links bend at the gear-tooth positions) or **chain link snapping** (each link's position is locked to a gear tooth).

**`intersect` plane** (`Plane.070`) with `display_type='WIRE'` — invisible interactive plane for click-detection on the scroller display.

**`refMini` and `refMecanism` anchors** — runtime hooks for sub-systems within the scroller.

## Connections

- **Reads from:** `005_meshes_*.py` (8 meshes including 3 Gear.* meshes), no node groups
- **Read by:** `999_finalize.py` (parents `scroller/` under `lab/`)
- **Depends on:** `081_lab.py` (parent zone)
- **Depended on by:** runtime chain animation system, gear rotation animation

## Notable code patterns

- **3 ARRAY modifiers in one script** — Bruno's heaviest ARRAY usage so far. Two use `relative_offset` (constant pixel/unit-spaced repetition); one uses `use_object_offset` + an empty as the offset transform (rotational/translational repetition around a pivot).
- **`use_object_offset=True` on the pulley chain** is the **clever trick**: by rotating `chainPulleyArrayReference`, each ARRAY-cloned chain link is rotated incrementally around the empty's pivot. 6 links × -60°/link = -360° = a full pulley wheel.
- **Vertex groups Tips + Valleys on each gear** — supplies named vertex sets for runtime to use. The hardcoded vertex-index lists (e.g., `[[4,1.0],[5,1.0],...]` for `Tips`) name pairs of consecutive vertices (each tooth has 2 outer points). This is **mesh-data-driven animation hooks**.
- **3 gears of escalating tooth counts** — Bruno's complete gear train (small → medium → large), so the runtime can wire up gear meshing animations.
- **All 3 ARRAY-modifier meshes at z≈0** in staging — they pile up at the staging origin, runtime applies the lab transform.
- **Chain offset 0.8 (relative)** — 80% offset means each link overlaps the previous by 20%, simulating physical chain link interlocking.
- **`refChainPulley` arc count=6** with -60° per link = exactly 360° total = a complete loop around the pulley. Bruno mathematically pre-tuned the arc.
- **Wire-display `intersect` plane** — same trick as 083: invisible raycast plane for clicks.
