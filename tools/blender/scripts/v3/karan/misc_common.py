"""Shared helpers for the karan section-13 misc/fx layer (title, controls, air
dancers, playstation, animals).

Named WITHOUT a `13-` prefix so the section run-all glob (`13-misc-fx-*.py`)
never tries to `.run()` it. The `13-misc-fx-*.py` prop scripts import it for:

  - terrain-height raycast + a spiral search that snaps a preferred anchor onto
    clear dry land (away from water/ponds/river/ocean, every section
    footprint/marker, rocks, bridges, slabs, and any already-placed structure
    or earlier section-13 prop),
  - chunky-bevel cuboid/cylinder/sphere builders in a yaw-rotated local plan
    space (mirrors the projects-hut / buildings authoring style),
  - a base PIVOT empty: child meshes parent to it so the runtime animates the
    whole prop by driving ONE transform (the skills-sphere hierarchy approach),
  - a runtime REF anchor empty carrying interaction custom props,
  - a hidden WIRE collider box for solid props.

Unlike `buildings_common`, section 13 does NOT clear the grass mask or cull
foliage — these props are light and sit naturally in the grass.

Placement convention matches the rest of the karan build: a 2D point is (x, z)
where x = east-west and z = north-south (Blender X, Y). Object Z (height) always
comes from a downward terrain raycast — never hardcoded.
"""
import math
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Vector

KARAN_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan"
if KARAN_DIR not in sys.path:
    sys.path.append(KARAN_DIR)

BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"

# ---- placement gates (mirrors buildings_common / 04-vegetation-oak-trees) ----
ISLAND_RADIUS = 52.0     # keep within walkable land
LAND_MIN = -0.05         # plateau ~0.0; ponds/river carved <-0.6, ocean misses.
OBSTACLE_MARGIN = 1.4    # metres of clearance around scanned obstacles
OBSTACLE_KEYS = ("bridge", "basalt", "boulder", "shard", "rock",
                 "sectionfootprint", "sectionmarker", "slab", "slabes",
                 "structurefootprint", "structuremesh", "miscfootprint")


# ============================================================================
# terrain + placement validation
# ============================================================================
def terrain():
    return bpy.data.objects.get("terrain") or bpy.data.objects.get("terrain_mesh")


def height_at(x, z):
    """Downward raycast onto the terrain; Blender-Z, or None when the ray misses
    (off-terrain = ocean)."""
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


GRASS_IMAGE = "terrainGrass"
_grass_cache = {}


def _grass_grid_bounds():
    """World XY extent terrainGrass maps across (Plane.003's GN grid, ±96).
    Mirrors buildings_common so world->mask sampling stays consistent."""
    plane = bpy.data.objects.get("Plane.003")
    size_x = size_y = 192.0
    cx = cy = 0.0
    if plane is not None:
        for m in plane.modifiers:
            if m.type != "NODES" or not m.node_group:
                continue
            grid = m.node_group.nodes.get("Grid")
            if grid is not None:
                size_x = grid.inputs["Size X"].default_value
                size_y = grid.inputs["Size Y"].default_value
            xf = m.node_group.nodes.get("Transform Geometry")
            if xf is not None and not xf.inputs["Scale"].is_linked:
                sx, sy, _sz = xf.inputs["Scale"].default_value
                size_x *= sx
                size_y *= sy
            if xf is not None and not xf.inputs["Translation"].is_linked:
                tx, ty, _tz = xf.inputs["Translation"].default_value
                cx, cy = tx, ty
        cx += plane.location.x
        cy += plane.location.y
    return (cx - size_x * 0.5, cx + size_x * 0.5, cy - size_y * 0.5, cy + size_y * 0.5)


def _grass_pixels():
    img = bpy.data.images.get(GRASS_IMAGE)
    if img is None or img.size[0] == 0 or img.size[1] == 0:
        return None
    key = img.name
    if key not in _grass_cache:
        w, h = img.size
        ch = img.channels
        arr = np.asarray(img.pixels[:], dtype=np.float32).reshape((h, w, ch))
        _grass_cache[key] = (arr, w, h, ch)
    return _grass_cache[key]


def grass_at(x, z):
    """Sampled grass coverage (terrainGrass green channel) at world (x, z), in
    [0, 1]. Returns 1.0 (assume grass) if the mask is missing; 0.0 off-grid.
    Same world->pixel mapping as buildings_common.clear_grass_under."""
    data = _grass_pixels()
    if data is None:
        return 1.0
    arr, w, h, ch = data
    if ch < 2:
        return 1.0
    min_x, max_x, min_z, max_z = _grass_grid_bounds()
    if max_x <= min_x or max_z <= min_z:
        return 1.0
    u = (x - min_x) / (max_x - min_x)
    v = (z - min_z) / (max_z - min_z)
    if u < 0.0 or u > 1.0 or v < 0.0 or v > 1.0:
        return 0.0
    px = min(w - 1, max(0, int(u * w)))
    py = min(h - 1, max(0, int(v * h)))
    return float(arr[py, px, 1])


def world_matrix(o):
    """Robust world transform — unparented build objects read their matrix_world
    as identity-translation when parked in an excluded collection, so prefer
    matrix_basis (always live) until 15-finalize parents things."""
    return o.matrix_basis if o.parent is None else o.matrix_world


def obstacle_boxes():
    """XY AABBs (+margin) of every live obstacle mesh: bridges, rocks, slabs,
    all section markers/footprints, structures, and earlier section-13 props."""
    boxes = []
    for o in bpy.data.objects:
        if o.type != "MESH":
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


GRASS_MIN = 0.45         # min terrainGrass coverage to count a spot as grass


def prefix_boxes(prefixes, margin=0.0):
    """XY AABBs (+margin) of every MESH object whose name starts with one of
    `prefixes` — used to avoid soft boundaries (bricks/fences/bushes) that
    aren't in OBSTACLE_KEYS."""
    prefixes = tuple(prefixes)
    boxes = []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith(prefixes):
            continue
        m = world_matrix(o)
        cs = [m @ Vector(c) for c in o.bound_box]
        xs = [c.x for c in cs]
        ys = [c.y for c in cs]
        boxes.append((min(xs) - margin, max(xs) + margin,
                      min(ys) - margin, max(ys) + margin))
    return boxes


def _valid(x, z, boxes, placed, min_spacing, require_grass=True):
    if math.hypot(x, z) > ISLAND_RADIUS:
        return False
    h = height_at(x, z)
    if h is None or h < LAND_MIN:
        return False
    if require_grass and grass_at(x, z) < GRASS_MIN:
        return False
    for (xmin, xmax, ymin, ymax) in boxes:
        if xmin <= x <= xmax and ymin <= z <= ymax:
            return False
    for (px, pz) in placed:
        if math.hypot(x - px, z - pz) < min_spacing:
            return False
    return True


def find_spot(anchor, boxes, placed, min_spacing=6.0, step=1.3, max_radius=20.0,
              require_grass=True):
    """Snap `anchor` onto the nearest clear dry GRASS spot (off water/river/
    bridge/footprints). Spirals outward in growing rings. Returns (x, z, ground)
    or None if nothing clears."""
    ax, az = anchor
    if _valid(ax, az, boxes, placed, min_spacing, require_grass):
        return (ax, az, height_at(ax, az))
    r = step
    while r <= max_radius:
        for deg in range(0, 360, 18):
            a = math.radians(deg)
            x = ax + math.cos(a) * r
            z = az + math.sin(a) * r
            if _valid(x, z, boxes, placed, min_spacing, require_grass):
                return (x, z, height_at(x, z))
        r += step
    return None


# ============================================================================
# materials + geometry builders (chunky-bevel crafted style)
# ============================================================================
def material(name, color, roughness=0.82, emissive_strength=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        if emissive_strength > 0.0:
            bsdf.inputs["Emission Color"].default_value = color
            bsdf.inputs["Emission Strength"].default_value = emissive_strength
        if len(color) == 4 and color[3] < 1.0:
            bsdf.inputs["Alpha"].default_value = color[3]
            mat.blend_method = "BLEND"
            mat.use_screen_refraction = False
    return mat


def bevel(obj, width=0.03, segments=2, angle_deg=44.0):
    """Soft angle-limited bevel — turns flat cubes into crafted timber/stone."""
    mod = obj.modifiers.new("miscBevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.angle_limit = math.radians(angle_deg)
    mod.use_clamp_overlap = True
    return obj


def world_xy(base_x, base_z, yaw, local_x, local_y):
    c = math.cos(yaw)
    s = math.sin(yaw)
    return (base_x + local_x * c - local_y * s,
            base_z + local_x * s + local_y * c)


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


def link(obj, collection_name):
    coll = get_collection(collection_name)
    if obj.name not in {o.name for o in coll.objects}:
        coll.objects.link(obj)
    return obj


def _shade_smooth(obj):
    if obj.type == "MESH":
        for poly in obj.data.polygons:
            poly.use_smooth = True
    return obj


def cuboid(name, center, size, mat, yaw=0.0, rot_x=0.0, rot_y=0.0,
           collection="miscFx", bevel_w=0.03, mesh_prefix="miscMesh"):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center,
                                    rotation=(rot_x, rot_y, yaw))
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{mesh_prefix}_{name}"
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel_w > 0.0:
        bevel(obj, width=bevel_w)
    return link(obj, collection)


def local_cuboid(name, base_x, base_z, ground, yaw, local_x, local_y, local_z,
                 size, mat, rot_x=0.0, rot_y=0.0, collection="miscFx",
                 bevel_w=0.03, mesh_prefix="miscMesh"):
    wx, wz = world_xy(base_x, base_z, yaw, local_x, local_y)
    return cuboid(name, (wx, wz, ground + local_z), size, mat, yaw=yaw,
                  rot_x=rot_x, rot_y=rot_y, collection=collection,
                  bevel_w=bevel_w, mesh_prefix=mesh_prefix)


def cylinder(name, radius, depth, center, mat, vertices=20,
             rotation=(0.0, 0.0, 0.0), collection="miscFx", bevel_w=0.0,
             scale=(1.0, 1.0, 1.0), mesh_prefix="miscMesh"):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius,
                                        depth=depth, location=center,
                                        rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{mesh_prefix}_{name}"
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel_w > 0.0:
        bevel(obj, width=bevel_w)
    return link(obj, collection)


def sphere(name, radius, center, mat, segments=20, ring_count=12,
           scale=(1.0, 1.0, 1.0), collection="miscFx", mesh_prefix="miscMesh"):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=ring_count,
                                         radius=radius, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{mesh_prefix}_{name}"
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    _shade_smooth(obj)
    return link(obj, collection)


# ============================================================================
# anchors / pivots / colliders (runtime contract)
# ============================================================================
def pivot_empty(name, location, yaw=0.0, props=None, collection="refs",
                size=0.6, display="PLAIN_AXES"):
    """Base pivot the prop's meshes parent to — runtime drives ONE transform."""
    e = bpy.data.objects.get(name) or bpy.data.objects.new(name, None)
    e.empty_display_type = display
    e.empty_display_size = size
    e.location = location
    e.rotation_mode = "XYZ"
    e.rotation_euler = (0.0, 0.0, yaw)
    for k, v in (props or {}).items():
        e[k] = v
    return link(e, collection)


def ref_anchor(name, location, yaw=0.0, props=None, collection="refs", size=0.5):
    return pivot_empty(name, location, yaw=yaw, props=props,
                       collection=collection, size=size)


def parent_to(child, parent, keep_transform=True):
    """Parent child to parent. With keep_transform, the child stays put in world
    space (matrix_parent_inverse) so authored positions are preserved."""
    child.parent = parent
    if keep_transform:
        child.matrix_parent_inverse = parent.matrix_world.inverted()
    return child


def collider_box(key, base_x, base_z, ground, yaw, size, collection="colliders"):
    """Hidden WIRE collider box (named miscFootprint_<key>) for solid props."""
    sx, sy, sz = size
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= sx
        v.co.y *= sy
        v.co.z = v.co.z * sz + sz * 0.5
    mesh = bpy.data.meshes.get(f"miscMesh_footprint_{key}") or bpy.data.meshes.new(
        f"miscMesh_footprint_{key}")
    mesh.clear_geometry()
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.get(f"miscFootprint_{key}") or bpy.data.objects.new(
        f"miscFootprint_{key}", mesh)
    obj.data = mesh
    obj.location = (base_x, base_z, ground)
    obj.rotation_mode = "XYZ"
    obj.rotation_euler = (0.0, 0.0, yaw)
    obj.display_type = "WIRE"
    obj.hide_render = True
    obj["misc_footprint"] = True
    obj["prop"] = key
    return link(obj, collection)


# Discrete section-05 foliage object prefixes (mirrors buildings_common).
FOLIAGE_PREFIXES = ("bushAnchor_", "flower_", "brick_", "fence_")


def cull_foliage_near(points, radius=0.7, prefixes=FOLIAGE_PREFIXES):
    """Delete discrete section-05 foliage objects (bushes/flowers/bricks/fences)
    whose XY centre falls within `radius` of ANY given (x, z) point, so a placed
    prop never overlaps a flower/bush. Grass blades (a GN system, not discrete
    objects) are untouched."""
    removed = 0
    for o in list(bpy.data.objects):
        if not o.name.startswith(prefixes):
            continue
        m = world_matrix(o)
        if o.type == "MESH" and len(o.bound_box):
            c = m @ (sum((Vector(b) for b in o.bound_box), Vector()) / 8.0)
        else:
            c = m @ Vector((0.0, 0.0, 0.0))
        for (px, pz) in points:
            if math.hypot(c.x - px, c.y - pz) <= radius:
                bpy.data.objects.remove(o, do_unlink=True)
                removed += 1
                break
    print(f"  culled {removed} foliage objects near {len(points)} point(s)")
    return removed


def remove_objects_with_prefix(*prefixes):
    n = 0
    for o in list(bpy.data.objects):
        if o.name.startswith(prefixes):
            bpy.data.objects.remove(o, do_unlink=True)
            n += 1
    return n


def remove_orphan_data(mesh_prefix=None, curve_prefix=None):
    if mesh_prefix:
        for m in list(bpy.data.meshes):
            if m.name.startswith(mesh_prefix) and m.users == 0:
                bpy.data.meshes.remove(m)
    if curve_prefix:
        for c in list(bpy.data.curves):
            if c.name.startswith(curve_prefix) and c.users == 0:
                bpy.data.curves.remove(c)


def save():
    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")
