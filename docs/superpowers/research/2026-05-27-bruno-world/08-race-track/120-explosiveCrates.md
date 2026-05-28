# 120_explosiveCrates.py — 23 destructible crates scattered across the world

**Path:** `folio-2025/scripts/blender_world_steps/steps/120_explosiveCrates.py`
**Lines:** 288
**Adds:** 23 MESH objects to collection `explosiveCrates`
**Group:** [08-race-track](../08-race-track.md)

## What it does (code-level)

Creates `explosiveCrates` collection and **links it directly to `scene.collection`** (unlike most zone-child scripts which leave linking to finalize). Adds 23 MESH instances of `Cube.053`.

All 23 crates share:
- **Mesh datablock**: `Cube.053`
- **Scale**: (1, 1, 1) — or very close (some have (0.9999..., 1, 0.9999...) artifacts)
- **NO** modifiers
- **NO** custom properties (no explicit mass/restitution/booleans)
- **rotEuler.X = ~π/2** (90°) — the crate is tipped on its side (the mesh's Z axis becomes Y in world)
- **Z (height)** varies: most at 0.532 (resting on ground), some at 1.61–1.72 (stacked on lower crate), one at 0.570

Each crate has a unique rotZ between -π and +π — random scattered orientation. Locations span the whole world:

| Range | (x, y) | Count |
|---|---|---|
| Race track north | (~46-48, ~-38) | 4 crates |
| Race track west | (~-75 to -84, ~42-71) | 11 crates (largest cluster — also at varying Z heights for stacking) |
| Bowling-area south | (~7 to 12, ~-18 to -40) | 5 crates |
| Behind-the-scenes east | (~27-28, ~19-20) | 3 crates |

The 11 west-side crates form a tight ~7m × 14m cluster between (-84, 42) and (-73, 65) — likely a stockpile/storage of explosive crates as a visual gag near the time-machine area.

## Key data

- **Datablocks referenced:** mesh `Cube.053` (instanced 23×)
- **Materials assigned:** via mesh datablock — `palette` (per group .md)
- **Modifiers added:** none (the crate mesh is hand-modeled, no procedural smoothing/bevel needed)
- **Custom properties:** none in this script
- **World positions of key anchors:** see table — 4 distinct clusters across the map
- **Object types breakdown:** 23 MESH
- **Parent collection:** `explosiveCrates` (linked directly to scene; re-parented under `circuit/` by finalize)

## Technique / recipe

**Single-mesh scatter via hand-placed instances:** Bruno places each crate by hand (no GN scatter) but all 23 share the SAME `Cube.053` mesh datablock. The variation comes from:
1. Position (4 cluster regions across the map)
2. Z-rotation (each crate has its own yaw, looks "naturally tossed")
3. Z height (some stacked on top of others)

**Tipped on side (rotX=π/2):** the crate's authored mesh has its Z-axis as the natural "up" but is rotated so its Y-axis points up — so the mesh data was authored as a horizontal box, and rotated to stand vertically. (Or vice versa.)

**No modifiers, no custom props** — these are passive scenery objects. The runtime probably reads `explosiveCrates` as a special collection (the runtime explosion-on-hit logic targets all objects under this collection name). FWA badges revealed by destroying crates likely live in collection `121_fwa` (the next script — outside this batch).

**`scene.collection.children.link(coll)` in this script** (line 7-9) — unusual. Most zone-child scripts skip this and let finalize do the linking. This collection links itself directly to the scene root, probably because the explosive crates are scattered across multiple zones and don't fit cleanly under `circuit/` alone.

## Connections

- **Reads from:** `005_meshes_*.py` (`Cube.053`)
- **Read by:** `999_finalize.py` (may re-parent under `circuit/` or keep at scene level)
- **Depends on:** `062_circuit.py` (zone container)
- **Depended on by:** `121_fwa.py` (the FWA badges revealed by destroying crates — covered in another batch)

## Notable code patterns

- **Direct `scene.collection.children.link(coll)`** call inside the script — Bruno's atypical "self-link" pattern. Compare with `043_areas.py` which does the same. The script doesn't rely on finalize to parent it.
- **Index sparsity**: crate indices are .001, .002, .003, .004, .009, .015, .019, .023, .030, .034, .038, .042, .046, .050, .054, .058, .062, .066, .070, .077, .081, .085, .089 — 23 unique indices spanning 1-89 with gaps. The gaps suggest a shared global naming pool (other scripts have their own crates at the missing indices) OR original-blend had more crates and Bruno deleted some.
- **No `booleans = []`** custom prop — these crates are simpler than vehicle parts (which DO have `booleans`).
- **`refObjects...` prefix NOT used** — these aren't generic objects, they're specifically `explosiveCrates`. The runtime probably has a dedicated `explosiveCrates` handler with explosion/FWA-spawn logic.
