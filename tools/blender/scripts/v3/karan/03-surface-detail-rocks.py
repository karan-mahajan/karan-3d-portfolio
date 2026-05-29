"""Place stylized basalt rocks on karan's island — tune-by-iteration.

Section-03 rocks delta. Generates low-poly rock clusters and links them into
the `basaltRocks` collection (child of scenery.002).

Five rocks use a rounded boulder-cluster silhouette; five use jagged volcanic
shards. Positions were checked against terrainWater so they stay off water.

Run additively on the open world (which already has the bridges):
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/03-surface-detail-rocks.py').read())
"""
import math

import bpy

TERRAIN_OBJECT = "terrain"
ROCKS_COLLECTION = "basaltRocks"
FOAM_COLLECTION = "shoreFoam"
CONTAINER_COLLECTION = "scenery.002"
BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"

# Distinct basalt colour (object-level override). Dark charcoal-grey so the
# columns read as volcanic rock against the sunset terrain. Tell me to change it.
ROCK_COLOR = (0.055, 0.055, 0.065, 1.0)   # near-black basalt grey
ROCK_MATERIAL = "rock"
FOAM_COLOR = (0.78, 0.96, 0.92, 0.62)
FOAM_MATERIAL = "shoreFoam"

# Scatter on dry land (world XYZ). Existing values are locked from Blender;
# new placements were checked against terrainWater with a 4m footprint.
ROCKS = [
    {"name": "rock01", "style": "boulder", "location": (-14.231287002563477, -17.561372756958008, -0.00006103515625), "yaw_deg": 19.99999941818584, "scale": 1.0},
    {"name": "rock02", "style": "boulder", "location": (-28.0, 20.0, 0.00006103515625), "yaw_deg": 74.99999867197056, "scale": 0.8500000238418579},
    {"name": "rock03", "style": "boulder", "location": (-1.944184192353163, -13.812934731225955, -0.00030517578125), "yaw_deg": 130.00000134084985, "scale": 1.100000023841858},
    {"name": "rock04", "style": "boulder", "location": (-3.6853944108749044, 1.294518899959649, 0.0), "yaw_deg": 205.0000000128204, "scale": 0.8999999761581421},
    {"name": "rock05", "style": "boulder", "location": (12.995860900207745, 22.93405558080794, 0.0001220703125), "yaw_deg": 299.99999468788224, "scale": 1.0},
    {"name": "rock06", "style": "shard", "location": (-38.0, 8.0, -0.211181640625), "yaw_deg": 35.0, "scale": 0.75},
    {"name": "rock07", "style": "shard", "location": (-8.0, 31.0, 0.0), "yaw_deg": 165.0, "scale": 0.7},
    {"name": "rock08", "style": "shard", "location": (-6.0, -34.0, 0.0), "yaw_deg": 250.0, "scale": 0.8},
    {"name": "rock09", "style": "shard", "location": (32.0, 11.0, -0.00006103515625), "yaw_deg": 325.0, "scale": 0.9},
    {"name": "rock10", "style": "shard", "location": (43.0, -10.0, -0.0001220703125), "yaw_deg": 95.0, "scale": 0.85},
]

# Clustered outer-coast rocks. Each anchor is the first coast edge found by
# scanning from ocean toward land. Rocks are offset toward the water side so
# they fill the pale shoreline band after the grass instead of sitting on grass.
SHORE_CLUSTERS = [
    ("W", (-52.5, 36.0, -0.03656005859375), 4),
    ("W", (-53.0, 28.0, -0.0928955078125), 3),
    ("W", (-52.0, 20.0, -0.05511474609375), 3),
    ("W", (-50.0, 12.0, -0.00567626953125), 4),
    ("W", (-48.5, 2.0, -0.07244873046875), 3),
    ("W", (-51.5, -10.0, -0.50054931640625), 4),
    ("W", (-53.0, -22.0, -0.25469970703125), 3),
    ("W", (-54.0, -34.0, -0.35601806640625), 4),
    ("S", (-46.0, -47.0, -0.00323486328125), 4),
    ("S", (-36.0, -47.5, -0.08489990234375), 3),
    ("S", (-26.0, -52.0, -0.13690185546875), 4),
    ("S", (-16.0, -51.0, -0.15264892578125), 3),
    ("S", (-6.0, -46.0, -0.03033447265625), 4),
    ("S", (6.0, -51.0, -0.20904541015625), 3),
    ("S", (18.0, -54.5, -0.49371337890625), 4),
    ("S", (30.0, -53.0, -0.03643798828125), 3),
    ("S", (42.0, -43.0, 0.00006103515625), 4),
    ("E", (49.5, -12.0, -0.063232421875), 4),
    ("E", (51.0, 16.0, -0.19744873046875), 3),
    ("E", (50.0, 40.0, -0.0186767578125), 4),
    ("N", (-44.0, 50.0, -0.7315673828125), 3),
    ("N", (-32.0, 52.0, -0.5072021484375), 4),
    ("N", (-18.0, 51.5, -0.17535400390625), 3),
    ("N", (-4.0, 46.0, -0.1588134765625), 4),
    ("N", (12.0, 51.5, -0.4310302734375), 3),
    ("N", (28.0, 54.0, -0.22607421875), 4),
    ("N", (42.0, 53.0, -0.58721923828125), 3),
]


def _expand_shore_rocks():
    directions = {
        "W": {"normal": (-1.0, 0.0), "tangent": (0.0, 1.0), "yaw": 90.0},
        "E": {"normal": (1.0, 0.0), "tangent": (0.0, 1.0), "yaw": 270.0},
        "S": {"normal": (0.0, -1.0), "tangent": (1.0, 0.0), "yaw": 0.0},
        "N": {"normal": (0.0, 1.0), "tangent": (1.0, 0.0), "yaw": 180.0},
    }
    layout = (
        (-2.55, 0.38, 0.30),
        (-1.78, 0.92, 0.40),
        (-0.98, 1.42, 0.32),
        (-0.18, 0.62, 0.46),
        (0.58, 1.12, 0.34),
        (1.34, 1.72, 0.28),
        (2.08, 0.72, 0.38),
        (2.82, 1.36, 0.26),
    )
    rocks = []
    index = 1
    for side, (x, y, z), _count in SHORE_CLUSTERS:
        data = directions[side]
        nx, ny = data["normal"]
        tx, ty = data["tangent"]
        for i, (tangent_offset, normal_offset, size) in enumerate(layout):
            loc = (
                x + tx * tangent_offset + nx * normal_offset,
                y + ty * tangent_offset + ny * normal_offset,
                z - 0.10,
            )
            rocks.append({
                "name": f"shoreRock{index:02d}",
                "location": loc,
                "yaw_deg": data["yaw"] + i * 19.0,
                "scale": (size, size * 0.82, size * 0.54),
                "foam": i == 3,
            })
            index += 1
    return rocks


SHORE_ROCKS = _expand_shore_rocks()


def _faceted_mesh(name, verts, faces):
    mesh = bpy.data.meshes.get(name) or bpy.data.meshes.new(name)
    mesh.clear_geometry()
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    for poly in mesh.polygons:
        poly.use_smooth = False
    return mesh


def _add_lowpoly_boulder(verts, faces, center, radius, seed):
    cx, cy = center
    rx, ry, rz = radius
    segs = 8
    start = len(verts)
    rings = (
        (0.00, 0.64, 0.58, 0.00),
        (0.22, 0.98, 0.90, 0.18),
        (0.58, 1.00, 0.82, 0.40),
        (0.90, 0.66, 0.56, 0.12),
        (1.18, 0.22, 0.18, 0.45),
    )
    for i, (zmul, xmul, ymul, offset) in enumerate(rings):
        for j in range(segs):
            a = math.tau * j / segs + offset + seed * 0.11
            wobble = 1.0 + 0.14 * math.sin(seed * 1.7 + i * 1.3 + j * 2.1)
            verts.append((
                cx + math.cos(a) * rx * xmul * wobble,
                cy + math.sin(a) * ry * ymul * (1.0 + 0.12 * math.cos(seed + j)),
                max(0.0, rz * zmul * (1.0 + 0.04 * math.sin(seed + j * 0.9))),
            ))
    faces.append(tuple(range(start + segs - 1, start - 1, -1)))
    for i in range(len(rings) - 1):
        for j in range(segs):
            a = start + i * segs + j
            b = start + i * segs + (j + 1) % segs
            c = start + (i + 1) * segs + (j + 1) % segs
            d = start + (i + 1) * segs + j
            faces.append((a, b, c, d))
    top = start + (len(rings) - 1) * segs
    faces.append(tuple(range(top, top + segs)))


def _build_boulder_mesh(name):
    verts = []
    faces = []
    for i, (center, radius) in enumerate((
        ((-1.05, -0.15), (1.05, 0.88, 2.15)),
        ((0.52, 0.10), (1.28, 1.04, 3.15)),
        ((1.62, -0.24), (0.82, 0.70, 1.72)),
        ((-1.82, -0.78), (0.48, 0.42, 0.92)),
        ((0.00, -1.08), (0.86, 0.68, 1.18)),
        ((1.98, -0.88), (0.48, 0.40, 0.78)),
        ((-0.72, -1.02), (0.54, 0.42, 0.88)),
    )):
        _add_lowpoly_boulder(verts, faces, center, radius, i + 1)
    return _faceted_mesh(name, verts, faces)


def _add_shard(verts, faces, center, radius, height, lean, seed):
    cx, cy = center
    sides = 6
    base = len(verts)
    rings = (
        (0.00, 1.00, 1.00, 0.00),
        (0.42, 0.74, 0.62, 0.12),
        (0.78, 0.38, 0.32, 0.28),
        (1.00, 0.12, 0.08, 0.36),
    )
    for i, (zmul, xmul, ymul, offset) in enumerate(rings):
        for j in range(sides):
            a = math.tau * j / sides + seed * 0.37 + offset
            wobble = 1.0 + 0.18 * math.sin(seed + i * 1.4 + j * 1.9)
            lx = lean[0] * zmul
            ly = lean[1] * zmul
            verts.append((
                cx + lx + math.cos(a) * radius[0] * xmul * wobble,
                cy + ly + math.sin(a) * radius[1] * ymul * wobble,
                height * zmul,
            ))
    faces.append(tuple(range(base + sides - 1, base - 1, -1)))
    for i in range(len(rings) - 1):
        for j in range(sides):
            a = base + i * sides + j
            b = base + i * sides + (j + 1) % sides
            c = base + (i + 1) * sides + (j + 1) % sides
            d = base + (i + 1) * sides + j
            faces.append((a, b, c, d))
    top = base + (len(rings) - 1) * sides
    faces.append(tuple(range(top, top + sides)))


def _build_shard_mesh(name):
    verts = []
    faces = []
    shards = (
        ((0.00, 0.00), (0.92, 0.70), 5.4, (0.42, 0.18)),
        ((-0.68, -0.12), (0.66, 0.54), 4.2, (-0.34, 0.28)),
        ((0.72, -0.22), (0.58, 0.48), 3.7, (0.32, -0.05)),
        ((-1.14, -0.52), (0.42, 0.34), 2.4, (-0.18, 0.14)),
        ((1.20, -0.62), (0.38, 0.30), 2.2, (0.16, 0.04)),
        ((0.12, -0.82), (0.44, 0.36), 3.0, (0.02, -0.20)),
        ((-0.20, 0.45), (0.42, 0.34), 3.4, (-0.12, 0.16)),
    )
    for i, shard in enumerate(shards):
        _add_shard(verts, faces, *shard, seed=i + 3)
    return _faceted_mesh(name, verts, faces)


def _rock_mesh(style):
    if style == "boulder":
        return _build_boulder_mesh("rockStyle_boulderCluster")
    if style == "shard":
        return _build_shard_mesh("rockStyle_volcanicShards")
    raise ValueError(f"Unknown rock style: {style}")


def _build_foam_mesh(name):
    mesh = bpy.data.meshes.get(name) or bpy.data.meshes.new(name)
    mesh.clear_geometry()
    verts = []
    faces = []
    outer_x, outer_y = 1.65, 0.70
    inner_x, inner_y = 1.18, 0.46
    segments = 22
    start_angle = math.radians(22)
    end_angle = math.radians(338)
    for i in range(segments + 1):
        t = start_angle + (end_angle - start_angle) * i / segments
        wobble = 1.0 + 0.06 * math.sin(i * 1.7)
        verts.append((math.cos(t) * outer_x * wobble, math.sin(t) * outer_y * wobble, 0.0))
        verts.append((math.cos(t) * inner_x, math.sin(t) * inner_y, 0.0))
    for i in range(segments):
        a = i * 2
        faces.append((a, a + 1, a + 3, a + 2))
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return mesh


def _apply_foam_material(ob):
    mat = bpy.data.materials.get(FOAM_MATERIAL) or bpy.data.materials.new(FOAM_MATERIAL)
    if not getattr(mat, "node_tree", None):
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF") if mat.node_tree else None
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = FOAM_COLOR
        bsdf.inputs["Alpha"].default_value = FOAM_COLOR[3]
    mat.diffuse_color = FOAM_COLOR
    mat.use_nodes = True
    mat.blend_method = "BLEND"
    mat.show_transparent_back = True
    if not ob.material_slots:
        ob.data.materials.append(mat)
    for slot in ob.material_slots:
        slot.link = "OBJECT"
        slot.material = mat


def _apply_rock_color(ob):
    """Object-level override so only these rocks recolour; shared mesh/palette stay Bruno's."""
    mat = bpy.data.materials.get(ROCK_MATERIAL)
    if mat is None:
        mat = bpy.data.materials.new(ROCK_MATERIAL)
    if not getattr(mat, "node_tree", None):
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF") if mat.node_tree else None
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = ROCK_COLOR
    mat.diffuse_color = ROCK_COLOR
    if not ob.material_slots:
        ob.data.materials.append(mat)
    for slot in ob.material_slots:
        slot.link = "OBJECT"
        slot.material = mat


def _place_rock(coll, spec):
    mesh = _rock_mesh(spec["style"])
    ob = bpy.data.objects.get(spec["name"])
    if ob is None:
        ob = bpy.data.objects.new(spec["name"], mesh)
    ob.location = spec["location"]
    ob.rotation_mode = "XYZ"
    ob.rotation_euler = (0.0, 0.0, math.radians(spec["yaw_deg"]))
    s = spec["scale"]
    ob.scale = s if isinstance(s, tuple) else (s, s, s)
    ob.data = mesh
    try:
        ob.display_type = "TEXTURED"
    except Exception:
        pass
    if ob.name not in {o.name for o in coll.objects}:
        try:
            coll.objects.link(ob)
        except Exception:
            pass
    _apply_rock_color(ob)
    print(f"  placed {ob.name!r} ({spec['style']}) at {tuple(round(v, 2) for v in ob.location)} "
          f"yaw {spec['yaw_deg']:.0f} scale {s}")


def _place_foam(coll, rock_spec, index):
    mesh = _build_foam_mesh("shoreFoam_crescent")
    name = f"shoreFoam{index:02d}"
    ob = bpy.data.objects.get(name) or bpy.data.objects.new(name, mesh)
    x, y, _ = rock_spec["location"]
    ob.location = (x, y, 0.028)
    ob.rotation_mode = "XYZ"
    ob.rotation_euler = (0.0, 0.0, math.radians(rock_spec["yaw_deg"] + 18.0))
    sx, sy, _ = rock_spec["scale"]
    ob.scale = (max(0.55, sx * 2.1), max(0.36, sy * 2.0), 1.0)
    ob.data = mesh
    try:
        ob.display_type = "TEXTURED"
    except Exception:
        pass
    if ob.name not in {o.name for o in coll.objects}:
        try:
            coll.objects.link(ob)
        except Exception:
            pass
    _apply_foam_material(ob)
    print(f"  placed {name!r} at {tuple(round(v, 2) for v in ob.location)}")


def _remove_obsolete(prefix, keep_names):
    for ob in list(bpy.data.objects):
        if ob.name.startswith(prefix) and ob.name not in keep_names:
            bpy.data.objects.remove(ob, do_unlink=True)


def run():
    print("[03-surface-detail-rocks] place basalt rocks on karan's island")

    container = bpy.data.collections.get(CONTAINER_COLLECTION)
    if container and container.name not in {c.name for c in bpy.context.scene.collection.children}:
        try:
            bpy.context.scene.collection.children.link(container)
        except Exception:
            pass
    coll = bpy.data.collections.get(ROCKS_COLLECTION) or bpy.data.collections.new(ROCKS_COLLECTION)
    foam_coll = bpy.data.collections.get(FOAM_COLLECTION) or bpy.data.collections.new(FOAM_COLLECTION)
    if container and foam_coll.name not in {c.name for c in container.children}:
        try:
            container.children.link(foam_coll)
        except Exception:
            pass

    shore_names = {spec["name"] for spec in SHORE_ROCKS}
    foam_names = {
        f"shoreFoam{i:02d}"
        for i, spec in enumerate((s for s in SHORE_ROCKS if s.get("foam")), start=1)
    }
    _remove_obsolete("shoreRock", shore_names)
    _remove_obsolete("shoreFoam", foam_names)

    for spec in ROCKS:
        _place_rock(coll, spec)
    for spec in SHORE_ROCKS:
        _place_rock(coll, {**spec, "style": "boulder"})

    foam_index = 1
    for spec in SHORE_ROCKS:
        if spec.get("foam"):
            _place_foam(foam_coll, spec, foam_index)
            foam_index += 1

    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")


if __name__ == "__main__":
    run()
