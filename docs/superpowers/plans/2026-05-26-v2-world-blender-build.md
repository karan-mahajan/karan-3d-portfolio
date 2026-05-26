# v2 alpine misty highlands — Blender Python build plan

> **Workflow:** Author delivers ONE phase script per round. User runs it in Blender, verifies the viewport against the phase's checkpoint, then approves the next phase. Each script is self-contained, idempotent (re-running rebuilds its own collection from scratch), and saves `world.blend` at the end.

**Goal:** Author `static/world/world.glb` from a single source-of-truth `tools/blender/world.blend` that matches the spec at [`docs/superpowers/specs/2026-05-26-world-design.md`](../specs/2026-05-26-world-design.md). This plan covers the Blender phases only; runtime wiring (`Terrain.js`, `Nature.js`, `Paths.js`, `DistantIslands.js` rewrite + material library + sun/fog retuning + `.verify` scripts) is a separate follow-up plan after `world.glb` is approved.

**Architecture:**
- One `world.blend` master file under `tools/blender/`.
- One Python script per phase under `tools/blender/scripts/phase-NN-name.py` — each clears its own collection (idempotent), builds geometry, places ref empties, names colliders with the prefix dispatch from spec §11.2, then `bpy.ops.wm.save_mainfile()`.
- A shared helper module `tools/blender/scripts/_lib.py` (delivered in Phase 0) provides palette lookup, collection clear/create, ref-empty placement, and collider naming so phase scripts stay focused on geometry.
- Final phase (13) exports `world.glb` with the name-prefix dispatch contract from spec §11.

**Tech Stack:** Blender 4.2 LTS, `bpy` Python API, target export = glTF 2.0 binary with custom properties + collections preserved.

---

## File structure

```
tools/blender/
├── world.blend                          # master file (created Phase 0)
├── scripts/
│   ├── _lib.py                          # shared helpers (palette, collection, refs, colliders)
│   ├── _palette.py                      # 25 locked hex codes (single source of truth)
│   ├── phase-00-setup.py                # collections + scene units + initial save
│   ├── phase-01-palette-texture.py      # generate static/textures/palette.png
│   ├── phase-02-terrain.py
│   ├── phase-03-spawn.py
│   ├── phase-04-projects-workshop.py
│   ├── phase-05-skills-observatory.py
│   ├── phase-06-experience-cairns.py
│   ├── phase-07-contact-beacon.py
│   ├── phase-08-lighthouse.py
│   ├── phase-09-river-bridges.py
│   ├── phase-10-trail-viewpoints.py
│   ├── phase-11-foliage.py
│   ├── phase-12-mountain-bands.py       # consumes user-painted PNGs
│   └── phase-13-export-glb.py
└── reference/                           # screenshots from approved phases (gitignored)
```

**Run pattern (both modes supported by every script):**
- Interactive: open `world.blend` in Blender 4.2 → Scripting workspace → Text Editor → Open Script → Run.
- Headless: `blender --background tools/blender/world.blend --python tools/blender/scripts/phase-NN-name.py`.

---

## Phase sequence + rationale

The order optimises for **early viewport feedback** and **independent verification**:

| # | Phase | Why this order | Depends on |
|---|---|---|---|
| 0 | Setup (collections, units, save) | Empty skeleton must exist before anything else | — |
| 1 | Palette texture PNG | Geometry phases that author UVs need the PNG to eyedrop-verify | 0 |
| 2 | Terrain | Every focal structure's Y is sampled from terrain height; place props after the terrain exists | 0 |
| 3 | Spawn (hearth + wayfinder + lectern) | The visual anchor at origin; verifies palette + terrain look right in one screenshot | 1, 2 |
| 4 | Projects workshop (E) | First cardinal section. Tests the section build pattern that 5-7 reuse | 2 |
| 5 | Skills observatory (S) | Reuses section pattern | 2 |
| 6 | Experience cairn trail (N) | Reuses section pattern + introduces ridge geometry | 2 |
| 7 | Contact beacon (W) | Reuses section pattern + sits on cliff edge — surfaces any terrain edge bugs | 2 |
| 8 | Lighthouse + islet | Offshore, no terrain dependency | 0 |
| 9 | River + tributary + waterfall + bridges | Needs terrain shape locked + Contact's western cliff to spill over | 2, 7 |
| 10 | Hiking trail + viewpoint markers | Routes around the 4 sections — needs their positions final | 4, 5, 6, 7 |
| 11 | Foliage | Exclusion zones consume positions of focal structures + river + trail | 3–10 |
| 12 | Mountain cardboard bands | Needs user-painted PNG assets (rule 1 gate) | 0 |
| 13 | Export `world.glb` + boot-time assertions | All geometry + refs must exist; this phase validates them | all prior |

Phases 4–7 share a section pattern. If Phase 4 surfaces a problem with the pattern, fix it in Phase 4's script before delivering Phase 5 — don't fix the same bug four times.

---

## Conventions every phase script follows

These rules are documented here once. Phase scripts encode them via `_lib.py`.

1. **Idempotency.** First action is `_lib.clear_collection("<name>")` — removes everything in the collection then re-creates it. User can re-run a phase script any number of times without dupes.
2. **Collection-scoped.** Each phase writes only into its own collection per spec §11.5. No phase writes into another phase's collection. Phase 13's collider naming and Phase 0's setup are the only exceptions.
3. **Heightfield sampling.** Props that sit on terrain call `_lib.height_at(x, z)` (Phase 2 writes this helper). At y=0.02 (inner plateau flat floor); past r=22 it samples the actual terrain mesh via raycast. **This mirrors the runtime `terrain.heightAt(x, z)` contract — rule 4 of CLAUDE.md.**
4. **Collider naming.** Every collider mesh is `cuboid_<thing>`, `tube_<thing>`, or `trimesh_<thing>` per spec §11.2. Half-extents come from scale, cylinder Y=height first then X/Z=radius (Bruno's `tube*` convention). Collider mesh is a child of the visible mesh's parent empty so it can be removed at runtime without breaking the parent transform.
5. **Ref empties.** Every section gets `refZoneBounding_<section>` (radius via uniform scale) and `refZoneFrustum_<section>` (smaller radius). Other refs per spec §11.3. Empties use display type "PLAIN_AXES" so they're visible in viewport but don't render.
6. **Palette UVs.** Faces get UVs that snap to the 25 palette cells. Authoring uses `_lib.palette_uv("<color_key>")` which returns the UV coordinates for that color's cell in `palette.png`. No prop sets a vertex color outside the palette.
7. **No collider on accents.** Grass, flowers, ferns, ground cover, mountain quads, lighthouse beam = NO collider mesh. Per CLAUDE.md rule 5.
8. **Save at end.** Last line of every script: `bpy.ops.wm.save_mainfile()`.
9. **Print a verification line.** Last print before save:
   `print(f"[phase-NN] OK — created {N_meshes} meshes, {N_refs} refs, {N_colliders} colliders in collection '<name>'")`
   This gives a fast headless smoke-test signal.

---

## Phase 0: Setup (collections + scene units + helper library)

**Files delivered this phase:**
- Create: `tools/blender/world.blend` (empty scene with collection skeleton)
- Create: `tools/blender/scripts/_lib.py`
- Create: `tools/blender/scripts/_palette.py`
- Create: `tools/blender/scripts/phase-00-setup.py`
- Create: `tools/blender/reference/.gitkeep`
- Modify: `.gitignore` — add `tools/blender/reference/`

**What the script does:**
- Sets scene units to meters, length unit = "METERS", scale=1.
- Sets up the **exact collection tree** from spec §11.5 (terrain, spawn, sections/{projects,experience,skills,contact}, lighthouse, water/{river,tributary,waterfall,ocean}, bridges, trail/{perimeter,detour_nw,detour_summit,detour_se}, viewpoints, foliage/{trees,hero_trees,ground_cover,grass}, mountains, refs).
- Deletes the default cube/camera/light.
- Sets viewport clip start=0.1, end=400 (so we can see the 180m mountains).
- Sets viewport background to the **mist horizon color `#e0d4c0`** so we eyeball the misty-dawn look as we build.
- Adds a single SUN light at the spec's `~12°` elevation, color `#f4d6b0`, intensity tuned for viewport preview (NOT a runtime authority — runtime sun lives in `Sun.js`).
- Adds an ambient (world) color `#aab2b5`.
- Saves `world.blend`.

**`_palette.py` contents:** the 25 hex codes from spec §2 as a dict, organised by category, plus the 128×4 cell coordinates for each colour (computed once: each colour occupies a 5×4-px block; 25 colours × 5px wide = 125px used, last 3px padding).

**`_lib.py` exports (initial set; later phases extend):**
- `clear_collection(name)` — delete all objects in collection then re-create.
- `get_collection(path)` — `"sections/projects"` returns the projects sub-collection.
- `palette_uv(color_key)` — `palette_uv("pine_canopy")` returns the (u, v) coords for that colour.
- `place_in(collection, obj)` — link object into a specific collection (and unlink from scene's default).
- `ref_empty(name, location, radius=1.0, userdata=None)` — creates an empty with PLAIN_AXES display, uniform scale = radius, adds to refs collection.
- `name_collider(obj, kind, parent_mesh)` — renames `obj` to `cuboid_<parent>` / `tube_<parent>` / `trimesh_<parent>`, parents it to the visible mesh's empty.

**Verification checkpoint (you look for):**
1. Open `tools/blender/world.blend` in Blender 4.2.
2. Outliner shows the collection tree from spec §11.5 — exactly. (Mismatch = report; do NOT proceed.)
3. Scene units = Metric, Length = Meters.
4. Default cube/camera/light gone; one Sun + Ambient remains.
5. Viewport background is the mist tan colour (`#e0d4c0`).
6. Pressing N → View → Clip End reads 400.
7. The script's last print line shows `[phase-00] OK — collections initialised`.

**Approval gate:** confirm all 7 items match. Then I deliver Phase 1.

---

## Phase 1: Palette texture PNG

**Files delivered this phase:**
- Create: `tools/blender/scripts/phase-01-palette-texture.py`
- Create: `static/textures/palette.png` (output artefact)

**What the script does:**
- Imports `_palette` for the 25 hex codes.
- Builds a 128×4 RGBA `numpy` array. Each colour occupies a 5px-wide × 4px-tall block; last 3px of width are left as the mist-horizon padding colour `#e0d4c0` (matches viewport bg so any UV mistake reads as "transparent fog" not as a wrong colour).
- Writes the array via Blender's `bpy.data.images.new` + `pack_into` then saves out to `static/textures/palette.png`. Pixel format = sRGB, 4 channels, no compression, no mipmap chain.
- Does NOT modify `world.blend` — palette is a runtime asset, not Blender geometry.
- Prints `[phase-01] OK — wrote palette.png (128x4, 25 colours)` and the byte size (expected ~400 B).

**Verification checkpoint:**
1. `static/textures/palette.png` exists. File size < 1 KB.
2. Open in Preview / image viewer: 128×4 px, 25 distinct vertical colour strips, last few px = warm tan (the padding colour).
3. Eyedrop a sample of cell 0 → expect `#c6c3bc` (sky high). Eyedrop a middle cell → expect a colour from spec §2.
4. **Critical:** open the PNG in an editor with sRGB awareness. The sRGB transform must not darken/shift the colours. If colours look wrong, the script's colour-space write is the bug, not the spec.

**Approval gate:** if any colour mismatches its spec hex by more than 1 LSB per channel, I fix the script. Then I deliver Phase 2.

---

## Phase 2: Terrain mesh

**Files delivered this phase:**
- Create: `tools/blender/scripts/phase-02-terrain.py`
- Modifies (via Blender): `tools/blender/world.blend` → adds `terrain` collection contents.

**What the script does:**
- Clears the `terrain` collection.
- Creates a 260×260m plane subdivided to ~193×193 verts (so each quad ≈ 1.35m, per spec §3).
- Applies a height function on every vertex (pure Python, no modifiers — keeps the bake reproducible):
  - **Inner plateau (r ≤ 20m):** y = 0.02 (flat floor matching the runtime's existing inner plateau convention).
  - **Plateau undulation (20 < r ≤ 85m):** y = layered Perlin (3 octaves, amplitude smoothly ramping 0 → 0.8m as r increases). The `_lib.py` helpers add a deterministic `noise2d(x, z, seed=42)` so re-running the script produces the same shape.
  - **Shore slope (85 < r ≤ 95m):** y = smoothstep ramp from plateau height down to -2.0 (ocean floor).
  - **Ocean floor (r > 95m):** y = -2.0 with very low-amplitude undulation so it doesn't read as a perfectly flat sheet.
  - **Western cliff override (x < -78m AND |z| < 60m):** an additional 25m drop applied to verts in this region — this is where the waterfall (Phase 9) will spill. Drop is ramped via smoothstep so it doesn't z-fight the regular shore.
  - **NE ridge (Experience trail rises here):** an additive ridge bump centred on the line from spawn to (+15, +95), peaking at +12m. Phase 6 cairn trail follows this ridge.
- UV-unwraps the terrain with one face → palette cell rule:
  - meadow grass `#94a978` for the inner plateau.
  - dirt path `#6e6256` for the four spawn-radial corridor strips (computed analytically, ~3m wide each).
  - sand `#9a8a72` along the shore (85 < r ≤ 95m band).
  - rock mid `#5d6770` on the NE ridge top.
  - deeper water `#5d8094` on the ocean floor.
- Adds a `trimesh_terrain` collider mesh = a triangulated **copy** of the visible mesh, linked into the terrain collection. Runtime treats it as a Rapier heightfield.
- Places ref empties:
  - `refSpawnPoint` at (0, 0.02, 0).
  - `refRespawn_origin` at (0, 0.02, 0) — used by the existing respawn-when-y<-5 logic.
  - 4 ref empties for the radial path direction: `refPath_N`, `refPath_E`, `refPath_S`, `refPath_W` at the path start positions (used by Phase 3 spawn paths to align).
- Adds `_lib.height_at(x, z)` — a runtime-of-Blender helper that raycasts from y=+50 down onto the terrain mesh and returns the hit Y. Phase 3+ scripts use this.

**Verification checkpoint:**
1. Outliner → terrain collection contains `terrain_mesh` + `trimesh_terrain`.
2. In Top View (`Numpad 7`) with wireframe (`Z`→Wireframe), the mesh looks like:
   - A roughly circular plateau out to ~90m.
   - A visible NE ridge ramping up.
   - Western edge has a cliff drop (visible in Front View `Numpad 1` as a hard step).
   - Four faint cardinal corridors at +X / -X / +Z / -Z (the dirt paths) visible if you switch to Material Preview shading (Z→3).
3. With shading set to **Material Preview**, colours match: meadow green centre, dirt corridors radial, sand ring at shore, water deeper outside. (Materials will only render correctly once we apply the palette image in a later refinement — for Phase 2, vertex-colour preview is sufficient.)
4. Edit Mode → select inner-plateau verts (r<20) → press N → Item → Median Z reads ~0.02.
5. Edit Mode → select a vert at (0, 0, +95) → median Z reads ~-2.
6. Edit Mode → select a vert at (+15, 0, +95) → median Z reads ~+12 (the ridge peak).
7. `[phase-02] OK — terrain 260x260m, 193x193 verts, 4 cardinal paths, NE ridge, W cliff` printed.

**Approval gate:** confirm terrain silhouette + dimensions + cliff drop visually. Then Phase 3.

---

## Phase 3: Spawn (hearth + wayfinder + lectern)

**Files delivered this phase:**
- Create: `tools/blender/scripts/phase-03-spawn.py`

**What the script does (per spec §4.1):**
- Clears the `spawn` collection.
- **Wayfinder obelisk:** square footprint 0.5×0.5m, height 2.2m. Built from a beveled cube; top face carved with a shallow inset (the "scroll pictogram cap"). Body palette = `#5d6770`, engraved edges palette = `#9a8a72`. Four side faces have a 0.1m inset rectangle (the "carved" face area). At (0, `height_at(0,0)`, 0).
- **Hearth ring:** 8 fitted stones arranged in a 3m diameter circle. Each stone = beveled cube ~0.35m, slight randomisation per stone (different scales + rotations, seeded so re-runs are deterministic). Central ember pit = small recessed disk with palette `#ffc46d` material flagged emissive (runtime swaps to an emissive variant).
- **Resume lectern:**
  - Pedestal: 0.4×0.4×0.9m cuboid, palette `#5d6770` body + `#9a8a72` edge band (band = a 0.05m inset face strip at the top).
  - Slab: 0.6×0.4×0.05m cuboid tilted 20° toward spawn (i.e., toward +X+Z relative to lectern position, since lectern is SW of obelisk).
  - Scroll: low-poly cylindrical roll (~0.5×0.3m), palette `#fff5dc` body with `#d5c4ad` end caps. Two short cylinders at each end = the rolled-up portions.
  - Stone weight: small beveled cube ~0.08m, palette `#5d6770`, on one corner of the parchment.
  - Position: 1.5m SW of wayfinder = (-1.06, height_at(-1.06,-1.06), -1.06).
- **Four worn-path stubs:** short ribbon meshes (2m long, 1m wide) at the start of each cardinal corridor, palette `#6e6256` (dirt). These are just the spawn-cluster stubs — the full radial dirt is on the terrain UV (Phase 2) and the perimeter trail is Phase 10.
- **Colliders:**
  - `cuboid_wayfinder` — half-extents (0.25, 1.1, 0.25), centred at wayfinder centre.
  - `cuboid_lectern_pedestal` — half-extents matching the 0.4×0.9×0.4 pedestal, NO collider for slab/scroll/weight (player can lean over).
  - `tube_hearth_ring` — radius 1.55m, height 0.4m (low ring), centred at spawn. Player walks AROUND the hearth.
- **Refs:**
  - `refZoneBounding_spawn` at (0, height_at(0,0), 0), scale=12 (12m bounding radius).
  - `refZoneFrustum_spawn` at same position, scale=9.
  - `refInteractivePoint_wayfinder` at the top of the wayfinder (0, height+2.2, 0).
  - `refResumeInteractivePoint` at the centre of the lectern slab top.
  - `refHearth` at the ember pit centre — runtime attaches the ember emissive point light here.

**Verification checkpoint:**
1. Top View: spawn cluster sits at origin. Wayfinder slightly forward of centre (just visual); lectern offset SW.
2. Front View (`Numpad 1`): wayfinder is 2.2m tall — measure with grid spacing (each grid line = 1m by default).
3. Hearth ring is 3m across (measure between opposite stones).
4. Lectern is at human-readable height — pedestal top ~0.9m above terrain, slab tilts toward where the player would stand.
5. Material Preview: colours match spec — grey stone, warm copper lantern colour at hearth, cream parchment, brown wood.
6. Outliner shows `cuboid_wayfinder`, `cuboid_lectern_pedestal`, `tube_hearth_ring` inside spawn collection.
7. Outliner shows 5 ref empties inside refs collection: `refZoneBounding_spawn`, `refZoneFrustum_spawn`, `refInteractivePoint_wayfinder`, `refResumeInteractivePoint`, `refHearth`.
8. `[phase-03] OK — spawn: 4 mesh groups, 3 colliders, 5 refs` printed.

**Approval gate:** if the spawn cluster reads as "traveller's refuge" silhouette, approve → Phase 4.

---

## Phase 4: Projects workshop pavilion (E)

**Files delivered this phase:**
- Create: `tools/blender/scripts/phase-04-projects-workshop.py`

**What the script does (per spec §4.3):**
- Clears `sections/projects` collection.
- Computes section root position: `(+70, height_at(+70, 0), 0)`.
- **Pavilion structure (6×5m footprint, 4m apex):**
  - Three half-height stone walls (back + 2 sides), 1.6m tall, 0.3m thick. Palette `#5d6770`.
  - Timber slats on top of each stone wall, 0.4m tall × 0.1m thick, palette `#b87850`.
  - Peaked timber roof: two sloped quads meeting at a 4m apex line that runs north-south (so the open face is east, away from spawn — the player approaches the open side).
  - Front face is open (no wall mesh).
- **Anvil:** at pavilion centre, palette `#5d6770` body with `#9a8a72` worn striking surface (top face = different UV cell). 0.6m long × 0.3m wide × 0.5m tall.
- **Forge:** back-left corner stone hearth, 1.2×1.0×0.9m, with a recessed coal pit on top (palette `#ffc46d` emissive, runtime swaps to emissive variant). Chimney rises 2.5m above the roof apex.
- **Tool wall:** 5 simple tool meshes (hammer, tongs, file, tongs2, hammer2) hanging on the back wall — each a small ~0.4m group of cuboids + cylinders, palette `#5d6770` heads + `#b87850` handles. Authored as instances of 2 base shapes so they instance later.
- **Project Showcase wall area:** a clean 4m-wide × 2.5m-tall flat panel on the back wall interior, palette `#b87850` (timber backing). Marked with a ref empty so runtime mounts the existing `Billboards.js` showcase here.
- **Colliders:**
  - `cuboid_workshop_wall_back`, `cuboid_workshop_wall_left`, `cuboid_workshop_wall_right` — sized to each wall.
  - `cuboid_anvil_base` — half-extents (0.3, 0.25, 0.15).
  - `tube_forge` — radius 0.7m, height 0.9m.
  - No collider on tools (visual only — player can't reach them above head height).
  - No collider on roof (player can't reach it).
- **Refs:**
  - `refZoneBounding_projects` at section root, scale=13.
  - `refZoneFrustum_projects` at section root, scale=10.
  - `refInteractivePoint_projects` at the centre of the Showcase wall area, 1.5m above ground.
  - `refShowcaseMount` at the same position as `refInteractivePoint_projects` but with userData `{ width: 4.0, height: 2.5 }` — runtime uses this to size the billboard.
  - `refForge` at forge coal pit centre — runtime attaches emissive point light + smoke particle here.
  - `refRespawn_projects` at section root.

**Verification checkpoint:**
1. Top View: workshop appears at +70m east of spawn (gridline +70). Pavilion roughly 6m × 5m footprint with the open face pointing east-back-of-pavilion-is-west (so the player walking east from spawn approaches the open front).
2. Front View facing -X: stone half-walls, timber slats, peaked roof at 4m apex.
3. Anvil sits in the middle; forge is back-left; chimney rises above the roof.
4. Material Preview: stone grey + warm timber + orange ember.
5. Outliner: 9 mesh groups in projects collection + 5 colliders + 6 refs in refs collection.
6. `[phase-04] OK — projects: workshop pavilion, 5 colliders, 6 refs` printed.

**Approval gate:** if pavilion reads as "Karan's workshop" and the showcase mount area is clearly the back wall, approve → Phase 5.

---

## Phase 5: Skills observatory tower (S)

**Files delivered this phase:**
- Create: `tools/blender/scripts/phase-05-skills-observatory.py`

**What the script does (per spec §4.4):**
- Clears `sections/skills` collection.
- Computes section root: `(0, height_at(0, -70), -70)`.
- **Stone shaft:** cylinder, 3m diameter (radius 1.5m), 4m tall. 32 segments. Palette `#5d6770` body with `#9a8a72` mortar bands at 1m intervals (separate face loops with different UVs).
- **Copper dome:** half-sphere atop the shaft, radius 1.5m. Palette `#b87850` weathered copper with `#9a8a72` edges (a thin ring of palette `#9a8a72` faces at the dome base).
- **Cupola lantern:** small cube + roof apex on top of dome, palette `#ffc46d` emissive cap + `#b87850` body. Marked with a ref for runtime light attach.
- **Telescope:** brass-and-wood cylinder mounted on the dome, angled ~45° toward the sky. Brass = palette `#b87850`, wood tripod base = `#b87850` darker (using the same colour cell but UV-shifted into a darker portion — acceptable since the palette has a dirt/wood family).
- **Base ring of artifacts (4 items):**
  - Reading lectern (smaller version of the resume lectern, no scroll — empty slab).
  - Stack of scrolls (3 stacked cylinders).
  - Stack of books (3 stacked cuboids of varying size).
  - Open chest with instruments (chest = cuboid with open lid, instruments = 2 small cuboids + 1 cylinder inside).
  - Each artifact is at a 30°–90° offset around the tower base, ~2.2m from tower centre.
- **Door:** wooden door on the south face of the shaft (-Z side), 0.9m wide × 1.9m tall, palette `#b87850`. Decorative only.
- **Colliders:**
  - `tube_observatory` — radius 1.5m, height 4m, centred at section root.
  - `cuboid_artifact_lectern`, `cuboid_artifact_scrolls`, `cuboid_artifact_books`, `cuboid_artifact_chest` — sized to each visible mesh's bbox.
  - No collider on dome/telescope/lantern (player can't reach above 4m).
- **Refs:**
  - `refZoneBounding_skills` at section root, scale=13.
  - `refZoneFrustum_skills` at section root, scale=10.
  - `refInteractivePoint_skills` at the tower south door, 1.5m above ground.
  - `refRespawn_skills` at section root.

**Verification checkpoint:**
1. Top View: observatory at -70m south of spawn. Round footprint visible.
2. Front View: 3m diameter shaft, 4m tall, dome on top.
3. Side View: telescope angled skyward, copper dome shaded warm against grey shaft.
4. Material Preview: stone grey shaft, weathered copper dome, warm cupola lantern, brown door.
5. 4 artifacts ringing the tower base in Top View.
6. Outliner: shaft + dome + lantern + telescope + door + 4 artifacts (9 mesh groups) + 5 colliders + 4 refs.
7. `[phase-05] OK — skills: observatory, 5 colliders, 4 refs` printed.

**Approval gate:** if the tower reads as "observatory" (silhouette of dome + telescope is the key tell), approve → Phase 6.

---

## Phase 6: Experience cairn trail (N)

**Files delivered this phase:**
- Create: `tools/blender/scripts/phase-06-experience-cairns.py`

**What the script does (per spec §4.2):**
- Clears `sections/experience` collection.
- Section root: `(0, height_at(0, +70), +70)`. The N ridge from Phase 2 lifts the terrain here; trail terminus is at `(+15, height_at(+15, +95), +95)` ≈ +12m elevation.
- **Trail bezier curve:** ~7 control points from `(0, 0, +4)` (just N of spawn, at the timber bridge — bridge itself is Phase 9) up to `(+15, +12, +95)` (summit lookout — viewpoint mesh is Phase 10). Curve hugs the ridge.
- **Trail ribbon mesh:** extrude the bezier into a flat ribbon, 1.2m wide, palette `#6e6256` (dirt) with `#9a8a72` (sand) variation along the edges.
- **Stepping stones:** at the steepest section of the trail (between t=0.4 and t=0.6 along the curve), add 5 flat stones embedded into the trail surface, palette `#5d6770`.
- **Cairns (7 total):** spaced roughly evenly along the trail. Each cairn = a stack of 3–5 carved stones, total height 0.8–1.8m varying per cairn. Footprint 0.4×0.4m. Body `#5d6770`, carved face inset `#9a8a72`.
- **Cairn lanterns:** each cairn has a small lit lantern on top — copper body `#b87850`, warm emissive cap `#ffc46d`. Each lantern gets its own ref empty (`refCairnLantern_1` through `refCairnLantern_7`) so runtime attaches point lights.
- **Colliders:**
  - `cuboid_cairn_1` through `cuboid_cairn_7` — sized to each cairn's bbox.
  - No collider on trail surface, stepping stones (player walks on terrain heightfield — runtime treats trail as visual only).
  - No collider on lanterns (above head height when player stands at trail).
- **Refs:**
  - `refZoneBounding_experience` at section root (i.e., midway up the trail, at +70 not the summit), scale=14 (slightly bigger; the trail is long).
  - `refZoneFrustum_experience` at section root, scale=11.
  - `refInteractivePoint_experience` at the first cairn (closest to spawn).
  - `refCairnLantern_1..7` at each lantern centre.
  - `refRespawn_experience` at section root.

**Verification checkpoint:**
1. Top View: a winding trail from just N of spawn rising NE-ish to a ridge ~+95m. 7 cairns dotting the trail.
2. Front View (looking south): trail rises visibly up the NE ridge. Cairns get smaller toward the top in perspective.
3. Material Preview: dirt trail, grey cairns, warm lantern caps.
4. Outliner: 1 trail mesh + 7 cairns + 7 lanterns (mesh groups) + 7 cuboid colliders + ~12 refs.
5. `[phase-06] OK — experience: cairn trail, 7 cairns, 7 colliders, 12 refs` printed.

**Approval gate:** if the trail reads as "rising journey of milestones", approve → Phase 7.

---

## Phase 7: Contact cliff beacon (W)

**Files delivered this phase:**
- Create: `tools/blender/scripts/phase-07-contact-beacon.py`

**What the script does (per spec §4.5):**
- Clears `sections/contact` collection.
- Section root: `(-70, height_at(-70, 0), 0)`. This sits AT the cliff edge — Phase 2's western cliff drops at `x < -78` so the beacon platform is on the last bit of solid ground before the drop.
- **Stone platform:** 3×3m cuboid, 0.3m thick (so the player stands on a slightly elevated stone deck). Palette `#5d6770` body with `#9a8a72` edge band.
- **Iron brazier:**
  - Tripod base: 3 angled cylinders forming an inverted tripod, palette `#4a525c` (dark iron).
  - Bowl: wide shallow cylinder atop the tripod, 1m diameter × 0.4m tall, palette `#5d6770`.
  - Flame mesh: low-poly flame shape inside the bowl, palette `#ffc46d` emissive (runtime applies vertex animation; mesh is the shape, runtime drives the flicker).
  - Total height ~1.8m from platform top.
- **Smoke trail anchor:** runtime particle attaches here; placed at `refBrazier`.
- **Inscription plinth:** small stone marker beside the brazier (0.8m tall × 0.3×0.3m), palette `#5d6770` with engraved face `#9a8a72`. Ref empty marks its interactive point.
- **Colliders:**
  - `cuboid_contact_platform` — half-extents (1.5, 0.15, 1.5), centred 0.15m above terrain.
  - `tube_brazier` — radius 0.5m, height 1.0m (tripod + bowl block, not the flame — flame doesn't block).
  - `cuboid_inscription_plinth` — small box collider.
- **Refs:**
  - `refZoneBounding_contact` at section root, scale=12.
  - `refZoneFrustum_contact` at section root, scale=9.
  - `refInteractivePoint_contact` at the inscription plinth.
  - `refBrazier` at the bowl centre — runtime attaches emissive point light + smoke particle system.
  - `refRespawn_contact` at section root.

**Verification checkpoint:**
1. Top View: platform sits at -70m west of spawn, brazier centred on it.
2. Front View (looking north): the **cliff drop is visible just past the platform** — the platform sits literally on the edge.
3. Material Preview: stone platform, dark iron tripod, warm flame.
4. The brazier glow should read as the most-saturated warm point in the world so far (spec §4.5 explicitly calls this out).
5. Outliner: platform + brazier (4 parts: tripod, bowl, flame, smoke ref) + plinth = 7 mesh groups + 3 colliders + 5 refs.
6. `[phase-07] OK — contact: beacon platform, 3 colliders, 5 refs` printed.

**Approval gate:** confirm cliff edge proximity is correct (not floating, not buried). Then Phase 8.

---

## Phase 8: Lighthouse + islet

**Files delivered this phase:**
- Create: `tools/blender/scripts/phase-08-lighthouse.py`

**What the script does (per spec §4.6):**
- Clears `lighthouse` collection.
- Position: `(-130, -1, +35)`. (Y=-1 is sea level minus 1, the islet rises +3m above.) No terrain sampling here — islet is offshore.
- **Rocky islet:** disc-like rock mesh, 8m diameter, rises 3m above sea level. Mildly irregular shape (Phase 0's seeded noise, low frequency). Palette `#5d6770` rock body with `#9a8a72` sand fringe at base.
- **Lighthouse cylinder:** 8m tall, tapering from 1.0m radius at base to 0.8m at top. Body palette `#9ea7ab` (fog-faded distant — sells the "far away" read even up close) with 3 horizontal `#fff5dc` (snow/white) bands at y=2, y=4, y=6.
- **Glass cupola:** at top, 0.9m radius × 1.0m tall shape (slight onion-dome look). Palette `#9ec5d6` (glacial river — close enough to glassy blue) with transparency hint via material name (`*glass*`).
- **Lamp:** small sphere inside cupola, palette `#ffc46d` emissive. `refLighthouseLamp` for runtime light attach.
- **Beam pivot:** an empty named `refLighthouseBeamPivot` placed at the lamp centre. Runtime rotates this empty's child Object3D — for Blender authoring, we just place a sample beam cone (palette `#ffc46d`, 20m long, low-opacity material name `*beam*`) parented to the pivot so we can see the geometry. Runtime can swap the actual beam mesh if needed; the pivot is the anchor.
- **No colliders.** Spec §4.6 calls this out — islet sits past the r=120 soft-clamp, player is pushed back before reaching it.

**Verification checkpoint:**
1. Top View: islet at (-130, +35) — far NW of spawn (well outside the 90m plateau).
2. Front View facing east: lighthouse is 8m tall, white bands clearly visible.
3. The cupola glows warm.
4. A long thin beam mesh extends from the lamp (~20m, you may need to scroll the view).
5. Outliner: islet + lighthouse body + cupola + lamp + beam = 5 mesh groups. 0 colliders. 2 refs (`refLighthouseLamp`, `refLighthouseBeamPivot`).
6. `[phase-08] OK — lighthouse: islet + tower + cupola + beam, 0 colliders, 2 refs` printed.

**Approval gate:** distance from spawn looks right; lighthouse reads as a far landmark. Then Phase 9.

---

## Phase 9: River + tributary + waterfall + bridges

**Files delivered this phase:**
- Create: `tools/blender/scripts/phase-09-river-bridges.py`

**What the script does (per spec §7):**
- Clears `water/river`, `water/tributary`, `water/waterfall`, `water/ocean`, `bridges` collections.
- **Main river bezier:** 12 control points from `(+95, height_at, +95)` (NE source) snaking SW, passing 4m N of spawn (where the bridge crosses), down to `(-78, height_at, +20)` (W cliff exit, just before the drop). Variable handle weights so width varies.
- **River ribbon mesh:** extrude the curve into a flat ribbon. Width varies 2m → 5m via per-control-point width (use Blender's curve bevel + taper objects, or a Python loop that builds the mesh by sampling the curve every 0.5m). Palette `#9ec5d6` (glacial river) with `#fff5dc` edge foam strips along the banks (separate UV island, 0.3m wide).
- **Tributary bezier:** second curve, branches south from the main river near the projects/spawn corridor at `(+15, height_at, +5)`, ends at `(+25, height_at, -25)`. Uniform 1.5m width.
- **Waterfall mesh:** single vertical plane at the W cliff edge `(-78, ramping y from terrain_top down to -2, +20)`, 3m wide × 20m tall. Palette `#9ec5d6` with `#fff5dc` foam at top edge. Material name `*waterfall*` so runtime applies the stripe shader.
- **Ocean plane:** large 200×200m flat plane at y=-1.5, palette `#5d8094` (deeper water). Centred so it covers everything west of the cliff and rings the playable plateau. Material name `*ocean*` so runtime applies the water surface shader.
- **Main bridge (across river, 5m N of spawn):**
  - 8 timber planks, each ~0.6m wide × 2.5m long × 0.1m thick, palette `#b87850`. Laid side-by-side spanning 5m.
  - 2 stone supports (cylinders) at each bridge end, palette `#5d6770`, sized to bridge thickness.
- **Tributary stepping stones (3):** flat stone discs ~0.6m diameter, top surface placed `~0.15m above water surface` (so player feet land on stone, not in water). Spaced 0.7m apart. Palette `#5d6770`.
- **Colliders:**
  - `cuboid_bridge_deck` — single big cuboid covering the bridge plank surface (player walks across this, not on individual plank colliders).
  - `tube_bridge_support_n`, `tube_bridge_support_s` — two cylinders.
  - `tube_stepping_stone_1/2/3` — three tiny cylinders matching the stepping stone discs.
  - **No collider** on river/tributary/waterfall/ocean surfaces (runtime handles wading via the existing radial system + heightfield; water is visual + audio).
- **Refs:**
  - `refWaterfallSpray` at the base of the waterfall — runtime spray particles attach here.
  - `refRiverSource` at the river source (for any future fish/particle spawning).

**Verification checkpoint:**
1. Top View: river meanders from NE corner across the plateau toward the W cliff. One branch (tributary) splits south. Bridge crosses near spawn.
2. Front View: bridge sits at terrain level. Waterfall drops down the cliff (visible drop into the ocean plane).
3. Material Preview: light glacial blue river + foam edges, dark blue ocean, brown timber bridge, grey stone stepping stones.
4. Stepping stones are clearly above the tributary surface (you should NOT see them clipping into water).
5. Outliner: river ribbon + tributary ribbon + waterfall plane + ocean plane + bridge (8 planks + 2 supports) + 3 stepping stones = ~16 mesh groups + 5 colliders + 2 refs.
6. `[phase-09] OK — water: river/tributary/waterfall/ocean, bridges + stones, 5 colliders, 2 refs` printed.

**Approval gate:** river path looks natural, waterfall lands in ocean, bridge is walkable. Then Phase 10.

---

## Phase 10: Hiking trail + viewpoint markers

**Files delivered this phase:**
- Create: `tools/blender/scripts/phase-10-trail-viewpoints.py`

**What the script does (per spec §8):**
- Clears `trail/perimeter`, `trail/detour_nw`, `trail/detour_summit`, `trail/detour_se`, `viewpoints` collections.
- **Perimeter loop bezier:** ~12 control points forming a roughly circular path at ~80m radius from spawn. Routes around (not into) all 4 cardinal section bounding zones. Snaps to terrain height at every sample.
- **Perimeter ribbon mesh:** 1.2m wide, palette `#6e6256` with `#9a8a72` edge fade. Extrude bezier → ribbon as Phase 9.
- **3 detour spurs:**
  - **NW overlook detour:** branches off perimeter at `(-60, +60)` area, ends at the cliff edge between Contact and Experience. Single 0.8m carved waystone marker, palette `#5d6770`.
  - **Summit lookout detour:** branches off the perimeter near Experience and climbs N to `(+15, +12, +95)` — same summit endpoint as the cairn trail terminus. Single waystone marker.
  - **SE viewpoint detour:** branches off the perimeter at `(+60, -60)` area, ends in the SE meadow at `(+45, -85)`. Single waystone marker.
- **Waystones:** 3 carved standing stones, 0.8m tall × 0.4×0.4m footprint, palette `#5d6770` body + `#9a8a72` inset carved face.
- **Colliders:**
  - `cuboid_waystone_nw`, `cuboid_waystone_summit`, `cuboid_waystone_se` — sized to each waystone.
  - **No collider** on trail ribbons (visual only, like the cairn trail in Phase 6).
- **Refs:**
  - `refViewpoint_nw`, `refViewpoint_summit`, `refViewpoint_se` — at each waystone base, with userData `{ viewpoint: "nw" }` etc. so runtime can wire any future "viewpoint discovered" achievement.
  - **No `refZoneBounding_*` for viewpoints** — they're not section-scoped; they're discoverable markers.

**Verification checkpoint:**
1. Top View: a roughly circular trail at ~80m radius, with 3 spurs branching off to specific points.
2. NW spur ends on the cliff edge (between Contact and Experience).
3. Summit spur ends at +95m N (same point as Phase 6 cairn trail summit).
4. SE spur ends in the SE meadow.
5. Each spur endpoint has a single carved stone waystone visible.
6. Material Preview: dirt trail, grey waystones.
7. Outliner: 4 ribbon meshes (perimeter + 3 spurs) + 3 waystones + 3 cuboid colliders + 3 refs.
8. `[phase-10] OK — trail: perimeter + 3 detours, 3 waystones, 3 colliders, 3 refs` printed.

**Approval gate:** trail loops cleanly around all sections, spurs land at the intended viewpoints. Then Phase 11.

---

## Phase 11: Foliage

**Files delivered this phase:**
- Create: `tools/blender/scripts/phase-11-foliage.py`

**What the script does (per spec §5):**
- Clears `foliage/trees`, `foliage/hero_trees`, `foliage/ground_cover` collections (NOT `foliage/grass` — grass remains the existing runtime instanced billboard).
- **Author 13 unique source meshes:**
  - 7 primary pine variants — low-poly cone-stack silhouettes, palette `#3a5536` canopy + `#5a7253` sunlit highlight + `#283933` deep shade base + `#b87850` trunk. Each variant differs in height (4m–7m), proportions, and lean angle.
  - 5 birch variants — slender deciduous, palette `#94a978` foliage + `#fff5dc` trunk bark + `#283933` shadow.
  - 1 hero ancient pine — much larger (10–12m), more detailed silhouette, used for 5 hand-placed instances.
- **Author ground cover source meshes:**
  - 3 fern variants — low-poly fronds, palette `#5a7253`.
  - 4 wildflower clusters (pink/yellow/white) — small billboard quads, palette colours from §2 + `#fff5dc`.
  - 5 mossy boulder variants — beveled rocks, palette `#5d6770` body + `#94a978` moss top.
- **Exclusion zones** (computed analytically in the script):
  - 5 focal structures: 6m buffer each, centred at spawn + 4 section roots.
  - River + tributary corridor: 5m buffer along each curve (sample curve every 1m, exclude within 5m).
  - Hiking trail (full loop + detours): 2m buffer.
  - Lighthouse islet: entire islet (8m radius around (-130, +35)).
  - Three viewpoints: 4m buffer each.
- **Tree placement (~125 instances, plus 5 hero hand-placed):**
  - Stratified sampling on terrain, weighted by NE-quadrant density (heaviest cluster) and SW-quadrant sparsity (lightest, meadow).
  - For each candidate position, reject if inside any exclusion zone.
  - Pick variant via seeded random; rotate around Y, scale uniformly 0.85–1.15.
  - Birches preferentially placed within 8m of river/tributary (resample N times until a birch lands near water if quota not met).
  - Total: ~90 pines + ~35 birches.
- **Hero tree hand-placement (5 positions per spec §5.1):**
  - Near Experience cairn trail base (visible silhouette from spawn).
  - Near Projects workshop east side.
  - Near Skills observatory south side.
  - At NE forest clearing (future deer spot).
  - At summit lookout (frames the view).
  - Each placed as a `THREE.Mesh`-equivalent (individual object, not instance) per spec §5.4. Refs: `refHeroTree_1..5`.
- **Ground cover placement (~150 instances):**
  - Same stratified sampling + exclusion zone reject + variant pick.
  - ~40 ferns (favouring NE forest), ~80 wildflowers (favouring SW meadow), ~30 mossy boulders (everywhere).
- **Colliders:**
  - Hero trees get a `tube_hero_tree_<n>` collider — radius matching trunk, height matching tree.
  - Regular pines + birches **could** get tube colliders, but per spec §5.4 "Trees use existing `Nature.addExclusion(x, z, r)` API" — the runtime treats scattered trees with the existing system, so we do NOT bake colliders for instanced trees in Blender. Hero trees alone get explicit colliders.
  - **No colliders** on ground cover (per CLAUDE.md rule 5: walk-through accents get no collider).
- **Refs:**
  - `refHeroTree_1..5` for the 5 hand-placed hero trees.
  - **No per-instance refs** — runtime treats instances as a single InstancedMesh per variant; their transforms come from the Blender instance positions directly.

**Verification checkpoint:**
1. Top View: forest density higher in NE, sparser in SW. No trees inside the 4 sections, river corridor, trail strips, viewpoint areas, or lighthouse islet.
2. Birches concentrated near the river bends.
3. 5 hero trees clearly larger than the regular pines; placed at the spec'd spots.
4. Material Preview: green canopy, brown trunks, varied ground cover.
5. Run `bpy.context.scene.statistics_text` (or look at the viewport overlay stats) — total triangle count should be roughly within the spec §12 budget (< 100k total world). Tree count: ~125 instances + 5 hero + ~150 ground cover = ~280 objects (per spec §5.4 total).
6. Outliner: `foliage/trees` has 13 source meshes (the variants) + ~125 instance refs. `foliage/hero_trees` has 5 individual meshes. `foliage/ground_cover` has 12 source meshes + ~150 instance refs.
7. `[phase-11] OK — foliage: 125 trees + 5 hero + 150 ground cover, 5 colliders, 5 refs` printed.

**Approval gate:** density, distribution, and exclusion zones all look correct in Top View. Then Phase 12 (which needs your painted PNGs).

---

## Phase 12: Mountain cardboard bands

> **Asset gate:** This phase consumes painted silhouette PNGs you author. Before running the script, drop these 4 PNGs into `static/textures/mountains/`:
> - `mountain-front-ridge.png` — front ridge silhouette, north only, palette colours via UV
> - `mountain-mid-peaks.png` — mid peaks with snow caps
> - `mountain-far-snow.png` — far snow peaks, heavily faded
> - `mountain-foothills-east.png` — eastern foothills, lower silhouette
>
> Each PNG: ~2048×512 px (will be UV-mapped onto wide tilted quads), sRGB, with transparency for the sky. Use only the 25 palette colours from spec §2. Snow caps in `#fff5dc`. If you'd like me to generate placeholder PNGs procedurally so you can see the geometry before painting the final art, ask.

**Files delivered this phase:**
- Create: `tools/blender/scripts/phase-12-mountain-bands.py`
- Consume: `static/textures/mountains/*.png` (user-authored)

**What the script does (per spec §6):**
- Clears `mountains` collection.
- **At script start:** asserts the 4 PNG files exist. If any are missing, prints which ones and exits with a clear message — does NOT make placeholders, per rule 1.
- Creates 4 tilted-quad planes:
  - **Front ridge** at distance ~110m from spawn, tilted ~75° toward camera, width ~180m × height ~50m. Material loads `mountain-front-ridge.png`, palette colours, alpha channel for sky transparency.
  - **Mid peaks** at ~145m, slightly more tilted, width ~220m × height ~60m. Loads `mountain-mid-peaks.png`.
  - **Far snow peaks** at ~180m, most faded, width ~260m × height ~70m. Loads `mountain-far-snow.png`.
  - **Eastern foothills** at ~120m E only (separate quad), width ~160m × height ~30m. Loads `mountain-foothills-east.png`.
- Each plane's material has a `*mountain*` name prefix so runtime applies the heavy-fog override material from spec §10.2.
- **No colliders.** Visual only.
- **No refs.**

**Verification checkpoint:**
1. Top View: 4 quads visible at the correct distances ringing the playable area (front ridge & mid & far on N + foothills on E).
2. Camera view from spawn (set camera at (0, 1.7, 0) looking N): mountain silhouettes layered behind each other, front ridge sharpest, far snow softest.
3. Material Preview: each band shows the painted silhouette + palette colours + sky transparency.
4. **If you see white quads or magenta missing-texture quads:** PNGs aren't being loaded — check the file paths.
5. `[phase-12] OK — 4 mountain bands loaded, sizes: front=180x50 mid=220x60 far=260x70 east=160x30` printed.

**Approval gate:** mountains read as layered depth from spawn camera. Then Phase 13 (export).

---

## Phase 13: Export world.glb + boot-time assertions

**Files delivered this phase:**
- Create: `tools/blender/scripts/phase-13-export-glb.py`
- Output: `static/world/world.glb`

**What the script does:**
- **Pre-export assertions (catches issues anti-pattern #14 in v2-karan-builder-notes would otherwise let through):**
  - Required refs exist: `refZoneBounding_spawn`, `refZoneBounding_projects`, `refZoneBounding_skills`, `refZoneBounding_experience`, `refZoneBounding_contact`, `refRespawn_origin`, `refResumeInteractivePoint`, `refLighthouseBeamPivot`, plus all 5 `refHeroTree_*` and the 7 `refCairnLantern_*`.
  - Required collections non-empty: terrain, spawn, sections/* (all 4), lighthouse, water/* (all 4), bridges, trail/perimeter, foliage/trees, mountains.
  - All collider mesh names match the prefix dispatch: every mesh whose name starts with `cuboid_`, `tube_`, or `trimesh_` is in a collection (no orphans).
  - Section root positions match spec: `refZoneBounding_projects` at (+70, *, 0), `_skills` at (0, *, -70), `_experience` at (0, *, +70), `_contact` at (-70, *, 0). Tolerance ±0.5m.
  - Triangle count under 100k (per spec §12 budget).
- **If any assertion fails, the export is BLOCKED.** Script prints all failures and exits without writing the GLB. You re-run the affected phase script, fix, re-export.
- **Export:**
  - Triangulates all meshes (`bpy.ops.object.mode_set` + `bpy.ops.mesh.quads_convert_to_tris`).
  - Calls `bpy.ops.export_scene.gltf` with:
    - `filepath=static/world/world.glb`
    - `export_format='GLB'` (binary)
    - `export_apply=True` (apply all modifiers)
    - `export_extras=True` (include custom properties from refs)
    - `export_cameras=False` (the in-Blender preview camera is not for runtime)
    - `export_lights=False` (runtime sun + section lights are authored in JS)
    - `export_animations=False` (this world is static)
    - `export_materials='EXPORT'` (export material names but the runtime ShaderMaterial overrides these)
    - `use_visible=True` so anything in hidden collections is excluded.
  - Verifies output file exists and prints size.

**Verification checkpoint:**
1. Run script — should print:
   ```
   [phase-13] assertions OK
   [phase-13] exported static/world/world.glb (XX.X KB)
   ```
2. Check `static/world/world.glb` exists. Size should be in the rough range of 1–5 MB depending on triangle count (Bruno's was ~9 MB but his world had more props).
3. Open the GLB in https://gltf-viewer.donmccurdy.com/ (or `vite` dev server later) — geometry loads, prop placement matches the Blender viewport.
4. **Smoke-test the dispatch contract:** in a Node REPL, parse the GLB and confirm at least one node name starts with `cuboid_`, one with `tube_`, one with `ref`. The exact assertion script can run: `node -e "import('@gltf-transform/core').then(c => c.NodeIO().read('static/world/world.glb').then(d => console.log(d.getRoot().listNodes().slice(0,10).map(n => n.getName()))))"`.

**Approval gate:** GLB exports cleanly, asserts pass, file is on disk and previews correctly. **At this point the Blender authoring is DONE.** Next session: runtime wiring plan (rewriting `Terrain.js`/`Nature.js`/`Paths.js`/`DistantIslands.js`, the SmoothLitPaletteMaterial library, sun/fog retuning, and `.verify` scripts).

---

## Cross-cutting risks to watch

- **Triangle budget.** If Phase 11 pushes total >100k, we cut detail from individual pine variants (fewer cone segments) before reducing instance count — the density is the art direction.
- **Asset rule (CLAUDE.md rule 1) — Phase 12 mountains.** If you'd rather skip painting and source mountain silhouettes from Kenney/elsewhere, we re-plan Phase 12 to load those assets instead. Procedural generation in the script is OFF unless you explicitly approve.
- **Section heights from `height_at`.** Phase 2 must finish first; all subsequent phases sample from the existing terrain mesh. If Phase 2 changes, sections 4–7 may need re-positioning — but section ROOTS are at cardinal +70m where the terrain is the flat plateau, so vertical drift should be small (<10cm) even on terrain edits.
- **Idempotency drift.** Each phase clears its own collection at start. If you ever copy/paste objects between collections in the Blender UI, they may get orphaned by the next run. Treat the scripts as the source of truth — manual edits in Blender between phases are fine for inspection but won't persist across re-runs.
- **Blender 4.x API changes.** If `bpy.ops.export_scene.gltf` arg names differ in your specific 4.x point release, I fix in Phase 13. (Most likely culprit: `use_visible` vs `export_visible`.) We confirm in Phase 0 by running a tiny `bpy.ops.export_scene.gltf?` introspection.

---

## Plan self-review (writing-plans skill output)

**Spec coverage check:**
- §1 World identity → reflected in Phase 0 (viewport bg colour + sun colour) and material naming throughout. ✓
- §2 25-color palette → Phase 1 (PNG) + every geometry phase via `palette_uv()`. ✓
- §3 Spatial layout (dimensions, section positions, world map) → Phase 2 (terrain dimensions) + Phases 3–7 (section positions). ✓
- §4 Focal structures (5 sections + lighthouse) → Phases 3–8. ✓
- §5 Foliage → Phase 11. ✓
- §6 Mountain treatment → Phase 12. ✓
- §7 River/waterfall/bridges → Phase 9. ✓
- §8 Hiking trail + viewpoints → Phase 10. ✓
- §9 Sun/camera/atmosphere → JS runtime tuning, out of Blender scope (next plan). Phase 0 sets viewport sun for preview only. ✓ (deferred)
- §10 Materials → JS runtime, out of Blender scope (next plan). Phase 1 + UV authoring set up the palette PNG that materials consume. ✓ (deferred)
- §11 Blender authoring conventions → Phase 0 sets up collections; every phase encodes name-prefix dispatch + ref empties + InstancedGroup. ✓
- §12 Performance budget → Phase 13 asserts triangle count < 100k. ✓
- §13 Pattern adoption → embedded throughout (no separate task; the patterns are how the world is built). ✓
- §14 Runtime stays same → no task needed; we don't touch runtime. ✓
- §15 Implementation outline → this plan IS the implementation outline. ✓

**Placeholder scan:** every phase has concrete file paths, exact coordinates, dimensions, palette references, collider names, and ref empty names. No "TBD", no "implement appropriate", no "similar to". ✓

**Type/name consistency:** ref empty names match across phases (`refZoneBounding_*`, `refRespawn_*`, `refForge`, `refBrazier`, `refHearth`, `refCairnLantern_*`, `refHeroTree_*`, `refLighthouseBeamPivot`, `refWaterfallSpray`). Collider naming (`cuboid_*`, `tube_*`, `trimesh_*`) matches §11.2 throughout. Phase 13 asserts exactly the names we used. ✓

---

*End of plan. After approval, I deliver Phase 0's script and we begin.*
