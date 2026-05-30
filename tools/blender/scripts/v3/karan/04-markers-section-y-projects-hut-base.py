"""Build the base Projects hut landmark.

This is the first approval pass for the east Projects section marker. It
replaces the generic three-card marker from 04-markers-section-landmarks.py
with a cozy stylized cabin: stone pad + corner buttresses, half-timber walls,
a steep shingled gable roof with bargeboards + ridge cap, a recessed arched
entry housing a glowing project screen, mullioned windows, lanterns, a carved
PROJECTS sign, a flagstone path, section ref, and a hidden footprint.

The camera-in / GSAP carousel / escape is a LATER Three.js pass; here we only
build the geometry and leave the screen + refs in place to support it.

Move/rotate the whole hut by changing LOCATION and YAW below. The script
samples the terrain at LOCATION, so the base sits on the saved heightfield.

Run on the already-built karan world:
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/04-markers-section-y-projects-hut-base.py').read())
"""
import math
import os
import sys
import importlib.util

import bmesh
import bpy
import numpy as np
from mathutils import Vector

TOOLS_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts"
if TOOLS_DIR not in sys.path:
    sys.path.append(TOOLS_DIR)
KARAN_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() \
    else "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan"

import _lib

BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"
MARKER_COLLECTION = "sectionMarkers/projectsHut"
COLLIDER_COLLECTION = "colliders"
REF_COLLECTION = "refs"
GRASS_IMAGE = "terrainGrass"
GRASS_MASK_FILE = (
    "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/"
    "karan/resources/masks/terrainGrass-authored.exr"
)
GRASS_SCRIPT = os.path.join(KARAN_DIR, "02-ground-grass-grass.py")

# Placement and axis copied from the manually adjusted
# projectHut_foundation_right_edge in world-v3-karan.blend.
LOCATION = (32.723134, -31.782017)
YAW = math.radians(176.000028)
PLAN_SCALE = 1.43

# Shared roof geometry (local plan units for X/Y, world metres for Z). The
# gable framing, sign and screen reference these so they stay aligned with the
# shingled slopes.
ROOF_HALF_W = 3.40   # half-width to the eave edge, includes side overhang
ROOF_HALF_D = 2.55   # half-depth to the gable edge, includes gable overhang
EAVE_Z = 3.35
RIDGE_Z = 6.75

FOOTPRINT = (12.4 * PLAN_SCALE, 10.4 * PLAN_SCALE, 7.4)
INTERACTION_OFFSET = (0.0, -4.15)
DOOR_CLEARANCE_OFFSET = (0.0, -2.92)
GRASS_CLEAR_HALF_EXTENTS = (7.20 * PLAN_SCALE, 6.40 * PLAN_SCALE)
GRASS_CLEAR_SOFT_EDGE = 0.65

MATERIALS = {
    "project_hut_stone": (0.31, 0.32, 0.28, 1.0),
    "project_hut_stone_edge": (0.46, 0.47, 0.40, 1.0),
    "project_hut_stone_buttress": (0.40, 0.41, 0.385, 1.0),
    "project_hut_wall_wood": (0.42, 0.20, 0.075, 1.0),
    "project_hut_wall_wood_light": (0.68, 0.38, 0.14, 1.0),
    "project_hut_infill": (0.80, 0.64, 0.44, 1.0),
    "project_hut_dark_wood": (0.12, 0.060, 0.025, 1.0),
    "project_hut_roof": (0.72, 0.51, 0.24, 1.0),
    "project_hut_roof_dark": (0.36, 0.22, 0.08, 1.0),
    "project_hut_shingle": (0.52, 0.33, 0.15, 1.0),
    "project_hut_shingle_dark": (0.34, 0.20, 0.085, 1.0),
    "project_hut_flagstone": (0.44, 0.45, 0.42, 1.0),
    "project_hut_door": (0.16, 0.075, 0.025, 1.0),
    "project_hut_window_glow": (1.0, 0.76, 0.34, 0.88),
    "project_hut_lamp_glow": (1.0, 0.70, 0.32, 0.92),
    "project_hut_screen_glow": (0.45, 0.74, 1.0, 1.0),
    "project_hut_sign_face": (0.055, 0.075, 0.065, 1.0),
    "project_hut_sign_text": (0.95, 0.78, 0.36, 1.0),
    "project_hut_door_return_white": (0.92, 0.90, 0.84, 1.0),
    "project_hut_footprint": (0.18, 0.16, 0.11, 0.20),
}


def _terrain():
    return bpy.data.objects.get("terrain") or bpy.data.objects.get("terrain_mesh")


def _height_at(x, z):
    terr = _terrain()
    if terr is None:
        return 0.02
    inv = terr.matrix_world.inverted()
    origin = inv @ Vector((x, z, 80.0))
    direction = inv.to_3x3() @ Vector((0.0, 0.0, -1.0))
    success, location, _normal, _face_index = terr.ray_cast(origin, direction)
    if not success:
        return None
    return (terr.matrix_world @ location).z


def _material(name, roughness=0.76, emissive_strength=0.0):
    color = MATERIALS[name]
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


def _materials():
    return {
        "stone": _material("project_hut_stone", 0.88),
        "stone_edge": _material("project_hut_stone_edge", 0.82),
        "buttress": _material("project_hut_stone_buttress", 0.90),
        "wall": _material("project_hut_wall_wood", 0.74),
        "wall_light": _material("project_hut_wall_wood_light", 0.72),
        "infill": _material("project_hut_infill", 0.78),
        "dark": _material("project_hut_dark_wood", 0.70),
        "roof": _material("project_hut_roof", 0.84),
        "roof_dark": _material("project_hut_roof_dark", 0.82),
        "shingle": _material("project_hut_shingle", 0.80),
        "shingle_dark": _material("project_hut_shingle_dark", 0.82),
        "flagstone": _material("project_hut_flagstone", 0.88),
        "door": _material("project_hut_door", 0.68),
        "window": _material("project_hut_window_glow", 0.34, emissive_strength=2.6),
        "lamp": _material("project_hut_lamp_glow", 0.28, emissive_strength=4.2),
        "screen": _material("project_hut_screen_glow", 0.30, emissive_strength=1.7),
        "sign_face": _material("project_hut_sign_face", 0.66),
        "sign_text": _material("project_hut_sign_text", 0.60, emissive_strength=0.75),
        "door_return": _material("project_hut_door_return_white", 0.70),
        "footprint": _material("project_hut_footprint", 0.90),
    }


def _cleanup():
    prefixes = (
        "sectionMarker_projects",
        "sectionLabel_projects",
        "sectionFootprint_projects",
        "sectionRef_projects",
        "projectHut_",
    )
    for obj in list(bpy.data.objects):
        if obj.name.startswith(prefixes):
            bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        if mesh.name.startswith("projectHutMesh_") and mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    for curve in list(bpy.data.curves):
        if curve.name.startswith("projectHutCurve_") and curve.users == 0:
            bpy.data.curves.remove(curve)


def _place(obj, collection=MARKER_COLLECTION):
    _lib.place_in(collection, obj)
    return obj


def _world(base_x, base_z, local_x, local_y):
    c = math.cos(YAW)
    s = math.sin(YAW)
    local_x *= PLAN_SCALE
    local_y *= PLAN_SCALE
    return (
        base_x + local_x * c - local_y * s,
        base_z + local_x * s + local_y * c,
    )


def _plan_size(size):
    return (size[0] * PLAN_SCALE, size[1] * PLAN_SCALE, size[2])


def _bevel(obj, width=0.03, segments=2, angle_deg=44.0):
    """Soft-bevel chunky timber/stone so edges catch light — the single
    biggest lever turning flat cubes into crafted props. Angle-limited so flat
    coplanar faces stay flat; clamp_overlap stops thin pieces self-folding."""
    mod = obj.modifiers.new("projectHutBevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.angle_limit = math.radians(angle_deg)
    mod.use_clamp_overlap = True
    return obj


def _cuboid(name, center, size, material, rotation_y=0.0, rotation_x=0.0,
            collection=MARKER_COLLECTION):
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=center, rotation=(rotation_x, rotation_y, YAW))
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"projectHutMesh_{name}"
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    return _place(obj, collection)


def _local_cuboid(name, base_x, base_z, ground, local_x, local_y, local_z, size,
                  material, rotation_y=0.0, rotation_x=0.0):
    wx, wz = _world(base_x, base_z, local_x, local_y)
    return _cuboid(name, (wx, wz, ground + local_z), _plan_size(size), material,
                   rotation_y=rotation_y, rotation_x=rotation_x)


def _brace(name, base_x, base_z, ground, axis, fixed_local, p0, p1, breadth,
           thick, material, bevel_w=0.022):
    """Diagonal timber between two in-plane points. axis='xz' lays the brace on
    a Y-facing face (front/back/gable, tilts about local Y); axis='yz' lays it
    on an X-facing face (side walls, tilts about local X). `breadth` is the
    in-plane width (local units), `thick` the out-of-plane depth (world Z)."""
    a0, b0 = p0
    a1, b1 = p1
    if axis == "xz":
        d_aw = (a1 - a0) * PLAN_SCALE
        d_bw = b1 - b0
        length = math.hypot(d_aw, d_bw)
        theta = -math.atan2(d_bw, d_aw)
        ca, cb = (a0 + a1) * 0.5, (b0 + b1) * 0.5
        obj = _local_cuboid(name, base_x, base_z, ground, ca, fixed_local, cb,
                            (length / PLAN_SCALE, breadth, thick), material,
                            rotation_y=theta)
    else:  # "yz"
        d_aw = (a1 - a0) * PLAN_SCALE
        d_bw = b1 - b0
        length = math.hypot(d_aw, d_bw)
        theta = math.atan2(d_bw, d_aw)
        ca, cb = (a0 + a1) * 0.5, (b0 + b1) * 0.5
        obj = _local_cuboid(name, base_x, base_z, ground, fixed_local, ca, cb,
                            (breadth, length / PLAN_SCALE, thick), material,
                            rotation_x=theta)
    return _bevel(obj, width=bevel_w)


def _cylinder(name, radius, depth, center, material, vertices=32, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=center,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"projectHutMesh_{name}"
    obj.data.materials.append(material)
    return _place(obj)


def _sphere(name, radius, center, material, scale=(1.0, 1.0, 1.0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=radius, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"projectHutMesh_{name}"
    obj.scale = scale
    obj.data.materials.append(material)
    return _place(obj)


def _shade(obj):
    if obj.type == "MESH":
        for poly in obj.data.polygons:
            poly.use_smooth = True
    return obj


def _add_light(name, base_x, base_z, ground, local_x, local_y, local_z, energy, size):
    wx, wz = _world(base_x, base_z, local_x, local_y)
    light = bpy.data.lights.get(name) or bpy.data.lights.new(name, "POINT")
    light.color = (1.0, 0.72, 0.38)
    light.energy = energy
    light.shadow_soft_size = size
    obj = bpy.data.objects.get(name) or bpy.data.objects.new(name, light)
    obj.data = light
    obj.location = (wx, wz, ground + local_z)
    _lib.place_in(MARKER_COLLECTION, obj)
    return obj


def _bm_tilted_box(bm, cx, cy, cz, hx, hy, hz, tilt_y=0.0):
    """Append a box to `bm` in hut-local space (X/Y in plan units, scaled here;
    Z in world metres). `tilt_y` tilts the box about its own local Y so shingle
    strips lie flat on the slope. The whole bmesh is later placed at the hut
    origin with the YAW spin, mirroring `_world`."""
    cxw, cyw = cx * PLAN_SCALE, cy * PLAN_SCALE
    hxw, hyw = hx * PLAN_SCALE, hy * PLAN_SCALE
    ct, st = math.cos(tilt_y), math.sin(tilt_y)
    vs = []
    for ix in (-1, 1):
        for iy in (-1, 1):
            for iz in (-1, 1):
                px, py, pz = ix * hxw, iy * hyw, iz * hz
                rx = px * ct + pz * st
                rz = -px * st + pz * ct
                vs.append(bm.verts.new((cxw + rx, cyw + py, cz + rz)))
    for idx in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
                (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
        bm.faces.new([vs[i] for i in idx])


def _bm_tri_prism(bm, base_hw, base_z, apex_z, y_center, y_half):
    """Append a triangular gable prism (apex up) to `bm` in hut-local space."""
    bx = base_hw * PLAN_SCALE
    yf = (y_center - y_half) * PLAN_SCALE
    yb = (y_center + y_half) * PLAN_SCALE
    v = [
        bm.verts.new((-bx, yf, base_z)),
        bm.verts.new((bx, yf, base_z)),
        bm.verts.new((0.0, yf, apex_z)),
        bm.verts.new((-bx, yb, base_z)),
        bm.verts.new((bx, yb, base_z)),
        bm.verts.new((0.0, yb, apex_z)),
    ]
    bm.faces.new((v[0], v[1], v[2]))
    bm.faces.new((v[3], v[5], v[4]))
    bm.faces.new((v[0], v[2], v[5], v[3]))
    bm.faces.new((v[2], v[1], v[4], v[5]))
    bm.faces.new((v[0], v[3], v[4], v[1]))


def _bm_object(name, bm, base_x, base_z, ground, material, bevel=None):
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    mesh = bpy.data.meshes.new(f"projectHutMesh_{name}")
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    obj.location = (base_x, base_z, ground)
    obj.rotation_mode = "XYZ"
    obj.rotation_euler = (0.0, 0.0, YAW)
    _place(obj)
    if bevel:
        _bevel(obj, **bevel)
    return obj


def _arch_panel_mesh(name, material, width=1.12, height=2.02, arch_radius=0.56, depth=0.12):
    width *= PLAN_SCALE
    arch_radius *= PLAN_SCALE
    depth *= PLAN_SCALE
    half = width * 0.5
    straight_h = height - arch_radius
    segments = 18
    outline = [(-half, 0.0), (half, 0.0), (half, straight_h)]
    for i in range(segments + 1):
        t = math.pi * (i / segments)
        outline.append((math.cos(t) * arch_radius, straight_h + math.sin(t) * arch_radius))
    outline.append((-half, 0.0))

    front = [(x, -depth * 0.5, z) for x, z in outline]
    back = [(x, depth * 0.5, z) for x, z in outline]
    verts = front + back
    n = len(outline)
    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    for i in range(n - 1):
        faces.append((i, i + 1, n + i + 1, n + i))

    mesh = bpy.data.meshes.new(f"projectHutMesh_{name}")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    return obj


def _text(name, body, base_x, base_z, ground, local_x, local_y, local_z, size, material):
    curve = bpy.data.curves.new(f"projectHutCurve_{name}", "FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0.014
    curve.materials.append(material)
    obj = bpy.data.objects.new(name, curve)
    wx, wz = _world(base_x, base_z, local_x, local_y)
    obj.location = (wx, wz, ground + local_z)
    obj.rotation_mode = "XYZ"
    obj.rotation_euler = (math.radians(90.0), 0.0, YAW)
    return _place(obj)


def _add_entry(base_x, base_z, ground, mats):
    # Stone base pad + raised stone rim grounding the cabin.
    _bevel(_local_cuboid("projectHut_foundation_underlay", base_x, base_z, ground, 0.0, 0.0, 0.05, (7.05, 5.30, 0.10), mats["stone"]), width=0.03)
    _bevel(_local_cuboid("projectHut_foundation_stone_slab", base_x, base_z, ground, 0.0, 0.0, 0.12, (6.50, 4.74, 0.20), mats["stone"]), width=0.03)
    _bevel(_local_cuboid("projectHut_foundation_rear_edge", base_x, base_z, ground, 0.0, 2.42, 0.24, (6.70, 0.26, 0.30), mats["stone_edge"]), width=0.03)
    _bevel(_local_cuboid("projectHut_foundation_left_edge", base_x, base_z, ground, -3.36, 0.0, 0.24, (0.26, 4.74, 0.30), mats["stone_edge"]), width=0.03)
    _bevel(_local_cuboid("projectHut_foundation_right_edge", base_x, base_z, ground, 3.36, 0.0, 0.24, (0.26, 4.74, 0.30), mats["stone_edge"]), width=0.03)

    # Stone steps stepping up to the arch (outermost lowest).
    _bevel(_local_cuboid("projectHut_step_lower", base_x, base_z, ground, 0.0, -3.18, 0.14, (2.50, 0.78, 0.28), mats["stone_edge"]), width=0.035)
    _bevel(_local_cuboid("projectHut_step_upper", base_x, base_z, ground, 0.0, -2.58, 0.30, (2.10, 0.70, 0.28), mats["stone_edge"]), width=0.035)
    _bevel(_local_cuboid("projectHut_porch_deck", base_x, base_z, ground, 0.0, -2.10, 0.44, (2.60, 0.70, 0.20), mats["wall_light"]), width=0.03)

    # Recessed entry portal carved behind the front wall opening.
    portal_hw = 0.86
    recess_back = -0.70
    _bevel(_local_cuboid("projectHut_recess_left", base_x, base_z, ground, -portal_hw - 0.04, -1.25, 1.35, (0.16, 1.20, 2.30), mats["wall"]), width=0.02)
    _bevel(_local_cuboid("projectHut_recess_right", base_x, base_z, ground, portal_hw + 0.04, -1.25, 1.35, (0.16, 1.20, 2.30), mats["wall"]), width=0.02)
    _bevel(_local_cuboid("projectHut_recess_ceiling", base_x, base_z, ground, 0.0, -1.25, 2.46, (1.92, 1.20, 0.16), mats["dark"]), width=0.02)
    _bevel(_local_cuboid("projectHut_recess_floor", base_x, base_z, ground, 0.0, -1.25, 0.52, (1.92, 1.20, 0.12), mats["stone"]), width=0.02)

    # Arched back panel (reuses the arch outline) closes the recess behind the
    # screen so the player never sees raw interior.
    back = _arch_panel_mesh("projectHut_recess_back", mats["wall"], width=1.80, height=2.32, arch_radius=0.88, depth=0.16)
    wx, wz = _world(base_x, base_z, 0.0, recess_back)
    back.location = (wx, wz, ground + 0.50)
    back.rotation_mode = "XYZ"
    back.rotation_euler = (0.0, 0.0, YAW)
    _place(back)

    # Thick rounded timber arch: jambs + a ring of voussoir blocks.
    _bevel(_local_cuboid("projectHut_arch_jamb_left", base_x, base_z, ground, -portal_hw, -1.80, 1.20, (0.26, 0.34, 1.42), mats["dark"]), width=0.03)
    _bevel(_local_cuboid("projectHut_arch_jamb_right", base_x, base_z, ground, portal_hw, -1.80, 1.20, (0.26, 0.34, 1.42), mats["dark"]), width=0.03)

    spring_z = 1.90
    arc_r = portal_hw * PLAN_SCALE + 0.12   # world radius
    count = 9
    block_len = (math.pi * arc_r / count) * 1.4 / PLAN_SCALE
    for i in range(count):
        t = math.pi * (i + 0.5) / count
        lx = (math.cos(t) * arc_r) / PLAN_SCALE
        lz = spring_z + math.sin(t) * arc_r
        theta = -math.atan2(math.cos(t), -math.sin(t))
        _bevel(_local_cuboid(f"projectHut_arch_block_{i:02d}", base_x, base_z, ground, lx, -1.80, lz,
                             (block_len, 0.34, 0.30), mats["dark"], rotation_y=theta), width=0.025)


def _add_screen(base_x, base_z, ground, mats):
    # Glowing project screen just inside the arch, facing out toward the door.
    # Three.js renders the real project UI here later; this is the framed,
    # emissive placeholder the camera flies in to read.
    sy = -0.82
    sz = 1.62
    _bevel(_local_cuboid("projectHut_screen_frame", base_x, base_z, ground, 0.0, sy + 0.06, sz, (1.62, 0.10, 1.86), mats["dark"]), width=0.025)
    panel = _local_cuboid("projectHut_screen_panel", base_x, base_z, ground, 0.0, sy, sz, (1.40, 0.05, 1.64), mats["screen"])
    panel["section"] = "projects"
    panel["interaction"] = "projectsHut"
    panel["projectScreen"] = True
    _text("projectHut_screen_title", "PROJECTS", base_x, base_z, ground, 0.0, sy - 0.04, sz + 0.62, 0.16, mats["sign_text"])
    _add_light("projectHut_screenLight", base_x, base_z, ground, 0.0, sy - 0.60, sz, 60.0, 1.4)


def _add_buttresses(base_x, base_z, ground, mats):
    # Chunky stepped stone piers at the four base corners. Each steps inward
    # toward the wall as it rises (battered), grounding the cabin.
    for cx in (-2.95, 2.95):
        for cy in (-2.00, 2.00):
            ix = -0.10 if cx > 0 else 0.10
            iy = -0.10 if cy > 0 else 0.10
            tag = f"{int(round(cx)):+d}_{int(round(cy)):+d}"
            _bevel(_local_cuboid(f"projectHut_buttress_{tag}_lo", base_x, base_z, ground, cx, cy, 0.40, (0.95, 0.95, 0.80), mats["buttress"]), width=0.05)
            _bevel(_local_cuboid(f"projectHut_buttress_{tag}_mid", base_x, base_z, ground, cx + ix, cy + iy, 1.05, (0.74, 0.74, 0.62), mats["buttress"]), width=0.05)
            _bevel(_local_cuboid(f"projectHut_buttress_{tag}_hi", base_x, base_z, ground, cx + ix * 2, cy + iy * 2, 1.55, (0.56, 0.56, 0.50), mats["buttress"]), width=0.05)


def _add_wall_planks(base_x, base_z, ground, mats):
    # Half-timber (Tudor) walls: light infill panels framed by dark timber
    # corner posts, plates, sills and visible diagonal X-braces.
    _local_cuboid("projectHut_back_wall", base_x, base_z, ground, 0.0, 1.76, 1.78, (5.60, 0.22, 3.00), mats["infill"])
    _local_cuboid("projectHut_left_wall", base_x, base_z, ground, -2.74, 0.0, 1.78, (0.22, 3.60, 3.00), mats["infill"])
    _local_cuboid("projectHut_right_wall", base_x, base_z, ground, 2.74, 0.0, 1.78, (0.22, 3.60, 3.00), mats["infill"])
    _local_cuboid("projectHut_front_wall_left", base_x, base_z, ground, -1.80, -1.76, 1.78, (1.92, 0.22, 3.00), mats["infill"])
    _local_cuboid("projectHut_front_wall_right", base_x, base_z, ground, 1.80, -1.76, 1.78, (1.92, 0.22, 3.00), mats["infill"])
    _bevel(_local_cuboid("projectHut_front_header", base_x, base_z, ground, 0.0, -1.76, 3.10, (5.66, 0.26, 0.40), mats["dark"]), width=0.025)

    for cx in (-2.78, 2.78):
        for cy in (-1.80, 1.80):
            tag = f"{int(round(cx)):+d}_{int(round(cy)):+d}"
            _bevel(_local_cuboid(f"projectHut_post_{tag}", base_x, base_z, ground, cx, cy, 1.74, (0.26, 0.26, 3.20), mats["dark"]), width=0.025)

    for cy in (-1.80, 1.80):
        tag = f"{int(round(cy)):+d}"
        _bevel(_local_cuboid(f"projectHut_plate_top_{tag}", base_x, base_z, ground, 0.0, cy, 3.16, (5.84, 0.24, 0.22), mats["dark"]), width=0.02)
        _bevel(_local_cuboid(f"projectHut_sill_{tag}", base_x, base_z, ground, 0.0, cy, 0.42, (5.84, 0.26, 0.20), mats["dark"]), width=0.02)
    for cx in (-2.78, 2.78):
        tag = f"{int(round(cx)):+d}"
        _bevel(_local_cuboid(f"projectHut_plate_side_{tag}", base_x, base_z, ground, cx, 0.0, 3.16, (0.24, 3.66, 0.22), mats["dark"]), width=0.02)
        _bevel(_local_cuboid(f"projectHut_sill_side_{tag}", base_x, base_z, ground, cx, 0.0, 0.42, (0.26, 3.66, 0.20), mats["dark"]), width=0.02)

    # X-braces across the side walls (X-facing faces -> Y-Z plane).
    for side in (-1.0, 1.0):
        wx = side * 2.90
        tag = f"{int(side):+d}"
        _brace(f"projectHut_brace_{tag}_a", base_x, base_z, ground, "yz", wx, (-1.55, 0.60), (1.55, 2.75), breadth=0.16, thick=0.18, material=mats["dark"])
        _brace(f"projectHut_brace_{tag}_b", base_x, base_z, ground, "yz", wx, (-1.55, 2.75), (1.55, 0.60), breadth=0.16, thick=0.18, material=mats["dark"])
        _bevel(_local_cuboid(f"projectHut_midpost_{tag}", base_x, base_z, ground, wx, 0.0, 1.70, (0.16, 0.22, 2.40), mats["dark"]), width=0.02)

    # Diagonal braces on the front infill panels either side of the entry.
    for side, sx0, sx1 in ((-1.0, -2.55, -1.30), (1.0, 1.30, 2.55)):
        _brace(f"projectHut_front_brace_{int(side):+d}", base_x, base_z, ground, "xz", -1.86, (sx0, 0.60), (sx1, 2.60), breadth=0.14, thick=0.16, material=mats["dark"])


def _add_gable_framing(base_x, base_z, ground, mats, face):
    # Exposed king-post timber framing over a lighter infill triangle, set back
    # from the bargeboards so the eave overhang reads. Built on BOTH gable ends
    # (face=-1 front toward the entry, face=+1 back) so the roof void is never
    # open from outside.
    base_hw = ROOF_HALF_W - 0.10
    gy_infill = face * 1.92
    gyf = gy_infill + face * 0.10
    rise = RIDGE_Z - EAVE_Z
    end = "front" if face < 0 else "back"

    bm = bmesh.new()
    _bm_tri_prism(bm, base_hw, EAVE_Z, RIDGE_Z, gy_infill, 0.06)
    _bm_object(f"projectHut_gable_infill_{end}", bm, base_x, base_z, ground, mats["infill"], bevel={"width": 0.02})

    _bevel(_local_cuboid(f"projectHut_gable_tiebeam_{end}", base_x, base_z, ground, 0.0, gyf, EAVE_Z + 0.18, (2.0 * base_hw * 0.92, 0.13, 0.26), mats["dark"]), width=0.02)
    _bevel(_local_cuboid(f"projectHut_gable_kingpost_{end}", base_x, base_z, ground, 0.0, gyf, (EAVE_Z + RIDGE_Z) * 0.5 + 0.05, (0.22, 0.12, rise - 0.10), mats["dark"]), width=0.02)

    for side in (-1.0, 1.0):
        tag = f"{int(side):+d}"
        _brace(f"projectHut_gable_rafter_{end}_{tag}", base_x, base_z, ground, "xz", gyf,
               (side * base_hw, EAVE_Z + 0.05), (0.0, RIDGE_Z - 0.05),
               breadth=0.10, thick=0.24, material=mats["dark"], bevel_w=0.02)
        _brace(f"projectHut_gable_strut_{end}_{tag}", base_x, base_z, ground, "xz", gyf,
               (0.0, EAVE_Z + 0.90), (side * base_hw * 0.55, EAVE_Z + rise * 0.55),
               breadth=0.09, thick=0.20, material=mats["dark"], bevel_w=0.02)


def _add_roof(base_x, base_z, ground, mats):
    half_w = ROOF_HALF_W
    half_d = ROOF_HALF_D
    rise = RIDGE_Z - EAVE_Z
    half_w_world = half_w * PLAN_SCALE
    slope_len = math.hypot(half_w_world, rise)
    cos_a = half_w_world / slope_len
    sin_a = rise / slope_len
    angle = math.atan2(rise, half_w_world)

    # Overlapping wooden shingle courses, eave -> ridge. Each shingle is a
    # chunky beveled block, NOT a flat decal: it is thick, tilted shallower than
    # the deck so its butt lifts and steps over the course below (real lap
    # shadow), with keyway gaps + half-course stagger + alternating tone so the
    # rows read as individual hand-split shingles.
    n_rows = 10
    pitch = slope_len / n_rows
    shingle_hx = (pitch * 2.05 * 0.5) / PLAN_SCALE   # >1 course long -> deep lap
    shingle_hz = 0.085                                # thickness -> visible relief
    butt_drop = math.radians(13.0)                    # tilt shallower so butt lifts
    lift = 0.06                                        # sit proud of the deck
    depth_world = 2.0 * half_d * PLAN_SCALE
    col_w = 0.62
    n_cols = max(3, int(math.ceil(depth_world / col_w)))
    step_local = col_w / PLAN_SCALE
    shingle_hy = step_local * 0.40                     # keyway gap between tabs

    bm_light = bmesh.new()
    bm_dark = bmesh.new()
    for side in (-1.0, 1.0):
        tilt = side * (angle - butt_drop)
        for row in range(n_rows):
            s = (row + 0.5) * pitch
            lx = side * (half_w - (s * cos_a) / PLAN_SCALE) + side * sin_a * lift / PLAN_SCALE
            lz = EAVE_Z + s * sin_a + cos_a * lift
            target = bm_dark if (row % 2) else bm_light
            start = -half_d - step_local * 0.5 + (step_local * 0.5 if row % 2 else 0.0)
            for col in range(n_cols + 1):
                cy = start + col * step_local
                _bm_tilted_box(target, lx, cy, lz, shingle_hx, shingle_hy, shingle_hz, tilt_y=tilt)
    _bm_object("projectHut_roof_shingles_a", bm_light, base_x, base_z, ground, mats["shingle"], bevel={"width": 0.02})
    _bm_object("projectHut_roof_shingles_b", bm_dark, base_x, base_z, ground, mats["shingle_dark"], bevel={"width": 0.02})

    # Thick ridge cap.
    _bevel(_local_cuboid("projectHut_roof_ridge", base_x, base_z, ground, 0.0, 0.0, RIDGE_Z + 0.02, (0.66, 2.0 * half_d + 0.30, 0.34), mats["roof_dark"]), width=0.06)

    # Eave fascia along the long sloped sides (the generous overhang edge).
    for side in (-1.0, 1.0):
        _bevel(_local_cuboid(f"projectHut_eave_fascia_{int(side):+d}", base_x, base_z, ground,
                             side * (half_w + 0.02), 0.0, EAVE_Z - 0.04,
                             (0.16, 2.0 * half_d + 0.26, 0.30), mats["dark"]), width=0.03)

    # Heavy bargeboards down both gable edges, following each slope.
    for gable in (-1.0, 1.0):
        gy = gable * (half_d + 0.05)
        for side in (-1.0, 1.0):
            _brace(f"projectHut_bargeboard_{int(gable):+d}_{int(side):+d}", base_x, base_z, ground,
                   "xz", gy, (side * half_w, EAVE_Z), (0.0, RIDGE_Z),
                   breadth=0.11, thick=0.40, material=mats["dark"], bevel_w=0.03)

    _add_gable_framing(base_x, base_z, ground, mats, -1.0)
    _add_gable_framing(base_x, base_z, ground, mats, 1.0)


def _add_windows_and_lamps(base_x, base_z, ground, mats):
    # Recessed, mullioned 4-pane windows flanking the entry.
    for key, sx in (("left", -1.95), ("right", 1.95)):
        _bevel(_local_cuboid(f"projectHut_window_{key}_frame", base_x, base_z, ground, sx, -1.80, 1.95, (1.06, 0.20, 1.26), mats["dark"]), width=0.025)
        _local_cuboid(f"projectHut_window_{key}_glow", base_x, base_z, ground, sx, -1.66, 1.95, (0.80, 0.06, 1.00), mats["window"])
        _local_cuboid(f"projectHut_window_{key}_mull_v", base_x, base_z, ground, sx, -1.62, 1.95, (0.07, 0.05, 1.04), mats["dark"])
        _local_cuboid(f"projectHut_window_{key}_mull_h", base_x, base_z, ground, sx, -1.62, 1.95, (0.84, 0.05, 0.07), mats["dark"])
        _bevel(_local_cuboid(f"projectHut_window_{key}_sill", base_x, base_z, ground, sx, -1.86, 1.36, (1.16, 0.30, 0.12), mats["wall_light"]), width=0.025)
        _bevel(_local_cuboid(f"projectHut_window_{key}_lintel", base_x, base_z, ground, sx, -1.86, 2.60, (1.16, 0.26, 0.16), mats["dark"]), width=0.025)
        _add_light(f"projectHut_windowLight_{key}", base_x, base_z, ground, sx, -2.10, 1.95, 80.0, 2.0)

    # Hanging lanterns on brackets flanking the arch.
    for key, sx in (("left", -1.30), ("right", 1.30)):
        _bevel(_local_cuboid(f"projectHut_archLantern_{key}_bracket", base_x, base_z, ground, sx, -1.95, 3.05, (0.10, 0.66, 0.10), mats["dark"]), width=0.02)
        _local_cuboid(f"projectHut_archLantern_{key}_chain", base_x, base_z, ground, sx, -2.22, 2.78, (0.05, 0.05, 0.40), mats["dark"])
        _bevel(_local_cuboid(f"projectHut_archLantern_{key}_cage", base_x, base_z, ground, sx, -2.24, 2.42, (0.26, 0.26, 0.34), mats["dark"]), width=0.02)
        _sphere(f"projectHut_archLantern_{key}_glow", 0.16, (*_world(base_x, base_z, sx, -2.24), ground + 2.42), mats["lamp"], scale=(1.0, 1.0, 0.9))
        _add_light(f"projectHut_archLight_{key}", base_x, base_z, ground, sx, -2.24, 2.42, 95.0, 1.8)

    # One standing lantern post on the path.
    lx, ly = 1.85, -4.60
    _bevel(_local_cuboid("projectHut_pathLantern_base", base_x, base_z, ground, lx, ly, 0.10, (0.34, 0.34, 0.20), mats["stone_edge"]), width=0.03)
    _bevel(_local_cuboid("projectHut_pathLantern_post", base_x, base_z, ground, lx, ly, 1.05, (0.10, 0.10, 1.80), mats["dark"]), width=0.02)
    _bevel(_local_cuboid("projectHut_pathLantern_cage", base_x, base_z, ground, lx, ly, 2.04, (0.32, 0.32, 0.40), mats["dark"]), width=0.02)
    _sphere("projectHut_pathLantern_glow", 0.18, (*_world(base_x, base_z, lx, ly), ground + 2.04), mats["lamp"], scale=(1.0, 1.0, 0.9))
    _add_light("projectHut_pathLight", base_x, base_z, ground, lx, ly, 2.04, 110.0, 2.0)


def _add_path(base_x, base_z, ground, mats):
    # Irregular flagstones from the grass to the steps. Each stone samples the
    # terrain at its own world position so it sits on the heightfield.
    stones = (
        (0.00, -3.70, 1.30, 1.10),
        (-0.55, -4.50, 1.05, 0.95),
        (0.50, -5.20, 1.15, 1.00),
        (-0.35, -6.00, 0.95, 1.05),
        (0.40, -6.90, 1.20, 0.95),
        (-0.20, -7.70, 1.00, 0.90),
    )
    for i, (lx, ly, sx, sy) in enumerate(stones):
        wx, wz = _world(base_x, base_z, lx, ly)
        g = _height_at(wx, wz)
        if g is None:
            g = ground
        obj = _cuboid(f"projectHut_flagstone_{i:02d}", (wx, wz, g + 0.06), _plan_size((sx, sy, 0.12)), mats["flagstone"])
        _bevel(obj, width=0.04)


def _add_sign(base_x, base_z, ground, mats):
    # Carved PROJECTS board with a raised chamfered border, across the gable.
    sy = -2.18
    sz = 4.55
    _bevel(_local_cuboid("projectHut_sign_border", base_x, base_z, ground, 0.0, sy + 0.06, sz, (2.66, 0.14, 0.92), mats["dark"]), width=0.06)
    _local_cuboid("projectHut_sign_board", base_x, base_z, ground, 0.0, sy, sz, (2.34, 0.12, 0.66), mats["sign_face"])
    _text("projectHut_sign_text", "PROJECTS", base_x, base_z, ground, 0.0, sy - 0.10, sz, 0.30, mats["sign_text"])


def _add_refs(base_x, base_z, ground):
    ix, iz = _world(base_x, base_z, *INTERACTION_OFFSET)
    ref = bpy.data.objects.new("sectionRef_projects", None)
    ref.empty_display_type = "PLAIN_AXES"
    ref.empty_display_size = 1.0
    ref.location = (ix, iz, ground + 1.10)
    ref.rotation_euler = (0.0, 0.0, YAW)
    ref["section"] = "projects"
    ref["title"] = "Projects"
    ref["interaction"] = "projectsHut"
    ref["enterCameraPath"] = "doorToInteriorBoard"
    ref["doorLocalOffset"] = DOOR_CLEARANCE_OFFSET
    # Matches the project screen mounted just inside the arch (see _add_screen).
    ref["interiorBoardLocalOffset"] = (0.0, -0.82, 1.62)
    _lib.place_in(REF_COLLECTION, ref)


def _add_footprint(base_x, base_z, ground, material):
    hx, hy, hz = FOOTPRINT[0] * 0.5, FOOTPRINT[1] * 0.5, FOOTPRINT[2] * 0.5
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(bm, uv, (0.0, 0.0, hz), (hx, hy, hz), "sand_gravel")
    mesh = bpy.data.meshes.new("projectHutMesh_sectionFootprint_projects")
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(material)
    obj = bpy.data.objects.new("sectionFootprint_projects", mesh)
    obj.location = (base_x, base_z, ground)
    obj.rotation_mode = "XYZ"
    obj.rotation_euler = (0.0, 0.0, YAW)
    obj.display_type = "WIRE"
    obj.hide_viewport = True
    obj.hide_render = True
    obj["section_marker_footprint"] = True
    obj["section"] = "projects"
    obj["interaction"] = "projectsHut"
    _lib.place_in(COLLIDER_COLLECTION, obj)


def _save_mask_image(img, filepath):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        img.filepath_raw = filepath
        img.file_format = "OPEN_EXR"
        img.save()
        print(f"  {img.name}: saved edited pixels -> {filepath}")
    except Exception as e:
        print(f"  [WARN] could not save {img.name!r}: {e}")


def _restore_authored_grass_mask():
    """Rebuild the normal section-02 grass mask before clearing this hut."""
    if not os.path.exists(GRASS_SCRIPT):
        print(f"  [WARN] grass reset skipped: missing {GRASS_SCRIPT}")
        return
    spec = importlib.util.spec_from_file_location("projects_hut_grass_reset", GRASS_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.run()


def _grass_grid_bounds():
    """World XY extent that terrainGrass maps across.

    The grass blades are a Geometry-Nodes scatter on the grass plane
    (Plane.003), and the Image Texture samples terrainGrass by the GN Grid's
    UV (0..1 across its Size X/Y, centred on the plane origin). So the mask
    aligns to *that grid*, NOT the smaller `terrain` object — mapping by the
    terrain bounds (used previously) shifted the cleared rectangle off the hut.
    Falls back to the known 192m grid if the node graph can't be read."""
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


def _clear_grass_under_hut(base_x, base_z):
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
    c = math.cos(YAW)
    s = math.sin(YAW)
    local_x = dx * c + dz * s
    local_y = -dx * s + dz * c

    hx, hy = GRASS_CLEAR_HALF_EXTENTS
    edge = GRASS_CLEAR_SOFT_EDGE
    dist_x = np.abs(local_x) - hx
    dist_y = np.abs(local_y) - hy
    outside = np.maximum(dist_x, dist_y)
    clear = outside <= 0.0
    feather = (outside > 0.0) & (outside < edge)
    keep_factor = np.ones((h, w), dtype=np.float32)
    keep_factor[clear] = 0.0
    keep_factor[feather] = np.clip(outside[feather] / edge, 0.0, 1.0)

    channels = img.channels
    pixels = np.asarray(img.pixels[:], dtype=np.float32).reshape((h, w, channels))
    before = pixels[:, :, 1].copy()
    pixels[:, :, 1] *= keep_factor
    if channels >= 4:
        pixels[:, :, 3] = 1.0
    img.pixels.foreach_set(pixels.ravel())
    try:
        img.update()
    except Exception:
        pass
    _save_mask_image(img, GRASS_MASK_FILE)

    changed = int((np.abs(before - pixels[:, :, 1]) > 0.001).sum())
    cleared = int((pixels[:, :, 1] < 0.01).sum() - (before < 0.01).sum())
    print(f"  cleared grass under projects hut: changed={changed} newly_zero={max(cleared, 0)}")


def run():
    print("[04-markers-section-y-projects-hut-base] build projects hut base")
    base_x, base_z = LOCATION
    ground = _height_at(base_x, base_z)
    if ground is None or ground < -0.05:
        print(f"  [ABORT] invalid terrain at ({base_x:.1f},{base_z:.1f}) height={ground}")
        return

    _cleanup()
    mats = _materials()

    _add_entry(base_x, base_z, ground, mats)
    _add_wall_planks(base_x, base_z, ground, mats)
    _add_buttresses(base_x, base_z, ground, mats)
    _add_roof(base_x, base_z, ground, mats)
    _add_windows_and_lamps(base_x, base_z, ground, mats)
    _add_sign(base_x, base_z, ground, mats)
    _add_screen(base_x, base_z, ground, mats)
    _add_path(base_x, base_z, ground, mats)
    _add_refs(base_x, base_z, ground)
    _add_footprint(base_x, base_z, ground, mats["footprint"])
    _restore_authored_grass_mask()
    _clear_grass_under_hut(base_x, base_z)

    # Door/board placeholders are custom properties for the runtime pass.
    for obj in _lib.get_collection(MARKER_COLLECTION).objects:
        obj["section"] = "projects"
        obj["phase"] = "04c-projects-hut-base"

    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")
    print(
        f"  built projects hut base at ({base_x:.1f},{base_z:.1f},{ground:.3f}) "
        f"yaw={math.degrees(YAW):.1f}deg"
    )


if __name__ == "__main__":
    run()
