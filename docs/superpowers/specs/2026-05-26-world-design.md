# World design spec — Blender-authored alpine misty highlands

**Date:** 2026-05-26
**Status:** Design complete; implementation pending
**Companion doc:** [`reports/world-design-decisions.md`](../../../reports/world-design-decisions.md) — reasoning history + alternatives rejected for each choice. Read that for the "why"; this doc is the implementation contract.
**Brainstorm artifacts:** `.superpowers/brainstorm/` (gitignored) — palette swatches, layout map, foliage density mockups

## Scope

This spec describes the **static, Blender-authored world** that will replace the procedural terrain + foliage + paths in `karan-portfolio`. The runtime stack (player, camera, physics, weather, UI, achievements, audio) remains in place; Blender becomes the source of truth for geometry only.

### In scope
- Terrain heightfield (authored once, baked geometry)
- Five focal structures: spawn hearth, workshop (Projects), cairn trail (Experience), observatory (Skills), beacon (Contact)
- Lighthouse on offshore islet
- River + tributary + waterfall + bridges
- Hiking trail loop + viewpoint detours
- Foliage (~130 trees + ~150 ground-cover instances + 5 hero ancients)
- Distant mountain silhouettes (3 cardboard bands)
- Palette texture (128×4 sRGB) + per-prop UV authoring
- Material set (one master smooth-lit + ~6 special variants)
- Retuned values for existing runtime systems (sun, fog, camera FOV, day-cycle keyframes)

### Out of scope
- Blender Python scripts (delivered in next session via `writing-plans` skill)
- Specific 3D model sources (Kenney / Sketchfab / hand-modeled — decided per-asset in build phase)
- Wildlife placement code (runtime; `src/Wildlife/` new module, future session)
- Player character, animations, controllers (existing, untouched)
- UI, achievements, mini-map (existing, untouched)
- Weather effects code — only **values** are retuned

---

## 1. World identity

| Element | Value |
|---|---|
| Mood | Awe &amp; cinematic vast |
| Awe source | Natural / geological (mountains, valley, river, sea) |
| Biome | Alpine misty highlands (pine forests, snow peaks, glacial river) |
| Signature lighting | Misty dawn — pre-sunrise haze, cool dominant, sun barely a glow |
| Art direction | Stylized smooth-lit (palette-texture base color + smooth Lambert + atmospheric haze) |
| Reference games | Genshin Impact alpine areas, Sky: Children of the Light, Skyrim Falkreath, Witcher 3 Skellige |

The world reads as: a traveler's refuge at a mountain pass at dawn. Four functional posts ring a central hearth; a river meanders through; an ocean lies beyond the western cliff with a lighthouse anchoring the horizon; mountains rise to north and east through layered mist.

---

## 2. Palette — 25 colors, locked

Sampled via NearestFilter sRGB, 128×4 PNG (Bruno's pattern). Per-prop UV authoring snaps faces to specific palette cells.

### Sky &amp; atmosphere (5)
| Hex | Role |
|---|---|
| `#c6c3bc` | Sky high — desaturated warm grey |
| `#d5c4ad` | Sun-rim warm — the single warm anchor in the upper sky |
| `#e0d4c0` | Mist horizon — main fog tint |
| `#aab2b5` | Overcast mid sky — secondary atmospheric fill |
| `#7a8079` | Dark low fog — heaviest haze color |

### Rock &amp; mountain (5)
| Hex | Role |
|---|---|
| `#5d6770` | Mid rock — workshop foundation, observatory base |
| `#7e898d` | Distant peak — mid-band mountains |
| `#4a525c` | Dark rock shadow — crevices, cliffsides |
| `#9ea7ab` | Fog-faded distant — far peaks band |
| `#2c3540` | Deep crevice — darkest shadow tone, used sparingly |

### Snow &amp; ice (3)
| Hex | Role |
|---|---|
| `#fff5dc` | Sunlit snow — peak caps, river foam, brightest highlights |
| `#d8c8d6` | Shadowed snow — cool pink-purple tint |
| `#c8c8d4` | Old snow / ice — neutral cool |

### Pine &amp; foliage (4)
| Hex | Role |
|---|---|
| `#3a5536` | Pine canopy — dominant tree color |
| `#5a7253` | Sunlit pine — lit side of pines |
| `#283933` | Deep shade — under-canopy darkness, hero tree base |
| `#94a978` | Meadow grass — clearings, paths edge |

### Water (3)
| Hex | Role |
|---|---|
| `#9ec5d6` | Glacial river surface |
| `#5d8094` | Deeper water — ocean, river deep center |
| `#a8b8c0` | Reflective surface — light reflection on calm water |

### Warm accents &amp; earth (5)
| Hex | Role |
|---|---|
| `#f4d6b0` | Sun glow — sun disc &amp; rim halo |
| `#ffc46d` | Lantern warm — beacon, cairn lanterns, lighthouse beam, brazier flames |
| `#b87850` | Wood / lantern body — timber elements, hearth ring |
| `#6e6256` | Dirt path — trails, worn earth around spawn |
| `#9a8a72` | Sand / gravel — riverbank, beach below cliff |

**Authoring rule:** No prop may sample a color outside these 25 cells. New palette additions require a brainstorm round.

---

## 3. Spatial layout

### Dimensions (locked)
| Element | Value |
|---|---|
| Playable plateau radius | ~90m (~180m diameter) |
| Terrain mesh authored | 260×260m, ~193×193 grid (~1.35m/quad) |
| Section distance from spawn | 70m (~23-second walk at 3m/s) |
| River length on-map | ~280m incl. tributary &amp; waterfall |
| Hiking trail loop circumference | ~480m (~3-minute lap) |
| Cliff drop on western edge | ~25m down to ocean |
| Mountain silhouette start | ~120m from spawn |
| Fog fade-out | 165m (preserves existing Three.js setup) |
| Section bounding zone radius | ~12–14m (generous; UI/audio trigger) |
| Section frustum zone radius | ~9–11m (conservative; visibility) |

### World map (top-down, schematic)

```
              [ mountain band 3 — far snow peaks @ 180m ]
              [ mountain band 2 — mid peaks @ 145m   ]
              [ mountain band 1 — front ridge @ 110m ]
                          summit lookout *
                                 *
                                 |
                            (cairn trail)
                                 |
                                 N
                                 *
                          EXPERIENCE @ 70m
                                 |
                            ~ river ~
              [waterfall →] timber bridge
                                 |
                                 *
~~ocean~~  W * — — — — — SPAWN — — — — — * E
~~ocean~~  CONTACT     (wayfinder      PROJECTS  [ east foothills ]
~~ocean~~  (beacon)     + hearth)      (workshop)
~~ocean~~                    |
[lighthouse                  *
 islet ~40m                SKILLS @ 70m
 offshore]              (observatory)
                                 |
                            SE viewpoint *
                                 |
                          [ SE meadow ]
```

NW overlook, summit lookout, SE viewpoint are the three trail detours. River source = NE corner, exit = waterfall over W cliff. Tributary branches south near the projects-spawn corridor.

### Section positions (world-space, exact)

| Section | Cardinal | World pos (x, z) | Y (height on terrain) |
|---|---|---|---|
| Spawn | center | (0, 0) | 0.02 (hearth ring sits on flat-floor inner plateau) |
| Experience | N | (0, +70) | sampled from `terrain.heightAt(0, +70)` |
| Projects | E | (+70, 0) | sampled |
| Skills | S | (0, -70) | sampled |
| Contact | W | (-70, 0) | sampled (cliff-edge clearing) |
| Lighthouse islet | offshore NW | (-130, +35) | -1 (sea level, islet rises +3) |

(Note: existing `SECTION_POSITIONS` constants in code must be updated to these values.)

---

## 4. Focal structures

All five share a **stone-foundation + timber-upper + copper/iron-accents** material language. Each has exactly **one warm light source** that's visible from spawn through mist as an orienting glow.

### 4.1 Spawn hearth + wayfinder + resume lectern

- Flat clearing, 20m diameter, no foliage within 10m radius
- **Wayfinder stone:** carved obelisk, 2.2m tall, square footprint 0.5×0.5m. Faces aligned with cardinal directions. Four faces carved with the section name + small pictogram (anvil for Projects, cairn for Experience, dome for Skills, brazier for Contact). A **fifth carved emblem on the obelisk cap** (top face) shows a scroll pictogram pointing to the lectern. Material: rock palette `#5d6770` for body, `#9a8a72` for engraved edges
- **Hearth ring:** 8 fitted stones arranged in a 3m circle around a central ember pit. Embers glow faintly `#ffc46d` (lowest-intensity warm punctuation; subtle ambient hint)
- **Resume lectern:** small stone slab on a stone pedestal, placed 1.5m southwest of the wayfinder (offset so it doesn't block the cardinal-path silhouettes). Dimensions: pedestal 0.4×0.4×0.9m + slab 0.6×0.4×0.05m tilted ~20° toward the player. On top of the slab: an **open parchment scroll mesh** (~0.5×0.3m, rolled at both ends), material `#fff5dc` (cream highlight color) with darker edge wear in `#d5c4ad` (sun-rim warm) so it reads as parchment, not snow. Held flat by a small **stone weight** (`#5d6770`) on one corner. Pedestal material: `#5d6770` rock with `#9a8a72` engraved edge band
- **Resume interaction (existing pattern):** the lectern is registered via the existing `Interactables.js` + `Interaction.js` system. Walking near it surfaces an `ActionPrompts.js` cue ("Read resume" / E to interact). Pressing interact opens a modal (same component used for project showcases). **Initial modal content is placeholder** — short text like "Resume coming soon" + a link to LinkedIn / a download button stubbed out. The modal component accepts arbitrary HTML, so swapping in a real CV (formatted page or embedded PDF view) later is content-only, no geometry/spec change
- **Future-proofing:** new ref empty `refResumeInteractivePoint` placed at the lectern world position; the modal's content key (e.g. `resume`) is wired up but points to a placeholder data file `src/Portfolio/ResumeData.js` (created in the build phase with stub content). Real resume content lands in that file later
- **Four worn paths** radiate cardinally, materials = `#6e6256` (dirt) with `#9a8a72` (sand) edge fades
- Colliders: cuboid for the wayfinder, cuboid for the lectern pedestal (player can stand near it but not walk through), cylinder for hearth ring (player can walk between embers but not into them)

### 4.2 N — Experience (cairn trail)

- Trail rises from the timber bridge (4m north of spawn) up a gentle ridge to ~+95m elevation 12m above terrain
- **Cairns** (carved standing stones): 6–8 along the trail, each 0.8–1.8m tall, footprint 0.4×0.4m. Each represents one role/company on Karan's CV. Stone palette `#5d6770` body, carved face area `#9a8a72`
- Each cairn has a **small lit lantern** on top (`#ffc46d` emissive cap, copper-clad body in `#b87850`). At night the trail reads as a string of warm dots climbing the ridge
- **Trail surface:** dirt with embedded stepping-stones at the steep section
- The trail terminates at the **summit lookout** (one of the three viewpoints)
- Colliders: cuboid per cairn; trail surface is non-colliding (player walks on terrain heightfield)

### 4.3 E — Projects (workshop pavilion)

- Open-walled stone pavilion, footprint 6×5m, peaked timber roof 4m tall at apex
- **Three walls** (back + two sides) are half-height stone (`#5d6770`) topped with timber slats (`#b87850`); **front is open**
- **Anvil** at center (`#5d6770` body, `#9a8a72` worn striking surface), sized for player interaction
- **Forge** in back-left corner: stone hearth with low embers (`#ffc46d` emissive)
- **Chimney** rising 2.5m above roof, with a continuous small smoke wisp (runtime particle, ~3 particles)
- **Tool wall** on back wall: hanging hammers, tongs, files (each a small ~0.4m mesh, palette materials)
- **Project Showcase mount:** existing `Billboards.js` Project Showcase screen mounts onto the back interior wall (frame width 4m). No runtime change; the Blender geometry leaves a wall area sized to accept the screen
- Colliders: cuboid per wall, cuboid for anvil base, cylinder for forge

### 4.4 S — Skills (observatory tower)

- Squat stone tower, 3m diameter circular base, 4m tall to dome
- **Stone shaft:** drum of fitted stones `#5d6770`
- **Copper-clad dome:** half-sphere on top, `#b87850` weathered copper with edges `#9a8a72`. **Small lantern at cupola apex** (`#ffc46d`)
- **Telescope:** brass-and-wood telescope mounted on the dome, pointing at the sky
- **Base ring of artifacts:** small reading lectern, stack of scrolls, books, a single open chest with scientific instruments — arrayed around the tower base. Each existing skills sign becomes one of these artifacts
- **Door:** wooden door on the south side, decorative only (no interior, no interaction)
- Colliders: cylinder for the tower body, cuboids for artifacts

### 4.5 W — Contact (cliff-edge beacon)

- Stone platform, 3×3m, at the western cliff edge
- **Iron brazier** in the center: 3-leg tripod base (`#4a525c` iron), wide bowl (`#5d6770`), continuous flames inside (`#ffc46d` emissive with vertex animation for flicker, runtime)
- **Smoke trail:** runtime particle system blowing east in the wind (~15 particles, slow drift)
- **Inscription plinth:** small stone marker beside the brazier, carved with contact glyphs (links to social/email forms in the runtime modal)
- This section is **the most warm-saturated point in the world** — visible from spawn through mist as a strong glow
- Colliders: cuboid for platform, cylinder for brazier base

### 4.6 Lighthouse on offshore islet

- Rocky islet ~60m offshore (world pos (-130, +35), distance ~135m from origin), 8m diameter, rises 3m above sea level
- **Lighthouse:** thin tall cylinder, 8m tall, 1m diameter at base tapering to 0.8m at top
- **Body:** stone palette `#9ea7ab` with horizontal `#fff5dc` (white) bands every 2m
- **Glass cupola:** at top, `#9ec5d6` glassy material, contains a warm lamp `#ffc46d`
- **Rotating beam:** a child Object3D rotates slowly (runtime tween, ~6° per second). The beam itself is a low-opacity cone of `#ffc46d` light, ~20m long
- **No collider needed** — the islet at r≈135 sits past the existing soft-clamp at r=120 (CLAUDE.md world-layout rule), so the player is pushed back before reaching it. Lighthouse is **purely visual** — visible from spawn through mist as a distant glow
- The lighthouse is the second-strongest warm punctuation; together with the Contact beacon they form a visual line "beacon → ocean → lighthouse → infinity"

---

## 5. Foliage

### 5.1 Tree inventory

| Species | Variants | Instances | Placement |
|---|---:|---:|---|
| Primary pine (conifer) | **7** | ~90 | Forest fabric — heaviest NE, lightest SW |
| Secondary birch (deciduous, slender) | **5** | ~35 | Clearing margins, riverbank, scattered |
| **Hero ancient pine** | **1** unique mesh | **5** | Hand-placed landmarks |
| **Total** | **13 unique meshes** | **~130 instances** | InstancedGroup pattern |

**Hero tree placement (5):**
1. Near Experience cairn trail base — visible from spawn as a silhouette
2. Near Projects workshop — anchors the eastern silhouette
3. Near Skills observatory — anchors the southern silhouette
4. At the NE forest clearing (where the deer occasionally appears)
5. At the summit lookout — most dramatic silhouette, frames the view

### 5.2 Ground cover inventory

| Type | Variants | Instances |
|---|---:|---:|
| Ferns | 3 | ~40 |
| Wildflowers (pink + yellow + white clusters) | 4–5 | ~80 |
| Mossy boulders | 5 | ~30 |
| Tall grass / sedge | (existing instanced billboard, continue use) | dense |

### 5.3 Distribution rules

- Heaviest cluster density: NE quadrant (forest pushing down from mountains)
- Lightest density: SW quadrant (meadow + flowers, readable from the SE viewpoint)
- **Exclusion zones** (auto-generated, no foliage placed within):
  - 5 focal structures: 6m buffer each
  - River + tributary corridor: 5m buffer
  - Hiking trail (full loop + detours): 2m buffer
  - Lighthouse islet: entire islet
  - Three viewpoints: 4m buffer each
- Birches preferentially placed near riverbank + clearing margins
- Hero trees: hand-placed in Blender with manual transforms (not scattered)

### 5.4 Implementation

- Uses Bruno's `InstancedGroup` pattern: one `THREE.InstancedMesh` per unique mesh × material combination
- Trees use existing `Nature.addExclusion(x, z, r)` API — extend with new exclusion calls
- Hero trees use `THREE.Mesh` (only 5 of them; instancing overhead not worth it)
- All foliage gets the shared wind shader (smooth-lit material variant; see §10)

---

## 6. Mountain treatment

Three cardboard cutout layers + eastern foothills layer = 4 quads total.

| Band | Distance | Texture | Role |
|---|---|---|---|
| Front ridge | ~110m | Tilted quad plane with painted silhouette PNG (hand-authored, palette colors via UV), palette colors via UV | Tallest visible peaks; partial north only |
| Mid peaks | ~145m | Tilted plane, additional snow caps layer | Primary snow-cap visual |
| Far snow peaks | ~180m | Tilted plane, heavy alpha-fade, most snow | Tallest, most faded, farthest |
| Eastern foothills | ~120m | Tilted plane (lower silhouette) | Differentiates east from north |

**Texture detail:** each mountain band's texture is a single PNG painted with the silhouette + palette colors. Snow caps are a **separate alpha-blended layer** on top, using `#fff5dc`. Per-band fog factor in shader fades the mountain by distance.

**Cost:** 4 quad planes (~8 triangles total), negligible.

**Implementation:** Extends existing `src/World/DistantIslands.js`. Renamed to `DistantMountains.js` or similar; same rendering pattern.

---

## 7. River, waterfall, bridges

### 7.1 River geometry

- **Bezier curve** authored in Blender (~12 control points, snaking from NE source to W cliff)
- Extruded into a flat ribbon mesh with **varying width** (2m at narrow switchbacks, 5m at wide bends) — Bruno's `curveRoad` pattern
- **Tributary** = second Bezier curve, 1.5m uniform width, branches south from the main river near the projects-spawn corridor

### 7.2 River surface material

Custom `ShaderMaterial`:
- Base color: palette `#9ec5d6` (glacial river)
- **Animated UV scroll** along the curve direction at ~0.1 m/s (gives a flow appearance)
- **Edge foam strip** in `#fff5dc` along both banks (3-pixel strip in UV)
- Smooth Lambert lighting from the sun
- No reflectivity (cheaper than real water)

### 7.3 Waterfall

- **Single vertical plane** at the western cliff edge, 3m wide, 20m tall
- **Custom shader:** falling-stripe texture (vertical lines scrolling downward), color `#9ec5d6` with foam highlights `#fff5dc`
- **Spray at base:** runtime particle system, ~20 particles, 2m tall plume

### 7.4 Bridges

- **Main bridge:** timber-plank construction over the main river ~5m north of spawn. Span 5m, width 2m, 8 plank meshes + 2 stone supports. Materials: `#b87850` timber, `#5d6770` stone
- **Tributary stepping-stones:** 3 flat stones across the tributary, ~0.6m diameter each, top surface placed ~0.15m above water surface (so player feet land on stone, not in water). Stones spaced ~0.7m apart so a single stride covers each gap. Material `#5d6770`. No bridge mesh between them
- Colliders: cuboid for bridge deck + cylinders for stone supports + cylinders per stepping-stone

### 7.5 Fish (out of scope — runtime, listed for completeness)

Runtime instanced billboard quads, ~6–8 total, gentle wander animation. Lives in `src/Wildlife/` (future session).

---

## 8. Hiking trail + viewpoints

### 8.1 Perimeter loop

- **Bezier curve** authored in Blender, ~80m radius from spawn (between the 70m section positions and the 90m plateau edge)
- Extruded into a flat ribbon mesh, 1.2m wide, material = `#6e6256` (dirt) with subtle `#9a8a72` (sand) variation
- ~480m total circumference, ~3-minute walk at 3m/s
- Surface non-colliding (player walks on terrain heightfield); the ribbon is purely visual

### 8.2 Viewpoint detours

Three detour spurs branching off the perimeter loop:

| Viewpoint | Location | Marker | What you see |
|---|---|---|---|
| **NW overlook** | Cliff edge between Contact and Experience | Single carved waystone (0.8m tall, palette `#5d6770`) | Ocean to the west, north peaks to the north, lighthouse in the distance |
| **Summit lookout** | Climbs N past Experience, highest playable point (~12m elevation) | Single carved waystone | Looks back over the whole composition: spawn, sections, river, mountains |
| **SE viewpoint** | South meadow, low point | Single carved waystone | Looks back at the world from outside the playable plateau perspective |

Each viewpoint marker is a single static mesh with no interaction logic. The trail is **exploratory, not required** — cardinal section paths remain the main UX.

---

## 9. Sun, camera, atmosphere

Tuning-only changes to existing runtime files; no new systems.

| Setting | Value | File |
|---|---|---|
| Sun elevation (default) | ~12° (low, dawn-rim) | `src/World/Sun.js` |
| Sun color | `#f4d6b0` (warm peach) | `src/World/Sun.js` |
| Sun shadow softness | 3 desktop / 2 mobile | unchanged |
| Ambient color | `#aab2b5` (cool grey-blue) | `src/App.js` (`ambientLight`) |
| Camera FOV | **50°** | `src/Player/PlayerCamera.js` |
| Camera follow distance | existing `camera-controls` smoothing | unchanged |
| Fog color | `#e0d4c0` (mist horizon) | `src/App.js` (`scene.fog`) |
| Fog band — near (0–30m) | no fog | new distance bands in shader |
| Fog band — mid (30–100m) | light haze | new |
| Fog band — far (100–165m) | dense haze, mountains fade | new |
| Beyond 165m | cardboard mountains visible but heavily faded | new |
| Day cycle duration | 4 minutes (240s) | unchanged from `src/World/TimeOfDay.js` |
| Cycle keyframes | dawn (0–40s) → morning (40–100s) → midday (100–160s) → golden (160–200s) → dusk (200–240s) | retune `src/World/TimeOfDay.js` |
| Lantern/brazier emissive | `#ffc46d` | new palette color used in materials |
| Rain intensity | lighter showers, heavier mist | retune `src/Effects/Rain.js` |
| Lightning | unchanged | `src/Effects/Thunderstorm.js` unchanged |

---

## 10. Materials &amp; shading

### 10.1 Master material — `SmoothLitPaletteMaterial`

New material class. WebGL `ShaderMaterial` (no TSL). Composes:

1. **Palette sampling:** `texture(palette, uv).rgb` as base color
2. **Smooth Lambert lighting:** `dot(N, L)` clamped 0–1, mixed against the base color (no cel band)
3. **Fake light bounce:** sample terrain palette color where `normal.y < 0` (downward-facing surfaces tinted by ground)
4. **Distance-band fog:** smoothstep fog factor with the 4 distance bands described in §9
5. **Wind displacement** (vertex shader): shared `windNode` Fn — fractal Perlin displacement on world position + time, modulated by `Weather.wind` output. Applied to grass, foliage, trees, hero trees
6. **Reveal wipe** (Bruno's #3.6): `revealUniform = vec3(cx, cy, radius)`; per-fragment `discard()` if outside the revealing radius. Used once on world load via a single GSAP tween

All world props use this material unless they need a special variant (§10.2).

### 10.2 Special material variants

| Material | Use | Variation from master |
|---|---|---|
| `EmissiveGradient` | Lanterns, beacon flames, hearth embers, lighthouse cupola | Center-to-edge radial gradient + emissive intensity |
| `WaterSurface` | River + tributary surface | Animated UV scroll + edge foam strip |
| `WaterfallStripe` | Waterfall plane | Vertical stripe animation, no Lambert lighting |
| `MountainCardboard` | The 4 mountain band quads | Heavy distance-fog override, alpha-fade |
| `LighthouseBeam` | Rotating beam cone | Low-opacity additive blend |
| `ShadowedSnow` | Hero peak snow caps | Smooth gradient `#fff5dc` → `#d8c8d6` |

### 10.3 Palette texture asset

- File: `static/textures/palette.png`
- Dimensions: 128×4 px
- Format: sRGB, 4-channel (RGBA, alpha unused but kept for consistency)
- Loaded with `NearestFilter` magnify + minify, `generateMipmaps = false`, `colorSpace = THREE.SRGBColorSpace`
- Authored manually as a PNG (Blender plugin or image editor); 25 colors per §2 in specific cells, UV-aligned

---

## 11. Blender authoring conventions (from Bruno, adopted)

### 11.1 Single master GLB

All world geometry exports to one file: `static/world/world.glb`. Runtime walks the scene and dispatches by name.

### 11.2 Name-prefix dispatch

| Name pattern | Runtime treatment |
|---|---|
| `ref*` | Empty marker — parsed for position + scale-as-radius + userData |
| `cuboid*` | Static cuboid collider (Bruno's pattern: half-extents from scale) |
| `tube*` | Static cylinder collider |
| `trimesh*` | Triangle-mesh collider for complex shapes |
| `*Physical*` | RAPIER body becomes dynamic |
| `*KinematicPositionBased*` | RAPIER body becomes kinematic |
| Anything else | Static mesh, no collider |

### 11.3 Ref empties for runtime metadata

| Empty name | Purpose |
|---|---|
| `refZoneBounding_spawn`, `refZoneBounding_projects`, etc. | Section bounding cylinder (radius from scale) |
| `refZoneFrustum_*` | Per-section frustum-test cylinder |
| `refInteractivePoint_*` | World-space anchor for DOM-projected labels |
| `refRespawn_*` | Player respawn position (one per section) |
| `refHeroTree_1` … `refHeroTree_5` | Hero tree placement anchors |
| `refLighthouseBeamPivot` | Rotation pivot for the lighthouse beam |
| `refWaterfallSpray` | Anchor for runtime spray particles |
| `refForge`, `refBrazier`, `refHearth`, `refCairnLantern_*` | Anchors for runtime light + particle effects |

### 11.4 InstancedGroup

Repeated props authored as Blender instances ("reference" instances in the same collection). Runtime detects identical mesh data and builds one `THREE.InstancedMesh` per material × geometry, with all other instances becoming transform refs.

Used for: pines (×~90 in 7 variants), birches (×~35 in 5 variants), ferns (×~40), flowers (×~80), boulders (×~30), cairns (×~8), bridges/stones, lantern bodies.

### 11.5 Collection structure (Blender outliner)

```
world.blend
├── terrain                  (terrain mesh + heightfield mod)
├── spawn                    (wayfinder, hearth ring, paths)
├── sections/
│   ├── projects             (workshop pavilion + anvil + forge)
│   ├── experience           (cairn trail + cairn lanterns)
│   ├── skills               (observatory + artifacts)
│   └── contact              (cliff platform + brazier)
├── lighthouse               (islet + lighthouse + beam pivot)
├── water/
│   ├── river                (main bezier ribbon)
│   ├── tributary            (small bezier ribbon)
│   ├── waterfall            (vertical plane)
│   └── ocean                (large flat plane, west side)
├── bridges                  (main bridge + stepping stones)
├── trail/
│   ├── perimeter            (perimeter loop ribbon)
│   ├── detour_nw            (NW overlook spur)
│   ├── detour_summit        (summit lookout spur)
│   └── detour_se            (SE viewpoint spur)
├── viewpoints               (3 waystone markers)
├── foliage/
│   ├── trees                (instanced pines + birches)
│   ├── hero_trees           (5 ancient pines, individual)
│   ├── ground_cover         (instanced ferns + flowers + boulders)
│   └── grass                (existing instanced billboard, unchanged)
├── mountains                (4 cardboard quad bands)
└── refs                     (all ref* empties, organized by section)
```

---

## 12. Performance budget

Targeting a 5-year-old laptop @ 60fps + mobile-comfortable.

| Budget | Target | Notes |
|---|---|---|
| Total world triangles | < 100,000 | Bruno's full world: 110,580 — we have similar budget |
| Static draw calls | < 80 | InstancedGroup keeps this low |
| Materials (unique) | < 12 | One master + ~6 variants + a few labels |
| Texture memory | < 8 MB | Palette = 362 B; all others compressed KTX2 |
| Wildlife | ≤ 15 animated entities visible at once | Runtime; out of this spec |
| Mountains | 4 quads = ~8 tris | Free |
| Foliage instances | ~280 total | Bruno had ~340 (130 bushes + 108 flowers + 70 trees + 30 bricks) |
| Lights | 1 directional sun + ambient + ~8 point lights (lanterns/brazier/forge/lighthouse) | Point lights cluster-near-camera, gated by distance |

**Hot-path optimizations** (adopt from Bruno):
- `renderer.setPixelRatio(Math.min(devicePixelRatio, 2))`
- `renderer.sortObjects = false` once mesh count > 500 (manual `renderOrder` via Bruno's #2.2)
- Per-area `update()` gated by frustum-zone test (Bruno's #4.7)
- Adaptive DPR already adopted (commit d3b2331)

---

## 13. Pattern adoption matrix (Bruno → ours)

| Pattern | Adopt? | Notes |
|---|---|---|
| Palette texture (128×4 sRGB NearestFilter) | **Yes** | Core to our art direction |
| One master smooth-lit material | **Yes** | Smooth Lambert, not cel-band |
| NPR core-shadow smoothstep | **No** | Replaced with smooth Lambert |
| Fake light bounce from terrain | **Yes** | Cheap GI |
| Reveal/discard wipe | **Yes** | World-load entrance effect |
| Shared wind node (vertex displacement) | **Yes** | WebGL ShaderMaterial port (no TSL) |
| Emissive radial-gradient | **Yes** | Lanterns + brazier + lighthouse cupola |
| Single master GLB + name-prefix dispatch | **Yes** | `world.glb` is source of truth |
| `ref*` empty markers | **Yes** | Section bounding + interactive points + animation anchors |
| Scale-encodes-radius | **Yes** | Standard convention |
| Collider via mesh-name prefix | **Yes** | `cuboid*`, `tube*`, `trimesh*` |
| InstancedGroup | **Yes** | Trees, ground cover, cairns |
| Per-area `update()` only when in frustum | **Yes** | Adopt for the 4 sections |
| Distance-based physics sleep | Defer | Existing physics may already handle |
| Frame-time cap + global time scale | **Yes** | Universal win, regardless of world |
| 25° telephoto FOV | **No** | We use 50° for cinematic-vast |
| cheapDOF | **No** | Requires fixed camera |
| RAPIER `setActiveEvents` gating | **Yes** | Free perf |
| Initial-state snapshot for respawn | **Yes** | Existing pattern, keep |
| Day/Year/Weather cycles | **Yes** | Existing `TimeOfDay.js` works; retune keyframes |
| Howler audio groups + pool | **Yes** | Existing `AudioManager.js` keeps |
| `VITE_COMPRESSED` env switch | **Yes** | Dev vs prod asset switch |
| Compression pipeline | **Yes** | Already adopted (commits 2076a3d, 8fc5ad2) |

---

## 14. What runtime stays the same (no design change)

These existing systems remain untouched by the world rebuild:

- Player character (Avaturn + Mixamo) and animations
- `PlayerController` movement &amp; input
- Rapier3D physics integration (only the heightfield + collider sources change)
- Achievements (34 unlocks system)
- Map system (mini-map + overlay + teleport + Navmask)
- Audio manager (Howler-based)
- UI overlays (welcome, loading, interaction modal, tutorial, compass, action prompts)
- Discovery tracking, distance mini-game
- Torch (night-mode hand-attached light)
- Verification sandbox conventions (`.verify/scripts/` + `.verify/shots/YYYY-MM-DD/`)

---

## 15. Implementation outline (deferred to next session)

The next session uses the `writing-plans` skill to produce a phased Blender Python build plan. Expected high-level phases:

1. Palette texture authored as PNG, runtime palette material wired up
2. Terrain mesh authored in Blender (heightfield bake or sculpted)
3. Spawn hearth + wayfinder
4. Workshop pavilion (Projects)
5. Observatory tower (Skills)
6. Cairn trail (Experience)
7. Beacon platform (Contact)
8. Lighthouse + islet
9. River + tributary + waterfall + bridges
10. Hiking trail + viewpoint markers
11. Foliage (trees + ground cover + hero trees)
12. Mountain cardboard bands
13. Material library (`SmoothLitPaletteMaterial` + variants)
14. Runtime wiring: replace `Terrain.js` / `Nature.js` / `Paths.js` / `DistantIslands.js` with GLB-driven equivalents
15. Sun + fog + camera + day-cycle retuning
16. End-to-end verification via `.verify/scripts/`

Each phase will:
- Have its own deliverable artifact in `.blend` form
- Get a verification screenshot in `.verify/shots/<date>/`
- Be reviewed before the next phase ships

---

*End of spec. See `reports/world-design-decisions.md` for the reasoning trail of each numbered decision.*
