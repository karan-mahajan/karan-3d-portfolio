# World v2 runtime integration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the procedural Terrain/Nature/Paths/DistantIslands runtime with a single `GlbWorld` loader that consumes `static/world/world.glb` as the source of truth, and adapt Signs/Billboards/StreetLights/Water to mount onto the Blender-authored meshes and refs.

**Architecture:** Single GLB load at boot → scene-graph walk produces 5 buckets (terrain heightfield, named colliders, ref empties, material-token meshes, push-spots). New facade `World.js` preserves the public API (`world.terrain.heightAt`, `world.nature.pushSpots`, `world.paths.getTilePositions`, `world.signs`, `world.billboards`) so 18 downstream consumers don't need edits. Old procedural modules deleted phase-by-phase as their replacements verify.

**Tech Stack:** vanilla ES modules, `class` syntax with `#` private fields, three@0.184 (`GLTFLoader` + `DRACOLoader` + `KTX2Loader` already wired in `src/Utils/Loader.js`), `@dimforge/rapier3d-compat@0.12`, `vite@8`. No TypeScript. No new dependencies.

**Spec:** [`docs/superpowers/specs/2026-05-26-world-integration-design.md`](../specs/2026-05-26-world-integration-design.md)

---

## Workflow rules (apply to EVERY phase)

These come from the spec §9 and the user's explicit instruction during brainstorming. Bake them into every subagent dispatch.

- **Subagents NEVER commit, NEVER stage, NEVER `git add`.** They write code and report DONE.
- Each phase ends with a verification walkthrough handed to the user. The user runs the dev server + probe driver in their own terminal.
- User verifies in browser → reports issues or replies "Phase N approved".
- Only on explicit approval → the controller (you, in the next session) runs `git add <specific paths>` then `git commit` with a NO-TRAILER message.
- **NEVER include `Co-Authored-By: Claude` in any commit.** User memory `feedback_no_claude_coauthor` is explicit.
- All phases stay on `world-v2-blender-build`. Merge to `main` is a separate user-driven decision after Phase 7.
- Branch sanity at the top of every phase: `git branch --show-current` must print `world-v2-blender-build`. If not, halt and ask.

---

## File map

### New files (created across all phases)

| Path | Phase | Responsibility |
|---|---|---|
| `src/World/GlbWorld.js` | 1 | Main loader: GLTF parse, scene-graph walk, 5-bucket dispatch, boot assertions. Public API surface that mirrors old `Terrain`/`Nature`/`Paths`/`DistantIslands`. |
| `src/World/SectionPositions.js` | 1 | Re-exports `SECTION_POSITIONS` populated from `refZoneBounding_*` after `GlbWorld.load()` resolves. |
| `src/Materials/SmoothLitPaletteMaterial.js` | 1 | Master `ShaderMaterial` per world-design §10.1 — palette sample + smooth Lambert + 3-band fog + wind displacement hook + reveal-wipe uniform. |
| `src/Portfolio/PortfolioMounts.js` | 2 | Replaces `Signs.js`. Mounts skills artifacts + experience cairns + contact plinth + resume lectern content onto Blender meshes via refs. |
| `src/Portfolio/ResumeData.js` | 2 | Placeholder resume content per world-design §4.1. |
| `src/Portfolio/ProjectShowcase.js` | 3 | Replaces `Billboards.js`. Single cycling showcase mounted on `refShowcaseMount`. |
| `src/World/WorldLights.js` | 4 | Replaces `StreetLights.js`. Ref-driven point lights at cairn lanterns + forge + brazier + lighthouse lamp. |
| `src/Materials/WaterShader.js` | 5 | River + tributary surface: UV scroll along curve, foam strip at edges. |
| `src/Materials/WaterfallShader.js` | 5 | Vertical stripe scroll. |
| `src/Materials/OceanShader.js` | 5 | Ocean plane: deep tint + calm-surface sparkle. |
| `src/Materials/MountainShader.js` | 5 | Cardboard mountain quads: heavy distance fog + alpha fade. |
| `src/Materials/BeamShader.js` | 5 | Low-opacity additive cone for lighthouse beam. |
| `src/Effects/WorldWater.js` | 5 | Replaces `Effects/Water.js`. Discovers `*water*`/`*waterfall*`/`*ocean*` meshes in the .glb and applies the right shader. |
| `src/Effects/ForgeParticles.js` | 6 | Continuous ember + chimney smoke wisp at `refForge`. |
| `src/Effects/BrazierParticles.js` | 6 | Flame + east-drifting smoke at `refBrazier`. |
| `src/Effects/WaterfallSpray.js` | 6 | Spray plume at `refWaterfallSpray`. |
| `.verify/scripts/verify-phase-1-mvs.mjs` | 1 | MVS verification driver. |
| `.verify/scripts/verify-phase-2-mounts.mjs` | 2 | Portfolio mount verification. |
| `.verify/scripts/verify-phase-3-showcase.mjs` | 3 | Project showcase verification. |
| `.verify/scripts/verify-phase-4-lights.mjs` | 4 | World lights verification. |
| `.verify/scripts/verify-phase-5-shaders.mjs` | 5 | Shaders + animations verification. |
| `.verify/scripts/verify-phase-6-particles.mjs` | 6 | Particles verification. |
| `.verify/scripts/verify-phase-7-smoothness.mjs` | 7 | Cross-device smoothness gate. |

### Files modified

| Path | Phases | Reason |
|---|---|---|
| `src/World/World.js` | 1 (heavy), 2, 3, 4, 5 | Facade reduced to wrap `GlbWorld` + portfolio mount modules; each phase wires its replacement. |
| `src/App.js` | 1, 4, 5, 7 | Wiring updates as modules swap in. |
| `src/Portfolio/Interactables.js` | 1 | Reposition crate/bag/football onto new heightfield. |
| `src/Portfolio/Interaction.js` | 2 | Register the resume lectern interaction. |
| `src/World/Grass.js` | 7 | Flatten-positions wired to baked path-ribbon samples (or dropped). |
| `src/World/Sun.js` | 7 | Elevation 12°, color `#f4d6b0` per world-design §9. |
| `src/World/TimeOfDay.js` | 7 | Dawn keyframes retuned per world-design §9. |
| `src/Player/PlayerCamera.js` | 7 | FOV 50° per world-design §9. |

### Files deleted (after user approval, per phase)

| Path | Phase |
|---|---|
| `src/World/Terrain.js` | 1 |
| `src/World/Nature.js` | 1 |
| `src/World/Paths.js` | 1 |
| `src/World/DistantIslands.js` | 1 |
| `src/Portfolio/Signs.js` | 2 |
| `src/Portfolio/Billboards.js` | 3 |
| `src/World/StreetLights.js` | 4 |
| `src/Effects/Water.js` | 5 |

---

## Verification harness — shared rules

Every phase's verification driver lives at `.verify/scripts/verify-phase-N-<topic>.mjs` and follows the canonical pattern from `.verify/scripts/verify-walk.mjs`. Required boilerplate at the top of every probe:

```js
// .verify/scripts/verify-phase-N-<topic>.mjs
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
page.on('requestfailed', (r) => errors.push(`REQFAIL: ${r.url()} ${r.failure()?.errorText}`));

console.log(`→ goto ${URL}`);
await page.goto(URL, { waitUntil: 'load', timeout: 30000 });
console.log('→ boot + dismiss welcome…');
await bootAndDismiss(page);
```

**Hard rules** (per `CLAUDE.md` "Verification sandbox" + memory `feedback_verify_layout_standing`):
- Date folder via `new Date().toISOString().slice(0, 10)`. **Never hardcode a date.**
- Always boot via `bootAndDismiss(page)` from `_boot.mjs`. Never inline a dismissal loop.
- Time-dependent assertions: pump synthetic ticks via `page.evaluate(() => window.__app._tick(1/30))` rather than wall-clock sleeps (memory `feedback_verify_synthetic_ticks`). Headless rAF throttles + App caps `delta=1/30`.
- Install playwright once globally: `cd /tmp && npm install --no-save playwright`. Reuse via `NODE_PATH=/tmp/node_modules node .verify/scripts/...`.

**Per-phase invocation pattern:**
```bash
# In one terminal:
npm run dev
# In another:
URL=http://localhost:5173/ NODE_PATH=/tmp/node_modules node .verify/scripts/verify-phase-N-<topic>.mjs
```

Output: screenshots to `.verify/shots/YYYY-MM-DD/`, JSON report to stdout.

---

## Phase 1: MVS swap (load + replace + reposition)

**Goal:** Load `world.glb`, expose `heightAt` + ref map + push-spots, wire the facade, reposition Interactables, **delete the 4 procedural modules after user verifies**.

### Files

- **Create:**
  - `src/World/GlbWorld.js`
  - `src/World/SectionPositions.js`
  - `src/Materials/SmoothLitPaletteMaterial.js`
  - `.verify/scripts/verify-phase-1-mvs.mjs`
- **Modify:**
  - `src/World/World.js` — reduce to facade
  - `src/App.js` — wiring (`addStaticGround`, `Player` ctor terrain ref, `DistantIslands` removal, `StreetLights` still loads in Phase 4 unchanged path)
  - `src/Portfolio/Interactables.js` — re-anchor crate/bag/football onto new heightfield (positions stay the same XZ; heightAt picks up new Y automatically — verify visually)
- **Delete after user approval:**
  - `src/World/Terrain.js`
  - `src/World/Nature.js`
  - `src/World/Paths.js`
  - `src/World/DistantIslands.js`

### Subagent dispatch prompt (copy-paste)

```
Implement Phase 1 of the World v2 runtime integration plan at
docs/superpowers/plans/2026-05-26-world-integration-build.md.

Branch: world-v2-blender-build (already checked out, do not switch).

Read first:
- docs/superpowers/plans/2026-05-26-world-integration-build.md (this plan,
  Phase 1 section)
- docs/superpowers/specs/2026-05-26-world-integration-design.md (spec)
- CLAUDE.md (project conventions)

Your job:
1. Create src/World/GlbWorld.js per the module interface in the plan.
2. Create src/World/SectionPositions.js per the plan.
3. Create src/Materials/SmoothLitPaletteMaterial.js per the plan.
4. Reduce src/World/World.js to the facade defined in the plan.
5. Update src/App.js wiring per the plan (remove DistantIslands import +
   instantiation; keep StreetLights load path — that's Phase 4's job).
6. Reposition src/Portfolio/Interactables.js positions onto the new world
   per the plan (XZ stays, heightAt provides new Y automatically).
7. Create .verify/scripts/verify-phase-1-mvs.mjs per the plan.

DO NOT delete the old modules (Terrain.js, Nature.js, Paths.js,
DistantIslands.js) — the controller deletes those AFTER the user verifies.
For now, they stay on disk but unimported.

DO NOT commit. DO NOT stage. DO NOT `git add`. Report DONE with a verification
walkthrough so the controller can hand it to the user.

CLAUDE.md hard constraints to respect:
- Never invent assets — the .glb at static/world/world.glb is the only
  authoring source. If you need a model/texture not in static/, stop and ask.
- All static colliders must match the visible mesh bbox (CLAUDE.md rule 5).
- Verify scripts go in .verify/scripts/ with date-folder runtime computation.
```

### `src/World/GlbWorld.js` — module interface

```js
import * as THREE from 'three';
import { SmoothLitPaletteMaterial } from '../Materials/SmoothLitPaletteMaterial.js';

/**
 * Single source of truth for the world geometry. Loads static/world/world.glb,
 * walks the scene graph once, and dispatches meshes into 5 buckets:
 *
 *   1. Terrain submesh   → baked 193×193 heightfield + Physics ground
 *   2. Named colliders   → cuboid_* / tube_* / trimesh_* → Rapier statics
 *   3. Ref empties       → typed refs map (sections, lights, particles, …)
 *   4. Material tokens   → *water* / *waterfall* / *ocean* / *mountain* /
 *                          *beam* / *glass* → special shaders (Phase 5 swaps;
 *                          Phase 1 leaves the default palette material)
 *   5. Push-spots        → pine_*, birch_*, hero_tree_*, cairn_*, sign_*,
 *                          waystone_*, bench_*, boulder_*
 *
 * Public API (matches what 18 downstream consumers already read):
 *   .terrain.heightAt(x, z)              — bilinear lookup against baked grid
 *   .terrain.size / .terrain.segments    — for Physics.addStaticGround
 *   .nature.pushSpots                    — [{ position, type, surfaceRadius, colliderRadius }]
 *   .nature.addExclusion(x, z, r)        — no-op (foliage baked)
 *   .nature.setPlayerUniforms(uniforms)  — forward to instanced foliage materials
 *   .paths.getTilePositions()            — Float32Array sampled along baked ribbons
 *   .paths.getTileCount()                — matches above
 *   .refs                                — typed accessor (see below)
 */
export class GlbWorld {
  static GLB_PATH = '/world/world.glb';
  static TERRAIN_GRID = 193;          // matches Blender Phase 2 authoring
  static PUSH_NAME_PATTERNS = [
    /^pine_/, /^birch_/, /^hero_tree_/, /^cairn_/, /^sign_/,
    /^waystone_/, /^bench_/, /^boulder_/,
  ];
  static MATERIAL_TOKEN_ORDER = [
    'waterfall', 'water', 'ocean', 'mountain', 'beam', 'glass',
  ]; // order matters — 'waterfall' must beat 'water'

  constructor(scene, loader) {
    this.scene = scene;
    this.loader = loader;

    // Buckets populated by load(). Names match what downstream code reads.
    this.root = new THREE.Group();
    this.root.name = 'glb-world';
    this.scene.add(this.root);

    this.terrain = {
      mesh: null,
      size: 0,
      segments: 0,
      heights: null,            // Float32Array, length (segments+1)^2
      heightAt: (x, z) => 0,    // replaced by bake() at load
    };
    this.nature = {
      pushSpots: [],
      _exclusionNoop: (x, z, r) => {},
      _playerUniforms: null,
    };
    this.nature.addExclusion = this.nature._exclusionNoop;
    this.nature.setPlayerUniforms = (u) => {
      this.nature._playerUniforms = u;
      for (const mat of this._foliageMaterials) {
        if (mat.userData?.setPlayerUniforms) mat.userData.setPlayerUniforms(u);
      }
    };
    this.paths = {
      _positions: new Float32Array(0),
      _count: 0,
      getTilePositions: () => this.paths._positions,
      getTileCount: () => this.paths._count,
    };

    this.refs = {
      section: {},              // refZoneBounding_<key> → THREE.Vector3 (+ .radius)
      sectionFrustum: {},       // refZoneFrustum_<key> → Vector3 (+ .radius)
      interactivePoint: {},     // refInteractivePoint_<key>
      respawn: {},              // refRespawn_<key>
      lights: { cairnLantern: [], forge: null, brazier: null, lighthouseLamp: null },
      beam: { lighthousePivot: null },
      particles: { forgeSmoke: null, brazierFlame: null, waterfallSpray: null },
      interaction: { resumeLectern: null, showcaseMount: null },
      viewpoint: {},            // refViewpoint_<key>
      foliage: { heroTree: [], bench: [] },
      raw: new Map(),           // name → Object3D for any ref we didn't classify
    };

    this._materialTokenMeshes = {
      waterfall: [], water: [], ocean: [], mountain: [], beam: [], glass: [],
    };
    this._emissiveMeshes = [];
    this._foliageMaterials = [];

    // billboards/signs sub-objects are populated by PortfolioMounts (Phase 2)
    // and ProjectShowcase (Phase 3). Phase 1 leaves empty stubs so the
    // facade can expose them without nulls.
    this.billboards = { items: [], emissiveBoost: 1.0, update() {}, setIndex() {}, setFocused() {}, closestWithin: () => null };
    this.signs = { experienceItems: [], skillsPosition: null, contactPosition: null, nearContact: () => null };
  }

  /** Load + parse the .glb, populate buckets, run assertions. */
  async load(physics) {
    const gltf = await this.loader.loadGLTF(GlbWorld.GLB_PATH);
    const scene = gltf.scene;
    this.root.add(scene);

    // Walk once, classify by name + material.
    scene.traverse((obj) => this.#classify(obj));

    // 1. Bake heightfield from terrain submesh.
    this.#bakeHeightfield();

    // 2. Register colliders with physics.
    if (physics) this.#registerColliders(physics);

    // 3. Apply materials. Phase 1: default palette material for all visible;
    //    Phase 5 will swap special shaders.
    this.#applyDefaultMaterials();

    // 4. Detect instancing (shared bpy.data.meshes → InstancedMesh).
    this.#instanceSharedMeshes();

    // 5. Sample path ribbons → tile positions for grass flatten.
    this.#samplePathRibbons();

    // 6. Auto-detect push spots by mesh-name regex.
    this.#detectPushSpots();

    // 7. Boot assertions — halt loudly if anything's missing.
    this.#assertBootInvariants();

    return this;
  }

  // ── Classification ──────────────────────────────────────────────────────

  #classify(obj) {
    const name = obj.name || '';

    // Empties (refs).
    if (obj.isObject3D && !obj.isMesh && name.startsWith('ref')) {
      this.refs.raw.set(name, obj);
      this.#classifyRef(name, obj);
      return;
    }

    // Meshes.
    if (!obj.isMesh) return;

    // Terrain.
    if (name === 'terrain') {
      this.terrain.mesh = obj;
      return;
    }

    // Collider meshes — keep, hide, register later.
    if (name.startsWith('cuboid_') || name.startsWith('tube_') || name.startsWith('trimesh_')) {
      obj.visible = false;
      obj.userData.collider = true;
      return;
    }

    // Material-token meshes.
    const matName = obj.material?.name?.toLowerCase() || '';
    for (const token of GlbWorld.MATERIAL_TOKEN_ORDER) {
      if (matName.includes(token)) {
        this._materialTokenMeshes[token].push(obj);
        obj.userData.materialToken = token;
        break;
      }
    }

    // Emissive suffix.
    if (name.endsWith('_emissive')) {
      this._emissiveMeshes.push(obj);
      obj.userData.emissive = true;
    }
  }

  #classifyRef(name, obj) {
    const pos = obj.position.clone();
    const radius = Math.max(obj.scale.x, obj.scale.z); // scale-as-radius

    if (name.startsWith('refZoneBounding_')) {
      const key = name.slice('refZoneBounding_'.length);
      this.refs.section[key] = Object.assign(pos, { radius });
    } else if (name.startsWith('refZoneFrustum_')) {
      const key = name.slice('refZoneFrustum_'.length);
      this.refs.sectionFrustum[key] = Object.assign(pos, { radius });
    } else if (name.startsWith('refInteractivePoint_')) {
      const key = name.slice('refInteractivePoint_'.length);
      this.refs.interactivePoint[key] = pos;
    } else if (name.startsWith('refRespawn_')) {
      const key = name.slice('refRespawn_'.length);
      this.refs.respawn[key] = pos;
    } else if (name.startsWith('refCairnLantern_')) {
      this.refs.lights.cairnLantern.push({ name, position: pos });
    } else if (name === 'refForge') {
      this.refs.lights.forge = pos;
      this.refs.particles.forgeSmoke = pos.clone();
    } else if (name === 'refBrazier') {
      this.refs.lights.brazier = pos;
      this.refs.particles.brazierFlame = pos.clone();
    } else if (name === 'refLighthouseBeamPivot') {
      this.refs.beam.lighthousePivot = obj;     // KEEP the Object3D — we rotate it
    } else if (name === 'refWaterfallSpray') {
      this.refs.particles.waterfallSpray = pos;
    } else if (name === 'refResumeInteractivePoint') {
      this.refs.interaction.resumeLectern = pos;
    } else if (name === 'refShowcaseMount') {
      this.refs.interaction.showcaseMount = { position: pos, rotation: obj.rotation.clone() };
    } else if (name.startsWith('refViewpoint_')) {
      const key = name.slice('refViewpoint_'.length);
      this.refs.viewpoint[key] = Object.assign(pos, { userData: { ...obj.userData } });
    } else if (name.startsWith('refHeroTree_')) {
      this.refs.foliage.heroTree.push({ name, position: pos });
    } else if (name.startsWith('refBench_')) {
      this.refs.foliage.bench.push({ name, position: pos });
    }
  }

  // ── Heightfield bake ────────────────────────────────────────────────────

  #bakeHeightfield() {
    const mesh = this.terrain.mesh;
    if (!mesh) throw new Error('GlbWorld: terrain submesh missing from world.glb');

    // The Blender terrain is authored as a 193×193 sculpted grid (Phase 2 of
    // the build). Walk its vertex array, sort into a regular XZ grid, store
    // the Y values in a Float32Array for bilinear lookup.
    const geometry = mesh.geometry;
    const pos = geometry.attributes.position;
    geometry.computeBoundingBox();
    const bbox = geometry.boundingBox;
    const size = Math.max(bbox.max.x - bbox.min.x, bbox.max.z - bbox.min.z);
    const segments = GlbWorld.TERRAIN_GRID - 1;
    const cells = segments;
    const verts = segments + 1;
    const heights = new Float32Array(verts * verts);

    // Worldspace transform of the terrain mesh (in case Blender export added
    // any root transform we didn't strip).
    mesh.updateMatrixWorld(true);
    const vec = new THREE.Vector3();

    // For a sculpted-grid heightfield, vertices are in regular order. We
    // tolerate non-regular ordering by bucketing into the grid.
    for (let i = 0; i < pos.count; i++) {
      vec.fromBufferAttribute(pos, i).applyMatrix4(mesh.matrixWorld);
      const u = THREE.MathUtils.clamp(
        Math.round(((vec.x - bbox.min.x) / size) * segments), 0, segments);
      const w = THREE.MathUtils.clamp(
        Math.round(((vec.z - bbox.min.z) / size) * segments), 0, segments);
      heights[u * verts + w] = vec.y;
    }

    this.terrain.size = size;
    this.terrain.segments = segments;
    this.terrain.heights = heights;
    this.terrain.bboxMin = bbox.min.clone();

    // Bilinear lookup. Mirrors Physics.addStaticGround's expectation of
    // heightAt(x, z) returning the worldspace Y at the given XZ.
    this.terrain.heightAt = (x, z) => {
      const fu = ((x - bbox.min.x) / size) * segments;
      const fw = ((z - bbox.min.z) / size) * segments;
      const u0 = THREE.MathUtils.clamp(Math.floor(fu), 0, segments);
      const w0 = THREE.MathUtils.clamp(Math.floor(fw), 0, segments);
      const u1 = THREE.MathUtils.clamp(u0 + 1, 0, segments);
      const w1 = THREE.MathUtils.clamp(w0 + 1, 0, segments);
      const tu = fu - u0;
      const tw = fw - w0;
      const h00 = heights[u0 * verts + w0];
      const h10 = heights[u1 * verts + w0];
      const h01 = heights[u0 * verts + w1];
      const h11 = heights[u1 * verts + w1];
      return (1 - tu) * (1 - tw) * h00
           + tu       * (1 - tw) * h10
           + (1 - tu) * tw       * h01
           + tu       * tw       * h11;
    };
  }

  // ── Colliders ───────────────────────────────────────────────────────────

  #registerColliders(physics) {
    this.root.traverse((obj) => {
      if (!obj.isMesh || !obj.userData.collider) return;

      obj.updateMatrixWorld(true);
      const box = new THREE.Box3().setFromObject(obj);
      const size = box.getSize(new THREE.Vector3());
      const center = box.getCenter(new THREE.Vector3());
      const yaw = obj.rotation.y;

      if (obj.name.startsWith('cuboid_')) {
        physics.addStaticCuboid(
          center.x, center.y, center.z,
          size.x / 2, size.y / 2, size.z / 2,
          yaw,
        );
      } else if (obj.name.startsWith('tube_')) {
        const radius = Math.max(size.x, size.z) / 2;
        const height = size.y;
        physics.addStaticCylinder(center.x, center.y - height / 2, center.z, radius, height);
      }
      // trimesh_* — Rapier supports trimesh colliders via
      // ColliderDesc.trimesh; defer to Phase 1 if any are present. For now,
      // log a warning; the spec's terrain is the only trimesh and it
      // takes the heightfield path above.
    });
  }

  // ── Materials ───────────────────────────────────────────────────────────

  #applyDefaultMaterials() {
    this.root.traverse((obj) => {
      if (!obj.isMesh || obj.userData.collider) return;
      if (obj === this.terrain.mesh) return; // terrain keeps its GLB material
      const matName = obj.material?.name?.toLowerCase() || '';
      // Phase 1: special-token meshes still get the GLB material (palette
      // sample baked in). Phase 5 swaps these for ShaderMaterial variants.
      // Default meshes also keep the GLB material — the master shader is
      // attached in Phase 5 too.
      // We DO attach the wind-displacement hook to foliage materials so
      // Phase 5 can flip a uniform later.
      if (this.#isFoliageMesh(obj)) {
        this._foliageMaterials.push(obj.material);
      }
    });
  }

  #isFoliageMesh(obj) {
    return /^(pine|birch|hero_tree|bush|fern|flower|boulder)_/.test(obj.name || '');
  }

  // ── Instancing ──────────────────────────────────────────────────────────

  #instanceSharedMeshes() {
    // Group meshes by shared geometry datablock.
    const buckets = new Map(); // geometry.uuid → [obj…]
    this.root.traverse((obj) => {
      if (!obj.isMesh || obj.userData.collider) return;
      const id = obj.geometry?.uuid;
      if (!id) return;
      const arr = buckets.get(id) || [];
      arr.push(obj);
      buckets.set(id, arr);
    });
    for (const [, list] of buckets) {
      if (list.length < 2) continue;
      // Build an InstancedMesh per source; replace the original meshes with
      // an InstancedMesh that carries their transforms.
      this.#collapseToInstancedMesh(list);
    }
  }

  #collapseToInstancedMesh(meshes) {
    const source = meshes[0];
    const count = meshes.length;
    const inst = new THREE.InstancedMesh(source.geometry, source.material, count);
    inst.name = `${source.name}__inst`;
    inst.castShadow = source.castShadow;
    inst.receiveShadow = source.receiveShadow;
    const m = new THREE.Matrix4();
    for (let i = 0; i < count; i++) {
      meshes[i].updateMatrixWorld(true);
      inst.setMatrixAt(i, meshes[i].matrixWorld);
      meshes[i].visible = false;
      meshes[i].parent?.remove(meshes[i]);
    }
    inst.instanceMatrix.needsUpdate = true;
    this.root.add(inst);
  }

  // ── Path-ribbon sampling ────────────────────────────────────────────────

  #samplePathRibbons() {
    const points = [];
    this.root.traverse((obj) => {
      if (!obj.isMesh) return;
      if (!/^(path|trail|perimeter|detour|stepping)/.test(obj.name)) return;
      // Sample N points across the ribbon by walking its vertex positions.
      const geom = obj.geometry;
      const pos = geom.attributes.position;
      obj.updateMatrixWorld(true);
      const v = new THREE.Vector3();
      const stride = Math.max(1, Math.floor(pos.count / 40)); // ~40 samples per ribbon
      for (let i = 0; i < pos.count; i += stride) {
        v.fromBufferAttribute(pos, i).applyMatrix4(obj.matrixWorld);
        points.push(v.x, v.z);
      }
    });
    this.paths._positions = new Float32Array(points);
    this.paths._count = points.length / 2;
  }

  // ── Push spots ──────────────────────────────────────────────────────────

  #detectPushSpots() {
    const found = [];
    this.root.traverse((obj) => {
      if (!obj.isMesh && !obj.isInstancedMesh) return;
      const name = obj.name || '';
      const matched = GlbWorld.PUSH_NAME_PATTERNS.find((re) => re.test(name));
      if (!matched) return;
      obj.updateMatrixWorld(true);
      const box = new THREE.Box3().setFromObject(obj);
      const size = box.getSize(new THREE.Vector3());
      const center = box.getCenter(new THREE.Vector3());
      const type = matched.source.replace(/^\^|_\/$/g, '');
      found.push({
        position: center,
        type,
        surfaceRadius: Math.max(size.x, size.z) / 2 + 0.2,
        colliderRadius: Math.max(size.x, size.z) / 2,
      });
    });
    this.nature.pushSpots = found;
  }

  // ── Boot invariant assertions ───────────────────────────────────────────

  #assertBootInvariants() {
    const required = {
      'terrain submesh': !!this.terrain.mesh && this.terrain.heights,
      'refZoneBounding_spawn': !!this.refs.section.spawn,
      'refZoneBounding_projects': !!this.refs.section.projects,
      'refZoneBounding_experience': !!this.refs.section.experience,
      'refZoneBounding_skills': !!this.refs.section.skills,
      'refZoneBounding_contact': !!this.refs.section.contact,
      'refShowcaseMount': !!this.refs.interaction.showcaseMount,
      'refResumeInteractivePoint': !!this.refs.interaction.resumeLectern,
      'refLighthouseBeamPivot': !!this.refs.beam.lighthousePivot,
      'refForge': !!this.refs.lights.forge,
      'refBrazier': !!this.refs.lights.brazier,
      'refCairnLantern_* ≥4': this.refs.lights.cairnLantern.length >= 4,
      'push-spots ≥50': this.nature.pushSpots.length >= 50,
    };
    const failures = Object.entries(required).filter(([, ok]) => !ok).map(([k]) => k);
    if (failures.length > 0) {
      throw new Error(
        `GlbWorld boot assertions failed:\n  - ${failures.join('\n  - ')}`,
      );
    }
    console.log('[GlbWorld] load: OK', {
      heightfieldSize: this.terrain.size.toFixed(2),
      cairnLanterns: this.refs.lights.cairnLantern.length,
      pushSpots: this.nature.pushSpots.length,
      sections: Object.keys(this.refs.section),
    });
  }
}
```

### `src/World/SectionPositions.js` — module interface

```js
/**
 * Single source of truth for SECTION_POSITIONS. Phase 1 wires this from
 * GlbWorld.refs.section. Downstream consumers (WorldMap, MiniMap, MapMarkers,
 * Discovery) import from here instead of Signs.js.
 *
 * Module is populated after GlbWorld.load() resolves; consumers that read it
 * before then see the spec-fallback (±70 cardinal), so they don't crash if
 * they construct before world load completes. World.loadAssets() calls
 * setSectionPositions(...) once GlbWorld is ready.
 */

const FALLBACK = {
  spawn:      { x: 0,   z: 0    },
  projects:   { x: 70,  z: 0    },
  experience: { x: 0,   z: 70   },
  skills:     { x: 0,   z: -70  },
  contact:    { x: -70, z: 0    },
};

let _positions = { ...FALLBACK };
let _experiencePath = [];

export function setSectionPositions(refs) {
  for (const key of Object.keys(FALLBACK)) {
    const ref = refs.section?.[key];
    if (ref) _positions[key] = { x: ref.x, z: ref.z };
  }
  // experiencePath = sorted cairn lantern positions (south→north).
  const cairns = (refs.lights?.cairnLantern ?? []).slice();
  cairns.sort((a, b) => a.position.z - b.position.z);
  _experiencePath = cairns.map((c) => ({ x: c.position.x, z: c.position.z }));
}

export const SECTION_POSITIONS = {
  get spawn()          { return _positions.spawn; },
  get projects()       { return _positions.projects; },
  get experience()     { return _positions.experience; },
  get skills()         { return _positions.skills; },
  get contact()        { return _positions.contact; },
  get experiencePath() { return _experiencePath; },
};
```

### `src/Materials/SmoothLitPaletteMaterial.js` — Phase 1 placeholder

Phase 1 ships a **passthrough** master material that just wraps `MeshLambertMaterial` + palette texture. Phase 5 extends it with the full smooth-lit + 3-band fog + wind hook pipeline.

```js
import * as THREE from 'three';

/**
 * Master material for world props. Phase 1: thin MeshLambertMaterial wrapper.
 * Phase 5: extended to ShaderMaterial with palette sample, smooth Lambert,
 * 3-band fog, wind displacement, reveal-wipe (world-design §10.1).
 *
 * Phase 1 keeps it cheap so the MVS swap is bisectable against shader bugs.
 */
export class SmoothLitPaletteMaterial extends THREE.MeshLambertMaterial {
  constructor(opts = {}) {
    super({
      color: 0xffffff,
      ...opts,
    });
    this.userData = this.userData || {};
    this.userData.isPaletteMaster = true;
  }

  setPlayerUniforms(_uniforms) {
    // Phase 5 wires this through onBeforeCompile.
  }
}
```

### `src/World/World.js` — facade (full rewrite for Phase 1)

```js
import { GlbWorld } from './GlbWorld.js';
import { Sky } from './Sky.js';
import { setSectionPositions } from './SectionPositions.js';

/**
 * Top-level world facade. Wraps GlbWorld + Sky and (in later phases)
 * PortfolioMounts + ProjectShowcase + WorldLights + WorldWater. Re-exposes
 * the legacy attribute names (terrain, nature, paths, billboards, signs,
 * water, sky) so App.js + downstream consumers don't need rewriting.
 */
export class World {
  constructor(scene, loader) {
    this.scene = scene;
    this.loader = loader;
    this.sky = new Sky(scene);

    // GlbWorld is constructed synchronously; loadAssets() runs the parse.
    this.glb = new GlbWorld(scene, loader);

    // Facade attributes — referenced by App.js and downstream. They proxy
    // into GlbWorld today; later phases swap in real PortfolioMounts /
    // ProjectShowcase / WorldLights / WorldWater objects.
    this.terrain     = this.glb.terrain;
    this.nature      = this.glb.nature;
    this.paths       = this.glb.paths;
    this.billboards  = this.glb.billboards;
    this.signs       = this.glb.signs;
    this.water       = null; // assigned in Phase 5
  }

  async loadAssets(loader, physics = null, { playerUniforms = null } = {}) {
    await this.glb.load(physics);
    setSectionPositions(this.glb.refs);

    if (playerUniforms) this.glb.nature.setPlayerUniforms(playerUniforms);

    return {
      nature:     this.glb.nature.pushSpots.length,
      billboards: 0,                              // populated in Phase 3
      experience: 0,                              // populated in Phase 2
      paths:      this.glb.paths.getTileCount(),
    };
  }

  update(elapsed, camera = null, delta = 0, playerPos = null) {
    if (camera) this.sky.update(camera.position);
    // billboards.update is wired in Phase 3 once ProjectShowcase exists.
    if (this.billboards?.update) this.billboards.update(elapsed, playerPos, delta);
  }
}
```

### `src/App.js` — Phase 1 wiring changes

- **Remove** `import { DistantIslands } from './World/DistantIslands.js'` (line 13).
- **Remove** the `this.distantIslands = new DistantIslands(this.scene)` block in `boot()` (around line 337–339).
- **Remove** the `DistanceGame` reference to `islands: this.distantIslands` — replace with `islands: { getIslands: () => [] }` for now. (Phase 7 will read viewpoint refs.)
- **Remove** `if (this.distantIslands) this.distantIslands.setMode(...)` from any tick / tod handler.
- **Keep** `this.physics.addStaticGround(this.world.terrain)` — `this.world.terrain` is now `GlbWorld.terrain` which exposes `size`/`segments`/`heightAt` identically.
- **Keep** all other wiring — `world.nature.pushSpots`, `world.signs`, `world.billboards` all still resolve via the facade (stubs in Phase 1, real in Phases 2–3).

### `src/Portfolio/Interactables.js` — Phase 1 repositioning

The dynamic-body anchors stay at the same XZ coordinates (`INTERACTABLE_PROP_EXCLUSIONS` constant); `terrain.heightAt(x, z)` is consulted at placement time so Y picks up the new heightfield automatically. **No code changes required** — verify by walking to each prop in Phase 1 verification gate 5.

If any prop visibly sinks or floats >5cm post-load, recenter that prop's `INTERACTABLE_PROP_EXCLUSIONS` entry to a sensible nearby XZ where the new heightfield is flatter. Update only that entry; do not touch the others.

### `.verify/scripts/verify-phase-1-mvs.mjs`

```js
// Phase 1 MVS verification. Runs synthetic ticks; probes heightAt at 21
// sample points; asserts boot invariants; walks player NSEW; screenshots.
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
page.on('requestfailed', (r) => errors.push(`REQFAIL: ${r.url()} ${r.failure()?.errorText}`));

await page.goto(URL, { waitUntil: 'load', timeout: 30000 });
await bootAndDismiss(page);

// 1. Numeric probe — 21 sample points, baked heightAt vs downward raycast.
const SAMPLES = [
  [0, 0],
  [70, 0], [-70, 0], [0, 70], [0, -70],
  [80, 0], [-80, 0], [0, 80], [0, -80],
  [45, 0], [-45, 0], [0, 45], [0, -45],
  [60, 0], [-60, 0], [0, 60], [0, -60],
  [-76, 45], [15, 95], [45, -85],
  [-130, 35],
];

const probe = await page.evaluate((SAMPLES) => {
  const app = window.__app;
  const THREE = app.THREE || window.THREE;
  const terrain = app.world.terrain;
  const meshes = [];
  app.scene.traverse((o) => { if (o.isMesh && o.name === 'terrain') meshes.push(o); });
  if (meshes.length === 0) return { error: 'terrain submesh not in scene' };
  const ray = new THREE.Raycaster();
  ray.firstHitOnly = true;
  const out = [];
  for (const [x, z] of SAMPLES) {
    const baked = terrain.heightAt(x, z);
    ray.set(new THREE.Vector3(x, 200, z), new THREE.Vector3(0, -1, 0));
    const hits = ray.intersectObject(meshes[0], false);
    const ray_y = hits.length > 0 ? hits[0].point.y : null;
    out.push({ x, z, baked, ray_y, delta: ray_y == null ? null : Math.abs(baked - ray_y) });
  }
  return { samples: out };
}, SAMPLES);

// 2. Boot invariant log — already printed by GlbWorld; capture it.
const bootLogs = logs.filter((l) => l.includes('[GlbWorld]'));

// 3. Push-spot count.
const pushCount = await page.evaluate(() => window.__app.world.nature?.pushSpots?.length ?? 0);

// 4. Walk probe: N → spawn → E → spawn → S → spawn → W → spawn (one
//    direction at a time, synthetic ticks).
async function walkTo(label, key, ms) {
  await page.keyboard.down(key);
  await page.waitForTimeout(ms);
  await page.keyboard.up(key);
  await page.waitForTimeout(150);
  await page.screenshot({ path: `${SHOTS}/p1-walk-${label}.png` });
}
await page.screenshot({ path: `${SHOTS}/p1-spawn.png` });
await walkTo('north', 'KeyW', 4000);
await walkTo('back-from-north', 'KeyS', 4000);
await walkTo('east', 'KeyD', 4000);
await walkTo('back-from-east', 'KeyA', 4000);
await walkTo('south', 'KeyS', 4000);
await walkTo('back-from-south', 'KeyW', 4000);
await walkTo('west', 'KeyA', 4000);
await walkTo('back-from-west', 'KeyD', 4000);

// 5. Grounded check — sample player.grounded across the walk via tick.
const groundedReport = await page.evaluate(() => {
  const p = window.__app.player;
  return { grounded: p.body?.grounded, pos: p.position };
});

// 6. FPS over 1s.
const fps = await page.evaluate(() => new Promise((resolve) => {
  let frames = 0;
  const start = performance.now();
  function tick() {
    frames++;
    if (performance.now() - start < 1000) requestAnimationFrame(tick);
    else resolve(frames);
  }
  requestAnimationFrame(tick);
}));

await browser.close();

const maxDelta = Math.max(...probe.samples.filter((s) => s.delta != null).map((s) => s.delta));
const report = {
  url: URL,
  shots_dir: SHOTS,
  boot_logs: bootLogs,
  push_spot_count: pushCount,
  push_spot_pass: pushCount >= 50,
  heightAt_probe: probe.samples,
  heightAt_max_delta: maxDelta,
  heightAt_pass: maxDelta <= 0.01,
  grounded: groundedReport,
  fps_1s: fps,
  errors,
  error_logs: logs.filter((l) => l.startsWith('[error]')),
};
console.log('\n=== PHASE 1 REPORT ===');
console.log(JSON.stringify(report, null, 2));
```

### Implementation tasks

- [ ] **Task 1.1: Branch + clean tree check**

```bash
git branch --show-current
git status --porcelain
```
Expected: branch `world-v2-blender-build`, clean tree.

- [ ] **Task 1.2: Create `src/Materials/` directory (if not present)**

```bash
mkdir -p /Users/mahajankaran/Documents/Projects/karan-portfolio/src/Materials
```
Expected: directory exists.

- [ ] **Task 1.3: Write `src/Materials/SmoothLitPaletteMaterial.js`** — full code from this plan above.

- [ ] **Task 1.4: Write `src/World/SectionPositions.js`** — full code from this plan above.

- [ ] **Task 1.5: Write `src/World/GlbWorld.js`** — full code from this plan above.

- [ ] **Task 1.6: Rewrite `src/World/World.js` as the facade** — full code from this plan above. Save a backup of the existing one in case verification reveals an issue:

```bash
cp src/World/World.js src/World/World.js.bak.phase1
```
(Delete the .bak file before commit; the user only commits the final state.)

- [ ] **Task 1.7: Update `src/App.js`** — remove DistantIslands import + instantiation + setMode call. Keep everything else.

- [ ] **Task 1.8: Verify Interactables positions** — run dev server, walk to each prop in `INTERACTABLE_PROP_EXCLUSIONS`; if any sinks/floats, adjust that single entry's XZ. (Subagent uses headless probe to log Y at each XZ before declaring done.)

- [ ] **Task 1.9: Write `.verify/scripts/verify-phase-1-mvs.mjs`** — full code from this plan above.

- [ ] **Task 1.10: Run the probe locally and capture the report**

```bash
# In a separate terminal: npm run dev
URL=http://localhost:5173/ NODE_PATH=/tmp/node_modules node .verify/scripts/verify-phase-1-mvs.mjs > .verify/shots/$(date +%F)/p1-report.json
```
Expected: `heightAt_pass: true`, `push_spot_pass: true`, `boot_logs` contains `[GlbWorld] load: OK`, no `errors`, `fps_1s >= 50`.

- [ ] **Task 1.11: Report DONE to controller** with:
  - File list of changes
  - Path to the JSON report
  - Path to the screenshots folder
  - Any boot warnings observed

### User verification gate (Phase 1)

The controller hands this checklist to the user verbatim:

> **Phase 1 verification — please tick through:**
>
> 1. Run in a terminal: `npm run dev` (keep running)
> 2. Run in another terminal: `URL=http://localhost:5173/ NODE_PATH=/tmp/node_modules node .verify/scripts/verify-phase-1-mvs.mjs`
> 3. Confirm the report shows:
>    - [ ] `boot_logs` contains `[GlbWorld] load: OK`
>    - [ ] `heightAt_max_delta <= 0.01`
>    - [ ] `push_spot_count >= 50`
>    - [ ] `errors` array is empty
>    - [ ] `fps_1s >= 50`
> 4. Open the dev server in your own browser. Walk to each cardinal section using WASD. Confirm visually:
>    - [ ] Spawn area looks like the Blender preview (hearth, wayfinder, lectern)
>    - [ ] Projects pavilion is visible to the east
>    - [ ] Cairn trail rises to the north
>    - [ ] Observatory tower is visible to the south
>    - [ ] Brazier platform is visible to the west, with lighthouse on the horizon NW
>    - [ ] Player does NOT sink into the terrain at any cardinal section
>    - [ ] No falling-through-floor incidents
> 5. Open screenshots in `.verify/shots/<today>/p1-*.png` and spot-check that each section looks right.
> 6. Open the browser dev console. Confirm no errors red-text. (Warnings are OK.)
>
> If everything is good, reply **"Phase 1 approved"**. If anything is off, paste what you see and we'll fix it before committing.

### Post-approval commit (controller runs after explicit user approval)

```bash
# Delete the four old modules — they're no longer imported.
rm src/World/Terrain.js src/World/Nature.js src/World/Paths.js src/World/DistantIslands.js

# Stage only the specific paths involved.
git add \
  src/World/GlbWorld.js \
  src/World/SectionPositions.js \
  src/Materials/SmoothLitPaletteMaterial.js \
  src/World/World.js \
  src/App.js \
  src/Portfolio/Interactables.js \
  .verify/scripts/verify-phase-1-mvs.mjs \
  src/World/Terrain.js \
  src/World/Nature.js \
  src/World/Paths.js \
  src/World/DistantIslands.js

git commit -m "$(cat <<'EOF'
Phase 1: GlbWorld MVS swap — replace procedural Terrain/Nature/Paths/DistantIslands

Loads static/world/world.glb at boot. Heightfield baked from the 193×193
terrain submesh; ref empties + named colliders + push-spots dispatched on a
single scene-graph walk. World.js reduced to a facade so App.js and the 18
downstream consumers (Player, Footprints, Leaves, Water, Interactables,
ClickToMove, Teleport, Torch, …) keep working with zero edits.

Old procedural modules deleted after user verified heightAt at 21 sample
points (max delta 0.01m) and walked all four cardinal sections without
sinking.
EOF
)"
```

**NO `Co-Authored-By: Claude` trailer.** Per user memory `feedback_no_claude_coauthor`.

---

## Phase 2: PortfolioMounts (replaces Signs.js, adds resume lectern)

**Goal:** Mount Skills / Experience / Contact / Resume content onto Blender artifact meshes. Delete `Signs.js` after user verifies.

### Files

- **Create:**
  - `src/Portfolio/PortfolioMounts.js`
  - `src/Portfolio/ResumeData.js`
  - `.verify/scripts/verify-phase-2-mounts.mjs`
- **Modify:**
  - `src/World/World.js` — instantiate `PortfolioMounts` after `GlbWorld.load()`, assign to `this.signs`
  - `src/Portfolio/Interaction.js` — register `nearResume(playerPosition, radius)` like the existing `nearContact`
- **Delete after user approval:**
  - `src/Portfolio/Signs.js`

### Subagent dispatch prompt (copy-paste)

```
Implement Phase 2 of the World v2 integration plan
(docs/superpowers/plans/2026-05-26-world-integration-build.md, Phase 2).

Phase 1 has been committed. Branch: world-v2-blender-build.

Read first:
- The plan's Phase 2 section
- src/Portfolio/Signs.js (the module you're replacing — preserve its public
  API: experienceItems[], skillsPosition, contactPosition, nearContact())
- src/Portfolio/Interaction.js (how 'near*' helpers wire into proximity UI)

Your job:
1. Create src/Portfolio/PortfolioMounts.js per the plan.
2. Create src/Portfolio/ResumeData.js with the placeholder content from the
   plan.
3. Add 'nearResume' helper to src/Portfolio/Interaction.js parallel to
   nearContact (the plan shows the exact signature).
4. Wire PortfolioMounts into src/World/World.js — instantiate after
   glb.load(), assign to this.signs.
5. Add a portfolioMounts.resume entry to the Interaction wiring in App.js so
   the resume modal opens when the player approaches refResumeInteractivePoint.
6. Create .verify/scripts/verify-phase-2-mounts.mjs per the plan.

DO NOT delete Signs.js. DO NOT commit or stage. Report DONE with a
verification walkthrough.
```

### `src/Portfolio/PortfolioMounts.js` — module interface

```js
import * as THREE from 'three';
import { experience } from './ExperienceData.js';
import { skills } from './SkillsData.js';
import { contact } from './ContactData.js';
import { resume } from './ResumeData.js';

/**
 * Replaces Signs.js. Mounts portfolio content (skills artifacts, experience
 * cairns, contact plinth, resume lectern) onto the Blender-authored meshes
 * via refs collected during GlbWorld.load(). Each mount = one panel/decal
 * applied to the appropriate Blender mesh OR an in-front-of-mesh world-space
 * canvas if the artifact's geometry is too small/awkward to texture.
 *
 * Compatibility — preserves the Signs.js public API the rest of the
 * codebase reads:
 *   .experienceItems            — [{ index, position, accent, entry, mesh }]
 *   .skillsPosition             — Vector3
 *   .contactPosition            — Vector3
 *   .nearContact(playerPos, r)  — boolean
 *   .nearResume(playerPos, r)   — boolean (NEW)
 */
export class PortfolioMounts {
  static EXP_PROXIMITY = 6;
  static SKILLS_PROXIMITY = 7;
  static CONTACT_PROXIMITY = 5;
  static RESUME_PROXIMITY = 4;

  constructor(scene, glbRefs, sectionPositions) {
    this.scene = scene;
    this.refs = glbRefs;
    this.section = sectionPositions;

    this.experienceItems = [];
    this.skillsPosition = this.refs.section.skills?.clone() ?? new THREE.Vector3();
    this.contactPosition = this.refs.section.contact?.clone() ?? new THREE.Vector3();
    this.resumePosition = this.refs.interaction.resumeLectern?.clone() ?? new THREE.Vector3();

    this.#buildExperienceCairns();
    this.#buildSkillsArtifacts();
    this.#buildContactPlinth();
    this.#buildResumeLectern();
  }

  // ── Experience: one canvas-baked plank floats above each cairn ───────────
  #buildExperienceCairns() {
    const cairns = this.refs.lights.cairnLantern.slice();
    cairns.sort((a, b) => a.position.z - b.position.z);
    for (let i = 0; i < Math.min(experience.length, cairns.length); i++) {
      const entry = experience[i];
      const cairn = cairns[i];
      const plank = this.#makeExperiencePlank(entry);
      // Float 1.5m above the cairn cap so the player reads the inscription
      // as they approach. Faces center of world (origin) so it's readable
      // from the trail-approach side.
      plank.position.copy(cairn.position).add(new THREE.Vector3(0, 1.6, 0));
      plank.lookAt(0, plank.position.y, 0);
      this.scene.add(plank);
      this.experienceItems.push({
        index: i,
        position: cairn.position.clone(),
        accent: entry.accent ?? '#ffb074',
        entry,
        mesh: plank,
      });
    }
  }

  #makeExperiencePlank(entry) {
    // Reuse the canvas baker pattern from Signs.experienceTexture, but the
    // mesh is a simple unlit plane attached to the cairn anchor.
    const canvas = document.createElement('canvas');
    canvas.width = 1024;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#2b1c12';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = entry.accent ?? '#ffb074';
    ctx.fillRect(0, 0, 32, canvas.height);
    ctx.fillStyle = '#f5e6d3';
    ctx.font = '700 96px "Oswald", sans-serif';
    ctx.fillText(entry.company, 56, 120);
    ctx.fillStyle = entry.accent ?? '#ffb074';
    ctx.font = '600 56px "Rajdhani", sans-serif';
    ctx.fillText(entry.role, 56, 200);
    ctx.fillStyle = '#cfc0a8';
    ctx.font = '500 42px "Rajdhani", sans-serif';
    ctx.fillText(entry.period ?? '', 56, 260);
    if (entry.location) ctx.fillText(entry.location, 56, 320);
    const tex = new THREE.CanvasTexture(canvas);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 8;
    const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false });
    const plank = new THREE.Mesh(new THREE.PlaneGeometry(2.6, 1.2), mat);
    plank.name = `experience-plank-${entry.company}`;
    plank.userData.noTorchRaycast = true;
    return plank;
  }

  // ── Skills: one decal canvas per artifact mesh in the observatory base ──
  #buildSkillsArtifacts() {
    // Find Blender meshes named skills_artifact_* — these are the
    // observatory's lectern/scrolls/books/chest. Drape a canvas panel above
    // each one with one Skills category baked into it.
    const artifacts = [];
    this.scene.traverse((o) => {
      if (o.isMesh && /^skills_artifact_/.test(o.name)) artifacts.push(o);
    });
    artifacts.sort((a, b) => a.name.localeCompare(b.name));
    const categories = skills.categories ?? skills; // accept either shape
    for (let i = 0; i < Math.min(categories.length, artifacts.length); i++) {
      const cat = categories[i];
      const artifact = artifacts[i];
      const panel = this.#makeSkillsPanel(cat);
      artifact.updateMatrixWorld(true);
      const box = new THREE.Box3().setFromObject(artifact);
      panel.position.set(
        (box.min.x + box.max.x) / 2,
        box.max.y + 0.8,
        (box.min.z + box.max.z) / 2,
      );
      panel.lookAt(this.skillsPosition);
      this.scene.add(panel);
    }
  }

  #makeSkillsPanel(category) {
    const canvas = document.createElement('canvas');
    canvas.width = 1024;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#2b1c12';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#ffb074';
    ctx.font = '700 84px "Oswald", sans-serif';
    ctx.fillText(category.title ?? category.name ?? '', 40, 96);
    ctx.fillStyle = '#f5e6d3';
    ctx.font = '500 42px "Rajdhani", sans-serif';
    const items = category.items ?? category.list ?? [];
    items.forEach((s, i) => {
      ctx.fillText(`• ${s}`, 40, 160 + i * 56);
    });
    const tex = new THREE.CanvasTexture(canvas);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 8;
    const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false });
    const panel = new THREE.Mesh(new THREE.PlaneGeometry(2.0, 1.0), mat);
    panel.name = `skills-panel-${category.title ?? category.name ?? ''}`;
    panel.userData.noTorchRaycast = true;
    return panel;
  }

  // ── Contact: inscription plinth gets a canvas decal facing the player ────
  #buildContactPlinth() {
    const plinth = this.scene.getObjectByName('contact_inscription_plinth');
    if (!plinth) return;
    plinth.updateMatrixWorld(true);
    const box = new THREE.Box3().setFromObject(plinth);
    const panel = this.#makeContactPanel();
    panel.position.set(
      (box.min.x + box.max.x) / 2,
      box.max.y + 0.5,
      (box.min.z + box.max.z) / 2,
    );
    panel.lookAt(0, panel.position.y, 0);  // face spawn
    this.scene.add(panel);
  }

  #makeContactPanel() {
    const canvas = document.createElement('canvas');
    canvas.width = 1024;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#2b1c12';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#ffb074';
    ctx.font = '700 96px "Oswald", sans-serif';
    ctx.fillText('Contact', 40, 120);
    ctx.fillStyle = '#f5e6d3';
    ctx.font = '500 48px "Rajdhani", sans-serif';
    (contact.lines ?? contact.entries ?? []).forEach((line, i) => {
      ctx.fillText(line, 40, 200 + i * 64);
    });
    const tex = new THREE.CanvasTexture(canvas);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 8;
    const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false });
    const panel = new THREE.Mesh(new THREE.PlaneGeometry(2.0, 1.0), mat);
    panel.name = 'contact-panel';
    panel.userData.noTorchRaycast = true;
    return panel;
  }

  // ── Resume lectern: open scroll mesh exists in .glb; we attach a glow ────
  #buildResumeLectern() {
    // The lectern mesh is already in the .glb (spec §4.1). We just bake a
    // 'Read resume' decal above it.
    if (!this.refs.interaction.resumeLectern) return;
    const pos = this.resumePosition;
    const canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 128;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#2b1c12';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#ffb074';
    ctx.font = '700 64px "Oswald", sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Read résumé', canvas.width / 2, 80);
    const tex = new THREE.CanvasTexture(canvas);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 8;
    const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false });
    const panel = new THREE.Mesh(new THREE.PlaneGeometry(1.4, 0.35), mat);
    panel.name = 'resume-decal';
    panel.position.copy(pos).add(new THREE.Vector3(0, 1.4, 0));
    panel.lookAt(0, panel.position.y, 0);
    panel.userData.noTorchRaycast = true;
    this.scene.add(panel);
  }

  // ── Proximity helpers (Interaction.js consumes these) ────────────────────
  nearContact(playerPosition, radius = PortfolioMounts.CONTACT_PROXIMITY) {
    if (!this.contactPosition) return null;
    const dx = playerPosition.x - this.contactPosition.x;
    const dz = playerPosition.z - this.contactPosition.z;
    if (dx * dx + dz * dz <= radius * radius) {
      return { kind: 'contact', position: this.contactPosition, data: contact };
    }
    return null;
  }

  nearResume(playerPosition, radius = PortfolioMounts.RESUME_PROXIMITY) {
    if (!this.resumePosition) return null;
    const dx = playerPosition.x - this.resumePosition.x;
    const dz = playerPosition.z - this.resumePosition.z;
    if (dx * dx + dz * dz <= radius * radius) {
      return { kind: 'resume', position: this.resumePosition, data: resume };
    }
    return null;
  }
}
```

### `src/Portfolio/ResumeData.js`

```js
/**
 * Placeholder resume content. Modal renders the `html` field; later sessions
 * can either swap the html for a real CV or wire `downloadUrl` to a PDF.
 */
export const resume = {
  title: 'Résumé',
  html: `
    <h1>Karan Mahajan</h1>
    <p class="lead">Full CV coming soon. In the meantime:</p>
    <ul>
      <li><a href="https://www.linkedin.com/in/karanmahajan321/" target="_blank" rel="noopener">LinkedIn</a></li>
      <li><a href="mailto:karanmahajan321@gmail.com">karanmahajan321@gmail.com</a></li>
    </ul>
  `,
  downloadUrl: null,
};
```

### `src/Portfolio/Interaction.js` — `nearResume` wiring

Add near the existing `nearContact` block (around line 191):

```js
// Pseudo-diff (find existing nearContact branch and add nearResume below):
const nearContact =
  this.signs && this.signs.nearContact(playerPosition, CONTACT_PROXIMITY);
const nearResume =
  this.signs && this.signs.nearResume?.(playerPosition, RESUME_PROXIMITY);
// Pick whichever is closer; if both, prefer resume (smaller proximity).
const nearbyNonProject = nearResume ?? nearContact;
```

Add constant near the top of `Interaction.js`:

```js
const RESUME_PROXIMITY = 4;
```

Add modal handling parallel to the contact case in `Interaction.js`'s `focus()` method — when `nearbyNonProject.kind === 'resume'`, render `data.html` into the modal body and hide the project nav (no carousel).

### `src/World/World.js` — Phase 2 wiring update

Replace the `this.signs = this.glb.signs` line with PortfolioMounts instantiation:

```js
// In World.loadAssets after await this.glb.load(physics) and setSectionPositions(refs):
import { PortfolioMounts } from '../Portfolio/PortfolioMounts.js';
// ...
this.portfolioMounts = new PortfolioMounts(this.scene, this.glb.refs, SECTION_POSITIONS);
this.signs = this.portfolioMounts;  // facade attribute used by App.js
```

### `.verify/scripts/verify-phase-2-mounts.mjs`

```js
// Phase 2 — confirm each portfolio mount triggers the right modal on
// proximity, achievements still fire, resume modal opens with placeholder.
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

await page.goto(URL, { waitUntil: 'load', timeout: 30000 });
await bootAndDismiss(page);

// Teleport sequentially to each section using the Teleport API exposed on
// __app for tests. Press E to open the modal; screenshot; close.
async function visit(label, teleportKey) {
  await page.evaluate((key) => window.__app.teleport.toSection(key), teleportKey);
  await page.waitForTimeout(900);
  await page.screenshot({ path: `${SHOTS}/p2-near-${label}.png` });
  await page.keyboard.press('KeyE');
  await page.waitForTimeout(500);
  await page.screenshot({ path: `${SHOTS}/p2-modal-${label}.png` });
  await page.keyboard.press('Escape');
  await page.waitForTimeout(400);
}
await visit('skills', 'skills');
await visit('experience', 'experience');
await visit('contact', 'contact');
await visit('resume', 'resume');

// Achievements panel still works.
await page.keyboard.press('KeyJ');
await page.waitForTimeout(400);
await page.screenshot({ path: `${SHOTS}/p2-achievements.png` });

const ach = await page.evaluate(() => window.__app.achievements?.getUnlocked?.()?.length ?? -1);

await browser.close();
const report = {
  shots_dir: SHOTS,
  unlocked_count: ach,
  errors,
  error_logs: logs.filter((l) => l.startsWith('[error]')),
};
console.log('\n=== PHASE 2 REPORT ===');
console.log(JSON.stringify(report, null, 2));
```

> If `__app.teleport.toSection(key)` doesn't accept a `'resume'` key, the subagent must extend `Teleport.toSection()` to look up `world.signs.resumePosition` for the `resume` case.

### Implementation tasks

- [ ] **Task 2.1: Branch + clean tree check** (`git status --porcelain` → empty).
- [ ] **Task 2.2: Write `src/Portfolio/ResumeData.js`** — full code above.
- [ ] **Task 2.3: Write `src/Portfolio/PortfolioMounts.js`** — full code above.
- [ ] **Task 2.4: Add `nearResume()` + RESUME_PROXIMITY + modal branch to `src/Portfolio/Interaction.js`** — diff above.
- [ ] **Task 2.5: Update `src/World/World.js`** — import + instantiate `PortfolioMounts`, assign to `this.signs`.
- [ ] **Task 2.6: Write `.verify/scripts/verify-phase-2-mounts.mjs`** — full code above.
- [ ] **Task 2.7: Run probe**

```bash
URL=http://localhost:5173/ NODE_PATH=/tmp/node_modules node .verify/scripts/verify-phase-2-mounts.mjs
```

- [ ] **Task 2.8: Report DONE.**

### User verification gate (Phase 2)

> **Phase 2 verification:**
>
> 1. `npm run dev` running.
> 2. Run probe → confirm:
>    - [ ] `errors` empty
>    - [ ] Screenshots `p2-modal-*.png` show distinct modals for skills / experience / contact / resume
>    - [ ] `p2-achievements.png` shows achievements panel rendering correctly
> 3. In browser, walk to each section. Confirm:
>    - [ ] Skills observatory shows category panels above each artifact
>    - [ ] Experience cairns each show a company plank
>    - [ ] Contact plinth shows the contact panel
>    - [ ] Resume lectern triggers a "Read résumé" prompt; pressing E opens modal with LinkedIn link
> 4. Open Achievements (J). Confirm panel renders with no errors.
>
> Reply **"Phase 2 approved"** or paste issues.

### Post-approval commit

```bash
rm src/Portfolio/Signs.js
git add \
  src/Portfolio/PortfolioMounts.js \
  src/Portfolio/ResumeData.js \
  src/Portfolio/Interaction.js \
  src/World/World.js \
  src/Portfolio/Signs.js \
  .verify/scripts/verify-phase-2-mounts.mjs

git commit -m "$(cat <<'EOF'
Phase 2: PortfolioMounts — Skills/Experience/Contact/Resume onto Blender refs

Replaces Signs.js. Skills decals mount over observatory artifacts; experience
planks float over cairn lanterns; contact panel sits on the inscription
plinth; new resume lectern interaction with placeholder modal (LinkedIn link
+ email — real CV swaps in later via ResumeData.js).
EOF
)"
```

---

## Phase 3: ProjectShowcase (replaces Billboards.js)

**Goal:** Single cycling showcase mounted on `refShowcaseMount` inside the workshop pavilion. Delete `Billboards.js` after verify.

### Files

- **Create:**
  - `src/Portfolio/ProjectShowcase.js`
  - `.verify/scripts/verify-phase-3-showcase.mjs`
- **Modify:**
  - `src/World/World.js` — instantiate `ProjectShowcase`, assign to `this.billboards`
  - `src/Portfolio/Interaction.js` — no changes (it reads `this.billboards.items[0]` + `closestWithin` which `ProjectShowcase` preserves)
- **Delete after user approval:**
  - `src/Portfolio/Billboards.js`

### Subagent dispatch prompt

```
Implement Phase 3 of the World v2 integration plan
(docs/superpowers/plans/2026-05-26-world-integration-build.md, Phase 3).

Phases 1 + 2 committed. Branch: world-v2-blender-build.

Read first:
- The plan's Phase 3 section
- src/Portfolio/Billboards.js (preserve PUBLIC API: items[] array with one
  entry, emissiveBoost, update(), setIndex(), setFocused(), closestWithin(),
  projects array, focused flag, transitioning flag)
- src/Portfolio/Interaction.js (consumer reads items[0].position, .accent,
  .project, .screen — preserve all four)

Your job:
1. Create src/Portfolio/ProjectShowcase.js per the plan — same canvas-baking
   logic as the old Billboards' #buildScreenTexture, but the screen mesh is
   ANCHORED to the position + rotation read from refShowcaseMount instead of
   being built from STATION_X/Z constants.
2. Update src/World/World.js to instantiate ProjectShowcase and expose it as
   this.billboards (replacing the GlbWorld stub).
3. Export PROJECTS_CENTER from ProjectShowcase as the showcase mount's XZ
   position (for backwards compat with any code that reads it).
4. Create .verify/scripts/verify-phase-3-showcase.mjs.

DO NOT delete Billboards.js. DO NOT commit. Report DONE.
```

### `src/Portfolio/ProjectShowcase.js` — module interface

```js
import * as THREE from 'three';
import gsap from 'gsap';
import { portfolio } from './PortfolioData.js';

/**
 * Single cycling project showcase. Mounts onto refShowcaseMount in the
 * workshop pavilion (Blender Phase 4). Preserves Billboards.js public API
 * so Interaction.js + TimeOfDay.js + ActionPrompts.js work unchanged.
 *
 * Visual: one 5×3m screen mesh painted with a per-project canvas (image +
 * name + summary + tags + arrows + counter). Canvas re-baked when
 * setIndex() rotates content.
 */
export class ProjectShowcase {
  static AUTO_ROTATE_SECONDS = 5;
  static NEAR_PAUSE_RADIUS = 8;
  static FADE_DURATION = 0.18;
  static SCREEN_WIDTH = 5;
  static SCREEN_HEIGHT = 3;

  constructor(scene, refs, loader = null, terrain = null) {
    this.scene = scene;
    this.loader = loader;
    this.terrain = terrain;

    this.projects = portfolio.projects;
    this.currentIndex = 0;
    this.transitioning = false;
    this.focused = false;
    this._autoTimer = 0;
    this._playerNearby = false;
    this.emissiveBoost = 1.0;

    const mount = refs.interaction.showcaseMount;
    if (!mount) {
      console.warn('[ProjectShowcase] refShowcaseMount missing — showcase will not render');
      this.items = [];
      this.group = null;
      return;
    }
    this.group = new THREE.Group();
    this.group.name = 'project-showcase';
    this.group.position.copy(mount.position);
    this.group.rotation.copy(mount.rotation);
    this.scene.add(this.group);

    this.items = [];
    this.#buildScreen();
    this.#applyIndex(0, /* immediate */ true);
    this.#kickOffImagePreload();
  }

  #buildScreen() {
    const canvas = document.createElement('canvas');
    canvas.width = 1024;
    canvas.height = 614;
    this._canvas = canvas;
    this._ctx = canvas.getContext('2d');

    const tex = new THREE.CanvasTexture(canvas);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 8;
    this._texture = tex;

    const mat = new THREE.MeshBasicMaterial({
      map: tex,
      transparent: false,
      depthWrite: true,
    });
    this._material = mat;

    const screen = new THREE.Mesh(
      new THREE.PlaneGeometry(ProjectShowcase.SCREEN_WIDTH, ProjectShowcase.SCREEN_HEIGHT),
      mat,
    );
    screen.name = 'project-showcase-screen';
    screen.userData.noTorchRaycast = true;
    this.group.add(screen);
    this._screen = screen;
  }

  #drawProject(project) {
    const ctx = this._ctx;
    const w = this._canvas.width;
    const h = this._canvas.height;
    ctx.fillStyle = '#1a120a';
    ctx.fillRect(0, 0, w, h);
    // Accent border
    ctx.strokeStyle = project.accent ?? '#ffb074';
    ctx.lineWidth = 12;
    ctx.strokeRect(6, 6, w - 12, h - 12);
    // Title
    ctx.fillStyle = '#f5e6d3';
    ctx.font = '700 88px "Oswald", sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText(project.name, 32, 96);
    // Summary
    ctx.fillStyle = '#cfc0a8';
    ctx.font = '500 36px "Rajdhani", sans-serif';
    const lines = wrapText(ctx, project.summary, w - 64);
    lines.forEach((line, i) => ctx.fillText(line, 32, 160 + i * 44));
    // Tech tags
    ctx.fillStyle = project.accent ?? '#ffb074';
    ctx.font = '600 28px "Rajdhani", sans-serif';
    ctx.fillText((project.tech ?? []).join(' · '), 32, h - 80);
    // Counter
    ctx.fillStyle = '#f5e6d3';
    ctx.font = '500 24px "Rajdhani", sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText(
      `${this.currentIndex + 1} / ${this.projects.length}`,
      w - 32, h - 32,
    );
    this._texture.needsUpdate = true;
  }

  #applyIndex(i, immediate = false) {
    this.currentIndex = ((i % this.projects.length) + this.projects.length) % this.projects.length;
    const project = this.projects[this.currentIndex];
    this.#drawProject(project);
    this.items.length = 0;
    this.items.push({
      index: this.currentIndex,
      position: this.group.position.clone(),
      accent: project.accent ?? '#ffb074',
      project,
      screen: this._screen,
    });
  }

  setIndex(i) {
    if (this.transitioning) return;
    this.transitioning = true;
    const mat = this._material;
    const orig = mat.opacity ?? 1.0;
    mat.transparent = true;
    gsap.to(mat, {
      opacity: 0,
      duration: ProjectShowcase.FADE_DURATION,
      onComplete: () => {
        this.#applyIndex(i);
        gsap.to(mat, {
          opacity: orig,
          duration: ProjectShowcase.FADE_DURATION,
          onComplete: () => {
            mat.transparent = false;
            this.transitioning = false;
          },
        });
      },
    });
  }

  setFocused(focused) { this.focused = focused; }

  closestWithin(playerPosition, radius) {
    const item = this.items[0];
    if (!item) return null;
    const dx = playerPosition.x - item.position.x;
    const dz = playerPosition.z - item.position.z;
    return dx * dx + dz * dz <= radius * radius ? item : null;
  }

  update(elapsed, playerPos = null, delta = 0) {
    if (!this.items[0] || this.focused) return;
    if (playerPos) {
      const dx = playerPos.x - this.items[0].position.x;
      const dz = playerPos.z - this.items[0].position.z;
      const near = dx * dx + dz * dz < ProjectShowcase.NEAR_PAUSE_RADIUS ** 2;
      this._playerNearby = near;
      if (near) return;
    }
    this._autoTimer += delta;
    if (this._autoTimer >= ProjectShowcase.AUTO_ROTATE_SECONDS) {
      this._autoTimer = 0;
      this.setIndex(this.currentIndex + 1);
    }
  }

  #kickOffImagePreload() {
    if (!this.loader || !this.projects) return;
    for (const p of this.projects) {
      if (p.image) this.loader.texture.load(p.image, undefined, undefined, () => {});
    }
  }
}

function wrapText(ctx, text, maxWidth) {
  const words = (text ?? '').split(/\s+/);
  const out = [];
  let line = '';
  for (const w of words) {
    const test = line ? `${line} ${w}` : w;
    if (ctx.measureText(test).width > maxWidth && line) {
      out.push(line);
      line = w;
    } else line = test;
  }
  if (line) out.push(line);
  return out.slice(0, 8);
}

// Backwards-compat export — some downstream code reads PROJECTS_CENTER.
export const PROJECTS_CENTER = { x: 70, z: 0, radius: 70 };
```

### `.verify/scripts/verify-phase-3-showcase.mjs`

```js
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

await page.goto(URL, { waitUntil: 'load', timeout: 30000 });
await bootAndDismiss(page);

// Teleport to projects.
await page.evaluate(() => window.__app.teleport.toSection('projects'));
await page.waitForTimeout(800);
await page.screenshot({ path: `${SHOTS}/p3-pavilion.png` });

// Confirm a single showcase item is present + cycling.
const idx0 = await page.evaluate(() => window.__app.world.billboards.items[0]?.index);
// Force cycle 3 times via setIndex.
for (let i = 1; i <= 3; i++) {
  await page.evaluate((n) => window.__app.world.billboards.setIndex(n), idx0 + i);
  await page.waitForTimeout(400);
  await page.screenshot({ path: `${SHOTS}/p3-cycle-${i}.png` });
}

// Press E to open the modal.
await page.keyboard.press('KeyE');
await page.waitForTimeout(500);
await page.screenshot({ path: `${SHOTS}/p3-modal.png` });
await page.keyboard.press('Escape');

const billboardsState = await page.evaluate(() => ({
  itemsLen: window.__app.world.billboards.items.length,
  hasGroup: !!window.__app.world.billboards.group,
  index: window.__app.world.billboards.items[0]?.index ?? -1,
  pos: window.__app.world.billboards.items[0]?.position,
}));

await browser.close();
console.log('\n=== PHASE 3 REPORT ===');
console.log(JSON.stringify({ shots_dir: SHOTS, billboardsState, errors,
  error_logs: logs.filter((l) => l.startsWith('[error]')) }, null, 2));
```

### Implementation tasks

- [ ] **Task 3.1:** Branch + clean tree check.
- [ ] **Task 3.2:** Write `src/Portfolio/ProjectShowcase.js` — full code above.
- [ ] **Task 3.3:** Update `src/World/World.js` — import `ProjectShowcase`, instantiate after `glb.load()`, assign to `this.billboards`.
- [ ] **Task 3.4:** Write `.verify/scripts/verify-phase-3-showcase.mjs`.
- [ ] **Task 3.5:** Run probe → confirm `billboardsState.itemsLen === 1`, `hasGroup === true`, modal opens.
- [ ] **Task 3.6:** Report DONE.

### User verification gate (Phase 3)

> 1. Run dev + probe.
> 2. Confirm:
>    - [ ] `p3-pavilion.png` shows the workshop pavilion with the showcase on the back wall
>    - [ ] `p3-cycle-1/2/3.png` show distinct projects (different titles, different accent colors)
>    - [ ] `p3-modal.png` shows the project modal opening cleanly
>    - [ ] `billboardsState.itemsLen === 1`
>    - [ ] No console errors
> 3. In browser: walk into the pavilion. Showcase auto-rotates every 5s while you're outside `NEAR_PAUSE_RADIUS = 8m`. Stand within 8m → rotation pauses.
>
> Reply **"Phase 3 approved"** or paste issues.

### Post-approval commit

```bash
rm src/Portfolio/Billboards.js
git add \
  src/Portfolio/ProjectShowcase.js \
  src/World/World.js \
  src/Portfolio/Billboards.js \
  .verify/scripts/verify-phase-3-showcase.mjs

git commit -m "$(cat <<'EOF'
Phase 3: ProjectShowcase — single cycling showcase mounted on refShowcaseMount

Replaces Billboards.js. Same per-project canvas treatment + cycle behaviour;
position + rotation now driven by the Blender mount ref, so the showcase
sits on the back wall of the workshop pavilion (Blender Phase 4) instead of
free-standing at hardcoded STATION_X/Z.
EOF
)"
```

---

## Phase 4: WorldLights (replaces StreetLights.js)

**Goal:** Ref-driven point lights at cairn lanterns + forge + brazier + lighthouse lamp. Day/night response. Distance-gated to ≤50m from player.

### Files

- **Create:**
  - `src/World/WorldLights.js`
  - `.verify/scripts/verify-phase-4-lights.mjs`
- **Modify:**
  - `src/App.js` — replace `StreetLights` import + construction; pass refs from `world.glb.refs`
  - `src/World/TimeOfDay.js` — small wiring change: `streetLights` → `worldLights` accessor (or alias)
- **Delete after user approval:**
  - `src/World/StreetLights.js`

### Subagent dispatch prompt

```
Implement Phase 4 of the World v2 integration plan
(docs/superpowers/plans/2026-05-26-world-integration-build.md, Phase 4).

Phases 1–3 committed. Branch: world-v2-blender-build.

Read first:
- The plan's Phase 4 section
- src/World/StreetLights.js (PRESERVE public API: setMode(mode, duration),
  update(playerPos))
- src/World/TimeOfDay.js (consumer; look for streetLights.setMode + update)

Your job:
1. Create src/World/WorldLights.js per the plan. The class reads refs
   (cairnLantern[], forge, brazier, lighthouseLamp). For each, create a
   THREE.PointLight; pool the 5 closest to the player each frame (Bruno-
   pattern, same as old StreetLights). Distance-gate at 50m.
2. Pulse the matching *_emissive mesh emissive intensity when its light is
   active.
3. Replace src/App.js StreetLights wiring: change the import + ctor +
   .load() call to use WorldLights. The .load() in old StreetLights was
   async (loaded GLB models); WorldLights is synchronous (lights only —
   the meshes already exist in the .glb).
4. Update src/World/TimeOfDay.js any references from this.streetLights →
   this.worldLights (or add alias).
5. Create .verify/scripts/verify-phase-4-lights.mjs.

DO NOT delete StreetLights.js. DO NOT commit. Report DONE.
```

### `src/World/WorldLights.js` — module interface

```js
import * as THREE from 'three';
import gsap from 'gsap';

/**
 * Replaces StreetLights.js. Point lights driven by Blender refs:
 *   refCairnLantern_1..7  → warm lantern lights
 *   refForge              → forge ember light
 *   refBrazier            → brazier flame light
 *   (lighthouse lamp pos derived from refLighthouseBeamPivot.parent.position)
 *
 * Distance-pool: 5 active PointLights, follow the closest 5 ref positions
 * each frame (same trick as StreetLights). Distance-gate: lights past 50m
 * from player contribute zero (intensity ramps to 0 via gsap on entry/exit
 * of the gate band).
 *
 * Day/night response: setMode('day'|'night', duration) tweens master
 * intensity 0 ↔ 1.
 */
export class WorldLights {
  static MAX_ACTIVE = 5;
  static LIGHT_DISTANCE = 12;
  static LIGHT_DECAY = 1.5;
  static GATE_RADIUS = 50;
  static LIGHT_COLOR = 0xffe8c0;
  static NIGHT_INTENSITY = 1.5;

  constructor(scene, refs) {
    this.scene = scene;
    this.refs = refs;
    this.mode = 'day';
    this._master = 0; // 0..1 tweened by setMode

    // Build ref position list: cairn lanterns + forge + brazier + lighthouse.
    this.anchors = [];
    for (const c of refs.lights.cairnLantern) {
      this.anchors.push({ name: c.name, position: c.position.clone(), kind: 'cairn' });
    }
    if (refs.lights.forge) {
      this.anchors.push({ name: 'forge', position: refs.lights.forge.clone(), kind: 'forge' });
    }
    if (refs.lights.brazier) {
      this.anchors.push({ name: 'brazier', position: refs.lights.brazier.clone(), kind: 'brazier' });
    }
    // Lighthouse lamp = the lamp mesh in the lighthouse group. Find by name.
    const lamp = scene.getObjectByName('lighthouse_lamp_emissive');
    if (lamp) {
      lamp.updateMatrixWorld(true);
      const p = new THREE.Vector3().setFromMatrixPosition(lamp.matrixWorld);
      this.anchors.push({ name: 'lighthouse', position: p, kind: 'lighthouse' });
    }

    // Pool of PointLights — reused, NOT one-per-anchor.
    this.pool = [];
    for (let i = 0; i < WorldLights.MAX_ACTIVE; i++) {
      const pt = new THREE.PointLight(WorldLights.LIGHT_COLOR, 0, WorldLights.LIGHT_DISTANCE, WorldLights.LIGHT_DECAY);
      pt.visible = false;
      pt.userData.noTorchRaycast = true;
      scene.add(pt);
      this.pool.push(pt);
    }

    // Resolve emissive meshes per anchor (name suffix matching).
    this.anchors.forEach((a) => {
      a.emissive = scene.getObjectByName(`${a.kind === 'cairn' ? a.name.replace('ref', '').replace(/Lantern_(\d+)$/, 'lantern_$1') : a.kind}_emissive`);
    });
  }

  /** Snap or tween to day/night mode. duration=0 snaps. */
  setMode(mode, duration = 0) {
    this.mode = mode;
    const target = mode === 'night' ? 1 : 0;
    if (duration === 0) {
      this._master = target;
    } else {
      gsap.to(this, { _master: target, duration, ease: 'sine.inOut' });
    }
  }

  /** Per-frame: pool the 5 closest anchors, apply distance gate + master. */
  update(playerPos) {
    if (!playerPos) return;
    // Distance-rank anchors.
    const ranked = this.anchors
      .map((a) => ({ a, d: a.position.distanceTo(playerPos) }))
      .sort((u, v) => u.d - v.d);

    // Assign top 5 to pool, hide the rest.
    for (let i = 0; i < this.pool.length; i++) {
      const pt = this.pool[i];
      const slot = ranked[i];
      if (!slot || slot.d > WorldLights.GATE_RADIUS) {
        pt.visible = false;
        pt.intensity = 0;
        continue;
      }
      pt.position.copy(slot.a.position).y += 0.1;
      pt.visible = this._master > 0.01;
      // Soft gate band: fade intensity from 0 at 50m to full at 30m.
      const gate = THREE.MathUtils.smoothstep(WorldLights.GATE_RADIUS - slot.d, 0, 20);
      pt.intensity = this._master * WorldLights.NIGHT_INTENSITY * gate;

      // Emissive mesh follows the light intensity (so the visible cap glows).
      if (slot.a.emissive?.material) {
        const m = slot.a.emissive.material;
        if (m.emissive) m.emissive.setHex(WorldLights.LIGHT_COLOR);
        m.emissiveIntensity = this._master * 1.5 + 0.05; // tiny baseline by day
      }
    }
  }

  dispose() {
    for (const pt of this.pool) this.scene.remove(pt);
    this.pool = [];
  }
}
```

### `src/App.js` — Phase 4 wiring

Replace lines around 12 (`import { StreetLights }`) → `import { WorldLights } from './World/WorldLights.js';`

In `boot()` around line 345–360, replace the StreetLights construction with:

```js
this.worldLights = new WorldLights(this.scene, this.world.glb.refs);
this.worldLights.setMode(this.timeOfDay.mode, 0);
// No async load — refs are already in glb. Keep streetLights ref for any
// stragglers (TimeOfDay still reads .streetLights in places).
this.streetLights = this.worldLights;
```

And in the tick loop where `this.streetLights.update(playerPos)` is called, swap to `this.worldLights.update(playerPos)` (the `streetLights` alias keeps any other reads working).

### `.verify/scripts/verify-phase-4-lights.mjs`

```js
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

await page.goto(URL, { waitUntil: 'load', timeout: 30000 });
await bootAndDismiss(page);

// Force night.
await page.evaluate(() => window.__app.timeOfDay.setMode('night', 0));
await page.waitForTimeout(800);
await page.screenshot({ path: `${SHOTS}/p4-night-spawn.png` });

// Visit each light source, screenshot.
async function visit(label, x, z) {
  await page.evaluate(([x, z]) => window.__app.teleport.toXZ?.(x, z) ?? window.__app.player.teleport(x, 0, z), [x, z]);
  await page.waitForTimeout(700);
  await page.screenshot({ path: `${SHOTS}/p4-night-${label}.png` });
}
// Cairn trail mid (read from refs).
const refs = await page.evaluate(() => {
  const r = window.__app.world.glb.refs;
  return {
    cairnPositions: r.lights.cairnLantern.map((c) => ({ x: c.position.x, z: c.position.z })),
    forge: r.lights.forge && { x: r.lights.forge.x, z: r.lights.forge.z },
    brazier: r.lights.brazier && { x: r.lights.brazier.x, z: r.lights.brazier.z },
  };
});
if (refs.cairnPositions.length) await visit('cairn-mid', refs.cairnPositions[Math.floor(refs.cairnPositions.length / 2)].x, refs.cairnPositions[Math.floor(refs.cairnPositions.length / 2)].z);
if (refs.forge) await visit('forge', refs.forge.x - 4, refs.forge.z);
if (refs.brazier) await visit('brazier', refs.brazier.x + 4, refs.brazier.z);
// Lighthouse view from spawn.
await page.evaluate(() => window.__app.player.teleport(0, 0, 0));
await page.evaluate(() => window.__app.playerCamera.lookAt(-130, 0, 35));
await page.waitForTimeout(600);
await page.screenshot({ path: `${SHOTS}/p4-night-lighthouse-view.png` });

// Force day.
await page.evaluate(() => window.__app.timeOfDay.setMode('day', 0));
await page.waitForTimeout(800);
await page.screenshot({ path: `${SHOTS}/p4-day-spawn.png` });

const poolState = await page.evaluate(() => ({
  poolSize: window.__app.worldLights?.pool?.length ?? 0,
  active: (window.__app.worldLights?.pool ?? []).filter((p) => p.visible).length,
  master: window.__app.worldLights?._master,
}));

await browser.close();
console.log('\n=== PHASE 4 REPORT ===');
console.log(JSON.stringify({ shots_dir: SHOTS, poolState, refs, errors,
  error_logs: logs.filter((l) => l.startsWith('[error]')) }, null, 2));
```

### Implementation tasks

- [ ] **Task 4.1:** Branch + clean tree check.
- [ ] **Task 4.2:** Write `src/World/WorldLights.js` — full code above.
- [ ] **Task 4.3:** Update `src/App.js` — import + ctor + tick call.
- [ ] **Task 4.4:** Update `src/World/TimeOfDay.js` — `this.streetLights` reads still work via the alias, but rename internal var if convenient.
- [ ] **Task 4.5:** Write `.verify/scripts/verify-phase-4-lights.mjs`.
- [ ] **Task 4.6:** Run probe → confirm `poolState.poolSize === 5`, `poolState.master` is 1 after `setMode('night', 0)`, lights visible in night screenshots.
- [ ] **Task 4.7:** Report DONE.

### User verification gate (Phase 4)

> 1. Run dev + probe.
> 2. Confirm:
>    - [ ] `p4-night-spawn.png`: visible warm halos in the distance
>    - [ ] `p4-night-cairn-mid.png`: cairn lantern emits visible light
>    - [ ] `p4-night-forge.png`: warm ember light inside the pavilion
>    - [ ] `p4-night-brazier.png`: brazier visible from approach
>    - [ ] `p4-night-lighthouse-view.png`: lighthouse lamp visible across water
>    - [ ] `p4-day-spawn.png`: lights are dimmed/off; emissive meshes still have faint glow
>    - [ ] `poolState.poolSize === 5`, `poolState.master === 1` after night, `0` after day
> 3. Manually toggle TOD button. Lights should fade in/out smoothly over the tween duration.
>
> Reply **"Phase 4 approved"** or paste issues.

### Post-approval commit

```bash
rm src/World/StreetLights.js
git add \
  src/World/WorldLights.js \
  src/World/StreetLights.js \
  src/App.js \
  src/World/TimeOfDay.js \
  .verify/scripts/verify-phase-4-lights.mjs

git commit -m "$(cat <<'EOF'
Phase 4: WorldLights — ref-driven point lights at cairn/forge/brazier/lighthouse

Replaces StreetLights.js. PointLight pool (5 active) follows the closest
Blender ref positions; intensity tweens on day↔night; distance-gated to
≤50m from player. Matching *_emissive meshes pulse in sync so the visible
glow cap reads correctly.
EOF
)"
```

---

## Phase 5: World shaders + animations

**Goal:** Apply `*water*`/`*waterfall*`/`*ocean*`/`*mountain*`/`*beam*` shaders, rotate lighthouse beam, animate per-instance foliage wind, extend `SmoothLitPaletteMaterial` to the full smooth-lit pipeline.

### Files

- **Create:**
  - `src/Materials/WaterShader.js`
  - `src/Materials/WaterfallShader.js`
  - `src/Materials/OceanShader.js`
  - `src/Materials/MountainShader.js`
  - `src/Materials/BeamShader.js`
  - `src/Effects/WorldWater.js`
  - `.verify/scripts/verify-phase-5-shaders.mjs`
- **Modify:**
  - `src/Materials/SmoothLitPaletteMaterial.js` — extend to full shader (per-instance wind phase, 3-band fog, palette sample)
  - `src/World/GlbWorld.js` — swap special-token materials at load
  - `src/World/World.js` — instantiate `WorldWater`, assign to `this.water`
  - `src/App.js` — wire `worldWater` into tick loop + TimeOfDay; rotate `refs.beam.lighthousePivot` in the tick loop (night-only)
- **Delete after user approval:**
  - `src/Effects/Water.js`

### Subagent dispatch prompt

```
Implement Phase 5 of the World v2 integration plan
(docs/superpowers/plans/2026-05-26-world-integration-build.md, Phase 5).

Phases 1–4 committed. Branch: world-v2-blender-build.

Read first:
- The plan's Phase 5 section
- src/Effects/Water.js (PRESERVE public API: contains(x,z), playerOverWater,
  setColor, tweenColor, applyTimeOfDay, update(elapsed, delta, playerPos,
  sample), preRender, audio property, setPhysics)
- docs/superpowers/specs/2026-05-26-world-design.md §10 + §6 + §7 for shader
  expectations

Your job:
1. Write the 5 shader files (Water, Waterfall, Ocean, Mountain, Beam) per
   the plan. Each is a thin ShaderMaterial subclass.
2. Extend SmoothLitPaletteMaterial to a full ShaderMaterial with: smooth
   Lambert (dot(N,L) clamped), 3-band fog (30/100/165m), per-instance wind
   phase via InstancedBufferAttribute, palette texture lookup, reveal-wipe
   uniform. Existing call sites keep working.
3. Write src/Effects/WorldWater.js. It discovers *waterfall* / *water* /
   *ocean* meshes in world.glb (already classified into
   GlbWorld._materialTokenMeshes), swaps each mesh's material for the right
   shader. Preserves Water.js public API.
4. Update src/World/GlbWorld.js: in #applyDefaultMaterials, swap special-
   token meshes to the right shader. Master shader applied to foliage and
   default meshes.
5. Update src/App.js: rotate refs.beam.lighthousePivot at 6 deg/sec during
   night mode only.
6. Update src/World/World.js: instantiate WorldWater after glb load.
7. Write .verify/scripts/verify-phase-5-shaders.mjs.

Per-shader cost budget: <2ms/frame on desktop. If any shader exceeds budget,
add a mobile fallback (skip the animation, fall back to flat palette material
on isMobile detection).

DO NOT delete Effects/Water.js. DO NOT commit. Report DONE.
```

### `src/Materials/SmoothLitPaletteMaterial.js` — Phase 5 full implementation

Replace the Phase 1 placeholder with:

```js
import * as THREE from 'three';

const VERT = /* glsl */`
  uniform float uTime;
  uniform vec3  uWindDir;
  uniform float uWindStrength;
  attribute float aWindPhase;   // per-instance (foliage); 0 for non-instanced

  varying vec3  vWorldPos;
  varying vec3  vNormal;
  varying vec2  vUv;

  void main() {
    vUv = uv;

    vec3 pos = position;
    // Wind displacement — only meaningful where Y > 0 (vertices above the
    // base of the object sway more than the trunk).
    float sway = sin(uTime * 1.5 + aWindPhase + pos.x * 0.2 + pos.z * 0.2);
    pos += uWindDir * sway * uWindStrength * max(0.0, pos.y * 0.15);

    vec4 worldPos = modelMatrix * vec4(pos, 1.0);
    vWorldPos = worldPos.xyz;
    vNormal = normalize(mat3(modelMatrix) * normal);
    gl_Position = projectionMatrix * viewMatrix * worldPos;
  }
`;

const FRAG = /* glsl */`
  uniform sampler2D uPalette;
  uniform vec2  uPaletteCell;   // (cellU, cellV) of base color in palette
  uniform vec3  uLightDir;
  uniform vec3  uAmbient;
  uniform vec3  uFogColor;
  uniform float uFogNear;
  uniform float uFogFar;
  uniform vec3  uReveal;        // (cx, cz, radius); radius<0 disables

  varying vec3 vWorldPos;
  varying vec3 vNormal;
  varying vec2 vUv;

  void main() {
    if (uReveal.z > 0.0) {
      float d = distance(vWorldPos.xz, uReveal.xy);
      if (d > uReveal.z) discard;
    }

    vec3 N = normalize(vNormal);
    float ndl = max(dot(N, normalize(uLightDir)), 0.0);
    vec3 baseColor = texture2D(uPalette, uPaletteCell).rgb;
    vec3 lit = baseColor * (uAmbient + ndl);

    // 3-band fog (smooth not linear).
    float fogFactor = smoothstep(uFogNear, uFogFar, length(vWorldPos - cameraPosition));
    vec3 col = mix(lit, uFogColor, fogFactor);

    gl_FragColor = vec4(col, 1.0);
  }
`;

/**
 * Master smooth-lit palette material. Used for default props + foliage.
 * Phase 5 extends Phase 1's placeholder.
 */
export class SmoothLitPaletteMaterial extends THREE.ShaderMaterial {
  constructor({ palette, cell = [0.5, 0.5], windDir = new THREE.Vector3(1, 0, 0), windStrength = 0.0 } = {}) {
    super({
      vertexShader: VERT,
      fragmentShader: FRAG,
      uniforms: {
        uTime:         { value: 0 },
        uPalette:      { value: palette ?? null },
        uPaletteCell:  { value: new THREE.Vector2(cell[0], cell[1]) },
        uWindDir:      { value: windDir },
        uWindStrength: { value: windStrength },
        uLightDir:     { value: new THREE.Vector3(0.4, 0.8, 0.3) },
        uAmbient:      { value: new THREE.Color('#aab2b5').toArray ? new THREE.Vector3(0.42, 0.45, 0.46) : new THREE.Vector3(0.4, 0.4, 0.4) },
        uFogColor:     { value: new THREE.Color('#e0d4c0') },
        uFogNear:      { value: 30 },
        uFogFar:       { value: 165 },
        uReveal:       { value: new THREE.Vector3(0, 0, -1) },
      },
    });
    this.userData = { isPaletteMaster: true };
  }

  setPlayerUniforms(uniforms) {
    if (uniforms?.uPlayerPos) this.uniforms.uPlayerPos = uniforms.uPlayerPos;
  }

  setTime(t) { this.uniforms.uTime.value = t; }
}
```

The remaining shader files (Water, Waterfall, Ocean, Mountain, Beam) follow the same pattern: each is a thin `ShaderMaterial` subclass with its own vertex/fragment pair. **Code skeleton for each** (subagent fills the shader bodies per world-design §10.2):

```js
// src/Materials/WaterShader.js
import * as THREE from 'three';

const VERT = /* glsl */`
  uniform float uTime;
  varying vec2  vUv;
  varying vec3  vWorldPos;
  void main() {
    vUv = uv;
    vec4 wp = modelMatrix * vec4(position, 1.0);
    vWorldPos = wp.xyz;
    gl_Position = projectionMatrix * viewMatrix * wp;
  }
`;

const FRAG = /* glsl */`
  uniform float uTime;
  uniform vec3  uShallow;       // #9ec5d6 glacial
  uniform vec3  uDeep;          // #5d8094
  uniform vec3  uFoam;          // #fff5dc
  uniform float uFlowSpeed;     // 0.1 m/s
  varying vec2  vUv;
  varying vec3  vWorldPos;
  void main() {
    // UV scroll along V (treat the ribbon's V as flow direction).
    vec2 uv = vUv + vec2(0.0, uTime * uFlowSpeed);
    // Foam at the edges (uUv.x near 0 or 1 → bank).
    float bank = smoothstep(0.85, 1.0, abs(vUv.x - 0.5) * 2.0);
    vec3 base = mix(uDeep, uShallow, smoothstep(0.0, 1.0, uv.y));
    vec3 col  = mix(base, uFoam, bank);
    gl_FragColor = vec4(col, 0.92);
  }
`;

export class WaterShader extends THREE.ShaderMaterial {
  constructor({ shallow = '#9ec5d6', deep = '#5d8094', foam = '#fff5dc' } = {}) {
    super({
      vertexShader: VERT, fragmentShader: FRAG, transparent: true, depthWrite: false,
      uniforms: {
        uTime: { value: 0 },
        uShallow: { value: new THREE.Color(shallow) },
        uDeep: { value: new THREE.Color(deep) },
        uFoam: { value: new THREE.Color(foam) },
        uFlowSpeed: { value: 0.1 },
      },
    });
  }
  setTime(t) { this.uniforms.uTime.value = t; }
}
```

Same skeleton for:
- `WaterfallShader.js` — replace fragment with vertical-stripe `step(fract(uv.y * 8.0 - uTime * 2.0), 0.5)` + foam mix.
- `OceanShader.js` — extends `WaterShader`, slower scroll (0.05), deeper tint, calm-surface sparkle via `sin(uTime + uv.x * 50.0) * 0.05` highlight.
- `MountainShader.js` — vertex shader unchanged from default; fragment uses `smoothstep(uFogNear, uFogFar, distance(vWorldPos, cameraPosition))` to dial alpha down by distance band.
- `BeamShader.js` — fragment is `alpha = pow(1.0 - vUv.y, 2.0) * 0.5`; `blending = THREE.AdditiveBlending`, `depthWrite = false`.

### `src/Effects/WorldWater.js`

```js
import * as THREE from 'three';
import gsap from 'gsap';
import { WaterShader } from '../Materials/WaterShader.js';
import { WaterfallShader } from '../Materials/WaterfallShader.js';
import { OceanShader } from '../Materials/OceanShader.js';

/**
 * Replaces Effects/Water.js. Walks the .glb's classified material-token
 * meshes and swaps in the matching shader.
 *
 * Preserves Water.js public API used by App.js + Player + Achievements:
 *   .contains(x, z) → boolean (player over water)
 *   .playerOverWater (boolean getter)
 *   .applyTimeOfDay(mode, opts)
 *   .update(elapsed, delta, playerPos, sample)
 *   .preRender(renderer, camera) — no-op
 *   .audio property (AudioManager attached by App.boot)
 *   .setPhysics(physics) — kept as no-op (no shore-decor colliders)
 *   .loadShoreDecor() — returns resolved promise (was for lily pads + reeds;
 *                       baked into .glb now)
 */
export class WorldWater {
  constructor(scene, glbWorld) {
    this.scene = scene;
    this.glb = glbWorld;
    this.playerOverWater = false;
    this.audio = null;
    this.mesh = null; // back-compat for App.js raycast filter

    // Swap materials.
    this._waterMats = [];
    for (const m of this.glb._materialTokenMeshes.water) {
      const mat = new WaterShader();
      m.material = mat;
      m.userData.noTorchRaycast = true;
      this._waterMats.push(mat);
      this.mesh = this.mesh ?? m; // first one is the "main" mesh for back-compat
    }
    for (const m of this.glb._materialTokenMeshes.waterfall) {
      m.material = new WaterfallShader();
      m.userData.noTorchRaycast = true;
      this._waterMats.push(m.material);
    }
    for (const m of this.glb._materialTokenMeshes.ocean) {
      m.material = new OceanShader();
      m.userData.noTorchRaycast = true;
      this._waterMats.push(m.material);
    }
  }

  setPhysics(_physics) { /* no shore-decor colliders */ }
  loadShoreDecor() { return Promise.resolve(); }
  preRender() { /* no reflection pass */ }

  contains(x, z) {
    // Over-water test = distance from origin > island radius (read from
    // terrain bbox). Cheap heuristic; spec is OK with this.
    const r = Math.hypot(x, z);
    return r > 45; // matches world-design §3
  }

  applyTimeOfDay(_mode, _opts) { /* shaders already adapt via uniforms */ }

  update(elapsed, delta = 0, playerPos = null) {
    for (const m of this._waterMats) m.setTime?.(elapsed);
    this.playerOverWater = playerPos ? this.contains(playerPos.x, playerPos.z) : false;
  }
}
```

### `src/App.js` — Phase 5 wiring

In the tick loop, find the existing `if (this.water) this.water.update(...)` line. The facade keeps `this.water` populated by World.loadAssets, but now point it at WorldWater. After the existing tick block, add the beam rotation:

```js
// Lighthouse beam (night-only): rotate refLighthouseBeamPivot 6°/sec.
const pivot = this.world.glb?.refs.beam.lighthousePivot;
if (pivot && this.timeOfDay.mode === 'night') {
  pivot.rotation.y += (6 * Math.PI / 180) * delta;
}
```

### `src/World/World.js` — Phase 5 wiring

After the GlbWorld load + portfolio mounts + showcase:

```js
import { WorldWater } from '../Effects/WorldWater.js';
// ...inside loadAssets()
this.worldWater = new WorldWater(this.scene, this.glb);
this.water = this.worldWater;
```

### `.verify/scripts/verify-phase-5-shaders.mjs`

```js
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

await page.goto(URL, { waitUntil: 'load', timeout: 30000 });
await bootAndDismiss(page);

// Walk to the river bridge for the water/waterfall shot.
await page.evaluate(() => window.__app.player.teleport(0, 0, 6));
await page.waitForTimeout(700);
await page.screenshot({ path: `${SHOTS}/p5-river.png` });
await page.waitForTimeout(800);
await page.screenshot({ path: `${SHOTS}/p5-river-later.png` });   // confirm UV scrolled (compare visually)

// Waterfall view (west cliff).
await page.evaluate(() => window.__app.player.teleport(-50, 0, 0));
await page.waitForTimeout(700);
await page.screenshot({ path: `${SHOTS}/p5-waterfall.png` });

// Mountains visible from spawn looking N.
await page.evaluate(() => window.__app.player.teleport(0, 0, 0));
await page.evaluate(() => window.__app.playerCamera.lookAt(0, 5, 100));
await page.waitForTimeout(400);
await page.screenshot({ path: `${SHOTS}/p5-mountains.png` });

// Lighthouse beam at night.
await page.evaluate(() => window.__app.timeOfDay.setMode('night', 0));
await page.evaluate(() => window.__app.playerCamera.lookAt(-130, 5, 35));
await page.waitForTimeout(400);
await page.screenshot({ path: `${SHOTS}/p5-beam-night-a.png` });
await page.waitForTimeout(1500); // beam should have swept ~9°
await page.screenshot({ path: `${SHOTS}/p5-beam-night-b.png` });
const pivotY = await page.evaluate(() => window.__app.world.glb?.refs.beam.lighthousePivot?.rotation.y);

// Foliage wind — close-up of a tree, sample uniform.
await page.evaluate(() => window.__app.player.teleport(15, 0, 30));
await page.evaluate(() => window.__app.timeOfDay.setMode('day', 0));
await page.waitForTimeout(400);
await page.screenshot({ path: `${SHOTS}/p5-foliage.png` });

await browser.close();
console.log('\n=== PHASE 5 REPORT ===');
console.log(JSON.stringify({ shots_dir: SHOTS, beam_rotation_y: pivotY, errors,
  error_logs: logs.filter((l) => l.startsWith('[error]')) }, null, 2));
```

### Implementation tasks

- [ ] **Task 5.1:** Branch + clean tree check.
- [ ] **Task 5.2:** Write 5 shader files: `src/Materials/{Water,Waterfall,Ocean,Mountain,Beam}Shader.js` — full skeletons above.
- [ ] **Task 5.3:** Extend `src/Materials/SmoothLitPaletteMaterial.js` to the full ShaderMaterial — code above.
- [ ] **Task 5.4:** Update `src/World/GlbWorld.js` `#applyDefaultMaterials` to swap special-token meshes to the right shader and apply the master to default meshes.
- [ ] **Task 5.5:** Write `src/Effects/WorldWater.js` — code above.
- [ ] **Task 5.6:** Wire `WorldWater` into `src/World/World.js`.
- [ ] **Task 5.7:** Add beam rotation tick into `src/App.js`.
- [ ] **Task 5.8:** Write `.verify/scripts/verify-phase-5-shaders.mjs`.
- [ ] **Task 5.9:** Run probe → confirm beam rotated (pivotY > 0 after night view), screenshots show motion, no errors.
- [ ] **Task 5.10:** Report DONE.

### User verification gate (Phase 5)

> 1. Run dev + probe.
> 2. Confirm:
>    - [ ] `p5-river.png` vs `p5-river-later.png`: water UV has scrolled (foam strip pattern in slightly different place)
>    - [ ] `p5-waterfall.png`: vertical stripes visible
>    - [ ] `p5-mountains.png`: mountains visibly faded by distance band
>    - [ ] `p5-beam-night-a.png` vs `p5-beam-night-b.png`: beam pivot has rotated ~9°
>    - [ ] `p5-foliage.png`: foliage visible, no z-fighting
>    - [ ] `beam_rotation_y > 0`
>    - [ ] No console errors
> 3. In browser at night, watch the lighthouse beam sweep continuously. Switch to day → beam stops.
> 4. Walk past the river → smooth flow animation, no judder.
>
> Reply **"Phase 5 approved"** or paste issues.

### Post-approval commit

```bash
rm src/Effects/Water.js
git add \
  src/Materials/WaterShader.js \
  src/Materials/WaterfallShader.js \
  src/Materials/OceanShader.js \
  src/Materials/MountainShader.js \
  src/Materials/BeamShader.js \
  src/Materials/SmoothLitPaletteMaterial.js \
  src/Effects/WorldWater.js \
  src/Effects/Water.js \
  src/World/GlbWorld.js \
  src/World/World.js \
  src/App.js \
  .verify/scripts/verify-phase-5-shaders.mjs

git commit -m "$(cat <<'EOF'
Phase 5: world shaders — water/waterfall/ocean/mountain/beam + lighthouse rotation

WorldWater replaces Effects/Water.js; discovers *water* / *waterfall* /
*ocean* meshes by material token and swaps in the right ShaderMaterial.
Mountain quads gain distance-band alpha fade. Lighthouse beam pivot rotates
6°/sec during night mode. SmoothLitPaletteMaterial extended with per-
instance wind phase + 3-band fog so foliage sways out of sync.
EOF
)"
```

---

## Phase 6: Particles (forge embers / brazier flame / waterfall spray)

**Goal:** Continuous low-cost particle systems anchored at refForge / refBrazier / refWaterfallSpray.

### Files

- **Create:**
  - `src/Effects/ForgeParticles.js`
  - `src/Effects/BrazierParticles.js`
  - `src/Effects/WaterfallSpray.js`
  - `.verify/scripts/verify-phase-6-particles.mjs`
- **Modify:**
  - `src/App.js` — instantiate the 3 particle systems after world.loadAssets, add their `update()` calls to the tick loop

### Subagent dispatch prompt

```
Implement Phase 6 of the World v2 integration plan
(docs/superpowers/plans/2026-05-26-world-integration-build.md, Phase 6).

Phases 1–5 committed. Branch: world-v2-blender-build.

Read first:
- The plan's Phase 6 section
- src/Effects/Fireflies.js (existing particle-pool pattern using
  THREE.Points + BufferGeometry + a ring-buffer write index — adopt
  the same pattern for low GC pressure)

Your job:
1. Write the three particle modules per the plan. Each uses a pre-allocated
   THREE.Points pool (no per-frame allocations), ring-buffer writes, and
   reads its anchor position from glb.refs.particles.<key>.
2. Wire them into App.js: instantiate after world.loadAssets, add
   update(delta, time) calls to the tick loop. All must respect the
   frame-time cap (delta arg).
3. prefers-reduced-motion handling: if matchMedia('(prefers-reduced-motion:
   reduce)').matches, particle systems still construct but their update()
   short-circuits (no spawn). Same for the lighthouse beam rotation in
   Phase 5 — if any subagent missed that, add the check there too.
4. Write .verify/scripts/verify-phase-6-particles.mjs.

DO NOT commit. Report DONE.
```

### `src/Effects/ForgeParticles.js`

```js
import * as THREE from 'three';

const COUNT = 60;          // small pool — embers + chimney smoke
const EMBER_LIFE = 1.2;
const SMOKE_LIFE = 2.5;

export class ForgeParticles {
  constructor(scene, anchor) {
    this.scene = scene;
    this.anchor = anchor.clone();
    this.enabled = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const geom = new THREE.BufferGeometry();
    const positions = new Float32Array(COUNT * 3);
    const ages = new Float32Array(COUNT);
    const types = new Float32Array(COUNT);  // 0=ember 1=smoke
    geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geom.setAttribute('aAge', new THREE.BufferAttribute(ages, 1));
    geom.setAttribute('aType', new THREE.BufferAttribute(types, 1));

    const mat = new THREE.PointsMaterial({
      size: 0.18, color: 0xffc46d, transparent: true, opacity: 0.85,
      blending: THREE.AdditiveBlending, depthWrite: false,
    });

    this.points = new THREE.Points(geom, mat);
    this.points.name = 'forge-particles';
    this.points.userData.noTorchRaycast = true;
    this.scene.add(this.points);

    this._positions = positions;
    this._ages = ages;
    this._types = types;
    this._write = 0;
    this._spawnAccum = 0;

    for (let i = 0; i < COUNT; i++) ages[i] = -1; // inactive
  }

  update(elapsed, delta) {
    if (!this.enabled || !delta) return;
    // Spawn one ember every ~120ms; one smoke wisp every ~400ms.
    this._spawnAccum += delta;
    while (this._spawnAccum > 0.12) {
      this._spawnAccum -= 0.12;
      this.#spawn(0);
      if (Math.random() < 0.3) this.#spawn(1);
    }
    // Integrate.
    for (let i = 0; i < COUNT; i++) {
      if (this._ages[i] < 0) continue;
      this._ages[i] += delta;
      const lifeMax = this._types[i] === 1 ? SMOKE_LIFE : EMBER_LIFE;
      if (this._ages[i] > lifeMax) { this._ages[i] = -1; continue; }
      const ix = i * 3;
      this._positions[ix + 1] += delta * (this._types[i] === 1 ? 0.9 : 1.4);
      this._positions[ix]     += delta * (Math.random() - 0.5) * 0.2;
      this._positions[ix + 2] += delta * (Math.random() - 0.5) * 0.2;
    }
    this.points.geometry.attributes.position.needsUpdate = true;
    this.points.geometry.attributes.aAge.needsUpdate = true;
  }

  #spawn(type) {
    const i = this._write;
    this._write = (this._write + 1) % COUNT;
    const ix = i * 3;
    this._positions[ix]     = this.anchor.x + (Math.random() - 0.5) * 0.25;
    this._positions[ix + 1] = this.anchor.y + 0.2;
    this._positions[ix + 2] = this.anchor.z + (Math.random() - 0.5) * 0.25;
    this._ages[i] = 0;
    this._types[i] = type;
  }
}
```

`BrazierParticles.js` and `WaterfallSpray.js` follow the same shape:
- **`BrazierParticles`** — flame (vertical jitter, warm color, additive blend) + smoke (east-drift via `+= windDir.x * delta`).
- **`WaterfallSpray`** — spawn with upward velocity from `anchor`, gravity pull, fade alpha to 0.

### `src/App.js` — Phase 6 wiring

After `await this.world.loadAssets(...)`:

```js
import { ForgeParticles } from './Effects/ForgeParticles.js';
import { BrazierParticles } from './Effects/BrazierParticles.js';
import { WaterfallSpray } from './Effects/WaterfallSpray.js';
// ...
const refs = this.world.glb?.refs;
if (refs?.particles.forgeSmoke) this.forgeParticles = new ForgeParticles(this.scene, refs.particles.forgeSmoke);
if (refs?.particles.brazierFlame) this.brazierParticles = new BrazierParticles(this.scene, refs.particles.brazierFlame, this.wind);
if (refs?.particles.waterfallSpray) this.waterfallSpray = new WaterfallSpray(this.scene, refs.particles.waterfallSpray);
```

In tick:
```js
if (this.forgeParticles) this.forgeParticles.update(elapsed, delta);
if (this.brazierParticles) this.brazierParticles.update(elapsed, delta);
if (this.waterfallSpray) this.waterfallSpray.update(elapsed, delta);
```

### `.verify/scripts/verify-phase-6-particles.mjs`

```js
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

await page.goto(URL, { waitUntil: 'load', timeout: 30000 });
await bootAndDismiss(page);

async function near(label, getXZ) {
  const xz = await page.evaluate(getXZ);
  if (!xz) return;
  await page.evaluate(([x, z]) => window.__app.player.teleport(x, 0, z), [xz.x + 3, xz.z]);
  await page.waitForTimeout(600);
  await page.screenshot({ path: `${SHOTS}/p6-${label}.png` });
}
await near('forge', () => {
  const p = window.__app.world.glb?.refs.particles.forgeSmoke;
  return p ? { x: p.x, z: p.z } : null;
});
await near('brazier', () => {
  const p = window.__app.world.glb?.refs.particles.brazierFlame;
  return p ? { x: p.x, z: p.z } : null;
});
await near('waterfall', () => {
  const p = window.__app.world.glb?.refs.particles.waterfallSpray;
  return p ? { x: p.x, z: p.z } : null;
});

const particleCounts = await page.evaluate(() => ({
  forge: window.__app.forgeParticles?.points?.geometry?.attributes.position.count ?? 0,
  brazier: window.__app.brazierParticles?.points?.geometry?.attributes.position.count ?? 0,
  spray: window.__app.waterfallSpray?.points?.geometry?.attributes.position.count ?? 0,
}));

await browser.close();
console.log('\n=== PHASE 6 REPORT ===');
console.log(JSON.stringify({ shots_dir: SHOTS, particleCounts, errors,
  error_logs: logs.filter((l) => l.startsWith('[error]')) }, null, 2));
```

### Implementation tasks

- [ ] **Task 6.1:** Branch + clean tree check.
- [ ] **Task 6.2:** Write `src/Effects/ForgeParticles.js` (above) + `BrazierParticles.js` + `WaterfallSpray.js` (same pattern).
- [ ] **Task 6.3:** Wire all three into `src/App.js`.
- [ ] **Task 6.4:** Add `prefers-reduced-motion` guard to lighthouse beam rotation in App.js (if not already in Phase 5).
- [ ] **Task 6.5:** Write `.verify/scripts/verify-phase-6-particles.mjs`.
- [ ] **Task 6.6:** Run probe → confirm screenshots show particles, no errors.
- [ ] **Task 6.7:** Report DONE.

### User verification gate (Phase 6)

> 1. Run dev + probe.
> 2. Confirm screenshots show:
>    - [ ] `p6-forge.png`: ember/smoke particles around the forge
>    - [ ] `p6-brazier.png`: flame + smoke trail drifting east
>    - [ ] `p6-waterfall.png`: spray plume at base
>    - [ ] `particleCounts.forge > 0`, `.brazier > 0`, `.spray > 0`
> 3. In browser: set OS to `prefers-reduced-motion: reduce`, reload — particles construct but no animation (no spawning).
>
> Reply **"Phase 6 approved"** or paste issues.

### Post-approval commit

```bash
git add \
  src/Effects/ForgeParticles.js \
  src/Effects/BrazierParticles.js \
  src/Effects/WaterfallSpray.js \
  src/App.js \
  .verify/scripts/verify-phase-6-particles.mjs

git commit -m "$(cat <<'EOF'
Phase 6: forge / brazier / waterfall particles — anchored on Blender refs

Three low-allocation Points pools driven by ref positions. Forge emits
ember + chimney smoke; brazier emits flame + east-drifting smoke; waterfall
spray plumes from the base. All respect prefers-reduced-motion + the
frame-time cap.
EOF
)"
```

---

## Phase 7: Tuning + cleanup + cross-device smoothness gate

**Goal:** Retune Sun / Fog / FOV / TimeOfDay per spec §9; audit dead imports; wire Grass flatten-positions to baked path samples; add `renderer.sortObjects = false` past 500-mesh threshold; cross-device smoothness probe.

### Files

- **Create:**
  - `.verify/scripts/verify-phase-7-smoothness.mjs`
- **Modify:**
  - `src/World/Sun.js`
  - `src/App.js` (fog, sortObjects, mobile fallback)
  - `src/Player/PlayerCamera.js` (FOV)
  - `src/World/TimeOfDay.js` (keyframes)
  - `src/World/Grass.js` (path-flatten or no-op)
  - `src/Portfolio/WorldMap.js` (audit hardcoded positions, point at SECTION_POSITIONS)
  - `src/UI/MiniMap.js`, `src/UI/MapMarkers.js`, `src/UI/Discovery.js` (audit)

### Subagent dispatch prompt

```
Implement Phase 7 of the World v2 integration plan
(docs/superpowers/plans/2026-05-26-world-integration-build.md, Phase 7).

Phases 1–6 committed. Branch: world-v2-blender-build.

Read first:
- The plan's Phase 7 section
- docs/superpowers/specs/2026-05-26-world-design.md §9 (target sun/fog/FOV
  values)
- All files in the Phase 7 'Modify' list

Your job:
1. Retune src/World/Sun.js: default elevation 12°, color #f4d6b0.
2. Retune src/App.js fog: color #e0d4c0, near=30, far=165.
3. Retune src/Player/PlayerCamera.js: default FOV 50°.
4. Retune src/World/TimeOfDay.js keyframes: dawn 0-40s, morning 40-100s,
   midday 100-160s, golden 160-200s, dusk 200-240s.
5. Audit src/Portfolio/WorldMap.js, src/UI/MapMarkers.js, src/UI/MiniMap.js,
   src/UI/Discovery.js for hardcoded section positions. Replace any that
   don't already read from SECTION_POSITIONS.
6. In src/World/Grass.js: if any code still references the old Paths.js
   tile positions, switch to glb.paths.getTilePositions(). If grass-flatten
   is no longer needed (perf cost was minor in old codebase), drop the
   logic entirely.
7. In src/App.js: after world.loadAssets resolves, if scene mesh count > 500,
   set this.renderer.sortObjects = false. Add manual renderOrder = 1 on the
   water mesh and renderOrder = 999 on PostFX layers.
8. Mobile fallback: in WorldWater, if matchMedia('(max-width: 900px)') or
   isMobile heuristic, skip the UV-scroll uniform update (just hold the
   shader at t=0). Same for MountainShader alpha fade — fall back to a
   constant per-band alpha on mobile.
9. Write .verify/scripts/verify-phase-7-smoothness.mjs.

DO NOT commit. Report DONE.
```

### `.verify/scripts/verify-phase-7-smoothness.mjs`

```js
// Cross-device smoothness probe. Three Chromium presets — desktop, laptop,
// mobile. For each: 300-frame fps + frame-time variance + screenshots.
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

const PRESETS = [
  { id: 'desktop', viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2, isMobile: false },
  { id: 'laptop',  viewport: { width: 1440, height: 900 },  deviceScaleFactor: 1.5, isMobile: false },
  { id: 'mobile',  viewport: { width: 390, height: 844 },   deviceScaleFactor: 3, isMobile: true, hasTouch: true },
];

const reports = [];
for (const p of PRESETS) {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    viewport: p.viewport, deviceScaleFactor: p.deviceScaleFactor,
    isMobile: p.isMobile, hasTouch: p.hasTouch ?? false,
  });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(`PAGEERROR: ${e.message}`));
  await page.goto(URL, { waitUntil: 'load', timeout: 30000 });
  await bootAndDismiss(page);
  await page.screenshot({ path: `${SHOTS}/p7-${p.id}-spawn.png` });
  // Walk N for 4s.
  await page.keyboard.down('KeyW');
  await page.waitForTimeout(4000);
  await page.keyboard.up('KeyW');
  await page.screenshot({ path: `${SHOTS}/p7-${p.id}-walked.png` });

  // Sample 300 frame-time deltas.
  const stats = await page.evaluate(() => new Promise((resolve) => {
    const deltas = [];
    let last = performance.now();
    let count = 0;
    function tick(t) {
      deltas.push(t - last);
      last = t;
      count++;
      if (count < 300) requestAnimationFrame(tick);
      else {
        const sum = deltas.reduce((a, b) => a + b, 0);
        const mean = sum / deltas.length;
        const varSum = deltas.reduce((a, b) => a + (b - mean) ** 2, 0);
        const stddev = Math.sqrt(varSum / deltas.length);
        resolve({ mean, stddev, ratio: stddev / mean, fps: 1000 / mean });
      }
    }
    requestAnimationFrame(tick);
  }));

  reports.push({ preset: p.id, stats, errors });
  await browser.close();
}
console.log('\n=== PHASE 7 REPORT ===');
console.log(JSON.stringify({ shots_dir: SHOTS, presets: reports }, null, 2));
```

### Implementation tasks

- [ ] **Task 7.1:** Branch + clean tree check.
- [ ] **Task 7.2:** Update `src/World/Sun.js` — elevation default 12°, color `#f4d6b0`.
- [ ] **Task 7.3:** Update `src/App.js` fog color/range per spec §9.
- [ ] **Task 7.4:** Update `src/Player/PlayerCamera.js` FOV to 50° default.
- [ ] **Task 7.5:** Update `src/World/TimeOfDay.js` keyframes per spec §9.
- [ ] **Task 7.6:** Audit `src/Portfolio/WorldMap.js`, `src/UI/MapMarkers.js`, `src/UI/MiniMap.js`, `src/UI/Discovery.js` — replace any hardcoded section coords with `SECTION_POSITIONS` imports from `src/World/SectionPositions.js`.
- [ ] **Task 7.7:** Update `src/World/Grass.js` — switch from any `Paths.js` reference to `world.paths.getTilePositions()` (already wired through facade).
- [ ] **Task 7.8:** Add `renderer.sortObjects = false` + manual `renderOrder` settings in `src/App.js` (after boot).
- [ ] **Task 7.9:** Mobile fallback for water/mountain shaders.
- [ ] **Task 7.10:** Write `.verify/scripts/verify-phase-7-smoothness.mjs`.
- [ ] **Task 7.11:** Run probe → confirm:
  - desktop: `fps ≥ 60`, `ratio < 0.20`
  - laptop: `fps ≥ 55`, `ratio < 0.20`
  - mobile: `fps ≥ 30`, `ratio < 0.20`
- [ ] **Task 7.12:** Report DONE.

### User verification gate (Phase 7)

> 1. Run dev + probe (cross-device).
> 2. Confirm smoothness report:
>    - [ ] Desktop preset: `fps >= 60`, `stddev/mean < 0.20`
>    - [ ] Laptop preset: `fps >= 55`, `stddev/mean < 0.20`
>    - [ ] Mobile preset: `fps >= 30`, `stddev/mean < 0.20`
>    - [ ] No `PAGEERROR` in any preset
> 3. In browser: end-to-end walk — spawn → all 5 sections → night cycle → rain on → thunderstorm. No console errors. Achievements panel still shows unlocks.
> 4. Map + click-to-teleport lands without colliders blocking the player.
> 5. Sky / fog / sun color match spec §9 (warm peach sun, mist-horizon fog).
>
> Reply **"Phase 7 approved"** to finalize. If approved, the next step is **your** call: merge `world-v2-blender-build` into `main` (or not — we can sit on the branch).

### Post-approval commit

```bash
git add \
  src/World/Sun.js \
  src/App.js \
  src/Player/PlayerCamera.js \
  src/World/TimeOfDay.js \
  src/World/Grass.js \
  src/Portfolio/WorldMap.js \
  src/UI/MapMarkers.js \
  src/UI/MiniMap.js \
  src/UI/Discovery.js \
  src/Effects/WorldWater.js \
  src/Materials/MountainShader.js \
  .verify/scripts/verify-phase-7-smoothness.mjs

git commit -m "$(cat <<'EOF'
Phase 7: tuning + cleanup + cross-device smoothness gate

Sun elevation 12° + warm peach color; fog #e0d4c0 30→165m; camera FOV 50°.
TimeOfDay dawn-window keyframes retuned. Map systems read SECTION_POSITIONS
via the ref-driven module. sortObjects=false past 500 meshes with manual
renderOrder on water + PostFX. Mobile fallback skips expensive shader work
on touch + narrow viewports.

Smoothness verified across desktop / laptop / mobile presets — frame-time
stddev/mean < 0.20 on all three; FPS clears 60/55/30 respectively.

End of World v2 integration on branch world-v2-blender-build. Merge to main
when user is ready.
EOF
)"
```

---

## Plan self-review

### Spec coverage

| Spec section | Plan coverage |
|---|---|
| §1.1 Blender wins | Module fate table; per-phase rewrites of Signs/Billboards/StreetLights/Water |
| §1.2 Contract preservation | Phase 1 facade preserves `world.terrain.heightAt`, `world.nature.pushSpots`, etc.; 18 downstream consumers unchanged |
| §1.3 Smoothness | Phase 7 cross-device gate; per-instance wind phase Phase 5; frame-time cap respected throughout |
| §1.4 Bruno's bar or better | Phase 7 FPS gates; post-Bruno upgrades baked into Phase 5 (per-instance wind), Phase 6 (`prefers-reduced-motion`) |
| §1.5 Workflow rule (never commit before verify) | Every phase has subagent dispatch with "DO NOT commit", user verification gate, post-approval commit block |
| §2 Architecture / loader pipeline | Phase 1: GlbWorld with 5-bucket walk + boot assertions |
| §3 Module fate table | Tasks 1.1–7.12 implement every row |
| §4 7-phase plan | One phase per row, all present |
| §5 Verification harness | Every phase has `.verify/scripts/verify-phase-N-<topic>.mjs` driver |
| §6 Performance contract | Phase 5 per-shader cost log; Phase 7 cross-device FPS + variance gate |
| §7 Smoothness stack | Phase 7 wires sortObjects=false, mobile fallback; frame-time cap unchanged in existing tick loop |
| §8 Risk register R1–R16 | Heightfield drift covered by Phase 1 21-point probe; missing ref by boot assertions; material token order by `MATERIAL_TOKEN_ORDER` array; collider drift by `addStaticCuboid` size sanity (Phase 1 visual probe); FPS regression by Phase 7; beam parenting by Phase 5 verify; achievements by Phase 2 + 3 verify; teleport-into-collider by Phase 7 |
| §9 Workflow rules | Encoded in every phase header |
| §10 What this design does NOT change | Player/Camera/Audio/UI/Achievements/Effects/Travel/Torch are all in the "unchanged" list and have no tasks |
| §11 Post-Bruno advancements | Per-instance wind (Phase 5), `prefers-reduced-motion` (Phase 6 + Phase 5 beam guard), `AbortController` on .glb fetch (gltf-loader uses `LoadingManager`; if subagent finds a clean integration point, add; else defer to a follow-up — not blocking), distance LOD on foliage (deferred to Phase 7 if FPS gate fails) |
| §12 Open questions, settled | All 8 settled items appear in the plan |

### Placeholder scan

Searched the plan for "TBD", "TODO", "fill in", "implement later", "add appropriate", "similar to". Found:
- "subagent fills the shader bodies per world-design §10.2" in Phase 5 — this is acceptable; the skeleton shows the pattern, and the spec section is referenced for the fragment-shader body. The subagent has enough to write each shader.
- Phase 6 references "same pattern as ForgeParticles" for Brazier and WaterfallSpray — full forge code is given. Acceptable because the pattern is shown in full once.
- "If subagent finds a clean integration point, add; else defer" for AbortController — acceptable as an explicitly optional item per the spec.

No blocking placeholders.

### Type consistency

- `glbWorld.terrain.heightAt(x, z)` signature is consistent across the plan (called by Player, Footprints, Leaves, Water, Interactables, ClickToMove, Teleport, Torch — unchanged) and the Phase 1 implementation.
- `glbWorld.nature.pushSpots` is `[{position, type, surfaceRadius, colliderRadius}]` in both the plan and the Phase 1 detector.
- `refs.section.<key>` returns a `Vector3` with a `.radius` property attached — used consistently by `SectionPositions.js` and `WorldLights.js`.
- `setSectionPositions(refs)` signature is consistent in `SectionPositions.js` and the World.js wiring call.
- `WorldLights.setMode(mode, duration)` matches `StreetLights.setMode(mode, duration)` exactly (preserves TimeOfDay's call site).
- `PortfolioMounts.nearContact(playerPos, radius)` matches the old `Signs.nearContact` signature; new `nearResume` mirrors it.
- `ProjectShowcase` preserves `items[]`, `emissiveBoost`, `update()`, `setIndex()`, `setFocused()`, `closestWithin()`, `projects`, `focused`, `transitioning` — all consumed by Interaction.js + TimeOfDay.js + ActionPrompts.js.
- `WorldWater` preserves `contains`, `playerOverWater`, `applyTimeOfDay`, `update`, `preRender`, `audio` property, `setPhysics`, `loadShoreDecor` — all consumed by App.js.

No type drift detected.

---

## Execution handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-26-world-integration-build.md`.

Two execution options follow the standard `writing-plans` handoff. Recommend **subagent-driven** for this work because:
- Each phase is naturally a fresh-context unit (the phases were designed for that during brainstorming).
- The user's hard workflow rule (no stage / no commit before verify) maps directly to the subagent-driven review checkpoint.
- The codebase already has the same rhythm in place from the Blender build (handoff doc references the same one-phase-per-subagent pattern).
