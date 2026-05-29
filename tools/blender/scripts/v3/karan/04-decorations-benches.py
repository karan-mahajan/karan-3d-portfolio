"""Author Karan's Phase 4 benches beside the slab clearings.

The Bruno reference (`04-decorations-bruno-119-benches.py`) uses one chunky
wood bench mesh scattered around the old world. This phase keeps the idea
but not the asset: these are new palette-authored benches built from simple
geometry so they read as Karan's world, not a copied Bruno prop.

Placement is locked from manual Blender tuning in world-v3-karan.blend. Keep
the object names stable so rerunning this script updates the tuned benches
instead of leaving duplicates behind.

Run on the already-built karan world:
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/04-decorations-benches.py').read())
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

TOOLS_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts"
if TOOLS_DIR not in sys.path:
    sys.path.append(TOOLS_DIR)

import _lib

BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"
BENCH_COLLECTION = "decorations/benches"
COLLIDER_COLLECTION = "colliders"
REF_COLLECTION = "refs"

BENCH_MATERIAL_SPECS = (
    ("bench_dark_brown_planks", (0.24, 0.12, 0.055, 1.0)),
    ("bench_dark_brown_edges", (0.30, 0.15, 0.065, 1.0)),
    ("bench_light_side_frame", (0.74001, 0.68841, 0.476669, 1.0)),
    ("bench_black_legs", (0.015, 0.013, 0.012, 1.0)),
    ("bench_shadow_collider", (0.25, 0.28, 0.25, 1.0)),
)
MAT_OAK = 0
MAT_HONEY = 1
MAT_SAGE = 2
MAT_STONE = 3
MAT_COLLIDER = 4

BENCHES = [
    {
        "key": "slab01_south",
        "object": "bench_slab01_south",
        "location": (25.075253, -13.020023),
        "target": (18.03, -10.92),
        "yaw": -2.181662,
    },
    {
        "key": "slab01_south_001",
        "object": "bench_slab01_south.001",
        "location": (6.702155, -38.980190),
        "target": (18.03, -10.92),
        "yaw": -0.471239,
    },
    {
        "key": "slab02_west",
        "object": "bench_slab02_west",
        "location": (-14.619718, -5.770804),
        "target": (-1.13, -10.24),
        "yaw": 0.593412,
    },
    {
        "key": "slab03_west",
        "object": "bench_slab03_west",
        "location": (2.226260, 34.980457),
        "target": (-2.63, 17.30),
        "yaw": 2.420393,
    },
    {
        "key": "slab03_west_001",
        "object": "bench_slab03_west.001",
        "location": (-41.786316, 31.125631),
        "target": (-2.63, 17.30),
        "yaw": -0.523599,
    },
]


def _yaw_to_face(src_x, src_z, dst_x, dst_z):
    """Return Blender Z yaw so the bench local +Y faces the target."""
    return math.atan2(dst_x - src_x, dst_z - src_z)


def _height_at(x, z):
    """Raycast onto v3 terrain, accepting both legacy and Bruno object names."""
    terrain = bpy.data.objects.get("terrain") or bpy.data.objects.get("terrain_mesh")
    if terrain is None:
        return 0.02
    inv = terrain.matrix_world.inverted()
    origin = inv @ Vector((x, z, 50.0))
    direction = inv.to_3x3() @ Vector((0.0, 0.0, -1.0))
    success, location, _normal, _face_index = terrain.ray_cast(origin, direction)
    if not success:
        return 0.02
    return (terrain.matrix_world @ location).z


def _solid_material(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = 0.78
    return mat


def _bench_materials():
    return [_solid_material(name, color) for name, color in BENCH_MATERIAL_SPECS]


def _slat(bm, uv, center, half_extents, material_index, face_materials):
    faces = _lib.bm_add_cuboid(bm, uv, center, half_extents, "sand_gravel")
    face_materials.extend([material_index] * len(faces))
    return faces


def _slat_xrot(bm, uv, center, half_extents, material_index, face_materials, angle):
    """Cuboid rotated in the local Y/Z plane, useful for angled side cheeks."""
    faces = _slat(bm, uv, center, half_extents, material_index, face_materials)
    cy, cz = center[1], center[2]
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    verts = {vert for face in faces for vert in face.verts}
    for vert in verts:
        dy = vert.co.y - cy
        dz = vert.co.z - cz
        vert.co.y = cy + dy * cos_a - dz * sin_a
        vert.co.z = cz + dy * sin_a + dz * cos_a
    return faces


def _build_visible_bench_mesh():
    """Create a low-poly bench in local Blender axes.

    Local +Y is the sitting/facing direction. The origin is at ground level,
    so object Z can be set directly to terrain height.
    """
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    face_materials = []

    # Two black lower supports, visually separate from the light side cheeks.
    for x in (-1.02, 1.02):
        _slat(bm, uv, (x, -0.02, 0.22), (0.16, 0.34, 0.22), MAT_STONE, face_materials)

    # Slim black under-seat rail visible below the three seat boards.
    _slat(bm, uv, (0.0, 0.16, 0.35), (1.08, 0.045, 0.055), MAT_STONE, face_materials)

    # Three dark-brown seat boards.
    for i, y in enumerate((-0.34, -0.08, 0.18)):
        mat_index = MAT_HONEY if i != 1 else MAT_OAK
        _slat(bm, uv, (0.0, y, 0.50), (1.34, 0.078, 0.055), mat_index, face_materials)

    # Two dark-brown back boards seated flush on the back posts.
    # The vertical back posts sit at Y=-0.63 (front face Y=-0.53), so both
    # boards share depth Y=-0.50 to overlap that face ~3.5 cm (no float), and
    # they tile vertically (half-Z 0.14) with a 2 cm reveal: low Z[0.68,0.96],
    # high Z[0.98,1.26]. (fix 2026-05-29: was Y=-0.42/-0.56 staggered + half-Z
    # 0.06 -> lower board floated 4.5 cm off the frame with an 18 cm void.)
    for z, mat_index in ((0.82, MAT_OAK), (1.12, MAT_HONEY)):
        _slat(bm, uv, (0.0, -0.50, z), (1.38, 0.065, 0.14), mat_index, face_materials)

    # Light side frames: a clean 3-piece "H" per side — back post, front post,
    # and ONE solid arm bar resting flush on top of both. (rebuilt 2026-05-29:
    # the old 6-piece armrest had a thin rail + wide panel + angled brace + an
    # upper brace floating near the backrest, leaving gaps so the arm looked
    # broken; and the front pillar poked through the arm as a knob instead of
    # the arm capping it. Now: arm sits ON the front post, no protrusion, no
    # floating braces.)
    ARM_Z = 0.605          # arm-bar centre height
    ARM_HZ = 0.06          # arm-bar half-thickness  -> Z[0.545, 0.665]
    for x in (-1.42, 1.42):
        # back post: vertical, rear, rises to the backrest top
        _slat(bm, uv, (x, -0.55, 0.80), (0.10, 0.11, 0.66), MAT_SAGE, face_materials)
        # front post: vertical, front; TOP meets the arm-bar underside so the
        # arm rests on it (top Z = 0.665, overlapping the arm 0.12). No knob.
        front_post_top = ARM_Z + ARM_HZ           # 0.665
        front_post_bot = 0.20
        fp_cz = (front_post_top + front_post_bot) / 2.0
        fp_hz = (front_post_top - front_post_bot) / 2.0
        _slat(bm, uv, (x, 0.40, fp_cz), (0.10, 0.11, fp_hz), MAT_SAGE, face_materials)
        # arm bar: one solid horizontal piece spanning back post -> front post,
        # fully overlapping both ends so there are no gaps.
        _slat(bm, uv, (x, -0.075, ARM_Z), (0.105, 0.575, ARM_HZ), MAT_SAGE, face_materials)

    return bm, face_materials


def _local_bbox_for_bench():
    return {
        "center": (0.0, -0.07, 0.64),
        "half_extents": (1.53, 0.72, 0.64),
    }


def _add_ref(key, x, z, ground, yaw):
    ref = bpy.data.objects.get(f"refBench_{key}") or bpy.data.objects.new(f"refBench_{key}", None)
    ref.empty_display_type = "PLAIN_AXES"
    ref.location = (x, z, ground + 0.52)
    ref.rotation_euler = (0.0, 0.0, yaw)
    ref.scale = (0.55, 0.55, 0.55)
    _lib.place_in(REF_COLLECTION, ref)


def _build_collider(key, x, z, ground, yaw, material):
    box = _local_bbox_for_bench()
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cuboid(
        bm,
        uv,
        box["center"],
        box["half_extents"],
        "sand_gravel",
    )
    obj = _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"cuboid_bench_{key}_mesh",
        obj_name=f"cuboid_bench_{key}",
        location=(x, z, ground),
        collection_name=COLLIDER_COLLECTION,
        material=material,
        rotation_euler=(0.0, 0.0, yaw),
        hide=True,
    )
    obj.display_type = "WIRE"
    return obj


def _build_bench(spec, material):
    x, z = spec["location"]
    tx, tz = spec["target"]
    ground = _height_at(x, z)
    yaw = spec.get("yaw", _yaw_to_face(x, z, tx, tz))

    bm, face_materials = _build_visible_bench_mesh()
    obj = _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"bench_{spec['key']}_mesh",
        obj_name=spec.get("object", f"bench_{spec['key']}"),
        location=(x, z, ground),
        collection_name=BENCH_COLLECTION,
        material=material[0],
        rotation_euler=(0.0, 0.0, yaw),
    )
    obj.data.materials.clear()
    for mat in material:
        obj.data.materials.append(mat)
    if len(face_materials) != len(obj.data.polygons):
        print(
            f"  [WARN] {obj.name}: face/material plan mismatch "
            f"({len(face_materials)} planned, {len(obj.data.polygons)} polygons)"
        )
    for poly, mat_index in zip(obj.data.polygons, face_materials):
        poly.material_index = mat_index
    obj["phase"] = "04-decorations"
    obj["faces"] = f"slab center {tx:.2f}, {tz:.2f}"

    collider = _build_collider(spec["key"], x, z, ground, yaw, material[MAT_COLLIDER])
    _add_ref(spec["key"], x, z, ground, yaw)

    print(
        f"  {obj.name}: loc=({x:.2f}, {z:.2f}, {ground:.3f}) "
        f"yaw={math.degrees(yaw):.1f}° target=({tx:.2f}, {tz:.2f}); "
        f"collider={collider.name}"
    )
    return obj


def run():
    print("[04-decorations-benches] build Karan benches facing slab clearings")
    materials = _bench_materials()
    built = [_build_bench(spec, materials) for spec in BENCHES]

    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")
    print(f"  built {len(built)} benches")


if __name__ == "__main__":
    run()
