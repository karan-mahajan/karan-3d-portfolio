# Credits & Third-Party Assets

This is a 3D walkable portfolio built with vanilla Three.js. It stands on the
shoulders of a lot of open-source work, free asset packs, and one very
generous piece of inspiration. Thank you to everyone listed below.

If you are an author listed here and want different wording, a correction, or
removal, please reach out: karanmahajan321@gmail.com.

---

## Inspiration & reference

- **Bruno Simon** — [folio-2025](https://github.com/brunosimon/folio-2025),
  [bruno-simon.com](https://bruno-simon.com), and
  [Three.js Journey](https://threejs-journey.com).
  The entire concept of a walkable, playful 3D portfolio is inspired by Bruno's
  work. The world layout, art direction, and a number of runtime techniques in
  this project were studied directly from his ISC-licensed `folio-2025` source
  and Blender scene, then re-authored for this portfolio. Huge thanks — this
  project would not exist without his example and teaching.
  `folio-2025` is **ISC-licensed** (reproduction permitted with attribution);
  Copyright © Bruno Simon.

---

## Runtime libraries (npm)

| Library | Use | License |
|---|---|---|
| [three.js](https://threejs.org) (`three@0.184`) | WebGPU renderer, scene, materials, TSL shaders | MIT |
| [@dimforge/rapier3d-compat](https://rapier.rs) | Physics (character controller, colliders) | Apache-2.0 |
| [camera-controls](https://github.com/yomotsu/camera-controls) | Third-person follow camera | MIT |
| [GSAP](https://gsap.com) | UI fades + interaction transitions | [GreenSock Standard "No Charge" License](https://gsap.com/community/standard-license) |
| [Howler.js](https://howlerjs.com) | Audio (ambient, footsteps, UI sfx) | MIT |
| [Vite](https://vitejs.dev) | Dev server + build | MIT |
| [@vercel/speed-insights](https://vercel.com/docs/speed-insights) | Performance telemetry | MIT |

### Build / tooling (devDependencies & bundled decoders)

- [glTF-Transform](https://gltf-transform.dev) — GLB optimization/compression (MIT)
- [Draco](https://github.com/google/draco) — geometry compression; decoder bundled in `static/draco/` (Apache-2.0, © Google)
- [Basis Universal](https://github.com/BinomialLLC/basis_universal) — GPU texture transcoder bundled in `static/basis/` (Apache-2.0, © Binomial LLC)

---

## Character & animations

- **Avatar** (`static/models/character/avatar.glb`) — created with
  [Avaturn](https://avaturn.me). Avaturn-native locomotion clips also ship from
  Avaturn.
- **Animation clips** (`static/models/character/**`,
  `static/models/character/animations/**`) — walk, run, jump, push, kicks,
  flips, dances, gestures, etc. are from
  [Adobe Mixamo](https://www.mixamo.com), retargeted onto the Avaturn skeleton
  by stripping the `mixamorig` bone prefix. Mixamo content is free to use under
  the [Mixamo / Adobe license](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html).

---

## 3D models — asset packs

- **Kenney** — [kenney.nl](https://kenney.nl) — **CC0 1.0** (public domain).
  The bulk of `static/models/nature/*.glb` comes from Kenney's nature/survival
  asset packs: trees, cliffs & rocks, stones, fences, crops & dirt rows,
  bridges, paths, river tiles, flowers, mushrooms, tents, logs & stumps,
  statues, platforms, pots, canoe, campfires, beds, cacti, lily pads, and
  hanging moss. Thank you, Kenney.
- **Quaternius** — [quaternius.com](https://quaternius.com) — **CC0 1.0**
  (public domain). Everything under `static/models/nature/quaternius/*.glb`:
  stylized trees & pines, twisted/dead trees, bushes, ferns, plants, clover,
  flower groups & petals, wispy/tall grass, mushrooms, pebbles, and path rocks.
  Thank you, Quaternius.

## 3D models — individual (Sketchfab)

- **"Soccer ball / Football"** (`static/models/extras/soccer-ball/`) by
  [RPSebb](https://sketchfab.com/RPSebb) —
  [source](https://sketchfab.com/3d-models/soccer-ball-football-bd5708568d9042bf8b0e4893a416e92e)
  — Sketchfab Standard license.
- **"Birds"** (`static/models/wildlife/bird-fly/`) by
  [Zacxophone](https://sketchfab.com/Zacxophone) —
  [source](https://sketchfab.com/3d-models/birds-3a9bb97be78944f9bffc23fb25c2154e)
  — Sketchfab Standard license.
- **"Flying Flamingo"** (`static/models/wildlife/bird-fly-2/`) by
  [Michael Kolesidis](https://sketchfab.com/michaelkolesidis) —
  [source](https://sketchfab.com/3d-models/flying-flamingo-64d19a9497da4ddb9c4538ad1287a424)
  — Sketchfab Standard license.

### Models needing source confirmation

These models are in the project but their original-author metadata was stripped
during GLB compression, so the exact source/license is not recorded here yet.
**TODO: confirm provenance before relying on them publicly.**

- `static/models/wildlife/frog.glb`
- `static/models/wildlife/bird-ground.glb`, `bird-perched.glb`, `bird-perched-2.glb`
- `static/models/wildlife/incoming/Bird.glb`, `Eagle.glb`
- `static/models/props/Lantern.glb`, `Light Desk.glb`
- `static/models/extras/wooden-wall.glb`
- `static/models/colour-garden/colour-garden.glb` (custom Blender export — likely original)

---

## Textures

- **Lava** (`static/textures/lava/lava_albedo.jpg`, `lava_emissive.jpg`,
  `lava_normal.png`) — derived (downscaled / re-compressed) from
  "Lava" (https://sketchfab.com/3d-models/lava-845ca6b3b5854b19b69db54e1a840b0b)
  by [Beccasaurus](https://sketchfab.com/beccastabler), licensed under
  **CC-BY-4.0** (http://creativecommons.org/licenses/by/4.0/).
  Only the texture maps are used; the original mesh is not shipped.
- **Water normal maps** (`static/textures/water/Water_1_M_Normal.jpg`,
  `Water_2_M_Normal.jpg`) — standard water normal maps from the
  [three.js examples](https://github.com/mrdoob/three.js/tree/dev/examples/textures/water)
  (MIT).
- **Custom / original textures** — `static/textures/foliage/*` (foliage SDF,
  leaf mask, footprints), `static/textures/mountains/*` (backdrop mountain
  silhouettes), `static/textures/palette.png`, and the project screenshots in
  `static/textures/screenshots/*` are original to this project.

---

## Audio

- **Footsteps, splashes, impacts, and UI/material sfx**
  (`static/sounds/**`) — sourced from free libraries including
  [Kenney audio packs](https://kenney.nl/assets?q=audio) (CC0) and
  [Freesound](https://freesound.org) (the brick-impact clips under
  `static/sounds/hits/bricks/` retain Freesound IDs in their filenames).
  **TODO: verify the per-clip Freesound attribution requirements** — some
  Freesound sounds are CC0, others are CC-BY and require crediting the
  individual uploader.
- **Ambient loops** (`ambient-day`, `ambient-night`, `birds-day`,
  `ocean-loop`, `water-waves`, `wind-trees`, `rain-ambient`, `thunder`) — free
  ambient/nature loops; confirm individual source/license before public use.

---

## Notes

- Models marked **CC0** (Kenney, Quaternius) require no attribution — they are
  credited here as thanks, not obligation.
- **Sketchfab Standard** license permits commercial and non-commercial use in
  all media and derivative works under basic restrictions; see
  https://sketchfab.com/licenses.
- **CC-BY-4.0** assets (lava textures) require the attribution reproduced above
  to remain wherever the work is distributed.
