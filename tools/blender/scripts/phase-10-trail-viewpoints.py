"""
Phase 10: Hiking trail (perimeter loop + 3 viewpoint detours) + waystones.

What this produces (after Run Script + save):
- `trail/perimeter` collection:
    * `trail_perimeter`       - one closed-loop ribbon mesh sampled at 180
                                points around a 12-control-point Catmull-Rom
                                at ~80m radius from spawn. Routes between the
                                70m section anchors and the 90m plateau edge,
                                so all 4 cardinal sections sit inside the
                                loop. 1.2m wide three-strip ribbon:
                                0.2 `sand_gravel` left, 0.8 `dirt_path`
                                centre, 0.2 `sand_gravel` right. Each vertex
                                Y samples `height_at(x, z) + 0.02m`.
- `trail/detour_nw` collection:
    * `trail_detour_nw`       - spur branching off the perimeter near
                                (-60, +60) and ending at the cliff edge
                                (-76, +45), between Contact and Experience.
                                Same 1.2m three-strip ribbon, ~35 samples.
- `trail/detour_summit` collection:
    * `trail_detour_summit`   - spur branching off the perimeter near
                                (+30, +70) and climbing to the summit
                                (+15, +95) — the same endpoint as the Phase 6
                                cairn trail terminus. Same ribbon recipe.
- `trail/detour_se` collection:
    * `trail_detour_se`       - spur branching off the perimeter near
                                (+60, -60) and ending in the SE meadow at
                                (+45, -85). Same ribbon recipe.
- `viewpoints` collection:
    * `waystone_nw`           - carved standing stone at (-76, +45).
    * `waystone_summit`       - carved standing stone at (+15, +95).
    * `waystone_se`           - carved standing stone at (+45, -85).
                                Each is 0.4 x 0.4m footprint x 0.8m tall,
                                palette `rock_mid` body with ONE vertical
                                face repainted `sand_gravel` for the carved
                                emblem. The carved face is the one whose
                                outward normal most opposes the spur
                                tangent at the endpoint, so it faces a
                                player walking up the spur.
    * `cuboid_waystone_*`     - 3 hidden cuboid colliders, each sized to its
                                waystone bbox (0.2, 0.4, 0.2 half-extents in
                                Blender axes order, hy = 0.4 = height/2).
- 3 ref empties in `refs`:
    * `refViewpoint_nw`       - at waystone_nw base, radius 0.5, userData
                                { "viewpoint": "nw" }.
    * `refViewpoint_summit`   - at waystone_summit base, radius 0.5, userData
                                { "viewpoint": "summit" }.
    * `refViewpoint_se`       - at waystone_se base, radius 0.5, userData
                                { "viewpoint": "se" }.

Coordinate convention: authored in Blender Z-up. Runtime (x, y, z) maps to
Blender (x, z, y). Every trail vertex Y samples `_lib.height_at(x, z)`.

Idempotent: re-running clears `trail/perimeter`, `trail/detour_nw`,
`trail/detour_summit`, `trail/detour_se`, and `viewpoints` first.

How to run:
  1. Open tools/blender/world.blend in Blender 4.2+.
  2. Scripting workspace -> Text Editor -> Open -> phase-10-trail-viewpoints.py.
  3. Run Script (Alt+P).
  4. Script saves world.blend automatically (wm.save_as_mainfile).
"""

import os
import sys
import math

import bpy
import bmesh
from mathutils import Vector


# Mirror Phase 0..9's _script_dir() - Blender's Text Editor sets __file__
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

PERIMETER_COLLECTION = "trail/perimeter"
DETOUR_NW_COLLECTION = "trail/detour_nw"
DETOUR_SUMMIT_COLLECTION = "trail/detour_summit"
DETOUR_SE_COLLECTION = "trail/detour_se"
VIEWPOINTS_COLLECTION = "viewpoints"

# Perimeter loop: 12 control points around the plateau at ~80m radius.
# Routes outside the 70m section anchors and inside the 90m plateau edge.
# Order is CCW starting from due east.
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
PERIMETER_SAMPLE_COUNT = 180

# Detour control points (runtime x, z). First point of each branches off the
# perimeter near that perimeter control; last point is the viewpoint anchor.
DETOUR_NW_CONTROL_POINTS = [
    (-60.0,  60.0),
    (-65.0,  55.0),
    (-70.0,  50.0),
    (-76.0,  45.0),
]
DETOUR_SUMMIT_CONTROL_POINTS = [
    ( 30.0,  70.0),
    ( 25.0,  80.0),
    ( 18.0,  88.0),
    ( 15.0,  95.0),
]
DETOUR_SE_CONTROL_POINTS = [
    ( 60.0, -60.0),
    ( 55.0, -68.0),
    ( 50.0, -77.0),
    ( 45.0, -85.0),
]
DETOUR_SAMPLE_COUNT = 35

# Shared ribbon recipe — same as Phase 6's experience trail.
TRAIL_STRIP_WIDTHS = (0.2, 0.8, 0.2)
TRAIL_STRIP_KEYS = ("sand_gravel", "dirt_path", "sand_gravel")
TRAIL_TOTAL_WIDTH = sum(TRAIL_STRIP_WIDTHS)
TRAIL_LIFT = 0.02

# Waystone: 0.4 x 0.4m footprint x 0.8m tall standing stone.
WAYSTONE_HALF_X = 0.2
WAYSTONE_HALF_Y = 0.2
WAYSTONE_HEIGHT = 0.8
WAYSTONE_HALF_HEIGHT = WAYSTONE_HEIGHT * 0.5


# ============================================================================
# Curve sampling — Catmull-Rom (tau=0.5).
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


def _sample_open_curve(control_points, sample_count):
    """Sample `sample_count` points along an open Catmull-Rom curve.

    First / last control points are duplicated as virtual endpoints so the
    curve passes through them. Returns list of (x, z).
    """
    pts = [control_points[0]] + list(control_points) + [control_points[-1]]
    segments = len(pts) - 3
    samples = []
    for i in range(sample_count):
        u = i / (sample_count - 1)
        seg_f = u * segments
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
        samples.append(_catmull_rom(p0, p1, p2, p3, local_t))
    return samples


def _sample_closed_curve(control_points, sample_count):
    """Sample `sample_count` points around a CLOSED Catmull-Rom loop.

    Wrap-around trick: the last control acts as the virtual-before-first and
    the first acts as the virtual-after-last (also wrap the second so we have
    N segments covering the full loop). Each of the N controls becomes the
    start of a segment, giving a seamless closed curve. The last sample lands
    back at the first control point.
    """
    n = len(control_points)
    pts = (
        [control_points[-1]]
        + list(control_points)
        + [control_points[0], control_points[1]]
    )
    segments = n   # one CR segment per control point (closed loop)
    samples = []
    for i in range(sample_count):
        u = i / sample_count   # 0..(sample_count-1)/sample_count
        seg_f = u * segments
        seg_i = int(seg_f) % segments
        local_t = seg_f - int(seg_f)
        p0 = pts[seg_i]
        p1 = pts[seg_i + 1]
        p2 = pts[seg_i + 2]
        p3 = pts[seg_i + 3]
        samples.append(_catmull_rom(p0, p1, p2, p3, local_t))
    return samples


def _tangent_at_open_end(control_points, eps=0.005):
    """Unit tangent at the END (t=1) of an open Catmull-Rom curve in runtime
    XZ. Backward central difference using t=1-eps and t=1 so we get the
    direction the player is moving as they reach the endpoint."""
    p_a = _sample_open_at_t(control_points, max(0.0, 1.0 - eps))
    p_b = _sample_open_at_t(control_points, 1.0)
    tx = p_b[0] - p_a[0]
    tz = p_b[1] - p_a[1]
    length = math.hypot(tx, tz)
    if length == 0.0:
        return (1.0, 0.0)
    return (tx / length, tz / length)


def _sample_open_at_t(control_points, t):
    """Sample one (x, z) at parameter t in [0, 1] on the open curve."""
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
# Ribbon builder — shared by perimeter + 3 detours.
# ============================================================================


def _build_open_ribbon(samples, mesh_name, obj_name, collection_name,
                       material):
    """Three-strip ribbon for an OPEN curve sample list. Each sample emits a
    4-vert tangent ring (sand_left | dirt_centre | sand_right). Quads
    between consecutive rings form the three strips."""
    offsets = [-TRAIL_TOTAL_WIDTH * 0.5]
    for w in TRAIL_STRIP_WIDTHS:
        offsets.append(offsets[-1] + w)

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)

    rings = []
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
        perp_x = -tz
        perp_y = tx

        ring = []
        for offset in offsets:
            vx = rx + perp_x * offset
            vy = rz + perp_y * offset
            vz = _lib.height_at(vx, vy) + TRAIL_LIFT
            ring.append(bm.verts.new((vx, vy, vz)))
        rings.append(ring)

    for i in range(len(rings) - 1):
        lower = rings[i]
        upper = rings[i + 1]
        for s in range(3):
            face = bm.faces.new((lower[s], upper[s],
                                 upper[s + 1], lower[s + 1]))
            _lib.paint_face(face, uv, TRAIL_STRIP_KEYS[s])

    return _lib.bm_finalize_to_object(
        bm,
        mesh_name=mesh_name,
        obj_name=obj_name,
        location=(0.0, 0.0, 0.0),
        collection_name=collection_name,
        material=material,
    )


def _build_closed_ribbon(samples, mesh_name, obj_name, collection_name,
                         material):
    """Three-strip ribbon for a CLOSED curve sample list. Tangents use the
    cyclic neighbours of every sample (no endpoint special-case), and the
    final quad ring connects back to the first ring so there's no seam."""
    offsets = [-TRAIL_TOTAL_WIDTH * 0.5]
    for w in TRAIL_STRIP_WIDTHS:
        offsets.append(offsets[-1] + w)

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)

    n = len(samples)
    rings = []
    for i in range(n):
        rx, rz = samples[i]
        nx, nz = samples[(i + 1) % n]
        px, pz = samples[(i - 1) % n]
        tx, tz = nx - px, nz - pz
        length = math.hypot(tx, tz)
        if length == 0.0:
            tx, tz = 1.0, 0.0
            length = 1.0
        tx /= length
        tz /= length
        perp_x = -tz
        perp_y = tx

        ring = []
        for offset in offsets:
            vx = rx + perp_x * offset
            vy = rz + perp_y * offset
            vz = _lib.height_at(vx, vy) + TRAIL_LIFT
            ring.append(bm.verts.new((vx, vy, vz)))
        rings.append(ring)

    for i in range(n):
        lower = rings[i]
        upper = rings[(i + 1) % n]
        for s in range(3):
            face = bm.faces.new((lower[s], upper[s],
                                 upper[s + 1], lower[s + 1]))
            _lib.paint_face(face, uv, TRAIL_STRIP_KEYS[s])

    return _lib.bm_finalize_to_object(
        bm,
        mesh_name=mesh_name,
        obj_name=obj_name,
        location=(0.0, 0.0, 0.0),
        collection_name=collection_name,
        material=material,
    )


# ============================================================================
# Waystones
# ============================================================================


# bm_add_cuboid face order = [bottom, top, -Y, +Y, -X, +X].
# Outward normals of the 4 vertical faces in Blender XY (the plane runtime
# treats as horizontal). Runtime z = Blender Y, so a tangent (tx, tz) in
# runtime XZ maps to a Blender XY direction (tx, tz). We pick the vertical
# face whose normal · (-tangent) is maximal — i.e. the face pointing toward
# the player approaching the endpoint.
WAYSTONE_FACE_NORMALS = (
    (0.0,  0.0, -1.0),   # bottom — never picked
    (0.0,  0.0,  1.0),   # top — never picked
    (0.0, -1.0,  0.0),   # -Y
    (0.0,  1.0,  0.0),   # +Y
    (-1.0, 0.0,  0.0),   # -X
    (1.0,  0.0,  0.0),   # +X
)


def _pick_carved_face_index(tangent_xz):
    """Choose which cuboid face index gets repainted sand_gravel.

    `tangent_xz` is the unit tangent at the spur endpoint in runtime XZ
    (i.e. the direction the player is walking AT the endpoint). The face
    we want is the one whose outward normal opposes the tangent — that's
    the face the approaching player sees head-on. Equivalent to maximising
    normal · (-tangent_xz) over the 4 vertical faces.
    """
    tx, tz = tangent_xz
    best_idx = 2
    best_dot = -math.inf
    for idx in (2, 3, 4, 5):
        nx, ny, _nz = WAYSTONE_FACE_NORMALS[idx]
        # Normal points into Blender XY; player-facing direction is the
        # tangent reversed. Dot in the XY plane only.
        dot = nx * (-tx) + ny * (-tz)
        if dot > best_dot:
            best_dot = dot
            best_idx = idx
    return best_idx


def _build_waystone(material, obj_name, runtime_xz, tangent_xz):
    """One 0.4 x 0.4 x 0.8m carved standing stone. Body `rock_mid`, one
    vertical face (the approach-facing one) repainted `sand_gravel`.
    Returns (waystone_obj, base_xyz, centre_xyz)."""
    rx, rz = runtime_xz
    ground_z = _lib.height_at(rx, rz)
    centre_z = ground_z + WAYSTONE_HALF_HEIGHT

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    faces = _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(WAYSTONE_HALF_X, WAYSTONE_HALF_Y, WAYSTONE_HALF_HEIGHT),
        color_key="rock_mid",
    )
    carved_idx = _pick_carved_face_index(tangent_xz)
    _lib.paint_face(faces[carved_idx], uv, "sand_gravel")

    waystone = _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"{obj_name}_mesh",
        obj_name=obj_name,
        location=(rx, rz, centre_z),
        collection_name=VIEWPOINTS_COLLECTION,
        material=material,
    )
    return waystone, (rx, rz, ground_z), (rx, rz, centre_z)


def _build_waystone_collider(material, waystone_name, centre_xyz):
    """Hidden cuboid collider sized to the waystone's 0.4 x 0.4 x 0.8m bbox.
    Half-extents in Blender axes = (0.2, 0.2, 0.4)."""
    cx, cy, cz = centre_xyz
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(WAYSTONE_HALF_X, WAYSTONE_HALF_Y, WAYSTONE_HALF_HEIGHT),
        color_key="rock_mid",
    )
    name = f"cuboid_{waystone_name}"
    return _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"{name}_mesh",
        obj_name=name,
        location=(cx, cy, cz),
        collection_name=VIEWPOINTS_COLLECTION,
        material=material,
        hide=True,
    )


# ============================================================================
# Entry point
# ============================================================================


def main():
    # Clear in the locked order.
    _lib.clear_collection(PERIMETER_COLLECTION)
    _lib.clear_collection(DETOUR_NW_COLLECTION)
    _lib.clear_collection(DETOUR_SUMMIT_COLLECTION)
    _lib.clear_collection(DETOUR_SE_COLLECTION)
    _lib.clear_collection(VIEWPOINTS_COLLECTION)

    material = _lib.get_palette_material()

    # Perimeter loop.
    perimeter_samples = _sample_closed_curve(
        PERIMETER_CONTROL_POINTS, PERIMETER_SAMPLE_COUNT
    )
    _build_closed_ribbon(
        perimeter_samples,
        mesh_name="trail_perimeter_mesh",
        obj_name="trail_perimeter",
        collection_name=PERIMETER_COLLECTION,
        material=material,
    )

    # Three detour spurs.
    nw_samples = _sample_open_curve(
        DETOUR_NW_CONTROL_POINTS, DETOUR_SAMPLE_COUNT
    )
    _build_open_ribbon(
        nw_samples,
        mesh_name="trail_detour_nw_mesh",
        obj_name="trail_detour_nw",
        collection_name=DETOUR_NW_COLLECTION,
        material=material,
    )

    summit_samples = _sample_open_curve(
        DETOUR_SUMMIT_CONTROL_POINTS, DETOUR_SAMPLE_COUNT
    )
    _build_open_ribbon(
        summit_samples,
        mesh_name="trail_detour_summit_mesh",
        obj_name="trail_detour_summit",
        collection_name=DETOUR_SUMMIT_COLLECTION,
        material=material,
    )

    se_samples = _sample_open_curve(
        DETOUR_SE_CONTROL_POINTS, DETOUR_SAMPLE_COUNT
    )
    _build_open_ribbon(
        se_samples,
        mesh_name="trail_detour_se_mesh",
        obj_name="trail_detour_se",
        collection_name=DETOUR_SE_COLLECTION,
        material=material,
    )

    # Waystones — one per spur, at the spur endpoint, with the approach-
    # facing face repainted as the carved emblem.
    spurs = (
        ("nw",     DETOUR_NW_CONTROL_POINTS),
        ("summit", DETOUR_SUMMIT_CONTROL_POINTS),
        ("se",     DETOUR_SE_CONTROL_POINTS),
    )
    waystone_bases = {}
    waystone_centres = {}
    for key, controls in spurs:
        endpoint_xz = controls[-1]
        tangent_xz = _tangent_at_open_end(controls)
        name = f"waystone_{key}"
        _, base_xyz, centre_xyz = _build_waystone(
            material, name, endpoint_xz, tangent_xz
        )
        waystone_bases[key] = base_xyz
        waystone_centres[key] = centre_xyz

    # Hidden cuboid colliders, one per waystone.
    for key in ("nw", "summit", "se"):
        _build_waystone_collider(
            material, f"waystone_{key}", waystone_centres[key]
        )

    # Refs — one per viewpoint, at the waystone base, with userData so the
    # runtime can wire any future "viewpoint discovered" achievement.
    for key in ("nw", "summit", "se"):
        _lib.ref_empty(
            f"refViewpoint_{key}",
            waystone_bases[key],
            radius=0.5,
            userdata={"viewpoint": key},
        )

    blend_path = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "world.blend"))
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    print(
        f"{_lib.LOG_PREFIX}[phase-10] OK — trail: perimeter + 3 detours, "
        f"3 waystones, 3 colliders, 3 refs"
    )
    print(f"{_lib.LOG_PREFIX}[phase-10] saved -> {blend_path}")


if __name__ == "__main__":
    main()
