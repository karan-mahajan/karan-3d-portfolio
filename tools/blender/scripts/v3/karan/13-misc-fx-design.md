# Section 13 — food / misc / fx — karan delta design

**Date:** 2026-05-30
**Scope:** Blender only. Five custom karan props added ON TOP of the Bruno
verbatim section-13 layer (keep-everything: nothing Bruno-made is removed).
Blender authors **static geometry + a clean pivot/anchor** for each prop; the
Three.js runtime drives all motion (flailing, idle/hop, physics kicks) later.

Coordinate convention (matches the rest of the karan build): a 2D point is
`(x, z)` where `x` = east-west, `z` = north-south = Blender X, Y. Object height
(Blender Z) ALWAYS comes from a downward terrain raycast — never hardcoded.
Spawn at origin; player faces north (+Y). Walkable radius ≈ 52 m.

Reference coords already in the world (do not clip these):
- Section markers: projects (38, 10), experience (8, 36), skills (-14, -34),
  contact (-32, -12); skills sphere pond centre (-34.14, -35.72).
- Structures: cabin ≈ (22.7, 22.4) NE, outhouse ≈ (-22, 20) NW, statue ≈
  (-5.5, -5.5) near spawn.

---

## Shared helper — `misc_common.py` (no `13-` prefix → not globbed by run-all)

Self-contained section-13 helper, mirroring `foliage_common.py` /
`buildings_common.py`. Provides:
- `height_at(x, z)` — downward terrain raycast (z=80 down); `None` off-terrain.
- `obstacle_boxes()` + `find_spot(anchor, …)` — spiral search onto clear dry
  land, avoiding water (height `< LAND_MIN`), island edge, all section
  marker/footprint boxes, rocks/bridges/slabs, structures, and previously
  placed section-13 props.
- `material(name, color, roughness, emissive_strength)` — chunky principled mat.
- `bevel(obj, …)`, `cuboid(...)`, `cylinder(...)`, `world_xy(...)` — chunky-bevel
  builders in a yaw-rotated local plan space (same authoring style as the hut /
  buildings).
- `pivot_empty(name, x, z, ground, yaw, props)` — PLAIN_AXES empty at the prop
  base; child meshes parent to it so the runtime animates the whole prop by
  driving one transform (skills-sphere hierarchy approach).
- `ref_anchor(name, location, props)` — PLAIN_AXES empty carrying runtime
  custom props (interaction type, hints).
- `collider_box(key, center, half_extents, yaw)` — hidden WIRE box in
  `colliders` for solid props (so later vegetation/runtime keep clear).

Section 13 does **NOT** clear the grass mask or cull foliage (unlike buildings)
— these props are light and sit naturally in the grass.

Collections used: `miscFx` (visible geometry), `refs` (anchors), `colliders`
(footprints) — matching existing karan collection names.

---

## ① Title — "KARAN MAHAJAN" (kickable letters)

Bruno's design intent kept (mass-tagged knockable letters), re-styled chunky.
- **Single row** of individual letter objects spelling `KARAN MAHAJAN`
  (12 glyphs + 1 word gap). Each glyph is its OWN mesh object so the player can
  shove/kick it.
- Built from a baked Blender **FONT curve per glyph → SOLIDIFY (depth) →
  convert to mesh → chunky bevel**, palette/cream material, sunset-lit.
- Placed in a line centred ≈ `(0, 7)` running along X (≈ -4.3 → +4.3 m), each
  letter facing **-Y (south)** so it reads from the spawning player. Letters sit
  ON the terrain (raycast height) as kickable physics bodies.
- Per-letter custom props: `mass` (≈ 0.2, light enough to kick), `kickable =
  True`, `interaction = "titleLetter"`. Each letter also gets a width-fit
  collision empty (`titleLetterCollider_NN`, display CUBE) mirroring Bruno's
  per-letter cuboids, parented to its letter, for the runtime physics body.
- One `titleRef` anchor empty at the row centre with `title = "KARAN MAHAJAN"`,
  `interaction = "title"`.
- No static walk-through collider (they're dynamic at runtime).

## ② Controls board

- Wooden **A-frame signboard on two posts** beside spawn at ≈ `(11, 5)`, yaw
  angled to face the spawn/player. On terrain by raycast.
- Board face: baked FONT header `CONTROLS` + a few simple painted glyph blocks
  (move keys / look / run) as small beveled cuboids — readable, not pixel-art.
- `controlsRef` anchor empty in front of the board: `interaction = "controls"`,
  `hint = "move · look · run"` so the runtime can attach the live control
  overlay/prompt.
- Hidden `collider_box` around the two posts (solid prop).

## ③ Air dancers ×2

- Tall tapered **tube-guy**, sunset stripes (red→orange→yellow emissive accent),
  two floppy arms. Built as a **chain of ~5 stacked tube segments**: a base
  PLAIN_AXES pivot empty at ground, segment 0 parented to it, each higher
  segment parented to the one below (so the runtime rotates each joint
  progressively for the iconic wave). Authored in a neutral near-upright pose.
- Two instances flanking the east approach to Projects, placed symmetrically off
  the spawn→projects line at ≈ `(26, 3)` and `(30, 17)` (validated onto grass
  via `find_spot`).
- Base pivot custom props: `interaction = "airDancer"`, `segments = 5`,
  `swayAmplitude` (deg) + `swaySpeed` hints for the runtime. Naming:
  `airDancerPivot_00/_01`, segments `airDancerSeg_00_0…4`.
- Walk-through (no static collider).

## ④ PlayStation

- Chunky low-poly **console + controller on a small crate**, tucked by the cabin
  at ≈ `(26, 19)` (validated, not clipping the cabin footprint). Faint blue
  power-LED emissive. Pure static prop.
- `playstationRef` anchor: `interaction = "playstation"`.
- Hidden `collider_box` around the crate.

## ⑤ Animals — cat · dog · deer · rabbit

- Chunky low-poly critters, each a body + head + legs (+ ears/antlers/tail per
  species) in warm palette tones. Posed standing/sitting.
- Each parented to a **base pivot empty** (`animalPivot_<species>`) so the
  runtime drives idle/hop/graze on one transform. Pivot custom props:
  `species`, `interaction = "animal"`, `wanderRadius` (m), `idle` style hint.
- **Placement split** (all validated onto dry grass, off water/footprints):
  - **Pets** near the cabin: cat ≈ `(20, 18)`, dog ≈ `(24, 16)`.
  - **Wild** in the north meadow: deer ≈ `(4, 28)`, rabbit ≈ `(-3, 24)`.
- Walk-through (no static collider).

---

## Files (all under `tools/blender/scripts/v3/karan/`)

- `misc_common.py` — shared helpers (above).
- `13-misc-fx-title.py` — KARAN MAHAJAN kickable letters.
- `13-misc-fx-controls.py` — controls A-frame board.
- `13-misc-fx-air-dancers.py` — 2 segment-chain air dancers.
- `13-misc-fx-playstation.py` — console + controller crate.
- `13-misc-fx-animals.py` — cat, dog, deer, rabbit.
- `13-section-run-all.py` — full rebuild from zero: bruno foundation → 02 → 03 →
  bruno+karan 04/05/06 layers → **karan 13**, save to `world-v3-karan.blend`.
  (Chains AFTER 06, matching the real repo state — section 06 is built; there is
  no section 12. This supersedes the stale "…→05→12→13" order in the brief.)

Each per-prop script is an additive idempotent delta (`get() or new()`, cleanup
by prefix, `save_as_mainfile`) runnable standalone on the open
`world-v3-karan.blend`, and chained into the from-zero `13-section-run-all.py`.

## Out of scope (this session)

No JS/Three.js, no GLB export, no `src/` edits. Bruno verbatim layer already
built (16 scripts + `13-section-bruno-run-all.py`). No intermediate commits —
one bundled commit at the end after approval; no Co-Authored-By trailer.
