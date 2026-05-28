# 058_pinsPosition.py — 10 cylindrical-axis empties marking pin spawn positions

**Path:** `folio-2025/scripts/blender_world_steps/steps/058_pinsPosition.py`
**Lines:** 169
**Adds:** 10 EMPTY objects (all PLAIN_AXES) to collection `pinsPosition`
**Group:** [09-bowling](../09-bowling.md)

## What it does (code-level)

Creates `pinsPosition` collection. Adds 10 EMPTY anchor objects all named `cylinder.025` through `cylinder.034`. All share:

- **Type**: EMPTY, `empty_display_type='PLAIN_AXES'`, `empty_display_size=0.5`
- **z = 2.515** (elevated above the lane surface — these mark where pins should spawn from)
- **rotation_euler.X = -π** (rotated 180° around X — pins drop facing the right way?)
- **scale = (0.636, 0.636, 1.415)** (uniform across all 10 — matches the pin's collider proportions from 057_pins)

Positions form a classic 4-3-2-1 bowling triangle in the (-36 to -41 X, -34 to -39 Y) area:

| Empty | (x, y) | Triangle Row |
|---|---|---|
| `cylinder.025` | (-36.90, -36.96) | Row 1 (head pin) |
| `cylinder.026` | (-38.05, -37.68) | Row 2 |
| `cylinder.028` | (-38.05, -36.24) | Row 2 |
| `cylinder.027` | (-39.19, -36.96) | Row 3 |
| `cylinder.029` | (-39.19, -38.41) | Row 3 |
| `cylinder.030` | (-39.19, -35.52) | Row 3 |
| `cylinder.031` | (-40.37, -36.24) | Row 4 |
| `cylinder.032` | (-40.37, -37.68) | Row 4 |
| `cylinder.033` | (-40.37, -34.79) | Row 4 |
| `cylinder.034` | (-40.37, -39.13) | Row 4 |

X-spacing between rows: ~1.16m. Y-spacing within rows: ~1.44m. Same dimensions as the `pin0`-`pin9` empties in `057_pins.py`.

## Key data

- **Datablocks referenced:** none (all empties)
- **Materials assigned:** none
- **Modifiers added:** none
- **Custom properties:** none
- **World positions of key anchors:** 10 anchor positions in a 4-3-2-1 triangle at x≈-36.9 to -40.4, y≈-34.8 to -39.1, z=2.515
- **Object types breakdown:** 10 EMPTY
- **Parent collection:** `pinsPosition` (re-parented under `bowling/` by finalize)

## Technique / recipe

**Why 10 cylinder-shaped position empties + 10 pin0-pin9 empties from `057_pins`?** Two parallel sets of 10 anchors, both in 4-3-2-1 triangles, but at DIFFERENT locations:
- `pin0`-`pin9` (in 057) are at (-49.87 to -53.33, -24.16 to -28.49) — call this "pin staging area"
- `cylinder.025`-`cylinder.034` (here) are at (-36.90 to -40.37, -34.79 to -39.13) — call this "pin spawn deck"

Possible roles:
- **`pin0`-`pin9`** carries the **runtime physics body templates** (named like pin instances, ready to spawn)
- **`cylinder.025`-`cylinder.034`** carries the **spawn POSITIONS** (where the pin physics bodies materialize each game cycle)

The naming further confirms this: `cylinder.NNN` matches the pin's local collider shape (`tube.004/005` in 057), and `0.636 × 1.415` matches the bottom-tube collider proportions (0.975 × 1.587 there). Slightly smaller scale here — these may be slightly inset spawn positions.

**Two-tier system** lets the runtime separate "what to spawn" from "where to spawn" — handy for game cycling: reset by re-cloning templates at these positions.

**z=2.515** is significantly elevated — pins drop from this height onto the lane (z≈0). The drop gives them a brief moment of physics simulation before settling.

**`rotation_euler.X = -π`** (≈-180°) flips them upside down — perhaps pins are authored "head down" and need flipping to stand up. Or this is just the spawn orientation that the runtime uses.

## Connections

- **Reads from:** nothing (all empties)
- **Read by:** `999_finalize.py` (parents `pinsPosition/` under `bowling/`)
- **Depends on:** `052_bowling.py`
- **Depended on by:** runtime bowling pin-spawn logic (every "new game" event resets pins at these 10 locations)

## Notable code patterns

- **All 10 objects share identical scale and z** — every pin position is mathematically identical except for XY. Easy to read, easy for the runtime to iterate as a clean grid.
- **Triangle layout exactly matches standard bowling** — Bruno isn't reinventing the layout; he's authoring the canonical 4-3-2-1 setup.
- **Empty (no geometry, no material, no modifier) script** — pure data definition. 169 lines for 10 hand-placed transforms. Very repetitive — each empty's setup block is ~16 lines of try/except.
- **`empty_display_size = 0.5`** — smaller wireframes than the default 1.0 keeps the viewport clean despite 10 stacked anchors.
- **Indices skip** within the script's own sequence (cylinder.025-034 — consistent, no gaps internally, but the global cylinder.NNN namespace probably has cylinders elsewhere with .000-.024 indices used by other props).
