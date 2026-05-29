"""Author Karan's Phase 4 bonfire centerpiece near the slab clearings.

Reference Bruno bonfire (`04-decorations-bruno-089-bonfire.py`) drops a skull +
sword + embers cluster in the old landing zone. This phase keeps only the
"warm gathering point" intent. The current design is a modern low fire bowl:
light side-frame colored stone pads, bench-dark-brown logs, black metal trim,
and warm flame shards.

Stable object names so reruns update in place instead of leaving duplicates.

Run on the already-built karan world:
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/04-decorations-bonfire.py').read())
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
BONFIRE_COLLECTION = "decorations/bonfire"
COLLIDER_COLLECTION = "colliders"
REF_COLLECTION = "refs"

# Four slab-only placements. The first keeps the original object name so the
# existing bonfire is moved, not duplicated.
BONFIRES = [
    {
        "key": "central",
        "object": "bonfire_central",
        "location": (12.822151, -20.400848),
        "light": "bonfireLight",
        "n_logs": 10,
    },
    {
        "key": "slab01_east",
        "object": "bonfire_slab01_east",
        "location": (18.719921, 1.254658),
        "light": "bonfireLight_slab01_east",
        "n_logs": 10,
    },
    {
        "key": "slab02_center",
        "object": "bonfire_slab02_center",
        "location": (-18.897404, -1.639038),
        "light": "bonfireLight_slab02_center",
        "n_logs": 10,
    },
    {
        "key": "slab03_center",
        "object": "bonfire_slab03_center",
        "location": (-2.550000, 16.150000),
        "light": "bonfireLight_slab03_center",
        "n_logs": 10,
    },
]

# material slot order in the final mesh
MAT_LIGHT_STONE = 0
MAT_DARK_BROWN = 1
MAT_BLACK_METAL = 2
MAT_EMBER = 3
MAT_FLAME_OUTER = 4
MAT_FLAME_INNER = 5
MAT_COLLIDER = 6


def _height_at(x, z):
    for slab_name in ("slab01", "slab02", "slab03"):
        slab = bpy.data.objects.get(slab_name)
        if slab is None:
            continue
        inv = slab.matrix_world.inverted()
        origin = inv @ Vector((x, z, 50.0))
        direction = inv.to_3x3() @ Vector((0.0, 0.0, -1.0))
        success, location, _normal, _idx = slab.ray_cast(origin, direction)
        if success:
            return (slab.matrix_world @ location).z

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


def _solid_material(name, color, emissive=False, strength=4.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = 0.85
        if emissive:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = color
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = strength
    return mat


def _bonfire_materials():
    # returns a list ordered to match MAT_* slot indices
    return [
        _solid_material("bonfire_light_stone", (0.740021, 0.125571, 0.0, 1.0)),
        _solid_material("bonfire_bench_dark_brown", (0.24, 0.12, 0.055, 1.0)),
        _solid_material("bonfire_black_metal", (0.015, 0.013, 0.012, 1.0)),
        _solid_material("bonfire_ember", (1.0, 0.32, 0.06, 1.0), emissive=True, strength=5.5),
        _solid_material("bonfire_flame_outer", (1.0, 0.58, 0.12, 1.0), emissive=True, strength=6.5),
        _solid_material("bonfire_flame_inner", (1.0, 0.88, 0.42, 1.0), emissive=True, strength=7.5),
        _solid_material("bonfire_shadow_collider", (0.25, 0.28, 0.25, 1.0)),
    ]


def _box(bm, uv, center, half, mat_index, face_materials):
    faces = _lib.bm_add_cuboid(bm, uv, center, half, "sand_gravel")
    face_materials.extend([mat_index] * len(faces))
    return faces


def _cylinder(bm, uv, center, radius, height, mat_index, face_materials, segments=16):
    faces = _lib.bm_add_cylinder(bm, uv, center, radius, height, "sand_gravel", segments=segments)
    face_materials.extend([mat_index] * len(faces))
    return faces


def _box_rot_z(bm, uv, center, half, mat_index, face_materials, angle):
    """Cuboid rotated about Z in place (for the criss-cross logs)."""
    faces = _box(bm, uv, center, half, mat_index, face_materials)
    cx, cy = center[0], center[1]
    c, s = math.cos(angle), math.sin(angle)
    verts = {v for f in faces for v in f.verts}
    for v in verts:
        dx = v.co.x - cx
        dy = v.co.y - cy
        v.co.x = cx + dx * c - dy * s
        v.co.y = cy + dx * s + dy * c
    return faces


def _flame_shard(bm, uv, center, half, mat_index, face_materials, yaw=0.0):
    """Low-poly square pyramid flame with a rotated base."""
    cx, cy, cz = center
    hx, hy, hz = half
    c, s = math.cos(yaw), math.sin(yaw)

    def rot(dx, dy, z):
        return (
            cx + dx * c - dy * s,
            cy + dx * s + dy * c,
            z,
        )

    z0 = cz - hz
    apex = bm.verts.new((cx, cy, cz + hz))
    base = [
        bm.verts.new(rot(-hx, -hy, z0)),
        bm.verts.new(rot(hx, -hy, z0)),
        bm.verts.new(rot(hx, hy, z0)),
        bm.verts.new(rot(-hx, hy, z0)),
    ]
    faces = [
        bm.faces.new((base[0], base[1], apex)),
        bm.faces.new((base[1], base[2], apex)),
        bm.faces.new((base[2], base[3], apex)),
        bm.faces.new((base[3], base[0], apex)),
        bm.faces.new((base[3], base[2], base[1], base[0])),
    ]
    for face in faces:
        _lib.paint_face(face, uv, "lantern_warm")
    face_materials.extend([mat_index] * len(faces))
    return faces


def _build_visible_bonfire_mesh(n_logs):
    """Bonfire in local axes; origin at ground, +Z up."""
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    fm = []

    # Light stone pads echo the bench side-frame color instead of Bruno's
    # skull/sword setup.
    for i in range(10):
        ang = (i / 10) * math.tau
        sx = math.cos(ang) * 0.82
        sy = math.sin(ang) * 0.82
        _box_rot_z(bm, uv, (sx, sy, 0.08), (0.19, 0.10, 0.08), MAT_LIGHT_STONE, fm, ang)

    # Low black metal bowl + rim. It gives the fire a more modern, deliberate
    # silhouette than a loose pile of stones.
    _cylinder(bm, uv, (0.0, 0.0, 0.15), 0.58, 0.22, MAT_BLACK_METAL, fm, segments=20)
    _cylinder(bm, uv, (0.0, 0.0, 0.30), 0.44, 0.08, MAT_EMBER, fm, segments=20)

    # Dark-brown log pile, using the same family as the bench planks.
    # Ten staggered logs make the fire feel fuller without the black metal
    # cross cutting through the flame.
    log_half = (0.50, 0.06, 0.055)
    for i in range(n_logs):
        ang = (i / n_logs) * math.pi + (0.10 if i % 2 else 0.0)
        radius = 0.10 if i % 3 == 0 else 0.03
        sx = math.cos(ang + math.pi * 0.5) * radius
        sy = math.sin(ang + math.pi * 0.5) * radius
        z = 0.36 + (i % 4) * 0.055
        half = (log_half[0] - (i % 3) * 0.035, log_half[1], log_half[2])
        _box_rot_z(bm, uv, (sx, sy, z), half, MAT_DARK_BROWN, fm, ang)

    # Flame shards: pyramids instead of Bruno's flat burn planes.
    _flame_shard(bm, uv, (0.0, 0.0, 0.78), (0.18, 0.15, 0.38), MAT_FLAME_OUTER, fm, yaw=0.2)
    _flame_shard(bm, uv, (0.12, -0.08, 0.72), (0.11, 0.10, 0.30), MAT_FLAME_OUTER, fm, yaw=1.1)
    _flame_shard(bm, uv, (-0.12, 0.10, 0.70), (0.10, 0.09, 0.28), MAT_FLAME_OUTER, fm, yaw=-0.8)
    _flame_shard(bm, uv, (0.02, 0.02, 0.82), (0.09, 0.08, 0.31), MAT_FLAME_INNER, fm, yaw=0.7)

    return bm, fm


def _build_collider(key, x, z, ground, material):
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cylinder(bm, uv, (0.0, 0.0, 0.34), 0.90, 0.68, "sand_gravel", segments=20)
    obj = _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"tube_bonfire_{key}_mesh",
        obj_name=f"tube_bonfire_{key}",
        location=(x, z, ground),
        collection_name=COLLIDER_COLLECTION,
        material=material,
        hide=True,
    )
    obj.display_type = "WIRE"
    return obj


def _add_ref(key, x, z, ground):
    ref = bpy.data.objects.get(f"refBonfire_{key}") or bpy.data.objects.new(f"refBonfire_{key}", None)
    ref.empty_display_type = "PLAIN_AXES"
    ref.location = (x, z, ground + 0.58)
    ref.scale = (0.75, 0.75, 0.75)
    ref["phase"] = "04-decorations"
    _lib.place_in(REF_COLLECTION, ref)
    return ref


def _build_bonfire(spec, mats):
    bx, bz = spec["location"]
    ground = _height_at(bx, bz)

    bm, face_materials = _build_visible_bonfire_mesh(spec["n_logs"])
    obj = _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"{spec['object']}_mesh",
        obj_name=spec["object"],
        location=(bx, bz, ground),
        collection_name=BONFIRE_COLLECTION,
        material=mats[0],
        rotation_euler=(0.0, 0.0, 0.0),
    )
    obj.data.materials.clear()
    for m in mats:
        obj.data.materials.append(m)
    if len(face_materials) == len(obj.data.polygons):
        for poly, mi in zip(obj.data.polygons, face_materials):
            poly.material_index = mi
    else:
        print(f"  [WARN] face/material mismatch "
              f"({len(face_materials)} planned, {len(obj.data.polygons)} polys)")
    obj["phase"] = "04-decorations"
    collider = _build_collider(spec["key"], bx, bz, ground, mats[MAT_COLLIDER])
    ref = _add_ref(spec["key"], bx, bz, ground)

    # warm flickery point light just above the flames
    light = bpy.data.lights.get(spec["light"]) or bpy.data.lights.new(spec["light"], 'POINT')
    light.energy = 185.0
    light.color = (1.0, 0.68, 0.28)
    light.shadow_soft_size = 1.2
    lobj = bpy.data.objects.get(spec["light"]) or bpy.data.objects.new(spec["light"], light)
    lobj.data = light
    lobj.location = (bx, bz, ground + 0.9)
    _lib.place_in(BONFIRE_COLLECTION, lobj)

    print(
        f"  {obj.name}: slab-only loc=({bx:.2f}, {bz:.2f}, {ground:.3f}); "
        f"collider={collider.name}; ref={ref.name}"
    )
    return obj


def run():
    print("[04-decorations-bonfire] build Karan slab-only bonfires")
    mats = _bonfire_materials()
    built = [_build_bonfire(spec, mats) for spec in BONFIRES]

    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")
    print(f"  built {len(built)} bonfire(s)")


if __name__ == "__main__":
    run()
