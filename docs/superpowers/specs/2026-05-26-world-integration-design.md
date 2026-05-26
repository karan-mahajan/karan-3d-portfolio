# World v2 — runtime integration design

**Date:** 2026-05-26
**Status:** Design complete; implementation plan pending
**Branch:** `world-v2-blender-build`
**Companion docs:**
- [World design spec](2026-05-26-world-design.md) — what the .glb contains and why
- [Blender build resume handoff](../handoffs/2026-05-26-blender-build-resume.md) — how the .glb was authored

## Scope

This spec describes how the **Blender-authored `static/world/world.glb`** (produced by Phases 0–13 of the Blender build) is integrated into the existing Three.js runtime, replacing the procedural world systems and adapting the portfolio-mount systems to consume Blender authoring.

### In scope
- Replacing `src/World/Terrain.js`, `src/World/Nature.js`, `src/World/Paths.js`, `src/World/DistantIslands.js` with a single `GlbWorld` loader
- Rewriting `src/Portfolio/Signs.js`, `src/Portfolio/Billboards.js`, `src/World/StreetLights.js`, `src/Effects/Water.js` to consume Blender meshes / refs / material tokens
- New shader variants for `*water*`, `*waterfall*`, `*ocean*`, `*mountain*`, `*beam*`, `*glass*` material tokens
- New runtime hooks for `*_emissive` meshes, `refLighthouseBeamPivot`, `refForge`, `refBrazier`, `refWaterfallSpray`, `refResumeInteractivePoint`, `refShowcaseMount`, `refCairnLantern_*`, `refHeroTree_*`
- Repositioning procedural `Interactables.js` (crate / bag / football) onto the new heightfield
- Ref-driven `SECTION_POSITIONS` (single source of truth, no more hardcoded constants)
- Preservation of the public API contract used by 18 downstream consumers (most critically `terrain.heightAt(x,z)`)
- Verification harness for each phase + cross-device smoothness gate

### Out of scope
- Re-authoring the .glb. The Blender file is complete. If a missing ref is discovered during Phase 1 verify, the user decides whether to re-export or work around in runtime.
- Wildlife module (deferred per world-design.md §16)
- Real resume / CV content (Phase 2 ships placeholder)
- New player animations, mini-map features, UI overhauls, achievement additions
- TSL / WebGPU migration (WebGL ShaderMaterial throughout)

---

## 1. Guiding principles

### 1.1 Blender wins
Where old runtime overlaps with .glb authoring, the runtime is rewritten to consume the Blender mesh / ref / material. Where the .glb is silent (player, camera, physics, audio, UI, weather, achievements, dynamic interactables), the runtime stays untouched.

### 1.2 Contract preservation
The new loader exposes the **same public API surface** the rest of the codebase consumes today. Most critically `terrain.heightAt(x, z)` is consumed in **18 files** (Player, Footprints, Leaves, Water particles, Interactables, ClickToMove, Teleport, TorchLight, plus Signs/Billboards/StreetLights internals). The new loader provides this function with identical signature and semantics so those 18 files need no edits.

### 1.3 Smoothness over peak FPS
The site must feel smooth on a company laptop, a personal laptop, and mobile — not just hit a peak FPS number. This is the reason the world was authored in Blender: replace per-frame procedural cost with one-time load cost. Smoothness mechanisms are listed in §8.

### 1.4 Bruno's bar or better
Where Bruno's 2022 approach is still optimal, we adopt it (palette texture, name-prefix dispatch, instanced foliage, frame-time cap). Where modern Three.js / Web APIs offer a clearly better result, we use the modern path. Specific advancements in §11.

### 1.5 Hard workflow rule — never commit before user verifies
Per the user's explicit instruction:
- Subagents write code, stage **nothing**, commit **nothing**.
- Each phase ends with a subagent report + a verification walkthrough handed to the user.
- The user verifies in browser. If issues, we fix and re-verify.
- Only on explicit "Phase N approved" → controller commits.
- No `Co-Authored-By: Claude` trailer (per memory `feedback_no_claude_coauthor`).
- All work stays on `world-v2-blender-build` until the final merge decision.

---

## 2. Architecture

### 2.1 New top-level module — `GlbWorld`

Lives at `src/World/GlbWorld.js`. Constructed in `App.boot()` where `World` is today. Constructor stays synchronous; async `load()` does the GLTF parse + bucket walk + assertions.

`World.js` is reduced to a thin facade that instantiates `GlbWorld`, the portfolio-mount modules, and `WorldWater` / `WorldLights`. The facade preserves the `world.terrain`, `world.nature`, `world.paths`, `world.billboards`, `world.signs`, `world.water` attribute names that `App.js` and downstream code already use.

### 2.2 Loader pipeline (executed once at boot)

```
GLTFLoader → static/world/world.glb (already KTX2+Draco-pipelined)
                                │
       ┌────────────────────────┼────────────────────────┐
       ▼                        ▼                        ▼
  Scene walk             Material pass            Instancing pass
       │                        │                        │
       ├─ Terrain submesh       ├─ *waterfall* → WaterfallShader
       │  → bake 193×193 grid   ├─ *water* → WaterShader
       │  → expose heightAt()   ├─ *ocean* → OceanShader
       │  → Physics ground      ├─ *mountain* → MountainShader
       │                        ├─ *beam* → BeamShader
       ├─ cuboid_* → static     ├─ *glass* → GlassMaterial
       │  cuboid collider       ├─ *_emissive (name suffix) →
       ├─ tube_* → static       │  EmissiveMaterial
       │  cylinder collider     └─ default → SmoothLitPaletteMaterial
       ├─ trimesh_* → static
       │  trimesh collider               Shared mesh datablocks
       │  (hide source mesh)             → InstancedMesh per source
       │
       ├─ ref* empties → typed ref map
       │  refs.section.{spawn,projects,experience,skills,contact}
       │  refs.lights.cairnLantern[1..7]
       │  refs.lights.forge / brazier / lighthouseLamp
       │  refs.beam.lighthousePivot
       │  refs.particles.{forgeSmoke,brazierFlame,waterfallSpray}
       │  refs.interaction.{resumeLectern,showcaseMount}
       │  refs.viewpoint.{nw,summit,se}
       │  refs.foliage.heroTree[1..5]
       │  refs.foliage.bench[1..3]
       │
       └─ Push-spot detection by mesh-name regex
          pine_* / birch_* / hero_tree_* / cairn_* /
          sign_* / waystone_* / bench_* / boulder_*
          → bbox → surfaceRadius
          → world.nature.pushSpots
                       │
                       ▼
            Boot-time assertions (loud fail)
                       │
                       ▼
                Resolve load promise
```

### 2.3 Boot assertions (halt with clear message on failure)

The loader does **not** silently fall back when authoring conventions break. Each missing item is identified by name in the error:

- `terrain` submesh present + has ≥193×193 vertices on a regular XZ grid
- All 5 `refZoneBounding_{spawn,projects,experience,skills,contact}` empties present
- `refShowcaseMount`, `refResumeInteractivePoint`, `refLighthouseBeamPivot` present
- ≥4 `refCairnLantern_*`, ≥1 `refForge`, ≥1 `refBrazier`
- All expected material tokens resolved exactly once (no orphans, no double-matches)
- ≥50 push-spot meshes auto-detected (smoke test that mesh-name conventions held)
- Material token check order: `waterfall` → `water` → `ocean` → `mountain` → `beam` → `glass` → default (prevents `*water*` from matching `waterfall`)

### 2.4 Public API contract (what downstream code reads)

```js
glbWorld.terrain.heightAt(x, z)         // baked heightfield bilinear lookup
glbWorld.terrain.size / segments        // for Physics.addStaticGround
glbWorld.nature.pushSpots               // [{position, type, surfaceRadius, colliderRadius}]
glbWorld.nature.addExclusion(x, z, r)   // no-op (foliage baked; concept retired)
glbWorld.nature.setPlayerUniforms(u)    // forwards to instanced foliage materials
glbWorld.paths.getTilePositions()       // Float32Array sampled along baked path ribbons
glbWorld.paths.getTileCount()           // matches above (note: paths/billboards/signs
                                        //   are sub-objects on GlbWorld, NOT separate
                                        //   modules — the old Paths.js/Signs.js/
                                        //   Billboards.js modules are deleted/rewritten)
glbWorld.billboards.items[0]            // the single ProjectShowcase item
glbWorld.signs.experienceItems          // cairn anchors (used by Achievements)
glbWorld.signs.skillsPosition           // = refs.section.skills (Vector3)
glbWorld.signs.contactPosition          // = refs.section.contact
glbWorld.refs                           // NEW typed ref accessor (see §2.2)
```

A new module `src/World/SectionPositions.js` exposes the populated `SECTION_POSITIONS` constants the moment `glbWorld.load()` resolves. Existing imports from `Signs.js` are redirected to this module in Phase 1.

---

## 3. Module fate table

| Old module | New state | Reason |
|---|---|---|
| `World/Terrain.js` | **DELETED** end of Phase 1 | Replaced by `GlbWorld.terrain.heightAt(x,z)` baked from the 193×193 terrain submesh |
| `World/Nature.js` | **DELETED** end of Phase 1 | Foliage baked into .glb; push-spots auto-detected from mesh-name regex |
| `World/Paths.js` | **DELETED** end of Phase 1 | Path ribbons baked into .glb; tile positions sampled along the ribbon mesh |
| `World/DistantIslands.js` | **DELETED** end of Phase 1 | Mountains + lighthouse + islet baked into .glb; `DistanceGame.js` redirected to read island descriptors from `glbWorld.refs.viewpoint.*` |
| `Portfolio/Signs.js` | **REWRITTEN** as `Portfolio/PortfolioMounts.js` in Phase 2 | Skills signs become observatory artifacts; experience signs become cairns; contact sign becomes plinth; resume lectern added |
| `Portfolio/Billboards.js` | **REWRITTEN** as `Portfolio/ProjectShowcase.js` in Phase 3 | Single cycling showcase mounted on `refShowcaseMount` in the workshop pavilion |
| `World/StreetLights.js` | **REWRITTEN** as `World/WorldLights.js` in Phase 4 | Ref-driven point lights at cairn lanterns + forge + brazier + lighthouse lamp |
| `Effects/Water.js` | **REWRITTEN** as `Effects/WorldWater.js` in Phase 5 | Finds `*water*`/`*waterfall*`/`*ocean*` meshes via material token; old shore-decor placement (lily pads, reeds) is dropped — the new shore is baked |
| `World/World.js` | **REDUCED TO FACADE** in Phase 1 | Wraps the new `GlbWorld` + `PortfolioMounts` + `ProjectShowcase` + `WorldLights` + `WorldWater` modules and re-exposes the legacy attribute names so `App.js` and downstream code don't need to rewrite |
| `Portfolio/Interactables.js` | **KEPT procedural**; positions adjusted in Phase 1 | Crate, bag, football are dynamic Rapier bodies — not authorable in Blender; reposition onto the new heightfield |
| `World/Grass.js` | **KEPT**; Phase 7 tunes flatten-positions to sample along baked path ribbons | Grass blades stay shader-driven |
| `World/Sky.js`, `Sun.js`, `TimeOfDay.js`, `Wind.js`, `Palette.js` | **KEPT**; Phase 7 retunes values per world-design spec §9 | Tuning only |
| Player / Camera / Physics / Audio / UI / Achievements / Effects (Fireflies, Rain, Thunderstorm, Leaves, Footprints, WindLines, PostFX) / Travel / Torch | **UNTOUCHED** | They only consume `heightAt` + section positions, which the loader preserves |

---

## 4. Phase plan

7 phases, each = one verifiable chunk + one commit (after user approval). Phase 1 carries ~60% of the integration risk.

### Phase 1 — MVS swap (load + replace + reposition)

**Deliverables**
- `src/World/GlbWorld.js` — full loader pipeline per §2
- `src/World/SectionPositions.js` — ref-driven section position exports
- `src/Materials/SmoothLitPaletteMaterial.js` — master material per world-design §10.1 (smooth Lambert + palette sample + distance-band fog + reveal-wipe uniform). Special shaders deferred to Phase 5; everything renders with this material in Phase 1.
- `src/Portfolio/Interactables.js` — positions updated to sit on new heightfield
- `src/World/World.js` — reduced to thin facade that wraps `GlbWorld` and preserves the `world.terrain`, `world.nature`, `world.paths`, `world.billboards`, `world.signs`, `world.water` attribute names already used in `App.js`
- `src/App.js` — wiring updated to use `GlbWorld` via the `World` facade; no consumer-side rewrites required

**Phase 1 verification gates**
1. Boot smoke: `npm run dev` shows `GlbWorld load: OK` and no console errors.
2. Numeric probe: 21 sample points — spawn (1), four ±70 cardinals (4), four perimeter-trail points (N/E/S/W at r≈80) (4), four shore-edge points at r≈45 (4), four water-boundary points at r≈60 (4), three viewpoint locations (NW/summit/SE) (3), lighthouse islet (-130, +35) (1). Assert `glbWorld.terrain.heightAt(x, z)` matches a downward raycast against the terrain submesh within **±0.01m**.
3. Grounded probe: synthetic-tick driver places marker at `heightAt(x,z) + 0.001`, runs one physics step, asserts `grounded === true`.
4. Walk probe: synthetic ticks drive player through N→spawn→E→spawn→S→spawn→W→spawn; assert grounded throughout, no fall-through.
5. Cardinal-section screenshots written to `.verify/shots/YYYY-MM-DD/phase-1-{spawn,projects,experience,skills,contact}.png`.
6. Push-spot count ≥50 logged.
7. All boot assertions passed.

**After user approval:** delete `Terrain.js`, `Nature.js`, `Paths.js`, `DistantIslands.js`. Commit.

### Phase 2 — `PortfolioMounts` (replaces `Signs.js`)

**Deliverables**
- `src/Portfolio/PortfolioMounts.js` — reads `refSkillsArtifact_*`, `refExperienceCairn_*` (or the 7 cairn lantern refs as anchors), `refContactPlinth`, `refResumeInteractivePoint`. Mounts portfolio content (Skills / Experience / Contact / new placeholder Resume) onto Blender meshes.
- `src/Portfolio/ResumeData.js` — stub content per world-design §4.1
- `src/Portfolio/Interaction.js` extended to register the resume lectern

**Phase 2 verification gates**
1. Walking to each section opens its modal correctly.
2. Achievements panel still records first-visit unlocks (the 34-unlock system reads `refZoneBounding_*` via `SectionPositions.js`).
3. Resume lectern interaction prompt + placeholder modal opens.

**After user approval:** delete `Signs.js`. Commit.

### Phase 3 — `ProjectShowcase` (replaces `Billboards.js`)

**Deliverables**
- `src/Portfolio/ProjectShowcase.js` — single cycling showcase mounted on `refShowcaseMount` (position + rotation read from the ref). Cycle behaviour identical to current `Billboards`; only the mount source changes.

**Phase 3 verification gates**
1. Player enters workshop pavilion, sees showcase cycling at the back wall.
2. Showcase faces the player's natural approach direction (read `refShowcaseMount.rotation`).
3. Existing project interaction modal still opens.

**After user approval:** delete `Billboards.js`. Commit.

### Phase 4 — `WorldLights` (replaces `StreetLights.js`)

**Deliverables**
- `src/World/WorldLights.js` — point lights instantiated at `refCairnLantern_1..7`, `refForge`, `refBrazier`, lighthouse lamp position (read from the lighthouse cupola child). Day/night intensity + color driven by `TimeOfDay`. Distance-gated: lights past 50m from player stop contributing.
- `*_emissive` meshes get their emissive intensity uniform pulsed in sync with the matching point light (so the visible mesh glows when the light is on).

**Phase 4 verification gates**
1. Force night via TimeOfDay debug — 7 cairn lanterns visibly emit warm light.
2. Forge ember light visible inside pavilion (refForge).
3. Brazier light visible from spawn through fog (refBrazier).
4. Lighthouse lamp visible from spawn at night.
5. Day mode dims all to baseline; emissive meshes still glow faintly per world-design §4.

**After user approval:** delete `StreetLights.js`. Commit.

### Phase 5 — World shaders + animations

**Deliverables**
- `src/Materials/WaterShader.js` — UV-scroll along curve direction at ~0.1 m/s, foam strip at edges (world-design §7.2)
- `src/Materials/WaterfallShader.js` — vertical-stripe scroll (world-design §7.3)
- `src/Materials/OceanShader.js` — deeper color, calm surface
- `src/Materials/MountainShader.js` — distance-fog override + alpha fade per band (world-design §6)
- `src/Materials/BeamShader.js` — low-opacity additive cone (world-design §4.6)
- `src/Effects/WorldWater.js` — replaces `Effects/Water.js`; finds `*water*`/`*waterfall*`/`*ocean*` meshes and applies the right shader
- `refLighthouseBeamPivot` rotated at ~6°/s by App tick loop (night-only — see §5.1 advancements below)
- Wind displacement (shared `windNode`) applied to `SmoothLitPaletteMaterial` for instanced foliage + `refHeroTree_*`. Per-instance phase offset via `InstancedBufferAttribute` (post-Bruno upgrade, see §11) so trees don't all sway in sync.

**Phase 5 verification gates**
1. Walk to river — water shows UV scroll motion in N→W direction with foam at edges.
2. Watch waterfall — vertical stripes scroll downward.
3. Walk away — mountains visibly fade by distance band.
4. Night — lighthouse beam sweeps at ~6°/s and is suppressed in daytime.
5. Foliage sways with wind; trees are out of phase with each other (not synchronized).
6. Per-shader cost log: each special shader <2ms/frame on desktop preset.

**After user approval:** delete `Effects/Water.js`. Commit.

### Phase 6 — Particles

**Deliverables**
- `src/Effects/ForgeParticles.js` — continuous ember + chimney smoke wisp at `refForge`
- `src/Effects/BrazierParticles.js` — flame particle + east-drifting smoke at `refBrazier`
- `src/Effects/WaterfallSpray.js` — spray plume at `refWaterfallSpray` (extends existing particle pattern from `Effects/Water.js`)

**Phase 6 verification gates**
1. Walk near forge — ember + chimney smoke visible.
2. Walk near brazier — flame + east-drifting smoke (matches wind direction).
3. Walk near waterfall — spray plume visible at base.
4. All particles obey global frame-time cap (no judder when FPS dips).

### Phase 7 — Tuning + cleanup + smoothness gate

**Deliverables**
- `Sun.js` elevation 12°, color `#f4d6b0` (world-design §9)
- `App.js` fog `#e0d4c0`, range 30/100/165m bands (world-design §9)
- `PlayerCamera.js` FOV 50°
- `TimeOfDay.js` keyframes retuned per world-design §9 (dawn 0–40s, morning 40–100s, midday 100–160s, golden 160–200s, dusk 200–240s)
- `WorldMap.js` / `MapMarkers.js` / `MiniMap.js` / `Discovery.js` audited and updated if any still hardcode section positions
- `Grass.js` flatten-positions wired to path-ribbon samples (or dropped if perf-cheap)
- Dead Kenney-model imports removed from `static/models/` references (audit pass)
- `renderer.sortObjects = false` once world mesh count exceeds 500
- Mobile fallback flag added: skip expensive shaders (water UV scroll, mountain alpha fade) on `isMobile` if Phase 5 cost log showed >2ms/frame on mobile

**Phase 7 verification gates**
1. End-to-end walk: spawn → all 5 sections → night cycle → rain → thunderstorm → no console errors.
2. All 34 achievements firable (Achievements panel opens, unlocks list visible).
3. Mini-map + click-to-teleport land on intended targets without colliding into new geometry (Navmask rebuilds against new colliders).
4. Cross-device smoothness probe (see §6 below).

---

## 5. Verification harness

### 5.1 Per-phase pattern

Every phase produces three artifacts before the user is asked to approve:

1. **Boot smoke** — `npm run dev`, watch console for errors and "GlbWorld load: OK".
2. **Synthetic-tick driver** — `.verify/scripts/verify-phase-<n>.mjs` runs in headless Chromium, pumps `bag.update(1/30)` ticks (per memory `feedback_verify_synthetic_ticks` — headless rAF throttles).
3. **Phase-specific gates** as enumerated above.

Driver must:
- Use `bootAndDismiss(page)` from `.verify/scripts/_boot.mjs`
- Compute shots dir at runtime via `new Date().toISOString().slice(0, 10)` (per memory `feedback_verify_layout_standing`)
- Write to `.verify/shots/YYYY-MM-DD/<phase-name>-<probe>.png`

### 5.2 Cross-device smoothness gate (Phase 7)

Three Chromium presets — each writes its own FPS log + screenshot:

| Preset | Width × Height | DPR | Mobile? |
|---|---|---|---|
| Desktop | 1920 × 1080 | 2 | false |
| Laptop | 1440 × 900 | 1.5 | false |
| Mobile | 390 × 844 | 3 | true (touch + orientation) |

For each preset, capture 300 frames after spawn settles, then assert:
- **Mean FPS** matches §6 budgets per preset.
- **Frame-time variance**: `stddev / mean < 0.2` (Bruno's site sits around 0.15). High variance = juddering even at high mean FPS.
- **No-regression**: spot-check that the new world is at least as smooth as the procedural world on the same machine (run once each before/after the MVS swap).

---

## 6. Performance contract

### 6.1 Budgets (Bruno's bar or better)

| Metric | Bar |
|---|---|
| Desktop FPS at midday | ≥60 |
| Desktop FPS at night with all warm lights on | ≥58 |
| Laptop FPS at midday | ≥55 |
| Mobile FPS at midday | ≥30 (≥45 if reachable) |
| Static draw calls | <80 |
| Total triangles | <100,000 |
| Materials (unique) | <12 |
| Texture memory | <8 MB |
| Frame-time variance (stddev/mean) | <0.20 |
| Per-shader compile time | <50ms |
| Per-shader frame cost (desktop) | <2ms |
| `.glb` parse time on a cold cache | <800ms |

### 6.2 Heightfield bake cost budget

- Vertex extraction from terrain submesh: O(N) where N=193×193≈37k. Budget: <50ms.
- Stored as Float32Array(N) + small lookup metadata. Memory: ~150KB.
- `heightAt(x,z)` per call: O(1) bilinear lookup against the stored grid. Budget: <1µs per call (matches existing `Terrain.heightAt`).

---

## 7. Smoothness stack (the reason this site feels good)

All mechanisms below are required, not optional. Each phase that adds code follows them; Phase 7 audits all of them.

| Mechanism | Description |
|---|---|
| **Frame-time cap (delta ≤ 1/30s)** | Every tick consumer multiplies by capped delta, so slow frames scale animations down rather than skip. Already in `App.js`. |
| **Global time scale** | If perf monitor detects sustained frame-time >1/30s, global scale drops further. Animations slow, never judder. |
| **Adaptive DPR** | Already adopted (commit d3b2331). Phase 1 verifies still wired through `GlbWorld`. |
| **Single GLB, one parse** | Whole world is one fetch + parse on boot. After load, zero per-frame procedural geometry cost. |
| **InstancedMesh per shared datablock** | Foliage detected at load and collapsed to one `InstancedMesh` per source mesh. |
| **`renderer.sortObjects = false` past 500 meshes** | Phase 7 adds this. Manual `renderOrder` is set on water (after foliage) and PostFX (last). |
| **Frustum-gated section updates** | Per-section `update()` only fires when player is inside `refZoneFrustum_*`. Phase 2 + 3 wire this. |
| **Distance-gated point lights** | Cairn lanterns + brazier + forge + lighthouse: past 50m from player, light contribution is zero. Phase 4. |
| **Distance-based shader LOD** | Far foliage past 80m uses flat palette (skips wind shader). Phase 5 advancement. |
| **Fog as a culler** | Mist horizon 30→100→165m fades distant geometry; GPU skips lighting pixels past fog. Mountain quads are 8 triangles total. |
| **No PostFX on mobile** | Phase 7 detects `isMobile` and bypasses PostFX render target. |
| **Shadow softness tuned per device** | 3 cascades desktop, 2 mobile; shadow map size scales with DPR. Already in spec. |
| **Per-frame allocations = 0** | No `new Vector3()` in tick paths. New modules (`GlbWorld`, `PortfolioMounts`, `WorldLights`, `WorldWater`) must reuse pooled vectors. Code-review gate. |
| **Audio pause on blur** | Tab-blur pauses ambient + footsteps (existing, per memory `feedback_audio_pause_on_blur`). |
| **Lazy heavy resources** | PostFX render target + special shaders init only on first use, not at boot. |

---

## 8. Risk register

| # | Risk | Likelihood | Blast radius | Mitigation |
|---|---|---|---|---|
| R1 | Heightfield grid extraction bug (axis flip, scale off, vertex order wrong) | Medium | All 18 `heightAt` consumers broken | Phase 1 raycast-vs-baked probe at 20 points; assert ±0.01m before declaring loader OK |
| R2 | Missing ref empty in .glb (e.g. `refZoneBounding_skills` absent or misnamed) | Medium | Section won't load; cascading nulls | Loud boot assertion identifies the missing ref by name; halt; no silent fallback |
| R3 | Material name token collision (`*water*` matches `waterfall`) | Low | Wrong shader on waterfall mesh | Check order `waterfall` → `water` → `ocean`; assertion that each special material resolves exactly once |
| R4 | Collider drift — `cuboid_*` bbox doesn't match visible mesh bbox | Medium | Player walks through pavilion wall OR floats above forge | Log `(mesh_bbox - collider_bbox)` for each pair; assert max delta <0.1m. Visible mesh is authoritative per CLAUDE.md rule 5 |
| R5 | Performance regression — too many static colliders | Medium | FPS dip below 60 desktop | Phase 1 FPS probe; tune by collapsing co-located colliders if needed |
| R6 | Section position drift — `refZoneBounding_*` differs from spec ±70 | Low | Mini-map / compass / teleport markers misaligned | Boot log prints actual section coords; user spot-checks against world-design §3 |
| R7 | Push-spot regression — auto-detect misses a category (e.g. `bench_*` renamed) | Low | Comedy gag silently broken | Assertion `pushSpots.length >= 50`; logs the categories that contributed |
| R8 | Interactables (crate/bag/football) land off-terrain | Low | Item floats or sinks | Phase 1 re-heightAt every Interactables placement; visual probe |
| R9 | Grass-flatten over baked paths fails (`getTilePositions` returns empty) | Low | Grass blades grow through path ribbon | Phase 7 visual check; fallback = sample N points along path ribbon mesh |
| R10 | Lighthouse beam parented wrong (rotates in world space not local) | Medium | Beam doesn't sweep correctly | Phase 5 visual check; pivot from `refLighthouseBeamPivot` rotation, not lamp position |
| R11 | Achievements panel breaks (depends on `world.signs`, `world.billboards`) | Medium | 34-unlock regression | Phase 2 + 3 verify includes opening Achievements panel; ensure `world.signs.experienceItems` + `world.billboards.items[0]` still populate via new modules |
| R12 | Footstep audio surface detection breaks (mesh material → footstep clip mapping changed) | Low | Wrong footstep sound on path/grass/wood | Phase 7 walk probe with audio enabled; ear-check |
| R13 | Map / teleport (`Travel/Teleport.js`) lands inside a new collider | Medium | Player stuck on teleport | Phase 7 teleport probe for each marker; Navmask rebuilds from new colliders |
| R14 | Adaptive DPR + new shader stack tank mobile FPS | Medium | Mobile users can't run site | Phase 5 mobile FPS probe; fallback flag in Phase 7 skips expensive shaders on `isMobile` if shader cost >2ms/frame |
| R15 | Frame-time juddering on weak devices despite high mean FPS | Medium | Site "feels broken" on company laptops | Phase 7 stddev/mean gate (<0.20); tune by collapsing colliders, gating updates, lowering shadow res |
| R16 | New ShaderMaterial variants cost more than the old palette material | Medium | Phase 5 FPS regression | Per-shader compile + per-frame ms cost log; fallback to flat palette on `isMobile` if >2ms |

### Rollback plan

Three levels:
1. **In-phase regression** — caught before commit. Subagent iterates; no rollback needed.
2. **Branch-level** — `git revert <phase-commit>` on `world-v2-blender-build`. Subsequent phases get fix-up commits.
3. **Post-merge to main** (worst case) — `git revert <merge-commit>` on main. Procedural world restored. `world-v2-blender-build` stays available for re-work; `.glb` stays in repo.

---

## 9. Workflow rules (hard)

These are non-negotiable per the user's explicit instruction. They apply to every phase.

1. **Subagents never commit, never stage, never `git add`.**
2. Every phase ends with a subagent report + a verification walkthrough handed to the user.
3. The user verifies in browser. Reports issues or "Phase N approved".
4. If issues: we fix and re-verify. Loop until approved.
5. Only on explicit approval → controller commits with a NO-TRAILER message (never `Co-Authored-By: Claude` per memory `feedback_no_claude_coauthor`).
6. All phases stay on `world-v2-blender-build`. Merge to `main` is a separate decision at the end, also user-driven.
7. Never push without explicit user OK.

---

## 10. What this design does NOT change

Unchanged systems (no edits, no rewrites):
- Player character (Avaturn + Mixamo), animations, controller, camera follow
- `Physics.js` API (only the source `terrain` object changes; the API stays)
- `Sky.js`, `Wind.js`, `Palette.js` (Phase 7 retunes values only)
- Audio manager (Howler), all audio assets
- Achievements (34 unlocks), Discovery tracking, Distance mini-game
- Tutorial coachmarks, Compass HUD, MiniMap + MapOverlay, Click-to-move, Teleport, Navmask
- All UI overlays (welcome, loading, interaction modal, action prompts, mobile joystick)
- All effect modules NOT in the rewrite list: Fireflies, Rain, Thunderstorm, Leaves, Footprints, WindLines, PostFX
- Torch (night-mode hand-attached light)
- Verification sandbox conventions (`.verify/scripts/` + `.verify/shots/YYYY-MM-DD/`)
- Build tooling (Vite, KTX2 + Draco compression, Vercel Speed Insights, GTM)

---

## 11. Post-Bruno advancements

Bruno authored his portfolio in 2022 without AI assistance. Where modern Three.js / Web APIs give us a clearly better result than his 2022 approach, we use the modern path. Each advancement below has zero added risk vs his approach.

| Upgrade | Bruno's approach | Ours | Phase |
|---|---|---|---|
| **Per-instance wind phase** | Single shared time uniform — trees sway in sync | `InstancedBufferAttribute` per-instance phase offset; trees out of phase with each other; more organic | 5 |
| **`prefers-reduced-motion` support** | None | Detect via `matchMedia('(prefers-reduced-motion: reduce)')`; disable wind sway, particle emission, water animation, beam rotation, weather effects. Calm fallback for motion-sensitive users | 5 + 6 |
| **Distance-based shader LOD** | Single shader for all foliage | Far foliage (>80m) drops to flat palette; closer foliage runs wind shader. Saves vertex shader cost on the long tail of trees | 5 |
| **Modern color management** | Linear pipeline + sRGB textures | Confirm `THREE.ColorManagement.enabled = true` + `THREE.SRGBColorSpace` on all loaded textures + ACES tonemapping in `App.js`. Audit in Phase 7 | 7 |
| **`AbortController` on .glb fetch** | None | If user navigates away mid-load, cancel the fetch. Saves bandwidth on flaky connections | 1 |
| **`requestIdleCallback` for non-critical init** | Inline init | PostFX render target, particle pools, audio decoding all init on idle after first frame. Boot feels faster | 1 + 6 |
| **`ResizeObserver` for canvas** | Window `resize` event listener | More precise resize detection (catches CSS-driven size changes). Already partially adopted in some modules; audit in Phase 7 | 7 |
| **`View Transitions API` for modal opens** | GSAP fade tween | Where supported, use native view transitions for modal open/close. Falls back to GSAP. Smoother on Chrome | Optional in Phase 2 |
| **Mesh BVH for picking** | Naive raycast against scene | Build `MeshBVH` index on collider meshes for click-to-teleport / Navmask. Faster than naive raycast — only needed if Phase 7 perf probe shows raycast time >2ms | Phase 7 fallback |

---

## 12. Open questions surfaced during brainstorming, settled

- **Cutover strategy:** branch isolation on `world-v2-blender-build`; phase-by-phase commits after explicit user approval; merge to main is one final decision (§9).
- **`heightAt` implementation:** bake the 193×193 heightfield from the terrain submesh at load; reuse existing bilinear math; preserve API (§2.4, §6.2).
- **Push spots:** auto-detect by mesh-name regex (§2.2).
- **Section positions:** ref-driven from `refZoneBounding_*` empties; new `SectionPositions.js` is the single source of truth (§2.4).
- **Phase size:** MVS first, then per-feature phases (§4).
- **Resume lectern:** folded into Phase 2 (PortfolioMounts) — conceptually the same as the other portfolio mounts.
- **Material token check order:** `waterfall` before `water` before `ocean` (§2.3).
- **Grass-flatten over paths:** sample along baked path ribbons in Phase 7; drop only if perf-cheap to do so.

---

## 13. Implementation plan handoff

This spec describes **what** we're building. The implementation plan (next step, via `writing-plans` skill) will detail:

- Exact file paths for each new module
- Function signatures and module interfaces
- Per-phase subagent dispatch instructions
- Test fixtures + verification driver code
- Step-by-step gate criteria the user is asked to confirm

**User reviews this spec first → controller runs `writing-plans` → user reviews the plan → only then does any code get written.**

---

*End of spec. See [world-design.md](2026-05-26-world-design.md) for the .glb's authoring contract; see [blender-build-resume.md](../handoffs/2026-05-26-blender-build-resume.md) for what each .glb phase produced.*
