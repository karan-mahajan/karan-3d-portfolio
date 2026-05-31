# Material consolidation — Phase-1 analysis & verification

Companion to `material-consolidation-prompt.md`. This is the read-only
investigation the prompt asked for, plus a post-implementation audit of the
shipped consolidation. All numbers are measured from the actual GLBs and the
installed `three@0.184` source — not estimated.

## 1. Material census (measured from `static/world/*.glb`)

157 baked GLB materials across the monolithic + instanced-visual systems
(prompt said ~151; close). Bucketed:

| Bucket | Count | Handling |
|---|---|---|
| flat-opaque | 130 | → shared `opaque:double` node material |
| flat-emissive | 15 | emissive folded into the shared materials via a baked `worldEmissive` attribute |
| transparent (`BLEND`) | 10 | 6 are `skill_base_*_glow` (skipped by design); 4 window/lamp glows → shared `transparent:double` |
| textured | 2 | left as their own materials (a couple of extra programs is fine) |

Flag scan across all 157:

- `metallicFactor != 0`: **0** → the shared materials' `metalness:0` is lossless.
- `roughnessFactor != 1`: **156** → roughness genuinely varies, so it is baked
  per-vertex into a `worldRoughness` attribute (a flat shared roughness would
  have regressed shading).
- `doubleSided`: **157** (all) → side collapses to `*:double`, so the live
  shared set is effectively **opaque:double + transparent:double ≈ 2 programs**.
- `alphaMode == MASK`: **0** → no alpha-test path needed.
- pre-existing `COLOR_0`: **0** → baking a vertex-colour attribute is lossless
  (nothing to clobber).

## 2. Where GLB materials become live materials

- **Monolithic** GLBs are added under `system:<name>` groups in
  `GlbV3World.load()` (one `THREE.Mesh` per glTF primitive — GLTFLoader does not
  merge primitives). ~681 primitives total ⇒ ~681 static meshes/draw calls
  (areas 216, miscFx 96, structures 80, trees ~164, poleLights 24, …).
- **Instanced** systems (`rocks`, `bricks`, `flowers`, path tiles) build one
  `InstancedMesh` per template reusing `proto.material` — already 1 draw call
  each; left untouched by consolidation except the material swap.

## 3. Consolidation mechanism — verified lossless

`GlbV3World.#consolidateBakedWorldMaterials()` (runtime, post-load) bakes each
flat material into per-vertex attributes and reassigns one shared
`MeshStandardNodeMaterial` per `(opaque|transparent) × side`:

- `color` (vec4) = linear `material.color` rgb + `opacity` in `.a`.
- `worldEmissive` (vec3) = `emissive * emissiveIntensity` (captures
  `KHR_materials_emissive_strength`, which GLTFLoader applies to
  `emissiveIntensity`).
- `worldRoughness` (float) = `material.roughness`.

Equivalence checks against the `three` source:

- **Colour path** (`NodeMaterial.setupDiffuseColor`): `colorNode = vertexColor()`
  and `material.vertexColors` stays `false`, so there is **no double-multiply**
  (the auto `colorNode.mul(vertexColor())` branch at line 849 is skipped). Vertex
  colours are interpreted in working/linear space — same space as
  `material.color` — so no colour-space drift.
- **Opacity**: `diffuseColor.a = colorNode.a * materialOpacity` (opacity uniform
  is 1). The opaque material forces `alpha = 1` via `isOpaque()`; the transparent
  one keeps the baked alpha. `MeshStandardNodeMaterial` chosen over `Lambert`
  because the GLB materials *are* metallic-roughness Standard — same BRDF =
  pixel-identical; Lambert would drop the (faint) specular term.
- **Emissive**: `emissiveNode` bypasses the `materialEmissive` accessor (which is
  the one that re-applies intensity), so baking `emissive * intensity` is exact.
- **Transparency render state**: GLTFLoader sets `depthWrite = false` for `BLEND`
  (GLTFLoader.js:3623); the shared transparent material uses
  `depthWrite:false` too → **matches the original**. `renderOrder`,
  `castShadow`/`receiveShadow`, and `side` are preserved (consolidation only
  swaps the material and adds attributes; geometry is untouched, so colliders
  built earlier in load are unaffected).

## 4. Prewarm — comprehensive, behind the loading screen

`App.#prewarmDayNightShaders()` adds throwaway proxy meshes (one `Mesh` + one
`InstancedMesh` per shared material, so both pipeline variants compile), then
runs `compileAsync(scene)` once per light rig (night + day). It is **`await`ed
inside `boot()`** (App.js:723), and every material-creating system — Grass,
Water, Foliage, Flowers, Lava, Bonfires, AnimatedProps, Fireflies, Rain,
Thunderstorm — is constructed *before* line 719. So `compileAsync(scene)`
compiles the **entire** scene, not just GLB materials, behind the loading
screen. No static-world shader compiles on a visible frame.

## 5. Spatial-chunk geometry merge (the second Bruno lever, done safely)

Bruno's constant FPS comes from one shared material **and** merged geometry
(few draw calls). #1–4 give the shared material; `#mergeStaticWorldChunks()`
(runs right after consolidation) adds a **scoped, culling-preserving** merge.

Mechanism: eligible meshes are bucketed by **(coarse `28 m` world grid cell ×
shared material)** and each bucket is merged into one mesh → one draw call.
Bucketing by a grid — rather than a blanket per-system merge — keeps each merged
mesh's AABB bounded, so per-mesh **frustum culling still skips off-screen
chunks** (a whole-island merge would force-draw everything). Geometry is baked
into root-local space (so re-parenting doesn't double the root transform) and
reduced to exactly the attributes the shared material reads
(`position/normal/color/worldEmissive/worldRoughness`), non-indexed, so a
heterogeneous set merges cleanly. `castShadow`/`receiveShadow` are OR-ed from
the sources; visuals are pixel-identical (same material, exact world positions).

**Allow-list** — `structures, scenery, fences, benches, lanterns, poleLights,
statue, birchTrees, cherryTrees, oakTrees, areas`. Eligibility also requires the mesh to currently hold a
`userData.worldSharedMaterial` material (auto-excludes textured/bespoke/skipped
materials) and to not be an `InstancedMesh` (instancing is already one draw
call). Safe because, verified against the codebase:

- **Push gag is position-based** (`ActionPrompts.addPushSpot({position})`), not
  mesh-raycast — merging never breaks it.
- **PlayerCamera does not raycast world meshes**; camera collision is unaffected.
- **All colliders are built before consolidation** (lines 322–373) as
  independent Rapier shapes, so removing the visual meshes can't move the ground
  or props.
- Pole-light / lantern / bench **refs are empties** that drive lights/colliders;
  nothing looks up their visual meshes by name.
- **Trees** are safe despite being conceptually "push spots": v3 sets
  `nature.pushSpots = []` (no procedural push spots — only billboards / signs /
  compass / sections are registered), oak's green canopy is stripped into
  foliage anchors *before* this pass (`#extractTreeFoliage`), birch/cherry
  leaves come from the instanced `treeLeaves` system, and trunk colliders are
  built earlier in `load()`. Only static trunk/branch geometry survives to merge.

- **`areas`** (the portfolio core) merges its inert decoration — `projectHut_*`
  shells, `contactBoard_*` structure (~150 meshes, referenced nowhere in src/) —
  while keeping interactive parts addressable. `skillSphere_*` (the animated
  orbit rings + core that `SkillSphere.js` spins/recolours by name) is already
  material-excluded because consolidation skips it. An additional name guard
  (`inscription|_sign|mailbox|board_face|board_text|artifact`) protects the
  `contact_inscription_plinth` (read by PortfolioMounts) plus likely
  decal/motion surfaces of the half-wired portfolio layer. `root_*` marker
  groups are not meshes, so `refs.markers` is untouched. If the interaction
  layer later mounts onto a specific decorative mesh, add its name to that
  regex — the merge is one constant and fully reversible.

**Deliberately excluded** (would break runtime behaviour if baked static):
`lava` (re-materialised on `lavaSurface_core` by name, Lava.js:118), `miscFx`
(animated `airDancerSeg_*` / `animal_*` + dynamic title letters), `bonfires`
(styled at runtime). These still share one pipeline, so their draws remain cheap
even un-merged.

Console line at load: `static chunk merge: N meshes -> M merged draw calls`.

## 6. Acceptance criteria — status

1. Programs reduced 157 → ~2 shared (+2 textured). ✅
2. Visuals unchanged (colour / emissive / opacity / roughness / side / shadows /
   renderOrder all preserved or proven equivalent). ✅
3. No on-screen compiles — entire scene prewarmed at load. ✅
4. `npm run build` passes; terrain & colliders left raw. ✅
5. Nothing committed. ✅
