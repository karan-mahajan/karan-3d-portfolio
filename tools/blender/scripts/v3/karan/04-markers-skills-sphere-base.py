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
SPHERE_RADIUS = 6.0
SPHERE_CENTER_HEIGHT = 7.0
FOOTPRINT = (15.0, 15.0, 13.0)

# Pond anchoring + dressing. No flat water plane exists in this build — water is
# a terrain shader tint (see 02-ground-grass-water.py) — so the waterline is
# sampled at runtime: fill the depression to just under its lowest containing
# lip on a ring at the pond edge. Tune these two if the surface reads off.
WATERLINE_RING_R = 8.0
WATERLINE_DROP = 0.10

MATERIALS = {
    "skill_base_dark_stone": (0.20, 0.23, 0.20, 1.0),
    "skill_base_edge_stone": (0.42, 0.45, 0.39, 1.0),
    "skill_base_warm_wood": (0.40, 0.20, 0.08, 1.0),
    "skill_base_green_inlay": (0.10, 0.58, 0.34, 1.0),
    "skill_base_ring_glow": (0.34, 0.92, 0.62, 0.55),
    "skill_base_core_glow": (0.40, 1.00, 0.70, 1.0),
    "skill_base_shell_glow": (0.34, 0.92, 0.62, 0.08),
    "skill_base_halo_glow": (0.40, 1.00, 0.70, 0.12),
    "skill_base_column_glow": (0.34, 0.92, 0.62, 0.50),
    "skill_base_waterline_glow": (0.34, 0.92, 0.62, 0.60),
    "skill_base_subsurface_glow": (0.30, 0.85, 0.60, 0.18),
    "skill_base_reed": (0.16, 0.42, 0.20, 1.0),
    "skill_base_lilypad": (0.10, 0.45, 0.22, 1.0),
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


def _waterline_z(x, z, water_bed):
    """Rim-fill waterline for the pond, sampled from real terrain.

    No flat water plane exists in this build (water is a shader tint on the
    depression), so fill the bowl to just under its lowest containing lip on a
    ring at the pond edge. Degrades to a shallow level if the ring degenerates
    (e.g. flat terrain or a river outflow that drags the minimum to the bed).
    """
    lips = []
    for i in range(24):
        a = 2.0 * math.pi * i / 24.0
        h = _height_at(x + math.cos(a) * WATERLINE_RING_R, z + math.sin(a) * WATERLINE_RING_R)
        if h is not None:
            lips.append(h)
    if not lips:
        return water_bed + 0.6
    lowest_lip = min(lips)
    if lowest_lip <= water_bed + 0.05:
        return water_bed + 0.6
    return lowest_lip - WATERLINE_DROP


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
            if "ring" in name:
                strength = 0.9
            elif "shell" in name:
                strength = 0.55
            elif "halo" in name:
                strength = 0.85
            elif "column" in name:
                strength = 1.0
            elif "core" in name:
                strength = 2.2
            elif "waterline" in name:
                strength = 1.1
            elif "subsurface" in name:
                strength = 0.5
            else:
                strength = 1.6
            bsdf.inputs["Emission Strength"].default_value = strength
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


def _sphere(name, radius, location, material, segments=32, ring_count=16):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments,
        ring_count=ring_count,
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
    waterline = _waterline_z(x, z, water_bed)

    _cleanup()

    dark_stone = _material("skill_base_dark_stone")
    edge_stone = _material("skill_base_edge_stone")
    warm_wood = _material("skill_base_warm_wood")
    green = _material("skill_base_green_inlay")
    ring_glow = _material("skill_base_ring_glow")
    core_glow = _material("skill_base_core_glow")
    shell_glow = _material("skill_base_shell_glow")
    halo_glow = _material("skill_base_halo_glow")
    column_glow = _material("skill_base_column_glow")
    waterline_glow = _material("skill_base_waterline_glow")
    subsurface_glow = _material("skill_base_subsurface_glow")
    reed_mat = _material("skill_base_reed")
    lilypad_mat = _material("skill_base_lilypad")
    footprint_mat = _material("skill_base_footprint")

    # Floating layered plinth: high enough to leave visible air over the pond,
    # compact enough that the runtime text sphere remains the hero.
    _cylinder("skillSphere_plinth_lower", 3.75, 0.30, (x, z, ground + 0.15), dark_stone, vertices=96, scale=(1.03, 0.97, 1.0))
    _cylinder("skillSphere_plinth_upper", 3.06, 0.24, (x, z, ground + 0.42), edge_stone, vertices=96, scale=(1.01, 0.95, 1.0))
    _cylinder("skillSphere_inlay_disc", 2.44, 0.06, (x, z, ground + 0.58), green, vertices=96, scale=(1.00, 0.92, 1.0))
    _cylinder("skillSphere_core_pedestal", 0.95, 1.10, (x, z, ground + 1.05), warm_wood, vertices=18, scale=(1.0, 1.0, 1.0))

    center = (x, z, ground + SPHERE_CENTER_HEIGHT)
    cz = ground + SPHERE_CENTER_HEIGHT

    # Layered glowing nucleus: bright inner orb + soft halo + rising energy
    # column. Each part is a separate centred object so Three.js can fetch it by
    # name and pulse/rotate it independently of the orbit cage.
    _sphere("skillSphere_core_inner", 0.58, center, core_glow)
    _sphere("skillSphere_core_halo", 1.45, center, halo_glow, segments=48, ring_count=24)
    # Column spans pedestal top (ground+1.60) to core centre (ground+7.0):
    # length 5.40, centred at ground+4.30.
    _cylinder("skillSphere_energy_column", 0.07, 5.40, (x, z, ground + 4.30), column_glow, vertices=12)

    # Orbit cage: thickened equator + 4 meridians read as a visible globe frame.
    # Origins sit at the sphere centre so Three.js spins them about the core.
    _torus("skillSphere_orbit_ring_equator", SPHERE_RADIUS, 0.09, center, (0.0, 0.0, 0.0), ring_glow)
    _torus("skillSphere_orbit_ring_meridian_a", SPHERE_RADIUS, 0.08, center, (math.radians(90.0), 0.0, math.radians(0.0)), ring_glow)
    _torus("skillSphere_orbit_ring_meridian_b", SPHERE_RADIUS, 0.08, center, (math.radians(90.0), 0.0, math.radians(45.0)), ring_glow)
    _torus("skillSphere_orbit_ring_meridian_c", SPHERE_RADIUS, 0.08, center, (math.radians(90.0), 0.0, math.radians(90.0)), ring_glow)
    _torus("skillSphere_orbit_ring_meridian_d", SPHERE_RADIUS, 0.08, center, (math.radians(90.0), 0.0, math.radians(135.0)), ring_glow)

    # Horizontal latitude rings (rotation 0) above/below the equator so the cage
    # reads as a globe, not a meridian fan. r = sqrt(R^2 - h^2) per height.
    lat_mid_r = math.sqrt(SPHERE_RADIUS**2 - 3.0**2)   # ~5.20
    lat_high_r = math.sqrt(SPHERE_RADIUS**2 - 4.5**2)  # ~3.97
    _torus("skillSphere_orbit_lat_north_mid", lat_mid_r, 0.08, (x, z, cz + 3.0), (0.0, 0.0, 0.0), ring_glow)
    _torus("skillSphere_orbit_lat_south_mid", lat_mid_r, 0.08, (x, z, cz - 3.0), (0.0, 0.0, 0.0), ring_glow)
    _torus("skillSphere_orbit_lat_north_high", lat_high_r, 0.06, (x, z, cz + 4.5), (0.0, 0.0, 0.0), ring_glow)
    _torus("skillSphere_orbit_lat_south_high", lat_high_r, 0.06, (x, z, cz - 4.5), (0.0, 0.0, 0.0), ring_glow)

    # Faint emissive shell membrane gives the cage a glowing globe surface
    # without a solid ball (low alpha + BLEND via the _material helper).
    _sphere("skillSphere_orb_shell", SPHERE_RADIUS, center, shell_glow, segments=48, ring_count=24)

    # Four slim posts visually cradle the runtime sphere without boxing it in.
    for i, angle in enumerate((45, 135, 225, 315)):
        a = math.radians(angle)
        px = x + math.cos(a) * 2.66
        pz = z + math.sin(a) * 2.66
        post = _cuboid_mesh(f"skillSphere_support_post_{i:02d}", (0.0, 0.0, 1.55), (0.11, 0.11, 1.55), warm_wood)
        post.location = (px, pz, ground + 0.55)
        post.rotation_mode = "XYZ"
        post.rotation_euler = (0.0, 0.0, a + math.radians(45.0))
        _place(post)
        cap = _sphere(f"skillSphere_support_cap_{i:02d}", 0.22, (px, pz, ground + 3.75), ring_glow)
        cap.scale = (1.0, 1.0, 0.72)

    # === 1. Waterline anchor — tie the floating orb to the pond surface. ===
    # `waterline` is the rim-fill level sampled above. Ring sits just outside the
    # plinth; the broad disc glows faintly just under the surface.
    _torus("skillSphere_waterline_ring", 5.7, 0.10, (x, z, waterline), (0.0, 0.0, 0.0), waterline_glow)
    _cylinder("skillSphere_waterline_disc", 6.5, 0.05, (x, z, waterline - 0.08), subsurface_glow, vertices=72)

    # Approach corridor: pond center → world origin (island interior, ~NE).
    # Reeds/rocks/pads skip a wedge around it so the walk-in path stays clear.
    approach_angle = math.atan2(-z, -x)

    def _near_approach(angle, half_wedge=math.radians(26.0)):
        d = abs((angle - approach_angle + math.pi) % (2.0 * math.pi) - math.pi)
        return d < half_wedge

    # === 2a. Reeds — clusters of slim blades emerging from the water. ===
    reed_idx = 0
    for ci, deg in enumerate((15, 70, 120, 165, 210, 255, 300, 340)):
        base_a = math.radians(deg)
        if _near_approach(base_a):
            continue
        cluster_r = 6.2 + (ci % 3) * 0.9
        cx = x + math.cos(base_a) * cluster_r
        cy = z + math.sin(base_a) * cluster_r
        for b in range(3 + (ci % 3)):
            spread = 0.18 + 0.09 * b
            bx = cx + math.cos(base_a + b * 1.7) * spread
            by = cy + math.sin(base_a + b * 1.7) * spread
            bed = _height_at(bx, by)
            if bed is None:
                continue
            tip_above = 0.55 + 0.30 * ((ci + b) % 3)
            height = min(max(bed, waterline) + tip_above - bed, 1.9)
            reed = _cylinder(f"skillSphere_reed_{reed_idx:02d}", 0.04, height, (bx, by, bed + height * 0.5), reed_mat, vertices=6)
            lean = math.radians(6.0 + 2.0 * (b % 3))
            reed.rotation_euler = (lean * math.cos(base_a), lean * math.sin(base_a), 0.0)
            reed_idx += 1

    # === 2b. Lily pads — flat oval discs floating at the surface. ===
    pad_idx = 0
    for pi, deg in enumerate((40, 95, 150, 230, 285, 320)):
        a = math.radians(deg)
        if _near_approach(a):
            continue
        pad_r = 6.0 + (pi % 4) * 0.7
        pad = _cylinder(
            f"skillSphere_lilypad_{pad_idx:02d}",
            0.38 + 0.06 * (pi % 4), 0.03,
            (x + math.cos(a) * pad_r, z + math.sin(a) * pad_r, waterline + 0.015),
            lilypad_mat, vertices=20,
        )
        pad.scale = (1.0, 0.82, 1.0)
        pad_idx += 1

    # === 2c. Rocks — squashed boulders embedded at the pond rim. ===
    rock_idx = 0
    for ri, deg in enumerate((25, 80, 135, 190, 245, 300, 350)):
        a = math.radians(deg)
        if _near_approach(a):
            continue
        rock_r = 6.5 + (ri % 3) * 0.8
        rx = x + math.cos(a) * rock_r
        ry = z + math.sin(a) * rock_r
        bed = _height_at(rx, ry)
        if bed is None:
            continue
        size = 0.45 + 0.12 * (ri % 4)
        rock = _sphere(f"skillSphere_rock_{rock_idx:02d}", size, (rx, ry, max(bed, waterline) - 0.10), edge_stone if ri % 2 == 0 else dark_stone)
        rock.scale = (1.0 + 0.12 * (ri % 3), 0.9, 0.6 + 0.08 * (ri % 2))
        rock_idx += 1

    # === 3. Stepping stones — a walkable run from the shore to the plinth. ===
    # March outward along the approach until terrain rises above the waterline.
    step_dir = (math.cos(approach_angle), math.sin(approach_angle))
    step_idx = 0
    shore = None
    for s in range(6):
        sr = 5.6 + s * 1.5
        sx = x + step_dir[0] * sr
        sy = z + step_dir[1] * sr
        bed = _height_at(sx, sy)
        if bed is None:
            break
        top_z = max(bed, waterline) + 0.06
        _cylinder(f"skillSphere_steppingstone_{step_idx:02d}", 0.78 - 0.04 * s, 0.25, (sx, sy, top_z - 0.125), edge_stone, vertices=20)
        step_idx += 1
        if bed > waterline + 0.05:
            shore = (sx, sy, bed)
            break
    if shore is not None:
        _cylinder("skillSphere_approach_pad", 1.9, 0.08, (shore[0], shore[1], shore[2] + 0.04), green, vertices=48)

    _add_ref(x, z, ground)
    _add_footprint(x, z, water_bed, footprint_mat)

    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")
    print(
        f"  built floating skill sphere at ({x:.1f},{z:.1f}) "
        f"water_bed={water_bed:.3f} waterline={waterline:.3f} base={ground:.3f} "
        f"radius={SPHERE_RADIUS:.1f} | reeds={reed_idx} pads={pad_idx} "
        f"rocks={rock_idx} steps={step_idx}"
    )


if __name__ == "__main__":
    run()
