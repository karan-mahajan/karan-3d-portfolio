# Task prompt — Material consolidation to eliminate shader-compile hitches

> Hand this whole file to a fresh coding agent (Claude Code, Codex, etc.). It is
> self-contained — assume the agent has NO prior conversation context.

---

## Operating mode (read this first)

1. **Analyze before you touch anything.** Phase 1 is read-only investigation;
   report findings. Phase 2 is implementation.
2. **DO NOT commit. DO NOT push.** Leave every change uncommitted in the working
   tree for me to review and verify in a browser myself.
3. **Verify facts from the actual files — never guess.** Inspect the real
   material/GLB/source before quoting any number, name, or behaviour, then act.
   If an assumption below turns out wrong when you check, stop and report it.
4. **Match the existing code style:** vanilla ES modules, `class` syntax, private
   `#fields`, no TypeScript, no comments that restate code (only *why* for
   non-obvious choices). JSDoc on classes/methods is fine.
5. **Never invent assets.** If something needs a model/texture/atlas that isn't
   already in `static/`, stop and ask — don't fabricate or load a guessed path.
6. **Run `npm run build` after changes** to confirm it compiles (a pre-existing
   "chunks larger than 500 kB" warning is normal — ignore it). Don't burn time on
   screenshot/probe loops; I verify visuals manually in a real browser.

## Project

A 3D walkable portfolio. **Vanilla Three.js r0.184 on the WebGPU/TSL backend**
(`three/webgpu` + `three/tsl` node materials) + **@dimforge/rapier3d-compat**
physics + **Vite** (`publicDir: 'static'`). No React, no framework. Player walks
an island toward cardinal sections. Working dir is the repo root.
`npm run dev` → localhost:5173, `npm run build` → dist/.

The world geometry is loaded from per-system GLBs under `static/world/` via a
manifest, in **[src/World/GlbV3World.js](src/World/GlbV3World.js)** (the main
loader — read this thoroughly). `static/world/manifest.json` lists every GLB.

## What is ALREADY DONE — do not redo any of this

A 3-tier performance pass already shipped (committed). Do not repeat it:

- **Hitch fixes:** adaptive-DPR cooldown/hysteresis + day/night shader prewarm
  awaited before first toggle + persistent thunderstorm materials.
- **Steady-load cuts:** grass density lowered (≈450/axis); grass blade decimated
  9→5 verts; a build-time low-detail water shader branch on medium/low tiers.
- **Draco compression:** the visual world GLBs are Draco-compressed (11.4 MB →
  1.5 MB). `DRACOLoader` is already wired in
  [src/Utils/Loader.js](src/Utils/Loader.js); `tools/compress-world-glb.mjs`
  (`npm run compress:world`) re-runs it. **`terrain.glb` and `colliders.glb` are
  intentionally kept RAW** (their geometry feeds the physics heightfield + Rapier
  colliders — lossy quantization would move the ground / collider fit). Do not
  compress them, and do not re-run compression as part of this task.

## THE PROBLEM you are fixing

The world ships **151 distinct baked materials** (verify with the snippet in
"Analysis" below). Counts per GLB at time of writing: areas 40, miscFx 24,
structures 20, oakTrees 19, flowers 10, scenery 8, lava 6, statue/lanterns/
birch/bricks 3, cherry/fences/poleLights/benches 2-4, terrain/rocks 1.

On the WebGPU/TSL backend, **each distinct material compiles its own shader
program**, and each program is **JIT-compiled by the GPU driver the first time it
is actually rendered** — a synchronous, blocking operation = a dropped frame =
a visible hitch. Symptoms the user reports, and their cause:

- **"Gets stuck at random places while walking"** → a mesh whose material hasn't
  been seen yet enters the camera → its program compiles on-screen.
- **"Hitches at night / in the morning"** → the day↔night toggle changes the
  light rig, forcing **program variants** to recompile across many materials.

Bruno Simon's folio-2025 (the visual reference, at
`~/Documents/Projects/folio-2025` if present) avoids this by funnelling almost
the entire world through **one shared material** (`sources/Game/Materials.js`,
a palette-texture lookup) → ~1 program, compiled once at load, behind the
loading screen. Nothing compiles on-screen ever again. That is why his
framerate is constant.

## THE GOAL

Collapse the ~151 GLB-derived materials down to a **tiny shared set** (target:
~3 programs — one opaque lit, one emissive, one alpha-blended transparent; plus
keep any genuinely textured materials as-is) and **prewarm them during load** so
zero shader programs ever compile on-screen. **Visuals must stay pixel-identical**
— this is a perf change, not a restyle.

This *eliminates the entire class* of compile-hitch, where the existing Tier-1
prewarm only patched the day/night case.

## DO NOT TOUCH these (they are separate, bespoke, perf-tuned, user-validated)

These are **runtime-authored TSL node materials**, NOT part of the 151 baked GLB
materials, and are already correct. Leave them entirely alone:

- The **terrain ground material** (`GlbV3World.#applyTerrainGroundMaterial`) —
  custom grass-mask + tile-paint node graph.
- **Grass** ([src/World/Grass.js](src/World/Grass.js)) — bespoke instanced blade
  shader. Its blade shape + olive palette are user-validated; do not alter.
- **Water** ([src/Effects/Water.js](src/Effects/Water.js)), **Foliage**
  ([src/World/Foliage.js](src/World/Foliage.js)), **Sky/Sun/Moon/TimeOfDay**,
  Fireflies, Rain, WindLines, Leaves, Thunderstorm, Lava — all custom.
- **`terrain.glb`, `colliders.glb`** and any `*References`/`references.glb`.
- **Validated palettes:** tree/foliage/grass colours are user-approved. If your
  consolidation would shift ANY visible colour, that is a bug — flag it, don't
  ship it.

Your scope is strictly the **baked materials that arrive on the monolithic +
instanced world meshes from the GLBs** (areas, structures, scenery, statue,
miscFx, trees, fences, benches, lanterns, poleLights, rocks, bricks, flowers).

## PHASE 1 — ANALYZE (read-only; produce a written report before coding)

Investigate and report:

1. **Enumerate + categorize all 151 materials.** For each GLB material, record:
   base colour, emissive (note `KHR_materials_emissive_strength`), opacity/
   `alphaMode` (transparent?), and whether it has a **baseColorTexture / any
   texture** (textured materials CANNOT collapse to a flat vertex colour — they
   must keep their material or a textured shared variant). Quick count:
   ```sh
   node -e 'const fs=require("fs");const m=JSON.parse(fs.readFileSync("static/world/manifest.json","utf8"));
   for(const rel of [...m.monolithic.map(e=>e.file),...m.instanced.map(e=>e.visual).filter(Boolean)]){
     const b=fs.readFileSync("static/world/"+rel);const l=b.readUInt32LE(12);const j=JSON.parse(b.toString("utf8",20,20+l));
     for(const mt of (j.materials||[])) console.log(rel, mt.name, JSON.stringify({c:mt.pbrMetallicRoughness?.baseColorFactor,
       tex:!!mt.pbrMetallicRoughness?.baseColorTexture, emis:mt.emissiveFactor, es:mt.extensions?.KHR_materials_emissive_strength, alpha:mt.alphaMode}));
   }'
   ```
   Bucket them: **flat-opaque**, **flat-emissive**, **transparent**, **textured**.
   How many fall in each? (The flat-opaque bucket is the big win.)

2. **Find where GLB materials become live Three materials.** In
   `GlbV3World.js`, the monolithic GLBs are added via `loadGLTF` and the renderer
   auto-converts their materials to node materials. Instanced systems build
   `InstancedMesh`es reusing `proto.material` in `#loadInstancedSystem`. Identify
   every place a mesh keeps its baked material, so you know what to reassign.

3. **Confirm the consolidation mechanism is viable.** Recommended (see Phase 2):
   a **runtime** bake — after load, write each mesh's flat material colour into a
   `COLOR_0` (vertex-colour) buffer attribute and reassign a shared node material
   that reads it. Verify: are the baked materials flat-colour (no per-vertex
   colour already, no texture) so this is lossless? Are shadow flags
   (`castShadow`/`receiveShadow`) currently set per-mesh (must be preserved)?
   What node-material class fits the look — the terrain ground uses
   `MeshLambertNodeMaterial`; the world is flat-shaded low-poly, so Lambert+vertex
   colour likely matches. Confirm against a couple of real materials.

4. **Find the prewarm hook.** Locate the existing `compileAsync`/shader-prewarm
   in [src/App.js](src/App.js) (around the day/night prewarm) so the new shared
   materials get prewarmed the same way, at load, behind the loading screen.

5. **List risks/edge cases** you found: textured materials (e.g. scenery has at
   least one embedded texture), emissive props (lava letters, lamp glows, miscFx),
   double-sided/alpha materials, anything instanced, anything that also feeds a
   runtime collider from its mesh (trees/benches/fences — geometry only, colour
   change is safe, but don't disturb their geometry).

**Report all of the above, with the bucket counts and your proposed exact
material set, before writing code.**

## PHASE 2 — IMPLEMENT (after the analysis; verify each assumption as you go)

**Recommended approach: runtime material consolidation (no GLB/asset changes,
fully reversible, keeps Draco intact).** In `GlbV3World` after the world loads:

1. Traverse the world meshes you scoped. For each **flat-colour opaque** mesh:
   add a `COLOR_0` `Float32BufferAttribute` (count×3) filled with that mesh's
   material `.color` (linear), then assign **one shared
   `MeshLambertNodeMaterial`** whose `colorNode` reads the vertex colour. Preserve
   `castShadow`/`receiveShadow`/`side`. Result: all flat-opaque meshes → 1 program.
2. **Flat-emissive** meshes → a **second** shared material that also drives an
   emissive node from a baked emissive vertex colour (or a second attribute).
   Preserve emissive strength visually.
3. **Transparent** meshes → a **third** shared material (`transparent:true`,
   correct blending/depthWrite) reading vertex colour. Keep their existing
   `renderOrder` if any.
4. **Textured** materials: leave as their own materials (a handful of extra
   programs is fine) OR, only if trivial, fold into a textured shared variant.
   Do not lose any texture.
5. **Prewarm** the new shared materials at load via the same `compileAsync` path
   App.js already uses, so they never compile on-screen.

If you judge a **build-time** vertex-colour bake (a `gltf-transform` script that
writes `COLOR_0` into the GLBs) to be cleaner, you may propose it instead — but it
must re-apply after `npm run compress:world`, must keep terrain/colliders
untouched, and must not regress Draco. State the trade-off and let the result be
reviewable. Default to the runtime approach unless you have a strong reason.

**Correctness bar:** before/after, every prop must render the same colour. Since
you can't see the screen, prove equivalence structurally — e.g. assert the vertex
colour you bake equals the source material's linear `.color`, and that emissive/
transparent buckets keep their channels. Note anything you could not prove so the
user can eyeball it.

## Hard constraints (repeat)

- **No commits, no pushes.** Working-tree changes only.
- Don't touch `terrain.glb`, `colliders.glb`, references GLBs, or the bespoke
  runtime node materials listed above. Don't re-run Draco compression.
- Don't change any visible colour. Validated tree/foliage/grass palettes are
  off-limits — flag, don't edit.
- `npm run build` must pass.
- Match the codebase style; add `WHY` comments only where the choice is
  non-obvious.

## Key files

- [src/World/GlbV3World.js](src/World/GlbV3World.js) — world loader; where GLB
  meshes + materials land, and where instanced meshes are built. Primary edit
  site.
- [src/App.js](src/App.js) — tick loop + boot wiring + the existing shader
  prewarm to extend.
- [src/Utils/Loader.js](src/Utils/Loader.js) — GLTF/Draco loader setup.
- [src/Effects/Water.js](src/Effects/Water.js),
  [src/World/Grass.js](src/World/Grass.js),
  [src/World/Foliage.js](src/World/Foliage.js) — examples of the project's TSL
  node-material style (and the materials you must NOT touch).
- `static/world/manifest.json` — the GLB list driving everything.
- [CLAUDE.md](CLAUDE.md) — project rules (asset policy, collider sizing,
  heightfield grounding, verification sandbox layout under `.verify/`).

## Acceptance criteria

1. Distinct shader **programs** for the world geometry drop from ~151 to a small
   constant (~3 + a few textured). Demonstrate the reduced material set.
2. **Visuals unchanged** — no colour/emissive/transparency regressions.
3. No on-screen shader compiles: shared materials prewarmed at load. Walking into
   a new area and toggling day↔night should no longer trigger a compile.
4. `npm run build` passes; physics/grounding untouched (terrain & colliders raw).
5. Nothing committed.
