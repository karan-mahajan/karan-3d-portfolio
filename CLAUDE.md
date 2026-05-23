# karan-portfolio — Claude context

Bruno-Simon-style 3D walkable portfolio. Vanilla Three.js + Rapier3D + Vite. No
React, no framework. The player spawns at origin and walks toward cardinal
sections (Projects E, Skills S, Contact W, Experience N).

## Critical rules

### 1. Never invent assets — ask first
If a feature needs a 3D model, texture, sound, or animation that is **not
already** under `static/models/`, `static/textures/`, `static/sounds/`, or
`Extra/`:

1. **Stop.** Do not procedurally fake it, do not pick a "close enough" GLB from
   another folder, do not write code that loads a path that may not exist.
2. Tell the user exactly what asset is missing — name, format (GLB/FBX/GLTF),
   rough scale, and what it's for.
3. Ask: *"How would you like me to source this — Kenney pack, Sketchfab,
   Mixamo, or one you'll drop in?"*
4. Wait for the user to provide / point to the file before writing the loader
   code.

This applies to **animations** especially (Mixamo FBX clips), and to any new
object class (furniture piece, wildlife, prop). Procedural placeholders are
acceptable **only** as an explicit fallback inside a `try/catch` after a real
load attempt — and only when the user has agreed to that pattern.

### 2. Keep this file < 200 lines
When updating CLAUDE.md, prune before adding. Index-level facts only — no
tutorials, no code blocks longer than ~10 lines, no per-file walkthroughs.

### 3. Match the existing code style
Vanilla ES modules, `class` syntax, private fields with `#`. No TypeScript. No
comments that just restate what code does — only WHY a non-obvious choice was
made. JSDoc summaries on classes/methods are fine.

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

src/Utils/
  Sizes.js                  # resize event + pixel ratio cap
  Loader.js                 # GLTF + FBX + Texture promise wrappers, global progress
  Debug.js                  # dat.gui-style optional debug HUD

src/Physics/Physics.js      # Rapier init + world step + static ground + dynamic boxes

src/Player/
  Player.js                 # owns mesh + controller + physics body
  PlayerController.js       # WASD/space/shift input
  PlayerCamera.js           # camera-controls wrapper, smoothed follow
  Character.js              # Mixamo FBX load + animation mixer (idle/walk/run/jump)

src/World/
  Terrain.js                # green ground plane
  Sky.js                    # gradient sky sphere (warm sunset)
  Nature.js                 # Kenney trees / rocks / grass / mushrooms / logs, with exclusions
  Birds.js                  # ambient flock; GLB if available, procedural fallback
  World.js                  # composes terrain + sky + nature + billboards + signs + furniture + birds

src/Portfolio/
  Billboards.js             # Projects section (east) — interactive boards
  Signs.js                  # Experience trail (north), Skills (south), Contact (west)
  Furniture.js              # decorative props around sections (Kenney furniture pack)
  Interaction.js            # raycast + E-prompt + GSAP modal open/close
  PortfolioData.js          # project list
  ExperienceData.js         # work history
  SkillsData.js             # skill tags
  ContactData.js            # links

src/Effects/
  Fireflies.js              # particle dots around spawn at dusk
  Water.js                  # pond NW of spawn at (-12, 0.05, 18), radius 5.5, with lily pads
  Rain.js                   # toggleable rain particles
  PostFX.js                 # EffectComposer (bloom, optional vignette)

src/Audio/AudioManager.js   # ambient loop + footsteps + ui chimes (howler)

static/models/
  character/                # Mixamo FBX (idle, walk, run, jump, …)
  nature/                   # Kenney nature kit GLBs
  furniture/                # Kenney furniture kit GLBs
  wildlife/                 # birds, frog, etc.
  extras/                   # ad-hoc props
  maps/                     # any baked map textures
  props/                    # misc

Extra/                      # GLBs not yet wired into a class (Dock Long, Frog, Wooden Wall)
```

## World layout

- Spawn at (0, 0, 0). Player faces north (+Z).
- **Projects** — east, centered near `PROJECTS_CENTER` (Billboards.js)
- **Experience** — north, chain of signs along `SECTION_POSITIONS.experiencePath`
- **Skills** — south, around `SECTION_POSITIONS.skills`
- **Contact** — west, around `SECTION_POSITIONS.contact`
- **Pond** — NW at (-12, 0.05, 18), radius 5.5
- Section centers are ~35u from spawn. `Nature.addExclusion(x, z, r)` keeps
  trees out of clearings; always exclude new sections so trees don't clip props.

## Tick loop (App.js)

```
physics.step → player.update → playerCamera.update → world.update
→ interaction.tick → fireflies → water → rain → audio.tick → postfx.render
```

Sun + shadow camera follow the player so shadows stay sharp.

## Conventions

- Boot is async; `App.boot()` returns `{ character, world }`. Loader emits
  `progress` events; main.js drives the loading-bar fill.
- A `session-storage` flag (`karan-portfolio:journey-started`) skips the
  welcome overlay on subsequent reloads in the same tab.
- Controller is **paused** while overlays (loading, welcome, interaction modal)
  are up, then unpaused.
- Audio must start on a user gesture (browser policy) — handled in main.js.
- Physics: static ground covers the terrain plane. Dynamic bodies use Rapier's
  kinematic-position controller for the player.
- Fog tinted `#ffb084`, range 65→165, so distant trees fade into sunset.

## Deferred / parked work

- **Minimap + click-to-teleport** — auto-memory `project_minimap_teleport.md`.
  Bottom/top-right icon → fullscreen overlay → click marker → GSAP fade +
  Rapier body teleport. Do after the polish pass (water, fireflies, bloom,
  audio, start screen — most already in).

## When in doubt

- Reading [App.js](src/App.js) tells you the wiring.
- Reading [World.js](src/World/World.js) tells you what loads in what order.
- Reading [Interaction.js](src/Portfolio/Interaction.js) tells you how the
  player triggers UI modals.
- If an asset/animation/object isn't in `static/` or `Extra/`, **ask** (rule 1).
