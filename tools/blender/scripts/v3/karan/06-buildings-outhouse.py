"""Build a wooden outhouse / privy — karan section-06 structure (repurposed from
Bruno's 114_toilet, fully re-styled to the chunky-beveled projects-hut look).

A small stone pad, vertical-plank timber walls, a plank door with the classic
crescent-moon vent, a corner-post frame, and a single mono-pitch shed roof that
slopes from a high back to a low front overhang. Whimsical but crafted.

Placement: a preferred NW anchor snapped onto clear dry land by the same spiral
search the cabin uses (clears every footprint/marker, rocks, bridges, slabs,
ponds/river, and the cabin). Terrain-height raycast for Z, hidden footprint,
grass-mask clear + section-05 foliage cull under it.

Runs AFTER the section-05 foliage layer. Run standalone on the built world:
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/06-buildings-outhouse.py').read())
"""
import math
import os
import sys

import bpy

KARAN_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() \
    else "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan"
if KARAN_DIR not in sys.path:
    sys.path.append(KARAN_DIR)

import buildings_common as bc

KEY = "outhouse"
ANCHOR = (-22.0, 20.0)         # preferred NW spot; snapped to clear land at run
PREFER_FACE_ORIGIN = True

HALF_W = 0.72                  # wall half-width (X)
HALF_D = 0.64                  # wall half-depth (Y); door faces local -Y
WALL_T = 0.12
FRONT_Z = 2.10                 # eave height at the low (front) edge
BACK_Z = 2.42                  # eave height at the high (back) edge
ROOF_OVERHANG = 0.30
FOOTPRINT = (2.4, 2.3, BACK_Z + 0.4)
GRASS_CLEAR_HALF = (1.35, 1.3)

COLORS = {
    "stone":      (0.35, 0.35, 0.32, 1.0),
    "stone_edge": (0.47, 0.47, 0.42, 1.0),
    "plank":      (0.44, 0.26, 0.12, 1.0),
    "plank_dark": (0.30, 0.17, 0.075, 1.0),
    "post":       (0.22, 0.12, 0.05, 1.0),
    "door":       (0.21, 0.11, 0.045, 1.0),
    "roof":       (0.36, 0.21, 0.10, 1.0),
    "roof_dark":  (0.24, 0.14, 0.065, 1.0),
    "moon":       (0.96, 0.92, 0.72, 1.0),
}


def _mats():
    return {
        "stone":      bc.material("outhouse_stone", COLORS["stone"], 0.9),
        "stone_edge": bc.material("outhouse_stone_edge", COLORS["stone_edge"], 0.85),
        "plank":      bc.material("outhouse_plank", COLORS["plank"], 0.78),
        "plank_dark": bc.material("outhouse_plank_dark", COLORS["plank_dark"], 0.76),
        "post":       bc.material("outhouse_post", COLORS["post"], 0.72),
        "door":       bc.material("outhouse_door", COLORS["door"], 0.7),
        "roof":       bc.material("outhouse_roof", COLORS["roof"], 0.82),
        "roof_dark":  bc.material("outhouse_roof_dark", COLORS["roof_dark"], 0.82),
        "moon":       bc.material("outhouse_moon", COLORS["moon"], 0.5),
    }


def _build(bx, bz, ground, yaw, m):
    def lc(name, lx, ly, lz, size, mat, **kw):
        return bc.local_cuboid(f"outhouse_{name}", bx, bz, ground, yaw, lx, ly, lz, size, mat, **kw)

    # --- stone pad ---
    lc("pad_underlay", 0.0, 0.0, 0.05, (HALF_W * 2 + 0.7, HALF_D * 2 + 0.7, 0.10), m["stone_edge"])
    lc("pad", 0.0, 0.0, 0.18, (HALF_W * 2 + 0.4, HALF_D * 2 + 0.4, 0.26), m["stone"], bevel_w=0.04)
    base_z = 0.31

    wall_h_back = BACK_Z - base_z
    wall_h_front = FRONT_Z - base_z
    # back + side walls (full panels)
    lc("wall_back", 0.0, HALF_D, base_z + wall_h_back * 0.5, (HALF_W * 2, WALL_T, wall_h_back), m["plank"])
    for sx, tag in ((-1, "left"), (1, "right")):
        # side walls are tall enough to meet the sloped roof at the back
        lc(f"wall_{tag}", sx * HALF_W, 0.0, base_z + wall_h_back * 0.5, (WALL_T, HALF_D * 2, wall_h_back), m["plank"])

    # front piers either side of the door + top lintel
    door_hw = 0.36
    pier_w = HALF_W - door_hw
    for sx in (-1, 1):
        cx = sx * (door_hw + pier_w * 0.5)
        lc(f"wall_front_{sx}", cx, -HALF_D, base_z + wall_h_front * 0.5, (pier_w, WALL_T, wall_h_front), m["plank"])
    lintel_z = base_z + 1.78
    lc("front_lintel", 0.0, -HALF_D, lintel_z + (FRONT_Z - lintel_z) * 0.5,
       (door_hw * 2, WALL_T, FRONT_Z - lintel_z), m["plank"])

    # vertical-plank texture strips on back + sides
    for i in range(-2, 3):
        lc(f"plank_back_{i}", i * 0.26, HALF_D + 0.005, base_z + wall_h_back * 0.5,
           (0.06, 0.04, wall_h_back - 0.08), m["plank_dark"], bevel_w=0.0)
    for sx, tag in ((-1, "l"), (1, "r")):
        for i in range(-2, 3):
            lc(f"plank_side_{tag}_{i}", sx * (HALF_W + 0.005), i * 0.24, base_z + wall_h_back * 0.5,
               (0.04, 0.06, wall_h_back - 0.08), m["plank_dark"], bevel_w=0.0)

    # corner posts (chunky)
    for sx in (-1, 1):
        for sy in (-1, 1):
            h = wall_h_back if sy > 0 else wall_h_front
            lc(f"post_{sx}_{sy}", sx * HALF_W, sy * HALF_D, base_z + h * 0.5 + 0.04,
               (0.16, 0.16, h + 0.08), m["post"])

    # --- plank door + frame + crescent-moon vent ---
    lc("door", 0.0, -HALF_D + 0.02, base_z + 0.9, (door_hw * 2 - 0.06, 0.07, 1.7), m["door"])
    for sx in (-1, 1):
        lc(f"door_jamb_{sx}", sx * door_hw, -HALF_D - 0.01, base_z + 0.94, (0.08, 0.12, 1.8), m["post"])
    # hinges + latch
    for sz in (base_z + 0.45, base_z + 1.35):
        lc(f"door_hinge_{int(sz*100)}", -door_hw + 0.06, -HALF_D - 0.04, sz, (0.16, 0.05, 0.08), m["roof_dark"], bevel_w=0.0)
    # crescent = bright disc partly overlapped by a door-coloured disc
    moon_z = base_z + 1.36
    mwx, mwz = bc.world_xy(bx, bz, yaw, 0.0, -HALF_D - 0.03)
    bc.cylinder("outhouse_moon", 0.135, 0.05, (mwx, mwz, ground + moon_z), m["moon"],
                vertices=20, rotation=(math.pi / 2, 0.0, yaw))
    omx, omz = bc.world_xy(bx, bz, yaw, 0.07, -HALF_D - 0.04)
    bc.cylinder("outhouse_moon_cut", 0.115, 0.06, (omx, omz, ground + moon_z + 0.03), m["door"],
                vertices=20, rotation=(math.pi / 2, 0.0, yaw))

    # --- mono-pitch shed roof (slopes high back -> low front) ---
    depth = HALF_D * 2 + ROOF_OVERHANG * 2
    rise = BACK_Z - FRONT_Z
    angle = math.atan2(rise, depth)
    slab_len = math.hypot(depth, rise)
    mid_z = (FRONT_Z + BACK_Z) * 0.5 + 0.12
    lc("roof", 0.0, 0.0, mid_z, (HALF_W * 2 + ROOF_OVERHANG * 2, slab_len, 0.14),
       m["roof"], rot_x=angle, bevel_w=0.04)
    # ridge trim along the high back edge
    lc("roof_back_trim", 0.0, HALF_D + ROOF_OVERHANG - 0.03, BACK_Z + 0.16,
       (HALF_W * 2 + ROOF_OVERHANG * 2, 0.12, 0.16), m["roof_dark"], bevel_w=0.03)


def run():
    print("[06-buildings-outhouse] build wooden outhouse")
    bc.remove_objects_with_prefix("outhouse_", f"structureFootprint_{KEY}")
    # avoid the cabin: treat already-placed structure footprints as obstacles +
    # keep a generous spacing from the cabin centre if it exists.
    placed = []
    cabin_fp = bpy.data.objects.get("structureFootprint_cabin")
    if cabin_fp is not None:
        placed.append((cabin_fp.location.x, cabin_fp.location.y))
    spot = bc.find_spot(ANCHOR, bc.obstacle_boxes(), placed=placed,
                        footprint_radius=1.5, min_spacing=14.0 if placed else 0.0)
    if spot is None:
        print(f"  [ABORT] no clear dry-land spot near {ANCHOR}")
        return
    bx, bz, ground = spot
    yaw = math.atan2(-bx, -bz) if PREFER_FACE_ORIGIN else 0.0

    m = _mats()
    _build(bx, bz, ground, yaw, m)
    bc.add_footprint(KEY, bx, bz, ground, yaw, FOOTPRINT,
                     bc.material("structure_footprint", (0.18, 0.16, 0.11, 0.2), 0.9))
    bc.clear_grass_under(bx, bz, yaw, GRASS_CLEAR_HALF)
    bc.clear_foliage_under(bx, bz, yaw, GRASS_CLEAR_HALF)

    bc.save()
    print(f"  built outhouse at ({bx:.1f},{bz:.1f},{ground:.3f}) yaw={math.degrees(yaw):.1f}deg")


if __name__ == "__main__":
    run()
