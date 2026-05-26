"""
Phase 9: River + tributary + waterfall + bridges + ocean.

What this produces (after Run Script + save):
- `water/ocean` collection:
    * `ocean_plane`           - single 200x200m flat quad at runtime y=-1.5,
                                palette `deeper_water`. Material
                                `world_palette_ocean_material` (palette clone)
                                carries the `*ocean*` token so the runtime can
                                detect the surface shader by material name.
- `water/river` collection:
    * `river_surface`         - Catmull-Rom bezier sampled at 120 points from
                                NE source (+95, +95) snaking SW to W cliff
                                exit (-78, +20). Per-control-point width
                                varies 2m -> 5m mid-curve -> 3m near cliff,
                                interpolated linearly between controls. Built
                                as a 3-strip ribbon: 0.3m `sunlit_snow` foam
                                left, centre `glacial_river` (variable),
                                0.3m foam right. Every vertex Y samples
                                `height_at(x, z) + 0.02m` so the river drapes
                                the terrain. Material
                                `world_palette_water_material` (palette
                                clone) carries the `*water*` token.
- `water/tributary` collection:
    * `tributary_surface`     - smaller Catmull-Rom curve sampled at 50
                                points, 4 control points branching south
                                from (+15, +5) to (+25, -25). Uniform 1.5m
                                width: 0.2 foam | 1.1 centre | 0.2 foam.
                                Shares `world_palette_water_material`.
- `water/waterfall` collection:
    * `waterfall_plane`       - vertical plane at W cliff edge x=-78, z=18.5
                                to 21.5 (3m wide), runtime y from the river
                                level at the cliff exit down to y=-2 (hidden
                                under ocean plane). Split horizontally into
                                two stacked quads: top 0.5m strip is foam
                                (`sunlit_snow`), the rest is body
                                (`glacial_river`). Material
                                `world_palette_waterfall_material` (palette
                                clone) carries the `*waterfall*` token so
                                the runtime can detect the stripe shader.
- `bridges` collection:
    * `bridge_plank_1..8`     - 8 timber planks across the main river near
                                runtime z=+4. Each 0.6m wide (along river
                                flow) x 2.5m long (perpendicular) x 0.1m
                                thick. Palette `wood_lantern_body`. Tops sit
                                0.4m above the river surface at the bridge
                                centre.
    * `bridge_support_north`  - 0.25m-radius x ~1m stone cylinder under the
    * `bridge_support_south`    north / south plank end. Palette `rock_mid`.
                                Bases sit on the terrain heightfield at the
                                support's runtime XZ.
    * `stepping_stone_1..3`   - 3 flat discs across the tributary at curve
                                t = 0.3, 0.5, 0.7. Radius 0.3m, height 0.15m,
                                palette `rock_mid`. Tops sit 0.15m above the
                                tributary surface.
- Colliders (5; hidden via hide_viewport+hide_render, palette material attached):
    * `cuboid_bridge_deck`    - one cuboid sized to the world bbox of all 8
                                plank objects.
    * `tube_bridge_support_n` - cylinder matching the visible north support.
    * `tube_bridge_support_s` - cylinder matching the visible south support.
    * `tube_stepping_stone_1..3` - cylinders matching the visible stones.
- 2 ref empties in `refs`:
    `refWaterfallSpray`       - runtime (-78, -1.5, +20) at the base of the
                                  waterfall, radius 0.5. Runtime emits spray
                                  particles from here.
    `refRiverSource`          - runtime (+95, height_at(+95,+95), +95) at the
                                  river source, radius 0.5.

Special material names (single-source-of-truth here, mirrors Phase 8's
glass/beam pattern):
- `world_palette_ocean_material`     - ocean plane; `*ocean*` token.
- `world_palette_water_material`     - shared river + tributary; `*water*`.
- `world_palette_waterfall_material` - waterfall plane; `*waterfall*`.

All three are full clones of `world_palette_material` (same image texture,
Closest interpolation, sRGB) so the geometry still UV-snaps to the palette
PNG; only the material data-block name differs so the runtime can
discriminate by material-name token.

Coordinate convention: authored in Blender Z-up. Runtime (x, y, z) maps to
Blender (x, z, y). Every river / tributary vertex Y samples
`_lib.height_at(x, z)`. The ocean and waterfall planes use fixed Y values.

Idempotent: re-running clears `water/river`, `water/tributary`,
`water/waterfall`, `water/ocean`, and `bridges` collections first.

How to run:
  1. Open tools/blender/world.blend in Blender 4.2+.
  2. Scripting workspace -> Text Editor -> Open -> phase-09-river-bridges.py.
  3. Run Script (Alt+P).
  4. Script saves world.blend automatically (wm.save_as_mainfile).
"""

import os
import sys
import math

import bpy
import bmesh
from mathutils import Vector


# Mirror Phase 0..8's _script_dir() - Blender's Text Editor sets __file__
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

OCEAN_COLLECTION = "water/ocean"
RIVER_COLLECTION = "water/river"
TRIB_COLLECTION = "water/tributary"
WATERFALL_COLLECTION = "water/waterfall"
BRIDGES_COLLECTION = "bridges"

# Ocean.
OCEAN_RUNTIME_Y = -1.5
OCEAN_HALF_EXTENT = 100.0

# Main river control points (runtime x, z) — 12 points snaking SW.
# Per-control-point widths interpolated linearly between controls: 2m at the
# source, growing to ~5m mid-curve, narrowing to 3m at the cliff exit.
RIVER_CONTROL_POINTS = [
    (95.0, 95.0),
    (82.0, 85.0),
    (60.0, 72.0),
    (35.0, 55.0),
    (15.0, 35.0),
    (2.0, 18.0),
    (-5.0, 8.0),
    (-15.0, 12.0),
    (-30.0, 18.0),
    (-50.0, 20.0),
    (-65.0, 20.0),
    (-78.0, 20.0),
]
RIVER_CONTROL_WIDTHS = [
    2.0, 2.5, 3.2, 4.0, 4.8, 5.0,
    4.8, 4.5, 4.0, 3.6, 3.2, 3.0,
]
RIVER_SAMPLE_COUNT = 120
RIVER_FOAM_WIDTH = 0.3       # each foam strip
RIVER_LIFT = 0.02            # raise above heightfield to avoid z-fighting

# Tributary control points (runtime x, z) — 4 points branching south.
TRIB_CONTROL_POINTS = [
    (15.0, 5.0),
    (18.0, -5.0),
    (22.0, -15.0),
    (25.0, -25.0),
]
TRIB_SAMPLE_COUNT = 50
TRIB_TOTAL_WIDTH = 1.5
TRIB_FOAM_WIDTH = 0.2

# Waterfall plane: 3m wide x 20m tall vertical plane at the cliff edge.
WATERFALL_X = -78.0
WATERFALL_Z_CENTRE = 20.0
WATERFALL_HALF_WIDTH = 1.5    # half of 3m, sweeps z = 18.5..21.5
WATERFALL_BOTTOM_Y = -2.0     # below ocean plane, hidden underwater
WATERFALL_FOAM_THICKNESS = 0.5  # top-strip foam height in runtime metres

# Bridge — 8 planks side-by-side spanning the river near runtime z=+4.
BRIDGE_TARGET_Z = 4.0
BRIDGE_PLANK_COUNT = 8
BRIDGE_PLANK_WIDTH = 0.6     # along river flow direction
BRIDGE_PLANK_LENGTH = 2.5    # perpendicular to flow (across the river)
BRIDGE_PLANK_THICKNESS = 0.1
BRIDGE_DECK_LIFT = 0.4       # plank top above river surface
BRIDGE_SUPPORT_RADIUS = 0.25
BRIDGE_SUPPORT_HEIGHT = 1.0
BRIDGE_SUPPORT_SEGMENTS = 16

# Stepping stones across the tributary at these curve t values.
STEPPING_STONE_TS = (0.3, 0.5, 0.7)
STEPPING_STONE_RADIUS = 0.3
STEPPING_STONE_HEIGHT = 0.15
STEPPING_STONE_LIFT = 0.15   # top sits this high above tributary surface
STEPPING_STONE_SEGMENTS = 16


# ============================================================================
# Material variants — clones of world_palette_material with distinct names
# so the runtime can discriminate by material-name token. Mirrors Phase 8's
# `_clone_palette_material` pattern.
# ============================================================================


def _clone_palette_material(target_name):
    """Build a full clone of world_palette_material under `target_name`.

    Rebuilt every run (removed and recreated) so stale clones can't drift
    out of sync with the source material.
    """
    src = bpy.data.materials.get(_lib.PALETTE_MATERIAL_NAME)
    if src is None:
        src = _lib.get_palette_material()

    existing = bpy.data.materials.get(target_name)
    if existing is not None:
        bpy.data.materials.remove(existing, do_unlink=True)

    clone = src.copy()
    clone.name = target_name
    return clone


# ============================================================================
# Curve sampling — Catmull-Rom (tau=0.5), mirrors Phase 6.
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


def _sample_curve(control_points, sample_count):
    """Sample `sample_count` points along the Catmull-Rom curve through
    `control_points`. Endpoints duplicated as virtual controls so the curve
    passes through the first and last actual points.

    Returns list of (x, z, seg_f) — seg_f is the float segment index that
    callers can use to interpolate per-control-point attributes (e.g.
    river width).
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
        x, z = _catmull_rom(p0, p1, p2, p3, local_t)
        # Per-control width interpolation maps onto control indices, not the
        # padded `pts` list. The two flanking controls for this sample are
        # (seg_i) and (seg_i + 1) in the original control_points list.
        ctrl_f = seg_i + local_t
        samples.append((x, z, ctrl_f))
    return samples


def _sample_at_t(control_points, t):
    """Sample one (x, z) at parameter t in [0, 1]. Same basis as _sample_curve."""
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


def _width_at(ctrl_f, widths):
    """Linear interpolation through the per-control-point widths array.
    `ctrl_f` is a float in [0, len(widths)-1] from `_sample_curve`."""
    i = int(ctrl_f)
    if i >= len(widths) - 1:
        return widths[-1]
    frac = ctrl_f - i
    return widths[i] * (1.0 - frac) + widths[i + 1] * frac


# ============================================================================
# Ribbon builder — shared by river + tributary
# ============================================================================


def _build_ribbon(samples, widths, foam_width, mesh_name, obj_name,
                  collection_name, material):
    """Sample-stream three-strip ribbon following the heightfield.

    `samples` is the list of (x, z, ctrl_f) from `_sample_curve`.
    `widths` is the per-control widths array (used by `_width_at`).
    `foam_width` is the constant foam-strip width (each side).

    Each sample emits a 4-vert tangent ring (left foam outer, centre-left,
    centre-right, right foam outer). The two centre offsets carve out a
    variable-width centre strip; the foam strips are always `foam_width`
    wide on each side. Quads between consecutive rings form three strips:
    foam | centre | foam.
    """
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)

    rings = []
    for i, (rx, rz, ctrl_f) in enumerate(samples):
        if i == 0:
            nx, nz, _ = samples[i + 1]
            tx, tz = nx - rx, nz - rz
        elif i == len(samples) - 1:
            px, pz, _ = samples[i - 1]
            tx, tz = rx - px, rz - pz
        else:
            nx, nz, _ = samples[i + 1]
            px, pz, _ = samples[i - 1]
            tx, tz = nx - px, nz - pz
        length = math.hypot(tx, tz)
        if length == 0.0:
            tx, tz = 1.0, 0.0
            length = 1.0
        tx /= length
        tz /= length
        # Perpendicular in XY plane (Blender X, Y): rotate tangent +90 deg.
        perp_x = -tz
        perp_y = tx

        total_width = _width_at(ctrl_f, widths)
        half = total_width * 0.5
        # 4 boundary offsets: -half, -(half - foam), +(half - foam), +half.
        offsets = (-half, -(half - foam_width),
                   +(half - foam_width), +half)

        ring = []
        for offset in offsets:
            vx = rx + perp_x * offset
            vy = rz + perp_y * offset
            vz = _lib.height_at(vx, vy) + RIVER_LIFT
            ring.append(bm.verts.new((vx, vy, vz)))
        rings.append(ring)

    strip_keys = ("sunlit_snow", "glacial_river", "sunlit_snow")
    for i in range(len(rings) - 1):
        lower = rings[i]
        upper = rings[i + 1]
        for s in range(3):
            face = bm.faces.new((lower[s], upper[s],
                                 upper[s + 1], lower[s + 1]))
            _lib.paint_face(face, uv, strip_keys[s])

    return _lib.bm_finalize_to_object(
        bm,
        mesh_name=mesh_name,
        obj_name=obj_name,
        location=(0.0, 0.0, 0.0),
        collection_name=collection_name,
        material=material,
    )


# ============================================================================
# Ocean plane
# ============================================================================


def _build_ocean(material):
    """200x200m flat quad at runtime y = -1.5. Single face painted with
    deeper_water. Material is `world_palette_ocean_material`."""
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)

    h = OCEAN_HALF_EXTENT
    z = OCEAN_RUNTIME_Y
    v0 = bm.verts.new((-h, -h, z))
    v1 = bm.verts.new((+h, -h, z))
    v2 = bm.verts.new((+h, +h, z))
    v3 = bm.verts.new((-h, +h, z))
    face = bm.faces.new((v0, v1, v2, v3))
    _lib.paint_face(face, uv, "deeper_water")

    return _lib.bm_finalize_to_object(
        bm,
        mesh_name="ocean_plane_mesh",
        obj_name="ocean_plane",
        location=(0.0, 0.0, 0.0),
        collection_name=OCEAN_COLLECTION,
        material=material,
    )


# ============================================================================
# Waterfall plane
# ============================================================================


def _build_waterfall(material):
    """Vertical plane facing +X (east). Authored at Blender x = WATERFALL_X
    so all four corners share the same X coordinate. Split horizontally into
    two quads: a 0.5m foam strip across the top and a body strip below.

    Top Y of the plane = river level at the cliff exit (so the foam strip
    meets the river ribbon). Bottom Y = WATERFALL_BOTTOM_Y (hidden under
    the ocean plane).
    """
    river_top_y = _lib.height_at(WATERFALL_X, WATERFALL_Z_CENTRE) + RIVER_LIFT

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)

    z_min = WATERFALL_Z_CENTRE - WATERFALL_HALF_WIDTH
    z_max = WATERFALL_Z_CENTRE + WATERFALL_HALF_WIDTH
    y_top = river_top_y
    y_foam_bottom = river_top_y - WATERFALL_FOAM_THICKNESS
    y_bottom = WATERFALL_BOTTOM_Y

    # Build 6 verts: two rows of 3? No — 2 stacked quads share 2 verts in
    # the middle. So 6 verts = 3 rows x 2 z-positions.
    # Row Y values (Blender Z): top, foam_bottom, bottom.
    # Row index = horizontal (Blender Y = runtime Z): z_min, z_max.
    # The plane faces +X (normal pointing east), so vertex winding is CCW
    # when viewed from +X. From +X, increasing Blender Y is to the LEFT and
    # increasing Blender Z is UP. CCW from +X means: lower-left -> lower-
    # right -> upper-right -> upper-left in screen space, which translates
    # to (y=z_max, z=low) -> (y=z_min, z=low) -> (y=z_min, z=high) ->
    # (y=z_max, z=high).
    x = WATERFALL_X
    v_top_min = bm.verts.new((x, z_min, y_top))
    v_top_max = bm.verts.new((x, z_max, y_top))
    v_foam_min = bm.verts.new((x, z_min, y_foam_bottom))
    v_foam_max = bm.verts.new((x, z_max, y_foam_bottom))
    v_bot_min = bm.verts.new((x, z_min, y_bottom))
    v_bot_max = bm.verts.new((x, z_max, y_bottom))

    # Foam strip (top). CCW from +X.
    foam_face = bm.faces.new((v_foam_max, v_foam_min, v_top_min, v_top_max))
    _lib.paint_face(foam_face, uv, "sunlit_snow")

    # Body strip. CCW from +X.
    body_face = bm.faces.new((v_bot_max, v_bot_min, v_foam_min, v_foam_max))
    _lib.paint_face(body_face, uv, "glacial_river")

    return _lib.bm_finalize_to_object(
        bm,
        mesh_name="waterfall_plane_mesh",
        obj_name="waterfall_plane",
        location=(0.0, 0.0, 0.0),
        collection_name=WATERFALL_COLLECTION,
        material=material,
    )


# ============================================================================
# Bridge — anchor to the river curve and build perpendicular to its tangent
# ============================================================================


def _bridge_anchor():
    """Find the t value on the river curve where the sample's z is closest
    to BRIDGE_TARGET_Z. Returns (centre_x, centre_z, tangent_unit_xy).

    The bridge spans the river PERPENDICULAR to the tangent, so we also
    compute the unit tangent at that anchor point.
    """
    # Sample the curve densely enough that we can pick the closest-z sample.
    samples = _sample_curve(RIVER_CONTROL_POINTS, 400)
    best_idx = 0
    best_dist = abs(samples[0][1] - BRIDGE_TARGET_Z)
    for i in range(1, len(samples)):
        d = abs(samples[i][1] - BRIDGE_TARGET_Z)
        if d < best_dist:
            best_dist = d
            best_idx = i
    cx, cz, _ = samples[best_idx]

    # Tangent via central difference around the anchor sample.
    i_prev = max(0, best_idx - 1)
    i_next = min(len(samples) - 1, best_idx + 1)
    px, pz, _ = samples[i_prev]
    nx, nz, _ = samples[i_next]
    tx, tz = nx - px, nz - pz
    length = math.hypot(tx, tz)
    if length == 0.0:
        tx, tz = 1.0, 0.0
        length = 1.0
    return cx, cz, (tx / length, tz / length)


def _build_bridge(material):
    """8 planks laid side-by-side spanning the river at the bridge anchor.

    Each plank's long axis is perpendicular to the river tangent (it spans
    the river). Planks are laid out along the river flow direction so the
    full bridge is BRIDGE_PLANK_COUNT * BRIDGE_PLANK_WIDTH wide along flow.

    The 2 stone supports sit at the two perpendicular ends of the bridge
    (north end and south end relative to the river bank, NOT the world).
    Their cylinder bases rest on the terrain at each support's runtime XZ.

    Returns (plank_objs, support_n_obj, support_s_obj, bridge_centre_xyz,
    support_n_centre_xyz, support_s_centre_xyz).
    """
    cx, cz, (tx, tz) = _bridge_anchor()
    # Perpendicular unit vector in XY plane (rotate tangent +90 deg).
    perp_x = -tz
    perp_y = tx

    river_y = _lib.height_at(cx, cz) + RIVER_LIFT
    plank_top_y = river_y + BRIDGE_DECK_LIFT
    plank_centre_y = plank_top_y - BRIDGE_PLANK_THICKNESS * 0.5

    # Plank positions along the river flow direction. Centred on the anchor.
    total_flow = BRIDGE_PLANK_COUNT * BRIDGE_PLANK_WIDTH
    start_offset = -(total_flow * 0.5) + BRIDGE_PLANK_WIDTH * 0.5

    planks = []
    for i in range(BRIDGE_PLANK_COUNT):
        offset = start_offset + i * BRIDGE_PLANK_WIDTH
        plank_cx = cx + tx * offset
        plank_cz = cz + tz * offset

        # Local cuboid axes: along-flow = BRIDGE_PLANK_WIDTH; perpendicular
        # (across-river) = BRIDGE_PLANK_LENGTH. After yaw rotation about Z,
        # the local +X axis aligns with the river flow direction.
        yaw = math.atan2(tz, tx)

        bm = bmesh.new()
        uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
        _lib.bm_add_cuboid(
            bm, uv,
            center=(0.0, 0.0, 0.0),
            half_extents=(BRIDGE_PLANK_WIDTH * 0.5,
                          BRIDGE_PLANK_LENGTH * 0.5,
                          BRIDGE_PLANK_THICKNESS * 0.5),
            color_key="wood_lantern_body",
        )
        plank = _lib.bm_finalize_to_object(
            bm,
            mesh_name=f"bridge_plank_{i + 1}_mesh",
            obj_name=f"bridge_plank_{i + 1}",
            location=(plank_cx, plank_cz, plank_centre_y),
            collection_name=BRIDGES_COLLECTION,
            material=material,
            rotation_euler=(0.0, 0.0, yaw),
        )
        planks.append(plank)

    # Stone supports at the two perpendicular ends of the bridge. They sit
    # half a plank length out from the bridge centre line, along the
    # perpendicular axis. Each cylinder base on the terrain.
    support_offset = BRIDGE_PLANK_LENGTH * 0.5
    support_n_x = cx + perp_x * support_offset
    support_n_z = cz + perp_y * support_offset
    support_s_x = cx - perp_x * support_offset
    support_s_z = cz - perp_y * support_offset

    support_n_base_y = _lib.height_at(support_n_x, support_n_z)
    support_s_base_y = _lib.height_at(support_s_x, support_s_z)
    support_n_centre_y = support_n_base_y + BRIDGE_SUPPORT_HEIGHT * 0.5
    support_s_centre_y = support_s_base_y + BRIDGE_SUPPORT_HEIGHT * 0.5

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cylinder(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        radius=BRIDGE_SUPPORT_RADIUS,
        height=BRIDGE_SUPPORT_HEIGHT,
        color_key="rock_mid",
        segments=BRIDGE_SUPPORT_SEGMENTS,
    )
    support_n = _lib.bm_finalize_to_object(
        bm,
        mesh_name="bridge_support_north_mesh",
        obj_name="bridge_support_north",
        location=(support_n_x, support_n_z, support_n_centre_y),
        collection_name=BRIDGES_COLLECTION,
        material=material,
    )

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cylinder(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        radius=BRIDGE_SUPPORT_RADIUS,
        height=BRIDGE_SUPPORT_HEIGHT,
        color_key="rock_mid",
        segments=BRIDGE_SUPPORT_SEGMENTS,
    )
    support_s = _lib.bm_finalize_to_object(
        bm,
        mesh_name="bridge_support_south_mesh",
        obj_name="bridge_support_south",
        location=(support_s_x, support_s_z, support_s_centre_y),
        collection_name=BRIDGES_COLLECTION,
        material=material,
    )

    return (planks, support_n, support_s,
            (cx, cz, plank_centre_y),
            (support_n_x, support_n_z, support_n_centre_y),
            (support_s_x, support_s_z, support_s_centre_y))


# ============================================================================
# Tributary stepping stones
# ============================================================================


def _build_stepping_stones(material):
    """3 flat stone discs across the tributary at t=0.3, 0.5, 0.7. Returns
    list of (stone_obj, centre_xyz)."""
    stones = []
    for i, t in enumerate(STEPPING_STONE_TS):
        rx, rz = _sample_at_t(TRIB_CONTROL_POINTS, t)
        # Top of stone = tributary surface + STEPPING_STONE_LIFT.
        water_y = _lib.height_at(rx, rz) + RIVER_LIFT
        top_y = water_y + STEPPING_STONE_LIFT
        centre_y = top_y - STEPPING_STONE_HEIGHT * 0.5

        bm = bmesh.new()
        uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
        _lib.bm_add_cylinder(
            bm, uv,
            center=(0.0, 0.0, 0.0),
            radius=STEPPING_STONE_RADIUS,
            height=STEPPING_STONE_HEIGHT,
            color_key="rock_mid",
            segments=STEPPING_STONE_SEGMENTS,
        )
        stone = _lib.bm_finalize_to_object(
            bm,
            mesh_name=f"stepping_stone_{i + 1}_mesh",
            obj_name=f"stepping_stone_{i + 1}",
            location=(rx, rz, centre_y),
            collection_name=BRIDGES_COLLECTION,
            material=material,
        )
        stones.append((stone, (rx, rz, centre_y)))
    return stones


# ============================================================================
# Colliders
# ============================================================================


def _world_bbox(obj):
    """Return (min_corner, max_corner) Vectors of `obj` in world space."""
    mw = obj.matrix_world
    corners = [mw @ Vector(c) for c in obj.bound_box]
    minc = Vector((min(c.x for c in corners),
                   min(c.y for c in corners),
                   min(c.z for c in corners)))
    maxc = Vector((max(c.x for c in corners),
                   max(c.y for c in corners),
                   max(c.z for c in corners)))
    return minc, maxc


def _bridge_deck_collider(material, plank_objs):
    """Single cuboid covering the world bbox of all 8 planks."""
    minc = None
    maxc = None
    for plank in plank_objs:
        pmin, pmax = _world_bbox(plank)
        if minc is None:
            minc, maxc = pmin.copy(), pmax.copy()
        else:
            minc.x = min(minc.x, pmin.x)
            minc.y = min(minc.y, pmin.y)
            minc.z = min(minc.z, pmin.z)
            maxc.x = max(maxc.x, pmax.x)
            maxc.y = max(maxc.y, pmax.y)
            maxc.z = max(maxc.z, pmax.z)

    size = maxc - minc
    centre = (minc + maxc) * 0.5

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(size.x * 0.5, size.y * 0.5, size.z * 0.5),
        color_key="wood_lantern_body",
    )
    return _lib.bm_finalize_to_object(
        bm,
        mesh_name="cuboid_bridge_deck_mesh",
        obj_name="cuboid_bridge_deck",
        location=(centre.x, centre.y, centre.z),
        collection_name=BRIDGES_COLLECTION,
        material=material,
        hide=True,
    )


def _support_collider(material, side, centre_xyz):
    """Cylinder matching the visible support, hidden."""
    cx, cz, cy = centre_xyz
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cylinder(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        radius=BRIDGE_SUPPORT_RADIUS,
        height=BRIDGE_SUPPORT_HEIGHT,
        color_key="rock_mid",
        segments=BRIDGE_SUPPORT_SEGMENTS,
    )
    name = f"tube_bridge_support_{side}"
    return _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"{name}_mesh",
        obj_name=name,
        location=(cx, cz, cy),
        collection_name=BRIDGES_COLLECTION,
        material=material,
        hide=True,
    )


def _stepping_stone_collider(material, index, centre_xyz):
    """Cylinder matching the visible stepping stone, hidden."""
    cx, cz, cy = centre_xyz
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cylinder(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        radius=STEPPING_STONE_RADIUS,
        height=STEPPING_STONE_HEIGHT,
        color_key="rock_mid",
        segments=STEPPING_STONE_SEGMENTS,
    )
    return _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"tube_stepping_stone_{index + 1}_mesh",
        obj_name=f"tube_stepping_stone_{index + 1}",
        location=(cx, cz, cy),
        collection_name=BRIDGES_COLLECTION,
        material=material,
        hide=True,
    )


# ============================================================================
# Refs
# ============================================================================


def _place_refs():
    """2 ref empties: refWaterfallSpray (base of waterfall) +
    refRiverSource (head of river)."""
    spray_loc = (WATERFALL_X, WATERFALL_Z_CENTRE, OCEAN_RUNTIME_Y)
    _lib.ref_empty("refWaterfallSpray", spray_loc, radius=0.5)

    source_x, source_z = RIVER_CONTROL_POINTS[0]
    source_y = _lib.height_at(source_x, source_z)
    _lib.ref_empty(
        "refRiverSource",
        (source_x, source_z, source_y),
        radius=0.5,
    )
    return 2


# ============================================================================
# Entry point
# ============================================================================


def main():
    # Clear in the locked order from the spec.
    _lib.clear_collection("water/river")
    _lib.clear_collection("water/tributary")
    _lib.clear_collection("water/waterfall")
    _lib.clear_collection("water/ocean")
    _lib.clear_collection("bridges")

    # Source palette material (also re-creates the three clones each run).
    _lib.get_palette_material()
    ocean_mat = _clone_palette_material("world_palette_ocean_material")
    water_mat = _clone_palette_material("world_palette_water_material")
    waterfall_mat = _clone_palette_material("world_palette_waterfall_material")
    palette_mat = _lib.get_palette_material()

    _build_ocean(ocean_mat)

    river_samples = _sample_curve(RIVER_CONTROL_POINTS, RIVER_SAMPLE_COUNT)
    _build_ribbon(
        river_samples, RIVER_CONTROL_WIDTHS, RIVER_FOAM_WIDTH,
        mesh_name="river_surface_mesh",
        obj_name="river_surface",
        collection_name=RIVER_COLLECTION,
        material=water_mat,
    )

    trib_samples = _sample_curve(TRIB_CONTROL_POINTS, TRIB_SAMPLE_COUNT)
    trib_widths = [TRIB_TOTAL_WIDTH] * len(TRIB_CONTROL_POINTS)
    _build_ribbon(
        trib_samples, trib_widths, TRIB_FOAM_WIDTH,
        mesh_name="tributary_surface_mesh",
        obj_name="tributary_surface",
        collection_name=TRIB_COLLECTION,
        material=water_mat,
    )

    _build_waterfall(waterfall_mat)

    (planks, support_n, support_s,
     _bridge_centre, support_n_xyz, support_s_xyz) = _build_bridge(palette_mat)

    stones = _build_stepping_stones(palette_mat)

    # Colliders (palette material so material slot is non-empty, hidden).
    _bridge_deck_collider(palette_mat, planks)
    _support_collider(palette_mat, "n", support_n_xyz)
    _support_collider(palette_mat, "s", support_s_xyz)
    for i, (_stone_obj, centre) in enumerate(stones):
        _stepping_stone_collider(palette_mat, i, centre)

    _place_refs()

    blend_path = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "world.blend"))
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    print(
        f"{_lib.LOG_PREFIX}[phase-09] OK — water: river/tributary/"
        f"waterfall/ocean, bridges + stones, 5 colliders, 2 refs"
    )
    print(f"{_lib.LOG_PREFIX}[phase-09] saved -> {blend_path}")


if __name__ == "__main__":
    main()
