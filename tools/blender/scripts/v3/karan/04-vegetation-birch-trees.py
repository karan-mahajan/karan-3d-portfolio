"""Author Karan's Phase 4 birch tree structure.

Bruno's birch setup uses body anchors and lets runtime foliage draw the leafy
clusters. This follows that idea but builds a Karan-specific birch frame:
pale forked bark, dark scars, upward branches, and refTreeLeaves_* anchors.

Run on the already-built karan world:
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/04-vegetation-birch-trees.py').read())
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
BIRCH_COLLECTION = "vegetation/birchTrees"
COLLIDER_COLLECTION = "colliders"
REF_COLLECTION = "refs"

BIRCHES = [
    {
        "key": "preview",
        "object": "tree_birch_karan_preview",
        "location": (31.50, -12.50),
        "yaw": math.radians(27),
        "scale": 1.0,
        "variant": 3,
    },
    {
        "key": "west_meadow",
        "object": "tree_birch_karan_west_meadow",
        "location": (-36.00, 6.00),
        "yaw": math.radians(-42),
        "scale": 0.92,
        "variant": 4,
    },
    {
        "key": "north_west_meadow",
        "object": "tree_birch_karan_north_west_meadow",
        "location": (-33.00, 27.00),
        "yaw": math.radians(118),
        "scale": 1.06,
        "variant": 5,
    },
    {
        "key": "north_ridge",
        "object": "tree_birch_karan_north_ridge",
        "location": (-20.50, 33.80),
        "yaw": math.radians(-156),
        "scale": 0.96,
        "variant": 6,
    },
    {
        "key": "north_inner_grass",
        "object": "tree_birch_karan_north_inner_grass",
        "location": (-11.50, 25.40),
        "yaw": math.radians(74),
        "scale": 0.88,
        "variant": 7,
    },
    {
        "key": "south_meadow",
        "object": "tree_birch_karan_south_meadow",
        "location": (7.80, -37.00),
        "yaw": math.radians(16),
        "scale": 1.10,
        "variant": 8,
    },
    {
        "key": "south_east_grass",
        "object": "tree_birch_karan_south_east_grass",
        "location": (21.80, -20.60),
        "yaw": math.radians(-96),
        "scale": 0.94,
        "variant": 9,
    },
    {
        "key": "east_grass",
        "object": "tree_birch_karan_east_grass",
        "location": (39.00, 2.50),
        "yaw": math.radians(143),
        "scale": 1.02,
        "variant": 10,
    },
    {
        "key": "north_east_grass",
        "object": "tree_birch_karan_north_east_grass",
        "location": (18.00, 24.00),
        "yaw": math.radians(-18),
        "scale": 0.90,
        "variant": 11,
    },
    {
        "key": "south_west_grass",
        "object": "tree_birch_karan_south_west_grass",
        "location": (-42.00, -22.00),
        "yaw": math.radians(205),
        "scale": 0.98,
        "variant": 12,
    },
    {
        "key": "far_south_grass",
        "object": "tree_birch_karan_far_south_grass",
        "location": (12.00, -41.00),
        "yaw": math.radians(-132),
        "scale": 1.04,
        "variant": 13,
    },
]

MAT_BARK = 0
MAT_SCAR = 1
MAT_BRANCH = 2
MAT_COLLIDER = 3

OBSTACLE_MARGIN = 1.6   # metres of clearance around section markers
# Section markers only — birches are hand-placed, so we avoid section
# footprints/totems but NOT bridges/rocks.
OBSTACLE_KEYS = ("sectionfootprint", "sectionmarker")
LAND_MIN = -0.05        # karan land plateau = 0.0; ponds/river carved below


def _height_at(x, z):
    terrain = bpy.data.objects.get("terrain") or bpy.data.objects.get("terrain_mesh")
    if terrain is None:
        return 0.02
    inv = terrain.matrix_world.inverted()
    origin = inv @ Vector((x, z, 50.0))
    direction = inv.to_3x3() @ Vector((0.0, 0.0, -1.0))
    hit, location, _normal, _idx = terrain.ray_cast(origin, direction)
    if not hit:
        return 0.02
    return (terrain.matrix_world @ location).z


def _obstacle_boxes():
    boxes = []
    for o in bpy.data.objects:
        if o.type != 'MESH':
            continue
        n = o.name.lower()
        if not any(k in n for k in OBSTACLE_KEYS):
            continue
        cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
        xs = [c.x for c in cs]; ys = [c.y for c in cs]
        boxes.append((min(xs) - OBSTACLE_MARGIN, max(xs) + OBSTACLE_MARGIN,
                      min(ys) - OBSTACLE_MARGIN, max(ys) + OBSTACLE_MARGIN))
    return boxes


def _inside_boxes(px, pz, boxes):
    return [b for b in boxes if b[0] <= px <= b[1] and b[2] <= pz <= b[3]]


def _resolve_specs(specs, boxes, label):
    """Hand-placed avoidance: nudge a spec outward from an offending marker box
    until it is clear AND on land; skip it (loud warning) if unclearable."""
    out = []
    for spec in specs:
        x, z = spec["location"]
        hits = _inside_boxes(x, z, boxes)
        if not hits:
            out.append(spec)
            continue
        bx = (hits[0][0] + hits[0][1]) * 0.5
        bz = (hits[0][2] + hits[0][3]) * 0.5
        dx, dz = x - bx, z - bz
        d = math.hypot(dx, dz) or 1.0
        ux, uz = dx / d, dz / d
        placed = None
        for step in range(1, 9):
            nx, nz = x + ux * step, z + uz * step
            h = _height_at(nx, nz)
            if h is not None and h >= LAND_MIN and not _inside_boxes(nx, nz, boxes):
                placed = (round(nx, 2), round(nz, 2))
                break
        if placed is None:
            print(f"  [SKIP] {label} {spec['key']!r} clips a section marker and cannot be nudged clear")
            continue
        print(f"  [NUDGE] {label} {spec['key']!r} {spec['location']} -> {placed}")
        out.append({**spec, "location": placed})
    return out


def _solid_material(name, color, roughness=0.84):
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
        _solid_material("birch_pale_bark_karan", (0.86, 0.84, 0.72, 1.0)),
        _solid_material("birch_dark_bark_scars_karan", (0.10, 0.075, 0.055, 1.0), 0.9),
        _solid_material("birch_warm_branch_karan", (0.24, 0.12, 0.055, 1.0), 0.86),
        _solid_material("birch_shadow_collider", (0.25, 0.28, 0.25, 1.0)),
    ]


def _mark_faces(verts, material_index):
    faces = set()
    for vert in verts:
        faces.update(vert.link_faces)
    for face in faces:
        face.material_index = material_index
    return faces


def _tapered_segment(bm, start, end, radius_a, radius_b, material_index, segments=10):
    start_v = Vector(start)
    end_v = Vector(end)
    axis = end_v - start_v
    length = axis.length
    if length <= 0.001:
        return end_v
    result = bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        segments=segments,
        radius1=radius_a,
        radius2=radius_b,
        depth=length,
    )
    quat = Vector((0.0, 0.0, 1.0)).rotation_difference(axis.normalized())
    midpoint = start_v + axis * 0.5
    for vert in result["verts"]:
        vert.co = quat @ vert.co
        vert.co += midpoint
    _mark_faces(result["verts"], material_index)
    return end_v


def _bezier(start, control, end, t):
    inv = 1.0 - t
    return start * (inv * inv) + control * (2.0 * inv * t) + end * (t * t)


def _curved_taper(bm, start, control, end, radius_a, radius_b, material_index, steps=6, segments=10):
    points = [_bezier(Vector(start), Vector(control), Vector(end), i / steps) for i in range(steps + 1)]
    for index, (a, b) in enumerate(zip(points, points[1:])):
        t0 = index / steps
        t1 = (index + 1) / steps
        r0 = radius_a + (radius_b - radius_a) * t0
        r1 = radius_a + (radius_b - radius_a) * t1
        _tapered_segment(bm, a, b, r0, r1, material_index, segments=segments)
    return points[-1]


def _scar(bm, center, yaw, width, height):
    cx, cy, cz = center
    half_w = width * 0.5
    half_d = 0.010
    half_h = height * 0.5
    c = math.cos(yaw)
    s = math.sin(yaw)
    right = Vector((c, s, 0.0))
    depth = Vector((-s, c, 0.0))
    up = Vector((0.0, 0.0, 1.0))
    base = Vector((cx, cy, cz))
    corners = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                corners.append(base + right * (sx * half_w) + depth * (sy * half_d) + up * (sz * half_h))
    verts = [bm.verts.new(tuple(corner)) for corner in corners]
    for idx in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
        face = bm.faces.new(tuple(verts[i] for i in idx))
        face.material_index = MAT_SCAR


def _trunk_point(height, lean, t):
    start = Vector((0.0, 0.0, 0.08))
    control = Vector((lean[1] * -0.18, lean[0] * 0.22, height * 0.54))
    end = Vector((lean[0], lean[1], height))
    return _bezier(start, control, end, t)


def _build_birch_mesh(spec):
    variant = spec.get("variant", 0)
    height = 3.38 + 0.28 * math.sin(variant * 0.71)
    lean = (0.24 * math.sin(variant * 0.77), -0.20 * math.cos(variant * 0.51))
    bm = bmesh.new()
    anchors = []

    trunk_points = [_trunk_point(height, lean, i / 7) for i in range(8)]
    for index, (start, end) in enumerate(zip(trunk_points, trunk_points[1:])):
        t0 = index / 7
        t1 = (index + 1) / 7
        r0 = 0.17 + (0.072 - 0.17) * t0
        r1 = 0.17 + (0.072 - 0.17) * t1
        _tapered_segment(bm, start, end, r0, r1, MAT_BARK, segments=12)

    sibling_side = -1 if variant % 2 else 1
    sibling_base = Vector((0.10 * sibling_side, -0.06, 0.18))
    sibling_control = Vector((0.22 * sibling_side, -0.16 + 0.04 * math.sin(variant), height * 0.46))
    sibling_tip = Vector((0.36 * sibling_side, -0.28 + 0.08 * math.cos(variant), height * (0.76 + 0.04 * (variant % 3))))
    _curved_taper(
        bm,
        sibling_base,
        sibling_control,
        sibling_tip,
        0.105 + 0.010 * (variant % 2),
        0.046,
        MAT_BARK,
        steps=5,
        segments=10,
    )

    scar_count = 5 + (variant % 3)
    for index in range(scar_count):
        z = 0.52 + index * (height * 0.62 / max(scar_count - 1, 1))
        t = z / height
        trunk_center = _trunk_point(height, lean, t)
        yaw = variant * 0.72 + index * 1.37
        outward = Vector((math.cos(yaw), math.sin(yaw), 0.0))
        center = trunk_center + outward * 0.15
        _scar(bm, center, yaw + math.pi * 0.5, 0.18 + 0.035 * (index % 2), 0.055)

    branch_count = 5 + (variant % 4)
    for index in range(branch_count):
        t = 0.40 + (index + 0.25) / branch_count * 0.42
        angle = variant * 0.61 + index * (math.tau / branch_count) + 0.22 * math.sin(variant + index * 1.4)
        length = 0.58 + 0.14 * ((variant + index) % 3) + 0.10 * math.cos(index * 1.7)
        lift = 0.34 + 0.07 * ((variant + index) % 4) + 0.06 * math.sin(variant * 0.4 + index)
        radius = 0.42 + 0.06 * ((variant + index) % 4)
        start = _trunk_point(height, lean, t)
        direction = Vector((math.cos(angle), math.sin(angle), 0.0))
        side = Vector((-direction.y, direction.x, 0.0))
        end = start + direction * length + Vector((0.0, 0.0, lift))
        control = (
            start
            + direction * (length * 0.45)
            + side * ((0.12 + 0.04 * (index % 3)) * (-1 if (variant + index) % 2 else 1))
            + Vector((0.0, 0.0, lift * 0.72))
        )
        tip = _curved_taper(
            bm,
            start,
            control,
            end,
            max(0.034, 0.064 - index * 0.004),
            0.024,
            MAT_BRANCH,
            steps=5,
            segments=8,
        )
        anchors.append((tuple(tip), radius))

        if (index + variant) % 3 == 0 or index == branch_count - 1:
            fork_angle = angle + (0.62 if index % 2 else -0.58)
            fork_dir = Vector((math.cos(fork_angle), math.sin(fork_angle), 0.0))
            fork_start = _bezier(start, control, end, 0.62)
            fork_end = fork_start + fork_dir * (length * 0.44) + Vector((0.0, 0.0, 0.28))
            fork_control = fork_start + fork_dir * (length * 0.24) + Vector((0.0, 0.0, 0.24))
            fork_tip = _curved_taper(bm, fork_start, fork_control, fork_end, 0.032, 0.018, MAT_BRANCH, steps=4, segments=7)
            anchors.append((tuple(fork_tip), radius * 0.72))

    anchors.append((tuple(sibling_tip + Vector((0.16, -0.05, 0.22))), 0.52))
    top = _trunk_point(height, lean, 1.0)
    anchors.append((tuple(top + Vector((0.04, 0.12, 0.28))), 0.60))

    face_materials = [face.material_index for face in bm.faces]
    return bm, {"height": height, "anchors": anchors}, face_materials


def _local_to_world(point, x, z, ground, yaw, scale):
    px, py, pz = point
    c = math.cos(yaw)
    s = math.sin(yaw)
    return (
        x + (px * c - py * s) * scale,
        z + (px * s + py * c) * scale,
        ground + pz * scale,
    )


def _remove_leaf_refs(object_name):
    prefix = f"refTreeLeaves_{object_name}_"
    for obj in list(bpy.data.objects):
        if obj.name.startswith(prefix):
            bpy.data.objects.remove(obj, do_unlink=True)


def _add_leaf_refs(spec, ground, anchors):
    x, z = spec["location"]
    yaw = spec.get("yaw", 0.0)
    scale = spec.get("scale", 1.0)
    _remove_leaf_refs(spec["object"])
    refs = []
    for index, (point, radius) in enumerate(anchors):
        ref = bpy.data.objects.get(f"refTreeLeaves_{spec['object']}_{index:02d}") or bpy.data.objects.new(
            f"refTreeLeaves_{spec['object']}_{index:02d}",
            None,
        )
        ref.empty_display_type = "PLAIN_AXES"
        ref.location = _local_to_world(point, x, z, ground, yaw, scale)
        ref.scale = (radius * scale, radius * scale, radius * scale)
        ref["species"] = "birch"
        ref["phase"] = "04-vegetation"
        _lib.place_in(REF_COLLECTION, ref)
        refs.append(ref)
    return refs


def _add_tree_ref(spec, ground, height):
    x, z = spec["location"]
    scale = spec.get("scale", 1.0)
    ref = bpy.data.objects.get(f"refBirchTree_{spec['key']}") or bpy.data.objects.new(f"refBirchTree_{spec['key']}", None)
    ref.empty_display_type = "PLAIN_AXES"
    ref.location = (x, z, ground + height * 0.70 * scale)
    ref.scale = (0.72 * scale, 0.72 * scale, 0.72 * scale)
    ref["phase"] = "04-vegetation"
    _lib.place_in(REF_COLLECTION, ref)
    return ref


def _build_collider(spec, ground, height, material):
    x, z = spec["location"]
    scale = spec.get("scale", 1.0)
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cylinder(
        bm,
        uv,
        (0.0, 0.0, height * 0.42 * scale),
        0.30 * scale,
        height * 0.84 * scale,
        "sand_gravel",
        segments=12,
    )
    obj = _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"tube_birch_tree_{spec['key']}_mesh",
        obj_name=f"tube_birch_tree_{spec['key']}",
        location=(x, z, ground),
        collection_name=COLLIDER_COLLECTION,
        material=material,
        hide=True,
    )
    obj.display_type = "WIRE"
    return obj


def _build_birch(spec, materials):
    x, z = spec["location"]
    scale = spec.get("scale", 1.0)
    ground = _height_at(x, z)
    bm, structure, face_materials = _build_birch_mesh(spec)
    obj = _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"{spec['object']}_mesh",
        obj_name=spec["object"],
        location=(x, z, ground),
        collection_name=BIRCH_COLLECTION,
        material=materials[MAT_BARK],
        rotation_euler=(0.0, 0.0, spec.get("yaw", 0.0)),
    )
    obj.scale = (scale, scale, scale)
    obj.data.materials.clear()
    for material in materials:
        obj.data.materials.append(material)
    if len(face_materials) == len(obj.data.polygons):
        for poly, material_index in zip(obj.data.polygons, face_materials):
            poly.material_index = material_index
    else:
        print(
            f"  [WARN] {obj.name}: face/material mismatch "
            f"({len(face_materials)} planned, {len(obj.data.polygons)} polygons)"
        )
    obj["phase"] = "04-vegetation"
    obj["variant"] = spec.get("variant", 0)

    collider = _build_collider(spec, ground, structure["height"], materials[MAT_COLLIDER])
    tree_ref = _add_tree_ref(spec, ground, structure["height"])
    leaf_refs = _add_leaf_refs(spec, ground, structure["anchors"])
    print(
        f"  {obj.name}: structure-only loc=({x:.2f}, {z:.2f}, {ground:.3f}) "
        f"yaw={math.degrees(spec.get('yaw', 0.0)):.1f}; "
        f"collider={collider.name}; ref={tree_ref.name}; leafRefs={len(leaf_refs)}"
    )
    return obj


def run():
    print("[04-vegetation-birch-trees] build Karan birch tree structure")
    materials = _materials()
    specs = _resolve_specs(BIRCHES, _obstacle_boxes(), "birch")
    built = [_build_birch(spec, materials) for spec in specs]
    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")
    print(f"  built {len(built)} birch tree structure(s)")


if __name__ == "__main__":
    run()
