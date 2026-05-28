# 070_leaderboardReset.py — "RESET" button mesh + hidden font label

**Path:** `folio-2025/scripts/blender_world_steps/steps/070_leaderboardReset.py`
**Lines:** 39
**Adds:** 2 objects (1 MESH, 1 FONT) to collection `leaderboardReset`
**Group:** [09-bowling](../09-bowling.md)

## What it does (code-level)

Creates `leaderboardReset` collection. Adds 2 objects:

| Object | Type | Datablock | Location | Hidden |
|---|---|---|---|---|
| `refLeaderboardReset` | MESH | `Cube.210` | (-18.79, -19.18, 0.51) | No |
| `archiveReset` | FONT | curve `Text.005` | (-17.19, -20.27, 0.85) | viewport+render+select |

The mesh button is visible at z=0.51 (low — button at table height). The FONT object is HIDDEN in all three modes but carries the live "RESET" text data.

## Key data

- **Datablocks referenced:** mesh `Cube.210`, curve `Text.005` (a FONT curve)
- **Materials assigned:** via mesh datablock — `palette` on the button
- **Modifiers added:** none
- **Custom properties:** none
- **World positions of key anchors:**
  - Button at (-18.79, -19.18, 0.51) — far west of bowling zone, "leaderboard reset depot"
  - Hidden FONT label at (-17.19, -20.27, 0.85), rotated for vertical display
- **Object types breakdown:** 1 MESH, 1 FONT
- **Parent collection:** `leaderboardReset` (re-parented under `bowling/` by finalize)

## Technique / recipe

**Live FONT object as hidden reference:** the `archiveReset` FONT carries the live text "RESET" but is hidden in viewport, render, AND select. The mesh button (`refLeaderboardReset`) is what the player sees and interacts with.

**Why have a hidden FONT?** Three reasons:
1. The runtime might convert the FONT to a mesh on demand (for high-DPI text rendering)
2. The FONT datablock holds the editable text content that the runtime can read to know the button's label
3. Bruno uses it as a SOURCE for rendering: convert font → mesh → display, all on the fly, so any string change updates the visible label

**`archive` prefix** on the FONT — Bruno's "this is template/source data, not for direct render" pattern. Consistent with `archiveReset`, `archiveRailsCurve`, `archivePoles` (073), etc.

**Rotation on FONT** `(π/2, ~0, π/2)` — same orientation pattern as the Text.002 in `069_leaderboard.py`. The text stands vertical, faces viewer.

**FONT object type instead of MESH** — only place in batch 3 where Bruno uses a live FONT. The trade-off: FONT objects let you change text at edit-time without re-baking, but they're slower to render (so Bruno hides them and uses meshes for visible text).

## Connections

- **Reads from:** `005_meshes_*.py` (`Cube.210`), `007_curves.py` (`Text.005` FONT curve)
- **Read by:** `999_finalize.py` (parents `leaderboardReset/` under `bowling/`)
- **Depends on:** `052_bowling.py`
- **Depended on by:** runtime leaderboard reset logic (player presses button → wipe stored high scores)

## Notable code patterns

- **First FONT object in batch 3** — Bruno uses FONT sparingly. Most text is mesh-baked.
- **`archive` + hidden FONT pattern** — consistent across the world for "template data not for direct render."
- **Button + label split** — the visible mesh is the button shape; the (hidden) FONT carries the label text. The runtime composites or displays both based on logic.
- **Low z (0.51)** — table-height button. Player walks/drives up to the leaderboard panel and presses something at waist level.
- **39-line script for 2 objects** — clean, compact. Demonstrates how Bruno handles single-feature interactions efficiently.
