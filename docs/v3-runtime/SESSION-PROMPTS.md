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
- `30d8090` — B-loader: **first WebGPU frame** (GlbV3World + TSL Sky; world loads +
  collides + renders, 9/9 headless checks). Effects still disabled (TSL port
  pending) + day forced. ✅
- `fe81906` — **B0 effects port complete**: Fireflies/Rain/WindLines/Leaves/
  stars/spotShaft + PostFX tilt-shift all GLSL→TSL; `_b0ForceDay`+`_tslReady`
  crutches deleted; prewarm restored. 16/16 WebGPU night checks + 9/9 first-frame
  + visual day/night non-blank. World fully styled day AND night. ✅
- Next → **Phase C** (sections & interactions).

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

### B0 effects port (this session — verified against the running WebGPU app)
- **All six FX ported GLSL→TSL + crutches deleted.** `_b0ForceDay` and
  `_tslReady` are GONE from App.js; the day/night prewarm is restored. Verified
  16/16 on the **WebGPU backend** (`verify-v3-effects-night.mjs`): no page
  errors on day boot OR night toggle, every FX mesh is a NodeMaterial, night
  brings up fireflies (uIntensity 2.2) + stars (opacity 1) + spotlight. First
  frame still 9/9 (`verify-v3-first-frame.mjs`); visual day+night non-blank on
  the WebGL2 fallback (`verify-v3-effects-visual.mjs`).
- **Port strategy = re-author the karan GLSL as TSL node graphs, NOT port
  Bruno's effects.** Bruno's RainLines/WindLines/Leaves are compute-shader
  systems hard-wired to his `Game` singleton / `MeshDefaultMaterial` /
  `game.noises.perlin` / `game.terrain.terrainNode` — not portable. The CPU
  simulation in each karan effect (offset/spin/settle/wrap arrays) is UNCHANGED;
  only `ShaderMaterial` → node material + the vertex/fragment GLSL → vertex/color/
  opacity nodes. Every public API (TimeOfDay `.uniforms.*.value`, toggles,
  achievements, `fireflies.points`) is preserved so nothing downstream changed.
- **WebGPU renders `THREE.Points` as 1px PointList** (verified
  `WebGPUUtils.getPrimitiveTopology`: `if (object.isPoints) return PointList`) —
  there is NO point-size path on that primitive. The GLSL `gl_PointSize` clouds
  (Fireflies, TimeOfDay stars) were re-built as **instanced billboarded quads**:
  one quad/instance, offset `positionGeometry.xy.mul(worldSize)` in VIEW space
  inside `material.vertexNode` (constant world size → free perspective atten),
  radial disc via `smoothstep(0.5,0,length(uv-0.5))`. `PointsNodeMaterial`+
  `sizeNode` DOES exist and would also work, but the billboard-quad route reuses
  the exact same instanced-attribute pattern as the ribbon/leaf effects.
- **WebGPU caps a render pipeline at 8 vertex buffers.** Leaves had
  position+uv + 7 instanced attrs = 9 → `"Vertex buffer count (9) exceeds the
  maximum (8)"` at `createRenderPipeline` (fires during BOTH live render and the
  prewarm `compileAsync`). Fix: **pack instanced attrs into vec4 buffers** —
  Leaves now uses 3×vec4 (`aOffsetScale`,`aSpinAngle`,`aTintSettled`) + 1 scalar
  (`aSettledYaw`) = 2 geometry + 4 instanced = 6 buffers, repacked from the sim
  arrays by `#packBuffers()` each frame. Budget every instanced node mesh: keep
  `2 + instancedBufferCount ≤ 8`. (Fireflies/WindLines/stars use ≤2 instanced
  buffers, fine.)
- **MeshLambertNodeMaterial** is the lights+fog+shadow replacement for the old
  `UniformsLib.lights/fog` merge (which `three/webgpu` doesn't export). Set
  `colorNode`/`opacityNode`/`normalNode`/`positionNode`; `alphaTest` works as a
  property. The old magenta grass-shadow-tint was dropped (no grass in v3 yet).
- **TSL building blocks confirmed in r184** (`three/tsl`): `attribute('name')`
  auto-reads an `InstancedBufferAttribute` per-instance (no `instancedArray`/
  compute needed for CPU-driven sims); `varying(float(0),'name')` carries
  vertex→fragment; `cond.greaterThan(0.5).select(a,b)` is the branch;
  `cameraViewMatrix`/`cameraProjectionMatrix`/`modelViewMatrix`/`cameraPosition`
  are accessor nodes; `texture(tex, uv())` 2-arg sampling; `screenUV` for
  full-screen UV. Mutable locals need `.toVar()` before `.addAssign`/`.assign`.
- **PostFX tilt-shift** is a screen-UV TSL `Fn([tex, amount])` on the scene-pass
  texture node: `strength = smoothstep(0.15,0.55,abs(screenUV.y-0.5)).mul(amount)`,
  an 8-tap ring at radius `strength*0.012` rotated by `hash(screenUV…)` so it
  reads as bokeh not banding; centerline radius→0 = crisp, no branch. Sample via
  `tex.sample(uvc)` / `tex.sample(uvc.add(off))`. It runs on the SHARP scene and
  `bloom` is added on top (`outputNode = tiltShift(scenePassColor,u).add(bloom)`)
  so highlights stay clean. `outputColorTransform` stays default `true`.
- **Cancelled-batch gotcha (process, not code):** one failed call in a parallel
  tool batch cancels the WHOLE batch — all sibling Edits/Writes silently revert
  to "failed" and DON'T apply. When touching many files, run the edits in their
  own message (or sequentially) so one bad `cp`/grep can't wipe the batch.

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
- **Grass mask (`static/world/terrainGrass.exr`) — decoded as FLOAT, 512², verified:**
  RGBA 32-bit, `colorInteropID="data"` (non-colour). **GREEN = grass density,
  range 0→0.64** (mean 0.178; 41% of pixels >0.1, 26% >0.5). **RED, BLUE = all
  zero. ALPHA = 1.** ⇒ (a) green max is **0.64 not 1.0**, so Bruno's
  `step(g-0.4,0.1)` hide + direct `g` height/width scaling must be **remapped**
  for karan (e.g. normalise by ~0.64, threshold ~0.12–0.15). (b) **NO water
  channel** — Bruno drives water + the sand/teal/blue terrain gradient off `.b`;
  karan's `.b` is empty, so **water/ocean CANNOT be mask-driven** here — it must
  come from the terrain pond/river basin geometry or a separate authored source.
  Decode trick: `three`'s `EXRLoader().setDataType(FloatType).parse(arrayBuffer)`
  runs headless in Node (no DOM); `magick`/`oiiotool` can't read this EXR.
  Grid: Plane.003 ±96 (192 wide) ⇒ mask UV = `(worldXZ + 96)/192` (== Bruno's
  `pos/128/1.5+0.5`); orientation vs world UNVERIFIED — confirm visually (memory
  reference_terrain_mask_screen_axes warns of an axis swap).
- **Bruno grass algorithm (folio-2025, three/webgpu TSL, verified):** 280×280
  blade grid (one triangle each), camera-following via modulo wrap
  (`loop = mod(pos-center+size/2, size)-size/2`), each blade billboarded to camera
  (`atan2(camZ-z, camX-x) - π/2`, rotate xz). Per blade: sample mask `.g`; height
  = `bladeHeight(0.6) * (0.6*rand+0.4) * (perlin(pos*0.0321)+0.5) * g`; width =
  `bladeWidth(0.1) * shape * g`; tip-only wind = `wind(pos.xz)*tipness*height*2`
  (two-octave Perlin, dir `π*0.6`); hidden blades pushed `y += step(g-0.4,0.1)*100`.
  Material = `MeshLambertNodeMaterial`, `normal=(0,1,0)`, `shadow=(1-tipness)*g`.
  Terrain colour (Bruno Terrain.js) = `mix(gradient(.b), grassColor #b8b62e, .g)`
  — for karan drop the `.b` gradient (empty); use `mix(dirtColor, grassColor, g)`.
- **Facade stubs:** `GlbV3World` exposes `terrain/nature/paths/billboards/signs/
  refs` matching the old GlbWorld surface so App.js + ActionPrompts + StreetLights
  + Teleport boot unchanged. `billboards.items=[]`, `signs.{skills,contact}
  Position` filled from `sectionRef_*`. `World.js` dropped PortfolioMounts/
  ProjectShowcase/Foliage/SectionPositions (Phase C/E rebuild them).

### Phase D grass (this session — verified WebGPU 9/9 + WebGL2 11/11, user-approved)
- **USE karan's curved blade ("myGrass"), NOT Bruno's flat triangle.** User
  corrected mid-build: "use myGrass, not the bruno's grass — not this triangle
  thing." The blade is authored in `tools/blender/.../02-ground-grass-blades.py`
  = a 9-vert curved arched blade (`Plane.012`): 4-segment stem, base 0.030 m →
  single tip, forward arch, per-vertex `blade_height` [0,1] → 6-stop OLIVE ramp
  (`#4F6429`→`#B8B868`) + ~10% brown dry-tip variant (`aDry < 0.10`), random yaw
  + ±20° lean (rooted at base), size 0.35–1.5×. So the Phase D prompt's "port
  Bruno's Grass.js directly" was WRONG — only Bruno's *runtime-window* technique
  is kept, the blade/look is karan's. See memory
  [[project_v3_grass_is_my_curved_blade]].
- **Mask channels (re-verified live in-app, matches the prior FLOAT decode):**
  `terrainGrass.exr` loaded via `Loader.loadEXR` (added; `EXRLoader`, HalfFloat,
  `colorSpace=NoColorSpace`, `flipY=false`, ClampToEdge+Linear). G = density,
  range 0→0.64, R/B = 0, A = 1. UV = `worldXZ/(2*96)+0.5` (Bruno mapping); the
  **orientation is CORRECT as-is** — grass visibly avoids the carved basins/paths
  and rings the island, no V-flip needed. Density remap used: `clamp(g*1.8,0,1)`
  for height/width fade; hide at `step(g,0.06)*+100`.
- **Real-blade runtime = instanced geometry, NOT billboarded.** One curved-blade
  `InstancedBufferGeometry` (9 verts + `blade_height` attr + 7-tri index) with
  per-instance attrs `aOffset(vec2) aYaw aTilt(vec2) aSize aDry`. Bruno's
  camera-window kept: a fixed N×N instance grid, modulo-wrapped to the player in
  `positionNode` each frame (`center` uniform = player XZ). Rotations built inline
  in TSL (`sin`/`cos` rotX/rotZ/rotY); colour ramp = piecewise `mix` over stops.
- **Blade grounding needs a height texture.** karan's terrain is NOT flat (ponds/
  river/beach, Y −1.5..0), so blades can't sit at y=0 like Bruno's. Built a
  half-float `RedFormat` `DataTexture` (`DataUtils.toHalfFloat`) off
  `terrain.heights` (transpose `[u*verts+w]`→`[w*verts+u]`; U=X, V=Z over the
  terrain bbox); sample blade base Y in the vertex node. **r16float is filterable
  on WebGPU; r32float is NOT** — use HalfFloat for any in-shader-sampled height/
  data texture, or it falls back to nearest (stepped) / errors.
- **Terrain ground material (replaces `#neutralizeTerrainMask`).** The terrain
  GLB's baseColorTexture is the red `terrainFurnitures` mask — replaced the whole
  material with a `MeshLambertNodeMaterial` whose `colorNode = mix(dirt #8f7d54,
  grassGreen #5f7a39, clamp(maskG*1.8))` sampled by `positionWorld.xz`. Lambert
  keeps sun/shadow/fog so the ground dims at night through the light rig. A
  `globalThis.__grassMaskDebug` flag (set via Playwright `addInitScript` BEFORE
  load, since the `if` runs at graph-build time) makes terrain output raw G — the
  fastest way to ground-truth mask sampling/orientation.
- **Wind TSL bridge:** added `Wind.offsetNode(worldXZ)` + `Wind.nodes` (TSL
  `uniform`s synced from `uniforms` in `update()`), mirroring the GLSL
  `windOffset` two-octave sample so TSL grass sways with the same one wind. GLSL
  path left intact (unused now).
- **Density is the camera-window tradeoff.** Blender bakes the FULL ~3.15M-blade
  field (~425/m², 12.8M tris, deliberately NOT exported). Runtime can't — it's a
  windowed grid: default `subdivisions=820` over `radius=38` ⇒ **672,400 blades
  (~116/m², ~4.7M tris)**, scaled by `√grassMultiplier` per tier. User compared
  counts vs Blender; 820 reads "much better". Local blade LOOK matches Blender;
  total count differs by design.
- **OLIVE palette breaks naive green-detection.** Pixels are olive/yellow-green
  (G≈R, e.g. `#B8B868`), so a verify metric of `g>r` finds nothing. Use
  `g >= r-12 && g > b+22 && g>55` (dirt tan has r>g, excluded). Cost me one false
  FAIL before I looked at the actual screenshot.
- **Process: `npm install --no-save <pkg>` in `/tmp` PRUNES `/tmp/node_modules`**
  (no package.json there) → wiped playwright. Install ALL needed pkgs in ONE
  command (`npm install --no-save playwright pngjs`). `pngjs` (for PNG pixel
  decode in verify) needs a `node_modules/pngjs` symlink like playwright — ESM
  ignores NODE_PATH.

---

## DONE — B0 effects port (GLSL→TSL ports + un-force day) ✅
Completed: all six FX ported, crutches deleted, prewarm restored, verified on
WebGPU (16/16 night) + first-frame (9/9) + visual day/night. See the
"B0 effects port" learnings group above. **Next session = Phase C below.**

<details><summary>original B0 effects-port prompt (for reference)</summary>

```
Continue the v3 runtime: finish B0 — port the disabled GLSL effects to TSL so
the world renders fully (incl. at night), then remove the day-mode crutch.

FIRST read docs/v3-runtime/SESSION-PROMPTS.md → "Learnings log" (authoritative
verified facts; the B0-finish/Phase-B group is the freshest). BEFORE finishing:
append new learnings, update this prompt + the Phase D prompt, bump Progress/commits.

Context: memory project_v3_runtime_phase_a (auto-loaded) + docs/v3-runtime/.
Last commit 30d8090 — the v3 world LOADS + COLLIDES + RENDERS a first WebGPU
frame (GlbV3World off manifest.json; Sky ported to TSL; build green; 9/9 headless
checks via .verify/scripts/verify-v3-first-frame.mjs). But to get that frame the
unported raw-GLSL effects are HIDDEN and the app is FORCED to day mode — see the
B0-finish learnings for the exact guards. Your job is to remove those crutches by
porting each effect to TSL.

Disabled today (each crashes the WebGPU backend as raw GLSL ShaderMaterial):
- App.js `this._tslReady = {fireflies, rain, windLines, leaves}` — meshes hidden,
  tick updates skipped. Port each → flip its flag true → re-show its mesh.
  (rain: only `rain.drops` (GLSL streaks) is hidden; splashes are MeshBasic.)
- TimeOfDay.js `starMaterial` (#buildStars) + `spotShaftMat` (#buildSpotlight) —
  always-visible meshes with opacity-0 uniforms; they still COMPILE → crash.
  Port both to TSL node materials.
- App.js `this._b0ForceDay = true` forces day so the night-only GLSL above stays
  hidden, AND gates the day/night shader prewarm (`#prewarmDayNightShaders` calls
  compileAsync on the whole scene incl. hidden GLSL + snaps to night). After the
  above are TSL, DELETE `_b0ForceDay` and restore the prewarm; verify night mode.
- Not built at all in v3 yet (leave for Phase D/E/F, don't force here): Grass,
  Foliage, Water — World.js no longer constructs them.
- PostFX tilt-shift is still TODO(B0) in PostFX.js (bloom-only today). Port the
  old GLSL TiltShiftShader to a screen-UV TSL Fn (jittered taps, strength =
  smoothstep(0.15,0.55,abs(uv.y-0.5)), centerline crisp) on the scenePassColor.

How: port Bruno's folio-2025 equivalents to TSL where they exist
(~/Documents/Projects/folio-2025/sources/Game/), else re-author the existing
GLSL as TSL node graphs. three/webgpu does NOT export UniformsUtils/UniformsLib —
Leaves' lights+fog merge must be redone as a node material (it's stubbed today).
Use subagents (own contexts) for the parallel-independent shader ports.

Verify EACH effect headless as you flip it on: WebGPU backend asserts state/
drawcalls (verify-v3-first-frame.mjs pattern); for a VISUAL screenshot launch
Chromium WITHOUT the WebGPU flags so WebGPURenderer falls back to WebGL2 (the
only backend Playwright can screenshot — see learnings). Re-verify night mode
once `_b0ForceDay` is gone. Then drop the disabled-effects table claims from any
docs that say the world is "unstyled".

Rules: VERIFY from actual files, never guess; don't deviate from Bruno unless 99%
sure; do NOT touch tools/blender/ or static/world/; one commit per verified
milestone after I approve; NO Co-Authored-By trailer.
```

</details>

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

## Phase D — Grass + terrain colour (Bruno grass → TSL)  ← DO THIS NEXT (user priority)

```
v3 runtime Phase D: grass + terrain colour. Make the world look real — replace the
flat placeholder ground (GlbV3World.#neutralizeTerrainMask) with a mask-driven
grass field + terrain colour. Renderer is WebGPU/TSL.

FIRST read docs/v3-runtime/SESSION-PROMPTS.md "Learnings log" — the grass-mask +
Bruno-grass-algorithm entries are ALREADY VERIFIED there (mask decoded, Bruno algo
extracted); don't re-investigate. Before finishing: append learnings + update this
prompt + Progress/commits. Context: memory project_v3_runtime_phase_a + docs.
Last commit chain ends at the first-frame loader (30d8090). World data is in
static/world/ — do NOT edit it or tools/blender/.

VERIFIED FACTS (from the Learnings log — trust these):
- Mask static/world/terrainGrass.exr, RGBA float 512². GREEN = grass density,
  range 0→0.64 (mean 0.178). RED/BLUE empty, ALPHA=1. So: NORMALISE/REMAP green
  (it never reaches 1.0) — don't copy Bruno's raw step(g-0.4,0.1)/direct-g scaling
  or you'll stunt/hide most blades. Suggested: gN = clamp(g/0.6,0,1); show where
  g>~0.12; height/width ∝ smoothstep(0.12, 0.5, g).
- NO water/blue channel — terrain colour can't use Bruno's .b sand/teal/blue
  gradient. Use mix(dirtColor, grassColor #b8b62e, gN). Water/ocean is a SEPARATE
  later step (basin geometry, not this mask).
- Grid: Plane.003 ±96 (192 wide). Mask UV = (worldXZ+96)/192. Load EXR with
  EXRLoader (three/examples/jsm/loaders/EXRLoader.js; add an EXR path to
  Utils/Loader.js — it only has PNG today; set NearestFilter, flipY=false,
  colorSpace=NoColorSpace, type per decode). ORIENTATION vs world is UNVERIFIED —
  sample, screenshot, and flip/swap UV axes if grass lands wrong (memory
  reference_terrain_mask_screen_axes warns of an axis swap).
- Bruno algorithm is in the Learnings log (280×280 billboard blades, modulo-wrap
  camera grid, tip-weighted two-octave Perlin wind, MeshLambertNodeMaterial).
  Source to mirror: ~/Documents/Projects/folio-2025/sources/Game/World/Grass.js +
  Terrain.js + Wind.js (three/webgpu TSL — near drop-in).

BUILD:
1. New src/World/Grass.js (TSL, three/webgpu). Port Bruno's grass with the karan
   remap above. Feed it the shared src/World/Wind.js uniform (already constructed
   in App). Add to scene; update center=playerXZ each tick. A perlin noise texture
   is needed (Bruno Noises.js generates one) — generate a small repeating perlin
   DataTexture or reuse Wind's noise.
2. Terrain colour: replace/repurpose GlbV3World.#neutralizeTerrainMask — give the
   terrain a TSL MeshLambertNodeMaterial colourNode = mix(dirt, grass, gN) sampling
   the same mask. (Keep it cheap; full Bruno Terrain.js parity optional.)
3. Re-enable wind in App if needed (Wind is renderer-agnostic; verify it's TSL-safe
   — it built a DataTexture in v2; on WebGPU sample via texture()).

VERIFY: grass renders in the right places + follows the camera + sways. WebGPU
asserts via the verify-v3-first-frame.mjs pattern (drawcalls jump); VISUAL
screenshot by launching Chromium WITHOUT WebGPU flags (WebGL2 fallback — the only
backend Playwright captures; symlink node_modules/playwright{,-core} → /tmp). Shots
under .verify/shots/<date>/. Iterate the remap/orientation until it reads as grass.

Rules: VERIFY from files, never guess; don't deviate from Bruno unless 99% sure;
do NOT touch tools/blender/ or static/world/; one commit after I approve; NO
Co-Authored-By trailer.
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
