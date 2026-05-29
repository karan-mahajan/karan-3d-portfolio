"""Replace the generic contact marker with a mailbox sign board.

The board uses the current portfolio contact language as a starting point, but
builds it as a taller 3D contact tower: mast, thick framed sign, raised cap,
braces, beacon, mailbox, and a ref point used by Three.js for the press-E
contact modal.

Run on the already-built karan world:
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/04-markers-section-z-contact-board.py').read())
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
MARKER_COLLECTION = "sectionMarkers/contactBoard"
COLLIDER_COLLECTION = "colliders"
REF_COLLECTION = "refs"

LOCATION = (-13.3709, 35.8798)
YAW = math.radians(45.0)
FOOTPRINT = (11.8, 9.2, 12.4)

MATERIALS = {
    "contact_board_dark_face": (0.025, 0.020, 0.018, 1.0),
    "contact_board_arch_wood": (0.22, 0.085, 0.025, 1.0),
    "contact_board_post_wood": (0.34, 0.16, 0.06, 1.0),
    "contact_board_text_name": (0.78, 0.34, 0.13, 1.0),
    "contact_board_text_glow": (1.00, 0.58, 0.22, 1.0),
    "contact_board_text_muted": (0.58, 0.50, 0.42, 1.0),
    "contact_board_mailbox": (0.45, 0.055, 0.030, 1.0),
    "contact_board_mailbox_dark": (0.18, 0.025, 0.015, 1.0),
    "contact_board_mailbox_flag": (0.78, 0.34, 0.13, 1.0),
    "contact_board_beacon": (0.92, 0.72, 0.38, 1.0),
    "contact_board_footprint": (0.18, 0.14, 0.11, 0.20),
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
        bsdf.inputs["Roughness"].default_value = 0.76
        if len(color) == 4 and color[3] < 1.0:
            bsdf.inputs["Alpha"].default_value = color[3]
            mat.blend_method = "BLEND"
    return mat


def _cleanup():
    prefixes = (
        "sectionMarker_contact",
        "sectionLabel_contact",
        "sectionRef_contact",
        "sectionFootprint_contact",
        "contactBoard_",
        "contactMailbox_",
    )
    exact = {"contact_inscription_plinth"}
    for obj in list(bpy.data.objects):
        if obj.name in exact or obj.name.startswith(prefixes):
            bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        if mesh.name.startswith("contactBoardMesh_") and mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    for curve in list(bpy.data.curves):
        if curve.name.startswith("contactBoardCurve_") and curve.users == 0:
            bpy.data.curves.remove(curve)


def _place(obj, collection=MARKER_COLLECTION):
    _lib.place_in(collection, obj)
    return obj


def _world(base_x, base_z, local_x, local_y):
    c = math.cos(YAW)
    s = math.sin(YAW)
    return (
        base_x + local_x * c - local_y * s,
        base_z + local_x * s + local_y * c,
    )


def _cuboid(name, center, size, material, collection=MARKER_COLLECTION):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center, rotation=(0.0, 0.0, YAW))
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"contactBoardMesh_{name}"
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    return _place(obj, collection)


def _local_cuboid(name, base_x, base_z, ground, local_x, local_y, local_z, size, material):
    wx, wz = _world(base_x, base_z, local_x, local_y)
    return _cuboid(name, (wx, wz, ground + local_z), size, material)


def _cylinder(name, radius, depth, center, material, vertices=18):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=center,
        rotation=(0.0, 0.0, YAW),
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"contactBoardMesh_{name}"
    obj.data.materials.append(material)
    return _place(obj)


def _sphere(name, radius, center, material):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24,
        ring_count=12,
        radius=radius,
        location=center,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"contactBoardMesh_{name}"
    obj.data.materials.append(material)
    return _place(obj)


def _arch_mesh(name, material):
    width = 8.35
    half = width * 0.5
    z_base = 8.96
    arch_h = 1.42
    radius = half
    thickness = 0.52
    segments = 24

    front = []
    back = []
    points = [(-half, z_base), (half, z_base)]
    for i in range(segments + 1):
        t = math.pi * (1.0 - i / segments)
        points.append((math.cos(t) * radius, z_base + math.sin(t) * arch_h))

    for x, z in points:
        front.append((x, -thickness * 0.5, z))
        back.append((x, thickness * 0.5, z))
    verts = front + back
    n = len(points)
    faces = [tuple(range(n)), tuple(range(n, 2 * n))[::-1]]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))

    mesh = bpy.data.meshes.new(f"contactBoardMesh_{name}")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    return obj


def _mailbox_body_mesh(name, material):
    length = 1.42
    depth = 0.78
    box_h = 0.44
    radius = depth * 0.5
    segments = 14
    points = [(-radius, 0.0), (radius, 0.0), (radius, box_h)]
    for i in range(segments + 1):
        t = math.pi * (i / segments)
        points.append((math.cos(t) * radius, box_h + math.sin(t) * radius))
    points.append((-radius, 0.0))

    verts = []
    for x in (-length * 0.5, length * 0.5):
        for y, z in points:
            verts.append((x, y, z))
    n = len(points)
    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    for i in range(n - 1):
        faces.append((i, i + 1, n + i + 1, n + i))

    mesh = bpy.data.meshes.new(f"contactBoardMesh_{name}")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    return obj


def _text(name, body, base_x, base_z, ground, local_x, local_z, size, material, animated=False):
    curve = bpy.data.curves.new(f"contactBoardCurve_{name}", "FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0.012
    curve.materials.append(material)
    obj = bpy.data.objects.new(name, curve)
    wx, wz = _world(base_x, base_z, local_x, -0.115)
    obj.location = (wx, wz, ground + local_z)
    obj.rotation_mode = "XYZ"
    obj.rotation_euler = (math.radians(90.0), 0.0, YAW)
    if animated:
        obj["runtime_animation"] = "contactTitlePulse"
        obj["runtime_section"] = "contact"
    return _place(obj)


def _add_ref(x, z, ground, ref_x, ref_z):
    ref = bpy.data.objects.new("sectionRef_contact", None)
    ref.empty_display_type = "PLAIN_AXES"
    ref.empty_display_size = 0.9
    ref.location = (ref_x, ref_z, ground + 1.15)
    ref.rotation_euler = (0.0, 0.0, YAW)
    ref["section"] = "contact"
    ref["title"] = "Contact"
    ref["interaction"] = "contactModal"
    ref["prompt"] = "press E"
    _lib.place_in(REF_COLLECTION, ref)


def _add_footprint(x, z, ground, material):
    hx, hy, hz = FOOTPRINT[0] * 0.5, FOOTPRINT[1] * 0.5, FOOTPRINT[2] * 0.5
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(bm, uv, (0.0, 0.0, hz), (hx, hy, hz), "sand_gravel")
    mesh = bpy.data.meshes.new("contactBoardMesh_sectionFootprint_contact")
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(material)
    obj = bpy.data.objects.new("sectionFootprint_contact", mesh)
    obj.location = (x, z, ground)
    obj.rotation_mode = "XYZ"
    obj.rotation_euler = (0.0, 0.0, YAW)
    obj.display_type = "WIRE"
    obj.hide_viewport = True
    obj.hide_render = True
    obj["section_marker_footprint"] = True
    obj["section"] = "contact"
    obj["interaction"] = "contactModal"
    _lib.place_in(COLLIDER_COLLECTION, obj)


def run():
    print("[04-markers-section-z-contact-board] build contact mailbox board")
    x, z = LOCATION
    ground = _height_at(x, z)
    if ground is None or ground < -0.05:
        print(f"  [ABORT] invalid terrain at ({x:.1f},{z:.1f}) height={ground}")
        return

    _cleanup()

    face = _material("contact_board_dark_face")
    arch = _material("contact_board_arch_wood")
    wood = _material("contact_board_post_wood")
    name_text = _material("contact_board_text_name")
    glow_text = _material("contact_board_text_glow")
    muted_text = _material("contact_board_text_muted")
    mailbox = _material("contact_board_mailbox")
    mailbox_dark = _material("contact_board_mailbox_dark")
    flag = _material("contact_board_mailbox_flag")
    beacon = _material("contact_board_beacon")
    footprint = _material("contact_board_footprint")

    _cylinder("contactBoard_center_post", 0.18, 10.8, (x, z, ground + 5.40), wood, vertices=18)
    _cylinder("contactBoard_top_beacon_stem", 0.075, 0.74, (x, z, ground + 10.92), wood, vertices=12)
    _sphere("contactBoard_top_beacon", 0.36, (x, z, ground + 11.36), beacon)

    _cuboid("contactBoard_upper_crossbar", (x, z, ground + 8.98), (8.70, 0.34, 0.26), wood)
    _cuboid("contactBoard_lower_crossbar", (x, z, ground + 3.96), (8.45, 0.30, 0.24), wood)
    board = _cuboid("contact_inscription_plinth", (x, z, ground + 6.46), (8.0, 0.60, 5.0), face)
    board["section"] = "contact"
    board["interaction"] = "contactModal"
    _cuboid("contactBoard_face_inset", (x, z, ground + 6.46), (7.42, 0.64, 4.28), face)
    _local_cuboid("contactBoard_left_frame", x, z, ground, -4.12, 0.0, 6.46, (0.24, 0.70, 5.22), wood)
    _local_cuboid("contactBoard_right_frame", x, z, ground, 4.12, 0.0, 6.46, (0.24, 0.70, 5.22), wood)
    _cuboid("contactBoard_bottom_frame", (x, z, ground + 3.96), (8.45, 0.70, 0.26), wood)

    arch_obj = _arch_mesh("contactBoard_arch_top", arch)
    arch_obj.location = (x, z, ground)
    arch_obj.rotation_mode = "XYZ"
    arch_obj.rotation_euler = (0.0, 0.0, YAW)
    _place(arch_obj)

    # Ground pad gives the player a clean approach point in grass.
    pad_mat = bpy.data.materials.get("marker_stone") or wood
    _cylinder("contactBoard_approach_pad", 2.55, 0.08, (x, z, ground + 0.04), pad_mat, vertices=56)

    # Angled braces make the sign read as a solid 3D structure from above.
    for i, local_x in enumerate((-2.42, 2.42)):
        bx, bz = _world(x, z, local_x, 0.35)
        brace = _cuboid(f"contactBoard_diagonal_brace_{i:02d}", (bx, bz, ground + 4.52), (0.16, 0.16, 3.85), wood)
        brace.rotation_euler[1] = math.radians(16.0 if local_x < 0 else -16.0)

    # Mailbox sits beside the tower and owns the actual contact interaction.
    mx, mz = _world(x, z, -3.35, -1.05)
    _cylinder("contactMailbox_post", 0.10, 1.32, (mx, mz, ground + 0.66), wood, vertices=12)
    mailbox_obj = _mailbox_body_mesh("contactMailbox_body", mailbox)
    mailbox_obj.location = (mx, mz, ground + 1.22)
    mailbox_obj.rotation_mode = "XYZ"
    mailbox_obj.rotation_euler = (0.0, 0.0, YAW)
    _place(mailbox_obj)
    door_x, door_z = _world(x, z, -2.62, -1.05)
    _cuboid("contactMailbox_door", (door_x, door_z, ground + 1.53), (0.12, 0.86, 0.74), mailbox_dark)
    fx, fz = _world(x, z, -2.84, -0.55)
    _cuboid("contactMailbox_flag", (fx, fz, ground + 1.78), (0.14, 0.10, 0.72), flag)
    _sphere("contactMailbox_signal_dot", 0.12, (fx, fz, ground + 2.18), beacon)

    _text("contactBoard_text_name_glow", "Karan Mahajan", x, z, ground, 0.0, 7.62, 0.86, glow_text, animated=True)
    _text("contactBoard_text_name", "Karan Mahajan", x, z, ground, 0.0, 7.58, 0.82, name_text, animated=True)
    _text("contactBoard_text_role", "FULL STACK WEB DEVELOPER", x, z, ground, 0.0, 6.78, 0.31, muted_text)
    _text("contactBoard_text_contact", "CONTACT", x, z, ground, 0.0, 5.68, 0.58, glow_text)
    _text("contactBoard_text_prompt", "MAILBOX - PRESS E", x, z, ground, 0.0, 4.80, 0.26, muted_text)

    _add_ref(x, z, ground, mx, mz)
    _add_footprint(x, z, ground, footprint)

    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")
    print(f"  built contact board at ({x:.1f},{z:.1f},{ground:.3f}) yaw={math.degrees(YAW):.1f}")


if __name__ == "__main__":
    run()
