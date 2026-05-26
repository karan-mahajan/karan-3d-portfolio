# v2 Karan builder notes — what to adopt, what to change, what to leave

> Knowledge transfer for the future "design + build Karan's world" session. For each notable Bruno pattern, the format is:
>
> 1. **The pattern**
> 2. **Why Bruno used it** (the constraint it solves)
> 3. **What to consider when adopting** (Bruno-specific assumptions Karan may not share)
> 4. **Alternative approaches** (modern Three.js, RAPIER, TSL features, etc.)
>
> Companion docs: `v2-recreation-playbook.md` (rebuild Bruno's), `bruno-origin-map.md` (where everything lives), v1 `CHECKLIST.md` (adoption-priority tracker).
>
> **Scope:** this file does NOT design Karan's world. It distills decisions for a later session to revisit with full context.

---

## 1. Engine & game loop

### 1.1 Frame-time cap at 1/30 + global time scale = 2

- **Pattern:** `Ticker.maxDelta = 1/30`, `Ticker.scale = 2`, `deltaScaled = delta * scale`. All physics + shader time runs off `deltaScaled`. GSAP global timeScale also set to 2.
- **Why:** Prevents tunneling and giant jerk on stalls (no frame exceeds 33ms of simulated time). The scale=2 makes the world feel snappier without changing the frame rate. Time is unified across physics, TSL, and DOM.
- **Adopting considerations:** Universal win, blueprint-independent. Recommended as Definitely-Adopt #1 in v1's `CHECKLIST.md`.
- **Alternatives:** None better. Don't try multi-fixed-step substep schemes in this kind of indie game; the cap + variable RAPIER timestep is robust.

### 1.2 Singleton Game with 3-phase async init

- **Pattern:** Game constructor → init() with 3 awaited phases (intro + main batch + physics-dependent). Asset list explicitly enumerated, not globbed.
- **Why:** Lets the intro screen show a real loading bar (intro batch ~4 small assets gets the kiosk on screen fast; main batch in parallel with RAPIER WASM); avoids over-loading on first paint.
- **Considerations:** Hardcoded asset list is brittle for content-heavy authoring. If Karan's content is dynamic (e.g., portfolio entries fetched from CMS), an asset manifest from a JSON file is better.
- **Alternatives:** Vite glob imports, or a JSON manifest in `static/` that Game reads to know what to load.

### 1.3 `setAnimationLoop` + priority-ordered Events

- **Pattern:** `renderer.setAnimationLoop(et => ticker.update(et))` drives everything; `Events` is a custom emitter with priority sorting so subsystem update order is explicit.
- **Why:** WebGPU integrates better with the GPU vsync via `setAnimationLoop`. Priority numbers make "render last" / "input first" intent self-documenting.
- **Considerations:** WebGPU is required (no WebGL fallback in Bruno's code). Karan's current main branch is on `@dimforge/rapier3d-compat ^0.12.0` and Three `^0.184.0` — WebGPU is feasible.
- **Alternatives:** Hand-rolled `requestAnimationFrame` (worse on WebGPU); EventTarget native (no priority).

### 1.4 `Object3D.copy` monkey-patch in `threejs-override.js`

- **Pattern:** Replace `Object3D.prototype.copy` to skip the `JSON.parse(JSON.stringify(userData))` deep clone.
- **Why:** That JSON round-trip is slow per-clone with thousands of meshes. Bruno's code is structured so userData is never mutated after creation, so the shallow share is safe.
- **Considerations:** If Karan's code mutates userData post-clone, this breaks. Audit before adopting.
- **Alternatives:** Don't deep-clone userData unless explicitly needed (replace specific usages), or use shallow clone.

---

## 2. Rendering & post-FX

### 2.1 WebGPU renderer with antialias gated on DPR

- **Pattern:** `antialias = pixelRatio < 2`, `setPixelRatio(Math.min(devicePixelRatio, 2))`.
- **Why:** On 2× displays, the pixel grid already AAs; MSAA buys nothing.
- **Adopt:** Yes, free perf.

### 2.2 `renderer.sortObjects = false` + manual renderOrder

- **Pattern:** Disable Three.js auto-sorting; manually set integer renderOrder; let setOpaqueSort/setTransparentSort be `(a,b) => a.renderOrder - b.renderOrder`.
- **Why:** Auto-sort is O(N log N) per frame; with thousands of meshes, it shows up. Manual sort is O(N) and gives full control over transparency layering.
- **Adopt:** Yes, once mesh count justifies it (>500 visible). Until then, premature.

### 2.3 Bloom with quality-branching mip count

- **Pattern:** `bloomPass._nMips = quality.level === 0 ? 5 : 2`, threshold=1, strength=0.25, smoothWidth=1. Always on.
- **Why:** Bruno's NPR cel-shaded look is *aesthetic*; bloom enhances the glow. Mobile gets fewer mips.
- **Considerations:** Heavy bloom suits Bruno's bright palette. Karan's blueprint may want subtler.
- **Alternatives:** Custom TSL bloom with thresholding by emissive intensity, or no bloom at all.

### 2.4 CheapDOF — fake vertical-strip blur

- **Pattern:** Compute `strength = |uv.y - 0.5|.smoothstep(start, end)` then `hashBlur(textureNode, strength*amount, {repeats:25})` then mix. Telephoto FOV (25°) sells the depth.
- **Why:** Real DOF needs depth buffer + circle-of-confusion math + expensive blur. This trick is one-shot per frame and reads as DOF when camera angle is fixed.
- **Considerations:** Only works with **fixed** or near-fixed camera (top-down-ish). Free-camera projects can't use it.
- **Alternatives:** Real depth-aware DOF (postfx pass that samples depth + chromatic blur).

### 2.5 GPU timestamp queries

- **Pattern:** `renderer.resolveTimestampsAsync(THREE.TimestampQuery.RENDER)` gated by monitoring flag → real GPU per-frame time.
- **Why:** Distinguishes GPU-bound vs CPU-bound when debugging "laggy feel".
- **Adopt:** Wire in but gate behind URL hash. Free.

---

## 3. Materials & shading (NPR / palette)

### 3.1 Single palette texture (128×4 sRGB, Closest filter)

- **Pattern:** All prop colors come from sampling one 128×4 palette texture by UV. UV authoring in Blender lands each mesh on specific rows/columns.
- **Why:** Tiny texture (362 bytes!) gives perfect color cohesion + lightning-fast sampling. Closest filter = pixel-art crispness.
- **Considerations:** Forces a low-poly stylized look. Karan's blueprint may want richer materials.
- **Alternatives:** Per-material color factors (loses cohesion), gradient palette texture (more variation but less stylized), procedural colors via vertex colors.

### 3.2 One master `MeshDefaultMaterial`

- **Pattern:** All props share one TSL material. `Materials.createFromMaterial(name, baseMat)` examines the Blender material name and wraps appropriately.
- **Why:** Consolidates NPR core-shadow, palette sampling, water-line blanking, reveal wipe, fog mix into a single shader. Easier to maintain than 35 per-material variants.
- **Considerations:** Loses per-material customization. Bruno escapes via emissive variants (`createEmissiveGradient`) for special cases.
- **Alternatives:** Material library with shared mixin TSL Fn() blocks composed per-material.

### 3.3 NPR core-shadow via smoothstep

- **Pattern:** `core = smoothstep(threshold-band, threshold+band, dot(N, L))`. Mix base color with shadow color by `core`.
- **Why:** Two-tone cel shading; no fragmentation, smooth band edge.
- **Considerations:** Universal NPR idiom. Adopt.

### 3.4 Fake light bounce from terrain

- **Pattern:** Sample terrain color (or terrain palette color); apply tint to fragments where normal.y < 0 (downward-facing surfaces).
- **Why:** Adds a hint of GI without raytracing — bottoms of trees pick up green from grass below.
- **Adopt:** Yes, cheap and convincing.

### 3.5 Water-line blanking by world y

- **Pattern:** Per-fragment `if (positionWorld.y > waterY - eps) wet else dry` (smoothed via smoothstep).
- **Why:** Free wet/dry transition; no extra geometry.
- **Adopt:** If water exists in Karan's world.

### 3.6 Reveal/discard wipe

- **Pattern:** `revealUniform = vec3(cx, cy, radius)`. Per-fragment `if (distance(positionWorld.xz, revealCenter) > revealRadius) discard()`. GSAP tweens radius from 0 → world-radius.
- **Why:** Single uniform drives a world-scale entrance wipe; no per-mesh fade timeline needed.
- **Adopt:** Yes — strong "first frame" effect; reusable for any transition.

### 3.7 TSL Wind node — fractal Perlin vertex displacement

- **Pattern:** TSL Fn() that maps `(worldPos, time)` → vec3 displacement. Sums 3 octaves of Perlin. Shared across grass, foliage, leaves, trees.
- **Why:** Single source of wind kept consistent across the world. Tied to `Weather.wind` output for cycle modulation.
- **Adopt:** Yes — keeps foliage coherent.

### 3.8 Emissive radial-gradient materials

- **Pattern:** `Materials.createEmissiveGradient(centerColor, edgeColor, …)` for lights/halos.
- **Why:** Cheap fake bloom-without-bloom for accent highlights.
- **Adopt:** Yes for accent UI/highlights.

---

## 4. World composition

### 4.1 Single master GLB + name-prefix dispatch

- **Pattern:** All areas authored in one collection in Blender; exported as `areas.glb`. Runtime dispatcher walks scene children and matches `child.name.startsWith(areaName)` to instantiate area classes.
- **Why:** Single source-of-truth file; Blender becomes the world editor; runtime just plumbs.
- **Considerations:** Areas.js dispatch list is hand-maintained — 13 active, EasterArea dormant. Easy to add/remove an area by editing this list.
- **Adopt:** Yes if Karan wants Blender-as-editor workflow. Alternative is per-area GLB files (slower iteration but cleaner separation).

### 4.2 Empty markers (`ref*`) for runtime metadata

- **Pattern:** Empties named `ref*` carry positions, radii (via scale), and userData. Regex `/^ref(?:erence)?([^0-9]+)([0-9]+)?$/` parses them into a `Map<string, Object3D[]>`.
- **Why:** Blender as a "Level editor" — annotate the scene with non-rendering markers that runtime code reads.
- **Adopt:** Yes — clean convention that scales.

### 4.3 Scale-encodes-radius/extent

- **Pattern:** Empties' uniform scale → cylinder radius (zone bounding) or sphere radius (zone frustum). Collider scale → half-extents.
- **Why:** Avoids a separate numeric property; the scale gizmo IS the radius gizmo in Blender.
- **Adopt:** Yes — ergonomic.

### 4.4 Collider-shape via child mesh name prefix

- **Pattern:** Child meshes named `cuboid*`, `tube*`, `ball*`, `trimesh*`, `hull*` get extracted as colliders, then removeFromParent so they don't render.
- **Why:** One Blender export carries both visuals and colliders; no separate physics file.
- **Adopt:** Yes — keeps source-of-truth single. **Caveat:** Bruno's `tube*` is unusual (Y=height first, then X=radius); document well.

### 4.5 Body-type substring tokens in mesh names

- **Pattern:** `*Physical*`, `*Dynamic*`, `*KinematicPositionBased*` substrings determine RAPIER body type.
- **Why:** Same one-file-source ergonomics as #4.4.
- **Adopt:** Yes; tokens regex'd out for runtime display.

### 4.6 InstancedGroup for repeated props

- **Pattern:** Per-collection "reference" instances in Blender. Runtime: first instance becomes the geometry base; rest become Object3D ref transforms; one InstancedMesh per material with `count = references.length`.
- **Why:** Massively reduces draw calls (one per material across many instances).
- **Adopt:** Yes for any prop scattered ≥10 times.

### 4.7 Per-area `update()` only when in-frustum

- **Pattern:** Each Area has `frustum.isIn` flag (refZoneFrustum vs camera optimalArea quad). `update()` only fires when in.
- **Why:** ~14 areas × per-tick logic adds up; only the visible area pays.
- **Adopt:** Yes.

### 4.8 All area dynamics start `sleeping: true`

- **Pattern:** RAPIER dynamic bodies created with `sleeping: true`; wake on physics event (collision, force).
- **Why:** Hundreds of dynamic props don't all simulate every frame.
- **Adopt:** Yes — RAPIER default for distant bodies.

### 4.9 Distance-based physics sleep

- **Pattern:** `Objects.js` sleeps bodies beyond `optimalArea.radius` per tick.
- **Why:** Far bodies are off-screen anyway; their physics doesn't need to advance.
- **Adopt:** Yes — combined with #4.8 is the right mobile-friendly default.

---

## 5. Camera & input

### 5.1 Smoothed focus point with magnet

- **Pattern:** `focusPoint.isTracking = true` → soft pull restores tracking; movement-action triggers re-tracking automatically.
- **Why:** Never feels like a snap; always feels like the camera "wants" to follow.
- **Adopt:** Yes — fundamental UX for follow cams.

### 5.2 Optimal-area quad via raycasting camera corners

- **Pattern:** Each frame, raycast camera frustum corners to ground plane → forms a quad. Used as the conservative bounding region for culling, shadow camera, fog distance.
- **Why:** With a tilted top-down-ish camera, the visible area isn't axis-aligned; the quad captures it.
- **Adopt:** Yes if camera angle is similar.

### 5.3 Speed-based zoom-out with smoothstep

- **Pattern:** `zoomOut = smoothstep(vMin, vMax, |vehicle.velocity|)`. Camera distance increases at speed.
- **Why:** Lets player see further when needed; reads "fast" emotionally.
- **Adopt:** Yes for vehicle-style movement.

### 5.4 Spring-damped camera roll on collision

- **Pattern:** Collision callback sets camera-roll target → spring (damping=4, pullStrength=100) over a few frames → restore.
- **Why:** Gives impact a "felt" cinematic effect.
- **Adopt:** Yes; tunable.

### 5.5 Cinematic transition = slerp + DOF fade

- **Pattern:** Camera move uses quaternion slerp + lookAt over 1.5s with `power2.inOut`; DOF amount fades to 0 during the move (so the destination is crisp).
- **Why:** Smooth, readable, signature feel.
- **Adopt:** Yes for area-to-area transitions.

### 5.6 Multi-modal input pipeline

- **Pattern:** Keyboard + Gamepad + Pointer + Wheel + Nipple + InteractiveButtons → unified named actions.
- **Why:** One callsite for "forward" works on any device; no per-source branches in game code.
- **Adopt:** Yes — clean abstraction.

### 5.7 Telephoto FOV (25°)

- **Pattern:** `PerspectiveCamera(25 fov, ratio, 0.1, 200)`.
- **Why:** Compressed look — feels like a diorama. Also enables cheapDOF trick (#2.4).
- **Considerations:** Locks Karan into the diorama aesthetic. Wide-angle (60–75°) feels more "first-person" and immersive.
- **Alternatives:** Wide FOV with mouselook (different vibe; rules out cheapDOF).

---

## 6. Physics (RAPIER 3D)

### 6.1 Native `@dimforge/rapier3d` 0.17 vs `-compat 0.12`

- **Note:** Karan's current package.json uses `@dimforge/rapier3d-compat ^0.12.0`. Bruno uses the native 0.17 with `vite-plugin-wasm + vite-plugin-top-level-await`. Native is faster + 0.17 has API improvements.
- **Adopt:** Migrate when ready. Compat works fine for prototyping.

### 6.2 Variable timestep = `ticker.deltaScaled`

- **Pattern:** `world.timestep = ticker.deltaScaled` each frame (with the 1/30 cap upstream).
- **Why:** Combines stability of capped delta with snappy 2× scaled time.
- **Adopt:** Yes.

### 6.3 Custom collision groups

- **Pattern:** `categories = { all, object, bumper, floor }` as bitmask membership filters.
- **Why:** Limits expensive collision checks; bumpers don't need to query against floor for "knock floors over" events.
- **Adopt:** Yes once group taxonomy is clear.

### 6.4 Force normalization in collision callback

- **Pattern:** `force = maxForce / (mass1 + mass2)`.
- **Why:** Audio scales naturally with impact regardless of who hit whom.
- **Adopt:** Yes for collision-triggered audio.

### 6.5 `setActiveEvents` only when callback exists

- **Pattern:** Don't pay event-emission cost for bodies without callbacks.
- **Adopt:** Yes — free perf.

### 6.6 Initial-state snapshot for respawn

- **Pattern:** At creation, snapshot body state. Respawn just resets to snapshot (no recreate).
- **Adopt:** Yes — much faster than rebuilding bodies.

---

## 7. Cycles & weather

### 7.1 Single Cycles base + DayCycles + YearCycles

- **Pattern:** Cycles updates progress 0..1; presets (day/dusk/night/dawn × winter/spring/summer/fall) hold target uniforms; smoothstep interpolates.
- **Why:** Tiny lookup table drives every visual change across time.
- **Adopt:** Yes — see `bruno-animation-keyframes.json` for literal stops.

### 7.2 Weather as noise-modulated cycles

- **Pattern:** `weather.temperature/humidity/wind/electricField/clouds` derived from `sin(x) * sin(x*1.678) * sin(x*2.345)` (irrational ratios → quasi-periodic).
- **Why:** Cheap, deterministic, no Perlin needed.
- **Adopt:** Yes — single line of code yields hours of varied weather.

### 7.3 GSAP-tweened overrides

- **Pattern:** When Tornado or Circuit-finish wants to force weather, a GSAP tween blends a strength uniform between baseline and override.
- **Adopt:** Yes — clean override pattern.

### 7.4 Lock via env vars for screenshots

- **Pattern:** `VITE_DAY_CYCLE_PROGRESS=0.5` freezes day at noon.
- **Why:** Reproducible screenshots / dev iteration.
- **Adopt:** Yes — trivial.

---

## 8. UI & UX

### 8.1 Reveal as 3-step state machine + single uniform

- **Pattern:** Reveal class drives `step=0/1/2`; tweens `revealUniform.radius` over a couple seconds; shader does the heavy lifting.
- **Adopt:** Yes — see #3.6.

### 8.2 InteractivePoints — 3D-positioned DOM labels

- **Pattern:** DOM <div> per point; world position projected to screen each frame; show/hide on hover/proximity.
- **Why:** Crisp text without billboard meshes; integrates with HTML modals.
- **Adopt:** Yes for callout labels.

### 8.3 Modals + ClosingManager + Tabs

- **Pattern:** Stacked modal overlays; tabs inside; ClosingManager handles Esc precedence.
- **Adopt:** Yes — clean and reusable.

### 8.4 Notifications with anti-spam

- **Pattern:** Toast with per-item `antiSpam` cooldown.
- **Adopt:** Yes.

### 8.5 Touch button overlay (6 buttons)

- **Pattern:** Interact, Unstuck, Previous, Next, Open, Close as DOM buttons feeding actions.
- **Why:** Mobile gets the same action set as keyboard.
- **Adopt:** Yes for mobile parity.

### 8.6 Map as ortho overlay

- **Pattern:** 117-object stylized 2D Blender 'map' collection rendered orthographically over the world.
- **Adopt:** Optional — common to top-down games.

---

## 9. Audio

### 9.1 Howler groups + pool=2 + antiSpam=0.1

- **Pattern:** Howler groups; `play()` (sequential) and `playRandomNext()` (skip-ahead); per-sound pool size + anti-spam cooldown.
- **Why:** Prevents audio clipping when many same-sound events fire in quick succession.
- **Adopt:** Yes.

### 9.2 Audio init deferred to first user input

- **Pattern:** Howler.audioContext doesn't construct until user clicks something.
- **Why:** iOS Safari requires this; suppresses autoplay warnings.
- **Adopt:** Yes — universal browser requirement.

### 9.3 Distance-faded volume per tick

- **Pattern:** Audio.update() each tick re-computes volume = `1 - distance/maxDist`.
- **Adopt:** Yes for positional audio.

---

## 10. Performance & build

### 10.1 `VITE_COMPRESSED` env switch

- **Pattern:** Dev uses raw `.glb`/`.png`; prod uses `-compressed.glb`/`.ktx`.
- **Why:** Fast iteration in dev; small payload in prod.
- **Adopt:** Yes.

### 10.2 `scripts/compress.js` pipeline

- **Pattern:** `gltf-transform draco --quantize-position 12 --quantize-normal 6 --quantize-texcoord 6` + `toktx` per-purpose presets + `sharp.webp({quality:80})`.
- **Why:** Per-asset compression. Manual one-shot after Blender export.
- **Considerations:** Bruno doesn't use `gltf-transform optimize` macro — it dedups across files and broke karan-portfolio once. Use Node API per-file.
- **Adopt:** Yes; copy `compress.js` verbatim.

### 10.3 PreRenderer shader warm-up at boot

- **Pattern:** On boot (high quality only): one-shot off-screen render compiles every material's shader. Helpers tagged `preventPreRender` are skipped.
- **Why:** Avoids first-frame stalls.
- **Adopt:** Yes.

### 10.4 Asset list explicit, never globbed

- **Pattern:** Each loaded asset is `[ keyName, path, loaderType, optionalModifierFn ]` in `Game.js`.
- **Why:** Tree-shakable, lazy-load aware, no surprise files.
- **Adopt:** Yes — manifest > glob.

### 10.5 Shadow recomputed only on `throttleChange` (400ms after resize)

- **Pattern:** Viewport.js triggers shadow rebuild only 400ms after the user stops resizing.
- **Adopt:** Yes — free.

---

## 11. Karan-specific transfer considerations (where Bruno's choices don't fit)

These are decisions Karan should revisit per their own blueprint:

- **Vehicle as the player avatar.** Bruno's PhysicsVehicle is core; if Karan's blueprint is "walking" or "first-person" or "puzzle", port the vehicle pattern only if relevant.
- **14 distinct areas each with a minigame/modal** vs one continuous environment. Bruno's central UX bet — Karan may want fewer/larger spaces.
- **NPR cel-shading with palette texture.** Visual direction; not universal. Alternatives include hand-painted, photoreal, line-only, mixed-media.
- **Bloom + bright colors + cheapDOF.** Adopt if going for Bruno-adjacent vibe; else, consider toned-down post.
- **Day/year/weather cycles.** Strong characterization. Decision: static vs dynamic environment.
- **Tornado, lightnings, rain, snow, confetti, leaves, water.** Each independent. Pick selectively.
- **Whispers (multiplayer).** Requires server backend. Big undertaking; only if "social presence" is a blueprint feature.
- **200+ achievements.** Heavy commitment; only if "game" is a core blueprint trait.
- **Howler MP3+WAV music (~150 MB).** Big asset footprint; alternatives include MP3-only, OGG, or shorter loops.
- **Telephoto 25° FOV.** Locks the diorama look. Wide-angle is different (more immersive).
- **Behind-the-scene devlog area.** Bruno's signature touch; Karan can do similar or differently.

---

## 12. Modern alternatives Karan might consider (2026 stack updates)

These weren't available or weren't standard when Bruno first built this:

- **TSL has stabilized.** Bruno already uses it; Karan can lean further. Look at `three/tsl` exports for newer node helpers.
- **WebGPU compute nodes.** For particle systems / GPU-driven simulation; Bruno does this for some effects (search `bruno-shaders.md` for "compute"). Karan can extend.
- **RAPIER 0.17 native** + `vite-plugin-wasm`. Faster than `-compat`. Migration is mechanical but breaks some 0.12 API names.
- **`three/addons/objects/BatchedMesh`** — modern alternative to InstancedMesh for non-identical geometry. Bruno hasn't adopted; might give Karan more flexibility.
- **`three/addons/render/EffectComposer` ported to TSL** — Bruno builds post via `RenderPipeline + outputNode.add(bloom)`, which is the current idiomatic WebGPU way; Karan can adopt as-is.
- **`@vercel/speed-insights`** — Karan already has this dependency; Bruno's analytics is a manual tag in `index.html`. Vercel handles the equivalent automatically.
- **MeshPhysicalNodeMaterial** (TSL-friendly) — for PBR-leaning props if Karan wants more material variety than the palette pattern.
- **Lottie/Rive for UI animation** — modern alternative to GSAP-heavy DOM tweens.
- **HTMX-style declarative interactions** for any panel/modal content — less imperative than Bruno's Modals.js.

---

## 13. Reading order for the design session

1. **`v2-final-index.md`** — quick map of where each piece of v2 data lives.
2. **`v2-karan-builder-notes.md`** — this file. Skim sections relevant to current design question.
3. **`bruno-origin-map.md`** — feature lookup. "How does Bruno do X?"
4. **`bruno-analysis.md`** (v1) — the master narrative.
5. **`v2-recreation-playbook.md`** — read once to understand the full asset extraction chain (informs what's authoring-heavy vs code-heavy).
6. Don't read source markdowns (`bruno-shaders.md`, `bruno-runtime-source.md`) cover-to-cover — too much. Jump in via anchor links from `bruno-origin-map.md`.

---

## 14. Anti-patterns to avoid carrying over

- **Hardcoded asset list of 43 entries in Game.js.** Use a manifest. Bruno's setup is fine for a hand-curated portfolio but won't scale to "data-driven content."
- **Single 700-line `View.js`.** Camera logic split into modules (focus + zoom + roll + cinematic) would be more reusable.
- **One master `MeshDefaultMaterial`** can become a god-class. Modular TSL Fn() composition gives the same effect with more reusable parts.
- **No automated test of the .glb → runtime contract.** Adding/renaming a Blender empty silently breaks runtime. A boot-time assertion ("expected refZoneBounding for landing") would have caught the EasterArea-dropped-from-list silently.
- **Mute palette node manually before each Blender export.** Easy to forget. A pre-export script that mutes the right nodes is a small automation win.

---

End — `v2-karan-builder-notes.md`. See `v2-final-index.md` for navigation.
