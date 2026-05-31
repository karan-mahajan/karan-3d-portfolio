# Plan — Water realism overhaul

Spec: [2026-05-31-water-realism-overhaul.md](../specs/2026-05-31-water-realism-overhaul.md)

One commit at the end (per project convention), after the user confirms it
works in-game. No intermediate commits, no automated verify probes.

## 1. Coherence fix (gameplay/audio agree with visible water)

- **Player.js** — replace the radial `distFromCenter > WATER_ENTRY_RADIUS` wade
  gate with terrain water-depth: `depth = WATER_SURFACE_Y − terrain.heightAt(x,z)`.
  Slowdown scales with depth (ankle-deep barely slows; chest-deep ~40% speed),
  clamped to `WATER_SLOWDOWN_MIN`. Keep `MAX_TRAVEL_RADIUS` as the void guard.
  Add `WATER_SURFACE_Y = -0.15` constant (matches Water `WATER_LEVEL_Y`).
- **App.js** — drive `inWater` / `waterDepth` for achievements from
  `water.playerOverWater()` + terrain depth instead of `r > 120`.

## 2. Water.js shader rework (all procedural, no assets)

New TSL imports: `fract, floor, min, step, viewportUV, viewportSafeUV,
viewportSharedTexture, mx_fractal_noise_float, mx_worley_noise_float`.

- **Deeper/darker tint** — pull the deep blend in (`smoothstep(0.18, 0.95, …)`),
  darken/saturate the day deep colour, and add a mild depth darkening multiplier
  so basin centres commit to dark blue. Raise opacity-with-depth.
- **Refraction** — sample `viewportSharedTexture(viewportSafeUV(uv + n.xz*k))`;
  `k` scales with shallowness and a top-down view factor (`V.y`). Mix the
  refracted bottom into the water colour only where shallow + looking down, so
  grazing angles fall back to the Fresnel sky reflection (artifact-free).
- **Caustics** — `mx_fractal_noise_float` sampled at two scrolling offsets,
  `pow(1 − |a − b|, k)` veins, masked to shallow water + inland, added to colour.
- **Foam** — break the shoreline band with `mx_worley_noise_float` (scrolling)
  so it's lacy and irregular; keep the tidal breathe. Add foam where the worley
  cells are bright near the waterline.
- **Normals** — add a low-amp `mx_fractal_noise` perturbation to the analytic
  ripple normal for organic break-up.
- **River current** — bias the inland `flowBands`/`currentRipple` along a
  dominant direction so the river reads as flowing, not sloshing.
- **Foam trail** — additive foam streak trailing the player's wake while wading.

## 3. Hand-off

- Build sanity (`npm run build`) to catch TSL graph errors, then hand to user
  for in-game verification. Flag the wade/swim animation + planar-reflection
  items as the remaining (asset/large-effort) work.

## Risk notes

- `viewportSharedTexture` samples the opaque buffer before the transparent pass;
  water is `transparent`, `depthWrite:false`, `renderOrder:2` → bottom is present.
  Keep distortion small; clamp UV with `viewportSafeUV` to avoid edge smear.
- Caustics/foam noise: a few octaves on a 144² plane — cheap.
- If `viewportSharedTexture` misbehaves on this backend, refraction is the one
  isolable piece to drop; the rest stand alone.
