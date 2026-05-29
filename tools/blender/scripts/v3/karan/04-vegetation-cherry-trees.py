"""Author Karan's Phase 4 cherry tree structures.

Bruno's cherry setup is split in two: `036` creates the collection and `135`
places 20 flat `Plane.023` tree body anchors. This keeps Bruno's approach:
Blender owns only woody structure plus leaf-anchor refs; runtime foliage adds
leaf clusters to those refs later.

The structures themselves are Karan-specific: curved trunks, asymmetric branch
fans, and per-tree leaf refs so the runtime blossoms do not repeat as clones.

Run on the already-built karan world:
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/04-vegetation-cherry-trees.py').read())
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
CHERRY_COLLECTION = "vegetation/cherryTrees"
COLLIDER_COLLECTION = "colliders"
REF_COLLECTION = "refs"

CHERRIES = [
    {
        "key": "preview",
        "object": "cherry_tree_preview",
        "location": (11.36, 3.69),
        "yaw": math.radians(18),
        "scale": 1.0,
        "variant": 0,
    },
    {
        "key": "bonfire_central_east",
        "object": "cherry_tree_bonfire_central_east",
        "location": (15.80, -22.80),
        "yaw": math.radians(-26),
        "scale": 0.92,
        "variant": 1,
    },
    {
        "key": "bonfire_central_west",
        "object": "cherry_tree_bonfire_central_west",
        "location": (10.10, -22.70),
        "yaw": math.radians(42),
        "scale": 1.06,
        "variant": 2,
    },
    {
        "key": "bonfire_slab01_north",
        "object": "cherry_tree_bonfire_slab01_north",
        "location": (21.00, 2.90),
        "yaw": math.radians(112),
        "scale": 0.96,
        "variant": 3,
    },
    {
        "key": "bonfire_slab02_west",
        "object": "cherry_tree_bonfire_slab02_west",
        "location": (-21.90, -4.70),
        "yaw": math.radians(-68),
        "scale": 0.88,
        "variant": 4,
    },
    {
        "key": "bonfire_slab03_west",
        "object": "cherry_tree_bonfire_slab03_west",
        "location": (-5.70, 18.40),
        "yaw": math.radians(154),
        "scale": 1.02,
        "variant": 5,
    },
    {
        "key": "bonfire_slab03_east",
        "object": "cherry_tree_bonfire_slab03_east",
        "location": (0.80, 19.10),
        "yaw": math.radians(-140),
        "scale": 0.91,
        "variant": 6,
    },
    {
        "key": "bridge01_north_west",
        "object": "cherry_tree_bridge01_north_west",
        "location": (-4.80, 12.10),
        "yaw": math.radians(68),
        "scale": 0.86,
        "variant": 7,
    },
    {
        "key": "bridge01_north_east",
        "object": "cherry_tree_bridge01_north_east",
        "location": (5.90, 11.80),
        "yaw": math.radians(-32),
        "scale": 1.08,
        "variant": 8,
    },
    {
        "key": "bridge01_south_west",
        "object": "cherry_tree_bridge01_south_west",
        "location": (-5.50, -0.60),
        "yaw": math.radians(205),
        "scale": 0.98,
        "variant": 9,
    },
    {
        "key": "bridge02_south_west",
        "object": "cherry_tree_bridge02_south_west",
        "location": (29.70, 12.90),
        "yaw": math.radians(-92),
        "scale": 0.94,
        "variant": 10,
    },
    {
        "key": "meadow_south",
        "object": "cherry_tree_meadow_south",
        "location": (6.60, -35.20),
        "yaw": math.radians(12),
        "scale": 1.12,
        "variant": 11,
    },
    {
        "key": "meadow_north_west",
        "object": "cherry_tree_meadow_north_west",
        "location": (-30.00, 31.50),
        "yaw": math.radians(-118),
        "scale": 1.04,
        "variant": 12,
    },
    {
        "key": "meadow_east",
        "object": "cherry_tree_meadow_east",
        "location": (36.00, -8.50),
        "yaw": math.radians(82),
        "scale": 0.90,
        "variant": 13,
    },
    {
        "key": "meadow_south_east_path",
        "object": "cherry_tree_meadow_south_east_path",
        "location": (24.00, -36.00),
        "yaw": math.radians(-162),
        "scale": 0.95,
        "variant": 14,
    },
    {
        "key": "meadow_west",
        "object": "cherry_tree_meadow_west",
        "location": (-37.00, 8.00),
        "yaw": math.radians(138),
        "scale": 1.00,
        "variant": 15,
    },
]

MAT_TRUNK = 0
MAT_TIP = 1
MAT_COLLIDER = 2


def _height_at(x, z):
    terrain = bpy.data.objects.get("terrain") or bpy.data.objects.get("terrain_mesh")
    if terrain is None:
        return 0.02
    inv = terrain.matrix_world.inverted()
    origin = inv @ Vector((x, z, 50.0))
    direction = inv.to_3x3() @ Vector((0.0, 0.0, -1.0))
    success, location, _normal, _idx = terrain.ray_cast(origin, direction)
    if not success:
        return 0.02
    return (terrain.matrix_world @ location).z


def _solid_material(name, color, roughness=0.82):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
    return mat


def _materials():
    return [
        _solid_material("cherry_trunk_dark_brown", (0.24, 0.12, 0.055, 1.0)),
        _solid_material("cherry_branch_tip_marker", (0.32, 0.16, 0.075, 1.0), 0.88),
        _solid_material("cherry_shadow_collider", (0.25, 0.28, 0.25, 1.0)),
    ]


def _cylinder(bm, uv, center, radius, height, material_index, face_materials, segments=10):
    faces = _lib.bm_add_cylinder(bm, uv, center, radius, height, "sand_gravel", segments=segments)
    face_materials.extend([material_index] * len(faces))
    return faces


def _branch_box(bm, uv, start, end, thickness, material_index, face_materials):
    start_v = Vector(start)
    end_v = Vector(end)
    axis = end_v - start_v
    length = axis.length
    if length <= 0.001:
        return []
    u = axis.normalized()
    helper = Vector((0.0, 0.0, 1.0))
    if abs(u.dot(helper)) > 0.92:
        helper = Vector((0.0, 1.0, 0.0))
    v = u.cross(helper).normalized()
    w = v.cross(u).normalized()
    center = (start_v + end_v) * 0.5
    hx = length * 0.5
    hy = thickness
    hz = thickness

    corners = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                corners.append(center + u * (sx * hx) + v * (sy * hy) + w * (sz * hz))
    verts = [bm.verts.new(tuple(c)) for c in corners]
    faces_idx = [
        (0, 1, 3, 2),
        (4, 6, 7, 5),
        (0, 4, 5, 1),
        (2, 3, 7, 6),
        (0, 2, 6, 4),
        (1, 5, 7, 3),
    ]
    faces = []
    for idx in faces_idx:
        face = bm.faces.new(tuple(verts[i] for i in idx))
        _lib.paint_face(face, uv, "sand_gravel")
        faces.append(face)
    face_materials.extend([material_index] * len(faces))
    return faces


def _bezier(start, control, end, t):
    inv = 1.0 - t
    return start * (inv * inv) + control * (2.0 * inv * t) + end * (t * t)


def _curve_points(start, control, end, segments):
    return [_bezier(start, control, end, i / segments) for i in range(segments + 1)]


def _curved_branch(bm, uv, start, control, end, radius_a, radius_b, material_index, face_materials, segments=5):
    points = _curve_points(Vector(start), Vector(control), Vector(end), segments)
    for index, (a, b) in enumerate(zip(points, points[1:])):
        t = index / max(segments - 1, 1)
        thickness = radius_a + (radius_b - radius_a) * t
        _branch_box(bm, uv, a, b, thickness, material_index, face_materials)


def _trunk_point(height, lean, t):
    end = Vector((lean[0], lean[1], height))
    control = Vector((lean[1] * -0.34, lean[0] * 0.30, height * 0.56))
    return _bezier(Vector((0.0, 0.0, 0.18)), control, end, t)


def _generate_structure(variant):
    height = 3.08 + 0.22 * math.sin(variant * 1.13)
    lean = (
        0.26 * math.sin(variant * 0.73 + 0.25),
        0.22 * math.cos(variant * 0.91 + 0.55),
    )
    branch_count = 5 + (variant % 4)
    twist = variant * 0.43
    anchors = []
    branches = []

    for index in range(branch_count):
        raw_t = 0.38 + (index + 0.5) / branch_count * 0.48
        t = max(0.36, min(0.88, raw_t + 0.035 * math.sin(variant + index * 1.7)))
        start = _trunk_point(height, lean, t)
        angle = twist + index * (math.tau / branch_count) + 0.26 * math.sin(variant * 0.6 + index)
        length = 0.68 + 0.18 * ((variant + index) % 3) + 0.10 * math.sin(index * 2.1)
        lift = 0.36 + 0.10 * ((variant + index) % 2) + 0.08 * math.cos(variant + index)
        direction = Vector((math.cos(angle), math.sin(angle), 0.0))
        side = Vector((-direction.y, direction.x, 0.0))
        end = start + direction * length + Vector((0.0, 0.0, lift))
        bend = (0.18 + 0.04 * ((variant + index) % 3)) * (-1 if (variant + index) % 2 else 1)
        control = start + direction * (length * 0.48) + side * bend + Vector((0.0, 0.0, lift * 0.62))
        radius_a = 0.078 - min(index, 5) * 0.005
        radius_b = 0.038 - min(index, 5) * 0.002
        branches.append((start, control, end, radius_a, radius_b, 5))
        anchors.append((tuple(end), 0.56 + 0.10 * ((variant + index) % 4)))

        if index % 2 == variant % 2 or index == branch_count - 1:
            fork_angle = angle + (0.55 if index % 2 else -0.50)
            fork_dir = Vector((math.cos(fork_angle), math.sin(fork_angle), 0.0))
            fork_start = _bezier(start, control, end, 0.70)
            fork_len = length * (0.44 + 0.05 * ((variant + index) % 2))
            fork_end = fork_start + fork_dir * fork_len + Vector((0.0, 0.0, 0.28 + 0.05 * math.sin(index)))
            fork_control = fork_start + fork_dir * (fork_len * 0.52) + side * (-bend * 0.45) + Vector((0.0, 0.0, 0.24))
            branches.append((fork_start, fork_control, fork_end, radius_b * 0.88, radius_b * 0.55, 4))
            anchors.append((tuple(fork_end), 0.42 + 0.06 * ((variant + index) % 3)))

    top = _trunk_point(height, lean, 1.0)
    crown_end = top + Vector((0.16 * math.cos(twist), 0.16 * math.sin(twist), 0.42))
    branches.append((top * 0.92 + Vector((0.0, 0.0, 0.18)), top + Vector((0.08, -0.05, 0.24)), crown_end, 0.062, 0.030, 4))
    anchors.append((tuple(crown_end), 0.68))

    return {
        "height": height,
        "lean": lean,
        "branches": branches,
        "anchors": anchors,
    }


def _build_tree_mesh(spec):
    structure = _generate_structure(spec.get("variant", 0))
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    face_materials = []

    height = structure["height"]
    lean = structure["lean"]
    trunk_points = _curve_points(
        Vector((0.0, 0.0, 0.18)),
        Vector((lean[1] * -0.34, lean[0] * 0.30, height * 0.56)),
        Vector((lean[0], lean[1], height)),
        6,
    )
    for index, (start, end) in enumerate(zip(trunk_points, trunk_points[1:])):
        t = index / max(len(trunk_points) - 2, 1)
        _branch_box(
            bm,
            uv,
            start,
            end,
            0.155 + (0.074 - 0.155) * t,
            MAT_TRUNK,
            face_materials,
        )
    _cylinder(bm, uv, (0.0, 0.0, 0.16), 0.28, 0.18, MAT_TRUNK, face_materials, segments=12)

    for start, control, end, radius_a, radius_b, segments in structure["branches"]:
        _curved_branch(bm, uv, start, control, end, radius_a, radius_b, MAT_TRUNK, face_materials, segments)

    # Tiny woody endpoint markers. They are not leaves; matching
    # refTreeLeaves_* empties below drive runtime leaf clusters.
    for point, radius in structure["anchors"]:
        _cylinder(bm, uv, point, radius * 0.10, radius * 0.10, MAT_TIP, face_materials, segments=8)

    return bm, face_materials, structure


def _build_collider(key, x, z, ground, scale, material, structure):
    height = structure["height"]
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cylinder(
        bm,
        uv,
        (0.0, 0.0, (height * 0.44) * scale),
        0.30 * scale,
        (height * 0.88) * scale,
        "sand_gravel",
        segments=12,
    )
    obj = _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"tube_cherry_tree_{key}_mesh",
        obj_name=f"tube_cherry_tree_{key}",
        location=(x, z, ground),
        collection_name=COLLIDER_COLLECTION,
        material=material,
        hide=True,
    )
    obj.display_type = "WIRE"
    return obj


def _local_to_world(point, x, z, ground, yaw, scale):
    px, py, pz = point
    c = math.cos(yaw)
    s = math.sin(yaw)
    return (
        x + (px * c - py * s) * scale,
        z + (px * s + py * c) * scale,
        ground + pz * scale,
    )


def _add_ref(key, x, z, ground, scale, structure):
    ref = bpy.data.objects.get(f"refCherryTree_{key}") or bpy.data.objects.new(f"refCherryTree_{key}", None)
    ref.empty_display_type = "PLAIN_AXES"
    ref.location = (x, z, ground + structure["height"] * 0.74 * scale)
    ref.scale = (0.75 * scale, 0.75 * scale, 0.75 * scale)
    ref["phase"] = "04-vegetation"
    _lib.place_in(REF_COLLECTION, ref)
    return ref


def _remove_leaf_refs(object_name):
    prefix = f"refTreeLeaves_{object_name}_"
    for obj in list(bpy.data.objects):
        if obj.name.startswith(prefix):
            bpy.data.objects.remove(obj, do_unlink=True)


def _add_leaf_refs(spec, ground, anchors):
    x, z = spec["location"]
    scale = spec.get("scale", 1.0)
    yaw = spec.get("yaw", 0.0)
    _remove_leaf_refs(spec["object"])
    refs = []
    for index, (point, radius) in enumerate(anchors):
        name = f"refTreeLeaves_{spec['object']}_{index:02d}"
        ref = bpy.data.objects.get(name) or bpy.data.objects.new(name, None)
        ref.empty_display_type = "PLAIN_AXES"
        ref.location = _local_to_world(point, x, z, ground, yaw, scale)
        ref.scale = (radius * scale, radius * scale, radius * scale)
        ref["species"] = "cherry"
        ref["phase"] = "04-vegetation"
        _lib.place_in(REF_COLLECTION, ref)
        refs.append(ref)
    return refs


def _build_tree(spec, materials):
    x, z = spec["location"]
    scale = spec.get("scale", 1.0)
    ground = _height_at(x, z)
    bm, face_materials, structure = _build_tree_mesh(spec)
    obj = _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"{spec['object']}_mesh",
        obj_name=spec["object"],
        location=(x, z, ground),
        collection_name=CHERRY_COLLECTION,
        material=materials[0],
        rotation_euler=(0.0, 0.0, spec.get("yaw", 0.0)),
    )
    obj.scale = (scale, scale, scale)
    obj.data.materials.clear()
    for material in materials:
        obj.data.materials.append(material)
    if len(face_materials) == len(obj.data.polygons):
        for poly, mat_index in zip(obj.data.polygons, face_materials):
            poly.material_index = mat_index
    else:
        print(
            f"  [WARN] {obj.name}: face/material mismatch "
            f"({len(face_materials)} planned, {len(obj.data.polygons)} polygons)"
        )
    obj["phase"] = "04-vegetation"
    obj["variant"] = spec.get("variant", 0)

    collider = _build_collider(spec["key"], x, z, ground, scale, materials[MAT_COLLIDER], structure)
    ref = _add_ref(spec["key"], x, z, ground, scale, structure)
    leaf_refs = _add_leaf_refs(spec, ground, structure["anchors"])
    print(
        f"  {obj.name}: structure-only loc=({x:.2f}, {z:.2f}, {ground:.3f}) "
        f"yaw={math.degrees(spec.get('yaw', 0.0)):.1f} variant={spec.get('variant', 0)}; "
        f"collider={collider.name}; ref={ref.name}; leafRefs={len(leaf_refs)}"
    )
    return obj


def run():
    print("[04-vegetation-cherry-trees] build Karan cherry tree structures")
    materials = _materials()
    built = [_build_tree(spec, materials) for spec in CHERRIES]
    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")
    print(f"  built {len(built)} cherry tree structure(s)")


if __name__ == "__main__":
    run()
