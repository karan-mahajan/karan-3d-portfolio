"""
Phase 6: Experience cairn trail (N cardinal).

What this produces (after Run Script + save):
- `sections/experience` collection populated with these visible mesh groups:
    * `experience_trail`               - one ribbon mesh, ~80 samples along a
                                         Catmull-Rom curve from (0, +4) up the
                                         NE ridge to (+15, +95). 1.2m wide,
                                         three strips: 0.2m sand_gravel left,
                                         0.8m dirt_path centre, 0.2m
                                         sand_gravel right. Each vertex's
                                         height samples height_at + 0.02m.
    * `experience_stepping_stone_1..5` - flat cuboid stones embedded into the
                                         steepest section of the trail
                                         (t = 0.4..0.6). Tops sit ~0.08m
                                         above the trail ribbon. Walk-through.
    * `experience_cairn_1..7`          - stacks of 3-5 carved stones each.
                                         Stack heights vary 0.8-1.8m. Stones
                                         get slight horizontal jitter + yaw
                                         so each cairn looks hand-stacked.
                                         One arbitrary middle-stone face is
                                         repainted sand_gravel per cairn to
                                         suggest a carved/inset panel. The
                                         entire stack lives in a single
                                         bmesh object per cairn so the bbox
                                         collider can size to the whole stack.
    * `experience_cairn_lantern_N_body`     - copper cylinder atop each cairn.
    * `experience_cairn_lantern_N_emissive` - warm cap above each body. The
                                              `_emissive` suffix is the
                                              runtime contract (precedent:
                                              `hearth_embers_emissive`,
                                              `cupola_lantern_emissive`).
- Colliders (7; hidden via hide_viewport+hide_render, palette material
  attached for consistency):
    * `cuboid_cairn_1..7`              - each sized to its visible cairn's
                                         world-space bbox.
    * No collider on the trail ribbon, stepping stones, or lanterns - the
      player walks on the terrain heightfield, lanterns sit above head
      height, and stepping stones read as visual embellishment.
- 11 ref empties in `refs`:
    `refZoneBounding_experience` (radius 14, at section root),
    `refZoneFrustum_experience`  (radius 11, at section root),
    `refInteractivePoint_experience` (radius 0.5, at top of cairn_1 - the
        cairn closest to spawn),
    `refCairnLantern_1..7` (radius 0.3, each at its lantern cap centre),
    `refRespawn_experience` (radius 0.5, at section root).

Trail orientation (single source of truth for this script):
- Trail starts at (0, +4) runtime - just N of spawn, where Phase 9's
  timber bridge will sit - and winds NE to (+15, +95) runtime, the
  summit lookout on Phase 2's NE ridge (terrain rises to ~+12m there).
- 7 cubic-Hermite (Catmull-Rom) control points; ~80 sampled points
  along the curve give a smooth ribbon hugging the heightfield.
- Cairns spaced from t=0.10 to t=0.95 along the curve; cairn_1 is the
  one closest to spawn (lowest elevation, first to be encountered).

Coordinate convention: authored in Blender Z-up. Runtime (x, y, z) maps
to Blender (x, z, y). Every Y position samples `_lib.height_at(x, z)`.

Idempotent: re-running clears the `sections/experience` collection first.

How to run:
  1. Open tools/blender/world.blend in Blender 4.2+.
  2. Scripting workspace -> Text Editor -> Open -> phase-06-experience-cairns.py.
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


# Mirror Phase 0..5's _script_dir() - Blender's Text Editor sets __file__
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
import _palette   # noqa: E402


COLLECTION = "sections/experience"

# Section root (runtime coords). The plan locks midpoint of the trail at
# x=0, z=+70. Phase 2's NE ridge lifts terrain here.
SECTION_RUNTIME_X = 0.0
SECTION_RUNTIME_Z = 70.0

# Trail control points in runtime (x, z). Start at +4 (just N of spawn,
# where Phase 9's timber bridge will land), end at (+15, +95) on the
# summit ridge. Gentle east curl so the trail winds rather than going
# straight. Order matters - Catmull-Rom sampler walks these.
TRAIL_CONTROL_POINTS = [
    (0.0, 4.0),
    (-2.0, 20.0),
    (1.0, 35.0),
    (5.0, 50.0),
    (8.0, 65.0),
    (12.0, 80.0),
    (15.0, 95.0),
]

# Number of sample points along the curve. ~80 keeps the ribbon smooth
# without bloating vert counts.
TRAIL_SAMPLE_COUNT = 80

# Ribbon strip widths (perpendicular to the curve tangent). 0.2 + 0.8 +
# 0.2 = 1.2m total per spec.
TRAIL_STRIP_WIDTHS = (0.2, 0.8, 0.2)
TRAIL_STRIP_KEYS = ("sand_gravel", "dirt_path", "sand_gravel")
TRAIL_TOTAL_WIDTH = sum(TRAIL_STRIP_WIDTHS)
TRAIL_LIFT = 0.02   # raise above heightfield to avoid z-fighting

# Stepping stones at the steepest mid-section (t = 0.4..0.6).
STEPPING_STONE_COUNT = 5
STEPPING_STONE_T_START = 0.4
STEPPING_STONE_T_END = 0.6
STEPPING_STONE_FOOTPRINT = (0.50, 0.40)   # x, y in meters (pre-rotation)
STEPPING_STONE_HEIGHT = 0.12
STEPPING_STONE_LIFT = 0.08  # tops sit this high above trail ribbon

# 7 cairns evenly spaced from t=0.10 to t=0.95.
CAIRN_COUNT = 7
CAIRN_T_START = 0.10
CAIRN_T_END = 0.95
# Stone count per cairn - hand-picked to vary silhouette along the trail.
# Index = cairn index 0..6.
CAIRN_STONE_COUNTS = (3, 4, 5, 4, 3, 4, 3)
CAIRN_STONE_FOOTPRINT_X = 0.35
CAIRN_STONE_FOOTPRINT_Y = 0.30
CAIRN_STONE_HEIGHT_MIN = 0.20
CAIRN_STONE_HEIGHT_MAX = 0.35
CAIRN_STONE_JITTER = 0.03           # max horizontal jitter per stone in m
CAIRN_STONE_YAW_DEG = 10.0          # max yaw per stone

# Lantern dimensions per cairn (atop the topmost stone).
LANTERN_BODY_RADIUS = 0.10
LANTERN_BODY_HEIGHT = 0.10
LANTERN_CAP_HALF_XY = 0.10
LANTERN_CAP_HEIGHT = 0.06


# ============================================================================
# Curve sampling
# ============================================================================


def _catmull_rom(p0, p1, p2, p3, t):
    """Standard Catmull-Rom basis (tau=0.5) for one segment between p1, p2.

    Each `p*` is a 2-tuple (x, z) in runtime coords. Returns (x, z) at
    parameter t in [0, 1].
    """
    t2 = t * t
    t3 = t2 * t
    a = -0.5 * t3 + t2 - 0.5 * t
    b = 1.5 * t3 - 2.5 * t2 + 1.0
    c = -1.5 * t3 + 2.0 * t2 + 0.5 * t
    d = 0.5 * t3 - 0.5 * t2
    x = a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0]
    z = a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]
    return (x, z)


def _sample_trail(control_points, sample_count):
    """Sample `sample_count` points along the Catmull-Rom curve through
    `control_points`. Endpoints are duplicated as virtual control points
    so the curve passes through the first and last actual control points.

    Returns a list of (x, z) tuples in runtime XZ. Caller handles height.
    """
    pts = [control_points[0]] + list(control_points) + [control_points[-1]]
    segments = len(pts) - 3   # number of CR segments
    samples = []
    for i in range(sample_count):
        u = i / (sample_count - 1)
        seg_f = u * segments
        seg_i = int(seg_f)
        if seg_i >= segments:
            # Clamp the right endpoint to the final control point exactly.
            seg_i = segments - 1
            local_t = 1.0
        else:
            local_t = seg_f - seg_i
        p0 = pts[seg_i]
        p1 = pts[seg_i + 1]
        p2 = pts[seg_i + 2]
        p3 = pts[seg_i + 3]
        samples.append(_catmull_rom(p0, p1, p2, p3, local_t))
    return samples


def _sample_at_t(control_points, t):
    """Sample the trail at a specific t in [0, 1]. Same basis as
    `_sample_trail`. Returns (x, z) in runtime."""
    pts = [control_points[0]] + list(control_points) + [control_points[-1]]
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
    return _catmull_rom(p0, p1, p2, p3, local_t)


# ============================================================================
# Trail ribbon
# ============================================================================


def _build_trail(material):
    """One ribbon mesh, ~80 samples along the curve. Each sample emits a
    cross-tangent of 4 verts (1 per strip boundary). Quads between
    consecutive samples form the three strip bands.

    The ribbon is authored entirely in world Blender coords (no rotation
    on the object) so the curve's tangent is computed in the world XY
    plane. The Z of each vertex is sampled via height_at + lift, giving a
    ribbon that drapes the terrain rather than a flat plane.
    """
    samples = _sample_trail(TRAIL_CONTROL_POINTS, TRAIL_SAMPLE_COUNT)

    # Pre-compute cumulative offsets across the ribbon width: 4 boundaries
    # for 3 strips. Centred so the dirt centre straddles the curve.
    offsets = [-TRAIL_TOTAL_WIDTH * 0.5]
    for w in TRAIL_STRIP_WIDTHS:
        offsets.append(offsets[-1] + w)

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)

    # For each sample, compute tangent (forward) and perpendicular in XY,
    # then emit 4 verts across the width. Tangent at endpoints uses the
    # next/prev sample; interior tangents are the central difference.
    rings = []   # list of 4-vert rings, one per sample
    for i, (rx, rz) in enumerate(samples):
        if i == 0:
            nx, nz = samples[i + 1]
            tx, tz = nx - rx, nz - rz
        elif i == len(samples) - 1:
            px, pz = samples[i - 1]
            tx, tz = rx - px, rz - pz
        else:
            nx, nz = samples[i + 1]
            px, pz = samples[i - 1]
            tx, tz = nx - px, nz - pz
        length = math.hypot(tx, tz)
        if length == 0.0:
            tx, tz = 1.0, 0.0
            length = 1.0
        tx /= length
        tz /= length
        # Perpendicular in XY plane (Blender X, Y): rotate tangent +90 deg
        # so the "left edge" sits on one side consistently.
        perp_x = -tz
        perp_y = tx

        ring = []
        for offset in offsets:
            vx = rx + perp_x * offset
            vy = rz + perp_y * offset
            vz = _lib.height_at(vx, vy) + TRAIL_LIFT
            ring.append(bm.verts.new((vx, vy, vz)))
        rings.append(ring)

    # Build quad strips between consecutive rings. 3 strips per pair.
    for i in range(len(rings) - 1):
        lower = rings[i]
        upper = rings[i + 1]
        for s in range(3):
            face = bm.faces.new((lower[s], upper[s],
                                 upper[s + 1], lower[s + 1]))
            _lib.paint_face(face, uv, TRAIL_STRIP_KEYS[s])

    # Object origin at (0, 0, 0) since all verts are in world coords.
    trail = _lib.bm_finalize_to_object(
        bm,
        mesh_name="experience_trail_mesh",
        obj_name="experience_trail",
        location=(0.0, 0.0, 0.0),
        collection_name=COLLECTION,
        material=material,
    )
    return trail, samples


# ============================================================================
# Stepping stones
# ============================================================================


def _build_stepping_stones(material):
    """5 flat stones along the steepest mid-section of the curve. Each
    cuboid is built in its own bmesh so we can rotate it to align with the
    local tangent. Stones embed slightly into the trail; tops sit ~0.08m
    above the ribbon surface."""
    rng = random.Random(6)
    objs = []
    for i in range(STEPPING_STONE_COUNT):
        # Even spacing in [start, end].
        t = STEPPING_STONE_T_START + (
            (STEPPING_STONE_T_END - STEPPING_STONE_T_START)
            * (i / (STEPPING_STONE_COUNT - 1))
        )
        rx, rz = _sample_at_t(TRAIL_CONTROL_POINTS, t)

        # Yaw to align the stone's long axis with the trail tangent.
        eps = 0.01
        nx, nz = _sample_at_t(
            TRAIL_CONTROL_POINTS, min(1.0, t + eps)
        )
        px, pz = _sample_at_t(
            TRAIL_CONTROL_POINTS, max(0.0, t - eps)
        )
        yaw = math.atan2(nz - pz, nx - px)

        # ±10% size variation; stable across runs via seeded RNG.
        scale = 1.0 + rng.uniform(-0.10, 0.10)
        hx = (STEPPING_STONE_FOOTPRINT[0] * scale) * 0.5
        hy = (STEPPING_STONE_FOOTPRINT[1] * scale) * 0.5
        hz = STEPPING_STONE_HEIGHT * 0.5

        # Place stone so its top sits STEPPING_STONE_LIFT above the trail
        # surface at that sample. Trail surface = height_at + TRAIL_LIFT.
        trail_surface_z = _lib.height_at(rx, rz) + TRAIL_LIFT
        top_z = trail_surface_z + STEPPING_STONE_LIFT
        centre_z = top_z - hz

        bm = bmesh.new()
        uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
        _lib.bm_add_cuboid(
            bm, uv,
            center=(0.0, 0.0, 0.0),
            half_extents=(hx, hy, hz),
            color_key="rock_mid",
        )
        stone = _lib.bm_finalize_to_object(
            bm,
            mesh_name=f"experience_stepping_stone_{i + 1}_mesh",
            obj_name=f"experience_stepping_stone_{i + 1}",
            location=(rx, rz, centre_z),
            collection_name=COLLECTION,
            material=material,
            rotation_euler=(0.0, 0.0, yaw),
        )
        objs.append(stone)
    return objs


# ============================================================================
# Cairns
# ============================================================================


def _build_cairn(material, cairn_index, t):
    """Build one cairn as a single bmesh with N stacked cuboid stones.

    Returns (cairn_obj, lantern_top_world_xyz) — lantern goes on top of
    the tallest (topmost) stone.

    Each stone is appended to the same bmesh with a small horizontal
    jitter and yaw per stone. The middle stone gets one face repainted
    sand_gravel to suggest a carved/inset panel. The cairn base sits on
    the heightfield at the cairn's runtime (x, z); we sample height_at
    separately because the trail ribbon is +0.02 above terrain and we
    want the stones grounded.
    """
    rx, rz = _sample_at_t(TRAIL_CONTROL_POINTS, t)
    base_z = _lib.height_at(rx, rz)

    rng = random.Random(60 + cairn_index)   # stable per cairn
    stone_count = CAIRN_STONE_COUNTS[cairn_index]
    middle_idx = stone_count // 2

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)

    current_z = base_z
    top_local_xy = (0.0, 0.0)     # last stone's local-xy jitter offset
    top_z = base_z
    for s in range(stone_count):
        stone_h = rng.uniform(CAIRN_STONE_HEIGHT_MIN, CAIRN_STONE_HEIGHT_MAX)
        jitter_x = rng.uniform(-CAIRN_STONE_JITTER, CAIRN_STONE_JITTER)
        jitter_y = rng.uniform(-CAIRN_STONE_JITTER, CAIRN_STONE_JITTER)
        yaw = math.radians(rng.uniform(-CAIRN_STONE_YAW_DEG,
                                       CAIRN_STONE_YAW_DEG))

        # Build the stone's verts in local space (centred at origin), then
        # rotate by yaw and translate into the cairn's local frame
        # (cairn origin will be at (rx, rz, 0); we add Z = current_z + h/2
        # for each stone here).
        hx = CAIRN_STONE_FOOTPRINT_X * 0.5
        hy = CAIRN_STONE_FOOTPRINT_Y * 0.5
        hz = stone_h * 0.5

        local_corners = [
            (-hx, -hy, -hz),
            (+hx, -hy, -hz),
            (+hx, +hy, -hz),
            (-hx, +hy, -hz),
            (-hx, -hy, +hz),
            (+hx, -hy, +hz),
            (+hx, +hy, +hz),
            (-hx, +hy, +hz),
        ]
        cosy = math.cos(yaw)
        siny = math.sin(yaw)
        centre_z = current_z + hz
        stone_verts = []
        for cx_l, cy_l, cz_l in local_corners:
            wx = cosy * cx_l - siny * cy_l + jitter_x
            wy = siny * cx_l + cosy * cy_l + jitter_y
            wz = cz_l + centre_z
            stone_verts.append(bm.verts.new((wx, wy, wz)))

        # Face indices match _lib.bm_add_cuboid's order:
        # [bottom, top, -Y, +Y, -X, +X].
        quad_indices = [
            (0, 3, 2, 1),
            (4, 5, 6, 7),
            (0, 1, 5, 4),
            (3, 7, 6, 2),
            (0, 4, 7, 3),
            (1, 2, 6, 5),
        ]
        stone_faces = []
        for idx in quad_indices:
            face = bm.faces.new((stone_verts[idx[0]], stone_verts[idx[1]],
                                 stone_verts[idx[2]], stone_verts[idx[3]]))
            stone_faces.append(face)
        for face in stone_faces:
            _lib.paint_face(face, uv, "rock_mid")

        # Carved/inset panel on the middle stone's +X face. Picking +X is
        # deterministic; the per-cairn yaw randomises which world direction
        # this face ends up pointing.
        if s == middle_idx:
            _lib.paint_face(stone_faces[5], uv, "sand_gravel")

        current_z = centre_z + hz
        if s == stone_count - 1:
            top_z = current_z
            top_local_xy = (jitter_x, jitter_y)

    cairn = _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"experience_cairn_{cairn_index + 1}_mesh",
        obj_name=f"experience_cairn_{cairn_index + 1}",
        location=(rx, rz, 0.0),
        collection_name=COLLECTION,
        material=material,
    )

    # Lantern anchor in world coords: cairn origin + top-stone jitter +
    # top Z. Caller uses this to place the lantern and its ref.
    lantern_anchor = (
        rx + top_local_xy[0],
        rz + top_local_xy[1],
        top_z,
    )
    return cairn, lantern_anchor


def _build_lantern(material, cairn_index, anchor):
    """Lantern atop one cairn: copper body cylinder + warm emissive cap
    cube. Returns (body_obj, emissive_obj, emissive_centre_xyz)."""
    ax, ay, az = anchor

    body_centre_z = az + LANTERN_BODY_HEIGHT * 0.5
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cylinder(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        radius=LANTERN_BODY_RADIUS, height=LANTERN_BODY_HEIGHT,
        color_key="wood_lantern_body",
        segments=12,
    )
    body = _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"experience_cairn_lantern_{cairn_index + 1}_body_mesh",
        obj_name=f"experience_cairn_lantern_{cairn_index + 1}_body",
        location=(ax, ay, body_centre_z),
        collection_name=COLLECTION,
        material=material,
    )

    cap_centre_z = az + LANTERN_BODY_HEIGHT + LANTERN_CAP_HEIGHT * 0.5
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(LANTERN_CAP_HALF_XY, LANTERN_CAP_HALF_XY,
                      LANTERN_CAP_HEIGHT * 0.5),
        color_key="lantern_warm",
    )
    emissive = _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"experience_cairn_lantern_{cairn_index + 1}_emissive_mesh",
        obj_name=f"experience_cairn_lantern_{cairn_index + 1}_emissive",
        location=(ax, ay, cap_centre_z),
        collection_name=COLLECTION,
        material=material,
    )

    return body, emissive, (ax, ay, cap_centre_z)


# ============================================================================
# Colliders
# ============================================================================


def _world_bbox(obj):
    """Return (min_corner, max_corner) Vectors of `obj` in world space.
    Mirrors phase-05's helper - matches Three.js Box3().setFromObject()."""
    mw = obj.matrix_world
    corners = [mw @ Vector(c) for c in obj.bound_box]
    minc = Vector((min(c.x for c in corners),
                   min(c.y for c in corners),
                   min(c.z for c in corners)))
    maxc = Vector((max(c.x for c in corners),
                   max(c.y for c in corners),
                   max(c.z for c in corners)))
    return minc, maxc


def _build_cairn_collider(material, cairn_obj, cairn_index):
    """cuboid_cairn_N sized to the visible cairn's world-space bbox.
    Centre = midpoint of bbox; half-extents = bbox size / 2."""
    minc, maxc = _world_bbox(cairn_obj)
    size = maxc - minc
    centre = (minc + maxc) * 0.5

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(size.x * 0.5, size.y * 0.5, size.z * 0.5),
        color_key="rock_mid",
    )
    return _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"cuboid_cairn_{cairn_index + 1}_mesh",
        obj_name=f"cuboid_cairn_{cairn_index + 1}",
        location=(centre.x, centre.y, centre.z),
        collection_name=COLLECTION,
        material=material,
        hide=True,
    )


# ============================================================================
# Refs
# ============================================================================


def _place_refs(cairn_lantern_anchors, first_cairn_top_z):
    """11 ref empties for the experience section. Returns the count."""
    cx = SECTION_RUNTIME_X
    cy = SECTION_RUNTIME_Z
    ground_z = _lib.height_at(cx, cy)
    section_loc = (cx, cy, ground_z)

    count = 0

    _lib.ref_empty(
        "refZoneBounding_experience",
        section_loc,
        radius=14.0,
    )
    count += 1
    _lib.ref_empty(
        "refZoneFrustum_experience",
        section_loc,
        radius=11.0,
    )
    count += 1

    # Interactive point at the top of cairn_1 (first cairn the player
    # meets walking up the trail from spawn).
    first_anchor = cairn_lantern_anchors[0]
    interactive_z = max(first_cairn_top_z, first_anchor[2])
    _lib.ref_empty(
        "refInteractivePoint_experience",
        (first_anchor[0], first_anchor[1], interactive_z),
        radius=0.5,
    )
    count += 1

    for i, anchor in enumerate(cairn_lantern_anchors):
        _lib.ref_empty(
            f"refCairnLantern_{i + 1}",
            anchor,
            radius=0.3,
        )
        count += 1

    _lib.ref_empty(
        "refRespawn_experience",
        section_loc,
        radius=0.5,
    )
    count += 1

    return count


# ============================================================================
# Entry point
# ============================================================================


def main():
    _lib.clear_collection("sections/experience")

    material = _lib.get_palette_material()

    _build_trail(material)
    _build_stepping_stones(material)

    # Even spacing of 7 cairns along the curve.
    cairn_ts = [
        CAIRN_T_START
        + (CAIRN_T_END - CAIRN_T_START) * (i / (CAIRN_COUNT - 1))
        for i in range(CAIRN_COUNT)
    ]

    cairn_objs = []
    cairn_lantern_anchors = []
    cairn_top_zs = []
    for i, t in enumerate(cairn_ts):
        cairn_obj, lantern_anchor = _build_cairn(material, i, t)
        cairn_objs.append(cairn_obj)
        cairn_lantern_anchors.append(lantern_anchor)
        cairn_top_zs.append(lantern_anchor[2])

    lantern_caps = []
    for i, anchor in enumerate(cairn_lantern_anchors):
        _, emissive, cap_centre = _build_lantern(material, i, anchor)
        lantern_caps.append((emissive, cap_centre))

    for i, cairn_obj in enumerate(cairn_objs):
        _build_cairn_collider(material, cairn_obj, i)

    # Use cap centres for the lantern refs (anchor = cap centre).
    cap_anchors = [cc for _, cc in lantern_caps]
    ref_count = _place_refs(cap_anchors, cairn_top_zs[0])

    blend_path = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "world.blend"))
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    print(
        f"{_lib.LOG_PREFIX}[phase-06] OK - experience: cairn trail, "
        f"{len(cairn_objs)} cairns, {len(cairn_objs)} colliders, "
        f"{ref_count} refs"
    )
    print(f"{_lib.LOG_PREFIX}[phase-06] saved -> {blend_path}")


if __name__ == "__main__":
    main()
