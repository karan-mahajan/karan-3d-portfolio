"""
Phase 7: Contact cliff beacon (W cardinal).

What this produces (after Run Script + save):
- `sections/contact` collection populated with these visible mesh groups:
    * `contact_platform`               - 3x3m x 0.3m thick stone slab, body
                                         palette `rock_mid`. Top surface is
                                         the player-walkable deck.
    * `contact_platform_rim_N|S|E|W`   - four thin 0.05m-tall sand_gravel
                                         cuboids forming a hollow square
                                         border around the platform top.
                                         Reads as a carved-edge band.
    * `contact_brazier_leg_1..3`       - iron tripod legs. Each leg = a
                                         Z-aligned cylinder rotated about
                                         the world Y axis by the splay angle
                                         then yawed by its azimuth
                                         (0/120/240 deg). Legs splay outward
                                         at the BASE and converge at a point
                                         ~1.0m above the platform top. Body
                                         palette `dark_rock_shadow`.
    * `contact_brazier_bowl`           - wide shallow cylinder (radius 0.5m,
                                         height 0.4m) sitting on the tripod
                                         convergence point. Palette
                                         `rock_mid`.
    * `brazier_flame_emissive`         - low-poly tapered cone inside the
                                         bowl, ~0.4m tall, 8 side segments.
                                         Palette `lantern_warm`. The
                                         `_emissive` suffix is the runtime
                                         contract for material swap +
                                         vertex-animated flicker (precedent:
                                         `hearth_embers_emissive`,
                                         `cupola_lantern_emissive`).
    * `contact_inscription_plinth`     - small 0.3x0.3m x 0.8m stone marker,
                                         offset 0.9m east of the brazier
                                         centre. Body palette `rock_mid`;
                                         the face pointing toward the
                                         brazier (-X) is repainted
                                         `sand_gravel` to read as engraved.
- Colliders (3; hidden via hide_viewport+hide_render, palette material
  attached for consistency):
    * `cuboid_contact_platform`        - half-extents (1.5, 0.15, 1.5) in
                                         Blender axis order (hx, hy_height,
                                         hz_north). Centre at platform
                                         centre.
    * `tube_brazier`                   - cylinder mesh, radius 0.5m, height
                                         1.0m. Covers the tripod + bowl
                                         mass; the flame doesn't block. The
                                         bbox tube_* convention is
                                         intentional - the runtime importer
                                         parses bbox X/Z as radius and Y as
                                         height.
    * `cuboid_inscription_plinth`      - half-extents (0.15, 0.4, 0.15).
- 5 ref empties in `refs`:
    `refZoneBounding_contact` (radius 12, at section root),
    `refZoneFrustum_contact`  (radius 9,  at section root),
    `refInteractivePoint_contact` (radius 0.5, at the plinth's top),
    `refBrazier` (radius 0.5, at the bowl centre - runtime attaches a warm
        point light + smoke particle system here),
    `refRespawn_contact` (radius 0.5, at section root).

Beacon orientation (single source of truth for this script):
- Section root sits at runtime (-70, 0). Phase 2's western cliff drops at
  runtime x < -78, so the platform at x=-70 is on the last bit of solid
  ground 8m east of the drop. Trust `_lib.height_at(-70, 0)` for ground Z.
- Tripod splay: 22.5 deg from vertical, legs azimuth 0/120/240 deg in the
  Blender XY plane. Leg length 1.1m produces a convergence point 1.016m
  above the platform top (close to the 1.0m spec target).
- Total brazier height from platform top:
    tripod L*cos(theta) ~= 1.016m
  + bowl height          0.40m
  + flame height         0.40m
  = ~1.82m (within the ~1.8m spec).

Coordinate convention: authored in Blender Z-up. Runtime (x, y, z) maps
to Blender (x, z, y). Every height samples `_lib.height_at(x, z)`.

Idempotent: re-running clears the `sections/contact` collection first.

How to run:
  1. Open tools/blender/world.blend in Blender 4.2+.
  2. Scripting workspace -> Text Editor -> Open -> phase-07-contact-beacon.py.
  3. Run Script (Alt+P).
  4. Script saves world.blend automatically (wm.save_as_mainfile).
"""

import os
import sys
import math

import bpy
import bmesh
from mathutils import Vector, Matrix


# Mirror Phase 0..6's _script_dir() - Blender's Text Editor sets __file__
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


COLLECTION = "sections/contact"

# Section root, runtime coords. Runtime x = -70 (west, last solid ground
# before Phase 2's cliff). Runtime z = 0 (centred on the spawn axis).
SECTION_RUNTIME_X = -70.0
SECTION_RUNTIME_Z = 0.0

# Platform dimensions.
PLATFORM_SIZE_X = 3.0      # E-W extent
PLATFORM_SIZE_Z = 3.0      # N-S extent (runtime Z -> Blender Y)
PLATFORM_THICKNESS = 0.3

# Sand-gravel rim that sits ON the platform top. 0.2m wide band, 0.05m tall.
PLATFORM_RIM_WIDTH = 0.2
PLATFORM_RIM_HEIGHT = 0.05

# Iron tripod legs.
TRIPOD_LEG_LENGTH = 1.1
TRIPOD_LEG_RADIUS = 0.05
TRIPOD_SPLAY_DEG = 22.5
TRIPOD_AZIMUTHS_DEG = (0.0, 120.0, 240.0)

# Bowl atop the tripod convergence point.
BOWL_RADIUS = 0.5
BOWL_HEIGHT = 0.4

# Flame cone inside the bowl.
FLAME_BASE_RADIUS = 0.3
FLAME_HEIGHT = 0.4
FLAME_SIDE_SEGMENTS = 8

# Inscription plinth.
PLINTH_SIZE_X = 0.3
PLINTH_SIZE_Z = 0.3        # N-S (runtime Z -> Blender Y)
PLINTH_HEIGHT = 0.8
PLINTH_OFFSET_X = 0.9      # east of brazier centre


# ============================================================================
# Platform
# ============================================================================


def _build_platform(material, ground_z):
    """3x3x0.3m cuboid centred at section root. `rock_mid` palette."""
    platform_centre_z = ground_z + PLATFORM_THICKNESS * 0.5

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(PLATFORM_SIZE_X * 0.5,
                      PLATFORM_SIZE_Z * 0.5,
                      PLATFORM_THICKNESS * 0.5),
        color_key="rock_mid",
    )
    return _lib.bm_finalize_to_object(
        bm,
        mesh_name="contact_platform_mesh",
        obj_name="contact_platform",
        location=(SECTION_RUNTIME_X, SECTION_RUNTIME_Z, platform_centre_z),
        collection_name=COLLECTION,
        material=material,
    )


def _build_platform_rim(material, ground_z):
    """Four thin sand_gravel cuboids on the platform top, forming a hollow
    square border. Each side is 0.2m wide and PLATFORM_RIM_HEIGHT tall.

    The N and S strips span the full 3m E-W; the E and W strips are
    shortened so they don't overlap the N/S strips at the corners."""
    platform_top_z = ground_z + PLATFORM_THICKNESS
    rim_centre_z = platform_top_z + PLATFORM_RIM_HEIGHT * 0.5

    half_x_long = PLATFORM_SIZE_X * 0.5
    half_z_long = PLATFORM_SIZE_Z * 0.5
    half_band = PLATFORM_RIM_WIDTH * 0.5
    half_h = PLATFORM_RIM_HEIGHT * 0.5

    # Inner span (E/W strips fit between the N/S strips).
    inner_half_z = half_z_long - PLATFORM_RIM_WIDTH

    sides = [
        # (suffix, local_centre_xy, half_extents_xy)
        ("N", (0.0, half_z_long - half_band),
         (half_x_long, half_band)),
        ("S", (0.0, -(half_z_long - half_band)),
         (half_x_long, half_band)),
        ("E", (half_x_long - half_band, 0.0),
         (half_band, inner_half_z)),
        ("W", (-(half_x_long - half_band), 0.0),
         (half_band, inner_half_z)),
    ]

    objs = []
    for suffix, (lcx, lcy), (lhx, lhy) in sides:
        bm = bmesh.new()
        uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
        _lib.bm_add_cuboid(
            bm, uv,
            center=(0.0, 0.0, 0.0),
            half_extents=(lhx, lhy, half_h),
            color_key="sand_gravel",
        )
        obj = _lib.bm_finalize_to_object(
            bm,
            mesh_name=f"contact_platform_rim_{suffix}_mesh",
            obj_name=f"contact_platform_rim_{suffix}",
            location=(SECTION_RUNTIME_X + lcx,
                      SECTION_RUNTIME_Z + lcy,
                      rim_centre_z),
            collection_name=COLLECTION,
            material=material,
        )
        objs.append(obj)
    return objs


# ============================================================================
# Brazier
# ============================================================================


def _build_brazier_leg(material, index, azimuth_deg, platform_top_z):
    """One tripod leg: Z-aligned cylinder built at origin, then tilted about
    Blender Y by the splay angle and yawed about Blender Z by `azimuth_deg`.
    The leg's base sits on the platform top at a splayed-out radius; its
    top meets the convergence point directly above the platform centre."""
    L = TRIPOD_LEG_LENGTH
    theta = math.radians(TRIPOD_SPLAY_DEG)
    az = math.radians(azimuth_deg)

    # See module docstring for the midpoint derivation. We position the
    # object at the leg's midpoint so the centred-at-origin cylinder mesh
    # aligns with base-on-platform / top-at-convergence after rotation.
    half_L = L * 0.5
    base_radius = L * math.sin(theta)
    convergence_z = platform_top_z + L * math.cos(theta)

    midpoint_x = SECTION_RUNTIME_X + half_L * math.sin(theta) * math.cos(az)
    midpoint_y = SECTION_RUNTIME_Z + half_L * math.sin(theta) * math.sin(az)
    midpoint_z = platform_top_z + half_L * math.cos(theta)

    # Tilt the local +Z axis by theta toward local +X (rotate about local
    # -Y so the top moves to +X), then yaw about world Z by az. Matrix
    # multiplication order: rotation applies right-to-left, so the
    # cylinder is first tilted, then yawed.
    tilt = Matrix.Rotation(theta, 4, Vector((0.0, -1.0, 0.0)))
    yaw = Matrix.Rotation(az, 4, Vector((0.0, 0.0, 1.0)))
    rot_euler = (yaw @ tilt).to_euler('XYZ')

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cylinder(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        radius=TRIPOD_LEG_RADIUS, height=L,
        color_key="dark_rock_shadow",
        segments=10,
    )
    obj = _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"contact_brazier_leg_{index + 1}_mesh",
        obj_name=f"contact_brazier_leg_{index + 1}",
        location=(midpoint_x, midpoint_y, midpoint_z),
        collection_name=COLLECTION,
        material=material,
        rotation_euler=(rot_euler.x, rot_euler.y, rot_euler.z),
    )
    return obj, base_radius, convergence_z


def _build_brazier_bowl(material, convergence_z):
    """Wide shallow cylinder centred on the convergence point, sized to the
    tube_brazier collider's outer radius (0.5m). Centre Z is convergence +
    half the bowl height so the bowl sits ON the tripod's apex."""
    bowl_centre_z = convergence_z + BOWL_HEIGHT * 0.5

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cylinder(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        radius=BOWL_RADIUS, height=BOWL_HEIGHT,
        color_key="rock_mid",
        segments=24,
    )
    obj = _lib.bm_finalize_to_object(
        bm,
        mesh_name="contact_brazier_bowl_mesh",
        obj_name="contact_brazier_bowl",
        location=(SECTION_RUNTIME_X, SECTION_RUNTIME_Z, bowl_centre_z),
        collection_name=COLLECTION,
        material=material,
    )
    return obj, bowl_centre_z


def _build_brazier_flame(material, bowl_centre_z):
    """Low-poly tapered cone, 8 side segments, base radius 0.3m, height
    0.4m. Sits with its base 0.05m above the bowl rim so it reads as
    sitting *inside* the bowl bowl_top - inset slightly. The `_emissive`
    suffix on the object name flags it for runtime emissive-material swap
    and vertex-animated flicker."""
    bowl_top_z = bowl_centre_z + BOWL_HEIGHT * 0.5
    base_z = bowl_top_z - 0.05   # inset slightly below the rim
    apex_z = base_z + FLAME_HEIGHT

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)

    apex_vert = bm.verts.new((0.0, 0.0, apex_z - base_z))
    base_ring = []
    for i in range(FLAME_SIDE_SEGMENTS):
        angle = (i / FLAME_SIDE_SEGMENTS) * math.tau
        x = math.cos(angle) * FLAME_BASE_RADIUS
        y = math.sin(angle) * FLAME_BASE_RADIUS
        base_ring.append(bm.verts.new((x, y, 0.0)))

    faces = []
    # Side triangles, CCW from outside so normals point outward.
    for i in range(FLAME_SIDE_SEGMENTS):
        j = (i + 1) % FLAME_SIDE_SEGMENTS
        face = bm.faces.new((base_ring[i], base_ring[j], apex_vert))
        faces.append(face)
    # Base cap (reversed so normal points -Z, sealing the underside).
    base_cap = bm.faces.new(list(reversed(base_ring)))
    faces.append(base_cap)

    for face in faces:
        _lib.paint_face(face, uv, "lantern_warm")

    obj = _lib.bm_finalize_to_object(
        bm,
        mesh_name="brazier_flame_emissive_mesh",
        obj_name="brazier_flame_emissive",
        location=(SECTION_RUNTIME_X, SECTION_RUNTIME_Z, base_z),
        collection_name=COLLECTION,
        material=material,
    )
    return obj


# ============================================================================
# Inscription plinth
# ============================================================================


def _build_plinth(material, ground_z):
    """0.3 x 0.3 x 0.8m stone marker 0.9m east of brazier centre. Body
    rock_mid; the -X face (pointing back at the brazier) repainted
    sand_gravel as the engraved face."""
    plinth_centre_x = SECTION_RUNTIME_X + PLINTH_OFFSET_X
    plinth_centre_y = SECTION_RUNTIME_Z
    plinth_centre_z = ground_z + PLATFORM_THICKNESS + PLINTH_HEIGHT * 0.5

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    faces = _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(PLINTH_SIZE_X * 0.5,
                      PLINTH_SIZE_Z * 0.5,
                      PLINTH_HEIGHT * 0.5),
        color_key="rock_mid",
    )
    # bm_add_cuboid returns faces in [bottom, top, -Y, +Y, -X, +X] order;
    # index 4 is the -X face which points back toward the brazier.
    _lib.paint_face(faces[4], uv, "sand_gravel")

    obj = _lib.bm_finalize_to_object(
        bm,
        mesh_name="contact_inscription_plinth_mesh",
        obj_name="contact_inscription_plinth",
        location=(plinth_centre_x, plinth_centre_y, plinth_centre_z),
        collection_name=COLLECTION,
        material=material,
    )
    return obj, (plinth_centre_x, plinth_centre_y, plinth_centre_z)


# ============================================================================
# Colliders
# ============================================================================


def _build_platform_collider(material, ground_z):
    """cuboid_contact_platform sized to the platform's visible bbox."""
    centre_z = ground_z + PLATFORM_THICKNESS * 0.5

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(PLATFORM_SIZE_X * 0.5,
                      PLATFORM_THICKNESS * 0.5,
                      PLATFORM_SIZE_Z * 0.5),
        color_key="rock_mid",
    )
    # NOTE: bm_add_cuboid half_extents arg is in Blender axis order
    # (X, Y_north, Z_height). The half-extents above are (1.5, 0.15, 1.5)
    # in Blender axes - matching the spec's (1.5, 0.15, 1.5) in (X, height,
    # N-S) order.
    return _lib.bm_finalize_to_object(
        bm,
        mesh_name="cuboid_contact_platform_mesh",
        obj_name="cuboid_contact_platform",
        location=(SECTION_RUNTIME_X, SECTION_RUNTIME_Z, centre_z),
        collection_name=COLLECTION,
        material=material,
        hide=True,
    )


def _build_brazier_collider(material, platform_top_z):
    """tube_brazier: cylinder mesh radius 0.5m, height 1.0m, centred so it
    covers the tripod + bowl mass (not the flame). Centre Z = platform_top
    + 0.5m so the tube spans [platform_top, platform_top + 1m]."""
    centre_z = platform_top_z + 0.5

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cylinder(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        radius=0.5, height=1.0,
        color_key="rock_mid",
        segments=16,
    )
    return _lib.bm_finalize_to_object(
        bm,
        mesh_name="tube_brazier_mesh",
        obj_name="tube_brazier",
        location=(SECTION_RUNTIME_X, SECTION_RUNTIME_Z, centre_z),
        collection_name=COLLECTION,
        material=material,
        hide=True,
    )


def _build_plinth_collider(material, plinth_centre):
    """cuboid_inscription_plinth: half-extents (0.15, 0.4, 0.15) in Blender
    axis order, centred on the plinth's visible centre."""
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(0.15, 0.4, 0.15),
        color_key="rock_mid",
    )
    return _lib.bm_finalize_to_object(
        bm,
        mesh_name="cuboid_inscription_plinth_mesh",
        obj_name="cuboid_inscription_plinth",
        location=(plinth_centre[0], plinth_centre[1], plinth_centre[2]),
        collection_name=COLLECTION,
        material=material,
        hide=True,
    )


# ============================================================================
# Refs
# ============================================================================


def _place_refs(ground_z, bowl_centre_z, plinth_centre, plinth_top_z):
    section_loc = (SECTION_RUNTIME_X, SECTION_RUNTIME_Z, ground_z)

    count = 0
    _lib.ref_empty("refZoneBounding_contact", section_loc, radius=12.0)
    count += 1
    _lib.ref_empty("refZoneFrustum_contact", section_loc, radius=9.0)
    count += 1
    _lib.ref_empty(
        "refInteractivePoint_contact",
        (plinth_centre[0], plinth_centre[1], plinth_top_z),
        radius=0.5,
    )
    count += 1
    _lib.ref_empty(
        "refBrazier",
        (SECTION_RUNTIME_X, SECTION_RUNTIME_Z, bowl_centre_z),
        radius=0.5,
    )
    count += 1
    _lib.ref_empty("refRespawn_contact", section_loc, radius=0.5)
    count += 1
    return count


# ============================================================================
# Entry point
# ============================================================================


def main():
    _lib.clear_collection(COLLECTION)

    material = _lib.get_palette_material()

    ground_z = _lib.height_at(SECTION_RUNTIME_X, SECTION_RUNTIME_Z)
    platform_top_z = ground_z + PLATFORM_THICKNESS

    _build_platform(material, ground_z)
    _build_platform_rim(material, ground_z)

    convergence_z = None
    for i, az in enumerate(TRIPOD_AZIMUTHS_DEG):
        _, _, convergence_z = _build_brazier_leg(
            material, i, az, platform_top_z
        )

    _, bowl_centre_z = _build_brazier_bowl(material, convergence_z)
    _build_brazier_flame(material, bowl_centre_z)

    _, plinth_centre = _build_plinth(material, ground_z)
    plinth_top_z = plinth_centre[2] + PLINTH_HEIGHT * 0.5

    _build_platform_collider(material, ground_z)
    _build_brazier_collider(material, platform_top_z)
    _build_plinth_collider(material, plinth_centre)

    ref_count = _place_refs(ground_z, bowl_centre_z, plinth_centre,
                            plinth_top_z)

    contact_coll = bpy.data.collections["contact"]
    visible_count = len([o for o in contact_coll.objects
                         if not o.hide_viewport])

    blend_path = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "world.blend"))
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    print(
        f"{_lib.LOG_PREFIX}[phase-07] OK - contact: beacon platform, "
        f"{visible_count} visible meshes, 3 colliders, {ref_count} refs"
    )
    print(f"{_lib.LOG_PREFIX}[phase-07] saved -> {blend_path}")


if __name__ == "__main__":
    main()
