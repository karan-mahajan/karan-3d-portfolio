# World design decisions — running log

> Running alignment record for the Blender-authored world rebuild. Each section captures one decision Karan made during the brainstorming session, the alternatives considered, and the reasoning. Subsequent sessions read this to skip re-litigating settled choices.
>
> Source brainstorm: 2026-05-26 session. Companion artifacts live under `.superpowers/brainstorm/` (gitignored).

---

## Out of scope (not decided here)

These are deferred to the implementation-planning session:

- Specific Blender Python scripts, file structure under `tools/blender-scripts/v2/`
- Specific 3D asset sources (Kenney vs Sketchfab vs hand-modeled)
- Collision shapes, mesh subdivision targets, draw-call budgets per material
- The exact runtime hookup (how the GLB replaces the procedural terrain in `src/World/Terrain.js`, `Nature.js`, `Paths.js`)

This doc captures **what the world is**, not **how we build it**.

---

## 1. Spawn mood — *Awe &amp; cinematic vast*

**Decision:** When a visitor spawns, the dominant emotion should be **awe** — a "this is a portfolio?" reaction. Scale + horizon + breathing room over cozy intimacy.

**Alternatives rejected:**
- *Cozy &amp; welcoming* (Bruno-adjacent) — risked reading as derivative; we want a clear visual fingerprint
- *Curious &amp; quietly mysterious* (Ghibli) — high replayability but harder to author-balance for first-impression impact
- *Playful &amp; whimsical* (Animal Crossing) — strong personality but undermines the "hire me" credibility signal

**Implications already absorbed:**
- Cannot use Bruno's 25° telephoto FOV — that sells diorama, the opposite of cinematic. Wider FOV (50–60°) is the working assumption; final number set in a later decision.
- Loses Bruno's cheapDOF trick (needs fixed camera) — accept that loss.
- Loses Bruno's "compress everything into one screen" framing — gain "you can see far."

---

## 2. Awe source — *Natural / geological*

**Decision:** The land itself is the spectacle. Mountains, valleys, river canyon, scale of geology. No single monumental architecture as the focal point; the silhouette of the land is the hero.

**Alternatives rejected:**
- *Architectural / monumental* (Shadow of the Colossus tower) — strong narrative but locks the world to one structure
- *Cosmic / celestial* (Outer Wilds) — sky does the work, but night-dominant world hurts engagement and existing portfolio is day-leaning
- *Layered (land + one hero structure)* — was the recommendation, rejected in favor of pure-natural to keep the geometry budget on terrain &amp; foliage

**Implications:**
- Mountains must read at distance — silhouette quality matters more than detail
- River is a primary feature, not decoration — visible from spawn, runs across the playable area
- Per-section buildings (Projects/Skills/Contact/Experience) are small focal nooks inside the natural landscape, not the world's anchors

---

## 3. Biome — *Alpine misty highlands*

**Decision:** Pine forests, snow-capped peaks, glacial river, low fog over a plateau. Cool dominant palette with warm sun accents. Skyrim / Witcher 3 vibe, not Studio Ghibli.

**Alternatives rejected:**
- *Mediterranean cliffs &amp; olive groves* — warmer mood, underused in games, but doesn't match the cool-awe target
- *Desert canyon &amp; mesa* (Journey / Sable) — cheap foliage budget, distinct silhouette, but emotionally arid for a portfolio first impression
- *Japanese valley + distant peak* — popular = familiar but risks anime read; deferred

**Palette anchor colors (from biome card; not final):**
- `#d4c5a3` warm hazy sky
- `#94a978` meadow green
- `#3a5536` pine green
- `#5d6f74` rock
- `#7a8a92` distant peak
- `#fff5dc` snow
- `#9ec5d6` glacial water

**Implications for build:**
- Pine silhouettes are low-poly-friendly (a cone is most of the work) — foliage budget can support density
- Distant peaks become cardboard cutouts behind heavy atmospheric haze (FPS-cheap version of mountains)
- Glacial river = flat plane + subtle normal scrolling + foam at edges; not a curve-extruded geometry
- Snow caps are paint, not geometry — palette + UV authoring puts white on upward-facing peak faces
- Existing fog color `#ffb084` (warm peach) **will change** to a cool blue-grey-with-warm-rim — current sunset tinting fights the alpine mood

---

## 4. Time-of-day signature — *Misty dawn*

**Decision:** The world is **tuned to misty dawn**. Pre-sunrise haze, sun barely a glow on the horizon, layers of mountain silhouettes fading into mist. Cool blue-grey dominant with one warm rim. This is the spawn frame, the loading screen tone, and the palette anchor.

**Cycle still runs:** existing `TimeOfDay.js` continues to drive day/dusk/night/dawn. This decision picks the **default state and the palette anchor**, not a frozen environment.

**Alternatives rejected:**
- *Golden hour* — too Bruno-adjacent; would need cool-mountain palette tricks to distinguish
- *Blue hour* — most distinctive but loading-screen / first-glance reads murky on bad monitors
- *Overcast painterly* — narrows the color budget; doesn't sell "vast"

**Implications:**
- Existing fog tint `#ffb084` (warm peach) **changes** to a cool blue-grey-with-warm-rim — needs the sun-edge to remain warm so the sky has a focal point
- Ambient + bounce light tilts cool; sun contribution stays warm but subtle
- **Risk to mitigate:** dawn alone can feel cold/lonely → ground decoration and warm interior lights (lantern at each section, bonfire-glow at spawn) must compensate. Plan for warm-pinprick punctuation in the palette.
- Snow caps catch first warm light — the only consistently-warm surface in the world other than the sun and lanterns. That's the cinematic frame.
- The Bruno palette is warm-dominant (11 of 25); ours **inverts** that ratio — more cool/desaturated, with sparser warm accents that hit harder.

---

## 5. Art direction — *Stylized smooth-lit*

**Decision:** Palette-texture-driven base color (Bruno's cohesion trick) + smooth Lambert lighting + heavy atmospheric haze. **No cel band.** The signature is in the atmosphere, not the shadow edge.

**Alternatives rejected:**
- *Cel-shaded NPR (Bruno)* — cheapest shader, but the realistic-leaning Avaturn character looks uncanny in a cel world; also reads as Bruno-derivative
- *Painterly textured* — strongest design statement but high authoring cost (per-prop hand-painted textures); larger memory footprint hurts mobile
- *Low-poly clean (Kenney)* — wrong vibe for awe-cinematic; demo-scene reading

**Implications:**
- **Palette texture still adopted** — Bruno's 128×4 sRGB + NearestFilter trick stays; only the lighting model changes
- WebGL `ShaderMaterial` reimplementation of: palette UV sampling + smooth Lambert + atmospheric fog mix + reveal wipe + shared wind (no TSL)
- Atmospheric haze layers do the heavy lifting — must be tuned per-distance band (near 0–20m no haze, mid 20–60m subtle, far 60m+ aggressive)
- Avaturn character lands naturally in this world; no special character shader work needed
- Future bounce-light pattern (Bruno's "tint downward-facing fragments by terrain color") still adopt — cheap GI
- **Reference target:** Genshin Impact's alpine areas, Sky: Children of the Light, Honkai Star Rail nature areas (smooth shading, palette cohesion, atmospheric depth)

## 6. Final palette (25 colors, draft) — *Mid-saturated / cohesive*

**Decision:** 25-color palette in Bruno's 5-category structure (sky / rock / snow / pine / water / warm-accent / earth), tuned to **mid-saturated cool-dominant with warm pinpricks**. Cohesive but readable on bad monitors. Genshin-alpine reference saturation, not desaturated-Sable or punchy-Honkai.

**Draft hex values** (subject to in-engine tuning during build phase):

| Category | Hex codes |
|---|---|
| Sky &amp; atmosphere (5) | `#c6c3bc` sky high · `#d5c4ad` sun-rim warm · `#e0d4c0` mist horizon · `#aab2b5` overcast mid · `#7a8079` dark low fog |
| Rock &amp; mountain (5) | `#5d6770` mid rock · `#7e898d` distant peak · `#4a525c` dark rock shadow · `#9ea7ab` fog-faded distant · `#2c3540` deep crevice |
| Snow &amp; ice (3) | `#fff5dc` sunlit snow · `#d8c8d6` shadowed snow · `#c8c8d4` old snow/ice |
| Pine &amp; foliage (4) | `#3a5536` pine canopy · `#5a7253` sunlit pine · `#283933` deep shade · `#94a978` meadow grass |
| Water (3) | `#9ec5d6` glacial river · `#5d8094` deeper water · `#a8b8c0` reflective surface |
| Warm accents &amp; earth (5) | `#f4d6b0` sun glow · `#ffc46d` lantern warm · `#b87850` wood/lantern body · `#6e6256` dirt path · `#9a8a72` sand/gravel |

**Authoring contract:**
- Palette texture is **128×4 sRGB**, sampled via NearestFilter (Bruno's pattern preserved)
- Each prop's UV layout snaps faces to specific palette cells in Blender
- Runtime shader samples `texture(palette, uv).rgb` as `colorNode` input to the smooth-lit material

**Alternatives rejected:**
- *Desaturated muted* — gallery-piece feel; risk of washing out on bad monitors and reading as "lonely"
- *Saturated dramatic* — punchy and screenshot-ready but reads as "game" rather than designer-portfolio

**Implications:**
- Warm pinpricks (`#ffc46d`, `#f4d6b0`) must be **sparse** — they're the punctuation. Used at: lanterns, sun rim, snow caps catching first light, fire/forge glows
- Existing `#ffb084` warm fog tint retires; replaced with cool atmospheric haze derived from `#e0d4c0` (mist) and `#9ea7ab` (fog-faded distant)
- 25 colors is the budget — adding props that don't fit the palette is forbidden during build (forces UV authoring discipline)

---

## 7. Cardinal section narratives — *Traveler's Refuge*

**Decision:** A mountain dweller has set up four functional posts around a central hearth at spawn. All four sections share an **alpine stone-foundation + timber-upper + copper/iron-accents** architectural language. Each post is function-differentiated by its working tools, not its building style.

**Per-section concept:**

| Cardinal | Section | Focal structure | Warm light source |
|---|---|---|---|
| **N** | Experience | Cairn trail rising up a gentle ridge; each carved stone marker holds one role/company | Lit cairn lanterns along the trail |
| **E** | Projects | Open-walled workshop pavilion with stone floor; anvil + tool wall + the Project Showcase screen mounted on the back board | Forge fire (low ember + smoke from chimney) |
| **S** | Skills | Squat stone tower (3–4m) with a copper-clad dome on top; telescope, scrolls/books arrayed at the base | Lantern on dome cupola |
| **W** | Contact | Tall iron brazier on a stone platform at the cliff edge; flames trail eastward in the wind | The brazier itself (largest warm punctuation in the world) |
| **center** | Spawn | Carved wayfinder stone (obelisk) + a hearth-ring of fitted stones; four worn footpaths radiate outward into the mist | Hearth coals (subtle, not a fire) |

**Alternatives rejected:**
- *Outposts of Discipline* — distinct silhouettes per direction (temple / workshop / grove / lighthouse) read as themed-park, lose the "one world" feel
- *Megalith Shrines* — minimal carved stone is cheapest, but reads as pagan-fantasy rather than designer-portfolio; less warmth

**Implications:**
- The four focal structures plus spawn = **5 hero pieces** Blender needs to author. Bruno had 14 areas; ours has 5. The asset budget per piece is correspondingly larger.
- Wayfinder stone at spawn is the first thing the player sees — must communicate "you can walk in four directions" without any UI prompt
- Existing `Billboards.js` Project Showcase mounts onto the workshop's back board (no runtime change; the GLB wraps geometry around it)
- Existing `Signs.js` array along `experiencePath` becomes carved-stone cairns along the trail (visual swap, runtime contract unchanged)
- The brazier on the west cliff is the single most-saturated warm punctuation in the world — visible from spawn through the mist as a glow, makes the W section the most magnetic on first arrival
- Each section's warm light source is positioned to be **visible from spawn through the mist** — gives the player four orienting glows to walk toward

---

## 8. World extent &amp; layout — *180m playable, river + trail + wildlife*

**Decision:** A 180m-diameter playable plateau on a 260m-square authored terrain, with sections at 70m from spawn (≈23-second walk). River meanders 280m through the plateau and spills over the western cliff as a waterfall; perimeter hiking trail with three viewpoint detours; wildlife placed where it makes sense; one offshore lighthouse anchors the ocean view.

**Spatial spec:**

| Element | Value |
|---|---|
| Playable plateau radius | **~90m** (≈180m diameter) |
| Terrain mesh authored | **260×260m**, ≈193×193 grid (≈1.35m/quad) |
| Section distance from spawn | **70m** (≈23-second walk at 3m/s) |
| River length on-map | **~280m** Bezier incl. tributary &amp; waterfall |
| Hiking trail loop circumference | **~480m** (≈3-minute lap) |
| Cliff drop on western edge | **~25m** down to ocean |
| Mountain silhouette start | **~120m** from spawn (cardboard, fog-faded) |
| Fog fade-out | **165m** (preserves existing Three.js setup) |
| Section bounding zone radius | **~12–14m** (generous; bounding triggers UI / audio) |
| Section frustum zone radius | **~9–11m** (conservative; drives visibility per Bruno's #4.7) |

**River path:**
- Source: NE corner, high in the mountains (cardboard at distance)
- Switchbacks SW through the plateau, passing north of spawn
- One tributary branches south near projects/skills
- Exits over the **western cliff as a waterfall**, ~20m drop into ocean
- **Crossings**: one timber bridge north of spawn (Experience trail), stepping-stones over tributary
- Implementation: Bezier curve in Blender, extruded into ribbon mesh (Bruno's `curveRoad` pattern)

**Hiking trail:**
- **Perimeter loop** at ~80m radius from spawn — circumnavigates all four sections without entering any
- **Three viewpoint detours:**
  - **NW overlook** — cliff edge between Contact and Experience, ocean + north peaks view
  - **Summit lookout** — climbs steeper terrain north of Experience, highest point in the playable area
  - **SE viewpoint** — south meadow, looks back at the world (the only place to see the whole composition from outside)
- Marked by a single small carved waystone at each viewpoint + a worn dirt path
- Trail is **exploratory, not required** — the cardinal section paths handle the main UX

**Lighthouse in ocean:**
- Small rocky islet **~40m west of the western cliff**, slightly NW of the Contact beacon
- **Single tall thin lighthouse** with a warm rotating beam (subtle, slow rotation) and a steady warm lamp at top
- **Narrative function:** the Contact beacon signals OUTWARD toward this lighthouse — visitor's eye traces "beacon → ocean → lighthouse → infinity"
- **Static Blender asset** (geometry + collider-less since it's offshore); the rotating beam is a small runtime tween on a child Object3D
- One of the strongest warm punctuation points in the world; visible from spawn through mist as a distant glow

**Wildlife (high-level — runtime placement, not Blender):**
- **Birds in flight** — small flock over the plateau, V-formation, drifts slowly; uses existing `bird-fly.glb` + `bird-fly-2.glb`
- **Birds perched** — on cairn stones (Experience trail), workshop roof (Projects), observatory dome (Skills); existing `bird-perched*.glb`
- **Ground bird** — near the spawn hearth; existing `bird-ground.glb`
- **Frog** — at riverbank near the timber bridge; existing `frog.glb`
- **Deer/elk** — distant glimpse at NE forest clearing, occasionally visible, retreats if player approaches *(asset TBD; ask user before adding)*
- **Rabbits** — small, in SE meadow + along the perimeter trail *(asset TBD; ask user)*
- **Fish in river** — small visual flicks at 3 river points; instanced mesh or particle *(asset TBD)*
- **Owl** — perched on a cairn at night only; signature night-mode creature *(asset TBD)*

Wildlife will be added **as scenes call for it** (per Karan, not pre-specced). Runtime system will live in `src/Wildlife/` (new module) — out of scope for this brainstorm.

**Weather/sun (already in code — retune only, no redesign):**
- `Rain.js` + `Thunderstorm.js` stay; retuned for alpine character (lighter showers, heavier mist)
- `Sun.js` + `TimeOfDay.js` stay; anchor sun colors at misty-dawn (cool ambient + warm rim sun)
- No new effects added in this brainstorm

**Alternatives rejected:**
- *v1 smaller world (120m)* — sections at 45m felt cramped given the awe-cinematic mood
- *Even bigger (240m+)* — pushes section walk time past 30s, FPS risk on mobile/old laptops

**Implications for build:**
- Existing `src/World/Terrain.js` heightfield must regenerate to 260×260m with the new layout
- Existing `src/World/Paths.js` becomes the perimeter trail + viewpoint detours (currently only does worn paths from spawn)
- Existing `src/World/Nature.js` exclusion zones now must avoid: 5 focal structures, river+tributary, trail, viewpoints, lighthouse islet
- New module `src/Wildlife/` for animal placement + per-creature behavior (out of scope here)
- `static/models/wildlife/` will grow — additions asked before each (rule 1 of CLAUDE.md)

---

## 9. Foliage style &amp; density — *Medium clustered with hero trees*

**Decision:** Pines cluster into small groves separated by open clearings; birches scatter in the clearings; **4–5 hero ancient pines** placed individually as 3–4× taller landmarks. Medium ground cover (flowers, ferns, mossy boulders, grass).

**Tree budget:**

| Species | Variants | Instances | Role |
|---|---:|---:|---|
| Primary pine (conifer cone) | 7 | ~90 | Main forest fabric |
| Secondary birch (deciduous, slender) | 5 | ~35 | Clearings + river bends |
| **Hero ancient pine** | 1 unique | 5 | Landmarks visible from spawn |
| **Total tree instances** | | **~130** | |

**Ground cover:**

| Type | Variants | Instances |
|---|---:|---:|
| Ferns | 3 | ~40 |
| Wildflowers (pink + yellow + white clusters) | 4–5 | ~80 |
| Mossy boulders | 5 | ~30 |
| Tall grass / sedge | (continue existing instanced billboard) | dense |

**Hero tree placement (5):**
1. Near Experience cairn trail (visible from spawn as a silhouette over Experience)
2. Near Projects workshop (anchors the eastern silhouette)
3. Near Skills observatory (anchors the southern silhouette)
4. At the NE forest clearing where the deer appears
5. At the summit lookout (most dramatic silhouette, frames the view)

**Distribution rules:**
- Heaviest cluster density in NE quadrant (forest pushing down from mountains)
- Lightest in SW quadrant (meadow + flowers — readable from the SE viewpoint)
- Exclusion zones around: 5 focal structures (sections + spawn), river+tributary corridor (5m buffer), entire hiking trail (2m buffer), lighthouse islet, viewpoints
- Birches favor riverbank + clearing margins
- Hero trees are hand-placed (manual transforms in Blender), not scattered

**Alternatives rejected:**
- *Sparse alpine (60 trees)* — too thin for "more trees" request; sections dominate sightlines too much
- *Dense conifer forest (200 trees)* — section silhouettes get lost behind mist + trees; FPS risk; portfolio feels claustrophobic

**Implications:**
- Uses Bruno's `InstancedGroup` pattern (one InstancedMesh per material × ~13 unique meshes = small draw-call budget)
- `Nature.addExclusion(x, z, r)` already exists in code — needs new exclusion calls for river curve, trail, viewpoints, lighthouse islet
- Hero trees use simple `THREE.Mesh` (not instanced) — only 5 of them, individual transforms needed

---

## 10. Mountain treatment — *Multi-layer cardboard cutout*

**Decision:** Three mountain bands at 110m / 145m / 180m from spawn, each a tilted plane with painted silhouette texture. Parallax depth via layer separation. Heavily fog-faded. Refines/extends existing `src/World/DistantIslands.js`.

| Band | Distance | Role |
|---|---|---|
| Front ridge | ~110m | Tallest visible silhouettes; partial north only |
| Mid peaks | ~145m | Most snow-capped peaks live here |
| Far snow peaks | ~180m | Tallest, most faded; primary snow-cap layer |
| Eastern foothills | ~120m | Lower silhouette differentiating east from north |

**Cost:** ~6 quad planes (12 triangles) negligible. Snow caps as separate alpha-blended layer with `#fff5dc`. All textures sample the palette via UV.

**Alternatives rejected:**
- *Low-poly geometry meshes* — faceted look fights smooth-lit art direction; FPS cost without benefit through 100m+ fog
- *Single matte painting on skybox* — no parallax; "stuck" feel as player moves
- *Hybrid cardboard-near + matte-far* — more complex; the 3-band cardboard alone delivers enough depth

---

## 11. River, waterfall, bridges — *Bezier ribbon + flat plane + runtime spray*

**Decision:** River and tributary are Bezier curves extruded into flat ribbon meshes in Blender (Bruno's `curveRoad` pattern). Waterfall is a vertical plane with an animated falling-stripe shader. Bridges are simple timber-plank meshes.

| Element | Spec |
|---|---|
| Main river | Bezier curve, width 2–5m (narrow at switchbacks, wide at bends) |
| Tributary | Bezier curve, 1.5m wide, no foam |
| Surface material | Palette color `#9ec5d6` + **animated UV scroll** for flow + edge foam strip in `#fff5dc` |
| Waterfall geometry | Single vertical plane at cliff edge |
| Waterfall shader | Animated falling-stripe texture (GLSL, runtime) |
| Waterfall spray | Runtime particle system, ~20 particles at base |
| Main bridge | Timber planks + stone supports, ~5m span over river north of spawn |
| Tributary crossing | 3 stepping-stones (no bridge mesh) |
| Underwater geometry | None (out of view) |
| Fish | Runtime instanced billboard quads, ~6–8 total, gentle wander animation |

**Implications:** Existing `Water.js` may handle the river surface shader; the waterfall stripe shader is new (custom `ShaderMaterial`). Fish placement system is new (lives in `src/Wildlife/`).

---

## 12. Sun, camera, atmosphere — *Anchored at misty dawn, retuned existing systems*

**Decision:** No new runtime systems. All values are number changes in existing files: `Sun.js`, `TimeOfDay.js`, `Rain.js`, `PlayerCamera.js`, `Fog` setup in `App.js`.

| Setting | Value | Source / change |
|---|---|---|
| Sun elevation (default) | **~12°** (low, dawn-rim) | `Sun.js` — retune |
| Sun color | `#f4d6b0` (warm peach) | retune |
| Sun shadow softness | 3 desktop / 2 mobile | keep |
| Ambient color | `#aab2b5` (cool grey-blue) | retune |
| Camera FOV | **50°** | `PlayerCamera.js` — wider than Bruno's 25°, narrower than typical 70° |
| Camera follow distance | existing `camera-controls` smoothing | keep |
| Fog color | `#e0d4c0` (mist horizon) | replaces `#ffb084` |
| Fog band — near (0–30m) | no fog (clarity at near range) | new distance bands |
| Fog band — mid (30–100m) | light haze | new |
| Fog band — far (100–165m) | dense haze, mountains fade | new |
| Beyond 165m | cardboard mountains visible but heavily faded | new |
| Day cycle duration | **4 minutes** | existing cadence preserved |
| Cycle anchor | dawn (0–40s) → morning (40–100s) → midday (100–160s) → golden (160–200s) → dusk (200–240s) | retune `TimeOfDay.js` keyframes |
| Lantern/brazier emissive | `#ffc46d` | new palette color |
| Rain intensity | lighter showers, heavier mist | retune `Rain.js` |
| Lightning | unchanged | keep `Thunderstorm.js` |

---

## 13. Resume placement — *Stone lectern at spawn*

**Decision:** A small stone lectern with an open parchment scroll, placed 1.5m southwest of the wayfinder at spawn. Always visible to every visitor; interaction wired through existing `Interactables.js` modal pattern. Initial modal content is a placeholder ("Resume coming soon" + LinkedIn link); content swap in the future does not require any geometry/spec change.

**Why spawn (not summit):**
- A resume is a recruiter-facing artifact — must be discoverable without exploration
- Summit lookout placement was the cinematic alternative; rejected because too many visitors would miss it
- Wayfinder obelisk gets a fifth carved emblem (scroll pictogram on the top face) pointing to the lectern

**Implications for build:**
- New static prop: lectern pedestal + tilted slab + parchment scroll + small stone weight
- New ref empty: `refResumeInteractivePoint`
- New runtime stub: `src/Portfolio/ResumeData.js` with placeholder modal content; consumed by the existing `Interaction.js` system
- Modal content key (`resume`) wired now; later content updates are pure data edits

---

## Decision summary — all 13 settled, brainstorm complete

Total decisions: 13. Total brainstorm rounds: ~10 (some combined). Formal spec written separately at `docs/superpowers/specs/2026-05-26-world-design.md`.

This document is the **reasoning history**; the formal spec is the **implementation contract**.

*Updates: append a new sub-section as each decision lands. Reasoning is the load-bearing part — preserve it.*
