# Skills sphere glow-up + section-04d finalize — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the v3 skills sphere read as a luminous floating data-globe at a locked Medium scale, anchor it to its pond with stepping-stone access, and finalize section-04 (tree exclusion for cherry/birch + verified from-zero rebuild) — Blender only.

**Architecture:** Three karan delta scripts are edited in place (`04-markers-skills-sphere-base.py`, `04-vegetation-cherry-trees.py`, `04-vegetation-birch-trees.py`). All are idempotent additive deltas that `_cleanup()` their own prefixes and `save_as_mainfile` to `world-v3-karan.blend`. Iterate fast by running a single delta headless on the existing world file; integration-verify once with the from-zero `04-section-run-all.py`.

**Tech Stack:** Blender 5.1.2 Python API (`bpy`, `bmesh`, `mathutils`), the project's `tools/blender/scripts/_lib.py` helpers. Blender binary: `/Applications/Blender.app/Contents/MacOS/Blender`.

---

## Conventions for this plan

- **Blender binary** (alias used below): `BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"`.
- **Run a delta headless on the existing world** (opens it, runs the script's
  `run()` via `__name__=="__main__"`, saves):
  `"$BLENDER" --background "$BLEND" --python "<script>.py"` where
  `BLEND="/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"`.
  This is safe and idempotent — each delta cleans its own prefixes before rebuild.
- **No per-task commits.** Per the sub-project rule (bundle spec + plan +
  implementation into ONE commit), every task ends at verification. The single
  commit is the final task. No `Co-Authored-By: Claude` trailer.
- **Never** touch `world.blend` or `world-v3-bruno.blend`. Don't write files
  outside `tools/blender/scripts/v3/` (verification renders go to `/tmp`).
- The skills sphere is intentionally **water-mounted** (floats above the pond
  bed); stepping stones intentionally cross water (bridge precedent). These are
  NOT y=0 violations.

## File structure

- **Modify** `tools/blender/scripts/v3/karan/04-markers-skills-sphere-base.py` —
  scale lock, cage/nucleus retune, pond waterline + landing, stepping stones,
  edge dressing. (Tasks 1–5)
- **Modify** `tools/blender/scripts/v3/karan/04-vegetation-cherry-trees.py` —
  marker-footprint avoidance over hand-placed specs. (Task 6)
- **Modify** `tools/blender/scripts/v3/karan/04-vegetation-birch-trees.py` —
  same avoidance. (Task 7)
- **No change** to `04-markers-section-z-contact-board.py` (keep tower) or
  `04-section-run-all.py` (already globs all `04-markers-*`).

---

## Task 1: Scale lock + cage/nucleus retune (the orb)

**Files:**
- Modify: `tools/blender/scripts/v3/karan/04-markers-skills-sphere-base.py`

- [ ] **Step 1: Shrink the three top-level constants**

Edit the constants block (currently lines 39–41):

```python
FLOAT_CLEARANCE = 1.55
SPHERE_RADIUS = 6.0
SPHERE_CENTER_HEIGHT = 7.0
FOOTPRINT = (15.0, 15.0, 13.0)
```

(Was `SPHERE_RADIUS = 8.4`, `SPHERE_CENTER_HEIGHT = 9.10`, `FOOTPRINT = (17.0, 17.0, 13.0)`.) The equator, 4 meridians, and shell already read `SPHERE_RADIUS`, so they auto-scale; only the non-derived literals below need editing.

- [ ] **Step 2: Re-scale the plinth stack** (currently lines 274–277)

```python
    _cylinder("skillSphere_plinth_lower", 3.75, 0.30, (x, z, ground + 0.15), dark_stone, vertices=96, scale=(1.03, 0.97, 1.0))
    _cylinder("skillSphere_plinth_upper", 3.06, 0.24, (x, z, ground + 0.42), edge_stone, vertices=96, scale=(1.01, 0.95, 1.0))
    _cylinder("skillSphere_inlay_disc", 2.44, 0.06, (x, z, ground + 0.58), green, vertices=96, scale=(1.00, 0.92, 1.0))
    _cylinder("skillSphere_core_pedestal", 0.95, 1.10, (x, z, ground + 1.05), warm_wood, vertices=18, scale=(1.0, 1.0, 1.0))
```

Pedestal now spans `ground+0.50 → ground+1.60` (top = 1.60, used by the column next).

- [ ] **Step 3: Re-scale the nucleus + energy column** (currently lines 285–289)

```python
    _sphere("skillSphere_core_inner", 0.58, center, core_glow)
    _sphere("skillSphere_core_halo", 1.45, center, halo_glow, segments=48, ring_count=24)
    # Column spans pedestal top (ground+1.60) to core centre (ground+7.0):
    # length 5.40, centred at ground+4.30.
    _cylinder("skillSphere_energy_column", 0.07, 5.40, (x, z, ground + 4.30), column_glow, vertices=12)
```

- [ ] **Step 4: Thicken the equator ring** (currently line 293)

```python
    _torus("skillSphere_orbit_ring_equator", SPHERE_RADIUS, 0.09, center, (0.0, 0.0, 0.0), ring_glow)
```

(Meridians stay at minor-radius `0.08` — leave lines 294–297 unchanged.)

- [ ] **Step 5: Recompute the latitude rings for R=6.0** (currently lines 301–306)

```python
    lat_mid_r = math.sqrt(SPHERE_RADIUS**2 - 3.0**2)   # ~5.20
    lat_high_r = math.sqrt(SPHERE_RADIUS**2 - 4.5**2)  # ~3.97
    _torus("skillSphere_orbit_lat_north_mid", lat_mid_r, 0.08, (x, z, cz + 3.0), (0.0, 0.0, 0.0), ring_glow)
    _torus("skillSphere_orbit_lat_south_mid", lat_mid_r, 0.08, (x, z, cz - 3.0), (0.0, 0.0, 0.0), ring_glow)
    _torus("skillSphere_orbit_lat_north_high", lat_high_r, 0.06, (x, z, cz + 4.5), (0.0, 0.0, 0.0), ring_glow)
    _torus("skillSphere_orbit_lat_south_high", lat_high_r, 0.06, (x, z, cz - 4.5), (0.0, 0.0, 0.0), ring_glow)
```

- [ ] **Step 6: Re-scale the support posts + caps** (currently lines 312–323)

```python
    # Four slim posts visually cradle the runtime sphere without boxing it in.
    for i, angle in enumerate((45, 135, 225, 315)):
        a = math.radians(angle)
        px = x + math.cos(a) * 2.66
        pz = z + math.sin(a) * 2.66
        post = _cuboid_mesh(f"skillSphere_support_post_{i:02d}", (0.0, 0.0, 1.55), (0.11, 0.11, 1.55), warm_wood)
        post.location = (px, pz, ground + 0.55)
        post.rotation_mode = "XYZ"
        post.rotation_euler = (0.0, 0.0, a + math.radians(45.0))
        _place(post)
        cap = _sphere(f"skillSphere_support_cap_{i:02d}", 0.22, (px, pz, ground + 3.75), ring_glow)
        cap.scale = (1.0, 1.0, 0.72)
```

- [ ] **Step 7: Run the delta headless and verify it builds + orb top ≈ base+13**

Run:
```bash
BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
BLEND="/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"
SCRIPT="/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/04-markers-skills-sphere-base.py"
"$BLENDER" --background "$BLEND" --python "$SCRIPT" 2>&1 | grep -iE "skill|radius|water_bed|base|error|traceback"
```
Expected: a line `built floating skill sphere at (-34.1,-35.7) water_bed=… base=… radius=6.0` and no `Traceback`.

- [ ] **Step 8: Assert orb geometry exists at the new scale**

Run:
```bash
"$BLENDER" --background "$BLEND" --python-expr "import bpy
shell=bpy.data.objects['skillSphere_orb_shell']
bb=[shell.matrix_world @ __import__('mathutils').Vector(c) for c in shell.bound_box]
top=max(v.z for v in bb); bot=min(v.z for v in bb)
print('ORB_DIAMETER', round(top-bot,2)); print('ORB_TOP_Z', round(top,2))
print('POSTS', len([o for o in bpy.data.objects if o.name.startswith('skillSphere_support_post_')]))"
```
Expected: `ORB_DIAMETER 12.0` (±0.1), `POSTS 4`.

---

## Task 2: Pond waterline + stone landing ring

**Files:**
- Modify: `tools/blender/scripts/v3/karan/04-markers-skills-sphere-base.py`

- [ ] **Step 1: Add a water-surface constant** under the existing constants (after the `FOOTPRINT = …` line)

```python
# Future pond fill level. The karan land plateau sits at z=0.0 and ponds are
# carved below it (~-0.6..-1.5); section-02 water renders at this surface later.
WATER_SURFACE_Z = 0.0
```

- [ ] **Step 2: Add four pond/approach materials** to the `MATERIALS` dict (after the `"skill_base_footprint": …` entry)

```python
    "skill_base_water_glow": (0.36, 0.95, 0.78, 0.22),
    "skill_base_path_stone": (0.40, 0.43, 0.40, 1.0),
    "skill_base_reed": (0.16, 0.46, 0.22, 1.0),
    "skill_base_lily": (0.12, 0.40, 0.20, 1.0),
```

(`skill_base_water_glow` contains `glow` → the `_material` helper makes it emissive; alpha 0.22 → BLEND. The other three are solid.)

- [ ] **Step 3: Fetch the new materials in `run()`** (after the `footprint_mat = _material("skill_base_footprint")` line)

```python
    water_glow = _material("skill_base_water_glow")
    path_stone = _material("skill_base_path_stone")
    reed = _material("skill_base_reed")
    lily = _material("skill_base_lily")
```

- [ ] **Step 4: Add the `_waterline_and_landing` helper** (insert after the `_add_footprint(...)` function definition, before `def run():`)

```python
def _waterline_and_landing(x, z, ground, water_glow, path_stone):
    # Glow ring + shallow submerged disc at the future pond fill level.
    _torus("skillSphere_waterline_ring", 4.3, 0.12, (x, z, WATER_SURFACE_Z + 0.03), (0.0, 0.0, 0.0), water_glow)
    _cylinder("skillSphere_submerged_disc", 4.0, 0.06, (x, z, WATER_SURFACE_Z - 0.05), water_glow, vertices=64)
    # Low stone ring around the plinth: somewhere to stand and circle the orb.
    _torus("skillSphere_landing_ring", 4.0, 0.30, (x, z, ground + 0.05), (0.0, 0.0, 0.0), path_stone)
```

- [ ] **Step 5: Call it in `run()`** — insert immediately before `_add_ref(x, z, ground)`

```python
    _waterline_and_landing(x, z, ground, water_glow, path_stone)
    _add_ref(x, z, ground)
```

- [ ] **Step 6: Run the delta + assert the three new objects exist**

Run:
```bash
BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
BLEND="/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"
SCRIPT="/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/04-markers-skills-sphere-base.py"
"$BLENDER" --background "$BLEND" --python "$SCRIPT" 2>&1 | grep -iE "error|traceback" || echo "clean run"
"$BLENDER" --background "$BLEND" --python-expr "import bpy
for n in ('skillSphere_waterline_ring','skillSphere_submerged_disc','skillSphere_landing_ring'):
    print(n, n in bpy.data.objects)"
```
Expected: `clean run`, then each of the three names → `True`.

---

## Task 3: Stepping-stone approach from the NE shore

**Files:**
- Modify: `tools/blender/scripts/v3/karan/04-markers-skills-sphere-base.py`

- [ ] **Step 1: Add the `_stepping_stones` helper** (insert after `_waterline_and_landing`, before `def run():`)

```python
def _stepping_stones(x, z, ground, path_stone):
    # March from the landing edge toward the island interior (NE shore, toward
    # spawn at origin). Stones step DOWN from the floating landing to ~the
    # waterline near shore — intentionally over water (bridge precedent).
    sx, sz = -x, -z
    sd = math.hypot(sx, sz) or 1.0
    ux, uz = sx / sd, sz / sd
    for i in range(4):
        d = 4.6 + i * 2.3
        px = x + ux * d
        pz = z + uz * d
        t = i / 3.0
        top = ground * (1.0 - t) + (WATER_SURFACE_Z + 0.18) * t
        stone = _cylinder(f"skillSphere_step_stone_{i:02d}", 0.85, 0.34, (px, pz, top - 0.17), path_stone, vertices=16)
        stone.scale = (1.12, 0.92, 1.0)
```

- [ ] **Step 2: Call it in `run()`** — extend the block before `_add_ref`

```python
    _waterline_and_landing(x, z, ground, water_glow, path_stone)
    _stepping_stones(x, z, ground, path_stone)
    _add_ref(x, z, ground)
```

- [ ] **Step 3: Run the delta + assert 4 stepping stones exist**

Run:
```bash
BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
BLEND="/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"
SCRIPT="/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/04-markers-skills-sphere-base.py"
"$BLENDER" --background "$BLEND" --python "$SCRIPT" 2>&1 | grep -iE "error|traceback" || echo "clean run"
"$BLENDER" --background "$BLEND" --python-expr "import bpy
print('STONES', len([o for o in bpy.data.objects if o.name.startswith('skillSphere_step_stone_')]))"
```
Expected: `clean run`, `STONES 4`.

---

## Task 4: Aquatic edge dressing (reeds, lily pads, rim rocks)

**Files:**
- Modify: `tools/blender/scripts/v3/karan/04-markers-skills-sphere-base.py`

- [ ] **Step 1: Add the `_edge_dressing` helper** (insert after `_stepping_stones`, before `def run():`)

```python
def _edge_dressing(x, z, reed, lily, path_stone):
    # Aquatic dressing around the rim at the future water surface. Keep the NE
    # approach corridor clear (skip the arc around the shore direction).
    shore_ang = math.atan2(-z, -x)
    for i, deg in enumerate(range(0, 360, 36)):
        a = math.radians(deg)
        da = abs((a - shore_ang + math.pi) % (2 * math.pi) - math.pi)
        if da < math.radians(45.0):
            continue
        rr = 5.8
        px = x + math.cos(a) * rr
        pz = z + math.sin(a) * rr
        kind = i % 3
        if kind == 0:  # reed clump
            for j in range(3):
                _cylinder(
                    f"skillSphere_reed_{i:02d}_{j}", 0.045, 1.1 + 0.2 * j,
                    (px + 0.12 * j, pz - 0.1 * j, WATER_SURFACE_Z + 0.55 + 0.1 * j),
                    reed, vertices=8,
                )
        elif kind == 1:  # lily pad
            pad = _cylinder(f"skillSphere_lily_{i:02d}", 0.55, 0.04, (px, pz, WATER_SURFACE_Z + 0.02), lily, vertices=20)
            pad.scale = (1.0, 0.82, 1.0)
        else:  # half-submerged rim rock
            rock = _sphere(f"skillSphere_rim_rock_{i:02d}", 0.5, (px, pz, WATER_SURFACE_Z - 0.05), path_stone)
            rock.scale = (1.1, 0.9, 0.6)
```

- [ ] **Step 2: Call it in `run()`** — extend the block before `_add_ref`

```python
    _waterline_and_landing(x, z, ground, water_glow, path_stone)
    _stepping_stones(x, z, ground, path_stone)
    _edge_dressing(x, z, reed, lily, path_stone)
    _add_ref(x, z, ground)
```

- [ ] **Step 3: Run the delta + assert dressing exists and the shore corridor is clear**

Run:
```bash
BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
BLEND="/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"
SCRIPT="/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/04-markers-skills-sphere-base.py"
"$BLENDER" --background "$BLEND" --python "$SCRIPT" 2>&1 | grep -iE "error|traceback" || echo "clean run"
"$BLENDER" --background "$BLEND" --python-expr "import bpy, math
ref=bpy.data.objects['sectionRef_skills']; x,y=ref.location.x,ref.location.y
shore=math.atan2(-y,-x); bad=0
for o in bpy.data.objects:
    if o.name.startswith(('skillSphere_reed_','skillSphere_lily_','skillSphere_rim_rock_')):
        a=math.atan2(o.location.y-y, o.location.x-x)
        da=abs((a-shore+math.pi)%(2*math.pi)-math.pi)
        if da<math.radians(45): bad+=1
print('DRESSING', len([o for o in bpy.data.objects if o.name.startswith(('skillSphere_reed_','skillSphere_lily_','skillSphere_rim_rock_'))]))
print('IN_CORRIDOR', bad)"
```
Expected: `DRESSING` > 0, `IN_CORRIDOR 0`.

---

## Task 5: Visual verification render of the whole orb

**Files:** none (verification only; render to `/tmp`).

- [ ] **Step 1: Render the orb headless to a PNG**

Run:
```bash
BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
BLEND="/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"
"$BLENDER" --background "$BLEND" --python-expr "import bpy, mathutils
ref=bpy.data.objects['sectionRef_skills']; c=ref.location.copy()
cam_d=bpy.data.cameras.new('verifyCam'); cam=bpy.data.objects.new('verifyCam',cam_d)
bpy.context.scene.collection.objects.link(cam)
cam.location=(c.x+22.0, c.y-22.0, c.z+9.0)
cam.rotation_euler=(c-cam.location).to_track_quat('-Z','Y').to_euler()
sc=bpy.context.scene; sc.camera=cam
sc.render.engine='BLENDER_EEVEE_NEXT'
sc.render.resolution_x=1024; sc.render.resolution_y=640
sc.render.filepath='/tmp/skill_orb.png'
bpy.ops.render.render(write_still=True)
print('RENDERED /tmp/skill_orb.png')"
```
Expected: `RENDERED /tmp/skill_orb.png`, no `Traceback`.

- [ ] **Step 2: Inspect the render**

Read `/tmp/skill_orb.png`. Confirm: a luminous globe-cage (thin bright rings + faint shell), a bright small core, the plinth + landing ring over the pond, stepping stones leading off toward the island interior, and reed/lily/rock dressing on the far rim. The orb should sit comfortably (not dwarf the scene) at ~12m.

- [ ] **Step 3: Tune literals if needed**

If proportions read wrong (rings too thin, dressing clipping, stones not reaching shore, landing too wide/narrow), adjust the concrete values in Tasks 1–4 (ring minor radii, `rr`, stepping-stone `d`/`top`, landing major radius) and re-run the delta + Step 1 render until it reads as the locked design. Each re-run is safe (the delta cleans its own prefixes).

---

## Task 6: Cherry tree marker-footprint avoidance

**Files:**
- Modify: `tools/blender/scripts/v3/karan/04-vegetation-cherry-trees.py`

- [ ] **Step 1: Add avoidance constants** near the top of the module (after the existing import/constant block, before the `CHERRIES = [` list or just after it — module scope)

```python
OBSTACLE_MARGIN = 1.6   # metres of clearance around markers/bridges/rocks
OBSTACLE_KEYS = ("sectionfootprint", "sectionmarker", "bridge", "basalt", "boulder", "shard", "rock")
LAND_MIN = -0.05        # karan land plateau = 0.0; ponds/river carved below
```

- [ ] **Step 2: Add the obstacle-box + nudge helpers** (insert after `_height_at`, before the tree-build functions)

```python
def _obstacle_boxes():
    boxes = []
    for o in bpy.data.objects:
        if o.type != 'MESH':
            continue
        n = o.name.lower()
        if not any(k in n for k in OBSTACLE_KEYS):
            continue
        cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
        xs = [c.x for c in cs]; ys = [c.y for c in cs]
        boxes.append((min(xs) - OBSTACLE_MARGIN, max(xs) + OBSTACLE_MARGIN,
                      min(ys) - OBSTACLE_MARGIN, max(ys) + OBSTACLE_MARGIN))
    return boxes


def _inside_boxes(px, pz, boxes):
    return [b for b in boxes if b[0] <= px <= b[1] and b[2] <= pz <= b[3]]


def _resolve_specs(specs, boxes, label):
    """Hand-placed avoidance: nudge a spec outward from an offending marker box
    until it is clear AND on land; skip it (loud warning) if unclearable."""
    out = []
    for spec in specs:
        x, z = spec["location"]
        hits = _inside_boxes(x, z, boxes)
        if not hits:
            out.append(spec)
            continue
        bx = (hits[0][0] + hits[0][1]) * 0.5
        bz = (hits[0][2] + hits[0][3]) * 0.5
        dx, dz = x - bx, z - bz
        d = math.hypot(dx, dz) or 1.0
        ux, uz = dx / d, dz / d
        placed = None
        for step in range(1, 9):
            nx, nz = x + ux * step, z + uz * step
            h = _height_at(nx, nz)
            if h is not None and h >= LAND_MIN and not _inside_boxes(nx, nz, boxes):
                placed = (round(nx, 2), round(nz, 2))
                break
        if placed is None:
            print(f"  [SKIP] {label} {spec['key']!r} clips a section marker and cannot be nudged clear")
            continue
        print(f"  [NUDGE] {label} {spec['key']!r} {spec['location']} -> {placed}")
        out.append({**spec, "location": placed})
    return out
```

(`from mathutils import Vector` and `import math` are already present at the top of this file — no import edit needed.)

- [ ] **Step 3: Apply avoidance in `run()`** — change the build line

Current:
```python
    materials = _materials()
    built = [_build_tree(spec, materials) for spec in CHERRIES]
```
New:
```python
    materials = _materials()
    specs = _resolve_specs(CHERRIES, _obstacle_boxes(), "cherry")
    built = [_build_tree(spec, materials) for spec in specs]
```

- [ ] **Step 4: Run the delta + verify no cherry sits in a footprint**

Run:
```bash
BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
BLEND="/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"
SCRIPT="/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/04-vegetation-cherry-trees.py"
"$BLENDER" --background "$BLEND" --python "$SCRIPT" 2>&1 | grep -iE "nudge|skip|built|error|traceback"
```
Expected: a `built N cherry tree structure(s)` line, optional `[NUDGE]`/`[SKIP]` lines, no `Traceback`.

---

## Task 7: Birch tree marker-footprint avoidance

**Files:**
- Modify: `tools/blender/scripts/v3/karan/04-vegetation-birch-trees.py`

- [ ] **Step 1: Add avoidance constants** at module scope (after the existing constants / `BIRCHES` list)

```python
OBSTACLE_MARGIN = 1.6
OBSTACLE_KEYS = ("sectionfootprint", "sectionmarker", "bridge", "basalt", "boulder", "shard", "rock")
LAND_MIN = -0.05
```

- [ ] **Step 2: Add the obstacle-box + nudge helpers** (insert after `_height_at`)

```python
def _obstacle_boxes():
    boxes = []
    for o in bpy.data.objects:
        if o.type != 'MESH':
            continue
        n = o.name.lower()
        if not any(k in n for k in OBSTACLE_KEYS):
            continue
        cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
        xs = [c.x for c in cs]; ys = [c.y for c in cs]
        boxes.append((min(xs) - OBSTACLE_MARGIN, max(xs) + OBSTACLE_MARGIN,
                      min(ys) - OBSTACLE_MARGIN, max(ys) + OBSTACLE_MARGIN))
    return boxes


def _inside_boxes(px, pz, boxes):
    return [b for b in boxes if b[0] <= px <= b[1] and b[2] <= pz <= b[3]]


def _resolve_specs(specs, boxes, label):
    """Hand-placed avoidance: nudge a spec outward from an offending marker box
    until it is clear AND on land; skip it (loud warning) if unclearable."""
    out = []
    for spec in specs:
        x, z = spec["location"]
        hits = _inside_boxes(x, z, boxes)
        if not hits:
            out.append(spec)
            continue
        bx = (hits[0][0] + hits[0][1]) * 0.5
        bz = (hits[0][2] + hits[0][3]) * 0.5
        dx, dz = x - bx, z - bz
        d = math.hypot(dx, dz) or 1.0
        ux, uz = dx / d, dz / d
        placed = None
        for step in range(1, 9):
            nx, nz = x + ux * step, z + uz * step
            h = _height_at(nx, nz)
            if h is not None and h >= LAND_MIN and not _inside_boxes(nx, nz, boxes):
                placed = (round(nx, 2), round(nz, 2))
                break
        if placed is None:
            print(f"  [SKIP] {label} {spec['key']!r} clips a section marker and cannot be nudged clear")
            continue
        print(f"  [NUDGE] {label} {spec['key']!r} {spec['location']} -> {placed}")
        out.append({**spec, "location": placed})
    return out
```

(`from mathutils import Vector` and `import math` are already present at the top of this file — no import edit needed.)

- [ ] **Step 3: Apply avoidance in `run()`** — change the build line

Current:
```python
    materials = _materials()
    built = [_build_birch(spec, materials) for spec in BIRCHES]
```
New:
```python
    materials = _materials()
    specs = _resolve_specs(BIRCHES, _obstacle_boxes(), "birch")
    built = [_build_birch(spec, materials) for spec in specs]
```

- [ ] **Step 4: Run the delta + verify; the `(-42,-22)` birch is the live test**

Run:
```bash
BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
BLEND="/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"
SCRIPT="/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/04-vegetation-birch-trees.py"
"$BLENDER" --background "$BLEND" --python "$SCRIPT" 2>&1 | grep -iE "nudge|skip|built|error|traceback"
```
Expected: a `built N birch tree structure(s)` line, no `Traceback`. If the `(-42,-22)` spec falls inside the padded skills footprint it prints a `[NUDGE]`; either outcome (nudge or pass-through) is acceptable as long as no tree ends inside a box (asserted in Task 8).

---

## Task 8: Full from-zero rebuild + integration verify

**Files:** none (runs the master orchestrator; verification only).

- [ ] **Step 1: Rebuild the whole karan world from zero**

Run (this loads all Bruno meshes — expect a few minutes):
```bash
BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
RUNALL="/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/04-section-run-all.py"
"$BLENDER" --background --factory-startup --python "$RUNALL" 2>&1 | tail -40
```
Expected: section lines for bruno-foundation … karan-vegetation, then `[04-section] saved -> …world-v3-karan.blend` and `[04-section] DONE (N steps total)`. No `Traceback`.

- [ ] **Step 2: Assert the skills override replaced the generic totem**

Run:
```bash
BLEND="/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"
"$BLENDER" --background "$BLEND" --python-expr "import bpy
print('GENERIC_SKILLS_TOTEM', 'sectionMarker_skills' in bpy.data.objects)
print('SKILLS_ORB', 'skillSphere_orb_shell' in bpy.data.objects)
print('SKILLS_REF', 'sectionRef_skills' in bpy.data.objects)"
```
Expected: `GENERIC_SKILLS_TOTEM False`, `SKILLS_ORB True`, `SKILLS_REF True`.

- [ ] **Step 3: Assert no cherry/birch tree base sits inside any marker footprint**

Run:
```bash
"$BLENDER" --background "$BLEND" --python-expr "import bpy
from mathutils import Vector
KEYS=('sectionfootprint','sectionmarker')
boxes=[]
for o in bpy.data.objects:
    if o.type=='MESH' and any(k in o.name.lower() for k in KEYS):
        cs=[o.matrix_world @ Vector(c) for c in o.bound_box]
        xs=[c.x for c in cs]; ys=[c.y for c in cs]
        boxes.append((min(xs),max(xs),min(ys),max(ys)))
bad=[]
for o in bpy.data.objects:
    nm=o.name.lower()
    if nm.startswith('cherry_tree') or nm.startswith('birch'):
        p=o.matrix_world.translation
        for (xmn,xmx,ymn,ymx) in boxes:
            if xmn<=p.x<=xmx and ymn<=p.y<=ymx:
                bad.append(o.name); break
print('TREES_IN_FOOTPRINT', len(bad), bad[:6])"
```
Expected: `TREES_IN_FOOTPRINT 0 []`. (If non-zero, the offending spec needs a larger nudge budget or manual reposition in Task 6/7 — fix and re-run Tasks 6–8.)

- [ ] **Step 4: Final render of the rebuilt world's skills area**

Re-run the Task 5 Step 1 render command against the freshly rebuilt `world-v3-karan.blend` and Read `/tmp/skill_orb.png` to confirm the orb + pond read correctly in the full scene (trees no longer clipping the pond).

---

## Task 9: Single bundled commit

**Files:** the spec, this plan, and the three edited scripts.

- [ ] **Step 1: Confirm only intended files changed**

Run:
```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio && git status --short
```
Expected modified/added: `docs/superpowers/specs/2026-05-29-skills-sphere-glowup-design.md`, `docs/superpowers/plans/2026-05-29-skills-sphere-glowup.md`, `tools/blender/scripts/v3/karan/04-markers-skills-sphere-base.py`, `tools/blender/scripts/v3/karan/04-vegetation-cherry-trees.py`, `tools/blender/scripts/v3/karan/04-vegetation-birch-trees.py`. The `.blend` files are gitignored (regenerable) — do NOT commit them. If `world.blend` shows modified, `git restore` it.

- [ ] **Step 2: Stage and commit (no Claude co-author trailer)**

```bash
cd /Users/mahajankaran/Documents/Projects/karan-portfolio
git add docs/superpowers/specs/2026-05-29-skills-sphere-glowup-design.md \
        docs/superpowers/plans/2026-05-29-skills-sphere-glowup.md \
        tools/blender/scripts/v3/karan/04-markers-skills-sphere-base.py \
        tools/blender/scripts/v3/karan/04-vegetation-cherry-trees.py \
        tools/blender/scripts/v3/karan/04-vegetation-birch-trees.py
git commit -m "v3 04d: skills sphere glow-up (medium data-globe + pond access), cherry/birch marker avoidance"
```
Expected: one commit on `bruno-world-analysis`.

---

## Self-review

- **Spec coverage:** §1 scale → Task 1; §2 nucleus/cage/shell → Task 1 (+ render tune Task 5); §3 pond waterline/edge/approach → Tasks 2–4; §4 contact (no change) → covered by "no change"; §5 cherry/birch exclusion → Tasks 6–7; §6 run-all verify → Task 8. Commit policy → Task 9. ✓
- **Placeholder scan:** all code steps carry concrete code; verification steps carry exact commands + expected output. Task 5 Step 3 is genuine iterative tuning of named literals, not a TODO. ✓
- **Type/name consistency:** object prefix `skillSphere_*` (cleaned by existing `_cleanup`), `_resolve_specs`/`_obstacle_boxes`/`_inside_boxes` identical across cherry & birch, `WATER_SURFACE_Z` defined in Task 2 before use in Tasks 3–4, materials defined in Task 2 before fetch. ✓
```
