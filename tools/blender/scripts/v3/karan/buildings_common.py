"""Shared helpers for the karan section-06 buildings layer (cabin, outhouse).

Named WITHOUT an `06-` prefix so the section run-all glob (`06-buildings-*.py`)
never tries to `.run()` it. The `06-buildings-*.py` structure scripts import it
for:

  - terrain-height raycast + a spiral search that snaps a preferred anchor onto
    clear dry land (away from water/ponds/river/ocean, every section
    footprint/marker, rocks, bridges, slabs, and any already-placed structure),
  - chunky-bevel + cuboid/cylinder builders in a local plan space rotated by the
    structure YAW (mirrors the projects-hut authoring style),
  - a hidden WIRE footprint box (for later vegetation/runtime),
  - GROUND CLEAR under the footprint: subtractively zero the `terrainGrass.G`
    mask (NO mask rebuild — that would wipe the hut's clearing) AND delete the
    discrete foliage objects (bushAnchor_/flower_/brick_/fence_) the section-05
    layer already scattered there, since 06 runs AFTER 05.

Placement convention matches the rest of the karan build: a 2D point is (x, z)
where x = east-west and z = north-south (Blender X, Y). Object Z (height) always
comes from a downward terrain raycast — never hardcoded.
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Vector

KARAN_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan"
if KARAN_DIR not in sys.path:
    sys.path.append(KARAN_DIR)

BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"

GRASS_IMAGE = "terrainGrass"
GRASS_MASK_FILE = (
    "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/"
    "karan/resources/masks/terrainGrass-authored.exr"
)

# ---- placement gates (mirrors foliage_common / 04-vegetation-oak-trees) -----
ISLAND_RADIUS = 52.0     # keep within walkable land
LAND_MIN = -0.05         # plateau ~0.0; ponds/river carved <-0.6, ocean misses.
OBSTACLE_MARGIN = 1.6    # metres of clearance around scanned obstacles
OBSTACLE_KEYS = ("bridge", "basalt", "boulder", "shard", "rock",
                 "sectionfootprint", "sectionmarker", "slab", "slabes",
                 "structurefootprint")

# Discrete section-05 foliage object prefixes culled under a footprint.
FOLIAGE_PREFIXES = ("bushAnchor_", "flower_", "brick_", "fence_")


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


def world_matrix(o):
    """Robust world transform — unparented build objects read their matrix_world
    as identity-translation when parked in an excluded collection, so prefer
    matrix_basis (always live) until 15-finalize parents things."""
    return o.matrix_basis if o.parent is None else o.matrix_world


def obstacle_boxes():
    """XY AABBs (+margin) of every live obstacle mesh: bridges, rocks, slabs,
    all section markers/footprints, and any structure footprint already placed."""
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


def _valid(x, z, boxes, placed, min_spacing):
    if math.hypot(x, z) > ISLAND_RADIUS:
        return False
    h = height_at(x, z)
    if h is None or h < LAND_MIN:
        return False
    for (xmin, xmax, ymin, ymax) in boxes:
        if xmin <= x <= xmax and ymin <= z <= ymax:
            return False
    for (px, pz) in placed:
        if math.hypot(x - px, z - pz) < min_spacing:
            return False
    return True


def find_spot(anchor, boxes, placed, footprint_radius, min_spacing=10.0,
              step=1.4, max_radius=22.0):
    """Snap `anchor` onto the nearest clear dry-land spot. Spirals outward in
    growing rings; the structure's own footprint_radius is added to obstacle
    margins via min_spacing. Returns (x, z, ground) or None if nothing clears."""
    ax, az = anchor
    if _valid(ax, az, boxes, placed, min_spacing):
        return (ax, az, height_at(ax, az))
    r = step
    while r <= max_radius:
        for deg in range(0, 360, 18):
            a = math.radians(deg)
            x = ax + math.cos(a) * r
            z = az + math.sin(a) * r
            if _valid(x, z, boxes, placed, min_spacing):
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
    mod = obj.modifiers.new("structureBevel", "BEVEL")
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


def _link(obj, collection_name):
    coll = get_collection(collection_name)
    if obj.name not in {o.name for o in coll.objects}:
        coll.objects.link(obj)
    return obj


def cuboid(name, center, size, mat, yaw=0.0, rot_x=0.0, rot_y=0.0,
           collection="structures", bevel_w=0.03):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center,
                                    rotation=(rot_x, rot_y, yaw))
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"structureMesh_{name}"
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel_w > 0.0:
        bevel(obj, width=bevel_w)
    return _link(obj, collection)


def local_cuboid(name, base_x, base_z, ground, yaw, local_x, local_y, local_z,
                 size, mat, rot_x=0.0, rot_y=0.0, collection="structures",
                 bevel_w=0.03):
    wx, wz = world_xy(base_x, base_z, yaw, local_x, local_y)
    return cuboid(name, (wx, wz, ground + local_z), size, mat, yaw=yaw,
                  rot_x=rot_x, rot_y=rot_y, collection=collection, bevel_w=bevel_w)


def cylinder(name, radius, depth, center, mat, vertices=24, rotation=(0.0, 0.0, 0.0),
             collection="structures", bevel_w=0.0, scale=(1.0, 1.0, 1.0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius,
                                        depth=depth, location=center,
                                        rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"structureMesh_{name}"
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel_w > 0.0:
        bevel(obj, width=bevel_w)
    return _link(obj, collection)


# ============================================================================
# footprint + ground/foliage clearing
# ============================================================================
def add_footprint(key, base_x, base_z, ground, yaw, footprint_size, mat,
                  collection="colliders"):
    """Hidden WIRE footprint box (named structureFootprint_<key>) so later
    vegetation/runtime can keep clear."""
    hx, hy, hz = footprint_size[0] * 0.5, footprint_size[1] * 0.5, footprint_size[2] * 0.5
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= footprint_size[0]
        v.co.y *= footprint_size[1]
        v.co.z = v.co.z * footprint_size[2] + hz
    mesh = bpy.data.meshes.get(f"structureMesh_footprint_{key}") or bpy.data.meshes.new(
        f"structureMesh_footprint_{key}")
    mesh.clear_geometry()
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.clear()
    mesh.materials.append(mat)
    obj = bpy.data.objects.get(f"structureFootprint_{key}") or bpy.data.objects.new(
        f"structureFootprint_{key}", mesh)
    obj.data = mesh
    obj.location = (base_x, base_z, ground)
    obj.rotation_mode = "XYZ"
    obj.rotation_euler = (0.0, 0.0, yaw)
    obj.display_type = "WIRE"
    obj.hide_render = True
    obj["structure_footprint"] = True
    obj["structure"] = key
    return _link(obj, collection)


def _grass_grid_bounds():
    """World XY extent terrainGrass maps across (Plane.003's GN grid, ±96)."""
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


def clear_grass_under(base_x, base_z, yaw, half_extents, soft_edge=0.65):
    """Subtractively zero terrainGrass.G inside the rotated footprint rectangle
    (with a soft feathered edge). NO mask rebuild — only multiplies the green
    channel down, so the hut's and prior structures' clearings are preserved.
    Saves the combined mask to the authored .exr."""
    img = bpy.data.images.get(GRASS_IMAGE)
    if img is None:
        print("  [WARN] grass clear skipped: image missing")
        return
    w, h = img.size
    if w == 0 or h == 0 or img.channels < 2:
        print(f"  [WARN] grass clear skipped: invalid {GRASS_IMAGE!r} image")
        return

    min_x, max_x, min_z, max_z = _grass_grid_bounds()
    width = max_x - min_x
    depth = max_z - min_z
    if width <= 0.0 or depth <= 0.0:
        print("  [WARN] grass clear skipped: invalid grass grid bounds")
        return

    px = min_x + (np.arange(w, dtype=np.float32) + 0.5) * (width / w)
    pz = min_z + (np.arange(h, dtype=np.float32) + 0.5) * (depth / h)
    wx, wz = np.meshgrid(px, pz)
    dx = wx - base_x
    dz = wz - base_z
    c = math.cos(yaw)
    s = math.sin(yaw)
    local_x = dx * c + dz * s
    local_y = -dx * s + dz * c

    hx, hy = half_extents
    dist_x = np.abs(local_x) - hx
    dist_y = np.abs(local_y) - hy
    outside = np.maximum(dist_x, dist_y)
    clear = outside <= 0.0
    feather = (outside > 0.0) & (outside < soft_edge)
    keep = np.ones((h, w), dtype=np.float32)
    keep[clear] = 0.0
    keep[feather] = np.clip(outside[feather] / soft_edge, 0.0, 1.0)

    channels = img.channels
    pixels = np.asarray(img.pixels[:], dtype=np.float32).reshape((h, w, channels))
    before = pixels[:, :, 1].copy()
    pixels[:, :, 1] *= keep
    if channels >= 4:
        pixels[:, :, 3] = 1.0
    img.pixels.foreach_set(pixels.ravel())
    try:
        img.update()
    except Exception:
        pass
    try:
        os.makedirs(os.path.dirname(GRASS_MASK_FILE), exist_ok=True)
        img.filepath_raw = GRASS_MASK_FILE
        img.file_format = "OPEN_EXR"
        img.save()
    except Exception as e:
        print(f"  [WARN] could not save grass mask: {e}")
    changed = int((np.abs(before - pixels[:, :, 1]) > 0.001).sum())
    print(f"  cleared grass: changed={changed} px")


def clear_foliage_under(base_x, base_z, yaw, half_extents, margin=0.4):
    """Delete the discrete section-05 foliage objects (bushes/flowers/bricks/
    fences) whose XY centre lands inside the rotated footprint rectangle."""
    hx, hy = half_extents[0] + margin, half_extents[1] + margin
    c = math.cos(yaw)
    s = math.sin(yaw)
    removed = 0
    for o in list(bpy.data.objects):
        if not o.name.startswith(FOLIAGE_PREFIXES):
            continue
        m = world_matrix(o)
        wc = m @ Vector((0.0, 0.0, 0.0)) if o.type != "MESH" else m @ (
            sum((Vector(b) for b in o.bound_box), Vector()) / 8.0)
        dx = wc.x - base_x
        dz = wc.y - base_z
        lx = dx * c + dz * s
        ly = -dx * s + dz * c
        if abs(lx) <= hx and abs(ly) <= hy:
            bpy.data.objects.remove(o, do_unlink=True)
            removed += 1
    print(f"  cleared foliage: removed={removed} objects")


def remove_objects_with_prefix(*prefixes):
    n = 0
    for o in list(bpy.data.objects):
        if o.name.startswith(prefixes):
            bpy.data.objects.remove(o, do_unlink=True)
            n += 1
    return n


def save():
    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")
