"""Build the base Projects hut landmark.

This is the first approval pass for the east Projects section marker. It
replaces the generic three-card marker from 04-markers-section-landmarks.py
with a compact walk-in hut: stone pad, wooden walls, pitched roof, porch,
arched door, warm windows, hanging lamps, side lanterns, sign, section ref,
and hidden footprint.

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

FOOTPRINT = (12.4 * PLAN_SCALE, 10.4 * PLAN_SCALE, 7.4)
INTERACTION_OFFSET = (0.0, -4.15)
DOOR_CLEARANCE_OFFSET = (0.0, -2.92)
GRASS_CLEAR_HALF_EXTENTS = (7.20 * PLAN_SCALE, 6.40 * PLAN_SCALE)
GRASS_CLEAR_SOFT_EDGE = 0.65

MATERIALS = {
    "project_hut_stone": (0.31, 0.32, 0.28, 1.0),
    "project_hut_stone_edge": (0.46, 0.47, 0.40, 1.0),
    "project_hut_wall_wood": (0.42, 0.20, 0.075, 1.0),
    "project_hut_wall_wood_light": (0.68, 0.38, 0.14, 1.0),
    "project_hut_dark_wood": (0.12, 0.060, 0.025, 1.0),
    "project_hut_roof": (0.72, 0.51, 0.24, 1.0),
    "project_hut_roof_dark": (0.36, 0.22, 0.08, 1.0),
    "project_hut_door": (0.16, 0.075, 0.025, 1.0),
    "project_hut_window_glow": (1.0, 0.76, 0.34, 0.88),
    "project_hut_lamp_glow": (1.0, 0.70, 0.32, 0.92),
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
        "wall": _material("project_hut_wall_wood", 0.74),
        "wall_light": _material("project_hut_wall_wood_light", 0.72),
        "dark": _material("project_hut_dark_wood", 0.70),
        "roof": _material("project_hut_roof", 0.84),
        "roof_dark": _material("project_hut_roof_dark", 0.82),
        "door": _material("project_hut_door", 0.68),
        "window": _material("project_hut_window_glow", 0.34, emissive_strength=2.6),
        "lamp": _material("project_hut_lamp_glow", 0.28, emissive_strength=4.2),
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


def _cuboid(name, center, size, material, rotation_y=0.0, collection=MARKER_COLLECTION):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center, rotation=(0.0, rotation_y, YAW))
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"projectHutMesh_{name}"
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    return _place(obj, collection)


def _local_cuboid(name, base_x, base_z, ground, local_x, local_y, local_z, size, material, rotation_y=0.0):
    wx, wz = _world(base_x, base_z, local_x, local_y)
    return _cuboid(name, (wx, wz, ground + local_z), _plan_size(size), material, rotation_y=rotation_y)


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


def _roof_mesh(name, material):
    half_w = 3.72 * PLAN_SCALE
    half_d = 2.98 * PLAN_SCALE
    eave_z = 3.55
    ridge_z = 5.22
    verts = [
        (-half_w, -half_d, eave_z),
        (half_w, -half_d, eave_z),
        (0.0, -half_d, ridge_z),
        (-half_w, half_d, eave_z),
        (half_w, half_d, eave_z),
        (0.0, half_d, ridge_z),
    ]
    faces = [
        (0, 3, 5, 2),
        (1, 2, 5, 4),
        (0, 1, 4, 3),
        (0, 2, 1),
        (3, 4, 5),
    ]
    mesh = bpy.data.meshes.new(f"projectHutMesh_{name}")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
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


def _add_wall_planks(base_x, base_z, ground, mats):
    # Main walls are split so the door is an actual opening.
    _local_cuboid("projectHut_back_wall", base_x, base_z, ground, 0.0, 1.76, 1.82, (5.70, 0.24, 3.02), mats["wall"])
    _local_cuboid("projectHut_left_wall", base_x, base_z, ground, -2.74, 0.0, 1.78, (0.24, 3.70, 2.96), mats["wall"])
    _local_cuboid("projectHut_right_wall", base_x, base_z, ground, 2.74, 0.0, 1.78, (0.24, 3.70, 2.96), mats["wall"])
    _local_cuboid("projectHut_front_wall_left", base_x, base_z, ground, -1.78, -1.76, 1.78, (1.95, 0.24, 2.96), mats["wall"])
    _local_cuboid("projectHut_front_wall_right", base_x, base_z, ground, 1.78, -1.76, 1.78, (1.95, 0.24, 2.96), mats["wall"])
    _local_cuboid("projectHut_front_header", base_x, base_z, ground, 0.0, -1.76, 3.15, (5.72, 0.28, 0.42), mats["dark"])

    # Large beams make the hut read as authored timber construction.
    for local_x in (-2.98, 2.98):
        _local_cuboid(f"projectHut_front_post_{local_x:+.0f}", base_x, base_z, ground, local_x, -1.90, 1.86, (0.22, 0.28, 3.30), mats["dark"])
        _local_cuboid(f"projectHut_back_post_{local_x:+.0f}", base_x, base_z, ground, local_x, 1.90, 1.86, (0.22, 0.28, 3.30), mats["dark"])
    for z_level in (0.76, 1.66, 2.56):
        _local_cuboid(f"projectHut_front_beam_{z_level:.1f}", base_x, base_z, ground, 0.0, -1.94, z_level, (5.96, 0.16, 0.13), mats["dark"])
        _local_cuboid(f"projectHut_back_beam_{z_level:.1f}", base_x, base_z, ground, 0.0, 1.94, z_level, (5.96, 0.16, 0.13), mats["dark"])

    # Subtle vertical planks on the front.
    for i, local_x in enumerate((-2.26, -1.30, 1.30, 2.26)):
        _local_cuboid(f"projectHut_front_plank_{i:02d}", base_x, base_z, ground, local_x, -2.055, 1.66, (0.055, 0.08, 2.20), mats["wall_light"])


def _add_roof(base_x, base_z, ground, mats):
    roof = _roof_mesh("projectHut_roof_main", mats["roof"])
    roof.location = (base_x, base_z, ground)
    roof.rotation_mode = "XYZ"
    roof.rotation_euler = (0.0, 0.0, YAW)
    _place(roof)

    _local_cuboid("projectHut_roof_ridge", base_x, base_z, ground, 0.0, 0.0, 5.28, (0.18, 6.20, 0.18), mats["roof_dark"])
    _local_cuboid("projectHut_front_eave", base_x, base_z, ground, 0.0, -3.07, 3.48, (7.64, 0.24, 0.22), mats["roof_dark"])
    _local_cuboid("projectHut_back_eave", base_x, base_z, ground, 0.0, 3.07, 3.48, (7.64, 0.24, 0.22), mats["roof_dark"])

    # Thin roof ribs on the visible front slope.
    for i, local_x in enumerate((-2.88, -1.92, -0.96, 0.0, 0.96, 1.92, 2.88)):
        rib = _local_cuboid(f"projectHut_roof_front_rib_{i:02d}", base_x, base_z, ground, local_x, -3.14, 4.20, (0.055, 0.16, 1.95), mats["roof_dark"], rotation_y=math.radians(-27.0 if local_x < 0 else 27.0))
        rib["decorative_roof_rib"] = True


def _add_entry(base_x, base_z, ground, mats):
    # Shaped foundation and porch. This replaces the earlier round pad with a
    # rectilinear stone/wood base that matches the concept hut silhouette.
    _local_cuboid("projectHut_foundation_underlay", base_x, base_z, ground, 0.0, 0.0, 0.035, (7.65, 5.78, 0.07), mats["stone"])
    _local_cuboid("projectHut_foundation_stone_slab", base_x, base_z, ground, 0.0, 0.0, 0.08, (6.72, 4.82, 0.16), mats["stone"])
    _local_cuboid("projectHut_foundation_front_step", base_x, base_z, ground, 0.0, -3.05, 0.10, (3.10, 1.10, 0.20), mats["stone_edge"])
    _local_cuboid("projectHut_foundation_rear_edge", base_x, base_z, ground, 0.0, 2.46, 0.22, (6.92, 0.26, 0.28), mats["stone_edge"])
    _local_cuboid("projectHut_foundation_left_edge", base_x, base_z, ground, -3.48, 0.0, 0.22, (0.26, 4.82, 0.28), mats["stone_edge"])
    _local_cuboid("projectHut_foundation_right_edge", base_x, base_z, ground, 3.48, 0.0, 0.22, (0.26, 4.82, 0.28), mats["stone_edge"])
    _local_cuboid("projectHut_porch_deck", base_x, base_z, ground, 0.0, -2.72, 0.30, (2.90, 1.54, 0.22), mats["wall_light"])
    _local_cuboid("projectHut_porch_lip", base_x, base_z, ground, 0.0, -3.50, 0.46, (3.12, 0.18, 0.28), mats["dark"])
    for i, local_x in enumerate((-0.84, 0.0, 0.84)):
        _local_cuboid(f"projectHut_porch_plank_{i:02d}", base_x, base_z, ground, local_x, -2.65, 0.325, (0.055, 1.32, 0.035), mats["dark"])

    frame = _arch_panel_mesh("projectHut_door_arch_frame", mats["dark"], width=1.48, height=2.25, arch_radius=0.74, depth=0.16)
    wx, wz = _world(base_x, base_z, 0.0, -1.99)
    frame.location = (wx, wz, ground + 0.30)
    frame.rotation_mode = "XYZ"
    frame.rotation_euler = (0.0, 0.0, YAW)
    _place(frame)

    door = _arch_panel_mesh("projectHut_front_door", mats["door"])
    wx, wz = _world(base_x, base_z, 0.0, -1.925)
    door.location = (wx, wz, ground + 0.40)
    door.rotation_mode = "XYZ"
    door.rotation_euler = (0.0, 0.0, YAW)
    door["section"] = "projects"
    door["interaction"] = "projectsHut"
    _place(door)

    # Solid returns behind the arch hide the interior/grass through the door
    # seams while keeping the door itself readable as an inset panel.
    _local_cuboid("projectHut_door_left_return_fill", base_x, base_z, ground, -0.88, -2.04, 1.62, (0.36, 0.22, 2.42), mats["door_return"])
    _local_cuboid("projectHut_door_right_return_fill", base_x, base_z, ground, 0.88, -2.04, 1.62, (0.36, 0.22, 2.42), mats["door_return"])
    _local_cuboid("projectHut_door_top_return_fill", base_x, base_z, ground, 0.0, -2.04, 2.68, (1.78, 0.22, 0.42), mats["door_return"])

    # Door frame follows the arch but uses separate timber pieces for depth.
    _local_cuboid("projectHut_door_left_jamb", base_x, base_z, ground, -0.70, -2.02, 1.26, (0.14, 0.18, 1.76), mats["dark"])
    _local_cuboid("projectHut_door_right_jamb", base_x, base_z, ground, 0.70, -2.02, 1.26, (0.14, 0.18, 1.76), mats["dark"])
    _sphere("projectHut_door_knob", 0.075, (*_world(base_x, base_z, 0.42, -2.105), ground + 1.32), mats["lamp"], scale=(1.0, 1.0, 0.82))


def _add_windows_and_lamps(base_x, base_z, ground, mats):
    for key, local_x in (("left", -1.75), ("right", 1.75)):
        _local_cuboid(f"projectHut_window_{key}_glow", base_x, base_z, ground, local_x, -2.055, 2.12, (0.72, 0.06, 0.54), mats["window"])
        _local_cuboid(f"projectHut_window_{key}_frame_top", base_x, base_z, ground, local_x, -2.095, 2.44, (0.86, 0.10, 0.09), mats["dark"])
        _local_cuboid(f"projectHut_window_{key}_frame_bottom", base_x, base_z, ground, local_x, -2.095, 1.80, (0.86, 0.10, 0.09), mats["dark"])
        _local_cuboid(f"projectHut_window_{key}_frame_side_a", base_x, base_z, ground, local_x - 0.43, -2.095, 2.12, (0.09, 0.10, 0.62), mats["dark"])
        _local_cuboid(f"projectHut_window_{key}_frame_side_b", base_x, base_z, ground, local_x + 0.43, -2.095, 2.12, (0.09, 0.10, 0.62), mats["dark"])
        _add_light(f"projectHut_windowLight_{key}", base_x, base_z, ground, local_x, -2.30, 2.12, 85.0, 2.0)

    # Hanging lamps under the front eaves.
    for key, local_x in (("left", -3.05), ("right", 3.05)):
        _local_cuboid(f"projectHut_hangingLamp_{key}_bracket", base_x, base_z, ground, local_x, -2.48, 3.18, (0.10, 0.72, 0.10), mats["dark"])
        _local_cuboid(f"projectHut_hangingLamp_{key}_chain", base_x, base_z, ground, local_x, -2.84, 2.84, (0.045, 0.045, 0.42), mats["dark"])
        _sphere(f"projectHut_hangingLamp_{key}_glow", 0.22, (*_world(base_x, base_z, local_x, -2.86), ground + 2.54), mats["lamp"], scale=(1.0, 1.0, 0.82))
        _add_light(f"projectHut_hangingLight_{key}", base_x, base_z, ground, local_x, -2.88, 2.54, 130.0, 2.4)

    # Two standing lanterns beside the porch echo the existing lantern language.
    for key, local_x in (("left", -2.15), ("right", 2.15)):
        _local_cuboid(f"projectHut_porchLamp_{key}_base", base_x, base_z, ground, local_x, -3.40, 0.08, (0.28, 0.28, 0.16), mats["dark"])
        _local_cuboid(f"projectHut_porchLamp_{key}_post", base_x, base_z, ground, local_x, -3.40, 0.82, (0.08, 0.08, 1.32), mats["dark"])
        _local_cuboid(f"projectHut_porchLamp_{key}_cage", base_x, base_z, ground, local_x, -3.40, 1.56, (0.34, 0.34, 0.38), mats["wall_light"])
        _sphere(f"projectHut_porchLamp_{key}_glow", 0.18, (*_world(base_x, base_z, local_x, -3.40), ground + 1.56), mats["lamp"], scale=(1.0, 1.0, 0.90))
        _add_light(f"projectHut_porchLight_{key}", base_x, base_z, ground, local_x, -3.40, 1.56, 95.0, 1.8)


def _add_sign(base_x, base_z, ground, mats):
    _local_cuboid("projectHut_sign_board", base_x, base_z, ground, 0.0, -2.20, 3.34, (2.10, 0.20, 0.48), mats["sign_face"])
    _local_cuboid("projectHut_sign_top_trim", base_x, base_z, ground, 0.0, -2.225, 3.61, (2.26, 0.18, 0.08), mats["dark"])
    _local_cuboid("projectHut_sign_bottom_trim", base_x, base_z, ground, 0.0, -2.225, 3.07, (2.26, 0.18, 0.08), mats["dark"])
    _text("projectHut_sign_text", "PROJECTS", base_x, base_z, ground, 0.0, -2.325, 3.34, 0.30, mats["sign_text"])


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
    ref["interiorBoardLocalOffset"] = (0.0, 1.38, 2.28)
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


def _clear_grass_under_hut(base_x, base_z):
    img = bpy.data.images.get(GRASS_IMAGE)
    terrain = _terrain()
    if img is None or terrain is None:
        print(f"  [WARN] grass clear skipped: image={bool(img)} terrain={bool(terrain)}")
        return

    w, h = img.size
    if w == 0 or h == 0 or img.channels < 2:
        print(f"  [WARN] grass clear skipped: invalid {GRASS_IMAGE!r} image")
        return

    corners = [terrain.matrix_world @ Vector(c) for c in terrain.bound_box]
    min_x = min(c.x for c in corners)
    max_x = max(c.x for c in corners)
    min_z = min(c.y for c in corners)
    max_z = max(c.y for c in corners)
    width = max_x - min_x
    depth = max_z - min_z
    if width <= 0.0 or depth <= 0.0:
        print("  [WARN] grass clear skipped: invalid terrain bounds")
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
    _add_roof(base_x, base_z, ground, mats)
    _add_windows_and_lamps(base_x, base_z, ground, mats)
    _add_sign(base_x, base_z, ground, mats)
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
