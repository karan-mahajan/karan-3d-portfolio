# Skills Sphere → "Observatory" Redesign

**Date:** 2026-05-31
**Status:** Design — awaiting user review
**Touches:** `src/Portfolio/SkillSphere.js`, `src/style.css`, and read-only use of `src/World/TimeOfDay.js`, `src/Player/PlayerCamera.js`

## Problem

The Skills installation (built by Codex) lets the player press E near the south
pond to fly the camera into a glowing sphere ringed with floating skill cards.
The concept is good but it "doesn't feel right." Three concrete causes:

1. **The structure is frozen.** The skill cards (`labelRoot`) rotate, but the
   Blender-authored rings and core are separate scene objects that never move.
   The eye reads the rings as "the globe," so the cards appear to drift
   independently of a dead-still cage. This is the headline complaint.
2. **The camera is pinned to dead center** (`distance` locked `0.1`, polar
   locked near the equator, no zoom). From a fixed point you only swivel — it
   feels flat, with no parallax or depth, and the top/bottom cards are hard to
   reach.
3. **Color carries all the meaning, and it clashes.** Category is encoded by
   accent color alone (inaccessible for colorblind users), the neon-green
   theme fights the warm sunset world, and there is no adaptation between day
   and night so readability suffers at one end or the other.

## Goal

Turn the installation into a living **Observatory**: a warm brass-and-teal
orrery whose rings spin at different speeds and carry the skill cards as one
mechanism, that adapts its glow and contrast to time of day, harmonizes with
the grass/trees/sky, and that the player can actually look around inside with
depth and freedom.

Non-goals (YAGNI): no DOM/screen-reader fallback list, no re-authoring of the
Blender geometry, no change to the press-E entry trigger or proximity logic,
no new assets.

## Chosen direction

"Observatory" identity (selected over Constellation and Reactor): differential
ring motion, warm gold + teal palette keyed to the sunset world, calm/premium
feel, day/night adaptive. Approved by user via visual companion 2026-05-31.

---

## Design

### 1. Living rings, coupled to the cards

The single most important change. The runtime must animate the Blender rings so
the whole assembly reads as one rotating instrument.

**Rings to drive** (fetched by `scene.getObjectByName`, the pattern
`#collectCoreVisuals` already uses):
`skillSphere_orbit_ring_equator`, `..._meridian_a/b/c/d`,
`..._orbit_lat_north_mid/south_mid/north_high/south_high`, `..._orb_shell`,
`..._energy_column`, `..._core_inner`, `..._core_halo`.

**Differential rotation** — assign each ring group a base spin rate and axis so
they move at visibly different speeds (orrery feel), not in lockstep:
- Equator: slow spin about the vertical (Y) axis.
- Meridians: medium spin, opposite direction, about their own tilt axis.
- Latitude rings: gentle counter-spin.
- Core inner: slow rotate; core halo: near-static breathing; energy column:
  slow rotate + subtle vertical shimmer.

**Pivot caveat:** rotation must pivot about the sphere center. If a ring mesh's
local origin is not at the center (verify per object after GLB load), wrap it in
a `THREE.Group` positioned at `this.center` and rotate the group, reparenting
the mesh into it once at construction. Otherwise rotate the mesh directly.

**Card coupling:** the card orbit (`labelRoot.rotation.y`) keeps its current
drift but its speed is derived from the same base rate as the equator ring (a
shared constant), so cards and rings read as carried by one mechanism rather
than two independent animations. Keep the gentle X-wobble.

**Two speeds:**
- *Idle / outside* — assembly spins at a readable "alive" pace so it looks
  active from the shore (current idle card speed `0.36` is the reference feel).
- *Inside / active* — everything eases to a calm browse pace (~current `0.16`),
  so reading isn't dizzying.

The existing core-hide-on-enter behaviour (`#setCoreVisible(false)`) is
**removed or revised**: in the Observatory the rings and core stay visible
inside (dimmed), since they're now the moving structure the player is sitting
within. (Confirm during implementation that the column/core don't occlude the
center camera; if they do, fade their opacity rather than hard-hiding.)

### 2. Free the inside camera

Replace the pinned-center rig in `#setInsideControlsFromDirection` /
`#applyInsideCamera` with a small orbit that gives depth:

- **Allow dolly:** `minDistance` small (≈`0.1`) → `maxDistance` ≈ `2.5` so the
  player can pull back toward the shell for parallax, and scroll-to-zoom works.
  Replace the current `#applyInsideCamera` that copies `this.center` verbatim
  with an offset orbit: camera sits at `center + sphericalOffset(distance,
  azimuth, polar)` and looks at `center`. (When `distance` is near zero this
  matches today's look-from-center; as it grows the player gets depth.)
- **Fuller pitch:** widen the polar clamp toward `0.02π … 0.98π` so the
  top/bottom cards of the fibonacci sphere are reachable.
- **Idle auto-drift:** when the user isn't actively dragging, apply a slow
  azimuth drift so the scene breathes and the "you can look around" affordance
  is obvious. Cancel drift on user input; resume after a short idle.
- Keep the polished GSAP enter/exit zoom transitions unchanged.
- Restore all saved control limits on exit (existing
  `#restoreInsideControlLimits` extended for the new fields).

### 2b. Cards always upright, never inverted, readable from every angle

The cards must read correctly no matter where the camera is or how far the rings
have spun — never mirrored, never upside-down. This is a hard requirement.

- **Full billboarding to the camera.** Each card's world orientation faces the
  camera every frame (the existing `update()` already does
  `parentQuat⁻¹ · cameraQuat`). This must be preserved so card *facing* is fully
  decoupled from ring/`labelRoot` spin — the rings rotate underneath, the cards
  pivot to stay flat-on to the viewer. Because they always face the camera, the
  reader never sees the back face.
- **Lock the up-vector to world-up.** Pure camera-quaternion copy lets cards
  roll with camera roll; for guaranteed-upright text, orient each card to *look
  at the camera position while keeping world-up as its up axis* (yaw/pitch to
  camera, zero roll). Result: text stays horizontal and upright from any
  azimuth, including the back side of the sphere and the top/bottom cards.
- **No mirroring from `DoubleSide`.** Cards keep `DoubleSide` only as a safety
  net; with correct billboarding the front face is always presented, so the
  canvas text is never seen reversed. Verify a back-of-sphere card reads
  left-to-right, not mirrored.
- This applies in both states — idle (cards orbiting on the spinning rings, seen
  from outside) and inside (cards all around the center camera).

### 3. Readability — depth fade

Cards currently use `depthTest:false`, so far-side cards can draw over near-side
cards in arbitrary order (the clutter/overlap). Add **distance/angle-based
opacity**: each frame, fade a card by how far it faces away from the camera
(dot product of card-direction-from-center vs camera-forward, or world-space
distance to camera). Front cards bright, side/back cards dim. This removes
overlap noise and adds depth cueing. Folds into the existing per-label opacity
lerp in `update()` (the `opacityLift` block) rather than adding a new pass.

### 4. Accessible, harmonized cards

**Category encoded three ways, not color-alone:**
- the existing category text chip (keep, make it primary),
- a small **per-category icon/shape** drawn on the canvas board (new),
- the accent color (retained but retuned).

**Retuned palette** (warm-world-harmonized, distinct hues, hold contrast on both
bright and dark card backdrops):

| Category        | Accent    |
|-----------------|-----------|
| Frontend        | `#4a90d9` (blue) |
| Backend & DB    | `#7fd1a8` (green) |
| DevOps & Tools  | `#e0a05a` (amber) |
| CMS             | `#d98aa8` (rose) |
| Other           | `#c4a6e8` (violet) |

Card base shifts from cold near-black `rgba(4,9,8,0.97)` to a **warm charcoal**
so it sits with the sunset world; text stays cream `#f6f1df`. Reduce `shadowBlur`
glow bleed on small/medium boards so edges stay crisp. Structure (rings/core,
title, hint) moves from pure neon green to the **brass gold `#e6c172` + teal
`#6fd6c4`** identity.

### 5. Time-of-day adaptation

Read `this.timeOfDay?.mode` (the binary `'day'`/`'night'` property `TorchLight`
already reads). Inject `timeOfDay` into `SkillSphere` from `App.js` (new
constructor param, same wiring style as `audio`/`achievements`).

Maintain two tuned target sets and cross-fade between them when the mode flips
(GSAP, mirroring how `TimeOfDay` tweens `billboards.emissiveBoost`):
- **Day target:** muted ring/core glow, higher card-background opacity and
  border contrast → readable against the bright sky.
- **Night target:** stronger ring/core glow (the installation becomes a warm
  beacon), card background can lighten its glow since the backdrop is dark.

The card canvas textures are static; per-mode contrast is achieved by animating
material `opacity` / an emissive-style boost and the ring material glow, not by
re-rasterizing canvases every transition. (If finer per-mode card redraw is ever
wanted, that's a later refinement — not in scope.)

### 6. Control hint

Extend the existing `.skill-sphere-hint` DOM to include a one-line controls cue
("drag to look · scroll to zoom · ESC to exit") so the new camera freedom is
discoverable. Restyle the hint border/accent to the gold+teal identity.

---

## Components & boundaries

All runtime changes live in **`src/Portfolio/SkillSphere.js`**; styling in
**`src/style.css`**. Internal structure stays as private methods so the public
surface (`near`, `enter`, `exit`, `update`) is unchanged — `Interaction.js` and
`App.js` callers are untouched except the one new `timeOfDay` constructor arg.

New private helpers (names indicative):
- `#collectRings()` — fetch + (if needed) pivot-wrap the ring objects.
- `#animateStructure(delta)` — differential ring/core rotation.
- `#categoryIcon(ctx, category, ...)` — draw the per-category shape on a board.
- `#applyTimeOfDay(mode)` — cross-fade day/night targets.
- `#fadeByDepth(label)` — folded into the existing label loop.
- `#applyInsideCamera(delta)` — rewritten for offset orbit + idle drift.

## Testing / verification

Per project convention, manual verification by the user (they verify manually;
no automated screenshot probes). Implementation hands off a running dev build
for sign-off. Checks to confirm:
1. Rings visibly spin at different speeds, idle (from shore) and inside.
2. Inside camera can zoom/dolly, look up/down, and idly drifts.
3. Cards: far-side cards dim, no overlap clutter; category icons present.
   Every card is upright and reads left-to-right (not mirrored/inverted) from
   all angles — back of sphere, top, bottom — both idle and inside.
4. Palette reads well at both day and night; switch time-of-day and confirm
   the cross-fade.
5. Enter/exit transitions still smooth; ESC restores third-person camera.

## Risks

- **Ring pivot:** if mesh origins aren't centered, naive `.rotation` spins them
  off-axis. Mitigated by the pivot-group wrap (verify per object).
- **Core occlusion:** keeping core/column visible inside may block the center
  view — fade instead of hide if so.
- **Variable timestep:** App uses variable delta; ring speeds are `delta`-scaled
  already, consistent with current code.
