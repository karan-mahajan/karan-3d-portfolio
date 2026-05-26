"""
Phase 3: Spawn cluster - wayfinder obelisk + hearth ring + resume lectern +
four worn path stubs, with colliders and ref empties.

What this produces (after Run Script + save):
- `spawn` collection populated with these visible meshes:
    * `wayfinder`              - 2.2m carved obelisk dead-centre at spawn.
    * `hearth_stones`           - 8 fitted stones in a 3m-diameter ring.
    * `hearth_embers_emissive`  - low ember disc at the ring centre. Name
                                  flags it for runtime emissive-material swap.
    * `lectern_pedestal`        - 0.4 x 0.4 x 0.9m support, SW of spawn.
    * `lectern_slab`            - 0.6 x 0.4 x 0.05m angled top, tilts toward
                                  spawn (NE direction).
    * `lectern_scroll`          - flat cream-parchment plane.
    * `lectern_scroll_roll_a`   - parchment roll cylinder (one end).
    * `lectern_scroll_roll_b`   - parchment roll cylinder (other end).
    * `lectern_weight`          - small stone weight on a parchment corner.
    * `spawn_path_N/E/S/W`      - 1 x 2m worn path stubs (3-strip dirt+gravel)
                                  pointing along each cardinal axis.
- Colliders (hidden in viewport + render, `world_palette_material` cosmetic):
    * `cuboid_wayfinder`        - half-extents (0.25, 1.1, 0.25).
    * `cuboid_lectern_pedestal` - half-extents (0.2, 0.45, 0.2).
    * `tube_hearth_ring`        - cylinder mesh, r=1.55m, h=0.4m.
- 5 ref empties in `refs`:
    `refZoneBounding_spawn`, `refZoneFrustum_spawn`,
    `refInteractivePoint_wayfinder`, `refResumeInteractivePoint`, `refHearth`.

Coordinate convention: authored in Blender Z-up. Runtime XYZ maps to Blender
(x, z, y) - Blender X = runtime X east-west, Blender Y = runtime Z
north-south, Blender Z = runtime Y height. Every visible Y position samples
`_lib.height_at(x, z)` so props sit on the heightfield.

Idempotent: re-running clears the `spawn` collection first, then rebuilds.
Refs are reused by name (ref_empty handles this).

How to run:
  1. Open tools/blender/world.blend in Blender 4.2+.
  2. Scripting workspace -> Text Editor -> Open -> phase-03-spawn.py.
  3. Run Script (Alt+P).
  4. Script saves world.blend automatically (wm.save_as_mainfile).
"""

import os
import sys
import math
import random

import bpy
import bmesh
from mathutils import Vector, Matrix


# Mirror Phase 0 / 2's _script_dir() - Blender's Text Editor sets __file__
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


# Generic bmesh helpers live in _lib so Phases 4-7 can reuse them. Bind
# locally so the spawn-specific builders read identically to before the lift.
PALETTE_MATERIAL_NAME = _lib.PALETTE_MATERIAL_NAME
PALETTE_UV_LAYER = _lib.PALETTE_UV_LAYER
_get_palette_material = _lib.get_palette_material
_replace_object = _lib.replace_object
_attach_palette_material = _lib.attach_palette_material
_paint_face = _lib.paint_face
_bm_finalize_to_object = _lib.bm_finalize_to_object
_bm_add_cuboid = _lib.bm_add_cuboid
_bm_add_cylinder = _lib.bm_add_cylinder

# Lectern sits 1.5m SW of spawn. 1.5 / sqrt(2) ~= 1.06066 per axis.
LECTERN_OFFSET = 1.5 / math.sqrt(2.0)


# ============================================================================
# Spawn-specific builders
# ============================================================================


def _build_wayfinder(material):
    """The 2.2m carved obelisk at spawn centre.

    Built tall along Blender Z (= runtime Y height). The shaft is a single
    cuboid block with a 30% inset on the top face (tapered cap suggests a
    carved finial) plus four 0.3 x 1.2m carved face insets on the vertical
    sides. The body uses `rock_mid`; every inset surface gets `sand_gravel`
    so the carved areas read as worn/sandy stone.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new(PALETTE_UV_LAYER)

    # Build at local origin; we set obj.location afterwards. Local Z runs
    # from 0 to 2.2 so the mesh origin sits at the base - matches how the
    # collider thinks about it.
    half_w = 0.25
    height_m = 2.2
    body_faces = _bm_add_cuboid(
        bm, uv_layer,
        center=(0.0, 0.0, height_m * 0.5),
        half_extents=(half_w, half_w, height_m * 0.5),
        color_key="rock_mid",
    )

    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()

    # The cuboid builder returns faces in order: bottom, top, -Y, +Y, -X, +X.
    bottom_face = body_faces[0]
    top_face = body_faces[1]
    side_faces = body_faces[2:6]

    # Top face: 30% inset to taper the cap. inset_individual gives the
    # carved-cap silhouette; depth=0 (flat top, just narrower).
    bmesh.ops.inset_individual(
        bm, faces=[top_face], thickness=half_w * 0.30, depth=0.0,
        use_even_offset=True,
    )
    # bmesh ops can re-key faces; re-resolve "top face" as the one with
    # highest centre Z.
    bm.faces.ensure_lookup_table()
    top_face_after = max(bm.faces, key=lambda f: f.calc_center_median().z)

    # Small inset on top for the "scroll emblem" - 0.25 x 0.15m rectangle
    # pressed 0.05m into the top. inset_individual with even_offset gives a
    # uniform-thickness frame, so to author a 0.25 x 0.15 panel from a
    # ~0.35 x 0.35 tapered top we just use a roughly-centred shrink. Close
    # enough for a stylised low-poly read; the depth carves the recess.
    bmesh.ops.inset_individual(
        bm, faces=[top_face_after], thickness=0.05, depth=-0.05,
        use_even_offset=True,
    )

    # Vertical face insets - the "carved" cardinal-direction panels. Each
    # side face gets a 0.3w x 1.2h shallow recess. inset_individual makes a
    # frame; the inner face after inset is the carved panel.
    for face in side_faces:
        # Inset thickness chosen so the inner panel is ~0.3m wide on a
        # 0.5m face = inset of 0.1m all around. Vertically that leaves a
        # 2.0m inner panel; we want only 1.2m, but inset_individual is
        # uniform - close enough for stylised low-poly authoring without
        # adding extra loop cuts.
        bmesh.ops.inset_individual(
            bm, faces=[face], thickness=0.1, depth=-0.05,
            use_even_offset=True,
        )

    # bmesh.ops.inset_individual is uniform — on a 0.5 x 2.2 face a thickness
    # of 0.1 gives a 0.3 x 2.0 inset (55% of the face), so painting the inset
    # `sand_gravel` floods the obelisk with brown. Keep the geometric recess
    # (shadow depth still reads as a carved panel) but leave the faces as
    # rock_mid so the obelisk reads as a uniform grey stone. The repaint
    # loop is kept (defensive) so any future bmesh op that re-keys faces
    # doesn't accidentally pick up a stray default UV.
    body_top_z = height_m

    for face in bm.faces:
        center = face.calc_center_median()
        normal = face.normal

        is_inset_top = (
            normal.z > 0.5
            and center.z < body_top_z - 0.001
        )
        is_inset_side = (
            abs(normal.z) < 0.5
            and max(abs(center.x), abs(center.y)) < half_w - 0.001
        )
        if is_inset_top or is_inset_side:
            _paint_face(face, uv_layer, "rock_mid")

    # _paint_face needs the cuboid bottom face to keep rock_mid - it
    # wasn't touched by any inset, so no action needed. Same for outer
    # frame faces left around each inset (they keep rock_mid from the
    # initial paint).
    _ = bottom_face  # documentation hook; unused.

    h0 = _lib.height_at(0.0, 0.0)
    obj = _bm_finalize_to_object(
        bm,
        mesh_name="wayfinder_mesh",
        obj_name="wayfinder",
        # Runtime (0, h0, 0) -> Blender (0, 0, h0).
        location=(0.0, 0.0, h0),
        collection_name="spawn",
        material=material,
    )
    return obj


def _build_hearth_ring(material):
    """8 fitted stones in a 3m-diameter circle + a low recessed ember disc.

    Stones authored as one joined mesh `hearth_stones`. Each stone is a
    cuboid with seeded scale + rotation variance so re-runs are byte-stable.
    The ember pit is its own object so the runtime can swap material by name.
    """
    rng = random.Random(42)
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new(PALETTE_UV_LAYER)

    ring_radius = 1.5
    base_x, base_y, base_z = 0.35, 0.30, 0.30  # base half-extent doubles to full size

    h_center = _lib.height_at(0.0, 0.0)

    for i in range(8):
        angle = (i / 8.0) * math.tau
        # Per-stone variance.
        scale_factor = rng.uniform(0.85, 1.15)
        yaw = rng.uniform(0.0, math.tau)
        tilt = math.radians(rng.uniform(-5.0, 5.0))

        # Stone footprint half-extents (along the stone's local axes).
        hx = (base_x * 0.5) * scale_factor
        hy = (base_y * 0.5) * scale_factor
        hz = (base_z * 0.5) * scale_factor

        # Stone centre in Blender XY (= runtime X, Z). Place stones at
        # heightfield height plus half stone height so they sit ON the ground.
        sx_world = math.cos(angle) * ring_radius
        sy_world = math.sin(angle) * ring_radius
        h_local = _lib.height_at(sx_world, sy_world)
        sz_world = h_local + hz

        # Build verts at origin, transform, then add.
        local_verts = [
            (-hx, -hy, -hz), ( hx, -hy, -hz),
            ( hx,  hy, -hz), (-hx,  hy, -hz),
            (-hx, -hy,  hz), ( hx, -hy,  hz),
            ( hx,  hy,  hz), (-hx,  hy,  hz),
        ]
        # Yaw around Z, then tilt around X (so the stone leans a touch).
        cy, sy = math.cos(yaw), math.sin(yaw)
        ct, st = math.cos(tilt), math.sin(tilt)

        world_verts = []
        for vx, vy, vz in local_verts:
            # Yaw.
            rx = vx * cy - vy * sy
            ry = vx * sy + vy * cy
            rz = vz
            # Tilt around X.
            ry2 = ry * ct - rz * st
            rz2 = ry * st + rz * ct
            world_verts.append(bm.verts.new(
                (rx + sx_world, ry2 + sy_world, rz2 + sz_world)
            ))

        quad_indices = [
            (0, 3, 2, 1), (4, 5, 6, 7),
            (0, 1, 5, 4), (3, 7, 6, 2),
            (0, 4, 7, 3), (1, 2, 6, 5),
        ]
        for idx in quad_indices:
            face = bm.faces.new((
                world_verts[idx[0]], world_verts[idx[1]],
                world_verts[idx[2]], world_verts[idx[3]],
            ))
            _paint_face(face, uv_layer, "rock_mid")

    stones_obj = _bm_finalize_to_object(
        bm,
        mesh_name="hearth_stones_mesh",
        obj_name="hearth_stones",
        location=(0.0, 0.0, 0.0),
        collection_name="spawn",
        material=material,
    )

    # Ember pit - its own mesh so runtime can detect the name and swap to
    # an emissive material variant. Disc sits 0.02m below ground so the
    # rim of the recess reads as a real fire pit, not a sticker.
    bm_pit = bmesh.new()
    pit_uv = bm_pit.loops.layers.uv.new(PALETTE_UV_LAYER)
    pit_radius = 0.5
    pit_height = 0.05
    pit_center_z = h_center - 0.02 + (pit_height * 0.5)
    _bm_add_cylinder(
        bm_pit, pit_uv,
        center=(0.0, 0.0, pit_center_z),
        radius=pit_radius, height=pit_height,
        color_key="lantern_warm",
        segments=24,
    )
    embers_obj = _bm_finalize_to_object(
        bm_pit,
        mesh_name="hearth_embers_mesh",
        obj_name="hearth_embers_emissive",
        location=(0.0, 0.0, 0.0),
        collection_name="spawn",
        material=material,
    )

    return stones_obj, embers_obj


def _build_lectern(material):
    """Pedestal + slab (tilted toward spawn) + parchment + stone weight.

    The lectern sits 1.5m SW of spawn. The slab tilts 20 degrees toward
    spawn (i.e. its top normal leans toward +X+Y in Blender, which is +X+Z
    in runtime - the NE direction toward the wayfinder). The tilt axis
    runs perpendicular to that, SE-NW: at -45 degrees yaw around the
    vertical axis from world X.
    """
    runtime_x = -LECTERN_OFFSET
    runtime_z = -LECTERN_OFFSET
    h_local = _lib.height_at(runtime_x, runtime_z)

    pedestal_h = 0.9
    pedestal_hx = 0.2
    pedestal_hy = 0.2
    band_h = 0.05  # the 5cm sand_gravel top trim

    # Pedestal main block: rock_mid bottom + sand_gravel top band. We split
    # along Z and paint each cap differently.
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(PALETTE_UV_LAYER)

    # Lower block (rock_mid).
    lower_z_center = (pedestal_h - band_h) * 0.5
    _bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, lower_z_center),
        half_extents=(pedestal_hx, pedestal_hy, (pedestal_h - band_h) * 0.5),
        color_key="rock_mid",
    )

    # Upper band (sand_gravel).
    band_z_center = (pedestal_h - band_h) + band_h * 0.5
    _bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, band_z_center),
        half_extents=(pedestal_hx, pedestal_hy, band_h * 0.5),
        color_key="sand_gravel",
    )

    # Pedestal sits with its base on terrain. Position in Blender axes:
    # runtime (rx, h, rz) -> Blender (rx, rz, h).
    pedestal_obj = _bm_finalize_to_object(
        bm,
        mesh_name="lectern_pedestal_mesh",
        obj_name="lectern_pedestal",
        location=(runtime_x, runtime_z, h_local),
        collection_name="spawn",
        material=material,
    )

    # Slab - tilted 20deg toward NE (toward spawn). In Blender authoring
    # frame with the lectern at +X+Y from itself pointing toward NE
    # (Blender +X+Y), the tilt axis is perpendicular to (1, 1, 0) - that's
    # (1, -1, 0) normalised. Rotating around that axis by +20deg leans the
    # slab top toward spawn.
    slab_hx, slab_hy, slab_hz = 0.3, 0.2, 0.025
    bm_slab = bmesh.new()
    slab_uv = bm_slab.loops.layers.uv.new(PALETTE_UV_LAYER)
    _bm_add_cuboid(
        bm_slab, slab_uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(slab_hx, slab_hy, slab_hz),
        color_key="rock_mid",
    )

    # Place slab origin at top of pedestal.
    slab_loc = (runtime_x, runtime_z, h_local + pedestal_h + slab_hz)
    # Tilt axis runs SE-NW in Blender XY plane. Lectern sits at -X-Y in
    # Blender (SW of spawn); we want the slab's top NORMAL to lean toward
    # +X+Y (toward spawn at NE). With right-hand rule, rotating +Z by
    # +20deg around axis (-1, +1, 0) produces a normal with +X+Y components
    # (verified by Rodrigues). The opposite axis (+1, -1, 0) would tilt the
    # slab away from spawn.
    tilt_axis = Vector((-1.0, 1.0, 0.0)).normalized()
    tilt_rot = Matrix.Rotation(math.radians(20.0), 4, tilt_axis)
    rot_euler = tilt_rot.to_euler('XYZ')
    slab_obj = _bm_finalize_to_object(
        bm_slab,
        mesh_name="lectern_slab_mesh",
        obj_name="lectern_slab",
        location=slab_loc,
        collection_name="spawn",
        material=material,
        rotation_euler=(rot_euler.x, rot_euler.y, rot_euler.z),
    )

    # Parchment scroll: a flat plane resting on the slab. We author it in
    # the slab's local frame and apply the same tilt + position so it
    # follows the slab face. +0.005m above slab top so faces don't
    # z-fight.
    scroll_w, scroll_h = 0.4, 0.25
    parchment_thickness = 0.005
    bm_scroll = bmesh.new()
    scroll_uv = bm_scroll.loops.layers.uv.new(PALETTE_UV_LAYER)
    _bm_add_cuboid(
        bm_scroll, scroll_uv,
        center=(0.0, 0.0, parchment_thickness * 0.5),  # thin plane above local origin
        half_extents=(scroll_w * 0.5, scroll_h * 0.5, parchment_thickness * 0.5),
        color_key="sunlit_snow",
    )
    # Scroll's local origin coincides with slab top - same world location +
    # slab thickness offset already; we set rotation_euler same as slab so
    # the parchment follows the tilt.
    scroll_loc = (
        runtime_x,
        runtime_z,
        h_local + pedestal_h + slab_hz * 2.0,
    )
    scroll_obj = _bm_finalize_to_object(
        bm_scroll,
        mesh_name="lectern_scroll_mesh",
        obj_name="lectern_scroll",
        location=scroll_loc,
        collection_name="spawn",
        material=material,
        rotation_euler=(rot_euler.x, rot_euler.y, rot_euler.z),
    )

    # End rolls - small cylinders along the scroll's local X (length axis).
    # Built as Z-cylinders, then rotated 90deg around Y so they lie flat
    # along X, then re-aligned with the slab tilt via the same euler. We
    # bake the lay-flat rotation into the mesh (verts) instead of stacking
    # rotations - simpler reasoning.
    roll_radius = 0.04
    roll_length = scroll_h  # rolls span the SHORT dimension of the parchment
    roll_offset_x = scroll_w * 0.5 + roll_radius * 0.5

    def _build_roll(name, local_x_offset):
        bm_roll = bmesh.new()
        roll_uv = bm_roll.loops.layers.uv.new(PALETTE_UV_LAYER)
        # Build cylinder with its axis along Z (default), centred at origin.
        _bm_add_cylinder(
            bm_roll, roll_uv,
            center=(0.0, 0.0, 0.0),
            radius=roll_radius, height=roll_length,
            color_key="sun_rim_warm",
            segments=16,
        )
        # Rotate verts so the cylinder lies along the scroll's Y axis
        # (short axis). Rotation 90deg around X: (x, y, z) -> (x, -z, y).
        for v in bm_roll.verts:
            x, y, z = v.co.x, v.co.y, v.co.z
            v.co = Vector((x, -z, y))
        # Offset along local X so the roll sits at the parchment edge.
        for v in bm_roll.verts:
            v.co.x += local_x_offset
            # Lift slightly so the roll sits ON the parchment surface, not
            # half-sunk: parchment top is at z = parchment_thickness.
            v.co.z += parchment_thickness + roll_radius

        return _bm_finalize_to_object(
            bm_roll,
            mesh_name=f"{name}_mesh",
            obj_name=name,
            location=scroll_loc,
            collection_name="spawn",
            material=material,
            rotation_euler=(rot_euler.x, rot_euler.y, rot_euler.z),
        )

    roll_a = _build_roll("lectern_scroll_roll_a", +roll_offset_x)
    roll_b = _build_roll("lectern_scroll_roll_b", -roll_offset_x)

    # Stone weight on a corner of the parchment. Pin near the +X+Y corner.
    bm_w = bmesh.new()
    w_uv = bm_w.loops.layers.uv.new(PALETTE_UV_LAYER)
    weight_half = 0.04
    _bm_add_cuboid(
        bm_w, w_uv,
        center=(scroll_w * 0.5 - weight_half - 0.02,
                scroll_h * 0.5 - weight_half - 0.02,
                parchment_thickness + weight_half),
        half_extents=(weight_half, weight_half, weight_half),
        color_key="rock_mid",
    )
    weight_obj = _bm_finalize_to_object(
        bm_w,
        mesh_name="lectern_weight_mesh",
        obj_name="lectern_weight",
        location=scroll_loc,
        collection_name="spawn",
        material=material,
        rotation_euler=(rot_euler.x, rot_euler.y, rot_euler.z),
    )

    return pedestal_obj, slab_obj, scroll_obj, roll_a, roll_b, weight_obj


def _build_path_stubs(material):
    """Four 1m x 2m worn ribbons at the start of each cardinal corridor.

    Each stub is a 3-strip plane: a 0.6m central `dirt_path` band flanked
    by two 0.2m `sand_gravel` bands. Raised +0.01m above the heightfield
    sample at each strip's centre to avoid z-fighting with terrain.
    """
    stub_length = 2.0  # along the cardinal axis (outward from spawn)
    stub_width = 1.0   # perpendicular to that
    strip_widths = (0.2, 0.6, 0.2)  # gravel | dirt | gravel
    strip_keys = ("sand_gravel", "dirt_path", "sand_gravel")

    # Directions: each entry = (name, runtime_dx, runtime_dz) representing
    # the OUTWARD direction the stub points. Stub centre is one stub-length
    # out from spawn so the inner edge sits at radius ~2m.
    cardinals = [
        ("spawn_path_N", 0.0, +1.0),
        ("spawn_path_E", +1.0, 0.0),
        ("spawn_path_S", 0.0, -1.0),
        ("spawn_path_W", -1.0, 0.0),
    ]

    objs = []
    for name, dx, dz in cardinals:
        bm = bmesh.new()
        uv = bm.loops.layers.uv.new(PALETTE_UV_LAYER)

        # In LOCAL frame the stub runs along +X (length) and spans -W/2..+W/2
        # along Y (width). We rotate the whole object afterwards to point
        # toward the cardinal.
        # Place 3 strip quads side-by-side along Y.
        cumulative = -stub_width * 0.5
        for strip_w, key in zip(strip_widths, strip_keys):
            y0 = cumulative
            y1 = cumulative + strip_w
            cumulative = y1

            v00 = bm.verts.new((-stub_length * 0.5, y0, 0.0))
            v10 = bm.verts.new((+stub_length * 0.5, y0, 0.0))
            v11 = bm.verts.new((+stub_length * 0.5, y1, 0.0))
            v01 = bm.verts.new((-stub_length * 0.5, y1, 0.0))
            face = bm.faces.new((v00, v10, v11, v01))
            _paint_face(face, uv, key)

        # Compute world position: centre of stub sits 2m out from spawn
        # (one half-length along outward direction).
        runtime_cx = dx * (stub_length * 0.5 + 1.0)
        runtime_cz = dz * (stub_length * 0.5 + 1.0)
        h_local = _lib.height_at(runtime_cx, runtime_cz)
        location = (runtime_cx, runtime_cz, h_local + 0.01)

        # Rotation: object local +X must align with outward direction
        # (dx, dz) in Blender XY. yaw = atan2(dz, dx).
        yaw = math.atan2(dz, dx)

        obj = _bm_finalize_to_object(
            bm,
            mesh_name=f"{name}_mesh",
            obj_name=name,
            location=location,
            collection_name="spawn",
            material=material,
            rotation_euler=(0.0, 0.0, yaw),
        )
        objs.append(obj)

    return objs


# ============================================================================
# Colliders
# ============================================================================


def _build_spawn_colliders(material):
    """Wayfinder cuboid + lectern pedestal cuboid + hearth tube collider.

    All colliders live in the `spawn` collection, hidden in viewport +
    render. Material attached for consistency only - colliders never
    render. Runtime importer reads by name prefix (cuboid_, tube_).
    """
    h0 = _lib.height_at(0.0, 0.0)

    # cuboid_wayfinder - half (0.25, 1.1, 0.25). Half-extent Y in runtime
    # terms (= Blender Z) is 1.1 = half of the 2.2m height. Center is at
    # ground + 1.1m.
    bm_w = bmesh.new()
    uv_w = bm_w.loops.layers.uv.new(PALETTE_UV_LAYER)
    _bm_add_cuboid(
        bm_w, uv_w,
        center=(0.0, 0.0, 0.0),
        half_extents=(0.25, 0.25, 1.1),
        color_key="rock_mid",
    )
    wayfinder_collider = _bm_finalize_to_object(
        bm_w,
        mesh_name="cuboid_wayfinder_mesh",
        obj_name="cuboid_wayfinder",
        location=(0.0, 0.0, h0 + 1.1),
        collection_name="spawn",
        material=material,
        hide=True,
    )

    # cuboid_lectern_pedestal - half (0.2, 0.45, 0.2). Pedestal is 0.9m tall,
    # so half-Y = 0.45; centre at ground + 0.45.
    runtime_x = -LECTERN_OFFSET
    runtime_z = -LECTERN_OFFSET
    h_pedestal = _lib.height_at(runtime_x, runtime_z)

    bm_p = bmesh.new()
    uv_p = bm_p.loops.layers.uv.new(PALETTE_UV_LAYER)
    _bm_add_cuboid(
        bm_p, uv_p,
        center=(0.0, 0.0, 0.0),
        half_extents=(0.2, 0.2, 0.45),
        color_key="rock_mid",
    )
    pedestal_collider = _bm_finalize_to_object(
        bm_p,
        mesh_name="cuboid_lectern_pedestal_mesh",
        obj_name="cuboid_lectern_pedestal",
        location=(runtime_x, runtime_z, h_pedestal + 0.45),
        collection_name="spawn",
        material=material,
        hide=True,
    )

    # tube_hearth_ring - r=1.55m, h=0.4m. Cylinder mesh; runtime importer
    # reads the bbox and builds the Rapier tube collider. Centre at
    # ground + 0.2 (half-height).
    bm_t = bmesh.new()
    uv_t = bm_t.loops.layers.uv.new(PALETTE_UV_LAYER)
    _bm_add_cylinder(
        bm_t, uv_t,
        center=(0.0, 0.0, 0.0),
        radius=1.55, height=0.4,
        color_key="rock_mid",
        segments=24,
    )
    hearth_collider = _bm_finalize_to_object(
        bm_t,
        mesh_name="tube_hearth_ring_mesh",
        obj_name="tube_hearth_ring",
        location=(0.0, 0.0, h0 + 0.2),
        collection_name="spawn",
        material=material,
        hide=True,
    )

    return wayfinder_collider, pedestal_collider, hearth_collider


# ============================================================================
# Refs
# ============================================================================


def _place_spawn_refs():
    """5 ref empties anchored to the spawn cluster. Locations follow
    `_lib.ref_empty`'s runtime convention: (x, y_height, z_north).

    Note: _lib.ref_empty passes `location` straight to obj.location, which
    is Blender axes. Phase 2's refs use (runtime_x, runtime_z, runtime_y) -
    i.e. Blender X = runtime X, Blender Y = runtime Z, Blender Z = runtime Y.
    We follow the same convention here.
    """
    h0 = _lib.height_at(0.0, 0.0)

    # refZoneBounding_spawn - 12m bounding cylinder.
    _lib.ref_empty(
        "refZoneBounding_spawn",
        (0.0, 0.0, h0),
        radius=12.0,
    )
    # refZoneFrustum_spawn - 9m visibility frustum.
    _lib.ref_empty(
        "refZoneFrustum_spawn",
        (0.0, 0.0, h0),
        radius=9.0,
    )
    # refInteractivePoint_wayfinder - top of obelisk for DOM label.
    _lib.ref_empty(
        "refInteractivePoint_wayfinder",
        (0.0, 0.0, h0 + 2.2),
        radius=0.5,
    )
    # refResumeInteractivePoint - lectern slab-top centre. Pedestal 0.9m +
    # slab thickness 0.05m above terrain.
    h_lectern = _lib.height_at(-LECTERN_OFFSET, -LECTERN_OFFSET)
    _lib.ref_empty(
        "refResumeInteractivePoint",
        (-LECTERN_OFFSET, -LECTERN_OFFSET, h_lectern + 0.95),
        radius=0.5,
    )
    # refHearth - ember pit centre. Runtime attaches the emissive light.
    _lib.ref_empty(
        "refHearth",
        (0.0, 0.0, h0),
        radius=0.3,
    )


# ============================================================================
# Entry point
# ============================================================================


def main():
    _lib.clear_collection("spawn")

    material = _get_palette_material()

    _build_wayfinder(material)
    _build_hearth_ring(material)
    _build_lectern(material)
    _build_path_stubs(material)
    _build_spawn_colliders(material)
    _place_spawn_refs()

    blend_path = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "world.blend"))
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    # Counts mirror spec verification line: "4 mesh groups, 3 colliders, 5 refs".
    print(
        f"{_lib.LOG_PREFIX}[phase-03] OK - spawn cluster, "
        f"4 mesh groups (wayfinder, hearth, lectern, path stubs), "
        f"3 colliders, 5 refs"
    )
    print(f"{_lib.LOG_PREFIX}[phase-03] saved -> {blend_path}")


if __name__ == "__main__":
    main()
