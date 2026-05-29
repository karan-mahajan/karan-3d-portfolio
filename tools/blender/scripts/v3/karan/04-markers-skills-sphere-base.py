"""Build the dedicated floating Skills sphere landmark.

This replaces the simple generic `sectionMarker_skills` totem produced by
04-markers-section-landmarks.py with a larger floating water installation for
the runtime Three.js skill globe:

  Blender owns: floating plinth, pedestal, orbit-frame rings, core holder,
  section ref, and hidden footprint.

  Three.js owns later: rotating skill text labels, enter-sphere camera move,
  label billboarding/readability, speed, and interaction state.

Run on the already-built karan world:
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/04-markers-skills-sphere-base.py').read())
"""
import math
import sys

import bmesh
import bpy
from mathutils import Vector

TOOLS_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts"
if TOOLS_DIR not in sys.path:
    sys.path.append(TOOLS_DIR)

import _lib

BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"
MARKER_COLLECTION = "sectionMarkers/skillsSphere"
COLLIDER_COLLECTION = "colliders"
REF_COLLECTION = "refs"

# Big south-west pond next to the skills area. This is the weighted low-water
# center of the actual connected terrain depression in the saved datablock.
LOCATION = (-34.14, -35.72)
YAW = math.radians(180.0)
FLOAT_CLEARANCE = 1.55
SPHERE_RADIUS = 8.4
SPHERE_CENTER_HEIGHT = 9.10
FOOTPRINT = (17.0, 17.0, 13.0)

MATERIALS = {
    "skill_base_dark_stone": (0.20, 0.23, 0.20, 1.0),
    "skill_base_edge_stone": (0.42, 0.45, 0.39, 1.0),
    "skill_base_warm_wood": (0.40, 0.20, 0.08, 1.0),
    "skill_base_green_inlay": (0.10, 0.58, 0.34, 1.0),
    "skill_base_ring_glow": (0.34, 0.92, 0.62, 0.55),
    "skill_base_core_glow": (0.40, 1.00, 0.70, 0.82),
    "skill_base_footprint": (0.14, 0.22, 0.16, 0.20),
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


def _material(name):
    color = MATERIALS[name]
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = 0.72
        if "glow" in name:
            bsdf.inputs["Emission Color"].default_value = color
            bsdf.inputs["Emission Strength"].default_value = 0.9 if "ring" in name else 1.6
        if len(color) == 4 and color[3] < 1.0:
            bsdf.inputs["Alpha"].default_value = color[3]
            mat.blend_method = "BLEND"
            mat.use_screen_refraction = False
    return mat


def _cleanup():
    prefixes = (
        "sectionMarker_skills",
        "sectionLabel_skills",
        "sectionFootprint_skills",
        "sectionRef_skills",
        "skillSphere_",
    )
    for obj in list(bpy.data.objects):
        if obj.name.startswith(prefixes):
            bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        if mesh.name.startswith("skillSphereMesh_") and mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    for curve in list(bpy.data.curves):
        if curve.name.startswith("skillSphereCurve_") and curve.users == 0:
            bpy.data.curves.remove(curve)


def _place(obj, collection=MARKER_COLLECTION):
    _lib.place_in(collection, obj)
    return obj


def _shade(obj):
    if obj.type != "MESH":
        return obj
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


def _shadow(obj):
    for attr, value in (("cast_shadow", True), ("receive_shadow", True)):
        try:
            setattr(obj, attr, value)
        except Exception:
            pass
    return obj


def _cylinder(name, radius, depth, location, material, vertices=48, scale=(1.0, 1.0, 1.0)):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
        rotation=(0.0, 0.0, YAW),
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"skillSphereMesh_{name}"
    obj.scale = scale
    obj.data.materials.append(material)
    _shadow(obj)
    _shade(obj)
    return _place(obj)


def _torus(name, major_radius, minor_radius, location, rotation, material):
    bpy.ops.mesh.primitive_torus_add(
        major_segments=128,
        minor_segments=10,
        major_radius=major_radius,
        minor_radius=minor_radius,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"skillSphereMesh_{name}"
    obj.data.materials.append(material)
    _shadow(obj)
    _shade(obj)
    return _place(obj)


def _sphere(name, radius, location, material):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32,
        ring_count=16,
        radius=radius,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"skillSphereMesh_{name}"
    obj.data.materials.append(material)
    _shadow(obj)
    _shade(obj)
    return _place(obj)


def _cuboid_mesh(name, center, half_extents, material):
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(bm, uv, center, half_extents, "sand_gravel")
    mesh = bpy.data.meshes.new(f"skillSphereMesh_{name}")
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    _shadow(obj)
    return obj


def _add_ref(x, z, ground):
    ref = bpy.data.objects.new("sectionRef_skills", None)
    ref.empty_display_type = "PLAIN_AXES"
    ref.empty_display_size = 1.0
    ref.location = (x, z, ground + SPHERE_CENTER_HEIGHT)
    ref.rotation_euler = (0.0, 0.0, YAW)
    ref["section"] = "skills"
    ref["title"] = "Skills"
    ref["interaction"] = "skillSphere"
    ref["sphereRadius"] = SPHERE_RADIUS
    ref["sphereCenterHeight"] = SPHERE_CENTER_HEIGHT
    ref["waterMounted"] = True
    ref["floatClearance"] = FLOAT_CLEARANCE
    ref["enterCameraOffset"] = (0.0, 0.0, 0.85)
    _lib.place_in(REF_COLLECTION, ref)


def _add_footprint(x, z, ground, material):
    hx, hy, hz = FOOTPRINT[0] * 0.5, FOOTPRINT[1] * 0.5, FOOTPRINT[2] * 0.5
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(bm, uv, (0.0, 0.0, hz), (hx, hy, hz), "sand_gravel")
    mesh = bpy.data.meshes.new("skillSphereMesh_sectionFootprint_skills")
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(material)
    obj = bpy.data.objects.new("sectionFootprint_skills", mesh)
    obj.location = (x, z, ground)
    obj.rotation_mode = "XYZ"
    obj.rotation_euler = (0.0, 0.0, YAW)
    obj.display_type = "WIRE"
    obj.hide_viewport = True
    obj.hide_render = True
    obj["section_marker_footprint"] = True
    obj["section"] = "skills"
    obj["interaction"] = "skillSphere"
    _lib.place_in(COLLIDER_COLLECTION, obj)


def run():
    print("[04-markers-skills-sphere-base] build dedicated skill sphere base")
    x, z = LOCATION
    water_bed = _height_at(x, z)
    if water_bed is None:
        print(f"  [ABORT] invalid terrain at ({x:.1f},{z:.1f}) height=None")
        return
    ground = water_bed + FLOAT_CLEARANCE

    _cleanup()

    dark_stone = _material("skill_base_dark_stone")
    edge_stone = _material("skill_base_edge_stone")
    warm_wood = _material("skill_base_warm_wood")
    green = _material("skill_base_green_inlay")
    ring_glow = _material("skill_base_ring_glow")
    core_glow = _material("skill_base_core_glow")
    footprint_mat = _material("skill_base_footprint")

    # Floating layered plinth: high enough to leave visible air over the pond,
    # compact enough that the runtime text sphere remains the hero.
    _cylinder("skillSphere_plinth_lower", 5.25, 0.32, (x, z, ground + 0.16), dark_stone, vertices=96, scale=(1.03, 0.97, 1.0))
    _cylinder("skillSphere_plinth_upper", 4.28, 0.26, (x, z, ground + 0.45), edge_stone, vertices=96, scale=(1.01, 0.95, 1.0))
    _cylinder("skillSphere_inlay_disc", 3.42, 0.06, (x, z, ground + 0.625), green, vertices=96, scale=(1.00, 0.92, 1.0))
    _cylinder("skillSphere_core_pedestal", 1.06, 1.16, (x, z, ground + 1.24), warm_wood, vertices=18, scale=(1.0, 1.0, 1.0))
    _sphere("skillSphere_core_preview", 0.56, (x, z, ground + SPHERE_CENTER_HEIGHT), core_glow)

    # Five preview orbit rings echo the Three.js runtime globe. They are
    # static Blender geometry; Three.js will animate live skill labels later.
    center = (x, z, ground + SPHERE_CENTER_HEIGHT)
    _torus("skillSphere_orbit_ring_equator", SPHERE_RADIUS, 0.032, center, (0.0, 0.0, 0.0), ring_glow)
    _torus("skillSphere_orbit_ring_meridian_a", SPHERE_RADIUS, 0.028, center, (math.radians(90.0), 0.0, math.radians(0.0)), ring_glow)
    _torus("skillSphere_orbit_ring_meridian_b", SPHERE_RADIUS, 0.026, center, (math.radians(90.0), 0.0, math.radians(45.0)), ring_glow)
    _torus("skillSphere_orbit_ring_meridian_c", SPHERE_RADIUS, 0.024, center, (math.radians(90.0), 0.0, math.radians(90.0)), ring_glow)
    _torus("skillSphere_orbit_ring_meridian_d", SPHERE_RADIUS, 0.022, center, (math.radians(90.0), 0.0, math.radians(135.0)), ring_glow)

    # Four slim posts visually cradle the runtime sphere without boxing it in.
    for i, angle in enumerate((45, 135, 225, 315)):
        a = math.radians(angle)
        px = x + math.cos(a) * 3.72
        pz = z + math.sin(a) * 3.72
        post = _cuboid_mesh(f"skillSphere_support_post_{i:02d}", (0.0, 0.0, 2.16), (0.13, 0.13, 2.16), warm_wood)
        post.location = (px, pz, ground + 0.64)
        post.rotation_mode = "XYZ"
        post.rotation_euler = (0.0, 0.0, a + math.radians(45.0))
        _place(post)
        cap = _sphere(f"skillSphere_support_cap_{i:02d}", 0.28, (px, pz, ground + 4.98), ring_glow)
        cap.scale = (1.0, 1.0, 0.72)

    _add_ref(x, z, ground)
    _add_footprint(x, z, water_bed, footprint_mat)

    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")
    print(
        f"  built floating skill sphere at ({x:.1f},{z:.1f}) "
        f"water_bed={water_bed:.3f} base={ground:.3f} radius={SPHERE_RADIUS:.1f}"
    )


if __name__ == "__main__":
    run()
