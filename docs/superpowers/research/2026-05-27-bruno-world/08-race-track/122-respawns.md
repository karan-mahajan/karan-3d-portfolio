# 122_respawns.py — 17 named respawn anchor empties (one per gameplay zone)

**Path:** `folio-2025/scripts/blender_world_steps/steps/122_respawns.py`
**Lines:** 283
**Adds:** 17 EMPTY objects (all ARROWS) to collection `respawns`
**Group:** [08-race-track](../08-race-track.md)

## What it does (code-level)

Creates `respawns` collection and links it directly to `scene.collection`. Adds 17 EMPTY objects, all `empty_display_type='ARROWS'` (directional indicators for spawn orientation). Each named by zone they correspond to.

| Empty name | Location | rotZ (rad) — spawn direction |
|---|---|---|
| `respawnCookie` | (15.64, -36.38, 0.5) | -9.64 (≈mod 2π → 0.34) |
| `respawnLanding` | (39.53, -37.83, 0.5) | -0.23 |
| `respawnAltar` | (74.79, 14.08, 0.5) | 1.12 |
| `respawnBonfire` | (55.07, -44.05, 0.5) | -8.49 |
| `respawnProjects` | (35.78, -17.57, 1.11) | -11.41 |
| `respawnLab` | (17.88, -18.80, 0.5) | -9.81 |
| `respawnCareer` | (26.28, -9.63, 0.5) | -11.00 |
| `respawnSocial` | (25.67, 14.47, 0.5) | -12.01 |
| `respawnBridge` | (52.25, -26.20, 0.5) | -10.35 |
| `respawnToilet` | (70.91, -66.02, 0.5) | -9.18 |
| `respawnControls` | (49.22, -34.56, 0.5) | 0.0 |
| `respawnBowling` | (21.30, -62.22, 0.5) | 3.69 |
| `respawnOnlyFans` | (36.91, 27.90, 0.5) | -11.51 |
| `respawnCircuit` | (-13.71, -14.70, 2.25) | -0.16 |
| `respawnTimeMachine` | (-56.49, 64.74, 0.5) | -11.70 |
| `respawnBehindTheScene` | (48.82, 11.47, 0.5) | -0.19 |
| `respawnAchievements` | (69.99, -20.36, 0.61) | 1.70 |

All at z≈0.5 except `respawnProjects` (1.11), `respawnCircuit` (2.25, in the race-track airspace), `respawnAchievements` (0.61).

## Key data

- **Datablocks referenced:** none (all empties)
- **Materials assigned:** none
- **Modifiers added:** none
- **Custom properties:** none in this script
- **World positions of key anchors:** 17 distinct positions across the entire world map, one per zone
- **Object types breakdown:** 17 EMPTY (all ARROWS)
- **Parent collection:** `respawns` (linked directly to scene; finalize re-parents under `circuit/` per group docs — but this is somewhat misleading because respawns serve the WHOLE world, not just the race track)

## Technique / recipe

**One named anchor per zone** — Bruno's runtime can look up a specific respawn empty by name (e.g., `bpy.data.objects['respawnBowling']`) when the player falls off the world or restarts a zone. The ARROWS display type encodes "spawn facing this direction."

**Zone-named pattern** (`respawnXxxx`) — clean lookup by string. The runtime probably maps `currentZone → bpy.data.objects['respawn' + capitalize(currentZone)]`.

**Z=0.5 default** — most respawn anchors are 0.5m above ground (above the player's foot origin). `respawnProjects` (1.11) and `respawnCircuit` (2.25) sit higher because those zones have elevated terrain.

**`respawnCircuit` is the lone race-track respawn (-13.71, -14.70, 2.25)** — and is the only one inside the race-track zone. The other 16 respawns are for the OTHER zones, so this script lives in `respawns` collection but isn't really "race-track only." The group .md placing it under race-track is a side-effect of script numbering (122 falls in the race-track index range).

**Counterintuitive parenting:** the `respawns` collection contains 17 anchors for 17 different zones, yet ends up under `circuit/` after finalize. This is probably an organizational quirk — the runtime reads `respawns/` regardless of where it's parented.

**Direct `scene.collection.children.link(coll)`** — same self-link pattern as `120_explosiveCrates.py`. These global utility collections don't wait for finalize.

## Connections

- **Reads from:** nothing
- **Read by:** `999_finalize.py` (re-parents `respawns/` somewhere — likely under `behindTheScene/` or directly under scene)
- **Depends on:** nothing
- **Depended on by:** runtime respawn/teleport logic for every zone

## Notable code patterns

- **ARROWS display type** — all 17 use this, communicating "this is a directional anchor." Empties with rotation matter; ARROWS makes the rotation visible in viewport.
- **String-named lookups** (`respawnBowling`, `respawnCircuit`, ...) — runtime convention for global anchor lookup by name.
- **Some `rotation_euler[2]` values are HUGE (e.g., -12.01, -11.70)** — Blender stores rotations modulo 2π but displays whatever the user authored. -12.01 rad = -12.01 + 2×2π = 0.555 rad ≈ 32°. The runtime will normalize these.
- **Zone names include `OnlyFans`** (clearly a joke/easter-egg zone in the social section), `BehindTheScene`, `Cookie`, `Achievements` — Bruno's playful zone naming.
