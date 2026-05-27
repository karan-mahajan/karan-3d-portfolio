# TerrainData Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a runtime `TerrainData` module to karan-portfolio that loads a worldspace data mask (`terrainData.png`) once at boot and exposes it to both CPU consumers (bilinear sampler + threshold predicates) and GPU consumers (shader uniforms + GLSL helper). Foundation for future spike-grass / cobblestone-slab / leaves-damping sub-projects.

**Architecture:** A single PNG (R = slab/path mask, G = grass mask, B = elevation gradient) is fetched once via the existing `Loader` and held in two parallel forms: a `THREE.Texture` for shaders and a `Uint8ClampedArray` byte cache for CPU sampling. Coverage maps 1:1 to the terrain bbox (PNG UV `(0,0)` → world XZ `(-extent, -extent)`, `(1,1)` → `(+extent, +extent)`). Mirrors the shape of our existing `Wind` module so consumers integrate identically.

**Tech Stack:** Vanilla Three.js (`three@0.184`), ES modules, class syntax with `#` private fields. No TypeScript. No test runner — verification is via headless Playwright probe in `.verify/scripts/`.

**Spec reference:** [`docs/superpowers/specs/2026-05-27-terraindata-foundation-design.md`](../specs/2026-05-27-terraindata-foundation-design.md) (commit `c312d2b`).

---

## How to use this plan across multiple sessions

Each phase below is **independently startable** from a fresh Claude session. Each phase has:

- **Context preamble** (what's done; what's next; relevant project conventions) — paste verbatim into the new session.
- **Read first** — the exact files the session should load before touching anything.
- **Files** — what gets created or modified in this phase.
- **Steps** — bite-sized checkboxes.
- **Exit criteria** — proves the phase is complete.
- **Commit** — the final step.

Phases are sequential by dependency:

| # | Phase | Depends on |
|---|---|---|
| 1 | Placeholder PNG drop | — |
| 2 | Implement `src/World/TerrainData.js` | (none — pure module) |
| 3 | Wire into `App.js` | Phase 2 |
| 4 | Verify probe | Phases 1, 2, 3 |

Phases 1 and 2 can be done in either order or in parallel. Phase 3 needs Phase 2. Phase 4 needs all of 1, 2, 3.

---

## File structure

| Path | Phase | Purpose |
|---|---|---|
| `static/textures/terrainData.png` | 1 | The 256×256 RGB data mask. Served at `/textures/terrainData.png` by Vite. Placeholder = copy of Bruno's PNG; will be replaced with our own painted version in a follow-up sub-project before merge to `main`. |
| `src/World/TerrainData.js` | 2 | New runtime module. Class `TerrainData` with constructor, `load()`, `sampleAt()`, `isInWater()`, `hasGrass()`, `hasSlab()`, `uniforms` getter, static `terrainDataGLSL` getter, `dispose()`. |
| `src/App.js` | 3 | Add `import { TerrainData }`, declare `this.terrainData = null` in ctor, construct + load in `boot()` after `world.loadAssets()` resolves. Add `window.__THREE = THREE` in ctor for verify-probe GPU access. |
| `.verify/scripts/verify-terraindata.mjs` | 4 | Headless probe: boot via `bootAndDismiss`, wait for `window.__app.terrainData`, run 4 assertions (spawn-finite, far-ocean-clamp, predicate-consistency, GPU/CPU parity), screenshot to `.verify/shots/<TODAY>/terraindata-load.png`, JSON report to `.verify/shots/<TODAY>/terraindata.json`. Exits non-zero on any failure. |

No file is deleted; this is purely additive.

---

# Phase 1 — Placeholder PNG drop

### Context preamble (paste into a fresh session)

> You are implementing **Phase 1 of the TerrainData foundation** in karan-portfolio (a vanilla Three.js + Vite portfolio). Today's date is **2026-05-27**. The full plan lives at `docs/superpowers/plans/2026-05-27-terraindata-foundation-plan.md` and the spec at `docs/superpowers/specs/2026-05-27-terraindata-foundation-design.md`.
>
> **This phase only:** Copy a placeholder PNG into `static/textures/terrainData.png`. The placeholder is Bruno Simon's `terrainData.png` from his folio-2025 project (already on disk at `~/Documents/Projects/folio-2025/resources/textures/terrainData.png`). It encodes worldspace masks (R = slab paths, G = grass density, B = elevation gradient) for his world, not ours — so it must be replaced before merge to `main`. Phases 2-4 will wire the runtime against this placeholder.
>
> **Commit policy:** No `Co-Authored-By: Claude` trailer (rejected user preference, recorded in memory).
>
> **Verify sandbox:** Not invoked in this phase. (Phase 4 is the verify phase.)

### Read first

- `docs/superpowers/specs/2026-05-27-terraindata-foundation-design.md` — sections "Architecture overview" and "Asset / license note".

### Files

- **Create:** `static/textures/terrainData.png` (256×256 RGB, 11 KB — placeholder)

### Steps

- [ ] **Step 1.1 — Confirm source PNG exists**

```bash
ls -lh ~/Documents/Projects/folio-2025/resources/textures/terrainData.png
```

Expected: a single file matching `terrainData.png`, around 11 KB.

If the file is missing, stop and report — without the source there is nothing to copy. (Do not invent a substitute.)

- [ ] **Step 1.2 — Confirm destination directory exists**

```bash
ls -ld /Users/mahajankaran/Documents/Projects/karan-portfolio/static/textures
```

Expected: directory exists (it already holds `palette.png` and subfolders). If the path is missing, stop and report.

- [ ] **Step 1.3 — Copy the placeholder PNG**

```bash
cp ~/Documents/Projects/folio-2025/resources/textures/terrainData.png \
   /Users/mahajankaran/Documents/Projects/karan-portfolio/static/textures/terrainData.png
```

- [ ] **Step 1.4 — Verify the file landed and has the expected dimensions**

```bash
file /Users/mahajankaran/Documents/Projects/karan-portfolio/static/textures/terrainData.png
```

Expected: `PNG image data, 256 x 256, 8-bit/color RGB, non-interlaced`.

If the dimensions are not 256×256 RGB, stop and report — the runtime spec (and Phase 2 code) assumes exactly that shape.

- [ ] **Step 1.5 — Verify the dev server can serve it**

(Optional but quick.) If the dev server is running (`npm run dev`), open `http://localhost:5173/textures/terrainData.png` in a browser. It should display as a small image. If not running, skip — Phase 4 will exercise this end-to-end.

- [ ] **Step 1.6 — Commit**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git add static/textures/terrainData.png
git commit -m "$(cat <<'EOF'
terrainData: drop placeholder PNG from folio-2025

256x256 RGB; R=slab/path mask, G=grass mask, B=elevation gradient.
This is Bruno Simon's terrainData.png from his folio-2025 project,
used as a development placeholder while we wire the TerrainData
runtime (src/World/TerrainData.js, Phase 2). The mask layout reflects
HIS world geometry (river curve, his section placements), so visuals
through this PNG will be wrong until we paint our own.

TODO: replace with our own painted/AI-generated terrainData.png
before merging this branch to main. Spec:
docs/superpowers/specs/2026-05-27-terraindata-foundation-design.md
EOF
)"
```

### Exit criteria

- `static/textures/terrainData.png` exists, is 256×256 RGB, ~11 KB.
- Commit message includes the TODO flagging it for replacement.
- No other files modified.

---

# Phase 2 — Implement `src/World/TerrainData.js`

### Context preamble (paste into a fresh session)

> You are implementing **Phase 2 of the TerrainData foundation** in karan-portfolio (a vanilla Three.js + Vite portfolio). Today's date is **2026-05-27**. The full plan lives at `docs/superpowers/plans/2026-05-27-terraindata-foundation-plan.md` and the spec at `docs/superpowers/specs/2026-05-27-terraindata-foundation-design.md`.
>
> **What's done:** Phase 1 dropped the placeholder PNG at `static/textures/terrainData.png` (256×256 RGB). It encodes R = slab mask, G = grass mask, B = elevation. (Optional — Phase 2 can be coded purely from the spec without that file present; verification needs it but the code does not.)
>
> **This phase only:** Implement the runtime module `src/World/TerrainData.js`. Class `TerrainData` exposes both CPU access (bilinear `sampleAt(x, z)` + threshold predicates) and GPU access (`uniforms` + static `terrainDataGLSL`). It does NOT wire into App.js (that's Phase 3) and there is NO consumer yet — the module is self-contained.
>
> **Project conventions (CLAUDE.md):**
> - Vanilla ES modules, `class` syntax, `#` private fields. NO TypeScript.
> - Comments only when the WHY is non-obvious — never restate what code does.
> - Mirror the shape of `src/World/Wind.js`: small focused class, `uniforms` object as instance state, static getter for the GLSL snippet, JSDoc summary on the class.
> - Do not add error handling for scenarios that cannot happen. Validate inputs only at system boundaries; trust internal callers.
>
> **No test runner** in this project. Phase 4 (the verify probe) is the integration test. Smoke-checking in Phase 2 is done by inspection + the next-phase wiring, not by a Node test runner.
>
> **Commit policy:** No `Co-Authored-By: Claude` trailer.

### Read first

- `docs/superpowers/specs/2026-05-27-terraindata-foundation-design.md` — sections "Module API", "UV coverage convention", "CPU sampler", "GLSL helper".
- `src/World/Wind.js` — the existing pattern this module mirrors (shape of `uniforms`, static GLSL getter).
- `src/Utils/Loader.js` — confirm `Loader.loadTexture(url)` returns `Promise<THREE.Texture>` (it does; line 57).
- `src/World/GlbWorld.js:317-334` — the bilinear-sample pattern for `heightAt`. The new sampler follows the same clamping + lerp structure.

### Files

- **Create:** `src/World/TerrainData.js`

### Steps

- [ ] **Step 2.1 — Write the module**

Create `/Users/mahajankaran/Documents/Projects/karan-portfolio/src/World/TerrainData.js` with this exact content:

```js
import * as THREE from 'three';

/**
 * Worldspace data mask loaded from a single 256x256 RGB PNG.
 *
 * Channels:
 *   R - slab / cobblestone path mask
 *   G - grass density / hidden mask (Bruno's `g < 0.4` => hide)
 *   B - elevation gradient (0 = deep water, 1 = high ground)
 *
 * UV convention: PNG (0,0) -> world XZ (-extent, -extent), (1,1) -> (+extent, +extent).
 * The PNG covers the entire terrain bbox 1:1; samples outside clamp to the edge.
 *
 * Two parallel forms held after load():
 *   - THREE.Texture for shaders (consumers spread `uniforms` into their material).
 *   - Uint8ClampedArray byte cache for CPU sampling (Footprints, Discovery, etc.).
 *
 * Treat the PNG as a *data* texture: NoColorSpace, LinearFilter, ClampToEdge.
 * The sRGB encoding on disk is for editor convenience; we read raw 0..255 bytes.
 */
export class TerrainData {
  static URL = '/textures/terrainData.png';
  static WIDTH = 256;
  static HEIGHT = 256;

  // Bruno's threshold pivots, citing folio-2025 source:
  //   - isInWater: Leaves.js:246 remap pivot (0.02, 0.13)
  //   - hasGrass:  Grass.js:126  step(g - 0.4, 0.1)
  // hasSlab is a chosen midpoint; tunable when the first slab consumer wires up.
  static WATER_THRESHOLD = 0.13;
  static GRASS_THRESHOLD = 0.4;
  static SLAB_THRESHOLD = 0.5;

  #pixels = null;          // Uint8ClampedArray, 256*256*4
  #texture = null;         // THREE.Texture
  #uniforms = null;        // { uTerrainData, uTerrainDataExtent }
  #extent;                 // terrain bbox half-extent in meters

  constructor({ extent } = {}) {
    if (!Number.isFinite(extent) || extent <= 0) {
      throw new Error(`TerrainData: extent must be a positive number, got ${extent}`);
    }
    this.#extent = extent;
    this.#uniforms = {
      uTerrainData: { value: null },
      uTerrainDataExtent: { value: extent },
    };
  }

  get extent() { return this.#extent; }

  /**
   * Fetch + decode the PNG. Builds the THREE.Texture AND the CPU byte cache.
   * Idempotent on re-call — returns the same instance state.
   *
   * @param {import('../Utils/Loader.js').Loader} loader — used for unified progress reporting.
   */
  async load(loader) {
    if (this.#texture) return;

    const texture = await loader.loadTexture(TerrainData.URL);

    texture.wrapS = THREE.ClampToEdgeWrapping;
    texture.wrapT = THREE.ClampToEdgeWrapping;
    texture.magFilter = THREE.LinearFilter;
    texture.minFilter = THREE.LinearFilter;
    // Data texture, not color: raw bytes -> 0..1 floats with no sRGB curve.
    texture.colorSpace = THREE.NoColorSpace;
    texture.generateMipmaps = false;
    texture.needsUpdate = true;

    this.#pixels = await this.#extractPixels(texture);
    this.#texture = texture;
    this.#uniforms.uTerrainData.value = texture;
  }

  /**
   * Bilinear CPU sample. Returns { r, g, b } floats in [0, 1].
   * About 25 ops per call — fine for handfuls of CPU consumers per frame,
   * NOT fine for per-vertex grass work (use the GPU path for that).
   */
  sampleAt(worldX, worldZ) {
    const px = this.#pixels;
    if (!px) {
      throw new Error('TerrainData.sampleAt() called before load() completed');
    }
    const W = TerrainData.WIDTH, H = TerrainData.HEIGHT;
    const u = (worldX / (2 * this.#extent) + 0.5) * (W - 1);
    const v = (worldZ / (2 * this.#extent) + 0.5) * (H - 1);
    const u0 = clampInt(Math.floor(u), 0, W - 1);
    const u1 = clampInt(u0 + 1, 0, W - 1);
    const v0 = clampInt(Math.floor(v), 0, H - 1);
    const v1 = clampInt(v0 + 1, 0, H - 1);
    const tu = clamp01(u - u0);
    const tv = clamp01(v - v0);

    const i00 = (v0 * W + u0) * 4;
    const i10 = (v0 * W + u1) * 4;
    const i01 = (v1 * W + u0) * 4;
    const i11 = (v1 * W + u1) * 4;

    const r = bilerp(px[i00], px[i10], px[i01], px[i11], tu, tv) / 255;
    const g = bilerp(px[i00 + 1], px[i10 + 1], px[i01 + 1], px[i11 + 1], tu, tv) / 255;
    const b = bilerp(px[i00 + 2], px[i10 + 2], px[i01 + 2], px[i11 + 2], tu, tv) / 255;

    return { r, g, b };
  }

  isInWater(worldX, worldZ) {
    return this.sampleAt(worldX, worldZ).b < TerrainData.WATER_THRESHOLD;
  }

  hasGrass(worldX, worldZ) {
    return this.sampleAt(worldX, worldZ).g > TerrainData.GRASS_THRESHOLD;
  }

  hasSlab(worldX, worldZ) {
    return this.sampleAt(worldX, worldZ).r > TerrainData.SLAB_THRESHOLD;
  }

  /**
   * Reference-shared across every material that uses this mask. Updating
   * one consumer's uniform updates them all. Matches `Wind.uniforms` today.
   */
  get uniforms() { return this.#uniforms; }

  /**
   * Drop into any shader's vertex or fragment GLSL after `#include <common>`:
   *
   *   shader.vertexShader = shader.vertexShader.replace(
   *     '#include <common>',
   *     `#include <common>\n${TerrainData.terrainDataGLSL}`,
   *   );
   *
   * The consumer must compute `worldXZ` (e.g. `(modelMatrix * vec4(position, 1.0)).xz`)
   * before calling the helpers. `texture2D` is GLSL 1.0 — three @ 0.184 emits
   * GLSL 1.0 in ShaderChunks today; revisit if we upgrade to GLSL 3.0.
   */
  static get terrainDataGLSL() {
    return /* glsl */ `
      uniform sampler2D uTerrainData;
      uniform float     uTerrainDataExtent;

      vec3 terrainDataAt(vec2 worldXZ) {
        vec2 uv = worldXZ / (2.0 * uTerrainDataExtent) + 0.5;
        return texture2D(uTerrainData, uv).rgb;
      }

      float terrainGrass(vec2 worldXZ)     { return terrainDataAt(worldXZ).g; }
      float terrainSlab(vec2 worldXZ)      { return terrainDataAt(worldXZ).r; }
      float terrainElevation(vec2 worldXZ) { return terrainDataAt(worldXZ).b; }
    `;
  }

  dispose() {
    if (this.#texture) {
      this.#texture.dispose();
      this.#texture = null;
    }
    this.#pixels = null;
    this.#uniforms.uTerrainData.value = null;
  }

  /**
   * Decode a THREE.Texture's image into a Uint8ClampedArray of RGBA bytes.
   * Uses OffscreenCanvas when available; falls back to HTMLCanvasElement
   * so SSR / older browsers still work. The canvas is discarded; only
   * the bytes are retained.
   */
  async #extractPixels(texture) {
    const img = texture.image;
    if (!img) {
      throw new Error('TerrainData: loaded texture has no .image — Loader behavior changed?');
    }
    const W = TerrainData.WIDTH, H = TerrainData.HEIGHT;
    if (img.width !== W || img.height !== H) {
      throw new Error(
        `TerrainData: PNG must be ${W}x${H}, got ${img.width}x${img.height}`);
    }
    let canvas, ctx;
    if (typeof OffscreenCanvas !== 'undefined') {
      canvas = new OffscreenCanvas(W, H);
      ctx = canvas.getContext('2d', { willReadFrequently: true });
    } else {
      canvas = document.createElement('canvas');
      canvas.width = W;
      canvas.height = H;
      ctx = canvas.getContext('2d', { willReadFrequently: true });
    }
    ctx.drawImage(img, 0, 0);
    return ctx.getImageData(0, 0, W, H).data;
  }
}

function clampInt(v, lo, hi) {
  return v < lo ? lo : v > hi ? hi : v;
}

function clamp01(v) {
  return v < 0 ? 0 : v > 1 ? 1 : v;
}

function bilerp(a00, a10, a01, a11, tu, tv) {
  const a0 = a00 * (1 - tu) + a10 * tu;
  const a1 = a01 * (1 - tu) + a11 * tu;
  return a0 * (1 - tv) + a1 * tv;
}
```

- [ ] **Step 2.2 — Lint check via build**

Run a build to confirm the file parses and resolves all imports:

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
npm run build
```

Expected: build succeeds (the new file is unreferenced, so the unused-warning may surface, but the build should not fail).

If the build fails with a syntax / import error, fix inline. If it fails with an unrelated error (existing broken file), stop and report — Phase 2's job is the new module, not pre-existing breakage.

- [ ] **Step 2.3 — Commit**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git add src/World/TerrainData.js
git commit -m "$(cat <<'EOF'
terrainData: runtime module — CPU sampler + GLSL helper

New class TerrainData (src/World/TerrainData.js) that loads
static/textures/terrainData.png and exposes:
  - sampleAt(x, z) -> {r,g,b}  bilinear CPU sample
  - isInWater / hasGrass / hasSlab  threshold predicates
  - uniforms  { uTerrainData, uTerrainDataExtent } for shaders
  - static terrainDataGLSL  drop-in shader helper

Mirrors the Wind.js shape so future grass / slab / leaves
consumers integrate identically. Module is unreferenced
until Phase 3 wires it into App.boot().

Spec: docs/superpowers/specs/2026-05-27-terraindata-foundation-design.md
EOF
)"
```

### Exit criteria

- `src/World/TerrainData.js` exists, ~150 lines.
- `npm run build` succeeds.
- Module is not yet imported anywhere; that happens in Phase 3.

---

# Phase 3 — Wire into `src/App.js`

### Context preamble (paste into a fresh session)

> You are implementing **Phase 3 of the TerrainData foundation** in karan-portfolio (a vanilla Three.js + Vite portfolio). Today's date is **2026-05-27**. The full plan lives at `docs/superpowers/plans/2026-05-27-terraindata-foundation-plan.md`.
>
> **What's done:**
> - Phase 1 placed `static/textures/terrainData.png` (256×256 RGB placeholder, Bruno's).
> - Phase 2 created `src/World/TerrainData.js` — the runtime class with `load(loader)`, `sampleAt`, predicates, `uniforms`, static GLSL getter.
>
> **This phase only:** Wire `TerrainData` into `src/App.js`. Three small edits:
>   1. Import the class.
>   2. Declare `this.terrainData = null` in the constructor.
>   3. After `world.loadAssets()` resolves inside `boot()`, construct + load it.
>   4. Also add `window.__THREE = THREE` in the constructor — a one-line dev hook used by the Phase 4 verify probe to access THREE without a separate import. Matches the existing `window.__app` / `window.__quality` pattern.
>
> Do NOT add any per-frame `update()` call (the texture is static). Do NOT add any consumer code (downstream sub-projects handle that).
>
> **Project conventions:**
> - Vanilla ES modules, `class` syntax, `#` private fields. NO TypeScript.
> - Comments only when the WHY is non-obvious.
> - No `Co-Authored-By: Claude` trailer in commits.

### Read first

- `docs/superpowers/specs/2026-05-27-terraindata-foundation-design.md` — section "Wiring + bootstrapping".
- `src/App.js:1-80` — constructor head (where `window.__quality` is set, line 59; where `this.water = null` style declarations live, lines 76-91).
- `src/App.js:300-340` — `boot()`'s post-world-load block (where `this.water = this.world.water` is grabbed, around line 329). This is the insertion point.
- `src/World/TerrainData.js` (Phase 2 output) — confirm the constructor signature `new TerrainData({ extent })` and `load(loader)`.

### Files

- **Modify:** `src/App.js` — three small additions, no removals.

### Steps

- [ ] **Step 3.1 — Add the import**

Open `src/App.js`. Find the existing imports block (top of file, ends around line 45). Add this import alphabetically among the `./World/*` imports — it sits between `./World/Sun.js` and `./World/TimeOfDay.js`:

Find:
```js
import { Sun } from './World/Sun.js';
import { TimeOfDay, detectAutoMode } from './World/TimeOfDay.js';
```

Replace with:
```js
import { Sun } from './World/Sun.js';
import { TerrainData } from './World/TerrainData.js';
import { TimeOfDay, detectAutoMode } from './World/TimeOfDay.js';
```

- [ ] **Step 3.2 — Expose THREE on window (verify-probe hook)**

In the constructor, find the existing `window.__quality` line (around line 59):

```js
    this.quality = detectQuality();
    window.__quality = this.quality;
```

Replace with:
```js
    this.quality = detectQuality();
    window.__quality = this.quality;
    // Dev hook for .verify probes — lets headless tests build ShaderMaterials
    // and read render targets without importing three from outside the bundle.
    window.__THREE = THREE;
```

- [ ] **Step 3.3 — Declare the field in the constructor**

In the constructor, find the block where peer fields are declared as `null` (around lines 76-91). It looks like:

```js
    this.player = null;
    this.discovery = null;
    this.miniMap = null;
    this.mapOverlay = null;
    this.navmask = null;
    this.clickToMove = null;
    this.teleport = null;
    this.transitionFx = null;
```

Add `this.terrainData = null;` after `this.transitionFx = null;`:

Find:
```js
    this.transitionFx = null;
```

Replace with:
```js
    this.transitionFx = null;
    // Populated in boot() after world.loadAssets() — extent depends on
    // terrain.size which is only known once the GLB is parsed.
    this.terrainData = null;
```

- [ ] **Step 3.4 — Construct + load inside `boot()`**

Find the post-world-load block in `boot()` (around lines 325-345 — the `this.water = this.world.water;` block):

```js
    // Water is built inside world.loadAssets so its exclusions feed Nature.
    // Hook it up to the rain (pond ripple footprint) and TimeOfDay (day/
    // night tint). The grass field consumes its exclusion list below in the
    // grass.load() call.
    this.water = this.world.water;
    if (this.water) {
      this.timeOfDay.water = this.water;
      this.timeOfDay.reapply();
      // Give Water a handle on AudioManager so wading triggers WAV splashes
      // (entry one-shot + per-step variant). See Water.update.
      this.water.audio = this.audio;
      if (this.water.mesh) this.water.mesh.userData.noTorchRaycast = true;
    }
```

Append immediately after that block:

```js

    // TerrainData mask — drives future grass hidden-mask, slab shader,
    // leaves water-damping. Awaited here so any downstream construction
    // in the rest of boot() can safely depend on it.
    this.terrainData = new TerrainData({ extent: this.world.terrain.size / 2 });
    await this.terrainData.load(this.loader);
```

(The blank line before the comment matches the file's existing spacing between blocks. Keep the trailing `\n`.)

- [ ] **Step 3.5 — Build check**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
npm run build
```

Expected: succeeds. If it fails, the import path or syntax is off — fix inline.

- [ ] **Step 3.6 — Manual smoke check via dev server**

Start the dev server in another terminal:

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
npm run dev
```

Open `http://localhost:5173/`. Once the welcome overlay appears (or you've clicked Start), open the browser console and run:

```js
await window.__app.terrainData.sampleAt(0, 0)
```

Expected: an object `{ r: <number 0..1>, g: <number 0..1>, b: <number 0..1> }`. The exact values depend on Bruno's placeholder PNG; the important thing is finite numbers in range.

Also check:
```js
window.__app.terrainData.uniforms.uTerrainData.value
```

Expected: a `THREE.Texture` instance (not `null`).

If `terrainData` is `null` on `window.__app`, the construction in `boot()` didn't run — check the await chain and that `world.loadAssets()` resolves successfully. If `sampleAt` throws, the load completed but extraction failed — check the OffscreenCanvas path.

Stop the dev server when done.

- [ ] **Step 3.7 — Commit**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git add src/App.js
git commit -m "$(cat <<'EOF'
terrainData: wire into App.boot()

Constructs TerrainData with extent = world.terrain.size / 2 once
loadAssets resolves and awaits load() before continuing boot.
Also exposes window.__THREE so verify probes can build
ShaderMaterials without a separate three import.

No consumers yet — pure foundation. Downstream grass / slab /
leaves sub-projects will read app.terrainData.uniforms and call
its CPU predicates.

Spec: docs/superpowers/specs/2026-05-27-terraindata-foundation-design.md
EOF
)"
```

### Exit criteria

- `npm run build` succeeds.
- In the dev-server browser console, `window.__app.terrainData.sampleAt(0, 0)` returns an `{r, g, b}` object with finite numbers in `[0, 1]`.
- `window.__app.terrainData.uniforms.uTerrainData.value` is a `THREE.Texture` (not null).
- `window.__THREE` is the `THREE` namespace.

---

# Phase 4 — Verify probe

### Context preamble (paste into a fresh session)

> You are implementing **Phase 4 of the TerrainData foundation** in karan-portfolio (a vanilla Three.js + Vite portfolio). Today's date is **2026-05-27**. The full plan lives at `docs/superpowers/plans/2026-05-27-terraindata-foundation-plan.md`.
>
> **What's done:**
> - Phase 1: placeholder PNG at `static/textures/terrainData.png`.
> - Phase 2: `src/World/TerrainData.js` runtime module.
> - Phase 3: wired into `App.js`. `window.__app.terrainData` is populated post-boot. `window.__THREE` is the THREE namespace.
>
> **This phase only:** Write `.verify/scripts/verify-terraindata.mjs`. It boots the dev server in headless Chromium, dismisses the welcome overlay, and runs four assertions:
>   1. **Spawn finite** — `sampleAt(0, 0)` returns three finite numbers in `[0, 1]`.
>   2. **Far ocean clamp** — `isInWater(120, 120) === true` (outside terrain bbox, edge-clamps to a low-elevation reading).
>   3. **Predicate consistency** — for a deterministic 16-point grid, `hasGrass / hasSlab / isInWater` agree with `sampleAt + threshold`.
>   4. **GPU/CPU parity** — render `terrainDataAt(testXZ)` to a 1×1 render target via a `ShaderMaterial`, read back, compare to `sampleAt(testXZ)`. Tolerance ±2/255 per channel.
>
> A screenshot goes to `.verify/shots/<TODAY>/terraindata-load.png`. A JSON report goes to `.verify/shots/<TODAY>/terraindata.json`. Probe exits non-zero on any failure.
>
> **Project conventions (CLAUDE.md "Verification sandbox"):**
> - Live under `.verify/scripts/`. Shots under `.verify/shots/<YYYY-MM-DD>/`. NEVER hardcode the date — compute via `new Date().toISOString().slice(0, 10)` at runtime.
> - Use `bootAndDismiss(page)` from `.verify/scripts/_boot.mjs`. NEVER inline a dismissal loop.
> - Playwright is not a project dep. The user runs probes with `NODE_PATH=/tmp/node_modules` (already set up). The probe just `import { chromium } from 'playwright'`.
> - Dev server must be running in another terminal (`npm run dev`).
>
> **No `Co-Authored-By: Claude` trailer in commits.**

### Read first

- `docs/superpowers/specs/2026-05-27-terraindata-foundation-design.md` — section "Verification plan".
- `.verify/scripts/_boot.mjs` — confirms the `bootAndDismiss(page)` signature.
- `.verify/scripts/verify-foliage.mjs` — closest existing pattern. Crib the chromium boot + report-JSON shape.
- `src/World/TerrainData.js` (Phase 2) — confirm the exact uniform names and `static terrainDataGLSL` signature.

### Files

- **Create:** `.verify/scripts/verify-terraindata.mjs`

### Steps

- [ ] **Step 4.1 — Write the probe**

Create `/Users/mahajankaran/Documents/Projects/karan-portfolio/.verify/scripts/verify-terraindata.mjs` with this exact content:

```js
// Probes the TerrainData foundation: PNG load, CPU bilinear sampler,
// threshold predicates, GPU/CPU parity. The dev server must already be
// running on http://localhost:5173/ (see CLAUDE.md "Verification sandbox").
//
// Usage:
//   1. npm run dev   (in another shell)
//   2. URL=http://localhost:5173/ node .verify/scripts/verify-terraindata.mjs
//
// Exits non-zero on any failed assertion.

import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { bootAndDismiss } from './_boot.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const URL = process.env.URL || 'http://localhost:5173/';
const TODAY = new Date().toISOString().slice(0, 10);
const SHOTS = path.resolve(__dirname, '..', 'shots', TODAY);
fs.mkdirSync(SHOTS, { recursive: true });

const browser = await chromium.launch({ headless: true });
const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
const page = await ctx.newPage();

const logs = [];
const errors = [];
page.on('console', (m) => logs.push(`[${m.type()}] ${m.text()}`));
page.on('pageerror', (e) => errors.push(`PAGEERROR: ${e.message}`));
page.on('requestfailed', (r) =>
  errors.push(`REQFAIL: ${r.url()} ${r.failure()?.errorText}`));

console.log(`→ goto ${URL}`);
await page.goto(URL, { waitUntil: 'load', timeout: 30000 });

console.log('→ boot + dismiss welcome');
await bootAndDismiss(page);

// Wait for TerrainData.load() to have completed (texture present + non-null).
console.log('→ wait for TerrainData to be loaded');
await page.waitForFunction(
  () => !!(
    window.__app &&
    window.__app.terrainData &&
    window.__app.terrainData.uniforms?.uTerrainData?.value
  ),
  null,
  { timeout: 15000 },
);

console.log('→ run assertions in page context');
const result = await page.evaluate(async () => {
  const failures = [];
  const app = window.__app;
  const THREE = window.__THREE;
  if (!app || !app.terrainData) {
    return { failures: ['app.terrainData missing in page context'] };
  }
  if (!THREE) {
    return { failures: ['window.__THREE missing — Phase 3 wiring incomplete'] };
  }
  const td = app.terrainData;

  // ── Assertion 1 — spawn point returns finite numbers in [0,1] ──
  const s0 = td.sampleAt(0, 0);
  const finiteIn01 = (x) => Number.isFinite(x) && x >= 0 && x <= 1;
  if (!finiteIn01(s0.r) || !finiteIn01(s0.g) || !finiteIn01(s0.b)) {
    failures.push(`A1 spawn sample out of [0,1]: ${JSON.stringify(s0)}`);
  }

  // ── Assertion 2 — far ocean (outside terrain bbox) clamps to in-water ──
  if (!td.isInWater(120, 120)) {
    const sFar = td.sampleAt(120, 120);
    failures.push(`A2 far ocean not in water: b=${sFar.b}`);
  }

  // ── Assertion 3 — threshold predicates consistent with sampleAt ──
  // Seeded RNG so probe is deterministic across runs.
  let s = 0xbada55 >>> 0;
  const rng = () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  const ext = td.extent;
  for (let i = 0; i < 16; i++) {
    const x = (rng() * 2 - 1) * ext;
    const z = (rng() * 2 - 1) * ext;
    const sample = td.sampleAt(x, z);
    if (td.hasGrass(x, z) !== (sample.g > 0.4)) {
      failures.push(`A3 hasGrass mismatch at (${x.toFixed(2)},${z.toFixed(2)})`);
    }
    if (td.hasSlab(x, z) !== (sample.r > 0.5)) {
      failures.push(`A3 hasSlab mismatch at (${x.toFixed(2)},${z.toFixed(2)})`);
    }
    if (td.isInWater(x, z) !== (sample.b < 0.13)) {
      failures.push(`A3 isInWater mismatch at (${x.toFixed(2)},${z.toFixed(2)})`);
    }
  }

  // ── Assertion 4 — GPU/CPU parity at one test point ──
  // Build a 1x1 render target + ShaderMaterial that emits terrainDataAt(testXZ).
  // The shader uses TerrainData.terrainDataGLSL verbatim, the same string
  // future consumers will splice into their materials.
  const renderer = app.renderer;
  if (!renderer) {
    failures.push('A4 renderer not exposed on app — cannot run GPU/CPU parity');
    return { failures, sample0: s0 };
  }
  const testX = 10.0, testZ = -5.0;
  const rt = new THREE.WebGLRenderTarget(1, 1, {
    format: THREE.RGBAFormat,
    type: THREE.UnsignedByteType,
    minFilter: THREE.NearestFilter,
    magFilter: THREE.NearestFilter,
  });
  const mat = new THREE.ShaderMaterial({
    uniforms: {
      uTerrainData: td.uniforms.uTerrainData,
      uTerrainDataExtent: td.uniforms.uTerrainDataExtent,
      uTestXZ: { value: new THREE.Vector2(testX, testZ) },
    },
    vertexShader: `
      void main() { gl_Position = vec4(position, 1.0); }
    `,
    fragmentShader: `
      ${td.constructor.terrainDataGLSL}
      uniform vec2 uTestXZ;
      void main() {
        gl_FragColor = vec4(terrainDataAt(uTestXZ), 1.0);
      }
    `,
  });
  const geom = new THREE.BufferGeometry();
  geom.setAttribute('position', new THREE.Float32BufferAttribute(
    [-1, -1, 0,  3, -1, 0,  -1, 3, 0], 3));
  const quad = new THREE.Mesh(geom, mat);
  const tmpScene = new THREE.Scene();
  tmpScene.add(quad);
  const tmpCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

  const prevRT = renderer.getRenderTarget();
  renderer.setRenderTarget(rt);
  renderer.render(tmpScene, tmpCam);
  renderer.setRenderTarget(prevRT);

  const buf = new Uint8Array(4);
  renderer.readRenderTargetPixels(rt, 0, 0, 1, 1, buf);
  const gpu = { r: buf[0] / 255, g: buf[1] / 255, b: buf[2] / 255 };
  const cpu = td.sampleAt(testX, testZ);
  const tol = 2 / 255;
  if (
    Math.abs(gpu.r - cpu.r) > tol ||
    Math.abs(gpu.g - cpu.g) > tol ||
    Math.abs(gpu.b - cpu.b) > tol
  ) {
    failures.push(
      `A4 GPU/CPU parity mismatch at (${testX},${testZ}): ` +
      `gpu=${JSON.stringify(gpu)} cpu=${JSON.stringify(cpu)} tol=${tol}`,
    );
  }

  rt.dispose();
  mat.dispose();
  geom.dispose();

  return { failures, sample0: s0, gpu, cpu };
});

console.log('→ result:', JSON.stringify(result, null, 2));

console.log('→ screenshot');
await page.screenshot({ path: `${SHOTS}/terraindata-load.png` });

await browser.close();

const report = {
  url: URL,
  shots_dir: SHOTS,
  today: TODAY,
  result,
  errors,
  console_warnings: logs
    .filter((l) => /terrain|warn|error|shader/i.test(l))
    .slice(0, 60),
};
fs.writeFileSync(`${SHOTS}/terraindata.json`, JSON.stringify(report, null, 2));
console.log(`→ report: ${SHOTS}/terraindata.json`);

if (result.failures.length > 0 || errors.length > 0) {
  console.error('FAILED');
  console.error('  assertion failures:', result.failures);
  console.error('  page errors:', errors);
  process.exit(1);
}
console.log('OK — all assertions passed');
```

- [ ] **Step 4.2 — Start the dev server in another terminal**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
npm run dev
```

Confirm Vite reports `Local: http://localhost:5173/`. Leave this running for the rest of Phase 4.

- [ ] **Step 4.3 — Confirm Playwright is reachable**

Probes use the globally-installed Playwright. From a fresh terminal:

```bash
node -e "import('playwright').then(p => console.log('playwright ok:', !!p.chromium))" 2>&1
```

If this prints `playwright ok: true`, you're set. If it prints `Cannot find package 'playwright'`, install once into `/tmp` per CLAUDE.md:

```bash
cd /tmp && npm install --no-save playwright && npx playwright install chromium
```

Then re-test with:

```bash
NODE_PATH=/tmp/node_modules node -e "import('playwright').then(p => console.log('ok:', !!p.chromium))" 2>&1
```

Use whichever invocation worked when running the probe in Step 4.4.

- [ ] **Step 4.4 — Run the probe**

From the project root (NOT from `.verify/`):

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
URL=http://localhost:5173/ node .verify/scripts/verify-terraindata.mjs
```

Or, if Playwright is only globally installed:

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
URL=http://localhost:5173/ NODE_PATH=/tmp/node_modules \
  node .verify/scripts/verify-terraindata.mjs
```

Expected final line: `OK — all assertions passed`.

Expected outputs (the date directory is computed at runtime):
- `.verify/shots/<TODAY>/terraindata-load.png` — a screenshot of the booted world
- `.verify/shots/<TODAY>/terraindata.json` — the assertion report

If the probe fails:

| Failure | Likely cause | Fix |
|---|---|---|
| `app.terrainData missing` | Phase 3 wiring didn't take | Re-verify Step 3.4; check await order in `boot()`. |
| `window.__THREE missing` | Step 3.2 not applied | Add the line in App.js ctor. |
| `A1 spawn sample out of [0,1]` | PNG decoded with wrong colorSpace | Check `texture.colorSpace = THREE.NoColorSpace` in `TerrainData.load`. |
| `A2 far ocean not in water` | PNG edge values are not low-elevation | Open `static/textures/terrainData.png`; if the corners are NOT dark, Bruno's PNG has been overwritten — restore from Phase 1 source. |
| `A3 *Mismatch` | Predicate threshold drift | Compare the constants in `TerrainData.js` against the spec table. |
| `A4 GPU/CPU parity mismatch` | sRGB curve on the texture, UV flip, or extent mismatch | Check `colorSpace = NoColorSpace` (sRGB); confirm extent uniform matches `terrain.size / 2`. |
| Probe hangs at boot | Welcome overlay not dismissing | `bootAndDismiss` already throws if welcome is stuck — check the dev server console for App.boot() errors. |

- [ ] **Step 4.5 — Open the screenshot for sanity**

```bash
open /Users/mahajankaran/Documents/Projects/karan-portfolio/.verify/shots/$(date +%Y-%m-%d)/terraindata-load.png
```

Expected: the booted world from the default spawn camera, no overlay covering it. (The image content doesn't validate the TerrainData mask itself — there are no consumers yet — but it confirms the boot path reached steady state.)

- [ ] **Step 4.6 — Commit**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git add .verify/scripts/verify-terraindata.mjs
git commit -m "$(cat <<'EOF'
terrainData: verify probe — load + sampler + GPU/CPU parity

Headless Playwright probe that boots the world, waits for
app.terrainData to be populated, and runs:
  - spawn sample finite-and-in-range
  - far ocean (out-of-bbox) clamps to in-water
  - threshold predicates consistent with sampleAt
  - GPU/CPU parity: render terrainDataAt() to a 1x1 RT and
    compare to sampleAt() within ±2/255 per channel

Exits non-zero on any failure; writes report JSON + screenshot
to .verify/shots/<YYYY-MM-DD>/.

Spec: docs/superpowers/specs/2026-05-27-terraindata-foundation-design.md
EOF
)"
```

### Exit criteria

- `.verify/scripts/verify-terraindata.mjs` runs to completion and prints `OK — all assertions passed`.
- `.verify/shots/<TODAY>/terraindata-load.png` exists.
- `.verify/shots/<TODAY>/terraindata.json` exists with `failures: []` and `errors: []`.
- All four assertions documented as passing in the JSON report.

---

## After all four phases complete

- The TerrainData foundation is wired and verified.
- There are still **no visual consumers**. The next sub-projects (spike-grass port, Bruno-style slab shader, leaves water-damping) each get their own brainstorm → spec → plan cycle.
- The placeholder `static/textures/terrainData.png` (Bruno's) MUST be replaced before merge to `main`. That replacement is a separate sub-project (author our own painted/AI-generated mask; brainstorm deferred).
- Memory update is appropriate only AFTER the user confirms the runtime works end-to-end (per the original brief). Suggested entries when that happens:
  - `project_terraindata_runtime.md` — "TerrainData mask module added 2026-05-27; placeholder = Bruno's PNG, replace before merge."
  - `reference_brunos_data_textures.md` — "Bruno encodes world layout in 256×256 RGB PNG: R=slab, G=grass, B=elevation. Sampled via worldspace UV. Foundation for grass / slab / leaves systems."

---

## Plan self-review

Coverage of spec (`docs/superpowers/specs/2026-05-27-terraindata-foundation-design.md`):

| Spec section | Plan coverage |
|---|---|
| Module API | Phase 2, Step 2.1 (full class verbatim) |
| UV coverage convention | Phase 2, Step 2.1 (`/ (2 * extent) + 0.5` in both CPU + GLSL paths); texture settings applied in `load()` |
| CPU sampler | Phase 2, Step 2.1 (`#extractPixels` + `sampleAt` + helpers) |
| GLSL helper | Phase 2, Step 2.1 (`static get terrainDataGLSL`) |
| Wiring + bootstrapping | Phase 3 (steps 3.1, 3.3, 3.4) |
| Verification plan | Phase 4 (all four assertions, screenshot, JSON report) |
| Asset / license note | Phase 1 commit message includes the replace-before-merge TODO |
| Open item: Loader API | Resolved during writing — `loadTexture()` confirmed in `src/Utils/Loader.js:57`. Plan uses it directly. |

Type / name consistency: `TerrainData` class name, `uTerrainData` + `uTerrainDataExtent` uniform names, `terrainDataAt` / `terrainGrass` / `terrainSlab` / `terrainElevation` GLSL helper names — all match across Phase 2 module, Phase 3 wiring, Phase 4 probe.

Placeholder scan: no TBD, no "implement later", no "similar to Task N", no vague "add error handling" — all code provided verbatim.

Scope: focused on foundation only. Non-goals from the spec (downstream sub-projects, our own painted PNG, CPU-call migrations) are explicitly listed as out-of-scope under "After all four phases complete."
