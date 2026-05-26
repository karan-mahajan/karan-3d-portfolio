"""
Phase 5: Skills observatory tower (S cardinal, -70m south of spawn).

What this produces (after Run Script + save):
- `sections/skills` collection populated with these visible mesh groups:
    * `observatory_shaft_segment_1..4`  - 4 stacked 1m stone cylinder
                                          segments. The 1m stack gives us
                                          a face seam at each metre so the
                                          mortar bands read as separate
                                          face rings between segments.
    * `observatory_dome`                - copper-clad half-sphere on top of
                                          the shaft; lowest latitude ring
                                          repainted sand_gravel as the
                                          weathered edge.
    * `observatory_cupola_cube`         - 0.4m timber cube perched on the
                                          dome apex.
    * `cupola_lantern_emissive`         - small lantern cap above the cube.
                                          The `_emissive` suffix is the
                                          runtime contract (precedent:
                                          `hearth_embers_emissive`,
                                          `forge_embers_emissive`).
    * `observatory_telescope_tube`      - brass tube angled ~45 deg upward,
                                          mounted partway up the dome.
    * `observatory_telescope_leg_1..3`  - 3 slanted wooden tripod legs.
    * `observatory_door`                - decorative timber door on the
                                          NORTH face of the shaft (facing
                                          the player approaching from spawn).
    * `observatory_artifact_lectern`    - small reading lectern (pedestal +
                                          tilted slab) NE of tower.
    * `observatory_artifact_scrolls`    - 3 stacked parchment cylinders on
                                          a small stone base, NW of tower.
    * `observatory_artifact_books`      - 3 stacked book cuboids, E of tower.
    * `observatory_artifact_chest`      - chest body + open lid + 3
                                          instruments inside, W of tower.
- Colliders (5; hidden via hide_viewport+hide_render, palette material
  attached for consistency):
    * `tube_observatory`               - cylinder r=1.5m, height=4m at
                                         section root.
    * `cuboid_artifact_lectern`         - bbox of the lectern artifact group.
    * `cuboid_artifact_scrolls`         - bbox of the scroll stack.
    * `cuboid_artifact_books`           - bbox of the book stack.
    * `cuboid_artifact_chest`           - bbox of the chest+lid+contents.
- 4 ref empties in `refs`:
    `refZoneBounding_skills` (radius 13), `refZoneFrustum_skills` (radius
    10), `refInteractivePoint_skills` (north door, +1.5m above ground),
    `refRespawn_skills` (radius 0.5).

Tower orientation (single source of truth for this script):
- North in runtime = +Z = Blender +Y. The decorative door faces +Y so the
  player walking south from spawn approaches the door head-on.
- Artifacts are arrayed on the NE / NW / E / W of the tower base, flanking
  the north approach without blocking the door sightline.

Coordinate convention: authored in Blender Z-up. Runtime XYZ maps to
Blender (x, z, y). Every Y position samples `_lib.height_at(x, z)` so
geometry sits on the heightfield.

Idempotent: re-running clears the `sections/skills` collection first.

How to run:
  1. Open tools/blender/world.blend in Blender 4.2+.
  2. Scripting workspace -> Text Editor -> Open -> phase-05-skills-observatory.py.
  3. Run Script (Alt+P).
  4. Script saves world.blend automatically (wm.save_as_mainfile).
"""

import os
import sys
import math

import bpy
import bmesh
from mathutils import Vector, Matrix


# Mirror Phase 0..4's _script_dir() - Blender's Text Editor sets __file__
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


COLLECTION = "sections/skills"

# Section root (runtime coords). The plan locks 0m east-west, -70m south.
SECTION_RUNTIME_X = 0.0
SECTION_RUNTIME_Z = -70.0

# Shaft + dome dimensions.
SHAFT_RADIUS = 1.5
SHAFT_HEIGHT = 4.0
SHAFT_SEGMENT_COUNT = 4         # 4x 1m stacked cylinders = visible mortar seams
SHAFT_SIDE_SEGMENTS = 32        # circular tessellation
MORTAR_BAND_THICKNESS = 0.04    # vertical thickness of each mortar band cylinder

DOME_RADIUS = 1.5
DOME_LON_SEGMENTS = 24          # longitude rings
DOME_LAT_SEGMENTS = 8           # latitude rings (only top hemisphere)

# Cupola sits flush on dome apex. Small cube + emissive cap on top.
CUPOLA_CUBE_HALF = 0.20         # 0.4m wide cube
LANTERN_CAP_HALF_XY = 0.10      # 0.2m wide emissive cap
LANTERN_CAP_HEIGHT = 0.16       # height of the lantern cap cuboid

# Telescope geometry.
TELESCOPE_TUBE_RADIUS = 0.08
TELESCOPE_TUBE_LENGTH = 0.80
TELESCOPE_PITCH_DEG = 45.0      # angle above horizontal
TELESCOPE_MOUNT_FRAC = 0.7      # fraction of dome radius from base where
                                # the tripod base lands on the dome surface

TRIPOD_LEG_RADIUS = 0.025
TRIPOD_LEG_LENGTH = 0.30
TRIPOD_LEG_SPLAY_DEG = 25.0     # angle each leg leans outward from vertical

# Decorative door on the south face of the shaft.
DOOR_WIDTH = 0.9
DOOR_HEIGHT = 1.9
DOOR_THICKNESS = 0.05

# Artifact ring radius (distance from tower centre to each artifact's centre).
ARTIFACT_RADIUS = 2.2

# Lectern artifact dimensions.
LECTERN_PEDESTAL_HX = 0.15      # 0.3m wide
LECTERN_PEDESTAL_HY = 0.15
LECTERN_PEDESTAL_H = 0.7
LECTERN_SLAB_HX = 0.20          # 0.4m wide
LECTERN_SLAB_HY = 0.125         # 0.25m deep
LECTERN_SLAB_HZ = 0.02          # 0.04m thick
LECTERN_SLAB_TILT_DEG = 15.0

# Scroll stack dimensions.
SCROLL_RADIUS = 0.04
SCROLL_LENGTH = 0.35
SCROLL_BASE_HX = 0.22
SCROLL_BASE_HY = 0.12
SCROLL_BASE_HZ = 0.025

# Book stack dimensions (Blender half-extents). Three books, varying size.
BOOK_DIMS = [
    (0.125, 0.10, 0.020),   # bottom: 0.25 x 0.20 x 0.04
    (0.110, 0.09, 0.025),   # middle: 0.22 x 0.18 x 0.05
    (0.100, 0.085, 0.015),  # top:    0.20 x 0.17 x 0.03
]

# Chest dimensions.
CHEST_BODY_HX = 0.25            # 0.5m wide
CHEST_BODY_HY = 0.175           # 0.35m deep
CHEST_BODY_HZ = 0.15            # 0.3m tall
CHEST_LID_THICK = 0.03          # 0.06m thick lid
CHEST_LID_OPEN_DEG = 80.0


# ============================================================================
# Local helpers
# ============================================================================


def _bm_add_dome(bm, uv_layer, center, radius, color_key,
                 lon_segments=24, lat_segments=8, edge_color_key=None):
    """Append a Z-up upper hemisphere to `bm` centred at `center`.

    Built as latitude/longitude rings so every quad face can be UV-painted
    to a palette cell. The lowest latitude ring (between dome base and the
    next ring up) is repainted to `edge_color_key` if provided - this gives
    a weathered-edge band on the dome.

    Latitude phi runs from 0 (equator, base) to pi/2 (pole, apex).
    `lat_segments` is the number of latitude divisions; ring 0 sits at the
    base, ring `lat_segments` is the pole.

    Returns the list of faces in build order:
      [side quads bottom-to-top, then 1 top n-gon fan around the pole].
    """
    cx, cy, cz = center

    rings = []
    for lat in range(lat_segments):
        phi = (lat / lat_segments) * (math.pi / 2.0)
        ring_radius = radius * math.cos(phi)
        ring_z = cz + radius * math.sin(phi)
        ring = []
        for lon in range(lon_segments):
            theta = (lon / lon_segments) * math.tau
            x = cx + math.cos(theta) * ring_radius
            y = cy + math.sin(theta) * ring_radius
            ring.append(bm.verts.new((x, y, ring_z)))
        rings.append(ring)

    # Apex point (single vertex at the pole).
    apex = bm.verts.new((cx, cy, cz + radius))

    faces = []
    # Quad bands between consecutive latitude rings.
    for lat in range(lat_segments - 1):
        lower = rings[lat]
        upper = rings[lat + 1]
        for lon in range(lon_segments):
            j = (lon + 1) % lon_segments
            face = bm.faces.new((lower[lon], lower[j], upper[j], upper[lon]))
            faces.append(face)

    # Top fan: tris from the last ring to the apex.
    top_ring = rings[-1]
    for lon in range(lon_segments):
        j = (lon + 1) % lon_segments
        face = bm.faces.new((top_ring[lon], top_ring[j], apex))
        faces.append(face)

    for face in faces:
        _lib.paint_face(face, uv_layer, color_key)

    if edge_color_key is not None:
        # First lon_segments faces are the lowest latitude band (lat=0).
        for face in faces[:lon_segments]:
            _lib.paint_face(face, uv_layer, edge_color_key)

    return faces


def _world_bbox(obj):
    """Return (min_corner, max_corner) Vectors of `obj` in world space.

    Equivalent to a Three.js Box3().setFromObject(node) for the mesh
    bounding box. Used to size colliders to their visible mesh per
    CLAUDE.md rule 5.
    """
    mw = obj.matrix_world
    corners = [mw @ Vector(c) for c in obj.bound_box]
    minc = Vector((min(c.x for c in corners),
                   min(c.y for c in corners),
                   min(c.z for c in corners)))
    maxc = Vector((max(c.x for c in corners),
                   max(c.y for c in corners),
                   max(c.z for c in corners)))
    return minc, maxc


def _group_world_bbox(objs):
    """Union bbox over a list of objects in world space."""
    mins = []
    maxs = []
    for obj in objs:
        minc, maxc = _world_bbox(obj)
        mins.append(minc)
        maxs.append(maxc)
    minc = Vector((min(m.x for m in mins),
                   min(m.y for m in mins),
                   min(m.z for m in mins)))
    maxc = Vector((max(m.x for m in maxs),
                   max(m.y for m in maxs),
                   max(m.z for m in maxs)))
    return minc, maxc


# ============================================================================
# Builders
# ============================================================================


def _build_shaft(material, ground_z):
    """4 stacked 1m stone cylinders + 3 thin mortar-band cylinders between
    them. Stacking gives clean face seams every 1m for the mortar bands
    to read as separate rings, no loop-cut bookkeeping needed."""
    cx = SECTION_RUNTIME_X
    cy = SECTION_RUNTIME_Z
    segment_h = SHAFT_HEIGHT / SHAFT_SEGMENT_COUNT

    segments = []
    for i in range(SHAFT_SEGMENT_COUNT):
        bottom_z = ground_z + i * segment_h
        centre_z = bottom_z + segment_h * 0.5
        bm = bmesh.new()
        uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
        _lib.bm_add_cylinder(
            bm, uv,
            center=(0.0, 0.0, 0.0),
            radius=SHAFT_RADIUS, height=segment_h,
            color_key="rock_mid",
            segments=SHAFT_SIDE_SEGMENTS,
        )
        seg = _lib.bm_finalize_to_object(
            bm,
            mesh_name=f"observatory_shaft_segment_{i + 1}_mesh",
            obj_name=f"observatory_shaft_segment_{i + 1}",
            location=(cx, cy, centre_z),
            collection_name=COLLECTION,
            material=material,
        )
        segments.append(seg)

    # Mortar bands sit at every internal seam: heights 1m, 2m, 3m above
    # ground. Slightly fatter radius so they protrude as a visible ring.
    band_radius = SHAFT_RADIUS + 0.03
    band_objs = []
    for i in range(1, SHAFT_SEGMENT_COUNT):
        seam_z = ground_z + i * segment_h
        bm = bmesh.new()
        uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
        _lib.bm_add_cylinder(
            bm, uv,
            center=(0.0, 0.0, 0.0),
            radius=band_radius, height=MORTAR_BAND_THICKNESS,
            color_key="sand_gravel",
            segments=SHAFT_SIDE_SEGMENTS,
        )
        band = _lib.bm_finalize_to_object(
            bm,
            mesh_name=f"observatory_shaft_mortar_{i}_mesh",
            obj_name=f"observatory_shaft_mortar_{i}",
            location=(cx, cy, seam_z),
            collection_name=COLLECTION,
            material=material,
        )
        band_objs.append(band)

    shaft_top_z = ground_z + SHAFT_HEIGHT
    return segments, band_objs, shaft_top_z


def _build_dome(material, shaft_top_z):
    """Half-sphere atop the shaft. Lowest latitude band repainted as the
    weathered edge."""
    cx = SECTION_RUNTIME_X
    cy = SECTION_RUNTIME_Z
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _bm_add_dome(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        radius=DOME_RADIUS,
        color_key="wood_lantern_body",
        lon_segments=DOME_LON_SEGMENTS,
        lat_segments=DOME_LAT_SEGMENTS,
        edge_color_key="sand_gravel",
    )
    dome = _lib.bm_finalize_to_object(
        bm,
        mesh_name="observatory_dome_mesh",
        obj_name="observatory_dome",
        location=(cx, cy, shaft_top_z),
        collection_name=COLLECTION,
        material=material,
    )
    dome_apex_z = shaft_top_z + DOME_RADIUS
    return dome, dome_apex_z


def _build_cupola(material, dome_apex_z):
    """Small timber cube on the dome apex + emissive lantern cap on top.

    The cube sits with its base at the dome apex; the lantern cap sits
    on top of the cube. The lantern object is named `cupola_lantern_emissive`
    so the runtime detects it by `_emissive` suffix (no separate ref).
    """
    cx = SECTION_RUNTIME_X
    cy = SECTION_RUNTIME_Z

    cube_centre_z = dome_apex_z + CUPOLA_CUBE_HALF
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(CUPOLA_CUBE_HALF, CUPOLA_CUBE_HALF, CUPOLA_CUBE_HALF),
        color_key="wood_lantern_body",
    )
    cube = _lib.bm_finalize_to_object(
        bm,
        mesh_name="observatory_cupola_cube_mesh",
        obj_name="observatory_cupola_cube",
        location=(cx, cy, cube_centre_z),
        collection_name=COLLECTION,
        material=material,
    )

    cube_top_z = cube_centre_z + CUPOLA_CUBE_HALF
    lantern_centre_z = cube_top_z + LANTERN_CAP_HEIGHT * 0.5
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(LANTERN_CAP_HALF_XY, LANTERN_CAP_HALF_XY,
                      LANTERN_CAP_HEIGHT * 0.5),
        color_key="lantern_warm",
    )
    lantern = _lib.bm_finalize_to_object(
        bm,
        mesh_name="cupola_lantern_emissive_mesh",
        obj_name="cupola_lantern_emissive",
        location=(cx, cy, lantern_centre_z),
        collection_name=COLLECTION,
        material=material,
    )

    return cube, lantern


def _build_telescope(material, shaft_top_z):
    """Brass tube + 3-leg wooden tripod on the dome.

    Tube is mounted at TELESCOPE_MOUNT_FRAC of the dome radius up from
    the dome base; the mount point lies on the dome surface in the +X
    (east) direction. Tube tilts up by TELESCOPE_PITCH_DEG so the muzzle
    points skyward (north-east-ish in world frame). Tripod legs splay
    from the mount point down to the dome surface.
    """
    cx = SECTION_RUNTIME_X
    cy = SECTION_RUNTIME_Z

    # Mount point on the dome surface: horizontal distance from tower
    # centre = dome_radius * cos(phi); height above shaft top =
    # dome_radius * sin(phi). With TELESCOPE_MOUNT_FRAC measured along
    # vertical from base, phi = asin(MOUNT_FRAC).
    phi = math.asin(TELESCOPE_MOUNT_FRAC)
    horiz = DOME_RADIUS * math.cos(phi)
    mount_z = shaft_top_z + DOME_RADIUS * math.sin(phi)
    # Mount toward +X (east) so the telescope reads cleanly from the south
    # approach without occluding the door.
    mount_x = cx + horiz
    mount_y = cy

    # Telescope tube: cylinder along local Z, rotated so its axis tips up
    # by TELESCOPE_PITCH_DEG above horizontal in the world XZ plane. Tube
    # centre is offset along its own axis by half-length so the BASE sits
    # at the mount point.
    pitch = math.radians(TELESCOPE_PITCH_DEG)
    axis_dir = Vector((math.cos(pitch), 0.0, math.sin(pitch)))
    tube_centre = Vector((mount_x, mount_y, mount_z)) \
        + axis_dir * (TELESCOPE_TUBE_LENGTH * 0.5)

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cylinder(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        radius=TELESCOPE_TUBE_RADIUS, height=TELESCOPE_TUBE_LENGTH,
        color_key="wood_lantern_body",
        segments=16,
    )
    # bm_add_cylinder builds along Z. To align local Z with axis_dir we
    # rotate around Y by -pitch (so local +Z swings toward +X by pitch).
    # Equivalent euler: (0, -pitch, 0) rotates +Z -> +X*sin + +Z*cos.
    # We want +Z -> +X*cos(pitch) + Z*sin(pitch) actually... revisit:
    # Standard rotation around Y by angle ay sends +Z to (sin(ay), 0,
    # cos(ay)). We want it to go to (cos(pitch), 0, sin(pitch)). So
    # sin(ay) = cos(pitch) and cos(ay) = sin(pitch) -> ay = pi/2 - pitch.
    ay = (math.pi * 0.5) - pitch
    tube = _lib.bm_finalize_to_object(
        bm,
        mesh_name="observatory_telescope_tube_mesh",
        obj_name="observatory_telescope_tube",
        location=(tube_centre.x, tube_centre.y, tube_centre.z),
        collection_name=COLLECTION,
        material=material,
        rotation_euler=(0.0, ay, 0.0),
    )

    # 3-leg tripod: legs splay outward from the mount point at 120 deg
    # intervals around the local vertical. Each leg is a cylinder along
    # local Z, tilted outward by TRIPOD_LEG_SPLAY_DEG.
    legs = []
    splay = math.radians(TRIPOD_LEG_SPLAY_DEG)
    for i in range(3):
        # Azimuth around the mount point. Offset by 30 deg so no leg
        # points straight at the tube axis (which is +X here).
        az = math.radians(30.0 + i * 120.0)
        bm = bmesh.new()
        uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
        _lib.bm_add_cylinder(
            bm, uv,
            center=(0.0, 0.0, 0.0),
            radius=TRIPOD_LEG_RADIUS, height=TRIPOD_LEG_LENGTH,
            color_key="dirt_path",
            segments=8,
        )
        # Leg direction: tipped outward (radial) by `splay` from straight
        # down. The TOP of the leg sits at the mount point; the bottom
        # sits TRIPOD_LEG_LENGTH below along that direction.
        leg_dir = Vector((math.sin(splay) * math.cos(az),
                          math.sin(splay) * math.sin(az),
                          -math.cos(splay)))
        leg_centre = Vector((mount_x, mount_y, mount_z)) \
            + leg_dir * (TRIPOD_LEG_LENGTH * 0.5)
        # Rotate local +Z to align with leg_dir. Use Vector.rotation_difference.
        rot_quat = Vector((0.0, 0.0, 1.0)).rotation_difference(leg_dir)
        rot_euler = rot_quat.to_euler('XYZ')
        leg = _lib.bm_finalize_to_object(
            bm,
            mesh_name=f"observatory_telescope_leg_{i + 1}_mesh",
            obj_name=f"observatory_telescope_leg_{i + 1}",
            location=(leg_centre.x, leg_centre.y, leg_centre.z),
            collection_name=COLLECTION,
            material=material,
            rotation_euler=(rot_euler.x, rot_euler.y, rot_euler.z),
        )
        legs.append(leg)

    return tube, legs


def _build_door(material, ground_z):
    """Decorative timber door on the NORTH face of the shaft (+Y in Blender).

    Player walks south from spawn and approaches the tower head-on from the
    north, so the door faces them. Sits 1cm in front of the curved cylinder
    surface to avoid z-fighting.
    """
    cx = SECTION_RUNTIME_X
    cy = SECTION_RUNTIME_Z

    door_y = cy + SHAFT_RADIUS + (DOOR_THICKNESS * 0.5) + 0.01
    door_centre_z = ground_z + DOOR_HEIGHT * 0.5

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(DOOR_WIDTH * 0.5, DOOR_THICKNESS * 0.5,
                      DOOR_HEIGHT * 0.5),
        color_key="wood_lantern_body",
    )
    door = _lib.bm_finalize_to_object(
        bm,
        mesh_name="observatory_door_mesh",
        obj_name="observatory_door",
        location=(cx, door_y, door_centre_z),
        collection_name=COLLECTION,
        material=material,
    )
    return door, door_y


# ============================================================================
# Artifact builders. Each returns the list of bpy objects belonging to the
# artifact so we can compute a union bbox for its collider.
# ============================================================================


def _artifact_anchor(angle_deg):
    """Return (runtime_x, runtime_z) for an artifact at `angle_deg` measured
    counter-clockwise from +X (east) in the Blender XY plane. The artifact
    sits ARTIFACT_RADIUS metres from the tower centre. Caller samples
    height_at separately."""
    rad = math.radians(angle_deg)
    rx = SECTION_RUNTIME_X + ARTIFACT_RADIUS * math.cos(rad)
    rz = SECTION_RUNTIME_Z + ARTIFACT_RADIUS * math.sin(rad)
    return rx, rz


def _build_artifact_lectern(material, angle_deg):
    """Mini reading lectern: small pedestal + tilted slab, no scroll.

    Slab tilts toward the tower (so a reader standing outside looks at the
    page). Tilt axis is perpendicular to the radial direction; we rotate
    +20 deg around that axis. Returns list of objects in this artifact.
    """
    rx, rz = _artifact_anchor(angle_deg)
    ground = _lib.height_at(rx, rz)

    pedestal_centre_z = ground + LECTERN_PEDESTAL_H * 0.5
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(LECTERN_PEDESTAL_HX, LECTERN_PEDESTAL_HY,
                      LECTERN_PEDESTAL_H * 0.5),
        color_key="rock_mid",
    )
    pedestal = _lib.bm_finalize_to_object(
        bm,
        mesh_name="observatory_artifact_lectern_pedestal_mesh",
        obj_name="observatory_artifact_lectern_pedestal",
        location=(rx, rz, pedestal_centre_z),
        collection_name=COLLECTION,
        material=material,
    )

    # Slab on top, tilted toward tower centre. Radial unit vector from
    # tower -> artifact is (cos(a), sin(a), 0); tilt axis perpendicular
    # to that in XY plane is (-sin(a), cos(a), 0). Rotating around it by
    # +LECTERN_SLAB_TILT_DEG via right-hand rule tips the slab top normal
    # AWAY from the tower; we want toward, so rotate by -tilt.
    rad = math.radians(angle_deg)
    radial = Vector((math.cos(rad), math.sin(rad), 0.0))
    tilt_axis = Vector((-math.sin(rad), math.cos(rad), 0.0))
    tilt_rot = Matrix.Rotation(math.radians(-LECTERN_SLAB_TILT_DEG),
                               4, tilt_axis)
    rot_euler = tilt_rot.to_euler('XYZ')

    slab_centre_z = ground + LECTERN_PEDESTAL_H + LECTERN_SLAB_HZ
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(LECTERN_SLAB_HX, LECTERN_SLAB_HY, LECTERN_SLAB_HZ),
        color_key="wood_lantern_body",
    )
    slab = _lib.bm_finalize_to_object(
        bm,
        mesh_name="observatory_artifact_lectern_slab_mesh",
        obj_name="observatory_artifact_lectern_slab",
        location=(rx, rz, slab_centre_z),
        collection_name=COLLECTION,
        material=material,
        rotation_euler=(rot_euler.x, rot_euler.y, rot_euler.z),
    )
    # Quiet the unused-var linter; `radial` documents intent above.
    _ = radial
    return [pedestal, slab]


def _build_artifact_scrolls(material, angle_deg):
    """Small stone base plate + 3 horizontal parchment cylinders stacked.

    Scroll axes run TANGENT to the tower so the stack pyramids vertically.
    Stack pattern: 2 on the bottom, 1 on top, like a small woodpile.
    """
    rx, rz = _artifact_anchor(angle_deg)
    ground = _lib.height_at(rx, rz)

    # Base plate.
    base_centre_z = ground + SCROLL_BASE_HZ
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(SCROLL_BASE_HX, SCROLL_BASE_HY, SCROLL_BASE_HZ),
        color_key="rock_mid",
    )
    base = _lib.bm_finalize_to_object(
        bm,
        mesh_name="observatory_artifact_scrolls_base_mesh",
        obj_name="observatory_artifact_scrolls_base",
        location=(rx, rz, base_centre_z),
        collection_name=COLLECTION,
        material=material,
    )

    # Scroll axis: tangent to the tower. Tangent = (-sin(a), cos(a), 0).
    rad = math.radians(angle_deg)
    tangent = Vector((-math.sin(rad), math.cos(rad), 0.0))
    # Rotate local +Z (cylinder axis) to align with tangent.
    rot_quat = Vector((0.0, 0.0, 1.0)).rotation_difference(tangent)
    rot_euler = rot_quat.to_euler('XYZ')

    base_top_z = ground + SCROLL_BASE_HZ * 2.0
    # First two scrolls side-by-side on the base, separated along the
    # PERPENDICULAR axis (radial direction), centres at base_top + r.
    bottom_z = base_top_z + SCROLL_RADIUS
    perp = Vector((math.cos(rad), math.sin(rad), 0.0))
    sep = SCROLL_RADIUS * 1.05   # touching with a hair of clearance

    objs = [base]
    for i, offset in enumerate((-sep, +sep)):
        pos = Vector((rx, rz, bottom_z)) + perp * offset
        bm = bmesh.new()
        uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
        _lib.bm_add_cylinder(
            bm, uv,
            center=(0.0, 0.0, 0.0),
            radius=SCROLL_RADIUS, height=SCROLL_LENGTH,
            color_key="sun_rim_warm",
            segments=12,
        )
        scroll = _lib.bm_finalize_to_object(
            bm,
            mesh_name=f"observatory_artifact_scroll_{i + 1}_mesh",
            obj_name=f"observatory_artifact_scroll_{i + 1}",
            location=(pos.x, pos.y, pos.z),
            collection_name=COLLECTION,
            material=material,
            rotation_euler=(rot_euler.x, rot_euler.y, rot_euler.z),
        )
        objs.append(scroll)

    # Top scroll: sits in the valley between the bottom two, centre is
    # SCROLL_RADIUS * sqrt(3) above the line of the bottom centres.
    top_z = bottom_z + SCROLL_RADIUS * math.sqrt(3.0)
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cylinder(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        radius=SCROLL_RADIUS, height=SCROLL_LENGTH,
        color_key="sun_rim_warm",
        segments=12,
    )
    top_scroll = _lib.bm_finalize_to_object(
        bm,
        mesh_name="observatory_artifact_scroll_3_mesh",
        obj_name="observatory_artifact_scroll_3",
        location=(rx, rz, top_z),
        collection_name=COLLECTION,
        material=material,
        rotation_euler=(rot_euler.x, rot_euler.y, rot_euler.z),
    )
    objs.append(top_scroll)

    return objs


def _build_artifact_books(material, angle_deg):
    """3 stacked book cuboids. Largest on bottom, smallest on top. Top face
    of each book gets sand_gravel to suggest paper pages; sides stay
    wood_lantern_body for the covers."""
    rx, rz = _artifact_anchor(angle_deg)
    ground = _lib.height_at(rx, rz)

    objs = []
    current_bottom_z = ground
    for i, (hx, hy, hz) in enumerate(BOOK_DIMS):
        centre_z = current_bottom_z + hz
        bm = bmesh.new()
        uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
        faces = _lib.bm_add_cuboid(
            bm, uv,
            center=(0.0, 0.0, 0.0),
            half_extents=(hx, hy, hz),
            color_key="wood_lantern_body",
        )
        # bm_add_cuboid face order = [bottom, top, -Y, +Y, -X, +X]. Repaint
        # the top face only - reads as the page edge of a closed book.
        _lib.paint_face(faces[1], uv, "sand_gravel")
        book = _lib.bm_finalize_to_object(
            bm,
            mesh_name=f"observatory_artifact_book_{i + 1}_mesh",
            obj_name=f"observatory_artifact_book_{i + 1}",
            location=(rx, rz, centre_z),
            collection_name=COLLECTION,
            material=material,
        )
        objs.append(book)
        current_bottom_z += hz * 2.0   # next book sits on this one's top

    return objs


def _build_artifact_chest(material, angle_deg):
    """Chest body + open lid hinged at the back + 3 instruments inside.

    Lid hinge runs along the artifact's TANGENT (relative to tower). When
    closed the lid would lie flat on top of the body; we rotate it open
    ~80 deg around the hinge so it tips backward (away from tower).
    """
    rx, rz = _artifact_anchor(angle_deg)
    ground = _lib.height_at(rx, rz)

    # Local axes for the chest: front faces AWAY from tower (radial outward),
    # back faces tower. With the chest centred at (rx, rz), the back hinge
    # line runs tangent to the tower at body's BACK edge (the edge closest
    # to the tower).
    rad = math.radians(angle_deg)
    radial = Vector((math.cos(rad), math.sin(rad), 0.0))
    tangent = Vector((-math.sin(rad), math.cos(rad), 0.0))

    # Body.
    body_centre_z = ground + CHEST_BODY_HZ
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(CHEST_BODY_HX, CHEST_BODY_HY, CHEST_BODY_HZ),
        color_key="wood_lantern_body",
    )
    body = _lib.bm_finalize_to_object(
        bm,
        mesh_name="observatory_artifact_chest_body_mesh",
        obj_name="observatory_artifact_chest_body",
        location=(rx, rz, body_centre_z),
        collection_name=COLLECTION,
        material=material,
    )

    # Author the lid in the chest's LOCAL frame (radial = +X local,
    # tangent = +Y local, up = +Z local) then transform into world space
    # via the chest's azimuth.
    #
    # In local frame the chest body half-extents are
    #   (radial, tangent, up) = (CHEST_BODY_HX, CHEST_BODY_HY, CHEST_BODY_HZ).
    # Hinge edge runs along local +Y at local x=-CHEST_BODY_HX (back,
    # toward tower), z=+CHEST_BODY_HZ (top of body).
    #
    # When closed the lid lies flat on the body top; centre at local
    # (0, 0, +CHEST_BODY_HZ + thick/2). Rotating around local +Y by NEGATIVE
    # CHEST_LID_OPEN_DEG sends the free edge (+X end) UP and toward -X
    # (backward, over the hinge), which is the open-backward pose we want.
    # Standard right-handed rotation around +Y by ay maps (x, y, z) to
    # (x cos(ay) + z sin(ay), y, -x sin(ay) + z cos(ay)). With ay = -80 deg,
    # the free edge moves to ~(-0.17 HX, 0, +0.98 HX) relative to hinge -
    # lid stands at 10 deg shy of vertical, tipped backward.
    lid_open_rad = -math.radians(CHEST_LID_OPEN_DEG)
    pivot_to_centre = Vector((CHEST_BODY_HX, 0.0, CHEST_LID_THICK * 0.5))
    rot_pivot = Matrix.Rotation(lid_open_rad, 4, (0.0, 1.0, 0.0))
    pivot_to_centre_rot = rot_pivot @ pivot_to_centre
    lid_local_centre = Vector((-CHEST_BODY_HX, 0.0, CHEST_BODY_HZ)) \
        + pivot_to_centre_rot

    # Transform local frame -> world frame: local +X -> radial,
    # local +Y -> tangent, local +Z -> world +Z.
    # World position = chest origin + lid_local_x * radial + lid_local_y *
    # tangent + lid_local_z * up.
    chest_origin = Vector((rx, rz, body_centre_z))
    lid_world = chest_origin \
        + radial * lid_local_centre.x \
        + tangent * lid_local_centre.y \
        + Vector((0.0, 0.0, 1.0)) * lid_local_centre.z

    # Lid orientation: in LOCAL frame the lid is a cuboid with half-extents
    # (CHEST_BODY_HX, CHEST_BODY_HY, CHEST_LID_THICK*0.5), tipped by
    # ay around +Y. Compose that with the azimuth that maps local -> world.
    # Azimuth rotation around world +Z by `angle_deg` maps local +X (radial)
    # to world (cos a, sin a, 0).
    az_rot = Matrix.Rotation(rad, 4, (0.0, 0.0, 1.0))
    local_rot = Matrix.Rotation(lid_open_rad, 4, (0.0, 1.0, 0.0))
    combined = az_rot @ local_rot
    rot_euler = combined.to_euler('XYZ')

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(CHEST_BODY_HX, CHEST_BODY_HY, CHEST_LID_THICK * 0.5),
        color_key="wood_lantern_body",
    )
    lid = _lib.bm_finalize_to_object(
        bm,
        mesh_name="observatory_artifact_chest_lid_mesh",
        obj_name="observatory_artifact_chest_lid",
        location=(lid_world.x, lid_world.y, lid_world.z),
        collection_name=COLLECTION,
        material=material,
        rotation_euler=(rot_euler.x, rot_euler.y, rot_euler.z),
    )

    # 3 small instruments inside the chest, sitting on the body floor.
    # Two cuboids + one cylinder, palette sand_gravel + rock_mid.
    objs = [body, lid]
    floor_z = ground + CHEST_LID_THICK   # tiny lift so they don't z-fight
    # Local positions inside the chest, expressed in the chest's local frame
    # then transformed to world. Spread along the local Y (tangent) axis.
    instruments = [
        ("cuboid", -0.10, 0.06, 0.04, "sand_gravel"),  # small cube +tangent left
        ("cuboid", +0.10, 0.05, 0.04, "rock_mid"),      # +tangent right
        ("cylinder", 0.0, 0.04, 0.10, "sand_gravel"),   # cylinder centre
    ]
    for i, item in enumerate(instruments):
        kind = item[0]
        local_y = item[1]
        size_a = item[2]
        size_b = item[3]
        color = item[4]
        inst_world_xy = Vector((rx, rz, 0.0)) + tangent * local_y
        inst_z = floor_z + size_b
        bm = bmesh.new()
        uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
        if kind == "cuboid":
            _lib.bm_add_cuboid(
                bm, uv,
                center=(0.0, 0.0, 0.0),
                half_extents=(size_a, size_a, size_b),
                color_key=color,
            )
        else:
            _lib.bm_add_cylinder(
                bm, uv,
                center=(0.0, 0.0, 0.0),
                radius=size_a, height=size_b * 2.0,
                color_key=color,
                segments=10,
            )
        inst = _lib.bm_finalize_to_object(
            bm,
            mesh_name=f"observatory_artifact_chest_instrument_{i + 1}_mesh",
            obj_name=f"observatory_artifact_chest_instrument_{i + 1}",
            location=(inst_world_xy.x, inst_world_xy.y, inst_z),
            collection_name=COLLECTION,
            material=material,
        )
        objs.append(inst)

    return objs


# ============================================================================
# Colliders
# ============================================================================


def _build_tower_collider(material, ground_z):
    """tube_observatory: r=1.5m, h=4m, centred at section root."""
    cx = SECTION_RUNTIME_X
    cy = SECTION_RUNTIME_Z
    centre_z = ground_z + SHAFT_HEIGHT * 0.5
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cylinder(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        radius=SHAFT_RADIUS, height=SHAFT_HEIGHT,
        color_key="rock_mid",
        segments=SHAFT_SIDE_SEGMENTS,
    )
    return _lib.bm_finalize_to_object(
        bm,
        mesh_name="tube_observatory_mesh",
        obj_name="tube_observatory",
        location=(cx, cy, centre_z),
        collection_name=COLLECTION,
        material=material,
        hide=True,
    )


def _build_artifact_collider(material, obj_list, collider_name):
    """Cuboid collider sized to the union world-space bbox of obj_list.

    Per CLAUDE.md rule 5 the collider must match the visible mesh: we
    centre on (bbox.min.z + bbox.max.z)/2 and use bbox/2 half-extents.
    """
    minc, maxc = _group_world_bbox(obj_list)
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
        mesh_name=f"{collider_name}_mesh",
        obj_name=collider_name,
        location=(centre.x, centre.y, centre.z),
        collection_name=COLLECTION,
        material=material,
        hide=True,
    )


# ============================================================================
# Refs
# ============================================================================


def _place_refs(ground_z, door_y):
    """4 ref empties anchored to the skills section."""
    cx = SECTION_RUNTIME_X
    cy = SECTION_RUNTIME_Z

    section_loc = (cx, cy, ground_z)

    _lib.ref_empty(
        "refZoneBounding_skills",
        section_loc,
        radius=13.0,
    )
    _lib.ref_empty(
        "refZoneFrustum_skills",
        section_loc,
        radius=10.0,
    )
    # Interactive point at the north door, 1.5m above ground.
    _lib.ref_empty(
        "refInteractivePoint_skills",
        (cx, door_y, ground_z + 1.5),
        radius=0.5,
    )
    _lib.ref_empty(
        "refRespawn_skills",
        section_loc,
        radius=0.5,
    )


# ============================================================================
# Entry point
# ============================================================================


def main():
    _lib.clear_collection("sections/skills")

    material = _lib.get_palette_material()

    ground_z = _lib.height_at(SECTION_RUNTIME_X, SECTION_RUNTIME_Z)

    _build_shaft(material, ground_z)
    _, dome_apex_z = _build_dome(material, ground_z + SHAFT_HEIGHT)
    _build_cupola(material, dome_apex_z)
    _build_telescope(material, ground_z + SHAFT_HEIGHT)
    _, door_y = _build_door(material, ground_z)

    # Artifacts flank the north approach (angle 90 deg) without blocking
    # the door sightline. NE = +45, NW = +135, E = 0, W = 180; the closest
    # to north are NE/NW at +/- 45 deg, comfortably outside the central
    # approach corridor.
    lectern_objs = _build_artifact_lectern(material, 45.0)
    scrolls_objs = _build_artifact_scrolls(material, 135.0)
    books_objs = _build_artifact_books(material, 0.0)
    chest_objs = _build_artifact_chest(material, 180.0)

    _build_tower_collider(material, ground_z)
    _build_artifact_collider(material, lectern_objs, "cuboid_artifact_lectern")
    _build_artifact_collider(material, scrolls_objs, "cuboid_artifact_scrolls")
    _build_artifact_collider(material, books_objs, "cuboid_artifact_books")
    _build_artifact_collider(material, chest_objs, "cuboid_artifact_chest")

    _place_refs(ground_z, door_y)

    blend_path = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "world.blend"))
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    skills_coll = bpy.data.collections.get("skills")
    visible_count = 0
    if skills_coll is not None:
        visible_count = len([o for o in skills_coll.objects if not o.hide_viewport])

    print(
        f"{_lib.LOG_PREFIX}[phase-05] OK - skills: observatory, "
        f"{visible_count} visible meshes, 5 colliders, 4 refs"
    )
    print(f"{_lib.LOG_PREFIX}[phase-05] saved -> {blend_path}")


if __name__ == "__main__":
    main()
