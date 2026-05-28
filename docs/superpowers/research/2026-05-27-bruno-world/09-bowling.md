# 09 — Bowling

**Bruno category:** 🎳 Bowling
**Scripts:** 9 (054, 055, 056, 057, 058, 059, 060, 069, 070)
**Total objects:** 83 (1 bowling root + 82 in props/UI)
**Status:** VISIBLE

---

## Purpose

A complete bowling alley with pins, ball-return furniture, jukebox music, score screen, leaderboard, branding sign, and bumpers. Like the race track, this is a **mini-game embedded in the portfolio** — players can actually bowl. Parented under `bowling` root (052, see [07-major-areas.md](07-major-areas.md)).

---

## Scripts

| # | File | Objs | Types | Materials | What it adds |
|---:|---|---:|---|---|---|
| 054 | `054_bumpers.py` | 5 | 3×EMPTY, 2×MESH | `darkGray`, `emissivePurpleRadialGradient` | Bowling lane bumpers — 2 meshes + 3 anchor empties. The emissive-purple gives a stylized arcade glow |
| 055 | `055_furnitures.py` | 43 | 25×EMPTY, 18×MESH | `emissiveOrangeRadialGradient`, `palette` | The bulk of the bowling alley's furniture — ball-return racks, seating booths, side tables. 10 NODES modifiers. Custom prop `mass` on some (interactable) |
| 056 | `056_jukebox.py` | 3 | 2×EMPTY, 1×MESH | `emissiveOrangeRadialGradient`, `emissivePurpleRadialGradient`, `palette` | The jukebox — 1 mesh + 2 anchor empties. 1 NODES modifier. Custom prop `mass`. Plays music when interacted with |
| 057 | `057_pins.py` | 14 | 13×EMPTY, 1×MESH | `palette` | 1 pin mesh + 13 placement empties (10 standard pins + 3 spares?). Custom prop `preventAutoAdd` (don't spawn at startup — runtime spawns dynamically after each ball) |
| 058 | `058_pinsPosition.py` | 10 | 10×EMPTY | — | 10 pin starting-position empties (the classic triangle: 1+2+3+4 = 10 pins). These are where the runtime spawns pins from |
| 059 | `059_screen.py` | 8 | 6×MESH, 2×EMPTY | `bowlingLabelStrike`, `emissivePurpleRadialGradient`, `palette` | The score screen above the alley — 6 mesh elements (frame, screen plane, strike-animation labels) + 2 anchor empties. 3 NODES modifiers |
| 060 | `060_sign.py` | 1 | 1×CURVE | — | The "Bowling" sign — 1 bezier curve (probably letterforms or a logo outline) |
| 069 | `069_leaderboard.py` | 2 | 2×MESH | `emissiveOrangeRadialGradient`, `palette` | The leaderboard panel showing top scores (210 verts — likely a 3D-extruded label board) |
| 070 | `070_leaderboardReset.py` | 2 | 1×MESH, 1×FONT | `palette` | The "reset leaderboard" button — 1 mesh + 1 FONT object (probably the "RESET" text) |

---

## How the bowling alley is composed

**The lane** (where the ball rolls): in `bowling` root (052) — 5 of those meshes are likely the lane planks, walls, gutter rails.

**The pin-spawn system:**
- `058_pinsPosition` defines the 10 starting positions (classic 4-3-2-1 triangle)
- `057_pins` provides the pin mesh + 13 placement empties (probably 10 in-play + 3 alternates)
- `preventAutoAdd` on pins means at startup they don't spawn — only after the player triggers a new game

**The score display:**
- `059_screen` — the in-world score TV mounted above the alley
- `069_leaderboard` — the persistent leaderboard panel (recent strikes / top scores)
- `070_leaderboardReset` — a "RESET" button (the font object is probably the button label)

**Player furniture:**
- `055_furnitures` (43 objects) is the bulk — ball-return racks, scoring kiosk, side tables, seating booths around the alley. 25 empties suggests heavy use of slot-style placement.
- `056_jukebox` — interactive music player (mass + emissive-purple glow)
- `054_bumpers` — bumper rails along the lane (likely toggleable for beginner mode)

**Branding:**
- `060_sign` — the curved "Bowling" entry sign
- `bowlingLabelStrike` material in `059_screen` — strike-animation label texture

---

## Why this design works for Bruno

- **Three emissive accent colors:** orange (warm, furniture/jukebox), purple (arcade-cool, screen/bumpers/jukebox), white (probably ambient lane lighting in root 052). The bowling alley has a **distinct color identity** vs. the warm-yellow rest of the world.
- **Branded material `bowlingLabelStrike`** = Bruno authored a specific strike-celebration animation texture. Polish detail.
- **`mass` on jukebox + some furniture** = the player can shove these around. Adds physical comedy.
- **Pins are runtime-spawned (preventAutoAdd)** rather than baked into the scene. Each game cycle resets the pins via the `pinsPosition` empties.
- **Score persistence implied by leaderboardReset** — there's a backend storing high scores, and a button to wipe it. Real game state.
- **The whole zone is a self-contained mini-game** — like the race track. Bowling and racing are the two "biggest" interactive zones in Bruno's world.

---

## Cross-references

- **Bowling root + alley empty:** see [07-major-areas.md](07-major-areas.md) — script 052 and 053
- **Furniture pattern (booths, racks):** see [11-furniture-displays-boards.md](11-furniture-displays-boards.md) for how Bruno handles seating across zones

---

## Source pointers

- Step scripts: `folio-2025/scripts/blender_world_steps/steps/054_bumpers.py` through `060_sign.py`, plus `069_leaderboard.py` and `070_leaderboardReset.py`
- Materials: `palette`, `darkGray`, `bowlingLabelStrike`, `emissiveOrangeRadialGradient`, `emissivePurpleRadialGradient`
- Bruno's runtime bowling code: `folio-2025/sources/Game/` (likely in `Bowling/` or under `Areas/`)
