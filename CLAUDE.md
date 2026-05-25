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

### 2. Keep this file < 200 lines

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

**Collider must match the visible mesh.** Use `new THREE.Box3().setFromObject(node)`
on the scaled mesh; pass `(box.min.y + box.max.y) / 2` as `y` and
`size.{x,y,z}/2` as half-extents. Reference:
[Nature.#placeInstances](src/World/Nature.js),
[Paths.#buildTile](src/World/Paths.js),
[Interactables.#buildStuckCrate](src/Portfolio/Interactables.js). Wrong sizing
= feet sink in or float inside.

**Note:** `addStaticCuboid(x, y, z, hx, hy, hz)` — `y` is the cuboid's
**centre**, no internal lift. Mesh origin at bbox bottom → `bottom + hy`;
measured bbox → `(box.min.y + box.max.y) / 2`.

### 6. Don't search `node_modules/` for user-referenced files

When the user says "I placed X" or "find the Y file", search only `src/`,
`static/`, `index.html`, `package.json`, repo-root. Never grep into
`node_modules/`, `dist/`, or `.verify/` for user files. `node_modules/` is
fair game **only** when debugging a dependency.

## Stack

- **three@0.184** — renderer, scene, lights, materials
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
src/Systems/            # Achievements (34 unlocks + time tracker), DistanceGame (shore mini-game)
src/Torch/TorchLight.js # night-mode hand-attached torch + F-aim shoulder IK
src/Audio/AudioManager.js # howler (ambient + footsteps + ui chimes + splashes)
static/models/          # character/ (Avaturn+Mixamo), nature/, extras/, props/, wildlife/
```

## World layout

- Spawn at (0, 0.02, 0). Player faces north (+Z).
- Island radius ≈ 45m; shore slope 45→57m down to y=-2 ocean floor.
- **Projects** — east, **single Project Showcase** screen at `PROJECTS_CENTER`
  (Billboards.js) that cycles through projects. Replaced the old per-project
  fan; legacy `world.billboards.items[0]` is the showcase itself.
- **Experience** — north, signs along `SECTION_POSITIONS.experiencePath`
- **Skills** — south, around `SECTION_POSITIONS.skills`
- **Contact** — west, around `SECTION_POSITIONS.contact`
- Past r=45 player wades (→ 15% speed); past r=120 soft-clamps back. Below
  y=-5 respawns at origin.
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
→ torchLight.tick → water.preRender → postfx.render
```

## Conventions

- Boot is async; `App.boot()` returns `{ character, world }`. Loader emits
  `progress` events; main.js drives the loading-bar fill.
- `session-storage` flag `karan-portfolio:journey-started` skips the welcome
  overlay on subsequent reloads. Loading + welcome overlays must sit above
  ALL HUD layers (torch hint, compass, achievement toast — they hide until
  overlays clear).
- Controller is **paused** while overlays (loading, welcome, interaction
  modal, action one-shots) are up, then unpaused.
- Audio must start on a user gesture (browser policy) — handled in main.js.
- Physics: heightfield ground sampled from `terrain.heightAt`. Player uses
  Rapier's kinematic-position character controller; football is the only
  dynamic body. Variable timestep — known wart, not yet fixed.
- Fog tinted `#ffb084`, range 65→165, so distant trees fade into sunset.
- **Achievements** (`Systems/Achievements.js`): 34 unlocks, time tracker, toast
  on unlock, full panel on key. Persists to localStorage. App tick feeds it
  player pos / moving / running / grounded / inWater / mode / isRaining.
- **Tutorial** (`UI/Tutorial.js`): first-visit coachmarks for WASD/joystick,
  drag-to-look, zoom. Detects look/zoom from raw input events, NOT camera
  state (camera-controls smoothes and gives false positives).
- **Compass** (`UI/Compass.js`): camera-linked HUD ring, rotates with camera
  yaw, hidden on mobile.
- **Torch** (`Torch/TorchLight.js`): night-only, hand-attached mesh, F to aim
  mouse beam with smoothed one-bone IK on the shoulder. Suppressed while
  modals/interactions are open.
- **Distance-guess** (`Systems/DistanceGame.js`): mini-game at the shore.
  Exact-only wins; the win card auto-dismisses.
- **Map system** (`UI/MiniMap.js`, `UI/MapOverlay.js`, `Travel/*`): parchment
  mini-map → full overlay on click or `M`; marker click = iris-wipe teleport
  with collision-clear landing via Navmask; land click drops a flag and
  auto-walks via `PlayerController.setVirtualInput` (WASD cancels). Data in
  [WorldMap.js](src/Portfolio/WorldMap.js); sessionStorage key
  `karan-world-discovered-v1`. Backtick = navmask debug overlay.

## Verification sandbox — MUST use `.verify/scripts/` + `.verify/shots/<date>/`

No exceptions, no `/tmp/`, no flat `.verify/*.png`. Layout:
`.verify/scripts/verify-<feature>.mjs` + `.verify/shots/YYYY-MM-DD/<name>.png`.

Rules: (1) compute shots dir at runtime via `new Date().toISOString().slice(0, 10)`
+ `fs.mkdirSync(..., { recursive: true })` — never hardcode a date;
(2) run from project root with `URL=http://localhost:5173/ node .verify/scripts/<file>.mjs`;
(3) `ls .verify/scripts/` first — copy an existing driver, don't duplicate;
(4) always boot via `bootAndDismiss(page)` from [\_boot.mjs](.verify/scripts/_boot.mjs)
— never inline your own dismissal loop.

`.verify/` is gitignored. Playwright is not a project dep — install once globally
(`cd /tmp && npm install --no-save playwright`), reuse via `NODE_PATH`. Canonical
driver: [verify-walk.mjs](.verify/scripts/verify-walk.mjs).

## Known parked work (don't surprise the user with rewrites)

- **Push is a comedy gag** — trees/rocks/signs/billboards/compass are push
  spots so [ActionPrompts.js](src/Portfolio/ActionPrompts.js) can rotate a
  joke pool. Real pushables: crate + bag. Lying-down props (`kind: 'log'`)
  excluded (standing anim mismatch). Don't "fix" without confirmation.
- **B (backflip) / C (cartwheel)** don't raycast for clearance — flag if you
  add similar global animations.
- **Furniture pass removed** (commit 12e494a) — don't re-add without asking.
  Grass cleared around interactable props so colliders match visuals (cd996b7).

## When in doubt

- [App.js](src/App.js) = wiring. [World.js](src/World/World.js) = load order.
- [Interaction.js](src/Portfolio/Interaction.js) + [ActionPrompts.js](src/Portfolio/ActionPrompts.js) = how the player triggers things.
- If an asset/animation isn't in `static/`, **ask** (rule 1).
