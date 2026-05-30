# v3 Runtime — session prompts (a living chain)

Copy-paste prompts to kick off each fresh session of the v3 runtime build. Run
each phase in its **own session**, **one after another**, to keep context lean
(use subagents inside a session for parallel-independent work). Every session
auto-loads the memory `project_v3_runtime_phase_a`; the full plan is
[PHASE-A-audit-and-plan.md](./PHASE-A-audit-and-plan.md).

## How to run these (chained — each prompt learns from the previous)
The prompts are **not static**. They form a chain where each session feeds the
next, so later sessions never re-investigate or guess what an earlier one already
proved.

**Every session MUST, before it finishes:**
1. **Append to the [Learnings log](#learnings-log) below** every verified fact,
   gotcha, API quirk, or decision it discovered (with the real file/line/value) —
   anything a later phase would otherwise have to rediscover.
2. **Edit the NEXT phase's prompt** in this doc to fold in those learnings
   (correct any stale assumption, add the new constraint, point at the new file).
3. **Update the [Progress / commits](#progress--commits)** line with the new commit.

**Every session MUST, when it starts:** read the Learnings log first, then its
prompt. Treat the log as authoritative over the prompt if they ever disagree.

This is a standing rule, in addition to the per-prompt rules below.

## Standing rules (apply to every prompt below)
- **Source of truth = the Blender world** (`tools/blender/world-v3-karan.blend`)
  exported to `static/world/` (split GLBs + `manifest.json`). Rebuild Bruno-style
  (folio-2025), not by bending old v2 JS.
- **Don't deviate from Bruno's approach unless 99% sure it's better** — and base
  that on actual files, never guessing.
- **Verify from actual files / datablocks**, never quote numbers or APIs from
  memory. Renderer is **WebGPU + TSL** (locked).
- **rapier is 0.19.3** (not 0.12) — verify its API before using collider calls.
- **Do NOT touch** `tools/blender/` or `static/world/` (the split export is done +
  committed). World scope = projects / skills / contact (experience is dropped).
- **Use subagents** (their own contexts) for parallel-independent shader/material
  ports to save context; keep orchestration + verification in the main thread.
- **One commit per verified milestone, after I approve.** **No `Co-Authored-By`
  trailer.**
- Headless verify lives under `.verify/scripts/` + `.verify/shots/<YYYY-MM-DD>/`
  via `_boot.mjs` (see CLAUDE.md).

## Progress / commits
- `26d3489` — Bruno-style split GLB export + `manifest.json` (Phase A + B-export). ✅
- `049998f` — B0 WebGPU/TSL render core (build-green, app not yet rendering). ✅
- Next → the prompts below, in order.

## Learnings log
Authoritative, verified facts each session appends (newest at the bottom of each
group). **Read this before your prompt.** If a prompt contradicts a learning,
the learning wins — but re-verify from the actual file before relying on it.

### Renderer / build (from B0)
- three@0.184: `three/webgpu` is a **superset** build — import core THREE from it,
  not `'three'` (mixing breaks `instanceof`). It exports `WebGPURenderer`,
  `PostProcessing`, `MeshLambertNodeMaterial`, `MeshStandardNodeMaterial`.
- `three/webgpu` does **NOT** export `UniformsUtils` / `UniformsLib` — only
  `Leaves.js` used them (build warning today). Any lights/fog-uniform merge must
  be re-done in TSL.
- TSL (`three/tsl`): `pass`, `output`, `uniform`, `texture`, `Fn`, `vec3`,
  `positionWorld`, … `bloom` is in `three/addons/tsl/display/BloomNode.js` (NOT
  `three/tsl`).
- `WebGPURenderer` constructs synchronously; `await renderer.init()` before first
  render. Render loop must be `renderer.setAnimationLoop(cb)` + `renderAsync()`
  (WebGPU renders async); old `requestAnimationFrame` removed.
- PostFX: WebGPU `PostProcessing` graph owns tonemap/colorspace via the `output`
  node — `postProcessing.outputColorTransform` was disabled to avoid double
  tonemapping. Tilt-shift still TODO(B0) in PostFX.js.
- Loaders (`three/examples/jsm/loaders/*`) are renderer-agnostic — keep as-is.
- **rapier is 0.19.3** in node_modules (build is clean against it); its collider
  API differs from the 0.12 the v2 code was written for — verify before use.

### World data / export (from A + B-export — verify against the GLBs, don't guess)
- `static/world/manifest.json` drives loading: `monolithic[]`, `instanced[]`
  (visual+references), `foliage[]`, `colliders`, `references`, `grassMask`,
  `grassGrid{bounds:96}`.
- Terrain: `terrain/terrain.glb` node has **scale 0.65** → world half-extent
  **±62.4** (mesh local ±96); POSITION Y −1.5..0 (heightfield baked). Account for
  the node scale when sampling heights.
- Reference empties carry baked **Y-up world TRS** + extras (`template`, `species`,
  section contract, `role`). Colliders: `tube_`=cylinder, `cuboid_`=box,
  `*Footprint_`=walkable pad.
- Instance systems = **rocks/bricks/flowers only** (shared datablock).
  benches/lanterns/poleLights are monolithic (unique per-object datablocks).

### Process
- WebGPU/TSL is locked (Bruno's stack) — chosen because WebGL was "less work," not
  "better." Don't reopen it without 99%-from-files evidence.

### B0-finish / Phase B loader (this session — all verified against running app)
- **Boot-blocker #1 (fixed):** `KTX2Loader.detectSupport(renderer)` calls
  `renderer.hasFeature()`, which THROWS on `WebGPURenderer` until `await
  renderer.init()` completes. `Loader.attachRenderer()` MUST be called in
  `boot()` after `init()`, NOT in the App constructor. (Was in `#initRenderer`.)
- **Boot-blocker #2 (fixed):** `Leaves.js` called `THREE.UniformsUtils.merge([
  UniformsLib.lights, UniformsLib.fog, …])` at construction; both are `undefined`
  on `three/webgpu` → `"reading 'merge'"` TypeError killed the whole App ctor.
  Guarded with a fallback (`{}`) until Leaves is ported to TSL.
- **Boot-blocker #3 (fixed):** PostFX used `output(...)` as a function and
  `outputColorTransform = false`. In r184 TSL, `output` is a **node object, not a
  function**. Correct pattern (per `addons/tsl/display/BloomNode.js`):
  `postProcessing.outputNode = scenePassColor.add(bloomPass)` with
  `outputColorTransform` left at its **default `true`** (it applies ACES + sRGB).
- `PostProcessing` is renamed `RenderPipeline` (deprecation warning, still works).
  `renderAsync()` is deprecated → use `render()` (init() already ran). PostFX now
  calls `postProcessing.render()`.
- **Rapier 0.19.3 file rename gotcha:** 0.19 ships `rapier.mjs` (+`rapier.cjs`);
  0.12 shipped `rapier.es.js`. A stale vite dep-optimize cache / browser `?v=`
  graph after the upgrade 404s on `rapier.es.js` → "Failed to fetch dynamically
  imported module" boot crash. Fix = `rm -rf node_modules/.vite` + restart dev
  server + hard-reload. rapier IS in `optimizeDeps.exclude` (vite.config) — that
  is correct, keep it. The 0.19 collider API (heightfield/cuboid/cylinder/
  capsule/ball) MATCHES the v2 calls; `Physics.js` works unchanged. NOTE:
  `Physics.clearanceFor`'s `world.castShape(...)` arg order is STALE for 0.19
  (0.19 inserts `targetDistance` before `maxToi`) — not first-frame-critical
  (backflip/cartwheel clearance only); fix in Phase G.
- **Terrain GLB:** node `terrain` scale 0.651, local ±96 → world **±62.5**
  (`size`=125, 129×129 verts = 128 segments). Heightfield baked in WORLD space
  (apply matrixWorld). Its material's `baseColorTexture` is a **red/black mask
  named `terrainFurnitures`** (512² 16-bit), NOT a colour — renders the ground
  red. `GlbV3World.#neutralizeTerrainMask()` strips it to a flat placeholder
  (`#6f7d52`) until Phase D installs the real grass/terrain shader. The dark
  pond/river basins are just lower terrain; water surfaces are Phase F.
- **Colliders.glb counts (verified at load):** 67 `tube_`→cylinder, 6
  `cuboid_`→box, 10 `*Footprint_`→flat pad (built as thin cuboids). Proxy meshes
  are parsed for bbox then discarded (never added to scene). `references.glb` =
  30 empties (sectionRef_*, controlsRef, lavaRef_pool, titleRef, playstationRef,
  refBonfire_*, refPoleLight_*, animal/airDancer pivots) — kept live under root.
- **WebGPU render IS happening headless on macOS** with Chromium flags
  `--enable-unsafe-webgpu --enable-features=Vulkan,WebGPU` (`renderer.backend
  .isWebGPUBackend === true`, 150 draw calls / 159k tris). BUT **Playwright
  `page.screenshot()` cannot capture the WebGPU swapchain** — the canvas reads
  blank even though it renders. To get a VISUAL screenshot, launch Chromium
  WITHOUT the WebGPU flags → `WebGPURenderer` falls back to the **WebGL2 backend**
  (`isWebGLBackend`), which Playwright captures fine; same TSL/scene. Probe:
  `.verify/scripts/verify-v3-first-frame.mjs` (asserts state + draw calls);
  `/tmp/diag_webgl.mjs` pattern for the visual shot. Playwright ESM can't use
  NODE_PATH — symlink `node_modules/playwright{,-core}` → `/tmp/node_modules/…`.
- **B0 effect-disable mechanism (App.js):** unported GLSL effects crash WebGPU at
  first render. They're hidden, not deleted: `this._tslReady = {fireflies, rain,
  windLines, leaves}` flags → hide each effect's render mesh (`rain.drops` is the
  GLSL streaks; splashes are MeshBasic & safe) + skip its tick update. Water +
  Foliage are simply not built by `World` in v3 yet. Night-only GLSL FX (stars +
  spotlight shaft live in `TimeOfDay`, always-visible meshes with opacity-0
  uniforms that still COMPILE) are avoided by `this._b0ForceDay = true` (forces
  day so TimeOfDay keeps `.visible=false`). The day/night shader prewarm is
  SKIPPED under `_b0ForceDay` — `compileAsync(scene)` compiles every material
  incl. hidden GLSL, and the prewarm snaps to night. **To finish B0:** port each
  effect to TSL, flip its `_tslReady` flag (re-show mesh), port TimeOfDay
  stars+spotShaft, then delete `_b0ForceDay` + restore prewarm.
- **Facade stubs:** `GlbV3World` exposes `terrain/nature/paths/billboards/signs/
  refs` matching the old GlbWorld surface so App.js + ActionPrompts + StreetLights
  + Teleport boot unchanged. `billboards.items=[]`, `signs.{skills,contact}
  Position` filled from `sectionRef_*`. `World.js` dropped PortfolioMounts/
  ProjectShowcase/Foliage/SectionPositions (Phase C/E rebuild them).

---

## NEXT — B0 finish → first WebGPU frame (Phase B loader + core materials)

```
Continue the v3 runtime: B0 → first WebGPU frame, then finish the GLSL→TSL ports.

FIRST read docs/v3-runtime/SESSION-PROMPTS.md → "Learnings log" (authoritative
verified facts). BEFORE finishing this session: append every new verified fact/
gotcha to that log, update the NEXT phase prompt with them, and bump the
Progress/commits line.

Context is in memory (project_v3_runtime_phase_a, auto-loaded) and
docs/v3-runtime/PHASE-A-audit-and-plan.md. Last commit: 049998f (B0 render
core: three→three/webgpu, WebGPURenderer + setAnimationLoop, PostFX→WebGPU
PostProcessing; `npm run build` passes but the app does NOT render a frame yet
because raw-GLSL ShaderMaterials error on WebGPU and the v3 world is unloaded).

Goal this session — get the FIRST verifiable WebGPU frame, then port effects:
1. Phase B loader: new GlbV3World that reads static/world/manifest.json — load
   the monolithic GLBs into the scene, bake the terrain heightfield (terrain
   node has scale 0.65 → world ±62.4) into Physics ground + terrain.heightAt,
   build Rapier colliders from colliders.glb (tube_=cylinder, cuboid_=box,
   *Footprint_=walkable pad; bbox→size) then hide them, collect references.glb
   empties into a typed map. Rewire App.js/World.js off the obsolete v2
   GlbWorld/SectionPositions. (rapier is 0.19.3 now — verify its collider API
   vs the old 0.12 calls before using; don't guess.)
2. Port the always-on materials to TSL so a frame renders: SmoothLitPaletteMaterial
   (master, FIRST) + Sky. Temporarily DISABLE the peripheral effects (Fireflies,
   Rain, WindLines, Leaves, Water, Foliage, Grass, Footprints) behind a guard so
   they don't crash the WebGPU render.
3. Verify: app boots to a first WebGPU frame — headless Chromium with a WebGPU
   flag (or assert the WebGL fallback backend), screenshot under
   .verify/shots/<YYYY-MM-DD>/ via .verify/scripts/ + _boot.mjs (see CLAUDE.md).
4. Then re-enable + port the disabled effects to TSL one by one (Leaves also
   needs a UniformsLib/UniformsUtils replacement — three/webgpu doesn't export
   them) + the PostFX tilt-shift (TODO(B0) in PostFX.js), verifying each.

Rules: use subagents (their own contexts) for the parallel-independent shader
ports to save context; VERIFY from actual files/datablocks, never guess; don't
deviate from Bruno's approach unless 99% sure it's better; do NOT touch
tools/blender/ or static/world/ (the split export is done + committed); one
commit per verified milestone after I approve; NO Co-Authored-By trailer.
```

---

## Phase C — Sections & interactions

```
v3 runtime Phase C: sections & interactions. Prereq: the world loads + renders on
WebGPU (B0/B done). Read memory project_v3_runtime_phase_a + docs/v3-runtime/,
and FIRST the SESSION-PROMPTS.md "Learnings log". Before finishing: append new
learnings there + update the next prompt + bump Progress/commits.

Rebuild SectionPositions + the interaction layer from the section contract baked
into references.glb extras (verify by reading the GLB, don't guess):
- sectionRef_projects {interaction:'projectsHut', enterCameraPath:
  'doorToInteriorBoard', doorLocalOffset[2], interiorBoardLocalOffset[3]}
- sectionRef_skills {interaction:'skillSphere', sphereRadius:6, sphereCenterHeight:7,
  waterMounted:true, floatClearance:1.55, enterCameraOffset[3]}
- sectionRef_contact {interaction:'contactModal', prompt:'press E'}
Wire the projectsHut / skillsSphere / contactBoard meshes (from areas/areas.glb)
as the interactable markers. Drop experience (inert). Retire the v2
Billboards/ProjectShowcase/Signs/PortfolioMounts interaction code.

Verify each interaction headless. One commit after I approve. No Claude trailer.
```

---

## Phase D — Grass + wind (Bruno grass → WebGL-free TSL)

```
v3 runtime Phase D: grass + wind. Read memory + docs/v3-runtime/ (FIRST the
SESSION-PROMPTS.md "Learnings log"; before finishing, append learnings + update
the next prompt + bump Progress/commits). Renderer is WebGPU/TSL, so port Bruno's folio-2025 Grass.js (sources at
~/Documents/Projects/folio-2025/sources/Game/World/Grass.js) DIRECTLY as TSL
(no GLSL backport needed now): 280×280 = 78,400-blade camera-following grid,
wrapped by modulo, density+colour from the terrain grass mask
(static/world/terrainGrass.exr green channel), driven by the shared Wind uniform.
Grid bounds from manifest.grassGrid (±96). Verify the mask channels first.

Verify headless (grass visible, follows camera). One commit after approval. No
Claude trailer.
```

---

## Phase E — Vegetation, foliage, props instancing

```
v3 runtime Phase E: instancing off the split GLBs (read manifest.json; verify
node counts/extras from the actual GLBs, don't guess). FIRST read the
SESSION-PROMPTS.md "Learnings log"; before finishing, append learnings + update
the next prompt + bump Progress/commits.
- Trees: monolithic trunks already load (vegetation/*.glb). Grow leaf clouds via
  Bruno-style Foliage at treeLeaves/treeLeavesReferences.glb anchors (extras.species
  birch/cherry) — port Bruno Foliage.js to TSL.
- Instanced (Visual + References pairs): rocks (rocksVisual: rockStyle_boulderCluster/
  volcanicShards), bricks (3 templates), flowers (8 zone templates). For each
  reference empty, read extras.template + baked world matrix → one InstancedMesh
  per (system, template).
- Foliage refs-only: bushes/bushesReferences.glb → SDF foliage.

Verify headless (rocks/bricks/flowers/leaves visible at correct transforms). One
commit after approval. No Claude trailer.
```

---

## Phase F — Lights, FX, animated props

```
v3 runtime Phase F: lights + fx + animated props. Read memory + docs (FIRST the
SESSION-PROMPTS.md "Learnings log"; before finishing, append learnings + update
the next prompt + bump Progress/commits). From
references.glb (verify extras): place point lights at refPoleLight_* / refBonfire_*;
animate animalPivot_{cat,dog,deer,rabbit} + airDancerPivot_* by name (extras carry
species/wanderRadius/sway/segments); lava from lavaRef_pool extras (surfaceObject/
coreObject/radius/flowDir/glowStrength/pulseSpeed/emberRate); water surfaces. Wire
day/night via the existing TimeOfDay. All as TSL.

Verify headless. One commit after approval. No Claude trailer.
```

---

## Phase G — Calibration & cleanup

```
v3 runtime Phase G: calibration + cleanup. FIRST read the SESSION-PROMPTS.md
"Learnings log"; before finishing, append final learnings + bump Progress/commits.
Recalibrate wade/clamp/respawn radii for the ±60 walkable world (current 45/120/-5 predate it). Point minimap/compass
at the organic section positions. Delete retired v2 systems (old GlbWorld,
SectionPositions, Nature/Paths/Grass-asset-pack, Billboards/ProjectShowcase/Signs
if fully replaced). Optional: gltf-transform Draco/KTX2 compression pass on
static/world/. Update CLAUDE.md (radius, renderer=WebGPU, rapier 0.19, world
scope). Verify headless. One commit after approval. No Claude trailer.
```
