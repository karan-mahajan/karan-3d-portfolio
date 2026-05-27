# TerrainData foundation — design

**Date:** 2026-05-27
**Scope:** New `src/World/TerrainData.js` runtime module that loads a worldspace data mask (`terrainData.png`) and exposes it to both CPU consumers (sampler + threshold predicates) and GPU consumers (shader uniforms + GLSL helper).
**Blocks:** spike-grass port, Bruno-style cobblestone slab shader, leaves water-damping, future surface-aware systems.
**Does not change:** existing renderer, terrain mesh, palette, any visible behavior. Purely additive foundation.

## Background

Bruno Simon's folio-2025 drives a large portion of his world appearance from a **single 256×256 RGB PNG** (`resources/textures/terrainData.png`). The three channels encode independent worldspace masks:

| Channel | Role | Consumers in folio-2025 |
|---|---|---|
| **R** | Slab / cobblestone path mask | `Game/World/Floor.js` — `slabTerrain = terrainData.r` drives slab blending |
| **G** | Grass density / hidden mask | `Game/Terrain.js` — mixes grass color; `Game/World/Grass.js` — hides blades where `g < 0.4` |
| **B** | Elevation / depth gradient | `Game/Terrain.js` — samples a 16-px vertical gradient for ground color; `Game/World/Leaves.js` — picks water-vs-air damping coefficient |

Bruno samples this PNG in his procedural plane shader via a worldspace→UV function (`worldPositionToUvNode`) and reads R/G/B as masks. This is the *technique* we're porting. Our karan-portfolio world has a sculpted Blender terrain (different from his procedural plane), our own palette (alpine, kept), and our own layout (cardinal sections, not Bruno's river). The technique is portable; the painted content is not.

## Goals

- A single runtime module that loads and exposes `terrainData.png` once, shared across the app.
- **GPU access** parity with Bruno: any shader can drop in a GLSL snippet and call `terrainDataAt(worldXZ)`, just like our existing `Wind.windOffsetGLSL`.
- **CPU access** for our existing CPU-side consumers (Footprints, AudioManager step-surface logic, Discovery, future Leaves damping). Bruno doesn't need this; we do.
- Coverage maps 1:1 to terrain bbox so a single PNG covers the whole walkable area without tiling.
- Zero per-frame cost (the texture is static; no `update()` tick).
- Placeholder strategy: drop Bruno's PNG in during development, replace with our own before merge to `main`.

## Non-goals

- Authoring our own `terrainData.png` (deferred — handled in a separate sub-project once the runtime is verified against Bruno's placeholder).
- The downstream sub-projects (spike-grass port, slab shader rewrite, leaves water-damping) themselves — each gets its own spec.
- Migrating existing CPU surface checks (`App.js#surfaceAt`, Discovery's path lookups) — purely additive; migrations are follow-up cleanup.
- The `terrainGrass.exr` / `terrainWater.exr` / `slabs.png` from Bruno's static folder. Out of scope for this sub-project.
- WebGPU / TSL parity. We are on vanilla three @ 0.184 + classic GLSL.

## Architecture overview

```
static/textures/terrainData.png   (placeholder = copy of Bruno's PNG; will be replaced)
        |
        v
src/World/TerrainData.js          (loads once during App.boot())
   |   |
   |   +--> CPU byte cache (Uint8ClampedArray, 256*256*4)
   |          - sampleAt(x, z) → { r, g, b }            bilinear
   |          - isInWater(x, z)  → b < 0.13             (Bruno threshold)
   |          - hasGrass(x, z)   → g > 0.4              (Bruno threshold)
   |          - hasSlab(x, z)    → r > 0.5              (chosen midpoint)
   |
   +-> THREE.Texture                                    (sampler2D for GLSL)
          - uniforms = { uTerrainData, uTerrainDataExtent }
          - static get terrainDataGLSL  (declares uniforms + helpers)
```

Consumers:

- **Future** spike-grass: GLSL `terrainDataAt(worldXZ).g` for hidden-mask lift.
- **Future** slab shader: GLSL `terrainDataAt(worldXZ).r` to mix slab vs. dirt.
- **Future** leaves damping: CPU `isInWater(x, z)` to pick damping coefficient.
- **Optional, later** AudioManager / Discovery: replace path-array lookups with `hasSlab` calls.

## Module API

```js
class TerrainData {
  static URL = '/textures/terrainData.png';

  constructor({ extent } = {})         // extent = terrain.size / 2  (≈96.85)
  async load(loader)                   // fetches + decodes the PNG, fills byte cache
  sampleAt(worldX, worldZ)             // CPU bilinear → { r, g, b } floats in [0,1]
  isInWater(worldX, worldZ)            // returns boolean
  hasGrass(worldX, worldZ)             // returns boolean
  hasSlab(worldX, worldZ)              // returns boolean
  get uniforms()                       // { uTerrainData, uTerrainDataExtent } — share across materials
  static get terrainDataGLSL()         // GLSL snippet: uniforms + terrainDataAt + aliases
  dispose()                            // releases byte cache + texture
}
```

`extent` is fixed at construction (terrain size doesn't change at runtime).

## UV coverage convention

A single rule:

```
PNG UV (0, 0) -> world XZ (-extent, -extent)
PNG UV (1, 1) -> world XZ (+extent, +extent)
```

With `terrain.size ≈ 193.7m` post-resize, `extent ≈ 96.85m`. One PNG covers the entire terrain bbox; outside it, samples clamp to the edge value (typically near-zero / underwater), which is the safe default.

**Texture settings** (set once when the THREE.Texture is built):

- `wrapS = wrapT = ClampToEdgeWrapping` — outside-terrain reads = edge value, safe default.
- `magFilter = LinearFilter`, `minFilter = LinearFilter` — bilinear; matches Bruno's defaults.
- `colorSpace = NoColorSpace` — this is a *data* texture; raw 0..255 → 0..1 with no sRGB curve. The PNG is sRGB-encoded on disk for editor convenience but the runtime treats it as linear data.

**Note:** Bruno divides by an extra `/ 1.5` (folio-2025 `Game/Terrain.js:90`) so his PNG tiles slightly. We do not need that — full-bbox 1:1 + edge clamp is simpler and sufficient.

## CPU sampler

`load()` pipeline:

1. Fetch PNG via the existing `Loader` (or fall back to `new THREE.TextureLoader().loadAsync(...)` — Loader API will be confirmed at implementation time; the fallback is one line either way).
2. Decode the loaded `<img>` into a hidden 256×256 `OffscreenCanvas` (with `HTMLCanvasElement` fallback for older browsers).
3. `getImageData(0, 0, 256, 256).data` → `Uint8ClampedArray` of length `256 * 256 * 4`.
4. Store on `this.#pixels`. Hold both the byte array (CPU sampling) and the THREE.Texture (GPU sampling).
5. Discard the canvas; only the bytes are kept.

`sampleAt(worldX, worldZ)` mirrors the bilinear pattern from `terrain.heightAt` in [src/World/GlbWorld.js](../../../src/World/GlbWorld.js):

```js
const W = 256, H = 256;
const u = (worldX / (2 * this.extent) + 0.5) * (W - 1);
const v = (worldZ / (2 * this.extent) + 0.5) * (H - 1);
const u0 = clamp(floor(u), 0, W - 1), u1 = clamp(u0 + 1, 0, W - 1);
const v0 = clamp(floor(v), 0, H - 1), v1 = clamp(v0 + 1, 0, H - 1);
const tu = u - u0, tv = v - v0;
// fetch 4 corner RGB triples from #pixels, bilerp, return { r, g, b }
```

About 25 ops per sample — cheap enough for handfuls of CPU consumers per frame, **not** cheap enough for per-vertex grass (use GPU path for that).

Convenience predicates are thresholded reads:

| Predicate | Test | Source for threshold |
|---|---|---|
| `isInWater(x, z)` | `sampleAt(x, z).b < 0.13` | Bruno's `Game/World/Leaves.js:246` remap pivot `(0.02, 0.13)` |
| `hasGrass(x, z)` | `sampleAt(x, z).g > 0.4` | Bruno's `Game/World/Grass.js:126` `step(g - 0.4, 0.1)` |
| `hasSlab(x, z)`  | `sampleAt(x, z).r > 0.5` | Midpoint default; tunable when we wire it |

**Memory cost:** ~256 KB RAM for the byte cache. Trivial vs. avoiding GPU readbacks.

## GLSL helper

A single static getter, in the same shape as `Wind.windOffsetGLSL` in [src/World/Wind.js](../../../src/World/Wind.js):

```glsl
uniform sampler2D uTerrainData;
uniform float     uTerrainDataExtent;

vec3 terrainDataAt(vec2 worldXZ) {
  vec2 uv = worldXZ / (2.0 * uTerrainDataExtent) + 0.5;
  return texture2D(uTerrainData, uv).rgb;
}

float terrainGrass(vec2 worldXZ)     { return terrainDataAt(worldXZ).g; }
float terrainSlab(vec2 worldXZ)      { return terrainDataAt(worldXZ).r; }
float terrainElevation(vec2 worldXZ) { return terrainDataAt(worldXZ).b; }
```

Consumer pattern (illustrative, for future spike-grass):

```js
material.onBeforeCompile = (shader) => {
  Object.assign(shader.uniforms, terrainData.uniforms);
  shader.vertexShader = shader.vertexShader
    .replace('#include <common>',
      `#include <common>\n${TerrainData.terrainDataGLSL}`)
    .replace('#include <begin_vertex>',
      `#include <begin_vertex>
       // Bruno's hidden mask: lift blade 100m if grass channel < 0.4
       float grassMask = step(0.4, terrainGrass(worldPos.xz));
       transformed.y += (1.0 - grassMask) * 100.0;`);
};
```

This is the same trick Bruno uses on folio-2025 `Game/World/Grass.js:126,179`.

**Contracts the snippet relies on:**

1. The consumer vertex shader must compute `worldPos` (or equivalent) **before** invoking the helper. Three.js's `begin_vertex` chunk doesn't auto-expose worldspace; consumers either include `modelMatrix * vec4(position, 1.0)` inline or pull from `instanceMatrix[3].xz` (matches what the deleted `Grass.js` already did for the player-bend uniform).
2. `uTerrainDataExtent` is a single float, set once at load; no per-frame update.
3. `uTerrainData` and `uTerrainDataExtent` are reference-shared across all materials via the `uniforms` getter — updating one updates all. Same model as `Wind.uniforms` today.

**Pitfall:** `texture2D` is GLSL 1.0. three @ 0.184 emits GLSL 1.0 in `ShaderChunk` today, so this is correct. A future GLSL 3.0 upgrade would need `texture()` — global concern, not TerrainData-specific.

## Wiring + bootstrapping

**Disk location during dev:** `static/textures/terrainData.png` (Vite's `publicDir: 'static'` serves it at `/textures/terrainData.png`). Sits next to the existing `static/textures/palette.png` from phase-01.

**Construction:** must run *after* `world.loadAssets()` completes — `extent` depends on `terrain.size`. Declared as `null` in the `App` constructor and populated in `boot()`, matching how `this.water` is already handled. Placement: parallel with the existing post-world-load block where the (currently commented-out) `grass.load(...)` call would live.

```js
// In App.boot(), after world.loadAssets() resolves:
this.terrainData = new TerrainData({ extent: this.world.terrain.size / 2 });
await this.terrainData.load(this.loader);
```

**Loader integration:** the existing `src/Utils/Loader.js` API will be confirmed at implementation time. Either path is one line: `this.loader.loadTexture('/textures/terrainData.png')` if it exists, else `new THREE.TextureLoader().loadAsync('/textures/terrainData.png')`.

**App tick:** no work added. The texture is static. (Bruno's tick updates a wheel-tracks `tracksDelta` we don't have.)

**Removals:** none. Purely additive. `App.js#surfaceAt` and Discovery's path lookups stay as-is for now.

## Verification plan

`.verify/scripts/verify-terraindata.mjs`, following the sandbox conventions in [CLAUDE.md](CLAUDE.md):

- Boot via `bootAndDismiss(page)` from `.verify/scripts/_boot.mjs` — never inline a dismissal loop.
- Wait for `window.app.terrainData` to be loaded (polling on the page side; existing pattern from other probes).
- Assertions via `page.evaluate`:
  1. **Spawn point** `(0, 0)`: `app.terrainData.sampleAt(0, 0)` returns finite numbers in `[0, 1]` for r/g/b.
  2. **Far ocean** `(120, 120)`: outside terrain bbox; should edge-clamp to a low-elevation reading, so `app.terrainData.isInWater(120, 120) === true`.
  3. **Threshold consistency**: for a grid of 16 deterministic test points, assert `hasGrass(x, z) === (sampleAt(x, z).g > 0.4)`, and similar for the other two predicates. Catches off-by-one bugs in the predicates.
  4. **GPU/CPU parity**: render a 1×1 test target through a small `ShaderMaterial` that emits `terrainDataAt(testXZ)` for one chosen world XZ, read it back via `renderer.readRenderTargetPixels`, compare to `sampleAt(testXZ)`. Tolerance ±2/255 per channel (bilinear rounding). Catches sRGB-curve mistakes, UV-flip bugs, extent-mismatch bugs.
- One screenshot to `.verify/shots/YYYY-MM-DD/terraindata-load.png` — date computed at runtime via `new Date().toISOString().slice(0, 10)`, never hardcoded.
- Driver runs from project root: `URL=http://localhost:5173/ node .verify/scripts/verify-terraindata.mjs`.

**Manual visual overlay:** out of scope for this spec. (Would be a debug-key HUD overlay showing the 256×256 mask; pattern of the navmask backtick toggle. Add later if it's worth it.)

## Asset / license note

`static/textures/terrainData.png` will, during development, be a literal copy of `~/Documents/Projects/folio-2025/resources/textures/terrainData.png`. This is acceptable for in-house technique study but **must be replaced** with our own painted/AI-generated version before any merge to `main`. The implementation plan must include a TODO/checkpoint for this swap and flag it in the commit message of the placeholder import.

## Open items

These are surfaced for awareness; none block this spec:

- **Loader API check.** Confirm `Loader.loadTexture` (or similar) exists during implementation. Fallback (`THREE.TextureLoader().loadAsync`) is one line.
- **Painted-PNG sub-project.** Producing our own `terrainData.png` (hand-paint vs. AI vs. auto-bootstrap-from-Blender) is deferred to its own brainstorm once the runtime is proven against Bruno's placeholder.
- **Memory update.** Per the original brief, no new memory entries until the user confirms the loader works end-to-end. The spec itself does not modify memory.
