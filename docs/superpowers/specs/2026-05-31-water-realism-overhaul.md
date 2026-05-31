# Spec — Water realism overhaul

**Date:** 2026-05-31
**Branch:** bruno-world-analysis
**Module:** [Water.js](../../../src/Effects/Water.js) (+ [Player.js](../../../src/Player/Player.js), [App.js](../../../src/App.js))

## Problem

The runtime water (one TSL plane covering ponds + ocean) reads as a flat "blue
node," not real water. Specifics raised by the user:

1. **Centre looks shallow / too light** — wants it to read as deeper, dark blue.
2. **The border looks like a synthetic blob edge**, not an actual coastline.
3. **No "real water" cues** — no see-through depth, no caustics ("veins"),
   no lively foam.
4. Character entering / wading should feel like water.

## Root causes (from analysis)

- **Depth tint never commits to deep.** Ponds carve only to −1.5 m; water line
  is −0.15, so max pond depth is 1.35 m, but the shallow→deep blend runs over
  `vDepth 0.30→1.35` — only the single deepest texel hits deep blue. The whole
  basin slope stays cyan.
- **Shoreline foam is a clean mathematical ring** — `smoothstep` band breathing
  with one `sin`, plus a uniform alpha fade. No noise, no break-up → "blue node."
- **Surface is an opaque tint, not see-through.** No refraction; the pond floor
  shows through undistorted (or is hidden by alpha), so no sense of water volume.
- **No caustics.** The single biggest missing "real water" cue.
- **In-water state is incoherent.** `Water.playerOverWater()` is terrain-height
  based (correct, fires in ponds), but `Player`/`App` gate wading slowdown,
  the in-water achievement, and ocean-audio depth on a **radial `r > 120`** test
  ([Player.js WATER_ENTRY_RADIUS](../../../src/Player/Player.js)). The walkable
  island is r≈60 and clamps before 120, so that path is **dead code** — you can
  stand in a pond with visible splashes while the game logic thinks you're dry.

## Goals (this pass — shader + code only, no new assets)

- Centre of water bodies reads as a genuine dark blue; rim stays light.
- Shoreline reads as an irregular, animated, lacy foam coastline.
- Water is see-through in shallow/top-down views (refraction of the bottom),
  turning reflective at grazing angles (Fresnel) — physically correct and it
  hides refraction artifacts at screen edges.
- Caustics ("veins") in shallow water.
- Noise-broken surface normals + a directional river current.
- A foam trail behind the wading player.
- **In-water state unified** through terrain water-depth so slowdown,
  achievements, and audio agree with the visible water.

## Explicit non-goals / asset-gated (rule 1 — ask before inventing)

- **Wade / swim character animation.** The Avaturn rig has no swim or wade clip.
  Faking one is forbidden by CLAUDE.md rule 1. Logged as an asset request; the
  procedural splashes/ripples/foam-trail carry the interaction until a clip lands.
- **Full planar/SSR scenery reflections.** WebGL `Reflector` is unavailable on
  the WebGPU/TSL backend; a TSL planar pass is a larger effort. Deferred — the
  Fresnel sky tint + refraction + caustics cover the bulk of the realism gain.

## Acceptance

- Ponds/river centres are clearly darker/bluer than their rims.
- Shoreline foam is irregular and animated, not a perfect ring.
- Looking down into shallow water shows the (distorted) bottom; grazing views
  reflect the sky.
- Caustics visible on shallow basin floors.
- Walking into a pond: slowdown + in-water achievement + ocean audio all engage
  (verified manually by the user).
- Day and night palettes both hold up; no wave crests poke above the grass lip.
