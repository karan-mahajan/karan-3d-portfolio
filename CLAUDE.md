# karan-portfolio — Claude context

3D walkable portfolio. Vanilla Three.js + Rapier3D + Vite. No React, no
framework. The player spawns at origin and walks toward cardinal sections
(Projects E, Skills S, Contact W, Experience N) on a small island surrounded
by ocean.

## Critical rules

### 1. Never invent assets — ask first

If a feature needs a 3D model, texture, sound, or animation **not already**
under `static/models|textures|sounds/`: stop, name exactly what's missing
(file, format, scale, purpose), ask the user how to source it (Kenney /
Sketchfab / Mixamo / they'll drop it in), and wait. Don't procedurally fake
it or load a path that may not exist. Applies especially to Mixamo FBX clips.
Procedural placeholders are OK **only** as an explicit `try/catch` fallback
after a real load attempt, with user buy-in.

### 2. Keep this file < 250 lines

When updating CLAUDE.md, prune before adding. Index-level facts only — no
tutorials, no code blocks longer than ~10 lines, no per-file walkthroughs.

### 3. Match the existing code style

Vanilla ES modules, `class` syntax, private fields with `#`. No TypeScript. No
comments that just restate what code does — only WHY a non-obvious choice was
made. JSDoc summaries on classes/methods are fine.

### 4. Place new props on the terrain heightfield, not at y=0

The terrain is an island with a 0.02m inner floor and waves up to ±0.65m past
r≈22 from spawn. Anything placed at hardcoded `y=0` is buried 0.02–0.65m.
**Always** sample `terrain.heightAt(x, z)` for the group/mesh Y _and_ every
physics collider Y. Reference patterns: [Billboards.js](src/Portfolio/Billboards.js),
[Signs.js](src/Portfolio/Signs.js), [StreetLights.js](src/World/StreetLights.js).

### 5. New solid props need a Rapier collider — sized to the **visible** mesh

If the player shouldn't walk through it OR should stand on top, register one
in [Physics.js](src/Physics/Physics.js): `addStaticCylinder` /
`addStaticCuboid` for static, `addDynamicBall` for pushable. Walk-through
accents (grass, flowers, ferns, pebbles…) get **no** collider.

**Collider must match the visible mesh.** Measure `new THREE.Box3().setFromObject(node)`
on the scaled mesh; pass `(box.min.y + box.max.y)/2` as `y` (cuboid `y` is the
**centre**, no internal lift) and `size.{x,y,z}/2` as half-extents — else feet
sink or float. Refs: [Nature.#placeInstances](src/World/Nature.js),
[Paths.#buildTile](src/World/Paths.js), [Interactables](src/Portfolio/Interactables.js).

### 6. Don't search `node_modules/` for user-referenced files

When the user says "I placed X" or "find the Y file", search only `src/`,
`static/`, `index.html`, `package.json`, repo-root. Never grep into
`node_modules/`, `dist/`, or `.verify/` for user files. `node_modules/` is
fair game **only** when debugging a dependency.

## Stack

- **three@0.184** — **WebGPURenderer** (WebGL2 auto-fallback); all custom
  shading is **TSL** node materials (GLSL `onBeforeCompile` silently no-ops)
- **@dimforge/rapier3d-compat@0.12** — physics (async WASM init; see [Physics.js](src/Physics/Physics.js))
- **camera-controls@3** — third-person follow cam
- **gsap@3** — UI fades + interaction transitions
- **howler@2** — audio (ambient + footsteps + ui sfx)
- **vite@8** — dev server, `publicDir: 'static'`, GLB/FBX/HDR included as assets
- **@vercel/speed-insights** — perf telemetry; Google Tag Manager (GTM-TFN8MHCZ) injected from `index.html`

```
npm run dev      # vite, serves on http://localhost:5173
npm run build    # production build → dist/
npm run preview  # preview built bundle
```

## File map

```
index.html              # loading screen, welcome overlay, controls HUD, GTM
src/main.js             # bootstrap: load → welcome → start journey
src/App.js              # renderer, scene, lights, tick loop, wires all modules
src/style.css           # all CSS

src/Utils/              # Sizes, Loader, Debug
src/Physics/Physics.js  # Rapier init + heightfield ground + collider helpers
src/Player/             # Player, PlayerController, PlayerCamera, Character (Avaturn+Mixamo)
src/World/              # Terrain, Sky, Nature, Grass, Paths, StreetLights, DistantIslands, TimeOfDay, Sun, Wind, Palette, World
src/Portfolio/          # Billboards (single Project Showcase), Signs, Interaction, Interactables, ActionPrompts, WorldMap (data), *Data
src/Effects/            # Fireflies, Water, Rain, Thunderstorm, Leaves, Footprints, WindLines, PostFX
src/UI/                 # UIController (mobile), Compass, Tutorial, AchievementToast/Panel, MiniMap, MapOverlay, MapMarkers, Discovery, coords, map.css
src/Travel/             # TransitionFX (iris wipe), Teleport, Navmask (A* nav grid), ClickToMove (auto-walk)
src/Systems/            # Achievements (42 unlocks + time tracker), DistanceGame (shore mini-game)
src/Audio/AudioManager.js # howler (ambient + footsteps + ui chimes + splashes)
static/models/          # character/ (Avaturn+Mixamo), nature/, extras/, props/, wildlife/
```

## World layout

- Spawn at (0, 0.02, 0). Player faces north (+Z).
- v2 Blender world (post-2026-05-27 resize): walkable perimeter r ≈ 60m,
  terrain mesh ±96.85m, ocean plane ±105m, cardinal sections at ±52.15m.
  Mountains pulled to scale 0.7 of original (far_snow at y≈126), lighthouse
  islet east edge at x=-106.85 (10m offshore). See [tools/blender/scripts/resize-world.py](tools/blender/scripts/resize-world.py)
  + [tighten-backdrop.py](tools/blender/scripts/tighten-backdrop.py) for the
  exact transforms applied to the source blend.
- **Projects** — east at +52.15m, **single Project Showcase** screen at
  `PROJECTS_CENTER` (Billboards.js) that cycles through projects.
- **Experience** — north at +52.15m, signs along `SECTION_POSITIONS.experiencePath`
- **Skills** — south at -52.15m, around `SECTION_POSITIONS.skills`
- **Contact** — west at -52.15m, around `SECTION_POSITIONS.contact`
- Runtime wade/clamp/respawn thresholds (`Past r=45 wades, r=120 clamps,
  y=-5 respawns`) PREDATE the v2 build — they're still calibrated for the
  legacy procedural island and likely need updating to match r≈60 walkable.
- Distant islands ring the horizon (DistantIslands.js) — visual only, no colliders.
- `Nature.addExclusion(x, z, r)` keeps trees out of clearings; always exclude
  new sections so trees don't clip props.

## Tick loop (App.js)

```
physics.step → player.update → playerCamera.update → discovery.update
→ clickToMove.update → miniMap.update → mapOverlay.update → compass.update
→ world.update → wind → grass.setPlayerPos → actionPrompts.tick
→ interaction.tick → interactables.update → ui.tick (mobile)
→ fireflies → water → rain → thunderstorm → windLines → leaves
→ footprints → audio.tick → achievements.tick → distanceGame.update
→ sun + shadow follow player → timeOfDay.tick → streetLights.update
→ water.preRender → postfx.render
```

## Rendering & perf (verified 2026-06-09)

- **Bottleneck is GPU fill, NOT draw calls.** Per frame on a capable laptop:
  ~414 draws, ~15 passes (`info.render.frameCalls`), ~1.18M tris, CPU ~0.7ms.
  The old "75k draw calls" was a misread of the *lifetime* `info.render.calls`
  counter — per-frame truth is `info.render.drawCalls`. Merge/instancing
  already work (~607 drawables).
- **Passes (~15 frameCalls):** 1 sun shadow map (DirectionalLight, 512²,
  PCFSoft, ±18 frustum, follows player each frame) + main scene + one fused
  PostFX node graph (edge tilt-shift → bloom mip chain → tone-map/AgX +
  palette grade). PostFX is skipped entirely when the quality tier disables it.
- **Water = pure-TSL surface, NO render targets.** `Water.preRender()` is a
  no-op; refraction reads the live frame via `viewportSharedTexture`. Don't
  re-add a Reflector/Refractor. IBL PMREM (128³) regen is throttled (sky-move
  + ≥12 frames), not per-frame ([Environment.js](src/World/Environment.js)).
- **Particles are GPU-TSL** (time-driven uniforms, no per-frame buffer upload):
  Snow/Rain/WindLines/Fireflies. Leaves stays CPU (stateful settle-on-terrain).
- **Debug HUD** ([Debug.js](src/Utils/Debug.js)): `?debug` = fps/tris/draws/
  passes/cpu/mem; `?debug=calls` adds per-system draw attribution + shadow
  re-submit count. No GPU-time readout — WebGPU r184 exposes no timestamps.

## Conventions

- Boot is async; `App.boot()` returns `{ character, world }`. Loader emits
  `progress` events; main.js drives the loading-bar fill.
- `session-storage` flag `karan-portfolio:journey-started` skips the welcome
  overlay on subsequent reloads. Loading + welcome overlays must sit above
  ALL HUD layers (compass, achievement toast — they hide until
  overlays clear).
- Controller is **paused** while overlays (loading, welcome, interaction
  modal, action one-shots) are up, then unpaused.
- Audio must start on a user gesture (browser policy) — handled in main.js.
- Physics: heightfield ground from `terrain.heightAt`. Player = Rapier
  kinematic-position char controller; football is the only dynamic body.
  **Fixed timestep 1/60 + accumulator** (≤5 steps/frame, frameDelta clamped to
  0.1s); render interpolates char pos between substeps (App.js ~1775–1839). The
  old "variable timestep wart" note was WRONG — motion is already smooth.
- Fog tinted `#ffb084`, range 65→165, so distant trees fade into sunset.
- **Achievements** (`Systems/Achievements.js`): 42 unlocks w/ rarity tiers
  (common→legendary), time tracker, rarity-themed toast on unlock, full panel
  on trophy click or `J` (completion %, per-category badges, NEW badge, 100%
  celebration). Persists to localStorage. App tick feeds it
  player pos / moving / running / grounded / inWater / mode / isRaining.
- **Character animation** (`Player/Character.js`): Avaturn T-pose avatar +
  bare-named clip GLBs; base idle = `idle.glb`; `breathing-idle.glb` plays
  ONLY ~4s after stopping from a run (no embedded-anim idle, no look-around
  gesture, no startWalking bridge — all removed 2026-06-09). Every clip is
  rest-pose-rebased (`rebaseClipToBind`) AND Z-up-normalized
  (`normalizeClipUpAxis`) at load — skipping either twists arms / sinks the
  body. WALK/RUN speeds track the clips' measured natural paces (1.65 /
  4.43 m/s) — keep within ~20% or locomotion reads frantic. Jumps: two
  in-place arcs picked by takeoff speed; knobs in `Player.JUMP_ANIM`.
- **Snow outfit** (`Player/OutfitSwap.js`): `avatar-snow.glb` meshes grafted
  onto the live skeleton (bones matched by name), revealed by a TSL frost-line
  wipe; App tick swaps at weather coverage ≥0.4, back at ≤0.12.
- **Tutorial** (`UI/Tutorial.js`): first-visit coachmarks for WASD/joystick,
  drag-to-look, zoom. Detects look/zoom from raw input events, NOT camera
  state (camera-controls smoothes and gives false positives).
- **Compass** (`UI/Compass.js`): camera-linked HUD ring, rotates with camera
  yaw, hidden on mobile.
- **Distance-guess** (`Systems/DistanceGame.js`): mini-game at the shore.
  Exact-only wins; the win card auto-dismisses.
- **Map system** (`UI/MiniMap.js`, `UI/MapOverlay.js`, `Travel/*`): parchment
  mini-map → full overlay on click or `M`; marker click = iris-wipe teleport
  with collision-clear landing via Navmask; land click drops a flag and
  auto-walks via `PlayerController.setVirtualInput` (WASD cancels). Data in
  [WorldMap.js](src/Portfolio/WorldMap.js); sessionStorage key
  `karan-world-discovered-v1`. Backtick = navmask debug overlay.

## Verification

The user usually verifies manually — **ask before running headless probe
loops or screenshot runs**. If you do probe: scripts live in `.verify/scripts/`
(`verify-<feature>.mjs`), shots in `.verify/shots/YYYY-MM-DD/` (compute the date
at runtime, never hardcode); boot via `bootAndDismiss(page)` from
[\_boot.mjs](.verify/scripts/_boot.mjs). `.verify/` is gitignored; Playwright is
NOT a project dep (install globally, reuse via `NODE_PATH`).

## Known parked work (don't surprise the user with rewrites)

- **Push is a comedy gag** — trees/rocks/signs/billboards/compass are push spots
  so [ActionPrompts.js](src/Portfolio/ActionPrompts.js) rotates a joke pool. Real
  pushables: crate + bag. Lying-down props (`kind: 'log'`) excluded. Don't "fix".
- **B (backflip) / C (cartwheel)** don't raycast for clearance.
- **Furniture pass removed** (12e494a) — don't re-add without asking.
- **Material/perf system is user-validated — don't break.** GLB mats → ~2 shared
  node materials + spatial-chunk STATIC-prop merge in [GlbV3World.js](src/World/GlbV3World.js).
  NEVER merge/re-material animated or name-looked-up meshes (skillSphere_/lava/
  miscFx/bonfire_/terrain). Rules: docs/v3-runtime/material-consolidation-analysis.md.

## When in doubt

- [App.js](src/App.js) = wiring. [World.js](src/World/World.js) = load order.
- If an asset/animation isn't in `static/`, **ask** (rule 1).

# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
