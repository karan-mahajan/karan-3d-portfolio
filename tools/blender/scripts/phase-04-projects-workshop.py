"""
Phase 4: Projects workshop pavilion (E cardinal, +70m east of spawn).

What this produces (after Run Script + save):
- `sections/projects` collection populated with these visible mesh groups:
    * `workshop_wall_back`        - 6m N-S stone half-wall on the EAST side.
    * `workshop_wall_north`       - 5m E-W stone side wall on the NORTH side.
    * `workshop_wall_south`       - mirror of the north wall.
    * `workshop_slat_back`        - timber slat band capping the back wall.
    * `workshop_slat_north`       - timber slat band capping the north wall.
    * `workshop_slat_south`       - timber slat band capping the south wall.
    * `workshop_roof_north`       - sloped timber roof half (north pitch).
    * `workshop_roof_south`       - sloped timber roof half (south pitch).
    * `workshop_showcase_panel`   - 4 x 2.5m timber backing on back-wall
                                    interior; runtime billboard mounts here.
    * `workshop_anvil`            - 0.6 x 0.3 x 0.5m cuboid anvil at centre,
                                    top face repainted to sand_gravel.
    * `workshop_forge_body`       - 1.2 x 1.0 x 0.9m hearth in back-left
                                    corner (NE interior).
    * `forge_embers_emissive`     - recessed coal-pit disc on the forge top.
                                    Name flags it for runtime emissive swap.
    * `workshop_forge_chimney`    - square stone chimney up through the roof.
    * `workshop_tool_hammer_1..3` - hammer-template tools on the back wall.
    * `workshop_tool_tongs_1..2`  - tongs-template tools on the back wall.
- Colliders (hidden in viewport + render, palette material cosmetic only):
    * `cuboid_workshop_wall_back`   - half-extents (0.15, 3.0, 0.8) Blender
                                      = E-W 0.3m thick, N-S 6m, height 1.6m.
    * `cuboid_workshop_wall_left`   - NORTH side wall (player-relative left
                                      when facing east into the pavilion).
                                      half-extents (2.5, 0.15, 0.8).
    * `cuboid_workshop_wall_right`  - SOUTH side wall (mirror).
    * `cuboid_anvil_base`           - half-extents (0.3, 0.15, 0.25).
    * `tube_forge`                  - radius 0.7m, height 0.9m cylinder.
- 6 ref empties in `refs`:
    `refZoneBounding_projects`, `refZoneFrustum_projects`,
    `refInteractivePoint_projects`, `refShowcaseMount` (with width/height
    userdata), `refForge`, `refRespawn_projects`.

Pavilion geometry & orientation (single source of truth for this script):
- The plan's parenthetical (plan line 276) is authoritative: "the player
  walking east from spawn approaches the open front". So the OPEN front
  faces WEST (toward spawn at origin), the BACK wall (with the showcase
  panel) faces EAST. Player enters by walking east into the open west face.
- "Back-left forge corner" with the player facing east into the back wall
  = player's LEFT = NORTH side of the interior. So the forge sits in the
  NORTH-EAST interior corner.
- Footprint is 6m N-S (the back wall holds the 4m showcase panel, so the
  back wall must be the long axis) x 5m E-W. Wall thickness 0.3m, stone
  height 1.6m + 0.4m timber slat band = 2.0m wall top, roof apex 4m total.
- Collider names use `_left` / `_right` per the plan even though
  geographically left=north / right=south (player frame from entry).

Coordinate convention: authored in Blender Z-up. Runtime XYZ maps to Blender
(x, z, y) - Blender X = runtime X east-west, Blender Y = runtime Z
north-south, Blender Z = runtime Y height. Every Y position samples
`_lib.height_at(x, z)` so geometry sits on the heightfield.

Idempotent: re-running clears the `sections/projects` collection first.

How to run:
  1. Open tools/blender/world.blend in Blender 4.2+.
  2. Scripting workspace -> Text Editor -> Open -> phase-04-projects-workshop.py.
  3. Run Script (Alt+P).
  4. Script saves world.blend automatically (wm.save_as_mainfile).
"""

import os
import sys
import math

import bpy
import bmesh
from mathutils import Vector


# Mirror Phase 0..3's _script_dir() - Blender's Text Editor sets __file__
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


COLLECTION = "sections/projects"

# Section root (runtime coords). The plan locks +70m east, 0 north-south.
SECTION_RUNTIME_X = 70.0
SECTION_RUNTIME_Z = 0.0

# Pavilion footprint and heights (metres). The back wall runs N-S so it
# can host the 4m showcase panel; the side walls run E-W.
FOOTPRINT_NS = 6.0   # back wall length (Blender Y)
FOOTPRINT_EW = 5.0   # side wall length (Blender X)
WALL_THICK = 0.3
STONE_H = 1.6
SLAT_H = 0.4
SLAT_INSET = 0.1     # slat band sits 10cm narrower than the wall it caps
WALL_TOTAL_H = STONE_H + SLAT_H  # = 2.0m
ROOF_APEX_Z_LOCAL = 4.0          # apex height above section root ground
ROOF_OVERHANG = 0.3              # how far the roof extends past the walls
ROOF_THICK = 0.08                # thickness of each sloped roof slab

# Back wall interior face X coordinate (relative to section centre). Back
# wall outer face is at +EW/2; inner face is +EW/2 - WALL_THICK.
_BACK_WALL_CENTRE_X = (FOOTPRINT_EW * 0.5) - (WALL_THICK * 0.5)
_BACK_WALL_INNER_X = (FOOTPRINT_EW * 0.5) - WALL_THICK

# Showcase panel: 4m wide (N-S) x 2.5m tall, mounted on the interior face
# of the back wall, centred vertically at 1.4m above ground (so it spans
# 0.15m..2.65m roughly).
SHOWCASE_WIDTH = 4.0
SHOWCASE_HEIGHT = 2.5
SHOWCASE_CENTRE_Z = 1.4   # height above section root ground (centre)
SHOWCASE_OFFSET = 0.01    # how far in front of back wall inner face

# Anvil dimensions (Blender axes; X=E-W, Y=N-S, Z=height).
ANVIL_EW = 0.6
ANVIL_NS = 0.3
ANVIL_H = 0.5

# Forge body dimensions and position. Forge sits in the NORTH-EAST interior
# corner (player's "back-left" when facing east). Centre is offset from
# inner corner by half its own size + a small inset so it doesn't kiss the
# walls.
FORGE_EW = 1.2
FORGE_NS = 1.0
FORGE_H = 0.9
FORGE_WALL_GAP = 0.15

# Forge chimney: square pillar, rises from the BACK of the forge body up
# 2.5m above the roof apex.
CHIMNEY_HALF = 0.25
CHIMNEY_TOP_ABOVE_APEX = 2.5

# Tools on the back wall interior. Heads palette rock_mid, handles
# wood_lantern_body. Mounted at ~1.4m above ground along the inside face.
TOOL_MOUNT_Z = 1.4
TOOL_BACK_OFFSET = 0.05     # how far in front of inner face the tools sit


# ============================================================================
# Builders
# ============================================================================


def _build_stone_wall(material, name, centre, half_extents):
    """Stone half-wall cuboid. `centre` and `half_extents` are Blender axes."""
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=half_extents,
        color_key="rock_mid",
    )
    return _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"{name}_mesh",
        obj_name=name,
        location=centre,
        collection_name=COLLECTION,
        material=material,
    )


def _build_timber_slat(material, name, centre, half_extents):
    """Timber slat band cuboid sitting atop a stone wall."""
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=half_extents,
        color_key="wood_lantern_body",
    )
    return _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"{name}_mesh",
        obj_name=name,
        location=centre,
        collection_name=COLLECTION,
        material=material,
    )


def _build_walls(material, ground_z):
    """Three stone half-walls + three timber slat bands.

    Back wall is on the +X side (EAST face of pavilion), 6m long N-S.
    Side walls are on +Y (NORTH) and -Y (SOUTH), 5m long E-W. The west
    side is intentionally open.

    Walls are positioned in WORLD coordinates already - we don't use a
    section-root empty for this, because every collider and ref also
    needs absolute world placement and a section transform would force
    extra bookkeeping.
    """
    cx = SECTION_RUNTIME_X
    cy = SECTION_RUNTIME_Z  # Blender Y = runtime Z

    stone_half_z = STONE_H * 0.5
    stone_centre_z = ground_z + stone_half_z

    slat_half_z = SLAT_H * 0.5
    slat_centre_z = ground_z + STONE_H + slat_half_z

    # Back wall (EAST face). Its inner face sits at X = cx + EW/2 - WALL_THICK.
    back_centre = (cx + _BACK_WALL_CENTRE_X, cy, stone_centre_z)
    back_half = (WALL_THICK * 0.5, FOOTPRINT_NS * 0.5, stone_half_z)
    back_wall = _build_stone_wall(material, "workshop_wall_back",
                                  back_centre, back_half)

    # Side walls run E-W. Their length covers the full footprint EW from the
    # OPEN west edge to where they meet the back wall on the east.
    side_half_x = FOOTPRINT_EW * 0.5
    # North wall: centred at +Y = +NS/2 - WALL_THICK/2 so its outer face
    # aligns with the footprint perimeter.
    north_centre = (cx,
                    cy + (FOOTPRINT_NS * 0.5) - (WALL_THICK * 0.5),
                    stone_centre_z)
    north_half = (side_half_x, WALL_THICK * 0.5, stone_half_z)
    north_wall = _build_stone_wall(material, "workshop_wall_north",
                                   north_centre, north_half)

    south_centre = (cx,
                    cy - (FOOTPRINT_NS * 0.5) + (WALL_THICK * 0.5),
                    stone_centre_z)
    south_half = (side_half_x, WALL_THICK * 0.5, stone_half_z)
    south_wall = _build_stone_wall(material, "workshop_wall_south",
                                   south_centre, south_half)

    # Timber slat bands - same footprint as their stone walls but with
    # SLAT_INSET pulled in on the thin axis so the slat reads as a band, not
    # just a continuation of the wall.
    back_slat_half = (WALL_THICK * 0.5 - SLAT_INSET * 0.5,
                      FOOTPRINT_NS * 0.5,
                      slat_half_z)
    back_slat_centre = (cx + _BACK_WALL_CENTRE_X, cy, slat_centre_z)
    back_slat = _build_timber_slat(material, "workshop_slat_back",
                                   back_slat_centre, back_slat_half)

    north_slat_half = (side_half_x,
                       WALL_THICK * 0.5 - SLAT_INSET * 0.5,
                       slat_half_z)
    north_slat = _build_timber_slat(material, "workshop_slat_north",
                                    (cx,
                                     cy + (FOOTPRINT_NS * 0.5)
                                        - (WALL_THICK * 0.5),
                                     slat_centre_z),
                                    north_slat_half)
    south_slat = _build_timber_slat(material, "workshop_slat_south",
                                    (cx,
                                     cy - (FOOTPRINT_NS * 0.5)
                                        + (WALL_THICK * 0.5),
                                     slat_centre_z),
                                    north_slat_half)

    return back_wall, north_wall, south_wall, back_slat, north_slat, south_slat


def _build_roof(material, ground_z):
    """Two sloped quads meeting at a 4m apex line that runs N-S.

    Apex runs along the line (cx, cy +/- ..., apex_z). Each pitch is a thin
    slab: built flat (long axis along Blender X, span along Y), then rotated
    around Y so it tips down toward its eave. With an N-S apex the two
    pitches face EAST and WEST; we name them by the direction they slope
    DOWN toward (roof_east tips down toward the east eave, etc).

    The roof overhangs the walls by ROOF_OVERHANG so it reads as a shelter
    rather than a slab flush with the wall tops.
    """
    cx = SECTION_RUNTIME_X
    cy = SECTION_RUNTIME_Z
    apex_z = ground_z + ROOF_APEX_Z_LOCAL
    wall_top_z = ground_z + WALL_TOTAL_H

    apex_x = cx
    eave_x_east = cx + (FOOTPRINT_EW * 0.5) + ROOF_OVERHANG
    eave_x_west = cx - (FOOTPRINT_EW * 0.5) - ROOF_OVERHANG
    eave_z = wall_top_z

    # Half-width of a pitch along its slope direction (apex to eave).
    east_dx = eave_x_east - apex_x          # > 0
    east_dz = eave_z - apex_z               # < 0 (eave below apex)
    east_slope = math.hypot(east_dx, east_dz)
    # Tilt angle: positive raw angle measured down from horizontal +X axis.
    east_tilt = math.atan2(-east_dz, east_dx)   # > 0

    west_dx = apex_x - eave_x_west          # > 0 (mirror; |west_dx|)
    west_dz = eave_z - apex_z               # < 0
    west_slope = math.hypot(west_dx, west_dz)
    west_tilt = math.atan2(-west_dz, west_dx)   # > 0

    roof_half_y = (FOOTPRINT_NS * 0.5) + ROOF_OVERHANG

    def build_pitch(name, slope_len, tilt, eave_x):
        """Build one roof pitch. `tilt` is the positive angle (radians)
        by which the slab tips down from horizontal. `eave_x` is the
        outer X coordinate (eave). The pitch's inner short edge meets the
        apex line; the outer short edge meets the eave."""
        bm = bmesh.new()
        uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
        _lib.bm_add_cuboid(
            bm, uv,
            center=(0.0, 0.0, 0.0),
            half_extents=(slope_len * 0.5, roof_half_y, ROOF_THICK * 0.5),
            color_key="wood_lantern_body",
        )
        # Midpoint of slab in world space: half-way between apex and eave
        # in both X and Z.
        mid_x = (apex_x + eave_x) * 0.5
        mid_z = (apex_z + eave_z) * 0.5
        # Rotation around Y: positive Y-rotation tilts +X end DOWN. For the
        # east pitch (eave at +X) we want the +X end down, so rotation = +tilt.
        # For the west pitch (eave at -X) we want the -X end down, so the
        # +X end goes UP -> rotation = -tilt.
        if eave_x > apex_x:
            rot_y = +tilt
        else:
            rot_y = -tilt
        return _lib.bm_finalize_to_object(
            bm,
            mesh_name=f"{name}_mesh",
            obj_name=name,
            location=(mid_x, cy, mid_z),
            collection_name=COLLECTION,
            material=material,
            rotation_euler=(0.0, rot_y, 0.0),
        )

    east_pitch = build_pitch("workshop_roof_east", east_slope,
                             east_tilt, eave_x_east)
    west_pitch = build_pitch("workshop_roof_west", west_slope,
                             west_tilt, eave_x_west)

    return east_pitch, west_pitch, apex_z


def _build_showcase_panel(material, ground_z):
    """Flat timber panel on back-wall INTERIOR. Mounted SHOWCASE_OFFSET
    in front of the inner face so it reads as a distinct backing for the
    runtime Billboards.js showcase."""
    cx = SECTION_RUNTIME_X
    cy = SECTION_RUNTIME_Z
    # Inner face of back wall sits at X = cx + (EW/2 - WALL_THICK).
    panel_x = cx + _BACK_WALL_INNER_X - SHOWCASE_OFFSET
    panel_centre = (panel_x, cy, ground_z + SHOWCASE_CENTRE_Z)
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    # Thin slab: X thickness 0.02m, Y = panel width, Z = panel height.
    panel_thickness = 0.02
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(panel_thickness * 0.5,
                      SHOWCASE_WIDTH * 0.5,
                      SHOWCASE_HEIGHT * 0.5),
        color_key="wood_lantern_body",
    )
    return _lib.bm_finalize_to_object(
        bm,
        mesh_name="workshop_showcase_panel_mesh",
        obj_name="workshop_showcase_panel",
        location=panel_centre,
        collection_name=COLLECTION,
        material=material,
    )


def _build_anvil(material, ground_z):
    """Single cuboid anvil at pavilion centre. Top face repainted
    sand_gravel to read as worn striking surface."""
    cx = SECTION_RUNTIME_X
    cy = SECTION_RUNTIME_Z
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    faces = _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(ANVIL_EW * 0.5, ANVIL_NS * 0.5, ANVIL_H * 0.5),
        color_key="rock_mid",
    )
    # bm_add_cuboid face order = [bottom, top, -Y, +Y, -X, +X]. Repaint top.
    _lib.paint_face(faces[1], uv, "sand_gravel")
    return _lib.bm_finalize_to_object(
        bm,
        mesh_name="workshop_anvil_mesh",
        obj_name="workshop_anvil",
        location=(cx, cy, ground_z + ANVIL_H * 0.5),
        collection_name=COLLECTION,
        material=material,
    )


def _forge_centre(ground_z):
    """World coordinates (Blender axes) for the forge body centre.

    Forge sits in the player's "back-left" corner. Player walks east from
    spawn through the open west face, looking east at the back wall.
    "Back-left" = NORTH-EAST interior corner. Body centre is inset from
    each corner wall by half its body extent + FORGE_WALL_GAP.
    """
    cx = SECTION_RUNTIME_X
    cy = SECTION_RUNTIME_Z
    forge_x = cx + (FOOTPRINT_EW * 0.5) - WALL_THICK \
              - (FORGE_EW * 0.5) - FORGE_WALL_GAP
    forge_y = cy + (FOOTPRINT_NS * 0.5) - WALL_THICK \
              - (FORGE_NS * 0.5) - FORGE_WALL_GAP
    forge_z = ground_z + FORGE_H * 0.5
    return forge_x, forge_y, forge_z


def _build_forge(material, ground_z, apex_z):
    """Forge body + embers disc + chimney."""
    forge_x, forge_y, forge_z = _forge_centre(ground_z)

    # Body
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(FORGE_EW * 0.5, FORGE_NS * 0.5, FORGE_H * 0.5),
        color_key="rock_mid",
    )
    body = _lib.bm_finalize_to_object(
        bm,
        mesh_name="workshop_forge_body_mesh",
        obj_name="workshop_forge_body",
        location=(forge_x, forge_y, forge_z),
        collection_name=COLLECTION,
        material=material,
    )

    # Embers disc - thin cylinder on top of the forge body. Centre Z lands
    # at body top + half embers height so the rim of the cylinder sits flush
    # with the body top.
    embers_radius = 0.35
    embers_height = 0.05
    embers_top_z = ground_z + FORGE_H
    embers_centre_z = embers_top_z - embers_height * 0.5  # slightly recessed
    bm_e = bmesh.new()
    e_uv = bm_e.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cylinder(
        bm_e, e_uv,
        center=(0.0, 0.0, 0.0),
        radius=embers_radius, height=embers_height,
        color_key="lantern_warm",
        segments=24,
    )
    embers = _lib.bm_finalize_to_object(
        bm_e,
        mesh_name="forge_embers_emissive_mesh",
        obj_name="forge_embers_emissive",
        location=(forge_x, forge_y, embers_centre_z),
        collection_name=COLLECTION,
        material=material,
    )

    # Chimney: square cuboid rising from the BACK of the forge body. "Back"
    # in player terms = the wall side, which here is the EAST (+X) edge of
    # the forge body. Chimney top sits 2.5m above the roof apex.
    chimney_top_z = apex_z + CHIMNEY_TOP_ABOVE_APEX
    chimney_bottom_z = forge_z + FORGE_H * 0.5  # body top
    chimney_height = chimney_top_z - chimney_bottom_z
    chimney_centre_z = (chimney_bottom_z + chimney_top_z) * 0.5
    # Place chimney near the back (+X) face of the forge body.
    chimney_x = forge_x + (FORGE_EW * 0.5) - CHIMNEY_HALF - 0.02
    bm_c = bmesh.new()
    c_uv = bm_c.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm_c, c_uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(CHIMNEY_HALF, CHIMNEY_HALF, chimney_height * 0.5),
        color_key="rock_mid",
    )
    chimney = _lib.bm_finalize_to_object(
        bm_c,
        mesh_name="workshop_forge_chimney_mesh",
        obj_name="workshop_forge_chimney",
        location=(chimney_x, forge_y, chimney_centre_z),
        collection_name=COLLECTION,
        material=material,
    )

    return body, embers, chimney


def _build_tools(material, ground_z):
    """5 small tool meshes mounted on the back-wall interior.

    Authored from 2 base templates so they can be instanced later:
    - hammer: short handle cylinder + cuboid head perpendicular to handle.
    - tongs: two narrow cuboid arms + a pivot cylinder.

    3 hammers + 2 tongs = 5 tools. Spaced evenly along the N-S axis of the
    back wall interior at Z = TOOL_MOUNT_Z. Mounted SHOWCASE_OFFSET further
    in front of the wall than the showcase panel, so they don't clip the
    panel surface.
    """
    cx = SECTION_RUNTIME_X
    cy = SECTION_RUNTIME_Z
    # Mount X: slightly in front of the back-wall inner face. Use a fixed
    # offset that keeps tools clear of the showcase panel (which sits at
    # SHOWCASE_OFFSET in front of the inner face).
    mount_x = cx + _BACK_WALL_INNER_X - SHOWCASE_OFFSET - TOOL_BACK_OFFSET

    # Position tools along the back-wall N-S axis but OUTSIDE the showcase
    # panel's 4m span so they don't overlap the panel visually. Panel covers
    # cy - 2.0..cy + 2.0 in Y; tools mount on the +Y and -Y wings.
    # Five tool positions: two on the south wing, two on the north wing,
    # and one centered low above where the panel ends.
    panel_half = SHOWCASE_WIDTH * 0.5
    # Available wing length each side: (FOOTPRINT_NS/2 - WALL_THICK) - panel_half
    wing_half = (FOOTPRINT_NS * 0.5) - WALL_THICK - panel_half
    if wing_half < 0.3:
        wing_half = 0.3   # safety; should not trigger with current dims
    # Two slots per wing.
    south_slot_1 = cy - panel_half - wing_half * 0.25
    south_slot_2 = cy - panel_half - wing_half * 0.75
    north_slot_1 = cy + panel_half + wing_half * 0.25
    north_slot_2 = cy + panel_half + wing_half * 0.75
    # Fifth tool sits between the two south slots, slightly higher.
    mid_slot = (south_slot_1 + south_slot_2) * 0.5

    objs = []

    def build_hammer(name, y_pos, mount_z):
        """Hammer template: short wood handle (Y-aligned cylinder) +
        rock_mid head (cuboid) perpendicular to handle. Whole tool fits
        in ~0.4m cube."""
        bm = bmesh.new()
        uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
        # Handle: cylinder along Y. Build along Z then rotate verts.
        handle_radius = 0.025
        handle_length = 0.30
        _lib.bm_add_cylinder(
            bm, uv,
            center=(0.0, 0.0, 0.0),
            radius=handle_radius, height=handle_length,
            color_key="wood_lantern_body",
            segments=12,
        )
        # Rotate so cylinder axis runs along Y instead of Z.
        for v in bm.verts:
            x, y, z = v.co.x, v.co.y, v.co.z
            v.co = Vector((x, z, -y))
        # Head: small cuboid at the +Y end of the handle, perpendicular.
        head_offset_y = handle_length * 0.5 + 0.05
        _lib.bm_add_cuboid(
            bm, uv,
            center=(0.0, head_offset_y, 0.0),
            half_extents=(0.04, 0.06, 0.04),
            color_key="rock_mid",
        )
        return _lib.bm_finalize_to_object(
            bm,
            mesh_name=f"{name}_mesh",
            obj_name=name,
            location=(mount_x, y_pos, mount_z),
            collection_name=COLLECTION,
            material=material,
        )

    def build_tongs(name, y_pos, mount_z):
        """Tongs template: two narrow cuboid arms forming a shallow V +
        small pivot cylinder where they meet."""
        bm = bmesh.new()
        uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
        # Two arms: each is a thin cuboid placed along the local Y, offset
        # +/- small Z so they read as opposing arms.
        arm_half_y = 0.18
        arm_half_x = 0.012
        arm_half_z = 0.012
        for sign in (+1.0, -1.0):
            _lib.bm_add_cuboid(
                bm, uv,
                center=(0.0, 0.0, sign * 0.025),
                half_extents=(arm_half_x, arm_half_y, arm_half_z),
                color_key="rock_mid",
            )
        # Pivot: small cylinder at the +Y end of the arms.
        pivot_radius = 0.02
        pivot_height = 0.06
        _lib.bm_add_cylinder(
            bm, uv,
            center=(0.0, arm_half_y, 0.0),
            radius=pivot_radius, height=pivot_height,
            color_key="wood_lantern_body",
            segments=12,
        )
        return _lib.bm_finalize_to_object(
            bm,
            mesh_name=f"{name}_mesh",
            obj_name=name,
            location=(mount_x, y_pos, mount_z),
            collection_name=COLLECTION,
            material=material,
        )

    objs.append(build_hammer("workshop_tool_hammer_1", south_slot_1,
                             ground_z + TOOL_MOUNT_Z))
    objs.append(build_hammer("workshop_tool_hammer_2", north_slot_1,
                             ground_z + TOOL_MOUNT_Z))
    objs.append(build_hammer("workshop_tool_hammer_3", mid_slot,
                             ground_z + TOOL_MOUNT_Z + 0.4))
    objs.append(build_tongs("workshop_tool_tongs_1", south_slot_2,
                            ground_z + TOOL_MOUNT_Z))
    objs.append(build_tongs("workshop_tool_tongs_2", north_slot_2,
                            ground_z + TOOL_MOUNT_Z))
    return objs


# ============================================================================
# Colliders
# ============================================================================


def _build_colliders(material, ground_z):
    """5 hidden colliders matching the visible walls + anvil + forge.

    Collider naming follows the plan: `_left` = NORTH side wall,
    `_right` = SOUTH side wall (player-relative when facing east into the
    pavilion). All cuboids are sized to the STONE half-wall only (1.6m
    height) — slats sit above and aren't player-reachable.
    """
    cx = SECTION_RUNTIME_X
    cy = SECTION_RUNTIME_Z

    stone_half_z = STONE_H * 0.5
    stone_centre_z = ground_z + stone_half_z

    # cuboid_workshop_wall_back - 6m N-S x 0.3m E-W x 1.6m tall.
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(WALL_THICK * 0.5, FOOTPRINT_NS * 0.5, stone_half_z),
        color_key="rock_mid",
    )
    back_collider = _lib.bm_finalize_to_object(
        bm,
        mesh_name="cuboid_workshop_wall_back_mesh",
        obj_name="cuboid_workshop_wall_back",
        location=(cx + _BACK_WALL_CENTRE_X, cy, stone_centre_z),
        collection_name=COLLECTION,
        material=material,
        hide=True,
    )

    # cuboid_workshop_wall_left - NORTH wall (player-left when entering east).
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(FOOTPRINT_EW * 0.5, WALL_THICK * 0.5, stone_half_z),
        color_key="rock_mid",
    )
    left_collider = _lib.bm_finalize_to_object(
        bm,
        mesh_name="cuboid_workshop_wall_left_mesh",
        obj_name="cuboid_workshop_wall_left",
        location=(cx,
                  cy + (FOOTPRINT_NS * 0.5) - (WALL_THICK * 0.5),
                  stone_centre_z),
        collection_name=COLLECTION,
        material=material,
        hide=True,
    )

    # cuboid_workshop_wall_right - SOUTH wall (mirror).
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(FOOTPRINT_EW * 0.5, WALL_THICK * 0.5, stone_half_z),
        color_key="rock_mid",
    )
    right_collider = _lib.bm_finalize_to_object(
        bm,
        mesh_name="cuboid_workshop_wall_right_mesh",
        obj_name="cuboid_workshop_wall_right",
        location=(cx,
                  cy - (FOOTPRINT_NS * 0.5) + (WALL_THICK * 0.5),
                  stone_centre_z),
        collection_name=COLLECTION,
        material=material,
        hide=True,
    )

    # cuboid_anvil_base - per plan half-extents (0.3, 0.25, 0.15) ordered
    # as the plan's runtime XYZ. Convert to Blender axes (X stays, plan Y
    # = runtime height = Blender Z, plan Z = runtime N-S = Blender Y).
    # So Blender half-extents = (0.3, 0.15, 0.25). Centre at ground + 0.25.
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        half_extents=(0.3, 0.15, 0.25),
        color_key="rock_mid",
    )
    anvil_collider = _lib.bm_finalize_to_object(
        bm,
        mesh_name="cuboid_anvil_base_mesh",
        obj_name="cuboid_anvil_base",
        location=(cx, cy, ground_z + 0.25),
        collection_name=COLLECTION,
        material=material,
        hide=True,
    )

    # tube_forge - radius 0.7m, height 0.9m per plan. Centred at forge body
    # centre (the visible forge body's footprint is 1.2 x 1.0, so r=0.7m
    # roughly inscribes it).
    forge_x, forge_y, forge_z = _forge_centre(ground_z)
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cylinder(
        bm, uv,
        center=(0.0, 0.0, 0.0),
        radius=0.7, height=0.9,
        color_key="rock_mid",
        segments=24,
    )
    forge_collider = _lib.bm_finalize_to_object(
        bm,
        mesh_name="tube_forge_mesh",
        obj_name="tube_forge",
        location=(forge_x, forge_y, forge_z),
        collection_name=COLLECTION,
        material=material,
        hide=True,
    )

    return (back_collider, left_collider, right_collider,
            anvil_collider, forge_collider)


# ============================================================================
# Refs
# ============================================================================


def _place_refs(ground_z):
    """6 ref empties anchored to the projects section.

    Refs follow `_lib.ref_empty`'s convention: location is Blender axes
    (x, y_north, z_height). Showcase mount + interactive point both sit 1cm
    in front of the back-wall interior, vertically centred on the showcase
    panel.
    """
    cx = SECTION_RUNTIME_X
    cy = SECTION_RUNTIME_Z

    section_loc = (cx, cy, ground_z)

    # Bounding + frustum cylinders at section root.
    _lib.ref_empty(
        "refZoneBounding_projects",
        section_loc,
        radius=13.0,
    )
    _lib.ref_empty(
        "refZoneFrustum_projects",
        section_loc,
        radius=10.0,
    )

    # Showcase mount + interactive point: 1cm in front of inner face, at
    # the panel centre height. The runtime Billboards.js mounts here.
    showcase_x = cx + _BACK_WALL_INNER_X - SHOWCASE_OFFSET - 0.01
    showcase_loc = (showcase_x, cy, ground_z + SHOWCASE_CENTRE_Z)
    _lib.ref_empty(
        "refInteractivePoint_projects",
        showcase_loc,
        radius=0.5,
    )
    _lib.ref_empty(
        "refShowcaseMount",
        showcase_loc,
        radius=0.5,
        userdata={
            "width": SHOWCASE_WIDTH,
            "height": SHOWCASE_HEIGHT,
        },
    )

    # refForge - top of forge coal pit. Forge body top = ground + FORGE_H.
    forge_x, forge_y, _forge_z = _forge_centre(ground_z)
    _lib.ref_empty(
        "refForge",
        (forge_x, forge_y, ground_z + FORGE_H),
        radius=0.5,
    )

    # refRespawn_projects at section root.
    _lib.ref_empty(
        "refRespawn_projects",
        section_loc,
        radius=0.5,
    )


# ============================================================================
# Entry point
# ============================================================================


def main():
    _lib.clear_collection("sections/projects")

    material = _lib.get_palette_material()

    ground_z = _lib.height_at(SECTION_RUNTIME_X, SECTION_RUNTIME_Z)

    _build_walls(material, ground_z)
    _, _, apex_z = _build_roof(material, ground_z)
    _build_showcase_panel(material, ground_z)
    _build_anvil(material, ground_z)
    _build_forge(material, ground_z, apex_z)
    _build_tools(material, ground_z)
    _build_colliders(material, ground_z)
    _place_refs(ground_z)

    blend_path = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "world.blend"))
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    print(
        f"{_lib.LOG_PREFIX}[phase-04] OK - projects: workshop pavilion, "
        f"5 colliders, 6 refs"
    )
    print(f"{_lib.LOG_PREFIX}[phase-04] saved -> {blend_path}")


if __name__ == "__main__":
    main()
