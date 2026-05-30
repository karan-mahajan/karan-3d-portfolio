# Skills sphere glow-up + section-04d finalize — design

**Date:** 2026-05-29
**Scope:** Blender only. No JS/Three.js, no GLB export, no runtime ref-name / boot
/ `SECTION_POSITIONS` work — integration is a separate later phase.
**World file:** `tools/blender/world-v3-karan.blend` only. Never touch `world.blend`
(v2) or `world-v3-bruno.blend`.
**Branch:** `bruno-world-analysis`.

## Context

v3 section-04 markers in `tools/blender/scripts/v3/karan/` already build a skills
sphere, contact tower, and projects hut. This phase makes the **skills sphere read
as a luminous orb** as standalone Blender geometry (exported orb ships without
labels; labels come later in Three.js), anchors it to its pond and makes it
reachable, locks its scale, then finalizes the section (contact decision, tree
exclusion, run-all verify).

Bruno's own section markers (`bruno/04-markers-bruno-0{44,61,81,93,103}-*.py`) carry
almost no visible geometry — they are interaction-metadata empties (`refInteractivePoint`,
`refZoneBounding`/`refZoneFrustum` circles, `physicalFixed`) plus the odd textured
plane. **There is no Bruno orb to copy** — the floating skills sphere is wholly a
karan invention. The karan scaffolding (`sectionRef_skills` empty + hidden footprint
collider) already mirrors Bruno's ref-empty convention.

## Locked decisions (brainstorm)

| Decision | Choice |
|---|---|
| Orb visual language | **A — Holographic data-globe**: thin bright emissive rings + faint shell membrane + small intense core/halo |
| Orb scale | **Medium**: 12m diameter / ~13m tall (down from 16.8m / 17.5m) |
| Pond approach | **C — stepping stones → low stone landing ring** around the plinth |
| Contact marker | **Keep the tower** (no change) |
| Hand-placed tree clip handling | **Nudge radially outward, then skip + warn** if unclearable |

## 1. Skills sphere — style & scale

Edit `04-markers-skills-sphere-base.py`.

- `SPHERE_RADIUS`: `8.4 → 6.0` (12m diameter).
- `SPHERE_CENTER_HEIGHT`: `9.10 → 7.0` (orb top ≈ 13m above base; orb bottom
  `center − radius = 1.0m` above the plinth — leaves room for the energy column +
  core pedestal; player looks up at it).
- Proportional ~0.71× shrink of all dependent geometry, **re-derived from
  radius/center, not hand-fudged**:
  - plinth lower/upper/inlay/core-pedestal radii & heights,
  - support posts (radius ring 3.72 and post heights) + caps,
  - energy column length (pedestal-top → core-center) and centre Z,
  - latitude ring heights and radii via `r = sqrt(R² − h²)` at the new R,
  - halo shell radius, core radius.
- The orb stays **water-mounted**: `base = water_bed + FLOAT_CLEARANCE` (1.55)
  unchanged; the float over the pond bed is intentional and correct.

## 2. Nucleus & cage (the "luminous orb" read)

- **Cage rings:** keep equator + 4 meridians; thicken minor-radius to **~0.07–0.09**
  (current 0.08 is fine for meridians/equator — confirm reads as a frame at the
  smaller scale, bump if thin). Keep the 4 latitude rings, radii/heights re-derived
  at R=6.0.
- **Shell membrane:** keep the faint emissive shell sphere (`skill_base_shell_glow`,
  low-alpha BLEND) at the ring radius so the cage reads as a glowing globe surface,
  not bare threads.
- **Nucleus (3 separate centred objects, named for Three.js to pulse/rotate each):**
  - `skillSphere_core_inner` — small bright orb, high emission.
  - `skillSphere_core_halo` — soft larger halo shell, low emission.
  - `skillSphere_energy_column` — thin pedestal-top → core glowing column.
- Materials: the emerald `skill_base_*_glow` family already exists; only sizes and
  emission strengths tuned. No new material concepts required.

## 3. Pond anchoring & approach (pick C)

All new pond props **raycast** their Y from the terrain/pond rim (`_height_at`);
none placed at hardcoded y=0; none land inside the orb footprint or on the orb.

- **Waterline glow ring + submerged disc** at the water surface beneath the orb
  (thin emissive ring + a shallow disc just below it).
- **Edge dressing:** reeds, lily pads, rim rocks around the pond edge. Sampled onto
  the rim; kept off the orb footprint.
- **Approach:** a short line of **stepping stones** from the NE shore (player comes
  from island interior / spawn side) + a low **stone landing ring** encircling the
  plinth so the player can stand and circle the orb (helps reading the future
  orbiting labels). Stone tops sit at terrain-sampled Y rising toward the plinth.
- Colliders / runtime walkability are **Three.js-later**. Blender authors geometry +
  keeps the existing hidden `sectionFootprint_skills` collider.

## 4. Contact marker

`04-markers-section-z-contact-board.py` — **no change.** Tower kept (10.8m mast +
beacon + framed board "Karan Mahajan" / "FULL STACK WEB DEVELOPER" / "CONTACT" /
"MAILBOX – PRESS E" + braces + mailbox). Already runs in run-all via the glob.

## 5. Tree exclusion — cherry + birch

`04-vegetation-cherry-trees.py` and `04-vegetation-birch-trees.py` are **hand-placed**
(explicit `location` spec lists), unlike oak's procedural scatter. Port oak's
avoidance and adapt to hand-placed positions:

- Add `OBSTACLE_MARGIN = 1.6` and `OBSTACLE_KEYS = (... "sectionfootprint",
  "sectionmarker")` (mirror oak; bridge/rock keys optional but harmless to include).
- Add `_obstacle_boxes()` (identical to oak: world-space padded bbox of every MESH
  whose lowercased name contains a key). Hidden footprint meshes are still in
  `bpy.data.objects`, so they are caught.
- In the build loop, for each spec's base `(x, z)`:
  1. If inside any padded box, compute the outward vector from box-center → `(x, z)`
     and nudge in small steps (e.g. 1.0m, up to ~8 steps) re-checking the new point
     stays on land (`_height_at ≥ land-min`, not water/ocean) and outside all boxes.
  2. If a clear on-land point is found, build the tree there (log the nudge).
  3. If not clearable within the step budget, **skip the tree and print a loud
     warning** naming the spec key and the offending marker.
- Birch `(−42, −22)` sits at the skills-pond footprint edge — exercise this path and
  confirm it ends clear (nudge or pass-through).

## 6. Run-all verify

`04-section-run-all.py` already globs `04-markers-*` and runs them sorted, so all four
marker scripts are included; `section-landmarks` (generic totems) sorts before the
dedicated overrides (`section-y-projects`, `section-z-contact`, `skills-sphere`), so
each override's `_cleanup()` correctly removes the generic marker it replaces. No
wiring edit needed.

**Verify:** a from-zero rebuild (`exec(open('.../04-section-run-all.py').read())` in
the Blender Python Console, per the over-Alt+P preference) runs clean end-to-end; the
skills override replaces the generic skills totem; no cherry/birch tree clips any
`sectionFootprint_*`. Auto-saves to `world-v3-karan.blend`.

## Constraints (unchanged)

- Save only to `world-v3-karan.blend`. Never touch `world.blend` / `world-v3-bruno.blend`.
- karan deltas ADD; never remove Bruno datablocks.
- Functional object/material names only — never the user's name in identifiers
  ("Karan Mahajan" as visible text body is fine).
- Props on `terrain.heightAt` (raycast), never y=0. Skills sphere is intentionally
  water-mounted (floats above pond bed).
- Trees/props never on water/ocean/bridge/rock — only grass/slabs/tiles.
- Verify facts against the actual datablock/file before quoting numbers.
- Prefer Python Console `exec(open(...).read())` over Alt+P.
- Don't write outside `tools/blender/scripts/v3/`.

## Out of scope (parked)

- JS/Three.js integration, GLB export, runtime ref-name / boot / `SECTION_POSITIONS`.
- Section-02 deferred water + grass rendering.
- Skill text labels, enter-sphere camera, label billboarding (all Three.js-later).

## Commit policy

Per the sub-project rule, **do not commit this spec or the plan separately** — bundle
spec + plan + implementation into one commit at the end after the user approves the
implementation. No `Co-Authored-By: Claude` trailer.
