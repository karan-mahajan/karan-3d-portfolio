"""
Phase 11: Foliage — trees, hero trees, ground cover.

What this produces (after Run Script + save):
- `foliage/trees` collection:
    * 16 hidden source meshes — `tree_pine_var_1..10_src`,
      `tree_birch_var_1..5_src`, `tree_hero_pine_src`. Each authored once at
      Blender origin; instance objects below SHARE the same mesh datablock so
      Phase 13's exporter can detect shared data and emit InstancedMesh.
    * ~110 `tree_pine_inst_001..` — instance objects pointing at one of the
      10 revamped pine source meshes. Pines now use 3-7 stacked low-poly
      icosphere foliage clumps (instead of cone stacks) — same approach as
      birches, classic pine taper top-to-bottom. Variants 4/5 = tall-narrow
      / short-wide silhouettes; 6 = leaning with side-offset clumps; 7 =
      bushy; 8 autumn warm; 9 deep-shade; 10 meadow-green. Stratified-sample
      placement across the plateau with NE-quadrant 1.5x density / SW-
      quadrant 0.3x. Rotated around Y, scaled 0.6-1.5.
    * ~42 `tree_birch_inst_001..` — instance objects pointing at one of the
      5 revamped birch source meshes (thicker trunks, visible branches,
      stacked foliage clumps). Placed preferentially within 8m of the
      river/tributary vertices.
- `foliage/hero_trees` collection:
    * `hero_tree_1..5` — 5 individual objects sharing the
      `tree_hero_pine_src` mesh. Hand-placed at:
        1. (0, +12)  — Experience cairn trail base, visible from spawn.
        2. (+78, 0)  — Projects workshop east side.
        3. (0, -78)  — Skills observatory south side.
        4. (+45, +45) — NE forest clearing.
        5. (+15, +90) — Summit lookout, framing the view.
      Scale 1.0 (no variance — these are landmarks).
    * `tube_hero_tree_1..5` — hidden cylinder colliders, radius matching the
      hero trunk (~0.6m), height matching the tree (~11m).
- `foliage/ground_cover` collection:
    * 16 hidden source meshes — `gc_fern_var_1..3_src`,
      `gc_flower_var_1..4_src`, `gc_boulder_var_1..5_src`,
      `gc_bush_var_1..4_src`.
    * ~48 `gc_fern_inst_001..` — favouring NE (1.5x), SW 0.5x.
    * ~96 `gc_flower_inst_001..` — favouring SW (1.5x), NE 0.5x.
    * ~40 `gc_boulder_inst_001..` — uniform weight, dramatic small/med/large
      mix (variants 1-5 step from ~0.3m to a ~2.5m hero boulder).
    * ~50 `gc_bush_inst_001..` — Bruno-style stacked clump bushes; uniform.
- `props/benches` collection:
    * `bench_nw`, `bench_summit`, `bench_se` — 3 hand-placed wooden benches
      (seat plank + 2 stone supports, authored as one bmesh each). Each
      bench sits 2.5m back from its viewpoint waystone in the -spur-tangent
      direction (i.e. on the PERIMETER-TRAIL/approach side, NOT the view
      side) so it lands on flat ground instead of the cliff or steep slope
      the waystone faces. The sitter looks past the waystone toward the
      view. Seat top at +0.53m above ground.
    * `cuboid_bench_<key>` — 3 hidden bbox-sized cuboid colliders.
- `props/signs` collection:
    * `sign_1..5` — 5 wooden trail signs (post cylinder + plank cuboid)
      placed at perimeter-trail parameters t=0.1, 0.3, 0.5, 0.7, 0.9,
      offset 1m perpendicular-outward from the path. Each yawed so its
      readable face points along the walking direction. No colliders
      (walk-through accents).
- `props/boulder_clusters` collection:
    * `cluster_<n>_boulder_<k>` — 6 hand-placed clusters (n=1..6), 3-5
      boulders per cluster within a 1.5m radius. Boulders SHARE the
      existing `gc_boulder_var_1..5_src_mesh` datablocks so they extend
      the regular boulder InstancedMesh. seed=12 so they're stable but
      distinct from the seed=11 scattered pass.
- 8 ref empties in `refs`:
    * `refHeroTree_1..5` at each hero tree position, radius 0.5.
    * `refBench_nw`, `refBench_summit`, `refBench_se` at each bench seat
      centre, radius 0.3. Useful for future "sit" interactions.

Coordinate convention: authored in Blender Z-up. Runtime (x, y, z) maps to
Blender (x, z, y). Source meshes built at Blender origin; per-instance
location/rotation/scale parks them onto the terrain. Every instance Y
samples `_lib.height_at(x, z)` so they sit on the heightfield.

Mesh-data-sharing pattern (the InstancedMesh contract):
  source_mesh = bpy.data.meshes.new("tree_pine_var_1_src_mesh")
  ...                            # bmesh.to_mesh(source_mesh)
  inst = bpy.data.objects.new(f"tree_pine_inst_001", source_mesh)
  inst.location = ...

Multiple objects reuse the same `bpy.data.meshes` datablock so .glb export
detects them as instances of one geometry.

Exclusion zones: sections (6m), viewpoints (4m), lighthouse (8m), hero trees
(3m each), plus per-vertex zones along the river (5m, downsampled every 4th
vert) and trail (2m, downsampled). Any candidate inside ANY zone is rejected.

Idempotent: re-running clears `foliage/trees`, `foliage/hero_trees`,
`foliage/ground_cover`, `props/benches`, `props/signs`,
`props/boulder_clusters`. NOT `foliage/grass` — grass remains the runtime
billboard system (CLAUDE.md, plan §5.4).

Seeded RNG (`random.Random(seed=11)`) so re-runs produce identical placements
byte-for-byte.

How to run:
  1. Open tools/blender/world.blend in Blender 4.2+.
  2. Scripting workspace -> Text Editor -> Open -> phase-11-foliage.py.
  3. Run Script (Alt+P).
  4. Script saves world.blend automatically (wm.save_as_mainfile).
"""

import os
import sys
import math
import random

import bpy
import bmesh
from mathutils import Vector


# Mirror Phase 0..10's _script_dir() - Blender's Text Editor sets __file__
# to the buffer name, so collect every plausible disk path and pick the
# first that actually has _lib.py.
def _script_dir():
    candidates = []
    try:
        if __file__ and os.path.isabs(__file__):
            candidates.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass

    space = getattr(bpy.context, "space_data", None)
    text = getattr(space, "text", None) if space else None
    if text and text.filepath:
        candidates.append(
            os.path.dirname(os.path.abspath(bpy.path.abspath(text.filepath)))
        )

    candidates.append(
        os.path.expanduser(
            "~/Documents/Projects/karan-portfolio/tools/blender/scripts"
        )
    )

    for path in candidates:
        if os.path.isfile(os.path.join(path, "_lib.py")):
            return path

    raise RuntimeError(
        "Could not locate _lib.py - tried: " + ", ".join(candidates)
    )


SCRIPT_DIR = _script_dir()
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import _lib       # noqa: E402


# ============================================================================
# Constants
# ============================================================================

TREES_COLLECTION = "foliage/trees"
HERO_TREES_COLLECTION = "foliage/hero_trees"
GROUND_COVER_COLLECTION = "foliage/ground_cover"

# Hand-placed decorative props (Part B of the foliage pass) live in a
# separate top-level `props/` collection so foliage/ stays purely the
# instanced/scattered system. Each sub-collection holds visible mesh objects
# (+ hidden colliders where applicable).
PROPS_BENCHES_COLLECTION = "props/benches"
PROPS_SIGNS_COLLECTION = "props/signs"
PROPS_CLUSTERS_COLLECTION = "props/boulder_clusters"

# Bench dimensions (m).
BENCH_SEAT_LENGTH = 1.2
BENCH_SEAT_DEPTH = 0.35
BENCH_SEAT_THICKNESS = 0.08
BENCH_SUPPORT_HALF_X = 0.15      # 0.30m wide
BENCH_SUPPORT_HALF_Y = 0.15      # 0.30m deep
BENCH_SUPPORT_HEIGHT = 0.45
BENCH_TOP_Y = BENCH_SUPPORT_HEIGHT + BENCH_SEAT_THICKNESS   # 0.53m

# Sign dimensions (m). Beefed up from the toothpick original — post is
# 2.5x thicker, plank is roughly 2x in every axis so it reads as an actual
# wooden sign (not invisible) from a few metres out.
SIGN_POST_RADIUS = 0.10
SIGN_POST_HEIGHT = 1.7
SIGN_PLANK_HALF_X = 0.40         # 0.8m wide
SIGN_PLANK_HALF_Y = 0.05         # 0.10m thick
SIGN_PLANK_HALF_Z = 0.175        # 0.35m tall

# Plateau placement bounds (runtime XZ). Skips the offshore lighthouse area.
PLACEMENT_MIN_X = -90.0
PLACEMENT_MAX_X = +90.0
PLACEMENT_MIN_Z = -90.0
PLACEMENT_MAX_Z = +90.0
CELL_SIZE = 5.0   # 5x5m stratified cells -> 36x36 = 1296 cells

# Target counts (+20% revamp pass).
TARGET_PINE_COUNT = 110
TARGET_BIRCH_COUNT = 42
TARGET_FERN_COUNT = 48
TARGET_FLOWER_COUNT = 96
TARGET_BOULDER_COUNT = 40
TARGET_BUSH_COUNT = 50

# Per-cell attempts in the stratified sampler.
ATTEMPTS_PER_CELL = 3

# Reject anything below this Y (in water).
WATER_REJECT_Y = -0.5

# Per-instance scale variance windows.
TREE_SCALE_MIN = 0.6
TREE_SCALE_MAX = 1.5
GC_SCALE_MIN = 0.7
GC_SCALE_MAX = 1.4

# Hero tree positions (runtime x, z). See module docstring for context.
HERO_TREE_POSITIONS = [
    (0.0,   12.0),
    (78.0,  0.0),
    (0.0,  -78.0),
    (45.0,  45.0),
    (15.0,  90.0),
]

# Exclusion zones — analytical points used before river/trail sampling.
SECTION_ZONES = [
    (0.0,   0.0,   6.0),   # spawn
    (70.0,  0.0,   6.0),   # projects
    (0.0,  -70.0,  6.0),   # skills
    (-70.0, 0.0,   6.0),   # contact
    (0.0,   70.0,  6.0),   # experience
]
VIEWPOINT_ZONES = [
    (-76.0, 45.0,  4.0),   # waystone_nw
    (15.0,  95.0,  4.0),   # waystone_summit
    (45.0, -85.0,  4.0),   # waystone_se
]
LIGHTHOUSE_ZONE = (-130.0, 35.0, 8.0)
HERO_TREE_BUFFER = 3.0

RIVER_BUFFER = 5.0
TRAIL_BUFFER = 2.0
WATER_VERTEX_DOWNSAMPLE = 4   # take every 4th vertex of the strip rings

# Hero pine dimensions (for collider sizing).
HERO_TREE_HEIGHT = 11.0
HERO_TREE_TRUNK_RADIUS = 0.6

# Re-encoded spur detour control points (must match DETOUR_*_CONTROL_POINTS
# in phase-10-trail-viewpoints.py). Used to compute the spur-tangent at each
# waystone endpoint so benches can be placed on the perimeter-trail SIDE of
# each waystone (opposite the view), with the sitter looking past the
# waystone toward the view.
DETOUR_SPUR_CONTROL_POINTS = {
    "nw": [
        (-60.0,  60.0),
        (-65.0,  55.0),
        (-70.0,  50.0),
        (-76.0,  45.0),
    ],
    "summit": [
        ( 30.0,  70.0),
        ( 25.0,  80.0),
        ( 18.0,  88.0),
        ( 15.0,  95.0),
    ],
    "se": [
        ( 60.0, -60.0),
        ( 55.0, -68.0),
        ( 50.0, -77.0),
        ( 45.0, -85.0),
    ],
}

# Re-encoded perimeter trail control points (must match
# PERIMETER_CONTROL_POINTS in phase-10-trail-viewpoints.py). Used to sample
# positions for the 5 wooden trail signs.
PERIMETER_CONTROL_POINTS = [
    ( 80.0,   0.0),
    ( 69.0,  40.0),
    ( 40.0,  69.0),
    (  0.0,  80.0),
    (-40.0,  69.0),
    (-69.0,  40.0),
    (-80.0,   0.0),
    (-69.0, -40.0),
    (-40.0, -69.0),
    (  0.0, -80.0),
    ( 40.0, -69.0),
    ( 69.0, -40.0),
]

# Hand-placed boulder cluster CENTRES (runtime x, z). 6 clusters that fill
# currently-empty pockets of the map (corridors between sections + the
# NE forest edge + SW meadow edge).
BOULDER_CLUSTER_CENTRES = [
    ( 30.0,  30.0),   # 1: between Projects + Experience corridor
    (-30.0,  30.0),   # 2: between Contact + Experience corridor
    ( 30.0, -30.0),   # 3: between Projects + Skills corridor
    (-30.0, -40.0),   # 4: between Contact + Skills (SW meadow)
    ( 50.0,  75.0),   # 5: NE forest edge
    (-50.0, -75.0),   # 6: SW meadow edge
]
CLUSTER_RADIUS = 1.5
CLUSTER_MIN_BOULDERS = 3
CLUSTER_MAX_BOULDERS = 5
CLUSTER_SECTION_BUFFER = 4.0   # looser than the default 6m so clusters can
                               # sit closer to section edges (per spec)


# ============================================================================
# Source mesh authoring helpers
# ============================================================================


def _new_source_mesh(name):
    """Create-or-replace a Blender mesh datablock by name.

    Phase 11 instances share the same datablock; clearing the mesh by name
    also invalidates every instance that referenced it, which is why we run
    clear_collection on the instance collections BEFORE rebuilding sources.
    """
    existing = bpy.data.meshes.get(name)
    if existing is not None:
        bpy.data.meshes.remove(existing, do_unlink=True)
    return bpy.data.meshes.new(name)


def _bm_add_clump(bm, uv, centre, radius, body_key,
                  shade_key=None, shade_fraction=0.0,
                  rings=3, segments=8, jitter=0.1, rng=None):
    """Append a low-poly faceted sphere ("foliage clump") to `bm`.

    Builds a UV-sphere style mesh with `rings` latitude rings and `segments`
    longitude slices, plus a top + bottom vertex. Per-vertex radius jitter
    (`jitter`, fraction of radius) breaks the perfect sphere silhouette.

    Painting: every face gets `body_key`. If `shade_key`+`shade_fraction>0`,
    that fraction of the *bottom-half* faces is repainted with shade_key
    (deterministic via `rng`). Returns nothing.
    """
    cx, cy, cz = centre
    if rng is None:
        rng = random.Random(0)

    # Build latitude rings between poles.
    ring_verts = []
    for r in range(rings):
        # r=0 just below top pole, r=rings-1 just above bottom pole.
        phi = math.pi * (r + 1) / (rings + 1)   # 0..pi
        z = math.cos(phi)
        ring_radius_factor = math.sin(phi)
        ring = []
        for s in range(segments):
            theta = (s / segments) * math.tau
            jr = radius * (1.0 + (rng.random() - 0.5) * jitter)
            rx = math.cos(theta) * ring_radius_factor * jr
            ry = math.sin(theta) * ring_radius_factor * jr
            rz = z * jr
            ring.append(bm.verts.new((cx + rx, cy + ry, cz + rz)))
        ring_verts.append(ring)

    top_pole = bm.verts.new((cx, cy, cz + radius * (1.0 + (rng.random() - 0.5) * jitter)))
    bottom_pole = bm.verts.new((cx, cy, cz - radius * (1.0 + (rng.random() - 0.5) * jitter)))

    side_faces = []

    # Triangles to top pole.
    top_ring = ring_verts[0]
    for s in range(segments):
        s2 = (s + 1) % segments
        face = bm.faces.new((top_pole, top_ring[s], top_ring[s2]))
        side_faces.append(face)

    # Quad bands between adjacent rings.
    for r in range(rings - 1):
        ra = ring_verts[r]
        rb = ring_verts[r + 1]
        for s in range(segments):
            s2 = (s + 1) % segments
            face = bm.faces.new((ra[s], rb[s], rb[s2], ra[s2]))
            side_faces.append(face)

    # Triangles to bottom pole.
    bot_ring = ring_verts[-1]
    for s in range(segments):
        s2 = (s + 1) % segments
        face = bm.faces.new((bottom_pole, bot_ring[s2], bot_ring[s]))
        side_faces.append(face)

    # Paint body, then repaint a fraction of the lower-half faces shade.
    for face in side_faces:
        _lib.paint_face(face, uv, body_key)

    if shade_key is not None and shade_fraction > 0.0:
        lower = [f for f in side_faces if f.calc_center_median().z < cz]
        rng.shuffle(lower)
        cut = int(len(lower) * shade_fraction)
        for f in lower[:cut]:
            _lib.paint_face(f, uv, shade_key)


def _build_pine_variant_source(name, height, num_clumps, trunk_height,
                               trunk_radius, base_radius, lean_deg=0.0,
                               body_key="pine_canopy",
                               sunlit_key="sunlit_pine",
                               shade_key="deep_shade",
                               trunk_key="wood_lantern_body",
                               clump_xy_jitter=0.10,
                               lean_side_offset=0.0):
    """Build one pine variant source mesh. Returns the bpy.data.meshes block.

    The canopy is now a stack of `num_clumps` low-poly icosphere foliage
    clumps (matching the revamped birches), decreasing in radius top->bottom
    to give the classic pine silhouette. A 50/50 split paints each clump
    body_key vs sunlit_key (alternating up the stack) so directional shading
    reads even on a still trunk; `_bm_add_clump`'s shade_fraction repaints a
    few underside faces deep_shade per clump for dapple. `body_key`/
    `sunlit_key`/`shade_key` let later variants paint the canopy with autumn
    / deep-shade / meadow palettes. Trunk sits below the canopy at
    z=0..trunk_height. `lean_side_offset` (m) shifts every clump in +X to
    bias the silhouette to one side (variant 6 leaning pine).
    """
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    rng = random.Random(hash(name) & 0xFFFFFFFF)

    # Trunk cylinder.
    bm_segments = 8
    bot_ring = []
    top_ring = []
    for i in range(bm_segments):
        angle = (i / bm_segments) * math.tau
        bx = math.cos(angle) * trunk_radius
        by = math.sin(angle) * trunk_radius
        bot_ring.append(bm.verts.new((bx, by, 0.0)))
        top_ring.append(bm.verts.new((bx, by, trunk_height)))
    for i in range(bm_segments):
        j = (i + 1) % bm_segments
        face = bm.faces.new((bot_ring[i], top_ring[i],
                             top_ring[j], bot_ring[j]))
        _lib.paint_face(face, uv, trunk_key)
    bottom_cap = bm.faces.new(list(reversed(bot_ring)))
    _lib.paint_face(bottom_cap, uv, "deep_shade")

    # Stack of icosphere clumps above the trunk. Bottom clump is the
    # widest (radius=base_radius), top clump tapers to ~30% of base. Each
    # clump overlaps the previous by ~40% so there's no visible gap.
    canopy_height = height - trunk_height
    # vertical step between clump CENTRES (overlap = ~0.6 * clump radius)
    if num_clumps == 1:
        step_z = 0.0
    else:
        step_z = canopy_height / num_clumps * 0.85
    # Bottom clump centre sits ABOVE the trunk top by ~0.4 * base_radius,
    # so the canopy visually wraps the top of the trunk.
    base_z = trunk_height + base_radius * 0.35
    for i in range(num_clumps):
        # Taper: bottom (i=0) = base_radius; top = ~0.30 * base_radius.
        t = i / max(1, num_clumps - 1)  # 0..1
        clump_r = base_radius * (1.0 - 0.70 * t)
        # Small XY jitter per clump — non-axial silhouette.
        ox = (rng.random() - 0.5) * 2.0 * clump_xy_jitter
        oy = (rng.random() - 0.5) * 2.0 * clump_xy_jitter
        # Lean bias: shift each clump in +X proportional to its height up
        # the stack (deeper into the canopy -> bigger shift).
        ox += lean_side_offset * t
        cz = base_z + i * step_z
        # Alternate body / sunlit per clump up the stack — gives the
        # silhouette a cheap directional shade without resorting to per-
        # face quadrant painting (which icospheres don't sit well with).
        clump_body = sunlit_key if (i % 2 == 0) else body_key
        _bm_add_clump(
            bm, uv,
            centre=(ox, oy, cz),
            radius=clump_r,
            body_key=clump_body,
            shade_key=shade_key,
            shade_fraction=0.30,   # underside dapple per clump
            rings=3, segments=8,   # 8 lon * 3 lat + 2 poles = 26 verts/clump
            jitter=0.12,
            rng=rng,
        )

    # Apply lean as a shear-by-tilt on the canopy verts (above trunk).
    if lean_deg != 0.0:
        lean_rad = math.radians(lean_deg)
        for v in bm.verts:
            if v.co.z > trunk_height:
                offset = (v.co.z - trunk_height) * math.tan(lean_rad)
                v.co.x += offset

    mesh = _new_source_mesh(name)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def _build_birch_variant_source(name, height, trunk_radius,
                                 branch_count, foliage_clumps,
                                 lean_deg=0.0):
    """Build one birch variant source mesh.

    Now built from: a thicker bark trunk with small dark-band scars, 2-3
    angled branch cylinders splaying off the trunk top, and 3-5 small
    foliage clumps (icospheres) anchored at the branch tips + trunk top.
    Total silhouette is markedly tree-shaped, not the cube-on-stick of the
    previous build.
    """
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    rng = random.Random(hash(name) & 0xFFFFFFFF)

    # White trunk (thicker than the v1: trunk_radius 0.10-0.15m).
    bm_segments = 10
    bot_ring = []
    top_ring = []
    for i in range(bm_segments):
        angle = (i / bm_segments) * math.tau
        bx = math.cos(angle) * trunk_radius
        by = math.sin(angle) * trunk_radius
        bot_ring.append(bm.verts.new((bx, by, 0.0)))
        top_ring.append(bm.verts.new((bx, by, height)))
    trunk_side_faces = []
    for i in range(bm_segments):
        j = (i + 1) % bm_segments
        face = bm.faces.new((bot_ring[i], top_ring[i],
                             top_ring[j], bot_ring[j]))
        _lib.paint_face(face, uv, "sunlit_snow")
        trunk_side_faces.append(face)
    bottom_cap = bm.faces.new(list(reversed(bot_ring)))
    _lib.paint_face(bottom_cap, uv, "deep_shade")
    top_cap = bm.faces.new(top_ring)
    _lib.paint_face(top_cap, uv, "sunlit_snow")

    # Dark-bark "scar" bands every ~1m up the trunk. We repaint a handful
    # of side faces deep_shade. With 10 segments, picking a contiguous
    # 2-face arc near a target Z fakes a band scar without re-meshing.
    target_band_zs = []
    z = 1.0
    while z < height - 0.4:
        target_band_zs.append(z)
        z += 1.0
    for band_z in target_band_zs:
        # Pick faces whose midpoint Z is closest to band_z.
        ordered = sorted(
            trunk_side_faces,
            key=lambda f: abs(f.calc_center_median().z - band_z),
        )
        band_face_count = max(1, min(3, bm_segments // 4))
        for face in ordered[:band_face_count]:
            _lib.paint_face(face, uv, "deep_shade")

    # Branches: small angled cylinders splaying off near the trunk top.
    # Each is a short cylinder built along an axis that we rotate post-hoc.
    branch_radius = 0.04
    branch_segments = 6
    branch_origin_z = height * 0.78  # branches start before crown
    branch_tip_positions = []
    for bi in range(branch_count):
        # Branch direction: tilted 25-45° off vertical, evenly spread.
        base_angle = (bi / branch_count) * math.tau + rng.random() * 0.5
        tilt = math.radians(25.0 + rng.random() * 20.0)
        length = 0.5 + rng.random() * 0.3
        dx = math.cos(base_angle) * math.sin(tilt)
        dy = math.sin(base_angle) * math.sin(tilt)
        dz = math.cos(tilt)
        # Branch axis: build a thin cylinder from (0,0,branch_origin_z)
        # along (dx, dy, dz)*length. Build by sweeping a perpendicular
        # frame.
        # Pick an arbitrary perpendicular to (dx, dy, dz).
        if abs(dz) < 0.99:
            perp = (math.sin(base_angle), -math.cos(base_angle), 0.0)
        else:
            perp = (1.0, 0.0, 0.0)
        # Second perpendicular via cross product.
        cross = (
            dy * perp[2] - dz * perp[1],
            dz * perp[0] - dx * perp[2],
            dx * perp[1] - dy * perp[0],
        )
        base_ring = []
        tip_ring = []
        for i in range(branch_segments):
            a = (i / branch_segments) * math.tau
            rx = math.cos(a) * branch_radius
            ry = math.sin(a) * branch_radius
            ox = perp[0] * rx + cross[0] * ry
            oy = perp[1] * rx + cross[1] * ry
            oz = perp[2] * rx + cross[2] * ry
            base_ring.append(bm.verts.new((ox, oy, branch_origin_z + oz)))
            tx = dx * length
            ty = dy * length
            tz = branch_origin_z + dz * length
            tip_ring.append(bm.verts.new((tx + ox, ty + oy, tz + oz)))
        for i in range(branch_segments):
            j = (i + 1) % branch_segments
            face = bm.faces.new((base_ring[i], tip_ring[i],
                                 tip_ring[j], base_ring[j]))
            _lib.paint_face(face, uv, "sunlit_snow")
        # Caps (deep_shade) so the tip looks solid.
        try:
            tcap = bm.faces.new(tip_ring)
            _lib.paint_face(tcap, uv, "sunlit_snow")
        except ValueError:
            pass
        branch_tip_positions.append((dx * length, dy * length,
                                     branch_origin_z + dz * length))

    # Foliage clumps: 3-5 small icospheres placed at branch tips + trunk top.
    # Mix sizes and slight Z offsets above each anchor.
    anchors = [(0.0, 0.0, height + 0.1)]   # trunk top
    anchors.extend(branch_tip_positions)
    rng.shuffle(anchors)

    for ci in range(foliage_clumps):
        # Pick an anchor (cycling) then jitter the position outward + up.
        ax, ay, az = anchors[ci % len(anchors)]
        jx = ax + (rng.random() - 0.5) * 0.35
        jy = ay + (rng.random() - 0.5) * 0.35
        jz = az + (rng.random() - 0.1) * 0.4
        r = 0.30 + rng.random() * 0.35
        # 60% chance of pure meadow_grass, 40% chance of pine_canopy mix
        # for variation within a single birch.
        body = "meadow_grass" if rng.random() < 0.6 else "pine_canopy"
        _bm_add_clump(
            bm, uv,
            centre=(jx, jy, jz),
            radius=r,
            body_key=body,
            shade_key="deep_shade",
            shade_fraction=0.25,
            rings=3, segments=8,
            jitter=0.15,
            rng=rng,
        )

    # Apply lean as a shear on canopy verts (above trunk top).
    if lean_deg != 0.0:
        lean_rad = math.radians(lean_deg)
        # Lean threshold: anything above ~70% of trunk height shears.
        thresh = height * 0.7
        for v in bm.verts:
            if v.co.z > thresh:
                offset = (v.co.z - thresh) * math.tan(lean_rad)
                v.co.x += offset

    mesh = _new_source_mesh(name)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def _build_fern_variant_source(name, frond_count, frond_length):
    """Low-poly fern: a few thin frond quads radiating from origin."""
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)

    rng = random.Random(hash(name) & 0xFFFF)
    for fi in range(frond_count):
        angle = (fi / frond_count) * math.tau + rng.random() * 0.3
        tilt = math.radians(40.0 + rng.random() * 20.0)
        length = frond_length * (0.8 + rng.random() * 0.3)
        # Frond as a thin tapered cuboid lying along the tilted direction.
        dir_x = math.cos(angle) * math.sin(tilt)
        dir_y = math.sin(angle) * math.sin(tilt)
        dir_z = math.cos(tilt)
        tip_x = dir_x * length
        tip_y = dir_y * length
        tip_z = dir_z * length
        # Build a flat quad from base to tip with small width.
        half_w = 0.05
        # Side perpendicular to the frond direction projected to XY.
        side_x = -math.sin(angle) * half_w
        side_y = math.cos(angle) * half_w
        v0 = bm.verts.new((-side_x, -side_y, 0.0))
        v1 = bm.verts.new((side_x, side_y, 0.0))
        v2 = bm.verts.new((tip_x + side_x, tip_y + side_y, tip_z))
        v3 = bm.verts.new((tip_x - side_x, tip_y - side_y, tip_z))
        face = bm.faces.new((v0, v1, v2, v3))
        _lib.paint_face(face, uv, "sunlit_pine")

    mesh = _new_source_mesh(name)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def _build_flower_variant_source(name, top_color_key):
    """Wildflower: a thin stem cuboid + a small cluster on top."""
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)

    # Stem.
    stem_height = 0.3
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, stem_height * 0.5),
        half_extents=(0.025, 0.025, stem_height * 0.5),
        color_key="meadow_grass",
    )

    # Flower top: small cuboid.
    top_size = 0.08
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, stem_height + top_size * 0.5),
        half_extents=(top_size, top_size, top_size * 0.5),
        color_key=top_color_key,
    )

    mesh = _new_source_mesh(name)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def _build_boulder_variant_source(name, size, mossy_top=True):
    """Mossy boulder: rough beveled cuboid. Top face painted meadow_grass to
    suggest moss, body painted rock_mid.

    `size` here is the boulder's horizontal half-extent (m). Heights are
    proportional but squashed (~0.4x). Per-variant size is now coarse-grained
    by the caller (variants 1-5 span 0.3..2.5m); per-instance scale variance
    adds another 0.7..1.4x on top.
    """
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)

    # Slightly squashed cuboid.
    hx = size * (0.5 + 0.1)
    hy = size * (0.5 + 0.1)
    hz = size * 0.4
    faces = _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, hz),
        half_extents=(hx, hy, hz),
        color_key="rock_mid",
    )
    # Top face (index 1) repainted moss-green.
    if mossy_top:
        _lib.paint_face(faces[1], uv, "meadow_grass")

    mesh = _new_source_mesh(name)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def _build_hero_boulder_variant_source(name, size):
    """Hero boulder variant 5: a larger boulder with extra silhouette
    asymmetry — two stacked rough cuboids with offset + a slightly tilted
    upper block. Painted rock_mid with a meadow_grass moss top and
    dark_rock_shadow on the lower belt to read 'big rock' from distance.
    """
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    rng = random.Random(hash(name) & 0xFFFFFFFF)

    # Lower block: wide + squat.
    hx0 = size * 0.55
    hy0 = size * 0.50
    hz0 = size * 0.30
    lower_faces = _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, hz0),
        half_extents=(hx0, hy0, hz0),
        color_key="rock_mid",
    )
    # Bottom face (index 0) -> dark shadow belt.
    _lib.paint_face(lower_faces[0], uv, "dark_rock_shadow")

    # Upper block: narrower, offset, smaller.
    hx1 = size * 0.38
    hy1 = size * 0.42
    hz1 = size * 0.22
    ox = (rng.random() - 0.5) * size * 0.15
    oy = (rng.random() - 0.5) * size * 0.15
    upper_faces = _lib.bm_add_cuboid(
        bm, uv,
        center=(ox, oy, hz0 * 2 + hz1),
        half_extents=(hx1, hy1, hz1),
        color_key="rock_mid",
    )
    # Top face (index 1) -> moss.
    _lib.paint_face(upper_faces[1], uv, "meadow_grass")

    mesh = _new_source_mesh(name)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def _build_bush_variant_source(name, palette):
    """Build a Bruno-style bush source mesh.

    A bush = 2-4 small low-poly icosphere-like clumps stacked + offset,
    total height ~0.3-0.8m. Painted with `palette` (a sequence of color
    keys); each clump picks one entry, and a fraction of the bottom-half
    faces flip to a shade key for depth.
    """
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    rng = random.Random(hash(name) & 0xFFFFFFFF)

    # Determine cluster count + total bush footprint.
    clump_count = 2 + rng.randrange(3)   # 2..4
    base_radius = 0.18 + rng.random() * 0.12   # ~0.18..0.30m per clump
    bush_max_z = 0.0
    for ci in range(clump_count):
        # Concentric-ish: first clump centred, later clumps offset.
        if ci == 0:
            cx = 0.0
            cy = 0.0
        else:
            angle = rng.random() * math.tau
            dist = base_radius * (0.6 + rng.random() * 0.5)
            cx = math.cos(angle) * dist
            cy = math.sin(angle) * dist
        # Stack the clumps a little higher each time, but with overlap.
        cz = base_radius * 0.6 + ci * base_radius * 0.6
        bush_max_z = max(bush_max_z, cz + base_radius)
        body = palette[ci % len(palette)]
        _bm_add_clump(
            bm, uv,
            centre=(cx, cy, cz),
            radius=base_radius * (0.9 + rng.random() * 0.3),
            body_key=body,
            shade_key="deep_shade",
            shade_fraction=0.20,
            rings=2, segments=8,
            jitter=0.18,
            rng=rng,
        )

    mesh = _new_source_mesh(name)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    return mesh


# ============================================================================
# Source-mesh registry — build every unique mesh once.
# ============================================================================


def _build_all_sources():
    """Author every source mesh. Returns dict {category: [mesh, ...]}.

    These are bpy.data.meshes datablocks. Instance objects below share them.
    A hidden placeholder object per source is also placed so the Outliner
    shows the source meshes — that's the documented contract from the plan.
    """
    sources = {"pine": [], "birch": [], "hero_pine": None,
               "fern": [], "flower": [], "boulder": [], "bush": []}

    # 10 pine variants — revamped to use icosphere clump stacks (matching
    # the birch revamp). spec keys:
    # (height, num_clumps, trunk_h, trunk_r, base_r, lean_deg,
    #  lean_side_offset, body_key, sunlit_key, shade_key, trunk_key)
    pine_specs = [
        # 1-3: classic green pines (the KEEPER trio). 3-4 clumps each.
        (4.0, 4, 0.6, 0.10, 0.85, 0.0, 0.0,
         "pine_canopy", "sunlit_pine", "deep_shade", "wood_lantern_body"),
        (4.5, 4, 0.7, 0.11, 0.95, 3.0, 0.0,
         "pine_canopy", "sunlit_pine", "deep_shade", "wood_lantern_body"),
        (5.0, 5, 0.8, 0.12, 1.05, 0.0, 0.0,
         "pine_canopy", "sunlit_pine", "deep_shade", "wood_lantern_body"),
        # 4: tall-narrow conifer — many clumps, each smaller.
        (7.5, 7, 1.4, 0.13, 0.80, 0.0, 0.0,
         "pine_canopy", "sunlit_pine", "deep_shade", "wood_lantern_body"),
        # 5: short-wide Christmas-tree pine — fewer clumps, bigger.
        (3.5, 3, 0.6, 0.13, 1.50, 0.0, 0.0,
         "pine_canopy", "sunlit_pine", "deep_shade", "wood_lantern_body"),
        # 6: leaning pine — moderate clump count + side-offset stack.
        (5.5, 4, 0.9, 0.13, 1.10, 8.0, 0.18,
         "pine_canopy", "sunlit_pine", "deep_shade", "wood_lantern_body"),
        # 7: bushy fir — many clumps with high overlap.
        (6.0, 5, 1.0, 0.14, 1.40, 0.0, 0.0,
         "pine_canopy", "sunlit_pine", "deep_shade", "wood_lantern_body"),
        # 8: AUTUMN warm pine.
        (4.5, 4, 0.7, 0.12, 0.95, 0.0, 0.0,
         "wood_lantern_body", "lantern_warm", "deep_shade", "dirt_path"),
        # 9: deep-shade dark pine.
        (5.0, 4, 0.8, 0.12, 1.00, 2.0, 0.0,
         "deep_shade", "pine_canopy", "deep_shade", "wood_lantern_body"),
        # 10: meadow-greener pine.
        (5.0, 4, 0.8, 0.12, 1.00, 0.0, 0.0,
         "meadow_grass", "sunlit_pine", "pine_canopy", "wood_lantern_body"),
    ]
    for i, spec in enumerate(pine_specs):
        (h, nc, th, tr, br, lean, lean_off,
         body, sun, shade, trunk) = spec
        mesh = _build_pine_variant_source(
            f"tree_pine_var_{i + 1}_src_mesh",
            height=h, num_clumps=nc, trunk_height=th,
            trunk_radius=tr, base_radius=br, lean_deg=lean,
            lean_side_offset=lean_off,
            body_key=body, sunlit_key=sun, shade_key=shade,
            trunk_key=trunk,
        )
        sources["pine"].append(mesh)

    # 5 birch variants — visibly different silhouettes.
    # (height, trunk_radius, branch_count, foliage_clumps, lean_deg)
    birch_specs = [
        (5.0, 0.12, 3, 5,  0.0),   # tall-narrow
        (3.5, 0.13, 2, 4,  0.0),   # short-bushy
        (4.2, 0.11, 3, 5,  6.0),   # leaning
        (4.8, 0.14, 3, 5,  0.0),   # multi-branch
        (3.8, 0.10, 1, 3, -3.0),   # single-cluster, slight lean opposite
    ]
    for i, spec in enumerate(birch_specs):
        h, tr, bc, fc, lean = spec
        mesh = _build_birch_variant_source(
            f"tree_birch_var_{i + 1}_src_mesh",
            height=h, trunk_radius=tr,
            branch_count=bc, foliage_clumps=fc,
            lean_deg=lean,
        )
        sources["birch"].append(mesh)

    # Hero pine — same clump approach but bigger: 11m tall, 6 clumps.
    sources["hero_pine"] = _build_pine_variant_source(
        "tree_hero_pine_src_mesh",
        height=HERO_TREE_HEIGHT, num_clumps=6,
        trunk_height=1.8, trunk_radius=HERO_TREE_TRUNK_RADIUS,
        base_radius=2.0, lean_deg=0.0,
    )

    # 3 fern variants.
    fern_specs = [(5, 0.4), (7, 0.35), (4, 0.45)]
    for i, (fc, fl) in enumerate(fern_specs):
        mesh = _build_fern_variant_source(
            f"gc_fern_var_{i + 1}_src_mesh",
            frond_count=fc, frond_length=fl,
        )
        sources["fern"].append(mesh)

    # 4 wildflower variants — different top colours.
    flower_specs = [
        "shadowed_snow",      # pink-ish
        "lantern_warm",       # yellow
        "sunlit_snow",        # white
        "lantern_warm",       # yellow (second variant for variety)
    ]
    for i, color_key in enumerate(flower_specs):
        mesh = _build_flower_variant_source(
            f"gc_flower_var_{i + 1}_src_mesh",
            top_color_key=color_key,
        )
        sources["flower"].append(mesh)

    # 5 boulder variants — dramatic small/med/large step.
    # (size, builder) — builder=None uses the default cuboid boulder.
    boulder_specs = [
        (0.35, None),                   # 1: SMALL
        (0.60, None),                   # 2: SMALL-MEDIUM
        (1.00, None),                   # 3: MEDIUM
        (1.60, None),                   # 4: LARGE
        (2.25, "hero"),                 # 5: HERO (stacked + offset)
    ]
    for i, (size, builder) in enumerate(boulder_specs):
        name = f"gc_boulder_var_{i + 1}_src_mesh"
        if builder == "hero":
            mesh = _build_hero_boulder_variant_source(name, size=size)
        else:
            mesh = _build_boulder_variant_source(name, size=size)
        sources["boulder"].append(mesh)

    # 4 bush variants — Bruno-style stacked clumps.
    bush_specs = [
        ["meadow_grass", "meadow_grass", "meadow_grass"],
        ["pine_canopy",  "pine_canopy",  "pine_canopy"],
        ["meadow_grass", "deep_shade",   "meadow_grass", "deep_shade"],
        ["sunlit_pine",  "sunlit_pine",  "sunlit_pine"],
    ]
    for i, palette in enumerate(bush_specs):
        mesh = _build_bush_variant_source(
            f"gc_bush_var_{i + 1}_src_mesh",
            palette=palette,
        )
        sources["bush"].append(mesh)

    return sources


def _attach_source_placeholder(mesh, obj_name, collection_name, material):
    """Place a hidden placeholder object for the source mesh so the Outliner
    shows it. Hidden via hide_viewport+hide_render. Located OFF-MAP
    (far above the build region) so it can't accidentally be confused with
    an instance even if someone unhides it."""
    existing = bpy.data.objects.get(obj_name)
    if existing is not None:
        bpy.data.objects.remove(existing, do_unlink=True)
    obj = bpy.data.objects.new(obj_name, mesh)
    obj.location = (0.0, 0.0, 200.0)   # far above the world
    obj.hide_viewport = True
    obj.hide_render = True
    _lib.attach_palette_material(obj, material)
    _lib.place_in(collection_name, obj)
    return obj


# ============================================================================
# Exclusion zones
# ============================================================================


def _collect_water_zones():
    """Pull (x, z, radius) zones from the river and tributary mesh vertices.

    Each ribbon vertex's Blender (x, y) maps to runtime (x, z). We downsample
    every Nth vertex to keep N×candidates within budget. The river ribbon has
    4 verts per ring; if we take every 4th vertex we hit the centre column.
    """
    zones = []
    for obj_name in ("river_surface", "tributary_surface"):
        obj = bpy.data.objects.get(obj_name)
        if obj is None:
            continue
        verts = obj.data.vertices
        for i, v in enumerate(verts):
            if i % WATER_VERTEX_DOWNSAMPLE != 0:
                continue
            world_co = obj.matrix_world @ v.co
            # Blender X = runtime X, Blender Y = runtime Z.
            zones.append((world_co.x, world_co.y, RIVER_BUFFER))
    return zones


def _collect_trail_zones():
    """Pull (x, z, radius) zones from trail ribbon vertices."""
    zones = []
    trail_names = (
        "trail_perimeter",
        "trail_detour_nw",
        "trail_detour_summit",
        "trail_detour_se",
    )
    for obj_name in trail_names:
        obj = bpy.data.objects.get(obj_name)
        if obj is None:
            continue
        verts = obj.data.vertices
        for i, v in enumerate(verts):
            if i % WATER_VERTEX_DOWNSAMPLE != 0:
                continue
            world_co = obj.matrix_world @ v.co
            zones.append((world_co.x, world_co.y, TRAIL_BUFFER))
    return zones


def _build_exclusion_zones():
    """Compose the full exclusion-zone list. Hero tree zones are appended by
    the caller after hero placement so subsequent regular trees don't cluster
    on top of the heroes."""
    zones = []
    zones.extend(SECTION_ZONES)
    zones.extend(VIEWPOINT_ZONES)
    zones.append(LIGHTHOUSE_ZONE)
    zones.extend(_collect_water_zones())
    zones.extend(_collect_trail_zones())
    return zones


def _is_excluded(x, z, zones):
    """O(N) check against every zone. Short-circuits on first match."""
    for (zx, zz, zr) in zones:
        dx = x - zx
        dz = z - zz
        if dx * dx + dz * dz < zr * zr:
            return True
    return False


# ============================================================================
# Quadrant weighting helper
# ============================================================================


def _quadrant_weight(x, z, ne_weight, sw_weight, default=1.0):
    """Return placement-probability weight based on which quadrant (x, z)
    falls into. NE = (+x, +z); SW = (-x, -z); the other two = default."""
    if x > 0 and z > 0:
        return ne_weight
    if x < 0 and z < 0:
        return sw_weight
    return default


# ============================================================================
# Tree placement
# ============================================================================


def _make_instance(name, source_mesh, location, rotation_z, scale,
                   collection_name, material):
    """Create an instance object that SHARES `source_mesh` (no copy).

    The InstancedMesh contract: every instance object holds a reference to
    the same bpy.data.meshes datablock. Phase 13's exporter detects shared
    data and emits one geometry with N world transforms.
    """
    existing = bpy.data.objects.get(name)
    if existing is not None:
        bpy.data.objects.remove(existing, do_unlink=True)
    obj = bpy.data.objects.new(name, source_mesh)
    obj.location = location
    obj.rotation_euler = (0.0, 0.0, rotation_z)
    obj.scale = (scale, scale, scale)
    _lib.attach_palette_material(obj, material)
    _lib.place_in(collection_name, obj)
    return obj


def _tree_scale(rng):
    """Sample a tree per-instance scale across the widened 0.6..1.5 window."""
    return TREE_SCALE_MIN + rng.random() * (TREE_SCALE_MAX - TREE_SCALE_MIN)


def _gc_scale(rng):
    """Sample a ground-cover per-instance scale across the 0.7..1.4 window."""
    return GC_SCALE_MIN + rng.random() * (GC_SCALE_MAX - GC_SCALE_MIN)


def _place_pines(rng, sources, zones, material):
    """Stratified-sample placement of pines across the plateau."""
    placed = 0
    cells_x = int((PLACEMENT_MAX_X - PLACEMENT_MIN_X) / CELL_SIZE)
    cells_z = int((PLACEMENT_MAX_Z - PLACEMENT_MIN_Z) / CELL_SIZE)

    # Shuffle cell order so we don't get a directional bias if we run out
    # of attempts mid-grid.
    cell_indices = [(cx, cz) for cx in range(cells_x) for cz in range(cells_z)]
    rng.shuffle(cell_indices)

    for (cx, cz) in cell_indices:
        if placed >= TARGET_PINE_COUNT:
            break
        cell_min_x = PLACEMENT_MIN_X + cx * CELL_SIZE
        cell_min_z = PLACEMENT_MIN_Z + cz * CELL_SIZE
        for _attempt in range(ATTEMPTS_PER_CELL):
            if placed >= TARGET_PINE_COUNT:
                break
            x = cell_min_x + rng.random() * CELL_SIZE
            z = cell_min_z + rng.random() * CELL_SIZE
            weight = _quadrant_weight(x, z, ne_weight=1.5, sw_weight=0.3)
            if rng.random() > weight:
                continue
            if _is_excluded(x, z, zones):
                continue
            y = _lib.height_at(x, z)
            if y < WATER_REJECT_Y:
                continue
            variant = rng.randrange(len(sources["pine"]))
            source_mesh = sources["pine"][variant]
            rot = rng.random() * math.tau
            scale = _tree_scale(rng)
            placed += 1
            _make_instance(
                name=f"tree_pine_inst_{placed:03d}",
                source_mesh=source_mesh,
                location=(x, z, y),
                rotation_z=rot,
                scale=scale,
                collection_name=TREES_COLLECTION,
                material=material,
            )
    return placed


def _place_birches(rng, sources, zones, material):
    """Birches favour river-proximate cells. We iterate the river vertex
    cloud, pick 1-2 nearby points per vert, and try to place a birch."""
    placed = 0
    river = bpy.data.objects.get("river_surface")
    if river is None:
        return 0

    # Downsample river verts more aggressively for the seed points.
    seed_verts = []
    for i, v in enumerate(river.data.vertices):
        if i % 8 != 0:
            continue
        world_co = river.matrix_world @ v.co
        seed_verts.append((world_co.x, world_co.y))
    rng.shuffle(seed_verts)

    for (vx, vz) in seed_verts:
        if placed >= TARGET_BIRCH_COUNT:
            break
        for _ in range(2):
            if placed >= TARGET_BIRCH_COUNT:
                break
            # Random offset within 8m of the river vertex, biased outside
            # the river exclusion (5m), so 5-8m offset.
            angle = rng.random() * math.tau
            dist = 5.5 + rng.random() * 2.5
            x = vx + math.cos(angle) * dist
            z = vz + math.sin(angle) * dist
            if x < PLACEMENT_MIN_X or x > PLACEMENT_MAX_X:
                continue
            if z < PLACEMENT_MIN_Z or z > PLACEMENT_MAX_Z:
                continue
            if _is_excluded(x, z, zones):
                continue
            y = _lib.height_at(x, z)
            if y < WATER_REJECT_Y:
                continue
            variant = rng.randrange(len(sources["birch"]))
            source_mesh = sources["birch"][variant]
            rot = rng.random() * math.tau
            scale = _tree_scale(rng)
            placed += 1
            _make_instance(
                name=f"tree_birch_inst_{placed:03d}",
                source_mesh=source_mesh,
                location=(x, z, y),
                rotation_z=rot,
                scale=scale,
                collection_name=TREES_COLLECTION,
                material=material,
            )
    return placed


def _place_hero_trees(sources, material):
    """5 hand-placed hero trees. Scale 1.0, rotation 0.0. Returns list of
    (name, x, z, y) for collider + ref placement."""
    placed = []
    hero_mesh = sources["hero_pine"]
    for i, (rx, rz) in enumerate(HERO_TREE_POSITIONS):
        y = _lib.height_at(rx, rz)
        name = f"hero_tree_{i + 1}"
        _make_instance(
            name=name,
            source_mesh=hero_mesh,
            location=(rx, rz, y),
            rotation_z=0.0,
            scale=1.0,
            collection_name=HERO_TREES_COLLECTION,
            material=material,
        )
        placed.append((name, rx, rz, y))
    return placed


def _build_hero_tree_collider(material, hero_name, rx, rz, base_y):
    """Hidden cylinder collider matching the hero tree trunk + canopy
    envelope."""
    cy = base_y + HERO_TREE_HEIGHT * 0.5
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cylinder(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        radius=HERO_TREE_TRUNK_RADIUS,
        height=HERO_TREE_HEIGHT,
        color_key="wood_lantern_body",
        segments=12,
    )
    suffix = hero_name.split("_")[-1]
    name = f"tube_hero_tree_{suffix}"
    return _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"{name}_mesh",
        obj_name=name,
        location=(rx, rz, cy),
        collection_name=HERO_TREES_COLLECTION,
        material=material,
        hide=True,
    )


# ============================================================================
# Ground cover placement
# ============================================================================


def _place_ground_cover(rng, sources, zones, material,
                       category, target_count, ne_weight, sw_weight,
                       name_prefix):
    """Generic stratified-sample placement for ground cover.

    Mirrors _place_pines but uses `category` from `sources` and the supplied
    quadrant weights / target count / name prefix. Per-instance scale uses
    the widened GC window (0.7..1.4).
    """
    placed = 0
    cells_x = int((PLACEMENT_MAX_X - PLACEMENT_MIN_X) / CELL_SIZE)
    cells_z = int((PLACEMENT_MAX_Z - PLACEMENT_MIN_Z) / CELL_SIZE)

    cell_indices = [(cx, cz) for cx in range(cells_x) for cz in range(cells_z)]
    rng.shuffle(cell_indices)

    for (cx, cz) in cell_indices:
        if placed >= target_count:
            break
        cell_min_x = PLACEMENT_MIN_X + cx * CELL_SIZE
        cell_min_z = PLACEMENT_MIN_Z + cz * CELL_SIZE
        for _attempt in range(ATTEMPTS_PER_CELL):
            if placed >= target_count:
                break
            x = cell_min_x + rng.random() * CELL_SIZE
            z = cell_min_z + rng.random() * CELL_SIZE
            weight = _quadrant_weight(x, z, ne_weight=ne_weight,
                                      sw_weight=sw_weight)
            if rng.random() > weight:
                continue
            if _is_excluded(x, z, zones):
                continue
            y = _lib.height_at(x, z)
            if y < WATER_REJECT_Y:
                continue
            variant = rng.randrange(len(sources[category]))
            source_mesh = sources[category][variant]
            rot = rng.random() * math.tau
            scale = _gc_scale(rng)
            placed += 1
            _make_instance(
                name=f"{name_prefix}_{placed:03d}",
                source_mesh=source_mesh,
                location=(x, z, y),
                rotation_z=rot,
                scale=scale,
                collection_name=GROUND_COVER_COLLECTION,
                material=material,
            )
    return placed


# ============================================================================
# Props: hand-placed decorative furniture (benches, signs, boulder clusters)
# ============================================================================
#
# Pattern: each prop type authors its visible mesh as ONE bmesh (composed
# of multiple components — seat + 2 supports for a bench, post + plank for
# a sign) and finalises to a single bpy.data.meshes datablock. Bench
# colliders use bm_finalize_to_object as well, hidden. Boulder clusters
# REUSE existing boulder source meshes (the same datablocks the scattered
# ground-cover pass uses), so cluster boulders also feed Phase 13's
# InstancedMesh detection alongside the regular boulder pass.


def _bm_add_bench(bm, uv):
    """Append a wooden bench (seat plank + 2 stone supports) to `bm`.

    Bench origin is at world XY 0,0 with the seat oriented along the X axis
    (bench length in X). Supports are at the ±X ends. The seat top sits at
    height BENCH_TOP_Y (0.53m). Bench facing direction is +Y (sitter looks
    along +Y); per-bench yaw rotation is applied at the object level.

    Total bbox (centred at origin): X=[-0.60, 0.60], Y=[-0.175, 0.175],
    Z=[0.0, 0.53].
    """
    # Stone supports: one per end. Centre Z = BENCH_SUPPORT_HEIGHT * 0.5.
    support_centre_z = BENCH_SUPPORT_HEIGHT * 0.5
    support_dx = (BENCH_SEAT_LENGTH * 0.5) - BENCH_SUPPORT_HALF_X
    for sign_x in (-1.0, 1.0):
        _lib.bm_add_cuboid(
            bm, uv,
            center=(sign_x * support_dx, 0.0, support_centre_z),
            half_extents=(BENCH_SUPPORT_HALF_X,
                          BENCH_SUPPORT_HALF_Y,
                          BENCH_SUPPORT_HEIGHT * 0.5),
            color_key="rock_mid",
        )

    # Seat plank: spans the full bench length on top of the supports.
    seat_centre_z = BENCH_SUPPORT_HEIGHT + BENCH_SEAT_THICKNESS * 0.5
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, seat_centre_z),
        half_extents=(BENCH_SEAT_LENGTH * 0.5,
                      BENCH_SEAT_DEPTH * 0.5,
                      BENCH_SEAT_THICKNESS * 0.5),
        color_key="wood_lantern_body",
    )


def _build_bench(key, rx, rz, facing_yaw_z, material):
    """Author one bench at (rx, rz) on the terrain heightfield, rotated so
    the seat faces `facing_yaw_z` (radians, Blender +Z rotation).

    Builds the visible mesh AND a hidden bbox-sized cuboid collider. Both
    live in PROPS_BENCHES_COLLECTION. Returns (bench_obj, collider_obj).
    """
    base_y = _lib.height_at(rx, rz)

    # Visible bench mesh — built at Blender origin, rotated + translated by
    # the object transform.
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _bm_add_bench(bm, uv)
    bench_obj = _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"bench_{key}_mesh",
        obj_name=f"bench_{key}",
        location=(rx, rz, base_y),
        collection_name=PROPS_BENCHES_COLLECTION,
        material=material,
        rotation_euler=(0.0, 0.0, facing_yaw_z),
    )

    # Collider: bbox-sized cuboid sitting at the bench centre. Bench bbox
    # spans Z=[0, BENCH_TOP_Y]; collider centre Y = base_y + BENCH_TOP_Y/2,
    # half-height = BENCH_TOP_Y/2 (~0.265m). The collider's XY half-extents
    # match the bench's local bbox half-extents but rotated by facing_yaw_z
    # to align with the bench. We bake the rotation into the collider mesh
    # by building it at origin and giving the OBJECT the same yaw.
    coll_bm = bmesh.new()
    coll_uv = coll_bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    coll_hx = BENCH_SEAT_LENGTH * 0.5
    coll_hy = BENCH_SEAT_DEPTH * 0.5
    coll_hz = BENCH_TOP_Y * 0.5
    _lib.bm_add_cuboid(
        coll_bm, coll_uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(coll_hx, coll_hy, coll_hz),
        color_key="deep_shade",
    )
    coll_centre_z = base_y + BENCH_TOP_Y * 0.5
    collider_obj = _lib.bm_finalize_to_object(
        coll_bm,
        mesh_name=f"cuboid_bench_{key}_mesh",
        obj_name=f"cuboid_bench_{key}",
        location=(rx, rz, coll_centre_z),
        collection_name=PROPS_BENCHES_COLLECTION,
        material=material,
        rotation_euler=(0.0, 0.0, facing_yaw_z),
        hide=True,
    )

    return bench_obj, collider_obj


def _bm_add_sign(bm, uv):
    """Append a wooden trail sign (vertical post + horizontal plank) to `bm`.

    Sign origin is the foot of the post. Post extends from Z=0 to Z=
    SIGN_POST_HEIGHT (1.7m). The plank sits ON TOP of the post, centred in
    XY at origin and extending in X (the readable face faces +Y). One face
    of the plank (+Y) is repainted sand_gravel to suggest engraved text.

    Total height ~ 1.7 + 0.35 = 2.05m. Plank bbox-half: 0.40 x 0.05 x
    0.175m. No collider — signs are walk-through accents.
    """
    # Post: thin Z-axis cylinder. Centre at half-height.
    _lib.bm_add_cylinder(
        bm, uv,
        center=(0.0, 0.0, SIGN_POST_HEIGHT * 0.5),
        radius=SIGN_POST_RADIUS,
        height=SIGN_POST_HEIGHT,
        color_key="wood_lantern_body",
        segments=8,
    )

    # Plank: small cuboid sitting on top of the post.
    plank_centre_z = SIGN_POST_HEIGHT + SIGN_PLANK_HALF_Z
    plank_faces = _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, plank_centre_z),
        half_extents=(SIGN_PLANK_HALF_X,
                      SIGN_PLANK_HALF_Y,
                      SIGN_PLANK_HALF_Z),
        color_key="wood_lantern_body",
    )
    # bm_add_cuboid face order: [bottom, top, -Y, +Y, -X, +X]. Repaint +Y
    # (index 3) sand_gravel to suggest the engraved/readable face.
    _lib.paint_face(plank_faces[3], uv, "sand_gravel")


def _build_sign(idx, rx, rz, facing_yaw_z, material):
    """Author one sign at (rx, rz) on the terrain heightfield, rotated so
    the readable face (+Y in local space) points toward the next section
    in walking direction. Returns the sign object."""
    base_y = _lib.height_at(rx, rz)

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _bm_add_sign(bm, uv)
    return _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"sign_{idx}_mesh",
        obj_name=f"sign_{idx}",
        location=(rx, rz, base_y),
        collection_name=PROPS_SIGNS_COLLECTION,
        material=material,
        rotation_euler=(0.0, 0.0, facing_yaw_z),
    )


def _sample_perimeter_at_t(t):
    """Sample (x, z) at parameter t in [0, 1) on the CLOSED Catmull-Rom
    perimeter loop. Mirrors phase-10's _sample_closed_curve algorithm but
    for a single t-value rather than a uniform list."""
    cps = PERIMETER_CONTROL_POINTS
    n = len(cps)
    pts = [cps[-1]] + list(cps) + [cps[0], cps[1]]
    segments = n
    seg_f = (t % 1.0) * segments
    seg_i = int(seg_f) % segments
    local_t = seg_f - int(seg_f)
    p0 = pts[seg_i]
    p1 = pts[seg_i + 1]
    p2 = pts[seg_i + 2]
    p3 = pts[seg_i + 3]
    # Catmull-Rom tau=0.5 (same constants as phase-10).
    u = local_t
    u2 = u * u
    u3 = u2 * u
    a = -0.5 * u3 + u2 - 0.5 * u
    b =  1.5 * u3 - 2.5 * u2 + 1.0
    c = -1.5 * u3 + 2.0 * u2 + 0.5 * u
    d =  0.5 * u3 - 0.5 * u2
    x = a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0]
    z = a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]
    return (x, z)


def _perimeter_tangent_yaw_at_t(t, eps=0.005):
    """Return the yaw (Z rotation, radians) such that the sign's +Y face
    points along the walking direction (the perimeter's CCW tangent at t).

    Tangent in runtime XZ is (dx, dz). Sign's +Y face direction after a
    yaw rotation about Z is (-sin(yaw), cos(yaw)). Solve yaw = atan2(-dx, dz)
    so the cross product aligns.
    """
    p_a = _sample_perimeter_at_t(t)
    p_b = _sample_perimeter_at_t(t + eps)
    dx = p_b[0] - p_a[0]
    dz = p_b[1] - p_a[1]
    return math.atan2(-dx, dz)


def _spur_tangent_at_endpoint(controls, eps=0.005):
    """Unit tangent at the END (t=1) of an open Catmull-Rom curve in runtime
    XZ. Mirrors phase-10's _tangent_at_open_end so spur tangents here match
    the ones used to paint the waystone carved-face.

    Returns (tx, tz) — the direction the player is walking AT the spur
    endpoint (i.e. toward the view past the waystone).
    """
    def sample_at(t):
        pts = [controls[0]] + list(controls) + [controls[-1]]
        segments = len(pts) - 3
        seg_f = t * segments
        seg_i = int(seg_f)
        if seg_i >= segments:
            seg_i = segments - 1
            local_t = 1.0
        else:
            local_t = seg_f - seg_i
        p0 = pts[seg_i]
        p1 = pts[seg_i + 1]
        p2 = pts[seg_i + 2]
        p3 = pts[seg_i + 3]
        u = local_t
        u2 = u * u
        u3 = u2 * u
        a = -0.5 * u3 + u2 - 0.5 * u
        b = 1.5 * u3 - 2.5 * u2 + 1.0
        c = -1.5 * u3 + 2.0 * u2 + 0.5 * u
        d = 0.5 * u3 - 0.5 * u2
        x = a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0]
        z = a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]
        return (x, z)

    p_a = sample_at(max(0.0, 1.0 - eps))
    p_b = sample_at(1.0)
    tx = p_b[0] - p_a[0]
    tz = p_b[1] - p_a[1]
    length = math.hypot(tx, tz)
    if length == 0.0:
        return (1.0, 0.0)
    return (tx / length, tz / length)


# Distance from each waystone to its bench, measured along the -tangent
# direction (back toward the perimeter trail / approach side).
BENCH_OFFSET_FROM_WAYSTONE = 2.5


def _place_benches(material):
    """Place 3 benches near the 3 viewpoint waystones. Returns a list of
    (key, rx, rz, base_y) for ref creation.

    Each bench sits on the PERIMETER-TRAIL side of its waystone — offset
    BENCH_OFFSET_FROM_WAYSTONE metres in the -tangent direction (i.e.
    AWAY from the view, back toward the approach) so the bench sits on
    flat plateau ground rather than out on the cliff/slope where the
    waystone faces. The sitter looks PAST the waystone toward the view,
    so the bench's local +Y (sitter-facing direction) aligns with the
    spur tangent.

    The previous build offset the bench OPPOSITE-to-approach by 1.5m,
    which put bench_nw out over the cliff trench and bench_summit on the
    steep summit ridge. This pass flips that.
    """
    placed = []
    waystones = {
        "nw":     (-76.0,  45.0),
        "summit": ( 15.0,  95.0),
        "se":     ( 45.0, -85.0),
    }
    for key, (wx, wz) in waystones.items():
        controls = DETOUR_SPUR_CONTROL_POINTS[key]
        tx, tz = _spur_tangent_at_endpoint(controls)
        # Step BACK from the waystone in -tangent direction to land on
        # the approach side.
        rx = wx - tx * BENCH_OFFSET_FROM_WAYSTONE
        rz = wz - tz * BENCH_OFFSET_FROM_WAYSTONE
        # Yaw so the bench's local +Y face direction equals (tx, tz) —
        # the sitter looks PAST the waystone toward the view. After a
        # yaw rotation about Z, local +Y rotates to (-sin(yaw), cos(yaw)),
        # so yaw = atan2(-tx, tz). Matches the convention used by
        # _perimeter_tangent_yaw_at_t below.
        yaw = math.atan2(-tx, tz)
        _build_bench(key, rx, rz, yaw, material)
        base_y = _lib.height_at(rx, rz)
        placed.append((key, rx, rz, base_y))
    return placed


def _place_signs(material):
    """Place 5 wooden trail signs at evenly-spaced t-values along the
    perimeter loop (t = 0.1, 0.3, 0.5, 0.7, 0.9). Each sign is yawed so
    its readable face points along the walking direction (CCW tangent).
    """
    signs = []
    t_values = [0.1, 0.3, 0.5, 0.7, 0.9]
    for i, t in enumerate(t_values):
        rx, rz = _sample_perimeter_at_t(t)
        # Offset the sign 1.0m perpendicular-outward from the trail so it
        # doesn't sit in the middle of the path. Perpendicular-outward
        # (radially away from origin) = the unit vector from origin to
        # (rx, rz).
        radial_len = math.hypot(rx, rz)
        if radial_len > 0.001:
            rx += (rx / radial_len) * 1.0
            rz += (rz / radial_len) * 1.0
        yaw = _perimeter_tangent_yaw_at_t(t)
        _build_sign(i + 1, rx, rz, yaw, material)
        signs.append((i + 1, rx, rz))
    return signs


def _place_boulder_clusters(sources, material):
    """Place 6 hand-positioned boulder clusters. Each cluster is 3-5
    boulders SHARING the existing boulder source meshes (variants 1-5
    from `sources["boulder"]`), placed within CLUSTER_RADIUS of the
    cluster centre on the terrain heightfield.

    Per-instance variant chosen via a seeded RNG (seed=12 — stable but
    distinct from the seed=11 regular boulder pass). Per-instance yaw
    rotation + scale 0.8-1.4. Rejects any candidate inside the cluster
    exclusion zone list (sections@4m, viewpoints@4m, lighthouse@8m, hero
    trees@3m, river@5m, trails@2m).

    Returns the total number of boulder instances placed across all
    clusters.
    """
    rng = random.Random(12)

    # Cluster-specific exclusion zones: looser 4m section buffer
    # (regular pass uses 6m). Everything else mirrors _build_exclusion_zones
    # so clusters don't poke into the river / trails / lighthouse / hero
    # trees.
    cluster_zones = []
    for (zx, zz, _zr) in SECTION_ZONES:
        cluster_zones.append((zx, zz, CLUSTER_SECTION_BUFFER))
    cluster_zones.extend(VIEWPOINT_ZONES)
    cluster_zones.append(LIGHTHOUSE_ZONE)
    for (rx, rz) in HERO_TREE_POSITIONS:
        cluster_zones.append((rx, rz, HERO_TREE_BUFFER))
    cluster_zones.extend(_collect_water_zones())
    cluster_zones.extend(_collect_trail_zones())

    total_placed = 0
    for ci, (cx, cz) in enumerate(BOULDER_CLUSTER_CENTRES):
        cluster_count = (CLUSTER_MIN_BOULDERS
                         + rng.randrange(CLUSTER_MAX_BOULDERS
                                         - CLUSTER_MIN_BOULDERS + 1))
        placed_in_cluster = 0
        attempt = 0
        # Try up to 4x the cluster count to avoid leaving a cluster empty
        # when a few candidates are rejected.
        while (placed_in_cluster < cluster_count
               and attempt < cluster_count * 4):
            attempt += 1
            angle = rng.random() * math.tau
            dist = rng.random() * CLUSTER_RADIUS
            bx = cx + math.cos(angle) * dist
            bz = cz + math.sin(angle) * dist
            if _is_excluded(bx, bz, cluster_zones):
                continue
            y = _lib.height_at(bx, bz)
            if y < WATER_REJECT_Y:
                continue
            variant = rng.randrange(len(sources["boulder"]))
            source_mesh = sources["boulder"][variant]
            yaw = rng.random() * math.tau
            scale = 0.8 + rng.random() * 0.6   # 0.8..1.4
            placed_in_cluster += 1
            _make_instance(
                name=f"cluster_{ci + 1}_boulder_{placed_in_cluster}",
                source_mesh=source_mesh,
                location=(bx, bz, y),
                rotation_z=yaw,
                scale=scale,
                collection_name=PROPS_CLUSTERS_COLLECTION,
                material=material,
            )
        total_placed += placed_in_cluster
    return total_placed


# ============================================================================
# Entry point
# ============================================================================


def main():
    # Clear the three foliage instance collections AND the three props
    # sub-collections FIRST so stale instance objects (which still reference
    # old source-mesh datablocks) are removed before we rebuild the sources.
    _lib.clear_collection(TREES_COLLECTION)
    _lib.clear_collection(HERO_TREES_COLLECTION)
    _lib.clear_collection(GROUND_COVER_COLLECTION)
    _lib.clear_collection(PROPS_BENCHES_COLLECTION)
    _lib.clear_collection(PROPS_SIGNS_COLLECTION)
    _lib.clear_collection(PROPS_CLUSTERS_COLLECTION)

    material = _lib.get_palette_material()

    # Build every source mesh once.
    sources = _build_all_sources()

    # Place a hidden placeholder object per source mesh so each datablock
    # has at least one Outliner entry. Phase 13 will detect shared mesh data
    # across the placeholder + instances and emit InstancedMesh.
    for i, mesh in enumerate(sources["pine"]):
        _attach_source_placeholder(
            mesh, f"tree_pine_var_{i + 1}_src", TREES_COLLECTION, material
        )
    for i, mesh in enumerate(sources["birch"]):
        _attach_source_placeholder(
            mesh, f"tree_birch_var_{i + 1}_src", TREES_COLLECTION, material
        )
    _attach_source_placeholder(
        sources["hero_pine"], "tree_hero_pine_src",
        HERO_TREES_COLLECTION, material,
    )
    for i, mesh in enumerate(sources["fern"]):
        _attach_source_placeholder(
            mesh, f"gc_fern_var_{i + 1}_src",
            GROUND_COVER_COLLECTION, material,
        )
    for i, mesh in enumerate(sources["flower"]):
        _attach_source_placeholder(
            mesh, f"gc_flower_var_{i + 1}_src",
            GROUND_COVER_COLLECTION, material,
        )
    for i, mesh in enumerate(sources["boulder"]):
        _attach_source_placeholder(
            mesh, f"gc_boulder_var_{i + 1}_src",
            GROUND_COVER_COLLECTION, material,
        )
    for i, mesh in enumerate(sources["bush"]):
        _attach_source_placeholder(
            mesh, f"gc_bush_var_{i + 1}_src",
            GROUND_COVER_COLLECTION, material,
        )

    # Build the exclusion zone list ONCE.
    zones = _build_exclusion_zones()

    # Hero trees first so subsequent placements avoid them.
    heroes = _place_hero_trees(sources, material)
    hero_zones = [(rx, rz, HERO_TREE_BUFFER) for (_, rx, rz, _) in heroes]
    # Insert hero buffers RIGHT AFTER section zones so the short-circuit
    # match-rate stays high.
    zones = SECTION_ZONES + hero_zones + zones[len(SECTION_ZONES):]

    # Hero tree colliders.
    for (name, rx, rz, by) in heroes:
        _build_hero_tree_collider(material, name, rx, rz, by)

    # Hero refs.
    for i, (_, rx, rz, by) in enumerate(heroes):
        _lib.ref_empty(
            f"refHeroTree_{i + 1}",
            (rx, rz, by + HERO_TREE_HEIGHT * 0.5),
            radius=0.5,
        )

    rng = random.Random(11)

    pine_count = _place_pines(rng, sources, zones, material)
    birch_count = _place_birches(rng, sources, zones, material)

    fern_count = _place_ground_cover(
        rng, sources, zones, material,
        category="fern",
        target_count=TARGET_FERN_COUNT,
        ne_weight=1.5, sw_weight=0.5,
        name_prefix="gc_fern_inst",
    )
    flower_count = _place_ground_cover(
        rng, sources, zones, material,
        category="flower",
        target_count=TARGET_FLOWER_COUNT,
        ne_weight=0.5, sw_weight=1.5,
        name_prefix="gc_flower_inst",
    )
    boulder_count = _place_ground_cover(
        rng, sources, zones, material,
        category="boulder",
        target_count=TARGET_BOULDER_COUNT,
        ne_weight=1.0, sw_weight=1.0,
        name_prefix="gc_boulder_inst",
    )
    bush_count = _place_ground_cover(
        rng, sources, zones, material,
        category="bush",
        target_count=TARGET_BUSH_COUNT,
        ne_weight=1.0, sw_weight=1.0,
        name_prefix="gc_bush_inst",
    )

    # --- Props pass: benches + signs + boulder clusters. ---
    benches = _place_benches(material)
    signs = _place_signs(material)
    cluster_boulder_count = _place_boulder_clusters(sources, material)

    # Bench refs (for future "sit" interactions). No refs for signs or
    # boulder clusters.
    for key, rx, rz, base_y in benches:
        _lib.ref_empty(
            f"refBench_{key}",
            (rx, rz, base_y + BENCH_TOP_Y),
            radius=0.3,
        )

    blend_path = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "world.blend"))
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    print(
        f"{_lib.LOG_PREFIX}[phase-11] OK — foliage: "
        f"{pine_count} pines + {birch_count} birches + "
        f"{len(heroes)} hero + {fern_count} ferns + "
        f"{flower_count} flowers + {boulder_count} boulders + "
        f"{bush_count} bushes, "
        f"{len(heroes)} colliders, {len(heroes)} refs | "
        f"props: {len(benches)} benches + {len(signs)} signs + "
        f"{len(BOULDER_CLUSTER_CENTRES)} boulder clusters "
        f"({cluster_boulder_count} boulder instances), "
        f"{len(benches)} colliders, {len(benches)} refs"
    )
    print(f"{_lib.LOG_PREFIX}[phase-11] saved -> {blend_path}")


if __name__ == "__main__":
    main()
