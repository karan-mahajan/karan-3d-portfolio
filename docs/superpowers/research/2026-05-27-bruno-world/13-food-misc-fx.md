# 13 — Food, Drink, Music + Misc Props + Special FX/Events

**Bruno categories:** 🍪 Food, Drink & Music + 🪧 Misc Props + 🌪️ Special FX / Events + 📦 Miscellaneous
**Scripts:** 15 (063, 079, 080, 092, 101, 107, 110, 121, 124, 126, 128, 129, 130, 138, 139)
**Total objects:** 156
**Status:** mixed — some VISIBLE (title, cookie, cups, pole, airDancers), most EXCLUDED (easter eggs, FWA, tornado, whispers, antenna, oldSchool, sudo)

---

## Purpose

A grab-bag of standalone content that doesn't fit into a single zone. Includes:
- **Player-facing UI/interactives** that span the world (cookie interactive sequence, title at landing, controls)
- **Branded props** (FWA award badges, cups)
- **Easter eggs & special events** (easter, egg, tornado, whispers — all hidden until triggered)
- **Standalone decorative props** (antenna, oldSchool, sudo)
- **The airDancers** (the inflatable tube-guys — 2 of them)

These scripts span EXCLUDED status because many are runtime-revealed (tornado event, easter hunt, FWA reveal after destroying crates).

---

## Scripts — Food, Drink & Music (2, both VISIBLE)

| # | File | Objs | Types | Materials | What it adds |
|---:|---|---:|---|---|---|
| 079 | `079_cookie.py` | 24 | 15×EMPTY, 9×MESH | `cookieBanner`, `emissiveOrangeRadialGradient`, `palette` | The interactive cookie zone — 9 cookie meshes + 15 anchor empties. Custom prop `preventAutoAdd` (revealed during cookie sequence). Inside `cookie` collection (one of the 14 areas) |
| 110 | `110_cups.py` | 6 | 3×MESH, 3×EMPTY | `palette` | 6 cups — inside timeMachine (108). 3 NODES modifiers (Smooth by Angle) |

## Scripts — Misc Props (4, mostly EXCLUDED)

| # | File | Objs | Types | Materials | What it adds | Status |
|---:|---|---:|---|---|---|---|
| 101 | `101_pole.py` | 13 | 9×MESH, 4×EMPTY | `palette`, `projectsLabels` | Signage pole at projects zone — 9 meshes + 4 anchor empties. Branded with `projectsLabels` | VISIBLE |
| 124 | `124_antenna.001.py` | 9 | 5×MESH, 4×EMPTY | `emissivePurpleRadialGradient`, `palette` | An antenna prop (likely a sci-fi accent piece) — 1 NODES + 1 MIRROR modifier | EXCLUDED |
| 126 | `126_oldSchool.py` | 8 | 5×MESH, 3×EMPTY | `emissiveOrangeRadialGradient`, `palette`, `redGradient` | An "old school" themed prop set (retro accent piece) | EXCLUDED |
| 128 | `128_sudo.py` | 4 | 2×ARMATURE, 2×MESH | — | A rigged "sudo" character — 2 armatures + 2 meshes. The sudo name suggests a hidden admin/developer character. Inside `archives.003` parent | EXCLUDED |

## Scripts — Special FX / Events (7, mostly EXCLUDED)

| # | File | Objs | Types | Materials | What it adds |
|---:|---|---:|---|---|---|
| 080 | `080_easter.001.py` | 21 | 14×EMPTY, 7×MESH | `palette` | The easter-egg event setup — 7 meshes + 14 anchors. EXCLUDED (revealed during easter hunt) |
| 107 | `107_FWA.py` | 4 | 2×MESH, 2×EMPTY | `palette` | FWA award badges — parented under `statue/FWA`. EXCLUDED until earned |
| 121 | `121_fwa.py` | 6 | 6×MESH | `palette` | FWA badges revealed from explosive crates — parented under `explosiveCrates`. EXCLUDED until crates destroyed |
| 129 | `129_easter.py` | 0 | — | — | Empty parent for `egg` — EXCLUDED |
| 130 | `130_egg.py` | 2 | 2×MESH | — | The easter egg meshes — EXCLUDED. Found at end of easter hunt |
| 138 | `138_tornado.py` | 17 | 17×EMPTY | — | Tornado event — 17 anchor empties for the tornado's path/effects. EXCLUDED until tornado triggers |
| 139 | `139_whispersForbiddenAreas.py` | 12 | 12×EMPTY | — | "Whispers" + forbidden-area markers — 12 anchors. EXCLUDED. Likely audio-only ambient triggers in restricted zones |

## Scripts — Miscellaneous (2, VISIBLE)

| # | File | Objs | Types | Materials | What it adds |
|---:|---|---:|---|---|---|
| 063 | `063_airDancers.py` | 2 | 2×MESH | `airDancer` | The 2 inflatable tube-guys at the race-track entrance. Custom material `airDancer` (animated/wavy shader) |
| 092 | `092_title.001.py` | 21 | 10×MESH, 10×EMPTY, 1×FONT | `palette` | The welcome title at landing — 10 letter/word meshes + 1 FONT object + 10 anchors. 10 NODES + 1 SOLIDIFY modifiers. Custom prop `mass` (knockable letters) |

---

## How these contribute to Bruno's world

### The "discoverable content" layer
- **EXCLUDED ≠ broken.** Bruno excludes scripts from view layer when their content is **runtime-revealed**:
  - `easter` + `egg` (129, 130) — only show during easter hunt
  - `FWA` (107) + `fwa` (121) — only after specific gameplay (statue visit, crate destruction)
  - `tornado` (138) — only during scripted weather event
  - `whispersForbiddenAreas` (139) — audio markers, no visible mesh anyway
  - `antenna.001`, `oldSchool`, `sudo` (124, 126, 128) — likely time-limited reveals or developer-mode content
- The world has **layered content density** — what you see on first visit is a fraction of what's there.

### The interactive set pieces
- **`title.001` (092)** — knockable welcome-message letters at landing. 10 mass-tagged letter meshes mean players can ram into and scatter the title. Visual gag + first-touch feedback.
- **`cookie` (079)** — 24 objects for a multi-stage interactive cookie sequence. The `preventAutoAdd` flag + 15 empty anchors suggest a runtime-spawned cookie reveal/collection mechanic.
- **`airDancers` (063)** — 2 inflatable dancers with the dedicated `airDancer` material (animated waving shader). Atmosphere at race-track entrance.

### The branded micro-props
- **`pole` (101)** — signage pole at projects zone. Branded with `projectsLabels`. Wayfinding inside the workshop.
- **`cups` (110)** — coffee/drink cups inside the retro time-machine room. World-building detail.

### The mystery content (EXCLUDED, all 7 special FX + 3 misc props)
- **`sudo` character (128)** with 2 armatures — a rigged figure with `admin` connotation. Likely Bruno's "developer mode" avatar — only shown when entering a sudo command in-game or hitting a developer key combo.
- **`antenna.001`** with `emissivePurpleRadialGradient` (purple is rare in Bruno's palette) — likely a futuristic accent for a hidden sci-fi corner.
- **`oldSchool`** mixes orange + red gradients — a retro nostalgia prop set, also hidden.
- **`tornado` (17 empties)** — the path/effect anchors for a scripted weather event. When it triggers, the runtime spawns particle effects along these 17 points.
- **`whispersForbiddenAreas` (12 empties)** — pure audio markers; entering these zones plays atmospheric whispers (forbidden-knowledge vibes).

---

## Why this design works for Bruno

- **EXCLUDED ≠ removed.** The .blend ships with all content; the view-layer flag controls visibility per-context. The runtime can enable any of these at any time without re-loading geometry.
- **Audio-only anchors (whispers, tornado path)** are JUST empties — no mesh data, but the runtime knows where to spawn sounds/particles when triggered.
- **AirDancers' dedicated material** = Bruno wrote a wave-animation shader specifically for these 2 meshes. Premium attention on a quirky detail.
- **Mass-tagged title letters** = the player's FIRST interaction is probably ramming into Bruno's name. Sets the playful tone immediately.
- **Cookie interactive sequence** is a deeper engagement than most zones — 15 anchors for multi-step progression.
- **The world has a "secrets" layer** — easter, egg, sudo, antenna, oldSchool, tornado, whispers — ALL hidden until specific triggers. Probably 30-40% of Bruno's content is post-first-visit discovery.

---

## Cross-references

- **Cookie zone** (079) is parented under `areas/cookie` — see [07-major-areas.md](07-major-areas.md).
- **Cups** (110) is inside `timeMachine` — see [06-buildings-structures.md](06-buildings-structures.md).
- **FWA badges** (107, 121): 107 is under `statue` ([06](06-buildings-structures.md)), 121 is under `explosiveCrates` ([08](08-race-track.md)).
- **Title** (092) is inside `landing` — see [07-major-areas.md](07-major-areas.md).
- **Pole** (101) is inside `projects` workshop — see [12-workshop-portfolio-icons.md](12-workshop-portfolio-icons.md).
- **AirDancers** are at race-circuit entrance.
- **Sudo** is inside `archives.003` — see [14-reference-hidden.md](14-reference-hidden.md).

---

## Source pointers

- Step scripts: 15 files (see Scripts tables above)
- Materials: `airDancer` (wave shader), `cookieBanner`, `palette`, `emissiveOrangeRadialGradient`, `emissivePurpleRadialGradient`, `redGradient`, `projectsLabels`
- Modifiers used: MIRROR (antenna), SOLIDIFY (title letters), NODES (multiple), ARMATURE (sudo)
- Bruno's runtime event system: `folio-2025/sources/Game/` (likely under `YearCycles/`, `Events/`, or `Triggers/`)
