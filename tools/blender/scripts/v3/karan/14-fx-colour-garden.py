"""Colour Garden — a walk-up paint-throw garden (karan-original FX feature).

A pure-entertainment interactive toy: a paint cauldron ringed by 6 emissive
COLOUR POTS (the picker), facing a fan of 6 grey abstract SCULPTURES the player
paints by charging + throwing a colour orb. No portfolio content — just delight.

Lives in section 14 (FX), like the lava pool, so the existing
`14-section-run-all.py` / `15-section-run-all.py` build it automatically (they
glob `14-fx-*.py`). Mirrors `14-fx-lava.py`'s authoring style + helpers.

WHAT THIS OWNS (Blender): the visual cauldron + pots + grey sculptures, placed
on clear grass via misc_common.find_spot, oriented so the statue fan faces AWAY
from spawn (player approaches the pots first). It does NOT author colliders or
do any painting.

WHAT THREE.JS OWNS LATER (src/Portfolio/ColourGarden.js): per-statue materials,
static colliders, colour-pot picking, charge/aim/throw, the paint bloom + slow-
mo. The visual meshes here export to their OWN GLB (static/world/colourGarden/)
via 16-export-glb.py and are loaded SEPARATELY at runtime — deliberately kept
out of the world prop-merge so each statue keeps an individual material and can
be recoloured.

NAMING CONTRACT (the runtime looks these up): sculptures `gardenStatue_<id>`
(obelisk/column/totem/orbpedestal/twistprism/ringbase), `gardenCauldron`,
`gardenCauldronPaint`, pots `gardenPot_<hue>` (crimson/amber/gold/emerald/
azure/violet). Pot hue -> hex is mirrored in ColourGarden.js.

VERIFY WITH A FULL REBUILD (terrain must exist for the height raycast):
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/15-section-run-all.py').read())
Standalone (only meaningful after a build):
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/14-fx-colour-garden.py').read())
"""
import importlib
import math
import os
import sys

import bpy

KARAN_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() \
    else "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan"
if KARAN_DIR not in sys.path:
    sys.path.append(KARAN_DIR)

import misc_common as mc          # raycast, find_spot, builders, link, save
importlib.reload(mc)

COLLECTION = "colourGarden"
MESH_PREFIX = "gardenMesh"

# User-picked centre (3D-cursor capture 2026-06-01), pulled ~6 m back toward the
# island interior so the away-from-spawn statue fan clears the SW shoreline.
# find_spot snaps it onto clear grass; any sculpture that would still land in
# water is pulled inward by _dry_spot. Tunable: change ANCHOR and rerun.
ANCHOR = (-6.5, -33.0)

# Inland rocks sitting inside the plaza are removed so the garden reads clean
# (the spot the user picked had one shard, rock08). Shore rocks are >9 m out, so
# 8 m only clears what's actually under the garden — and follows ANCHOR if moved.
ROCK_CULL_RADIUS = 8.0
ROCK_NAME_KEYS = ("rock", "boulder", "shard", "basalt")

GREY = (0.55, 0.57, 0.60, 1.0)          # sculpture neutral base (recoloured at runtime)
GREY_DARK = (0.22, 0.24, 0.28, 1.0)     # cauldron body
PAINT_GLOW = (0.95, 0.45, 0.85, 1.0)    # cauldron paint surface

# pot id -> emissive RGBA (ColourGarden.js maps the same ids to hex)
POTS = [
    ("crimson", (0.85, 0.12, 0.22, 1.0)),
    ("amber",   (0.95, 0.45, 0.10, 1.0)),
    ("gold",    (0.98, 0.82, 0.18, 1.0)),
    ("emerald", (0.20, 0.70, 0.30, 1.0)),
    ("azure",   (0.18, 0.55, 0.95, 1.0)),
    ("violet",  (0.55, 0.30, 0.85, 1.0)),
]

# sculpture id -> local (x, forward) in garden space; forward = +local_y = AWAY
# from the player. Fanned 6–14 m out so throws have range.
FAN = [
    ("obelisk",     (-6.0, 7.0)),
    ("column",      (-3.4, 10.0)),
    ("totem",       (-0.3, 11.5)),
    ("orbpedestal", ( 2.9, 10.4)),
    ("twistprism",  ( 5.6, 7.6)),
    ("ringbase",    ( 0.2, 6.2)),
]

POT_ARC_RADIUS = 1.9


# --------------------------------------------------------------------------- #
# local primitive helpers (cone/torus that misc_common lacks); cuboid/cylinder/
# sphere come from mc. All link into COLLECTION with the garden mesh prefix.
# --------------------------------------------------------------------------- #
def _cone(name, r1, r2, depth, center, mat, verts=20, scale=(1.0, 1.0, 1.0)):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2,
                                    depth=depth, location=center)
    o = bpy.context.object
    o.name = name
    o.data.name = f"{MESH_PREFIX}_{name}"
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    return mc.link(o, COLLECTION)


def _torus(name, R, r, center, mat):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r,
                                     major_segments=24, minor_segments=12,
                                     location=center,
                                     rotation=(math.radians(90.0), 0.0, 0.0))
    o = bpy.context.object
    o.name = name
    o.data.name = f"{MESH_PREFIX}_{name}"
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    o.data.materials.append(mat)
    return mc.link(o, COLLECTION)


def _join(parts, name):
    """Join parts into one object named `name` (so a sculpture = one mesh with
    one material the runtime can recolour)."""
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    o = bpy.context.object
    o.name = name
    o.data.name = f"{MESH_PREFIX}_{name}"
    return o


# --------------------------------------------------------------------------- #
# sculpture builders — base at ground, single joined object per statue
# --------------------------------------------------------------------------- #
def _build_obelisk(name, x, z, g, mat):
    shaft = _cone(f"{name}_shaft", 0.22, 0.10, 2.2, (x, z, g + 1.1), mat, verts=4)
    cap = _cone(f"{name}_cap", 0.16, 0.0, 0.5, (x, z, g + 2.45), mat, verts=4)
    return _join([shaft, cap], name)


def _build_column(name, x, z, g, mat):
    base = mc.cuboid(f"{name}_base", (x, z, g + 0.15), (0.9, 0.9, 0.3), mat,
                     collection=COLLECTION, mesh_prefix=MESH_PREFIX, bevel_w=0.0)
    shaft = mc.cylinder(f"{name}_shaft", 0.33, 2.0, (x, z, g + 1.3), mat,
                        vertices=16, collection=COLLECTION, mesh_prefix=MESH_PREFIX)
    cap = mc.cuboid(f"{name}_cap", (x, z, g + 2.425), (0.8, 0.8, 0.25), mat,
                    collection=COLLECTION, mesh_prefix=MESH_PREFIX, bevel_w=0.0)
    return _join([base, shaft, cap], name)


def _build_totem(name, x, z, g, mat):
    parts, h = [], 0.0
    for i, (w, t) in enumerate([(0.7, 0.6), (0.55, 0.5), (0.62, 0.55), (0.42, 0.7)]):
        parts.append(mc.cuboid(f"{name}_b{i}", (x, z, g + h + t / 2), (w, w, t), mat,
                               yaw=0.3 * i, collection=COLLECTION,
                               mesh_prefix=MESH_PREFIX, bevel_w=0.0))
        h += t
    return _join(parts, name)


def _build_orbpedestal(name, x, z, g, mat):
    ped = mc.cylinder(f"{name}_ped", 0.5, 1.2, (x, z, g + 0.6), mat, vertices=16,
                      collection=COLLECTION, mesh_prefix=MESH_PREFIX, scale=(0.9, 0.9, 1.0))
    orb = mc.sphere(f"{name}_orb", 0.55, (x, z, g + 1.75), mat, segments=20,
                    ring_count=12, collection=COLLECTION, mesh_prefix=MESH_PREFIX)
    return _join([ped, orb], name)


def _build_twistprism(name, x, z, g, mat):
    o = mc.cylinder(name, 0.42, 2.4, (x, z, g + 1.2), mat, vertices=6,
                    collection=COLLECTION, mesh_prefix=MESH_PREFIX)
    m = o.modifiers.new("twist", "SIMPLE_DEFORM")
    m.deform_method = 'TWIST'
    m.angle = math.radians(120.0)
    return o


def _build_ringbase(name, x, z, g, mat):
    base = mc.cuboid(f"{name}_base", (x, z, g + 0.3), (0.8, 0.8, 0.6), mat,
                     collection=COLLECTION, mesh_prefix=MESH_PREFIX, bevel_w=0.0)
    ring = _torus(f"{name}_ring", 0.55, 0.16, (x, z, g + 1.4), mat)
    return _join([base, ring], name)


SCULPTORS = {
    "obelisk": _build_obelisk, "column": _build_column, "totem": _build_totem,
    "orbpedestal": _build_orbpedestal, "twistprism": _build_twistprism,
    "ringbase": _build_ringbase,
}


def _dry_spot(bx, bz, yaw, lx, ly):
    """World position for a sculpture at local (lx, ly), guaranteed on dry land.
    If the spot is in water/off-terrain, pull it radially toward the centre until
    it clears (keeps the fan shape, just shorter). Returns (wx, wz, ground) or
    None if even the inner limit is wet."""
    t = 1.0
    while t >= 0.4:
        wx, wz = mc.world_xy(bx, bz, yaw, lx * t, ly * t)
        g = mc.height_at(wx, wz)
        if g is not None and g >= mc.LAND_MIN:
            return wx, wz, g
        t -= 0.08
    return None


def _cull_rocks_near(cx, cz, radius):
    """Delete inland rock meshes whose origin is within `radius` of (cx,cz) so
    the plaza reads clean. Matches rock/boulder/shard/basalt names; our own
    garden* meshes never contain those keys, so they're safe."""
    removed = []
    for o in list(bpy.data.objects):
        if o.type != "MESH":
            continue
        n = o.name.lower()
        if not any(k in n for k in ROCK_NAME_KEYS):
            continue
        wx, wy, _ = o.matrix_world.translation
        if math.hypot(wx - cx, wy - cz) <= radius:
            removed.append(o.name)
            bpy.data.objects.remove(o, do_unlink=True)
    if removed:
        print(f"  culled {len(removed)} rock(s) under garden: {', '.join(removed)}")


# --------------------------------------------------------------------------- #
def run():
    print("[14-fx-colour-garden] build the paint-throw colour garden")
    # idempotent: drop anything from a previous run
    mc.remove_objects_with_prefix("gardenStatue_", "gardenCauldron",
                                  "gardenCauldronPaint", "gardenPot_")

    # clear rocks under the chosen plaza BEFORE the spot search so find_spot sees
    # clean ground and lands exactly on the user-picked ANCHOR
    _cull_rocks_near(ANCHOR[0], ANCHOR[1], ROCK_CULL_RADIUS)

    boxes = mc.obstacle_boxes()
    spot = mc.find_spot(ANCHOR, boxes, placed=[], min_spacing=0.0, step=1.4,
                        max_radius=24.0, require_grass=True)
    if spot is None:
        print(f"  [ABORT] no clear grass spot near {ANCHOR}")
        return
    bx, bz, _g0 = spot
    # orient so local +Y (the statue fan) points AWAY from spawn: world_xy maps
    # local +Y to (-sin yaw, cos yaw); set that equal to (bx,bz)/|.| direction.
    yaw = math.atan2(-bx, bz)
    print(f"  garden centre ({bx:.2f},{bz:.2f}) yaw={math.degrees(yaw):.0f}°")

    stone = mc.material("gardenStone", GREY, roughness=0.85)

    # clearing points (for foliage cull) collected as we place
    clear_pts = [(bx, bz)]

    # --- cauldron at the centre --------------------------------------------- #
    cg = mc.height_at(bx, bz)
    if cg is None:
        print("  [ABORT] cauldron centre off-terrain")
        return
    dark = mc.material("gardenCauldronBody", GREY_DARK, roughness=0.6)
    glow = mc.material("gardenCauldronPaint", PAINT_GLOW, roughness=0.4,
                       emissive_strength=2.2)
    body = mc.cylinder("gardenCauldron", 0.55, 0.8, (bx, bz, cg + 0.4), dark,
                       vertices=20, collection=COLLECTION, mesh_prefix=MESH_PREFIX,
                       scale=(1.0, 1.0, 1.0), bevel_w=0.0)
    rim = _torus("gardenCauldron_rim", 0.55, 0.08, (bx, bz, cg + 0.8), dark)
    _join([body, rim], "gardenCauldron")
    _cone("gardenCauldronPaint", 0.48, 0.48, 0.06, (bx, bz, cg + 0.82), glow, verts=20)

    # --- colour pots in a semicircle on the PLAYER side (local -Y) ---------- #
    for i, (pid, rgba) in enumerate(POTS):
        a = math.radians(-50.0 + i * 20.0)
        lx = POT_ARC_RADIUS * math.sin(a)
        ly = -POT_ARC_RADIUS * math.cos(a)          # negative = player side
        wx, wz = mc.world_xy(bx, bz, yaw, lx, ly)
        pg = mc.height_at(wx, wz)
        if pg is None:
            continue
        pot_mat = mc.material(f"gardenPot_{pid}_mat", rgba, roughness=0.5,
                              emissive_strength=1.8)
        _cone(f"gardenPot_{pid}", 0.18, 0.13, 0.34, (wx, wz, pg + 0.17), pot_mat,
              verts=14)
        clear_pts.append((wx, wz))

    # --- grey sculptures fanned out on local +Y (away from player) ---------- #
    # _dry_spot pulls any sculpture that would land in water back onto dry land.
    for sid, (lx, ly) in FAN:
        dry = _dry_spot(bx, bz, yaw, lx, ly)
        if dry is None:
            print(f"  [skip] sculpture {sid} — no dry land along its ray")
            continue
        wx, wz, sg = dry
        SCULPTORS[sid](f"gardenStatue_{sid}", wx, wz, sg, stone)
        clear_pts.append((wx, wz))

    # remove discrete flowers/bushes/bricks/fences overlapping the garden props
    mc.cull_foliage_near(clear_pts, radius=1.1)

    mc.save()
    n = len([o for o in mc.get_collection(COLLECTION).objects])
    print(f"  built colour garden: {n} objects at ({bx:.1f},{bz:.1f})")


if __name__ == "__main__":
    run()
