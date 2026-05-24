# karan-portfolio — Claude context

Bruno-Simon-style 3D walkable portfolio. Vanilla Three.js + Rapier3D + Vite. No
React, no framework. The player spawns at origin and walks toward cardinal
sections (Projects E, Skills S, Contact W, Experience N) on a small island
surrounded by ocean.

## Critical rules

### 1. Never invent assets — ask first
If a feature needs a 3D model, texture, sound, or animation that is **not
already** under `static/models/`, `static/textures/`, or `static/sounds/`:

1. **Stop.** Do not procedurally fake it, do not pick a "close enough" GLB from
   another folder, do not write code that loads a path that may not exist.
2. Tell the user exactly what asset is missing — name, format (GLB/FBX/GLTF),
   rough scale, and what it's for.
3. Ask: *"How would you like me to source this — Kenney pack, Sketchfab,
   Mixamo, or one you'll drop in?"*
4. Wait for the user to provide / point to the file before writing the loader
   code.

This applies to **animations** especially (Mixamo FBX clips). Procedural
placeholders are acceptable **only** as an explicit fallback inside a
`try/catch` after a real load attempt — and only when the user has agreed.

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
**Always** sample `terrain.heightAt(x, z)` for the group/mesh Y *and* every
physics collider Y. Reference patterns: [Billboards.js](src/Portfolio/Billboards.js),
[Furniture.js](src/Portfolio/Furniture.js), [Signs.js](src/Portfolio/Signs.js),
[Lamps.js](src/World/Lamps.js).

### 5. New solid props need a Rapier collider — sized to the **visible** mesh
If the player should not walk through it OR should stand on top of it, register
one in [Physics.js](src/Physics/Physics.js): `addStaticCylinder` /
`addStaticCuboid` for static, `addDynamicBall` for things that should react to
being pushed/kicked. Walk-through accents (grass, flowers, mushrooms, pebbles,
ferns, reeds, lily pads) get **no** collider.

**Collider must match the visible mesh** — don't hardcode a footprint and hope.
`new THREE.Box3().setFromObject(node)` on the scaled mesh gives you the real
extents; pass `box.min.y` as the y arg and `size.{x,y,z}/2` as the half-extents.
Reference patterns: [Nature.#placeInstances](src/World/Nature.js) (bbox sizing
for rocks/logs), [Paths.#buildTile](src/World/Paths.js) (tile colliders so the
player walks on top, not through), [Furniture.#placeOne](src/Portfolio/Furniture.js),
[Interactables.#buildStuckCrate](src/Portfolio/Interactables.js). Symptoms when
this is wrong: player's feet sink into the visible mesh, or player stands
*inside* the painted geometry. Both are user-reported bugs already this sprint.

**Important:** `addStaticCuboid(x, y, z, hx, hy, hz)` treats `y` as the
cuboid's **bottom** and lifts by `hy` internally — pass `bottom_world_y`, not
the centre. Passing centre lands the collider `hy` above the visible mesh.

## Stack

- **three@0.184** — renderer, scene, lights, materials
- **@dimforge/rapier3d@0.19** — physics (async WASM init; see [Physics.js](src/Physics/Physics.js))
- **camera-controls@3** — third-person follow cam
- **gsap@3** — UI fades + interaction transitions
- **howler@2** — audio (ambient + footsteps + ui sfx)
- **vite@8** — dev server, `publicDir: 'static'`, GLB/FBX/HDR included as assets

```
npm run dev      # vite, serves on http://localhost:5173
npm run build    # production build → dist/
npm run preview  # preview built bundle
```

## File map

```
index.html                  # loading screen, welcome overlay, controls HUD
src/main.js                 # bootstrap: load → welcome → start journey
src/App.js                  # renderer, scene, lights, tick loop, wires all modules
src/style.css               # all CSS (overlay, HUD, sign tooltips)

src/Utils/                  # Sizes, Loader, Debug
src/Physics/Physics.js      # Rapier init + heightfield ground + static + dynamic helpers

src/Player/
  Player.js                 # owns mesh + controller + physics body + wading slowdown
  PlayerController.js       # WASD/space/shift input + speedMultiplier
  PlayerCamera.js           # camera-controls wrapper, smoothed follow
  Character.js              # Avaturn GLB + Mixamo FBX clips → AnimationMixer

src/World/                  # Terrain, Sky, Nature, Grass, Paths, Lamps, TimeOfDay, Sun, Wind, Palette, World
src/Portfolio/              # Billboards, Signs, Furniture, Interaction, Interactables, ActionPrompts, *Data
src/Effects/                # Fireflies, Water (ocean), Rain, Leaves, WindLines, PostFX
src/Audio/AudioManager.js   # ambient + footsteps + ui chimes + water splashes (howler)
static/models/              # character/ (Avaturn+Mixamo), nature/, furniture/, extras/, props/
```

## World layout

- Spawn at (0, 0.02, 0). Player faces north (+Z).
- Island radius ≈ 45m; shore slope 45→57m down to y=-2 ocean floor.
- **Projects** — east, centered near `PROJECTS_CENTER` (Billboards.js)
- **Experience** — north, signs along `SECTION_POSITIONS.experiencePath`
- **Skills** — south, around `SECTION_POSITIONS.skills`
- **Contact** — west, around `SECTION_POSITIONS.contact`
- Past r=45 the player wades (slowdown ramps to 15% speed); past r=120 a soft
  clamp teleports them back. Falls below y=-5 respawn at origin.
- `Nature.addExclusion(x, z, r)` keeps trees out of clearings; always exclude
  new sections so trees don't clip props.

## Tick loop (App.js)

```
physics.step → player.update → playerCamera.update → world.update
→ actionPrompts.tick → interaction.tick → interactables.update
→ fireflies → water → rain → audio.tick → postfx.render
```

Sun + shadow camera follow the player so shadows stay sharp.

## Conventions

- Boot is async; `App.boot()` returns `{ character, world }`. Loader emits
  `progress` events; main.js drives the loading-bar fill.
- A `session-storage` flag (`karan-portfolio:journey-started`) skips the
  welcome overlay on subsequent reloads in the same tab.
- Controller is **paused** while overlays (loading, welcome, interaction
  modal, action one-shots) are up, then unpaused.
- Audio must start on a user gesture (browser policy) — handled in main.js.
- Physics: heightfield ground sampled from `terrain.heightAt`. Player uses
  Rapier's kinematic-position character controller; football is the only
  dynamic body. Variable timestep — known wart, not yet fixed.
- Fog tinted `#ffb084`, range 65→165, so distant trees fade into sunset.

## Verification sandbox (everything goes in `.verify/`)

**All** verification artifacts — playwright scripts AND screenshots — live in
`.verify/` at the project root. Never `/tmp/`, never anywhere else. The user
opens screenshots locally to confirm a fix actually works.

Layout:

```
.verify/
  scripts/                 # all probe .mjs files
    verify-walk.mjs        # canonical boot + WASD + screenshot driver
  shots/
    YYYY-MM-DD/            # one folder per day, auto-created on run
      NN-step.png
```

- `.verify/` is gitignored (whole folder). Outputs never get committed AND
  the scripts never get committed either — they're scratch tooling that
  survives between sessions but stays local.
- Copy `scripts/verify-walk.mjs` as `scripts/verify-<feature>.mjs` for new
  probes (e.g. `verify-water.mjs`, `verify-football.mjs`). Every script must
  resolve its output dir as `../shots/<today>/` from its own `__dirname`
  (use `new Date().toISOString().slice(0, 10)`) and `mkdirSync` it.
- Run from project root: `URL=http://localhost:5173/ node .verify/scripts/verify-walk.mjs`
  (playwright must be installed somewhere reachable;
  `cd /tmp && npm install --no-save playwright` works since the project
  itself has no playwright dependency).
- Before adding a new probe, **read `ls .verify/scripts/`** to see what
  already exists — don't duplicate.

## Known parked work (don't surprise the user with rewrites)

- **Push interaction is intentionally a comedy gag** — trees/signs/lamps are
  all registered as push spots so [ActionPrompts.js](src/Portfolio/ActionPrompts.js)
  can rotate a joke pool. Do NOT "fix" this without confirmation.
- **B (backflip) / C (cartwheel)** don't currently raycast for clearance —
  flag if you add similar global animations.
- **Minimap + click-to-teleport** — see auto-memory `project_minimap_teleport.md`.

## When in doubt

- Reading [App.js](src/App.js) tells you the wiring.
- Reading [World.js](src/World/World.js) tells you what loads in what order.
- Reading [Interaction.js](src/Portfolio/Interaction.js) + [ActionPrompts.js](src/Portfolio/ActionPrompts.js) tell you how the player triggers things.
- If an asset/animation/object isn't in `static/`, **ask** (rule 1).
