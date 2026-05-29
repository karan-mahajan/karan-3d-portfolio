"""Author the four cardinal section landmarks for the walkable portfolio.

Decision pass before build:
  - Projects: KEEP Bruno's destination/zone-root idea, REPLACE the workshop
    pole with a compact project display frame on the east side.
  - Experience: KEEP Bruno's career-timeline idea, REPLACE it with a small
    north timeline obelisk.
  - Skills: KEEP Bruno's lab/learning signal, REPLACE the full lab with a
    south skill-totem landmark.
  - Contact: KEEP Bruno's social/contact zone idea, REPLACE the social icon
    cluster with a west signal/mail landmark.

All markers are authored as simple Blender geometry, placed on terrain by
raycast, and given hidden footprint boxes so later vegetation scripts can keep
clear of them.

Run on the already-built karan world:
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/04-markers-section-landmarks.py').read())
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
MARKER_COLLECTION = "sectionMarkers"
REF_COLLECTION = "refs"
COLLIDER_COLLECTION = "colliders"

MATERIALS = {
    "marker_dark_wood": (0.18, 0.09, 0.04, 1.0),
    "marker_warm_wood": (0.52, 0.28, 0.12, 1.0),
    "marker_stone": (0.33, 0.35, 0.33, 1.0),
    "marker_projects": (0.12, 0.38, 0.78, 1.0),
    "marker_experience": (0.80, 0.38, 0.12, 1.0),
    "marker_skills": (0.12, 0.58, 0.35, 1.0),
    "marker_contact": (0.72, 0.18, 0.38, 1.0),
    "marker_label": (0.93, 0.88, 0.72, 1.0),
    "marker_footprint": (0.15, 0.20, 0.18, 0.22),
}

MARKERS = [
    {
        "key": "projects",
        "title": "PROJECTS",
        "location": (38.0, 10.0),
        "yaw": math.radians(-90.0),
        "accent": "marker_projects",
        "footprint": (4.8, 3.2, 2.6),
    },
    {
        "key": "experience",
        "title": "EXPERIENCE",
        "location": (8.0, 36.0),
        "yaw": math.radians(180.0),
        "accent": "marker_experience",
        "footprint": (4.4, 4.4, 3.2),
    },
    {
        "key": "skills",
        "title": "SKILLS",
        "location": (-14.0, -34.0),
        "yaw": 0.0,
        "accent": "marker_skills",
        "footprint": (4.2, 4.2, 3.4),
    },
    {
        "key": "contact",
        "title": "CONTACT",
        "location": (-32.0, -12.0),
        "yaw": math.radians(90.0),
        "accent": "marker_contact",
        "footprint": (4.6, 3.6, 2.8),
    },
]


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
        bsdf.inputs["Roughness"].default_value = 0.82
        if len(color) == 4 and color[3] < 1.0:
            bsdf.inputs["Alpha"].default_value = color[3]
            mat.blend_method = "BLEND"
            mat.use_screen_refraction = False
    return mat


def _collection(name):
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


def _clear_marker_objects():
    prefixes = ("sectionMarker_", "sectionRef_", "sectionFootprint_", "sectionLabel_")
    for obj in list(bpy.data.objects):
        if obj.name.startswith(prefixes):
            bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        if mesh.name.startswith("sectionMarkerMesh_") and mesh.users == 0:
            bpy.data.meshes.remove(mesh)


def _cuboid(bm, center, half_extents, mat_index, face_materials):
    uv = bm.loops.layers.uv.verify()
    faces = _lib.bm_add_cuboid(bm, uv, center, half_extents, "sand_gravel")
    face_materials.extend([mat_index] * len(faces))
    return faces


def _cylinder(bm, center, radius, depth, mat_index, face_materials, vertices=10):
    result = bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        segments=vertices,
        radius1=radius,
        radius2=radius,
        depth=depth,
    )
    for vert in result["verts"]:
        vert.co += Vector(center)
    faces = {face for vert in result["verts"] for face in vert.link_faces}
    face_materials.extend([mat_index] * len(faces))
    return faces


def _build_projects(bm, face_materials):
    _cuboid(bm, (0.0, 0.0, 0.10), (1.95, 0.70, 0.10), 2, face_materials)
    for x in (-1.45, 1.45):
        _cuboid(bm, (x, 0.0, 1.28), (0.13, 0.13, 1.18), 0, face_materials)
    _cuboid(bm, (0.0, 0.0, 2.34), (1.70, 0.12, 0.16), 1, face_materials)
    for i, x in enumerate((-0.86, 0.0, 0.86)):
        _cuboid(bm, (x, -0.08, 1.30), (0.32, 0.075, 0.48), 3 if i != 1 else 7, face_materials)


def _build_experience(bm, face_materials):
    _cuboid(bm, (0.0, 0.0, 0.12), (1.38, 1.38, 0.12), 2, face_materials)
    _cylinder(bm, (0.0, 0.0, 1.38), 0.23, 2.45, 1, face_materials, vertices=8)
    for i, z in enumerate((0.72, 1.18, 1.64, 2.10)):
        x = -0.76 if i % 2 == 0 else 0.76
        _cuboid(bm, (x, 0.0, z), (0.58, 0.10, 0.12), 4, face_materials)
    _cuboid(bm, (0.0, 0.0, 2.70), (0.52, 0.52, 0.18), 4, face_materials)


def _build_skills(bm, face_materials):
    _cuboid(bm, (0.0, 0.0, 0.10), (1.25, 1.25, 0.10), 2, face_materials)
    _cylinder(bm, (0.0, 0.0, 1.42), 0.18, 2.58, 0, face_materials, vertices=8)
    levels = [(0.92, 0.0), (1.36, math.radians(60)), (1.80, math.radians(120)), (2.24, math.radians(180))]
    for z, a in levels:
        x = math.cos(a) * 0.70
        y = math.sin(a) * 0.70
        _cuboid(bm, (x, y, z), (0.30, 0.30, 0.22), 5, face_materials)
    _cuboid(bm, (0.0, 0.0, 2.82), (0.48, 0.48, 0.16), 5, face_materials)


def _build_contact(bm, face_materials):
    _cuboid(bm, (0.0, 0.0, 0.10), (1.55, 0.96, 0.10), 2, face_materials)
    _cuboid(bm, (0.0, 0.0, 1.04), (0.92, 0.18, 0.62), 6, face_materials)
    _cuboid(bm, (0.0, -0.02, 1.54), (0.98, 0.22, 0.08), 7, face_materials)
    _cuboid(bm, (-0.58, -0.03, 1.04), (0.08, 0.24, 0.40), 7, face_materials)
    _cylinder(bm, (1.10, 0.0, 1.58), 0.18, 0.14, 6, face_materials, vertices=12)


BUILDERS = {
    "projects": _build_projects,
    "experience": _build_experience,
    "skills": _build_skills,
    "contact": _build_contact,
}


def _build_marker_mesh(spec, mats):
    mesh_name = f"sectionMarkerMesh_{spec['key']}"
    old = bpy.data.meshes.get(mesh_name)
    if old is not None:
        bpy.data.meshes.remove(old)
    mesh = bpy.data.meshes.new(mesh_name)
    for mat in mats:
        mesh.materials.append(mat)

    bm = bmesh.new()
    face_materials = []
    BUILDERS[spec["key"]](bm, face_materials)
    bm.faces.index_update()
    slot_by_index = {face.index: slot for face, slot in zip(bm.faces, face_materials)}
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    for poly in mesh.polygons:
        poly.material_index = slot_by_index.get(poly.index, 0)
    return mesh


def _add_label(spec, x, z, ground, yaw, coll):
    obj = bpy.data.objects.get(f"sectionLabel_{spec['key']}") or bpy.data.objects.new(
        f"sectionLabel_{spec['key']}", bpy.data.curves.new(f"sectionLabelCurve_{spec['key']}", "FONT")
    )
    obj.data.body = spec["title"]
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.size = 0.34 if len(spec["title"]) > 7 else 0.42
    obj.data.extrude = 0.012
    obj.data.materials.clear()
    obj.data.materials.append(_material("marker_label"))
    obj.location = (x, z - 0.82, ground + 2.62)
    obj.rotation_mode = "XYZ"
    obj.rotation_euler = (math.radians(78.0), 0.0, yaw)
    obj.scale = (1.0, 1.0, 1.0)
    if obj.name not in {o.name for o in coll.objects}:
        coll.objects.link(obj)


def _add_ref(spec, x, z, ground, yaw):
    ref = bpy.data.objects.get(f"sectionRef_{spec['key']}") or bpy.data.objects.new(f"sectionRef_{spec['key']}", None)
    ref.empty_display_type = "PLAIN_AXES"
    ref.empty_display_size = 0.8
    ref.location = (x, z, ground + 1.5)
    ref.rotation_euler = (0.0, 0.0, yaw)
    ref["section"] = spec["key"]
    ref["title"] = spec["title"].title()
    _lib.place_in(REF_COLLECTION, ref)


def _add_footprint(spec, x, z, ground, yaw, material):
    hx, hy, hz = spec["footprint"][0] * 0.5, spec["footprint"][1] * 0.5, spec["footprint"][2] * 0.5
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(bm, uv, (0.0, 0.0, hz), (hx, hy, hz), "sand_gravel")
    mesh = bpy.data.meshes.get(f"sectionMarkerMesh_footprint_{spec['key']}") or bpy.data.meshes.new(
        f"sectionMarkerMesh_footprint_{spec['key']}"
    )
    mesh.clear_geometry()
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.clear()
    mesh.materials.append(material)
    obj = bpy.data.objects.get(f"sectionFootprint_{spec['key']}") or bpy.data.objects.new(f"sectionFootprint_{spec['key']}", mesh)
    obj.data = mesh
    obj.location = (x, z, ground)
    obj.rotation_mode = "XYZ"
    obj.rotation_euler = (0.0, 0.0, yaw)
    obj.display_type = "WIRE"
    obj.hide_render = True
    obj["section_marker_footprint"] = True
    obj["section"] = spec["key"]
    _lib.place_in(COLLIDER_COLLECTION, obj)


def run():
    print("[04-markers-section-landmarks] build four cardinal section markers")
    _clear_marker_objects()
    coll = _collection(MARKER_COLLECTION)
    mats = [
        _material("marker_dark_wood"),
        _material("marker_warm_wood"),
        _material("marker_stone"),
        _material("marker_projects"),
        _material("marker_experience"),
        _material("marker_skills"),
        _material("marker_contact"),
        _material("marker_label"),
    ]
    footprint_mat = _material("marker_footprint")

    built = 0
    for spec in MARKERS:
        x, z = spec["location"]
        ground = _height_at(x, z)
        if ground is None or ground < -0.05:
            print(f"  [skip] {spec['key']}: invalid terrain at ({x:.1f},{z:.1f}) height={ground}")
            continue
        mesh = _build_marker_mesh(spec, mats)
        obj = bpy.data.objects.get(f"sectionMarker_{spec['key']}") or bpy.data.objects.new(f"sectionMarker_{spec['key']}", mesh)
        obj.data = mesh
        obj.location = (x, z, ground)
        obj.rotation_mode = "XYZ"
        obj.rotation_euler = (0.0, 0.0, spec["yaw"])
        obj["section"] = spec["key"]
        obj["phase"] = "04c-section-markers"
        if obj.name not in {o.name for o in coll.objects}:
            coll.objects.link(obj)
        _add_label(spec, x, z, ground, spec["yaw"], coll)
        _add_ref(spec, x, z, ground, spec["yaw"])
        _add_footprint(spec, x, z, ground, spec["yaw"], footprint_mat)
        built += 1
        print(f"  {spec['key']}: ({x:.1f},{z:.1f},{ground:.3f})")

    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")
    print(f"  built {built}/4 section markers")


if __name__ == "__main__":
    run()
