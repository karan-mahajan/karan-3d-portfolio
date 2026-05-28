# 069_leaderboard.py — leaderboard panel + text mesh

**Path:** `folio-2025/scripts/blender_world_steps/steps/069_leaderboard.py`
**Lines:** 33
**Adds:** 2 MESH objects to collection `leaderboard`
**Group:** [09-bowling](../09-bowling.md)

## What it does (code-level)

Creates `leaderboard` collection. Adds 2 MESH objects forming the leaderboard panel:

| Object | Mesh | Location | Rotation (rad) |
|---|---|---|---|
| `refLeaderboard` | `Cube.214` | (-19.64, -16.42, 3.12) | (0, 0, 0) — flat panel |
| `Text.002` | `Text.001` | (-19.82, -16.41, 6.63) | (π/2, ~0, π/2) — text rotated to face viewer |

No modifiers, no custom props on either. The text mesh sits 3.5m above the panel — title text floating over the leaderboard.

## Key data

- **Datablocks referenced:** meshes `Cube.214` (panel), `Text.001` (text mesh — likely converted from a FONT/curve)
- **Materials assigned:** via mesh datablocks — `emissiveOrangeRadialGradient`, `palette` (per group .md). 210 verts total
- **Modifiers added:** none
- **Custom properties:** none
- **World positions of key anchors:**
  - Panel at (-19.64, -16.42, 3.12) — far west of the bowling zone, "leaderboard depot"
  - Text floating above at z=6.63
- **Object types breakdown:** 2 MESH
- **Parent collection:** `leaderboard` (re-parented under `bowling/` by finalize)

## Technique / recipe

**Title text as mesh (not FONT object):** `Text.002` uses mesh `Text.001` — this is a mesh BUILT FROM a font object, not a live FONT. Bruno baked the text geometry once and reuses it as static mesh. (Compare with `070_leaderboardReset.py` which uses a live FONT object for the RESET button label.)

**Panel + floating text** — the panel is just a 3D cube/plaque; the text floats above as a label. Two-mesh composition.

**Rotation pattern** on `Text.002` `(π/2, ~0, π/2)` rotates the text:
1. Up around X (π/2) — text faces up if authored flat in XY
2. Then around Z (π/2) — text reads left-to-right

Together: the text now stands vertical and faces the viewer.

**Far west location** (-19.64, -16.42) — like the screen and sign assets, these are off-stage; runtime re-positions or just renders here regardless of player position (the leaderboard might be a fixed-render UI surface).

**210 verts total** — modest geometry. The text mesh probably has most of those verts; the panel is a simple beveled cuboid.

## Connections

- **Reads from:** `005_meshes_*.py` (`Cube.214`, `Text.001`)
- **Read by:** `999_finalize.py` (parents `leaderboard/` under `bowling/`)
- **Depends on:** `052_bowling.py`
- **Depended on by:** runtime score-persistence + leaderboard rendering

## Notable code patterns

- **MESH (not FONT) for the leaderboard title** — Bruno only uses live FONT objects when the text needs to be runtime-editable (e.g., the RESET button in 070). Static titles get baked-to-mesh once.
- **Two-mesh composition** — minimal, no overcomplication. The leaderboard is just panel + text.
- **No modifier on either mesh** — both have hand-baked normals at the mesh level.
- **`Text.001` mesh datablock** is shared resources — the runtime might display dynamic scoreboard entries by other means (separate text objects or texture swaps).
