# Intro Cinematic — Design Spec

**Date:** 2026-05-31
**Status:** Awaiting user review
**Branch:** `bruno-world-analysis` (current)

## Goal

Replace the static loading → welcome-compass → world handoff with a cinematic
arrival: the character falls ~30 m out of the sunset sky into the real 3D
world, lands in a superhero power-landing, and the ground breaks with a
stylized procedural impact (cracks, dust, debris, shockwave, screen shake).
The wow of the splash is the hook — "if they like the splash, they'll explore
the whole world."

## Locked decisions (from brainstorming)

| Decision | Choice |
|---|---|
| Approach | Real in-engine cinematic (character falls through the actual 3D scene) |
| Flow | Auto-drop with one gate — a single **"▶ Drop in"** button replaces the compass welcome screen |
| Landing | Superhero power-landing (one knee, fist down, rise) |
| Break FX | Stylized procedural — runtime canvas crack decal + dust ring + debris + shockwave; **no new texture assets** |
| Loader | Redesigned to match the cinematic (atmospheric, themed bar + status lines + Drop-in button) |
| Replay | Plays every load, but a click or any key **instantly skips** to standing at spawn |
| Camera | Sweeping world-reveal (starts high over the island, sweeps as he falls, settles behind player on land) |
| Duration | Cinematic ~4–5 s from tap to player control |
| Landing spot | Dead-center spawn (0, terrain.heightAt(0,0), 0), facing north (+Z) — matches current spawn |

## Assets

User supplied three Mixamo FBX clips (Without Skin · FBX Binary · 30fps),
staged at `static/models/character/animations/`:

- `falling.fbx` (264 KB) — "Falling Idle", looping descent
- `hard-landing.fbx` (1.5 MB) — "Hard Landing", one-shot impact + rise
- `falling-to-landing.fbx` (292 KB) — "Falling To Landing", **backup** combined clip

**Note:** `hard-landing.fbx` is unusually large (1.5 MB vs ~280 KB) — conversion
step must verify it retargets cleanly onto the Avaturn rig. If it fails or looks
wrong, fall back to `falling-to-landing.fbx` as a single fall→land clip.

No other new assets. Cracks/dust/debris are all generated in code.

## Sequence (first load and every load)

1. **Redesigned loader** shows while `App.boot()` streams assets. Progress bar
   fills (monotonic, as today); rotating status lines play.
2. At 100%, loader content resolves to a single **"▶ Drop in"** button (the
   compass welcome screen is removed). Controller stays **paused**.
3. **Tap "Drop in"** → unlock audio (`app.audio.start()`), hide loader, start
   `IntroCinematic.play()`.
4. **Descent (~2.5–3 s):** character placed at spawn-XY, y ≈ 30, playing
   `falling` (loop). Camera begins high above the island (sunset framing) and
   sweeps down/around as the character falls. Physics controller stays paused —
   the fall is a scripted visual tween, not physics.
5. **Impact:** on reaching ground Y, switch to `hardLanding` (one-shot), and
   fire `GroundBreak` at the landing point: radial crack decal, dust ring,
   debris flecks, shockwave ring, **screen shake + camera bounce**.
6. **Recover & handoff (~1–1.5 s):** if `hardLanding` ends crouched, chain to
   existing `standingUp`, else settle to `idle`. Camera eases into the normal
   third-person resting offset; `PlayerCamera.resync()` hands control back to
   the orbit cam. Enable the physics controller. Cracks linger ~3 s then fade.
7. **HUD reveal:** compass + first-visit tutorial/coachmarks fade in (existing
   systems), exactly where they'd appear today.

**Skip:** any click or keydown during steps 4–6 cancels the cinematic — snap
character to standing at spawn, snap camera to resting offset, enable
controller immediately. Idempotent (safe to fire once).

## Architecture

New code is isolated so existing physics, material/perf, and gameplay are
untouched. The cinematic is a **pre-gameplay layer** that hands off cleanly.

### New: `src/Travel/IntroCinematic.js`

Owns the whole sequence. One public `play({ onComplete })` returning a promise
that resolves when control hands off, plus `skip()`.

- **Inputs (constructor):** `character`, `playerCamera`, `player`/`controller`,
  `terrain` (for `heightAt`), `groundBreak`, `audio`.
- **Descent:** sets `character.root.position` to `(0, startY, 0)` and tweens Y
  down with an ease-in (gravity feel) over the descent duration. Drives camera
  each frame along a scripted path (see Camera below). Uses the existing tick
  loop — `IntroCinematic.update(delta)` is called from `App` while active, or
  it self-drives via its own rAF/GSAP timeline. **Decision for plan:** prefer
  GSAP timeline (already a dep) for the camera + Y tweens; simplest and
  matches existing UI-transition patterns.
- **Impact detection:** when tweened Y ≤ ground Y, trigger impact once.
- **Handoff:** calls `playerCamera.resync()`, unpauses controller, resolves.
- **State guard:** `#active`, `#done` flags so `skip()` and natural completion
  can't double-fire.

### New: `src/Effects/GroundBreak.js`

Procedural impact FX, self-contained and disposable. `burst(position, opts)`:

- **Crack decal:** a canvas (2D) draws branching radial cracks → `CanvasTexture`
  on a small ground-facing transparent plane at the impact point, slightly
  above terrain to avoid z-fight. Fades alpha to 0 over ~3 s, then disposes.
- **Dust ring:** an expanding, fading ring (additive transparent plane or a
  small particle puff) — reuse the look of existing dust if any; else a simple
  expanding torus/plane.
- **Debris:** a short-lived points/instanced burst of flecks thrown outward and
  down, gravity-pulled, faded out (~1 s). Pure visual, no physics bodies.
- **Shockwave:** a thin expanding ring on the ground, quick fade.
- All meshes added to scene, removed + geometry/material disposed on completion.

### `src/Player/Character.js` (small additions)

Add to `MIXAMO_CLIPS`:

```js
{ action: 'falling',     url: '/models/character/animations/falling.glb' },
{ action: 'hardLanding', url: '/models/character/animations/hard-landing.glb' },
```

`falling` loops (`THREE.LoopRepeat`); `hardLanding` plays `{ once: true }` and
chains to `standingUp` or `idle`. No other Character changes — the existing
`play()`/cross-fade/`#onActionFinished` machinery handles it.

### `src/Player/PlayerCamera.js` (small additions)

- A **cinematic mode**: while active, `update()` is bypassed (reuse the existing
  `locked` flag, or add a parallel `cinematic` flag) and the camera is driven by
  `IntroCinematic`. `resync()` already exists to recover the orbit state on
  handoff.
- **Screen shake / camera bounce:** an additive decaying positional offset
  applied during the impact window (small amplitude, ~0.4 s decay). Lives in
  PlayerCamera as `addImpulse(strength)` so it could be reused by other heavy
  events later.

### Loader redesign — `index.html` + `src/style.css` + `src/main.js`

- **`index.html`:** restyle `#loading-screen` content; the compass
  `#welcome-screen` is removed (or repurposed). Add the **"Enter Karan's
  World"** button.
- **`src/style.css`:** atmospheric themed loader (sunset palette to match fog
  `#ffb084`), refined progress bar, button styling + a subtle idle animation.
- **`src/main.js`:** boot flow change — on 100%, swap loader to the Drop-in
  button. Button tap (or the existing key-start path) → `app.audio.start()` →
  `intro.play()` → on resolve, unpause controller + start tutorial. The current
  `sessionStorage` fast-path is replaced by "always play, skippable" behavior.

### `src/App.js` (wiring only)

Construct `GroundBreak` and `IntroCinematic`, expose `app.intro`. Add
`intro.update(delta)` to the tick loop guarded by an active flag (no-op when
inactive). No reordering of existing systems.

## Edge cases

- **Boot fails:** if `app.boot()` rejects, show the existing error text — no
  cinematic. (Unchanged from today.)
- **Character load fails (placeholder):** if `result.character.ok === false`,
  skip the cinematic, fall straight to standing at spawn with the existing
  placeholder messaging.
- **`hardLanding` retarget bad:** fall back to `falling-to-landing` as a single
  clip; if that also fails, skip impact animation but still fire the break FX
  and hand off (degrade gracefully).
- **Reduced motion:** respect `matchMedia('(prefers-reduced-motion: reduce)')`
  — skip the fall, fade the world in with the character already standing.
- **Mobile:** cinematic runs identically; the Drop-in button is the audio
  gesture. Camera path uses the same world-reveal (mobile zoom factor still
  applies on handoff).
- **Tab blur mid-cinematic:** existing audio pause-on-blur applies; the GSAP
  timeline keeps real-time, so a long blur won't strand the character — on
  return it's already landed/handed off (or the skip path covers it).

## Out of scope (don't build now)

- Physical Rapier debris chunks (option 3 from break-fx) — can graft on later.
- Photo-real textured crater (needs a texture asset) — not chosen.
- Per-section "drop in" re-entry from teleport — this is the **first-arrival**
  cinematic only.

## Verification

Per project rules, verification is **manual by the user** (no automated
screenshot/probe loops). The one scripted step is the **FBX→GLB conversion**
(`extract-fbx-as-glb.mjs`), which prints clip name + duration so we can confirm
the retarget before wiring. After implementation, user walks the intro on
desktop + mobile and confirms: fall reads, landing syncs, break fires, camera
hands off smoothly, skip works, reduced-motion path works.

## Resolved (was open)

1. **Descent start height:** 30 m (confirmed).
2. **Button text:** **"Enter Karan's World"** (themed, not literal "Drop in").
3. **Compass orientation:** improved — drop the static welcome card; after
   landing, the four cardinal section labels (Experience N · Projects E ·
   Skills S · Contact W) fade in around the compass HUD ring for ~3 s, then
   fade out. Orients newcomers in-world without a blocking screen.

## Side task (separate from cinematic)

User reports a stray faceted-dome mesh (with a cylindrical stub) baked into
**all Mixamo models**, wants it removed. Good news: the FBX→GLB conversion
(`extract-fbx-as-glb.mjs`) already strips every `isMesh`/`isSkinnedMesh` node,
so geometry won't survive into the GLBs the game loads. To confirm: inspect a
converted clip's scene graph for any non-mesh leftover (empty/bone/helper) and
strip it if present. Handle during the conversion step.
