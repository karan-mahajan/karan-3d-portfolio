"""Shared helpers for the karan section-05 foliage layer (bushes, flowers,
fences, bricks).

This module is intentionally NOT named with an `05-` prefix so the section
run-all glob (which matches `05-foliage-*.py`) never tries to `.run()` it.
The four `05-foliage-*.py` scripts import it for:

  - terrain-height raycast + valid-land / obstacle / footprint rejection
    (copied from 04-vegetation-oak-trees.py — the canonical validation),
  - the 4 cardinal SECTION specs (centre + accent colour), with each section's
    real footprint AABB read from the live `sectionFootprint_<key>` object so
    framing rings auto-size to clear big structures (skills sphere = 15x15,
    projects hut, contact board) instead of clipping them,
  - solid-material creation and a bmesh->mesh helper with per-face material
    slots.

Placement convention matches the rest of the karan build: a 2D point is
(x, z) where x = east-west and z = north-south (Blender X, Y). Object Z
(height) always comes from a downward terrain raycast — never hardcoded.
"""
import math
import sys

import bmesh
import bpy
from mathutils import Vector

KARAN_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan"
if KARAN_DIR not in sys.path:
    sys.path.append(KARAN_DIR)

BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"

# ---- placement gates (copied from 04-vegetation-oak-trees.py) --------------
ISLAND_RADIUS = 52.0     # keep within walkable land
LAND_MIN = -0.05         # plateau sits at ~0.0; ponds/river carved to <-0.6,
                         # ocean raycasts miss. >= -0.05 accepts only dry land.
OBSTACLE_MARGIN = 1.4    # metres of clearance around scanned obstacles
OBSTACLE_KEYS = ("bridge", "basalt", "boulder", "shard", "rock",
                 "sectionfootprint", "sectionmarker", "slab", "slabes")

# ---- the four cardinal sections --------------------------------------------
# location = landmark centre (fallback if the footprint object is absent).
# accent   = that section's marker accent colour (matches 04-markers MATERIALS).
# `location` is only a fallback if the live `sectionFootprint_<key>` object is
# missing — the real centres are read from those objects at run time (the
# dedicated hut/sphere/board structures repositioned the sections away from the
# old landmark coords, so these fallbacks mirror the structures' true centres).
SECTIONS = [
    {"key": "projects",   "location": (32.72, -31.78), "accent": (0.12, 0.38, 0.78, 1.0)},
    {"key": "experience", "location": (8.0, 36.0),     "accent": (0.80, 0.38, 0.12, 1.0)},
    {"key": "skills",     "location": (-34.14, -35.72), "accent": (0.12, 0.58, 0.35, 1.0)},
    {"key": "contact",    "location": (-13.37, 35.88), "accent": (0.72, 0.18, 0.38, 1.0)},
]

# sunset-palette flower colours for the open-meadow scatter (not section-coded)
MEADOW_FLOWER_COLORS = [
    (0.93, 0.55, 0.38, 1.0),  # peach
    (0.88, 0.35, 0.42, 1.0),  # coral
    (0.80, 0.22, 0.20, 1.0),  # red
    (0.92, 0.72, 0.28, 1.0),  # gold
]

# bush SDF-anchor tint (Bruno's yellow-green #b4b536 — LOCKED palette)
BUSH_COLOR_BASE = (0.706, 0.710, 0.212, 1.0)


# ============================================================================
# terrain + validation (verbatim behaviour from the oak script)
# ============================================================================
def world_matrix(o):
    """Robust world transform. `matrix_world` can read stale (identity
    translation) for objects parked in a view-layer-EXCLUDED collection — e.g.
    the section footprints in `colliders`, which never get evaluated. Until
    15-finalize parents things, every build object is unparented, so its
    `matrix_basis` (always live, built from loc/rot/scale) IS the world
    transform. Fall back to `matrix_world` only for the rare parented object."""
    return o.matrix_basis if o.parent is None else o.matrix_world


def terrain():
    return bpy.data.objects.get("terrain") or bpy.data.objects.get("terrain_mesh")


def height_at(x, z):
    """Downward raycast onto the terrain; returns Blender-Z (runtime Y), or
    None when the ray misses (off-terrain = ocean)."""
    terr = terrain()
    if terr is None:
        return 0.02
    inv = terr.matrix_world.inverted()
    o = inv @ Vector((x, z, 80.0))
    d = inv.to_3x3() @ Vector((0.0, 0.0, -1.0))
    ok, loc, _n, _i = terr.ray_cast(o, d)
    if not ok:
        return None
    return (terr.matrix_world @ loc).z


def obstacle_boxes():
    """XY AABBs (+margin) of every live obstacle mesh: bridges, rocks, slabs,
    and all section markers/footprints. Foliage candidates inside any box are
    rejected so nothing scatters into water-crossings, rock piles, or the
    section clearings."""
    boxes = []
    for o in bpy.data.objects:
        if o.type != 'MESH':
            continue
        n = o.name.lower()
        if not any(k in n for k in OBSTACLE_KEYS):
            continue
        m = world_matrix(o)
        cs = [m @ Vector(c) for c in o.bound_box]
        xs = [c.x for c in cs]
        ys = [c.y for c in cs]
        boxes.append((min(xs) - OBSTACLE_MARGIN, max(xs) + OBSTACLE_MARGIN,
                      min(ys) - OBSTACLE_MARGIN, max(ys) + OBSTACLE_MARGIN))
    return boxes


def valid(x, z, placed, boxes, min_spacing=0.0):
    """True if (x, z) is on dry walkable land, clear of every obstacle box,
    and at least `min_spacing` from each already-placed point."""
    if math.hypot(x, z) > ISLAND_RADIUS:
        return False
    h = height_at(x, z)
    if h is None or h < LAND_MIN:
        return False
    for (xmin, xmax, ymin, ymax) in boxes:
        if xmin <= x <= xmax and ymin <= z <= ymax:
            return False
    if min_spacing > 0.0:
        for (px, pz) in placed:
            if math.hypot(x - px, z - pz) < min_spacing:
                return False
    return True


# ============================================================================
# section geometry — read each section's REAL footprint so framing clears it
# ============================================================================
def _footprint(key):
    """Return (centre_x, centre_z, half_diagonal) of a section's footprint, or
    None. Centre uses world_matrix (matrix_basis) so it's correct despite the
    excluded-collection matrix_world bug; half-diagonal comes from the LOCAL
    bound box so it's rotation-invariant (the enclosing-circle radius)."""
    o = bpy.data.objects.get(f"sectionFootprint_{key}")
    if o is None:
        return None
    lx = [c[0] for c in o.bound_box]
    ly = [c[1] for c in o.bound_box]
    lz = [c[2] for c in o.bound_box]
    local_center = Vector(((min(lx) + max(lx)) * 0.5,
                           (min(ly) + max(ly)) * 0.5,
                           (min(lz) + max(lz)) * 0.5))
    wc = world_matrix(o) @ local_center
    half_diag = math.hypot((max(lx) - min(lx)) * 0.5, (max(ly) - min(ly)) * 0.5)
    return (wc.x, wc.y, half_diag)


def section_center(spec):
    """World (x, z) centre of a section — live footprint if present, else the
    fallback location."""
    fp = _footprint(spec["key"])
    return (fp[0], fp[1]) if fp is not None else spec["location"]


def section_ring_radius(spec, clearance=2.6, minimum=5.0):
    """Radius that encloses the section's footprint + clearance, so a framing
    ring of fences/bricks sits just OUTSIDE the structure (skills sphere etc.)."""
    fp = _footprint(spec["key"])
    if fp is None:
        return minimum
    return max(minimum, fp[2] + clearance)


def approach_dir(cx, cz):
    """Unit vector from a section centre toward the island centre (origin) —
    the side the player walks in from, where we leave the ring open and pave."""
    d = Vector((-cx, -cz))
    if d.length < 1e-4:
        return Vector((0.0, -1.0))
    return d.normalized()


# ============================================================================
# materials + mesh assembly
# ============================================================================
def solid_material(name, color, roughness=0.85):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = color
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
    return mat


def lighten(color, amount):
    """Mix a colour toward white by `amount` (0..1); keeps alpha."""
    r, g, b = color[0], color[1], color[2]
    a = color[3] if len(color) > 3 else 1.0
    return (r + (1.0 - r) * amount,
            g + (1.0 - g) * amount,
            b + (1.0 - b) * amount, a)


def faces_of(verts):
    """All faces touching any vert in `verts` (for slot tagging after a
    bmesh.ops primitive)."""
    fs = set()
    for v in verts:
        fs.update(v.link_faces)
    return fs


def build_mesh(name, bm, plan, materials, default_slot=0):
    """Write `bm` to a fresh mesh datablock named `name`, attach `materials`
    (a list, slot order), and set each polygon's material_index from `plan`
    (a list of (face, slot)). Frees the bmesh."""
    me = bpy.data.meshes.get(name)
    if me is not None:
        bpy.data.meshes.remove(me)
    me = bpy.data.meshes.new(name)

    bm.faces.index_update()
    slot_by_index = {f.index: slot for f, slot in plan}
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()

    me.materials.clear()
    for mat in materials:
        me.materials.append(mat)
    for p in me.polygons:
        p.material_index = slot_by_index.get(p.index, default_slot)
    return me


def link_object(name, mesh, location, collection, rotation_z=0.0, scale=1.0,
                userprops=None):
    """Get-or-create an object holding `mesh`, place it, link into `collection`
    (creating the collection at scene root if needed)."""
    ob = bpy.data.objects.get(name)
    if ob is None:
        ob = bpy.data.objects.new(name, mesh)
    else:
        ob.data = mesh
    ob.location = (location[0], location[1], location[2])
    ob.rotation_mode = "XYZ"
    ob.rotation_euler = (0.0, 0.0, rotation_z)
    if isinstance(scale, (tuple, list)):
        ob.scale = tuple(scale)
    else:
        ob.scale = (scale, scale, scale)
    ob["phase"] = "05-foliage"
    if userprops:
        for k, v in userprops.items():
            ob[k] = v
    if ob.name not in {o.name for o in collection.objects}:
        collection.objects.link(ob)
    return ob


def get_collection(name):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    elif coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try:
            bpy.context.scene.collection.children.link(coll)
        except Exception:
            pass
    return coll


def remove_objects_with_prefix(prefix):
    """Delete leftover objects from a prior run so re-running is clean."""
    n = 0
    for o in list(bpy.data.objects):
        if o.name.startswith(prefix):
            bpy.data.objects.remove(o, do_unlink=True)
            n += 1
    return n


def save():
    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")
