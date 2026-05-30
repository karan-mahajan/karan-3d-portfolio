"""Section 13 — the welcome TITLE behind the statue: "KARAN", on a curved arc.

Bruno's design intent kept (mass-tagged knockable letters) but re-styled to our
chunky-beveled crafted world: each glyph is its OWN beveled-mesh object, the
name is laid out along a gentle arc that CUPS toward the landing (concave to the
viewer), and each letter tilts to follow the curve — so the player can still
shove / kick the letters around at runtime.

Placement: anchored BEHIND the statue (further from spawn along the
spawn->statue line) and spiralled onto the nearest grass there, facing back
toward the landing so it reads as a backdrop behind the bust. Every letter is
sampled across its width and must sit on grass clear of rocks / water / bridge /
slabs / markers / structures (statue footprint included) and bricks / fences /
bushes; remaining soft foliage under the letters is culled. Letters seat FLUSH
on the terrain and carry `mass` + `colliderHalfExtents`. The search relaxes in
tiers so the title is never silently dropped.

Blender owns: static letter geometry, per-letter mass + collider hint, ref.
Three.js owns later: the kick/knock physics + any settle/reset behaviour.

Additive delta — run standalone on the open world-v3-karan.blend:
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/13-misc-fx-title.py').read())
"""
import importlib
import math
import sys

import bpy
from mathutils import Vector

KARAN_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan"
if KARAN_DIR not in sys.path:
    sys.path.append(KARAN_DIR)

import misc_common as mc
importlib.reload(mc)   # pick up edits even if Blender cached an older copy

TITLE_TEXT = "KARAN"
LETTER_SIZE = 0.98             # cap height (m)
LETTER_DEPTH = 0.17            # extrude thickness (m)
LETTER_PITCH = 0.74            # arc-length advance per letter (m)
LETTER_MASS = 0.2              # light enough to kick
ARC_RADIUS = 3.0               # curve radius; smaller = tighter semicircle
COLLECTION = "miscFx"

# placement: behind the statue, nearest grass, facing the landing
LANDING = (0.0, 0.0)
STATUE_NAMES = ("karan_statue_base", "karan_statue_head",
                "structureFootprint_karan_statue")
STATUE_FALLBACK = (-5.5, -5.5)
BEHIND_DIST = 4.0              # metres past the statue (away from spawn)
GRASS_MIN = 0.45              # min terrainGrass coverage required under a letter
ROCK_EXTRA = 0.8              # extra clearance around hard obstacle boxes
SOFT_PREFIXES = ("brick_", "fence_", "bushAnchor_")
FOLIAGE_CULL_R = 0.5          # cull stray foliage within this radius of a letter
SEARCH_MAX_R = 22.0
SEARCH_STEP = 1.3

MATERIALS = {
    "misc_title_letter": (0.95, 0.72, 0.36, 1.0),
}


def _cleanup():
    mc.remove_objects_with_prefix("titleLetter_", "titleRef")
    mc.remove_orphan_data(mesh_prefix="miscMesh_titleLetter",
                          curve_prefix="miscTitleCurve_")


def _letter_arcpos():
    out = []
    cursor = 0.0
    for ch in TITLE_TEXT:
        if ch == " ":
            cursor += LETTER_PITCH
            continue
        out.append((ch, cursor))
        cursor += LETTER_PITCH
    ss = [s for _ch, s in out]
    mid = (min(ss) + max(ss)) * 0.5
    return [(ch, s - mid) for ch, s in out]


def _letter_local(s):
    """Local (lx, ly, phi). Concave toward the landing: middle letter farthest,
    ends sweep forward toward the viewer."""
    phi = s / ARC_RADIUS
    lx = ARC_RADIUS * math.sin(phi)
    ly = -ARC_RADIUS * (1.0 - math.cos(phi))
    return lx, ly, phi


def _statue_anchor():
    """Actual statue XY (read from the live object), else the known anchor."""
    for nm in STATUE_NAMES:
        o = bpy.data.objects.get(nm)
        if o is not None:
            t = mc.world_matrix(o).translation
            return (t.x, t.y)
    for o in bpy.data.objects:
        if o.name.startswith("karan_statue"):
            t = mc.world_matrix(o).translation
            return (t.x, t.y)
    return STATUE_FALLBACK


def _behind_anchor():
    sx, sz = _statue_anchor()
    lx, lz = LANDING
    dx, dz = sx - lx, sz - lz
    d = math.hypot(dx, dz) or 1.0
    return (sx + dx / d * BEHIND_DIST, sz + dz / d * BEHIND_DIST)


def _expand(boxes, extra):
    return [(xmin - extra, xmax + extra, zmin - extra, zmax + extra)
            for (xmin, xmax, zmin, zmax) in boxes]


def _in_any(wx, wz, boxes):
    for (xmin, xmax, zmin, zmax) in boxes:
        if xmin <= wx <= xmax and zmin <= wz <= zmax:
            return True
    return False


def _point_ok(wx, wz, boxes, grass_min):
    if math.hypot(wx, wz) > mc.ISLAND_RADIUS:
        return False
    h = mc.height_at(wx, wz)
    if h is None or h < mc.LAND_MIN:
        return False
    if mc.grass_at(wx, wz) < grass_min:
        return False
    return not _in_any(wx, wz, boxes)


def _arc_valid(cx, cz, base_yaw, positions, boxes, grass_min):
    for _ch, s in positions:
        lx, ly, phi = _letter_local(s)
        for off in (-0.34, 0.0, 0.34):          # across the letter width (tangent)
            sx = lx + off * math.cos(phi)
            sy = ly - off * math.sin(phi)
            wx, wz = mc.world_xy(cx, cz, base_yaw, sx, sy)
            if not _point_ok(wx, wz, boxes, grass_min):
                return False
    return _point_ok(*mc.world_xy(cx, cz, base_yaw, 0.0, 0.0), boxes, grass_min)


def _scan(center, positions, boxes, grass_min):
    """Spiral out from the behind-statue anchor; nearest valid arc wins. yaw
    faces the landing so the name reads from spawn."""
    ax, az = center
    r = 0.0
    while r <= SEARCH_MAX_R:
        ring = [(ax, az)] if r == 0.0 else [
            (ax + math.cos(math.radians(d)) * r, az + math.sin(math.radians(d)) * r)
            for d in range(0, 360, 12)]
        for (cx, cz) in ring:
            base_yaw = math.atan2(-cx, cz)        # -local_y -> toward landing
            if _arc_valid(cx, cz, base_yaw, positions, boxes, grass_min):
                return (cx, cz, base_yaw)
        r += SEARCH_STEP
    return None


def _find_arc(center, positions, hard, soft):
    """Strict (grass + full clearance + avoid bricks) first, then relax in tiers
    so the title is ALWAYS placed."""
    tiers = [
        ("clear+grass+no-bricks", _expand(hard, ROCK_EXTRA) + soft, GRASS_MIN),
        ("clear+grass",           _expand(hard, ROCK_EXTRA),        GRASS_MIN),
        ("any ground",            _expand(hard, 0.5),               0.15),
    ]
    for label, boxes, grass_min in tiers:
        spot = _scan(center, positions, boxes, grass_min)
        if spot is not None:
            return spot, label
    return None, None


def _make_letter(idx, ch, cx, cz, base_yaw, s, mat):
    curve = bpy.data.curves.new(f"miscTitleCurve_{idx:02d}", "FONT")
    curve.body = ch
    curve.align_x = "CENTER"
    curve.align_y = "BOTTOM"
    curve.size = LETTER_SIZE
    curve.extrude = LETTER_DEPTH * 0.5
    curve.bevel_depth = 0.028
    curve.bevel_resolution = 1
    curve.materials.append(mat)

    obj = bpy.data.objects.new(f"titleLetter_{idx:02d}_{ch}", curve)
    mc.link(obj, COLLECTION)

    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    obj.data.name = f"miscMesh_titleLetter_{idx:02d}"
    for poly in obj.data.polygons:
        poly.use_smooth = False

    lx, ly, phi = _letter_local(s)
    wx, wz = mc.world_xy(cx, cz, base_yaw, lx, ly)
    ground = mc.height_at(wx, wz)
    if ground is None:
        ground = 0.0
    obj.rotation_mode = "XYZ"
    obj.rotation_euler = (math.radians(90.0), 0.0, base_yaw - phi)   # stand + tilt with arc

    # Seat FLUSH: stood-up glyph maps local +Y -> world +Z, so a vertex world Z
    # = location.z + local_y; lowest vertex on the terrain -> z = ground - min_y.
    verts = obj.data.vertices
    xs = [v.co.x for v in verts]
    ys = [v.co.y for v in verts]
    zs = [v.co.z for v in verts]
    ly_min = min(ys) if ys else 0.0
    obj.location = (wx, wz, ground - ly_min)
    obj["mass"] = LETTER_MASS
    obj["kickable"] = True
    obj["interaction"] = "titleLetter"
    obj["glyph"] = ch

    half_w = max(0.12, (max(xs) - min(xs)) * 0.5) if xs else 0.3
    half_h = max(0.30, (max(ys) - min(ys)) * 0.5) if ys else 0.5
    half_d = max(0.06, (max(zs) - min(zs)) * 0.5) if zs else LETTER_DEPTH * 0.5
    obj["colliderHalfExtents"] = (half_w, half_d, half_h)
    return obj, (wx, wz)


def run():
    print("[13-misc-fx-title] build KARAN curved kickable title behind the statue")
    _cleanup()
    mat = mc.material("misc_title_letter", MATERIALS["misc_title_letter"],
                      roughness=0.62, emissive_strength=0.12)

    positions = _letter_arcpos()
    center = _behind_anchor()
    hard = mc.obstacle_boxes()
    soft = mc.prefix_boxes(SOFT_PREFIXES, margin=0.25)
    spot, tier = _find_arc(center, positions, hard, soft)
    if spot is None:
        print("  [ABORT] no spot found for the title even after relaxing")
        return
    cx, cz, base_yaw = spot
    print(f"  anchor behind statue ~({center[0]:.1f},{center[1]:.1f}); tier: {tier}")

    letter_points = []
    for idx, (ch, s) in enumerate(positions):
        _obj, pt = _make_letter(idx, ch, cx, cz, base_yaw, s, mat)
        letter_points.append(pt)

    mc.cull_foliage_near(letter_points, radius=FOLIAGE_CULL_R)

    ground = mc.height_at(cx, cz)
    mc.ref_anchor(
        "titleRef", (cx, cz, (ground or 0.0) + 1.3), yaw=base_yaw,
        props={"interaction": "title", "title": TITLE_TEXT, "kickable": True,
               "layout": "arc", "arcRadius": ARC_RADIUS},
        size=0.8,
    )

    bpy.ops.object.select_all(action="DESELECT")
    mc.save()
    print(f"  built {len(positions)} curved letters at ({cx:.1f},{cz:.1f}) "
          f"yaw={math.degrees(base_yaw):.1f} R={ARC_RADIUS}")


if __name__ == "__main__":
    run()
