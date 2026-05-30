"""Build a cozy log cabin — karan section-06 structure (repurposed from Bruno's
115_cabin, fully re-styled to match the chunky-beveled projects-hut look).

A stone pad with corner stones, notched corner logs, stacked-log timber walls
with chinking, a plank door under a gabled porch lintel, a warm glowing
mullioned window, a steep shingled gable roof (slopes + ridge cap + bargeboards
+ triangular gable fills), and a stone chimney.

Placement: a preferred NE anchor snapped onto clear dry land by a spiral search
(clears every section footprint/marker, rocks, bridges, slabs, ponds/river, and
the other structure). Terrain-height raycast for Z. After building it lays a
hidden footprint, clears the grass mask under it, and culls the section-05
foliage objects that were scattered there.

Runs AFTER the section-05 foliage layer. Run standalone on the built world:
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/06-buildings-cabin.py').read())
"""
import math
import os
import sys

import bmesh
import bpy

KARAN_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() \
    else "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan"
if KARAN_DIR not in sys.path:
    sys.path.append(KARAN_DIR)

import buildings_common as bc

KEY = "cabin"
ANCHOR = (24.0, 22.0)          # preferred NE spot; snapped to clear land at run
PREFER_FACE_ORIGIN = True       # door faces toward island centre (welcoming)

# Local plan half-sizes (metres). Door faces local -Y.
HALF_W = 2.10                   # wall half-width (X)
HALF_D = 1.75                   # wall half-depth (Y)
WALL_T = 0.22
EAVE_Z = 2.35
RIDGE_Z = 3.95
ROOF_OVERHANG_X = 0.48
ROOF_OVERHANG_Y = 0.42
FOOTPRINT = (5.9, 5.2, RIDGE_Z + 0.4)
GRASS_CLEAR_HALF = (3.1, 2.8)

COLORS = {
    "stone":      (0.34, 0.34, 0.31, 1.0),
    "stone_edge": (0.47, 0.47, 0.42, 1.0),
    "log":        (0.41, 0.23, 0.105, 1.0),
    "log_dark":   (0.26, 0.14, 0.06, 1.0),
    "chink":      (0.63, 0.46, 0.29, 1.0),
    "shingle":    (0.47, 0.29, 0.135, 1.0),
    "shingle_dk": (0.31, 0.18, 0.085, 1.0),
    "door":       (0.20, 0.10, 0.04, 1.0),
    "trim":       (0.14, 0.07, 0.03, 1.0),
    "window":     (1.0, 0.78, 0.36, 0.92),
    "chimney":    (0.40, 0.40, 0.37, 1.0),
}


def _mats():
    return {
        "stone":      bc.material("cabin_stone", COLORS["stone"], 0.9),
        "stone_edge": bc.material("cabin_stone_edge", COLORS["stone_edge"], 0.85),
        "log":        bc.material("cabin_log", COLORS["log"], 0.78),
        "log_dark":   bc.material("cabin_log_dark", COLORS["log_dark"], 0.74),
        "chink":      bc.material("cabin_chink", COLORS["chink"], 0.8),
        "shingle":    bc.material("cabin_shingle", COLORS["shingle"], 0.82),
        "shingle_dk": bc.material("cabin_shingle_dark", COLORS["shingle_dk"], 0.82),
        "door":       bc.material("cabin_door", COLORS["door"], 0.7),
        "trim":       bc.material("cabin_trim", COLORS["trim"], 0.7),
        "window":     bc.material("cabin_window_glow", COLORS["window"], 0.34, 2.6),
        "chimney":    bc.material("cabin_chimney", COLORS["chimney"], 0.9),
    }


def _gable(name, bx, bz, ground, yaw, y_local, half_w, z_eave, z_ridge, thick, mat):
    """Triangular gable-fill prism (X-Z triangle extruded `thick` in Y) placed in
    local plan space; the object transform applies yaw + ground."""
    t = thick * 0.5
    pts_front = [(-half_w, y_local - t, z_eave), (half_w, y_local - t, z_eave),
                 (0.0, y_local - t, z_ridge)]
    pts_back = [(-half_w, y_local + t, z_eave), (half_w, y_local + t, z_eave),
                (0.0, y_local + t, z_ridge)]
    bm = bmesh.new()
    vf = [bm.verts.new(p) for p in pts_front]
    vb = [bm.verts.new(p) for p in pts_back]
    bm.faces.new(vf)
    bm.faces.new(vb[::-1])
    for i in range(3):
        j = (i + 1) % 3
        bm.faces.new([vf[i], vf[j], vb[j], vb[i]])
    bm.normal_update()
    mesh = bpy.data.meshes.get(f"structureMesh_{name}") or bpy.data.meshes.new(f"structureMesh_{name}")
    mesh.clear_geometry()
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.clear()
    mesh.materials.append(mat)
    obj = bpy.data.objects.get(name) or bpy.data.objects.new(name, mesh)
    obj.data = mesh
    obj.location = (bx, bz, ground)
    obj.rotation_mode = "XYZ"
    obj.rotation_euler = (0.0, 0.0, yaw)
    bc.bevel(obj, width=0.03)
    coll = bc.get_collection("structures")
    if obj.name not in {o.name for o in coll.objects}:
        coll.objects.link(obj)
    return obj


def _build(bx, bz, ground, yaw, m):
    def lc(name, lx, ly, lz, size, mat, **kw):
        return bc.local_cuboid(f"cabin_{name}", bx, bz, ground, yaw, lx, ly, lz, size, mat, **kw)

    # --- stone pad ---
    lc("pad_underlay", 0.0, 0.0, 0.05, (HALF_W * 2 + 0.9, HALF_D * 2 + 0.9, 0.10), m["stone_edge"])
    lc("pad", 0.0, 0.0, 0.20, (HALF_W * 2 + 0.5, HALF_D * 2 + 0.5, 0.30), m["stone"], bevel_w=0.05)
    for sx in (-1, 1):
        for sy in (-1, 1):
            lc(f"pad_corner_{sx}_{sy}", sx * (HALF_W + 0.18), sy * (HALF_D + 0.18), 0.30,
               (0.5, 0.5, 0.46), m["stone_edge"], bevel_w=0.05)
    base_z = 0.34

    # --- stacked-log walls (back + sides solid; front split around the door) ---
    wall_h = EAVE_Z - base_z
    wmid = base_z + wall_h * 0.5
    # back wall (+Y)
    lc("wall_back", 0.0, HALF_D, wmid, (HALF_W * 2, WALL_T, wall_h), m["log"])
    # side walls (±X)
    lc("wall_left", -HALF_W, 0.0, wmid, (WALL_T, HALF_D * 2, wall_h), m["log"])
    lc("wall_right", HALF_W, 0.0, wmid, (WALL_T, HALF_D * 2, wall_h), m["log"])
    # front wall (-Y) split into two piers + lintel around a 1.0m door
    door_hw = 0.52
    pier_w = HALF_W - door_hw
    for sx in (-1, 1):
        cx = sx * (door_hw + pier_w * 0.5)
        lc(f"wall_front_{sx}", cx, -HALF_D, wmid, (pier_w, WALL_T, wall_h), m["log"])
    lintel_z = base_z + 1.92
    lc("wall_front_lintel", 0.0, -HALF_D, lintel_z + (EAVE_Z - lintel_z) * 0.5,
       (door_hw * 2, WALL_T, EAVE_Z - lintel_z), m["log"])

    # horizontal chinking lines (thin light courses) on the visible walls
    for i, frac in enumerate((0.28, 0.55, 0.82)):
        z = base_z + wall_h * frac
        lc(f"chink_back_{i}", 0.0, HALF_D + 0.005, z, (HALF_W * 2 - 0.1, 0.05, 0.05), m["chink"], bevel_w=0.0)
        for sx, tag in ((-1, "l"), (1, "r")):
            lc(f"chink_side_{tag}_{i}", sx * (HALF_W + 0.005), 0.0, z, (0.05, HALF_D * 2 - 0.1, 0.05), m["chink"], bevel_w=0.0)

    # --- notched corner logs (vertical, protruding past the corners) ---
    for sx in (-1, 1):
        for sy in (-1, 1):
            bc.cylinder(f"cabin_cornerlog_{sx}_{sy}", 0.17, wall_h + 0.22,
                        bc.world_xy(bx, bz, yaw, sx * HALF_W, sy * HALF_D) + (ground + base_z + (wall_h + 0.22) * 0.5,),
                        m["log_dark"], vertices=12)

    # --- door (recessed plank) + frame + step ---
    lc("door", 0.0, -HALF_D + 0.03, base_z + 0.92, (door_hw * 2 - 0.08, 0.08, 1.78), m["door"])
    for sx in (-1, 1):
        lc(f"door_jamb_{sx}", sx * door_hw, -HALF_D - 0.02, base_z + 0.96, (0.1, 0.14, 1.9), m["trim"])
    lc("door_step", 0.0, -HALF_D - 0.34, base_z + 0.06, (1.5, 0.7, 0.14), m["stone_edge"], bevel_w=0.04)

    # --- glowing mullioned window on the +X wall ---
    win_y, win_z = -0.35, base_z + 1.18
    lc("window_frame", HALF_W + 0.02, win_y, win_z, (0.12, 1.02, 1.02), m["trim"])
    lc("window_glow", HALF_W + 0.05, win_y, win_z, (0.06, 0.84, 0.84), m["window"], bevel_w=0.0)
    lc("window_mull_v", HALF_W + 0.08, win_y, win_z, (0.04, 0.07, 0.86), m["trim"], bevel_w=0.0)
    lc("window_mull_h", HALF_W + 0.08, win_y, win_z, (0.04, 0.86, 0.07), m["trim"], bevel_w=0.0)

    # --- gable roof ---
    hw = HALF_W + ROOF_OVERHANG_X
    rise = RIDGE_Z - EAVE_Z
    run = hw
    angle = math.atan2(rise, run)
    plank_len = math.hypot(run, rise)
    plank_y = HALF_D * 2 + ROOF_OVERHANG_Y * 2
    mid_z = (EAVE_Z + RIDGE_Z) * 0.5
    lc("roof_right", hw * 0.5, 0.0, mid_z, (plank_len, plank_y, 0.16), m["shingle"], rot_y=angle, bevel_w=0.04)
    lc("roof_left", -hw * 0.5, 0.0, mid_z, (plank_len, plank_y, 0.16), m["shingle"], rot_y=-angle, bevel_w=0.04)
    lc("roof_ridge", 0.0, 0.0, RIDGE_Z + 0.02, (0.34, plank_y, 0.18), m["shingle_dk"], bevel_w=0.04)

    # gable fills + bargeboards (front -Y, back +Y)
    for sy, tag in ((-1, "front"), (1, "back")):
        _gable(f"cabin_gable_{tag}", bx, bz, ground, yaw, sy * HALF_D, HALF_W, EAVE_Z, RIDGE_Z, WALL_T, m["log"])
        # bargeboard trims following the two slopes
        for sx in (-1, 1):
            bcx = sx * hw * 0.5
            bc.local_cuboid(f"cabin_barge_{tag}_{sx}", bx, bz, ground, yaw, bcx,
                            sy * (HALF_D + ROOF_OVERHANG_Y), mid_z,
                            (plank_len, 0.12, 0.22), m["trim"], rot_y=sx * angle, bevel_w=0.0)

    # --- stone chimney on the back-right corner ---
    chx, chy = HALF_W - 0.35, HALF_D - 0.25
    lc("chimney", chx, chy, EAVE_Z + 0.55, (0.78, 0.78, RIDGE_Z + 1.2 - base_z), m["chimney"], bevel_w=0.05)
    lc("chimney_cap", chx, chy, RIDGE_Z + 1.15, (0.96, 0.96, 0.2), m["stone_edge"], bevel_w=0.05)


def run():
    print("[06-buildings-cabin] build log cabin")
    bc.remove_objects_with_prefix("cabin_", f"structureFootprint_{KEY}")
    spot = bc.find_spot(ANCHOR, bc.obstacle_boxes(), placed=[], footprint_radius=3.0, min_spacing=0.0)
    if spot is None:
        print(f"  [ABORT] no clear dry-land spot near {ANCHOR}")
        return
    bx, bz, ground = spot
    yaw = math.atan2(-bx, -bz) if PREFER_FACE_ORIGIN else 0.0  # door (-Y) faces origin

    m = _mats()
    _build(bx, bz, ground, yaw, m)
    bc.add_footprint(KEY, bx, bz, ground, yaw, FOOTPRINT,
                     bc.material("structure_footprint", (0.18, 0.16, 0.11, 0.2), 0.9))
    bc.clear_grass_under(bx, bz, yaw, GRASS_CLEAR_HALF)
    bc.clear_foliage_under(bx, bz, yaw, GRASS_CLEAR_HALF)

    bc.save()
    print(f"  built cabin at ({bx:.1f},{bz:.1f},{ground:.3f}) yaw={math.degrees(yaw):.1f}deg")


if __name__ == "__main__":
    run()
