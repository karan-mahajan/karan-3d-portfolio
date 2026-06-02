# Colour Garden — paint-throw delight mechanic

**Date:** 2026-06-01
**Status:** Design approved → plan written
**Branch context:** authored on `bruno-world-analysis`

## 0. Build order (user-directed)

Three phases, delivered as **one final commit** (per `feedback_no_intermediate_commits`):

1. **Phase 1 — Blender assets + placement.** Generate ALL models (sculptures +
   paint cauldron + colour-picker pots) and position them in a clearing inside
   Blender, export one `colour-garden.glb`. User runs the script and eyeballs it.
2. **Phase 2 — Runtime code.** Load + place the garden, colour-pot picking,
   charge/aim/throw, projectile, paint bloom, slow-mo, persistence — built
   consistently with the existing v3 runtime and honouring every memory.
   Runs on a **temporary stand-in clip** so it's testable before Phase 3.
3. **Phase 3 — Animations.** Swap the stand-in for real Mixamo `pickup` + `throw`
   clips (user sources them) wired through the blended state machine.

## 1. Purpose

A **pure-entertainment** interaction — no portfolio content, no information
reveal, no required achievement. The joy of the act is the entire point. It
exists because the world has lots of "good things" but nothing *playful* to do.

Inspired by (not copied from) Bruno Simon's exploding crates. Bruno's is a
*driving* portfolio, so his trigger is the car colliding with crates. We
*walk*, so the delivery mechanism is a **hand throw with a real animation**
instead of a vehicle. The destructive fireball is replaced with a **creative
paint bloom** (colour, not violence).

## 2. Core loop

1. Player walks into a hidden **paint-garden clearing**.
2. A semicircle of **colour pots** ring the cauldron. The pot nearest the player
   is the **active colour** (it glows brighter); an action prompt appears
   ("Hold to paint — <colour>").
3. Player triggers pickup → reach-and-grab animation; a glowing paint **orb in
   the active colour attaches to the right hand**.
4. Player **holds to charge** — a power meter fills; the throw clip is paused
   at its wind-up frame so the character holds a cocked-arm pose.
5. Camera direction aims; **camera pitch sets arc height, charge sets distance**.
6. **Release** → throw clip resumes through release + follow-through; the orb
   **detaches at the release frame** and flies a ballistic arc, gently
   aim-assisted toward the best-aligned statue.
7. On a statue hit → the statue **blooms to the chosen colour in slow-motion**
   with a paint-droplet burst, splat decal, micro screen-shake, and a splat
   sound.
8. Character eases back to idle. Painted statues stay painted (persisted).
9. Repeat — step to a different pot to paint in another colour.

## 3. World setup

New module: **`src/Portfolio/ColourGarden.js`**, wired in `World.js` load order
and `App.js` tick loop (after interactables, before/around the existing
interaction tick).

- **Location:** a free diagonal clearing, proposed centre **~(28, 28)** (south-
  east, between Projects-E and Skills-S), clear of all four cardinal sections
  (which sit at ±52.15m). Final coords tunable during implementation.
- `Nature.addExclusion(28, 28, ~10)` so trees/foliage don't clip the garden.
- **Station (orb source):** a **Blender-generated cauldron** at the garden
  centre, with a glowing emissive paint surface.
- **Colour pots (the picker):** **6 Blender-generated pots** in a semicircle
  around the cauldron, each a different vivid hue (emissive). The pot nearest
  the player = the active colour. Walk-through accents — **no collider**.
- **Targets:** **6 Blender-generated abstract sculptures** (see §3a) — obelisk,
  fluted column, totem stack, orb-on-pedestal, twisted prism, ring-on-base.
  Arranged in a shallow fan **6–14m in front** of the cauldron (inside throw
  range). Each: rendered colourless grey at start, given a static collider sized
  to its visible bbox.

- **Placement is authored in Blender** (Phase 1): every object is positioned in
  a clearing-local space (origin = garden centre) inside the blend and exported
  as **one `colour-garden.glb`**. At runtime ColourGarden loads that GLB, drops
  the whole group onto `terrain.heightAt(gardenX, gardenZ)`, and reads each named
  child's local transform for colliders + paint targeting. This keeps placement
  in Blender (consistent with the rest of the world) while the group stays a
  **standalone GLB — NOT merged into `world-v3.glb`** — so statues remain
  individually paintable (see §8).

## 3a. Asset authoring — a real v3 build SECTION (not a standalone script)

The garden is authored as a proper karan v3 section, **in-world**, so it sits in
the actual world alongside everything else and is rebuilt/repositioned through
the normal pipeline (per the user: "make it a v3 section, part of run-all +
export").

- New section: **`tools/blender/scripts/v3/karan/14-fx-colour-garden.py`** —
  lives in the **FX family (section 14)** like the lava pool, so the existing
  `14-section-run-all.py` and `15-section-run-all.py` build it automatically
  (they glob `14-fx-*.py`). **No renumbering**; finalize (15) + export (16) keep
  their names.
- Mirrors `14-fx-lava.py`: imports `misc_common` (raycast, `find_spot`,
  cuboid/cylinder/sphere builders, `material`, `cull_foliage_near`, `save`),
  builds into a **`colourGarden`** collection, snaps a preferred `ANCHOR` onto
  clear grass with `find_spot`, grounds every object via `height_at`, and orients
  the statue fan to face AWAY from spawn.
- Builds: 6 grey sculptures (cube/cylinder/cone/sphere/torus primitives + a twist
  modifier), a dark cauldron + emissive paint disc, 6 emissive colour pots in a
  semicircle on the player side. `save()`s `world-v3-karan.blend`.
- **Placement (the user's "in my world"):** `ANCHOR = (-12, 12)` (an open NW
  clearing the layout analysis found empty). `find_spot` snaps it clear of
  water/bridges/footprints/rocks/structures. Final spot is tunable — change
  ANCHOR and rerun; user eyeballs in Blender and redirects if wrong.
- **15-finalize** then parents the garden meshes under a `root_colourGarden`
  empty (world pose preserved), exactly like every other section.

**Export (`16-export-glb.py`):** a dedicated `_export_colour_garden()` selects
the whole `colourGarden` collection → **`static/world/colourGarden/colourGarden.glb`**,
recorded under a NEW manifest key **`interactive`**. This key is **NOT** in the
monolithic/instanced/foliage lists `GlbV3World` iterates, so the garden is never
folded into the shared-material prop-merge — that is what keeps statues
individually paintable (§8). `ColourGarden.js` loads this GLB directly.

**Run method:** Blender Python Console via `exec(open(...).read())` (per
`feedback_blender_python_console_over_altp`). Full rebuild =
`15-section-run-all.py`; export = run `16-export-glb.py` headless.

**Naming contract (Phase 2 depends on these exact object names):**
`gardenStatue_obelisk`, `gardenStatue_column`, `gardenStatue_totem`,
`gardenStatue_orbpedestal`, `gardenStatue_twistprism`, `gardenStatue_ringbase`,
`gardenCauldron`, `gardenCauldronPaint`, and pots `gardenPot_crimson`,
`gardenPot_amber`, `gardenPot_gold`, `gardenPot_emerald`, `gardenPot_azure`,
`gardenPot_violet` (pot suffix = hue; runtime maps each to an exact hex).

## 4. Animation state machine

Honours the standing rule (`feedback_animations_must_blend_smoothly`): every
state flows through blended crossfades; the wind-up middle is never skipped.

Two **new Mixamo clips** (user sources + drops in
`static/models/character/animations/`, then wired into the deferred-action
list in `Character.js`; auto-retargeted via `stripRootMotion` +
`retargetMixamoToAvaturn`):

- **`pickup`** — Mixamo "Picking Up" (reach + grab).
- **`throw`** — Mixamo "Throwing" / "Throw Object" / a baseball pitch. Must
  contain wind-up → release → follow-through in one clip.

Flow, using the existing `Character.play(name, { fade, once, then })`:

```
idle ─fade(0.2)→ pickup{once}
   (orb attaches to right-hand bone at grab frame)
pickup ─then→ aim/charge state:
   throw clip starts, then throwAction.paused = true at the wind-up time
   (arm held cocked while the power meter fills)
on release:
   throwAction.paused = false  → release + follow-through plays out
   (orb detaches from hand at the release frame → becomes projectile)
throw ─then→ idle    (chained, crossfaded — no pop)
```

**Charge-hold mechanism:** pause the single throw clip at a configured wind-up
time (`action.time = windUpTime; action.paused = true`), resume on release. No
separate "hold" clip; no second motion to blend.

**Orb hand-attach:** parent the orb mesh to the right-hand bone during
pickup→wind-up; on the release frame, reparent to the scene at the bone's world
transform and launch. (Mirrors how the football is handled around kicks — reuse
that pattern.)

## 5. Aim, charge & throw

- **Charge:** hold input (key + pointer) ramps a 0→1 meter over ~1.0s →
  maps to launch speed / distance. A small on-screen charge indicator (reuse
  existing HUD/`ActionPrompts` styling).
- **Aim:** camera yaw = throw heading; **camera pitch = arc apex height**
  (this is the user's explicit "how far / how low").
- **Aim-assist:** on release, select the statue whose direction is best aligned
  with camera-forward within a cone (e.g. ≤25°) and within range; bias the arc
  to converge on it. If none qualifies, throw a free arc.
- **Projectile:** a **computed ballistic arc** (gravity-styled parametric path),
  *not* a raw rigid body — guarantees reliable, always-satisfying hits and lets
  aim-assist curve cleanly. The orb is a small emissive sphere + point light. On
  reaching the target (or ground for a miss), resolve impact.
- **Hit classification:** distance of impact point from the statue's centre of
  mass → **clean centre hit** vs **glancing hit**. Only clean hits trigger
  slow-motion (keeps it special — Bruno's threshold trick).

## 6. Payoff ("juice"), all WebGPU/TSL

In order on a clean hit:

1. **Slow-motion (global, brief):** ease global time scale to ~0.35× for ~1.2s
   then back. Implemented via a single time-scale multiplier applied in the tick
   loop (and GSAP global timeline scale), mirroring Bruno's `Time.bulletTime`.
   Glancing hits skip this.
2. **TSL colour bloom:** the statue's material floods from the impact point
   outward — a spherical mask grows over the mesh, an emissive flash settles to
   the **active picked colour**. **Colour/emissive only — NO positionNode /
   vertex displacement** (per `reference_no_displacement_on_shared_world_material`).
3. **GPU paint-droplet burst:** a short-lived instanced/points particle spray
   in the hue, fading out (Bruno-style TSL particle node).
4. **Splat decal:** a quick splat sprite at the impact point.
5. **Micro screen-shake:** a few frames of small camera offset.
6. **Sound:** reuse `static/sounds/splash-light.mp3` as the splat SFX for now
   (wired through `AudioManager`); swap for a dedicated paint-splat later.

## 7. Persistence

- Painted statues persist across visits via **localStorage** (same approach as
  `Systems/Achievements.js`). Key e.g. `karan-colour-garden-v1`, storing
  `{ statueId: hue }`.
- On load, ColourGarden restores each painted statue to its stored hue (final
  colour, no bloom animation) so the garden stays colourful.

## 8. Material / perf constraint (hard)

The garden's statues **must not** enter the `GlbV3World` static-prop merge or
share the consolidated node materials (per
`project_v3_material_perf_system` + `reference_no_displacement_on_shared_world_material`).
ColourGarden **owns its statue meshes and their per-instance materials
directly**, so recolouring one never touches the shared system and never
displaces geometry. This is a small, contained set (5–6 meshes) so the perf cost
is negligible.

## 9. Files

**New:**
- `tools/blender/scripts/v3/karan/14-fx-colour-garden.py` — v3 FX section that
  authors the garden in-world (see §3a). Built by the existing run-alls.
- `static/world/colourGarden/colourGarden.glb` — export output (committed).
- `src/Portfolio/ColourGarden.js` — garden load+placement, colour-pot picking,
  charge/aim/throw, projectile, hit resolution, paint bloom, persistence.

**Touched (pipeline):**
- `tools/blender/scripts/v3/karan/16-export-glb.py` — `_export_colour_garden()`
  + `manifest.interactive` (kept out of the world prop-merge).

**Touched:**
- `src/Player/Character.js` — register `pickup` + `throw` deferred clips (Phase
  3); expose a charge-hold helper (pause/resume at wind-up frame) + the
  hand-attach/detach hook. Phase 2 uses an existing clip as a stand-in.
- `src/World/World.js` — construct ColourGarden in load order; expose it on the
  facade.
- `src/App.js` — construct/wire ColourGarden (needs player, playerCamera,
  controller, physics, audio, actionPrompts); tick it; apply the global slow-mo
  `timeScale` multiplier to `frameDelta`.
- `src/Audio/AudioManager.js` — register + play a `splat` one-shot reusing
  `/sounds/splash-light.mp3`.
- Camera shake **reuses the existing** `PlayerCamera.addImpulse(strength)` — no
  new hook needed.

**Assets to source (user):**
- Mixamo **"Picking Up"** + **"Throwing"** clips →
  `static/models/character/animations/`.
- (Later, optional) a dedicated paint-splat sound → `static/sounds/`.

## 10. Out of scope (YAGNI)

- No scoring, no achievement gating, no portfolio-content reveal.
- No multi-orb inventory UI; the cauldron is an infinite source.
- No rigid-body orb physics (computed arc instead).
- No external/downloaded models — all geometry is Blender-authored (§3a) or a
  runtime primitive (the orb sphere). The unused Kenney `statue-*.glb` are NOT
  used.
- No realistic figural busts (don't script well); abstract geometric forms only.
- No new sound asset required for v1 (reuse splash-light).
