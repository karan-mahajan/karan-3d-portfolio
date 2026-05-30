# v3 Runtime — Phase A: split GLB export + runtime audit + migration plan

Status: **Phase A planning complete.** No runtime code changed yet. This doc is
the hand-off for Phase B onward. Updated 2026-05-30 after the user chose **split
the export like Bruno** + a full blend inventory.

Guiding principle (user, 2026-05-30): **the Blender world file
(`tools/blender/world-v3-karan.blend`) is the single source of truth.** Trees,
leaves, house, lights, sections — everything comes from the blend, exactly like
Bruno Simon's folio-2025. The old model (JS asset-packs placed procedurally by
`Grass.js`/`Nature.js`/`Foliage.js`/`Paths.js`) is **retired**. We study how
Bruno wires blend → GLB → runtime and rebuild karan the same way. Don't bend the
old JS to fit the GLB — replace it.

World scope: **projects / skills / contact only.** Experience is dropped (its
marker/label still exist inert in the blend; the runtime ignores them).

---

## 1. Decisions locked this round

| # | Decision | Choice |
|---|---|---|
| 1 | Renderer | **WebGPU + TSL** (`three/webgpu` + `three/tsl`). Verified present in three@0.184. §6. |
| 2 | One GLB vs split | **Split, Bruno-style** — per-system Visual/References pairs + monolithic placed-once GLBs + a generated `manifest.json`. §4. |
| 3 | Grass mask delivery | **Yes** — exporter/Phase D copies `terrainGrass-authored.exr` → `static/world/`. §5. |
| 4 | Animations | **None to export.** Blend has 0 actions / 0 armatures / 0 drivers — all motion is runtime-driven via named pivots. §3. |
| 5 | New art assets needed from user | **None.** Everything is in the blend; only optional dev tooling later (gltf-transform for compression). §7. |

The single `static/world/world-v3.glb` produced earlier is **superseded** by the
split set below and will be deleted when the split exporter lands (no commit
until then).

---

## 2. Verified blend inventory (`world-v3-karan.blend`)

Source of truth for the split. Top-level collections (object counts; `[X]` =
view-layer-excluded, not exported):

```
terrain        1 mesh (+ live heightfield NODES)     statue          3 mesh
structures    80 mesh (cabin + outhouse)             lavaPool       19 mesh
sectionMarkers contactBoard 19m+5font                miscFx         92 mesh + 4 font
               projectsHut 119m+6light+2font          bricks         80 mesh (3 shared templates)
               skillsSphere 71m                        bushes         45 mesh (1 shared template)
               (+ experience marker/label, inert)      flowers        36 mesh (per-zone shared)
scenery.002    basaltRocks 204m (1+ shared templates) fences          4 mesh
               bridges 7m, slabs 3m, [rocks][road]    grass           1 mesh (Plane.003 GN, neutralized)
decorations    benches 5m, bonfire 4m+4light,         colliders      83 mesh (proxies)
               lanterns 5m+5light, pole_lights 24m+12light            refs          662 EMPTY
vegetation     birchTrees 24m, cherryTrees 28m, oakTrees 18m  [archives/visual/references excluded]
```

**Mesh-datablock sharing = instance-readiness** (the key split signal):

| shared datablock | uses | → split as |
|---|---|---|
| `rockStyle_boulderCluster` | 201 | instanced (rocks) |
| `rockStyle_volcanicShards` | 5 | instanced (rocks) |
| `bushAnchorMesh` | 45 | foliage refs (bushes) |
| `brickPaveMesh` / `brickPileMesh` / `brickKerbMesh` | 40 / 27 / 13 | instanced (bricks, 3 templates) |
| flower zone meshes (`contact`/`skills`/`meadow0-3`/`projects`/…) | 2–6 each | instanced (flowers) |
| **trees (birch/cherry/oak trunks)** | **all unique — NOT shared** | **monolithic** (per §4 D1) |

**Refs (662 empties), grouped by prefix:**
- `refTreeLeaves_*` (~580) — leaf-cloud anchors, each carries `{species: birch|cherry, phase}` → **Foliage** leaf clouds.
- `refBirchTree_*` / `refCherryTree_*` (~50) — whole-tree placement anchors (redundant with placed trunks; see D1).
- `refBench_*` (5), `refBonfire_*` (4), `refPoleLight_*` (12) — prop/light anchors (`phase` extra).
- `animalPivot_{cat,dog,deer,rabbit}`, `airDancerPivot_*` (2) — runtime animation pivots.
- `controlsRef`, `playstationRef`, `titleRef`, `lavaRef_pool` — interaction anchors with rich extras (e.g. `lavaRef_pool → {surfaceObject, coreObject, radius, flowDir, glowStrength, pulseSpeed, emberRate}`).
- `sectionRef_{projects,skills,contact,experience}` — **the interaction contract** (see §2a).
- `root_*` — 29 `section_root` empties (finalize scene-graph grouping).

**Colliders (83 meshes)** by shape prefix:
- `tube_*` → cylinder (per-tree trunks, bonfires, pole lights).
- `cuboid_*` → box (benches, statue).
- `*Footprint_*` → walkable landing pads (`sectionFootprint_*` carry `{section, interaction}`; `structureFootprint_*`; `miscFootprint_*`).

### 2a. Section interaction contract (`sectionRef_*` extras — verbatim)

```
sectionRef_projects  {section, title:'Projects', interaction:'projectsHut',
                      enterCameraPath:'doorToInteriorBoard',
                      doorLocalOffset[2], interiorBoardLocalOffset[3]}
sectionRef_skills    {section, title:'Skills', interaction:'skillSphere',
                      sphereRadius:6.0, sphereCenterHeight:7.0, waterMounted:True,
                      floatClearance:1.55, enterCameraOffset[3]}
sectionRef_contact   {section, title:'Contact', interaction:'contactModal', prompt:'press E'}
sectionRef_experience{section, title:'Experience'}   ← inert, runtime ignores
```
Blender XY positions (organic, not cardinal): projects ~(33,−26), skills
~(−34,−36), contact ~(−15,33). Z from heightfield.

---

## 3. Bruno's runtime model (what we copy) + animation finding

Bruno's `World.js` builds one class per content type, each fed a **visual**
template + **references** list pulled from separate GLBs:

```js
this.birchTrees = new Trees('Birch Tree', birchVisual.scene,
                            birchReferences.scene.children, '#ff4f2b', '#ff903f')
```
- `setBodies()` → one `InstancedMesh` of the template geometry, one matrix per
  reference empty.
- `Foliage`/`Bushes`/`Flowers` → instanced SDF clouds at reference transforms,
  no separate visual mesh.
- `InstancedGroup` helper does the same for multi-mesh props (benches, lanterns,
  poleLights, fences, bricks): template[0] + the rest as reference transforms.
- Named markers (`References.js`, regex `^ref(?:erence)?([^0-9]+)([0-9]+)?$`)
  drive zones/areas; `areasModel.scene.children` whose name `startsWith` an area
  key become interactive Area instances.
- Terrain: `terrainModel.scene.children[0].geometry`; heights read off the
  position attribute into a Rapier `heightfield` collider.

**Animation:** the karan blend has **0 actions, 0 armatures, 0 animation_data**.
Confirms `export_animations=False`. All world motion (animals, air dancers, lava,
grass, wind, water) is **runtime-driven** — the GLB carries only static meshes +
pivot/anchor empties the runtime animates by name. **No Mixamo/clip files are
needed for the world.** (The character rig — Avaturn + Mixamo — is separate and
already in `static/models/character/`.)

---

## 4. The split — output manifest (Bruno-style)

The export step becomes a **splitter**: it writes one folder per system under
`static/world/` plus a generated `static/world/manifest.json` the runtime reads
(data-driven loader — an improvement over Bruno's hand-maintained list, same
spirit). Three kinds of output:

**(a) Monolithic** — placed-once geometry, added to the scene as-is:

| file | source | why monolithic |
|---|---|---|
| `terrain/terrain.glb` | terrain (modifiers applied) | unique heightfield; source of physics heights |
| `structures/structures.glb` | structures | cabin + outhouse, unique geo |
| `areas/areas.glb` | sectionMarkers (projectsHut, skillsSphere, contactBoard) | section structures; names drive interactions |
| `scenery/scenery.glb` | bridges + slabs | unique geo |
| `statue/statue.glb` | statue | unique |
| `lava/lava.glb` | lavaPool | runtime animates `lavaSurface_*` via `lavaRef_pool` |
| `miscFx/miscFx.glb` | miscFx (title FONT, controls, playstation, animals, air dancers) | runtime drives child pivots by name |
| `vegetation/birchTrees.glb`,`cherryTrees.glb`,`oakTrees.glb` | tree trunks | unique per tree (D1) |
| `fences/fences.glb` | fences | only 4, not worth a pair |
| `colliders/colliders.glb` | colliders | proxy meshes; runtime builds Rapier shapes from prefix+bbox, then discards |

**(b) Instanced** — `{name}Visual.glb` (template at origin) + `{name}References.glb` (empties with transforms):

| system | visual | references | count | source |
|---|---|---|---|---|
| rocks | `rocks/rocksVisual.glb` | `rocks/rocksReferences.glb` | ~206 | basaltRocks (shared datablocks) |
| bricks | `bricks/bricksVisual.glb` (3 named templates) | `bricks/bricksReferences.glb` | 80 | bricks |
| flowers | `flowers/flowersVisual.glb` | `flowers/flowersReferences.glb` | 36 | flowers |
| benches | `benches/benchesVisual.glb` | `benches/benchesReferences.glb` | 5 | benches + `refBench_*` |
| poleLights | `poleLights/poleLightsVisual.glb` | `poleLights/poleLightsReferences.glb` | 12 | pole_lights + `refPoleLight_*` |
| lanterns | `lanterns/lanternsVisual.glb` | `lanterns/lanternsReferences.glb` | 5 | lanterns |

**(c) Foliage / data references** — empties only:

| file | source | consumer |
|---|---|---|
| `bushes/bushesReferences.glb` | bushes (45) | **Foliage** SDF (memory: bushes are SDF, not geometry) |
| `treeLeaves/treeLeavesReferences.glb` | `refTreeLeaves_*` (~580, `species` extra) | **Foliage** leaf clouds |
| `references.glb` | `sectionRef_*` + `controlsRef`/`playstationRef`/`titleRef`/`lavaRef_pool`/`refBonfire_*` + pivots | interaction/light/anim wiring |

Plus non-GLB: `terrainGrass.exr` (grass+water mask, copied from authored EXR).

**`manifest.json` schema** (generated by the splitter, read by the loader):
```jsonc
{
  "monolithic": [{ "system":"terrain", "file":"terrain/terrain.glb", "heightfield":true }, …],
  "instanced":  [{ "system":"rocks", "visual":"rocks/rocksVisual.glb",
                   "references":"rocks/rocksReferences.glb", "count":206 }, …],
  "foliage":    [{ "system":"bushes", "references":"bushes/bushesReferences.glb", "count":45 },
                 { "system":"treeLeaves", "references":"treeLeaves/treeLeavesReferences.glb",
                   "count":580, "bySpecies":true }],
  "colliders":  "colliders/colliders.glb",
  "references": "references.glb",
  "grassMask":  "terrainGrass.exr",
  "grassGrid":  { "bounds": 96.0 }
}
```

**Splitter mechanics** (rewrite of `16-export-glb.py` → multi-output; still
headless, idempotent, never saves the .blend):
1. Neutralize Plane.003 grass GN (unchanged from current script).
2. For each **monolithic** system: select its collection's visible objects →
   `bpy.ops.export_scene.gltf(use_selection=True, …)`.
3. For each **instanced** system: export the shared template(s) at origin →
   `…Visual.glb`; build temp empties at each user/ref transform, export →
   `…References.glb`; delete temp empties (in-memory).
4. For **foliage/data**: export the relevant empties → references GLB
   (carry `species`/extras).
5. Write `manifest.json`. Keep the runaway-GN guard + pre-export assertions per
   file. Remove the obsolete single `world-v3.glb`.

---

## 5. Bruno's grass (answers "how many grass?") + mask

`Grass.js`: `subdivisions = 280` → **280 × 280 = 78,400 blades** (1 tri each),
a **camera-following grid** wrapped by modulo so it always surrounds the player.
Density/colour driven by the terrain mask texture's **green channel**; below-
threshold blades are pushed 100 m up (hidden). Not baked, not millions.

karan: mask already authored at
`tools/blender/scripts/v3/karan/resources/masks/terrainGrass-authored.exr`;
grid bounds = Plane.003 (±~96 m). **Approved:** copy it to `static/world/
terrainGrass.exr` in Phase D (verify it carries the channels Bruno's shader
expects — green=grass, blue=water/dirt gradient — or adapt the shader).

---

## 6. Audit — v2 runtime vs v3 (what's obsolete)

| v2 file / system | Assumes (old world) | v3 reality | Verdict |
|---|---|---|---|
| `World/GlbWorld.js` | `world.glb`, terrain **193×193**, names `refForge`/`refBrazier`/`refCairnLantern_`/`pine_`/`hero_tree_`, path ribbons, `trimesh_` | split GLBs + `manifest.json`, terrain **129×129** (±96), `sectionRef_*`, `refPoleLight_/refBonfire_/refTreeLeaves_`, `tube_/cuboid_/*Footprint_`, `role`+`section_root` extras, no paths | **Rewrite** → `GlbV3World`: manifest loader + per-system builders. |
| `World/SectionPositions.js` | 4 cardinals ±70/±52, `experiencePath` | 3 organic sections, data in `sectionRef_*` extras | **Rewrite.** Drop experience + cairns. |
| `World/Grass.js` (Quaternius) | JS asset-pack tufts | terrain-mask TSL shader | **Replace** (Bruno grass). |
| `World/Nature.js`,`Foliage.js`,`Leaves.js` | asset-pack trees/canopies | blend trunks + `refTreeLeaves_` (species) | **Replace** (Trees + Foliage off refs). |
| `World/Paths.js` | path ribbons in GLB | none (deferred sub-project) | **Skip/stub.** |
| `Portfolio/Billboards.js`,`ProjectShowcase`,`Signs`,`PortfolioMounts` | `refShowcaseMount`, single showcase | `projectsHut`/`skillsSphere`/`contactBoard` meshes + `sectionRef_*` | **Rewrite** interaction layer. |
| `Physics.js` heightfield | 193-grid | 129-grid ±96; colliders from `role=collider` | Mostly OK; feed v3 grid + build colliders from proxy meshes. |
| `App.js` wade/clamp/respawn (45/120/−5) | legacy island | walkable ~±60, terrain ±96 | Recalibrate (Phase G). |
| `World/StreetLights.js` | own placement | `refPoleLight_*`/`refBonfire_*` anchors | Re-point to refs. |

**Untouched / still valid:** Player/Character (Avaturn+Mixamo), camera, audio,
UI (Compass/MiniMap/Tutorial/Achievements), TimeOfDay/Sun/Sky, Torch, Water/Rain/
Thunderstorm — none depend on world naming (though materials get re-authored as
TSL in B0).

### Renderer migration (B0) — why WebGPU + TSL is safe
- Bruno's grass/material/wind/water are TSL node graphs → near-drop-in reference.
- TSL is backend-agnostic: `WebGPURenderer` runs WebGPU where available and
  **falls back to WebGL** otherwise; same TSL compiles to both. No compat loss.
- Cost: `WebGLRenderer`→`WebGPURenderer` (async `await renderer.init()`); imports
  `three`→`three/webgpu`, shaders→`three/tsl`; re-author custom materials
  (`SmoothLitPaletteMaterial`, …) as TSL `MeshDefaultMaterial`. Rapier/
  camera-controls/gsap/howler are renderer-agnostic. Playwright verify needs a
  WebGPU Chromium flag or asserts the WebGL fallback.

---

## 7. Phased migration plan (each = its own session)

- **Phase B-export — Split exporter.** Rewrite `16-export-glb.py` per §4; produce
  the split set + `manifest.json`; delete single `world-v3.glb`. Verify each GLB
  opens + counts match. *(Mechanical; could fold into B0's commit.)*
- **Phase B0 — Renderer → WebGPU/TSL.** REAFFIRMED 2026-05-30 (WebGL stay-put
  considered and rejected: it's "less work," not "better"; Bruno's case study
  documents auto-WebGPU perf + mobile, which WebGL can't match). Verified API in
  three@0.184: `three/webgpu` exports `WebGPURenderer`/`PostProcessing`/
  `MeshLambertNodeMaterial`/`MeshStandardNodeMaterial`; `three/tsl` exports
  `pass`/`output`/`uniform`/`texture`/`Fn`; `bloom` is in
  `three/addons/tsl/display/BloomNode.js`.

  **Verified surface + ordered checklist (no small bootable slice — execute as one
  focused push; tree is non-booting mid-migration):**
  1. Swap `from 'three'` → `from 'three/webgpu'` in all 29 src files (superset
     build; mixing the two breaks `instanceof`). Loaders stay on
     `three/examples/jsm/loaders/*` (renderer-agnostic).
  2. [App.js:697] `new THREE.WebGLRenderer` → `new THREE.WebGPURenderer` (construct
     in the sync constructor is fine — only `.init()` is async). Keep shadowMap/
     toneMapping/outputColorSpace/info.autoReset (WebGPURenderer supports them).
  3. [App.js boot():295] `await this.renderer.init()` BEFORE the first render.
  4. [App.js:955] render loop `requestAnimationFrame(#tick)` →
     `renderer.setAnimationLoop(#tick)`; `postfx.render()` → `await
     postProcessing.renderAsync()` (WebGPU renders async).
  5. [Effects/PostFX.js] full rewrite: `EffectComposer`+`RenderPass`+
     `UnrealBloomPass`+`ShaderPass`(tilt-shift GLSL)+`OutputPass` → WebGPU
     `PostProcessing` graph: `pass(scene,camera)` → `bloom()` (addons) → tilt-shift
     as a TSL node (or defer tilt-shift initially) → `output`.
  6. Custom GLSL `ShaderMaterial`/`onBeforeCompile` → TSL node materials, in
     dependency order: `SmoothLitPaletteMaterial` (master, palette+lambert+fog+
     wind+reveal) first, then Sky, then the effect materials (Fireflies, Rain,
     WindLines, Leaves, Water, Foliage, Grass). Each currently constructed in the
     App constructor / World, so each must compile clean on WebGPU.
  7. World load is broken anyway (world.glb removed) — B0 lands together with the
     Phase B v3 loader so the app boots to a verifiable frame. Verify headless via
     a WebGPU-capable Chromium flag (or assert the WebGL fallback backend).

  Do B0 first — everything downstream authors TSL.
- **Phase B — Blend-driven loader.** `GlbV3World`: read `manifest.json`; load
  monolithic GLBs into the scene; bake 129-grid terrain heightfield + Physics
  ground; build Rapier colliders from `colliders.glb` (prefix→shape, bbox→size)
  then hide; collect `references.glb` empties into a typed map (prefix+extras).
  TSL palette material on visible meshes. **Deliverable: walk the v3 world with
  collision.**
- **Phase C — Sections & interactions.** Rebuild `SectionPositions` + interaction
  layer from `sectionRef_projects/skills/contact` extras; wire `projectsHut`/
  `skillsSphere`/`contactBoard` as interactables (door cam path, sphere float,
  contact modal). Drop experience.
- **Phase D — Grass + wind.** Port Bruno `Grass.js` (mask shader, camera grid)
  with `terrainGrass.exr`; shared wind uniform.
- **Phase E — Instancing: vegetation, foliage, props.** `Trees` (trunks placed +
  leaf `Foliage` off `refTreeLeaves_` by species), `Bushes`/`Flowers` foliage,
  `Rocks`/`Bricks`/`Benches`/`PoleLights`/`Lanterns` InstancedGroup off
  visual+references.
- **Phase F — Lights, FX, animated props.** Point lights at `refPoleLight_`/
  `refBonfire_`; animate `animalPivot_*`/`airDancerPivot_*`; lava (`lavaRef_pool`
  extras); water surfaces; day/night via existing TimeOfDay.
- **Phase G — Calibration & cleanup.** Wade/clamp/respawn for ±60; minimap/
  compass to organic positions; delete retired v2 systems; optional gltf-transform
  compression pass; update CLAUDE.md.

---

## 8. Open decisions (recommended defaults — flagging, not blocking)

- **D1 — Trees: monolithic trunks vs instanced template.** Trunks are unique per
  tree (hand-authored variation, not a shared datablock). **Recommend: monolithic
  per-species trunk GLBs now** (preserve variation; trunks are low-poly), leaves
  via Foliage refs. Revisit instancing only if perf demands. The
  `refBirchTree_/refCherryTree_` anchors stay available if we switch to a single
  template later.
- **D2 — Flowers: Foliage vs instanced meshes.** Bushes = **Foliage SDF** (per
  memory). Flowers are real authored meshes sharing per-zone datablocks →
  **Recommend instanced meshes** (not SDF), one InstancedMesh per zone template.
- **D3 — Compression.** Ship **uncompressed** first (like v2). Defer Draco/KTX2
  via `@gltf-transform/cli` to Phase G; it's the only new dev dependency, and
  only if size/load demands it.
- **D4 — `manifest.json`.** Generated by the splitter so the loader is
  data-driven (vs Bruno's hardcoded list). Recommend keep.

If you disagree with any default, say so before Phase B-export; otherwise I'll
proceed on these when you green-light the next session.
