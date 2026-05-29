"""Place stylized basalt rocks on karan's island — locked to hand placement.

Section-03 rocks delta. Generates two low-poly rock meshes (a rounded
boulder-cluster and jagged volcanic shards) and places every stone at the exact
transform captured from the hand-placed blend, read from
`resources/shore_stones.json` (10 inland rock* + 195 shoreRock* along the
shore). This is the read-back-and-lock source of truth: edit the stones in
Blender, re-capture the JSON, and a re-run reproduces them perfectly.

The earlier procedural shore-scan helpers are kept for reference but no longer
called — placement comes entirely from the JSON.

Run additively on the open world (which already has the bridges):
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/03-surface-detail-rocks.py').read())
"""
import json
import math
import os

import bpy
import numpy as np
from mathutils import Vector

TERRAIN_OBJECT = "terrain"
ROCKS_COLLECTION = "basaltRocks"
FOAM_COLLECTION = "shoreFoam"
CONTAINER_COLLECTION = "scenery.002"
BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"
# All stone transforms captured from the hand-placed blend (read-back-and-lock).
# Re-running reproduces every stone's exact position/yaw/scale. Regenerate with
# the capture step after any manual shoreline edits.
LOCKED_STONES_JSON = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/resources/shore_stones.json"

# Distinct basalt colour (object-level override). Dark charcoal-grey so the
# columns read as volcanic rock against the sunset terrain. Tell me to change it.
ROCK_COLOR = (0.055, 0.055, 0.065, 1.0)   # near-black basalt grey
ROCK_MATERIAL = "rock"
FOAM_COLOR = (0.78, 0.96, 0.92, 0.62)
FOAM_MATERIAL = "shoreFoam"
TERRAIN_WORLD_SIZE = 125.0
GRASS_EDGE_THRESHOLD = 0.08
SHORE_GRASS_MAX = 0.03
SHORE_WATER_MIN = 0.12
SHORE_WATER_MAX = 0.28

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

# Locked from the Blender file after manual shoreline cleanup. These are the
# actual hand-placed rocks on the west edge; generated rocks skip this band.
MANUAL_SHORE_ROCKS = [
    {"name": "shoreRock02", "location": (-53.493767, 34.157505, -0.155157), "yaw_deg": 108.999997, "scale": (0.4, 0.328, 0.216)},
    {"name": "shoreRock04", "location": (-53.389153, 35.790607, -0.13656), "yaw_deg": 100.000001, "scale": (0.46, 0.3772, 0.2484)},
    {"name": "shoreRock06", "location": (-52.900635, 38.343296, -0.257049), "yaw_deg": 100.000001, "scale": (0.28, 0.2296, 0.1512)},
    {"name": "shoreRock07", "location": (-53.30666, 37.7463, 0.053404), "yaw_deg": 90.000003, "scale": (0.38, 0.3116, 0.2052)},
    {"name": "shoreRock08", "location": (-52.371758, 39.11755, -0.13656), "yaw_deg": 222.999994, "scale": (0.26, 0.2132, 0.1404)},
    {"name": "shoreRock09", "location": (-52.969864, 24.970039, 0.071629), "yaw_deg": 90.000003, "scale": (0.3, 0.246, 0.162)},
    {"name": "shoreRock10", "location": (-53.212833, 26.354218, 0.0), "yaw_deg": 98.999999, "scale": (0.4, 0.328, 0.216)},
    {"name": "shoreRock11", "location": (-52.848186, 23.524136, 0.0), "yaw_deg": 90.000003, "scale": (0.32, 0.2624, 0.1728)},
    {"name": "shoreRock12", "location": (-53.418991, 28.016211, -0.192896), "yaw_deg": 95.000002, "scale": (0.46, 0.3772, 0.2484)},
    {"name": "shoreRock13", "location": (-53.571144, 31.228167, -0.192896), "yaw_deg": 90.000003, "scale": (0.34, 0.2788, 0.1836)},
    {"name": "shoreRock14", "location": (-53.386837, 29.399939, -0.192896), "yaw_deg": 185.000004, "scale": (0.28, 0.2296, 0.1512)},
    {"name": "shoreRock16", "location": (-53.27557, 32.587086, -0.192896), "yaw_deg": 222.999994, "scale": (0.26, 0.2132, 0.1404)},
    {"name": "shoreRock18", "location": (-52.567619, 18.464676, -0.155115), "yaw_deg": 108.999997, "scale": (0.4, 0.328, 0.216)},
    {"name": "shoreRock19", "location": (-52.30835, 15.939413, -0.155115), "yaw_deg": 90.000003, "scale": (0.32, 0.2624, 0.1728)},
    {"name": "shoreRock20", "location": (-52.619999, 19.82, -0.155115), "yaw_deg": 105.0, "scale": (0.46, 0.3772, 0.2484)},
    {"name": "shoreRock21", "location": (-52.814671, 16.805195, -0.155115), "yaw_deg": 90.000003, "scale": (0.34, 0.2788, 0.1836)},
    {"name": "shoreRock22", "location": (-52.967827, 21.217245, -0.155115), "yaw_deg": 100.000001, "scale": (0.28, 0.2296, 0.1512)},
    {"name": "shoreRock23", "location": (-52.720001, 22.08, -0.155115), "yaw_deg": 90.000003, "scale": (0.38, 0.3116, 0.2052)},
    {"name": "shoreRock24", "location": (-52.975597, 21.166512, 0.158587), "yaw_deg": 100.000001, "scale": (0.26, 0.2132, 0.1404)},
    {"name": "shoreRock28", "location": (-51.58427, 12.32245, -0.105676), "yaw_deg": 79.999998, "scale": (0.46, 0.3772, 0.2484)},
    {"name": "shoreRock31", "location": (-51.974411, 14.181248, -0.105676), "yaw_deg": 79.999998, "scale": (0.38, 0.3116, 0.2052)},
    {"name": "shoreRock32", "location": (-51.993298, 15.023856, -0.105676), "yaw_deg": 222.999994, "scale": (0.26, 0.2132, 0.1404)},
]


def _pixel_to_world(row, col, width, height):
    return (
        (row / (height - 1) - 0.5) * TERRAIN_WORLD_SIZE,
        (col / (width - 1) - 0.5) * TERRAIN_WORLD_SIZE,
    )


def _terrain_height_at(x, y, fallback):
    terrain = bpy.data.objects.get(TERRAIN_OBJECT)
    if terrain is None:
        return fallback
    try:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_terrain = terrain.evaluated_get(depsgraph)
        local_origin = eval_terrain.matrix_world.inverted() @ Vector((x, y, 20.0))
        local_dir = (eval_terrain.matrix_world.inverted().to_3x3() @ Vector((0.0, 0.0, -1.0))).normalized()
        hit, loc, _normal, _face = eval_terrain.ray_cast(local_origin, local_dir)
        if hit:
            return (eval_terrain.matrix_world @ loc).z
    except Exception:
        pass
    return fallback


def _edge_scan_for_side(side, step=4):
    img_g = bpy.data.images.get("terrainGrass")
    img_w = bpy.data.images.get("terrainWater")
    if img_g is None or img_w is None:
        print("  [WARN] terrainGrass/terrainWater missing — generated shore rocks skipped")
        return []

    width, height = img_g.size
    grass = np.asarray(img_g.pixels[:], dtype=np.float32).reshape((height, width, img_g.channels))[:, :, 1]
    water = np.asarray(img_w.pixels[:], dtype=np.float32).reshape((height, width, img_w.channels))[:, :, 0]

    directions = {
        "W": {"scan": range(0, height), "out": (-1, 0), "yaw": 90.0},
        "E": {"scan": range(height - 1, -1, -1), "out": (1, 0), "yaw": 270.0},
        "N": {"scan": range(width - 1, -1, -1), "out": (0, 1), "yaw": 180.0},
        "S": {"scan": range(0, width), "out": (0, -1), "yaw": 0.0},
    }
    sizes = (0.44, 0.52, 0.42, 0.58, 0.48, 0.40, 0.56, 0.46)
    rocks = []

    if side in ("W", "E"):
        samples = ((None, col) for col in range(28, width - 28, step))
    else:
        samples = ((row, None) for row in range(28, height - 28, step))

    for sample_index, (sample_row, sample_col) in enumerate(samples):
        row = sample_row
        col = sample_col
        for scan_value in directions[side]["scan"]:
            if side in ("W", "E"):
                row = scan_value
                col = sample_col
            else:
                row = sample_row
                col = scan_value
            if grass[row, col] > GRASS_EDGE_THRESHOLD:
                break
        else:
            continue

        out_row, out_col = directions[side]["out"]
        shore_pixel = None
        for distance in range(1, 22):
            rr = row + out_row * distance
            cc = col + out_col * distance
            if rr < 0 or rr >= height or cc < 0 or cc >= width:
                break
            if (
                grass[rr, cc] <= SHORE_GRASS_MAX
                and SHORE_WATER_MIN <= water[rr, cc] <= SHORE_WATER_MAX
            ):
                shore_pixel = (rr, cc)
                break
        if shore_pixel is None:
            continue

        x, y = _pixel_to_world(shore_pixel[0], shore_pixel[1], width, height)
        if side == "W" and 10.0 <= y <= 40.0:
            continue

        size = sizes[sample_index % len(sizes)]
        water_r = float(water[shore_pixel[0], shore_pixel[1]])
        fallback_z = -1.5 * water_r
        z = _terrain_height_at(x, y, fallback_z)
        rocks.append({
            "name": "shoreRockPending",
            "location": (x, y, z),
            "yaw_deg": directions[side]["yaw"] + ((sample_index % 5) - 2) * 8.0,
            "scale": (size, size * 0.82, size * 0.54),
            "source": f"{side}:grass-water-mask",
        })
    return rocks


def _build_shore_rocks():
    manual = [dict(spec) for spec in MANUAL_SHORE_ROCKS]
    generated = []
    for side in ("W", "S", "E", "N"):
        generated.extend(_edge_scan_for_side(side))
    for i, spec in enumerate(generated, start=101):
        spec["name"] = f"shoreRock{i:03d}"
    return manual + generated


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


def _load_locked_stones():
    """Read every hand-placed stone's locked transform from the JSON resource."""
    if not os.path.exists(LOCKED_STONES_JSON):
        print(f"  [WARN] {LOCKED_STONES_JSON} not found — no locked stones placed")
        return []
    with open(LOCKED_STONES_JSON) as handle:
        data = json.load(handle)
    stones = []
    for entry in data.get("stones", []):
        stones.append({
            "name": entry["name"],
            "style": entry.get("style", "boulder"),
            "location": tuple(entry["location"]),
            "yaw_deg": entry["yaw_deg"],
            "scale": tuple(entry["scale"]),
        })
    return stones


def run():
    print("[03-surface-detail-rocks] place locked basalt rocks on karan's island")

    container = bpy.data.collections.get(CONTAINER_COLLECTION)
    if container and container.name not in {c.name for c in bpy.context.scene.collection.children}:
        try:
            bpy.context.scene.collection.children.link(container)
        except Exception:
            pass
    coll = bpy.data.collections.get(ROCKS_COLLECTION) or bpy.data.collections.new(ROCKS_COLLECTION)

    # Source of truth is the captured JSON: every stone (inland rock* + the 195
    # hand-placed shoreRock*) is reproduced at its exact locked transform. The
    # procedural shore scan above is superseded and no longer called.
    stones = _load_locked_stones()
    keep = {s["name"] for s in stones}
    _remove_obsolete("shoreRock", keep)
    _remove_obsolete("rock", keep)
    _remove_obsolete("shoreFoam", set())

    for spec in stones:
        _place_rock(coll, spec)
    print(f"  placed {len(stones)} locked stones "
          f"({sum(1 for s in stones if s['style']=='shard')} shard / "
          f"{sum(1 for s in stones if s['style']=='boulder')} boulder)")

    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")


if __name__ == "__main__":
    run()
