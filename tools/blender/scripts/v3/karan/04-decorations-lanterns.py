"""Author Karan's Phase 4 lanterns, one beside each bench.

Bruno's reference (`04-decorations-bruno-117-lanterns.py`) scatters 17 lanterns
across the whole old map. This phase keeps the idea but not the asset: simple
palette-authored standing lanterns placed next to each Karan bench so the
slab clearings read as lit gathering spots.

Each lantern = a dark slim post on a footing, a glass cage with a warm emissive
core, and a cap — built from primitive boxes (one connected mesh). Placement is
derived from the bench list in `04-decorations-benches.py` so the two stay in
sync: each lantern sits just past the right arm of its bench, on the terrain.

Object names are stable (`lantern_<benchkey>`) so rerunning updates in place
instead of leaving duplicates.

Run on the already-built karan world:
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/04-decorations-lanterns.py').read())
"""
import importlib.util
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

KARAN_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() \
    else "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan"
TOOLS_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts"
if TOOLS_DIR not in sys.path:
    sys.path.append(TOOLS_DIR)

import _lib

BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"
LANTERN_COLLECTION = "decorations/lanterns"
BENCH_SCRIPT = os.path.join(KARAN_DIR, "04-decorations-benches.py")

# Where the lantern sits relative to its bench, in the bench's LOCAL frame
# (bench local +X = long axis / right side, +Y = facing/front). Just past the
# right arm, a touch forward so it lights the seat.
LANTERN_LOCAL_OFFSET = (1.95, 0.15)

LANTERN_MATERIAL_SPECS = (
    ("lantern_post_dark", (0.05, 0.045, 0.04, 1.0)),     # near-black post/cap
    ("lantern_frame_sage", (0.74001, 0.68841, 0.476669, 1.0)),  # light frame (matches bench)
    ("lantern_glow", (1.0, 0.78, 0.42, 1.0)),            # warm emissive core
)
MAT_DARK = 0
MAT_FRAME = 1
MAT_GLOW = 2


def _height_at(x, z):
    """Raycast onto v3 terrain, accepting both legacy and Bruno object names."""
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


def _solid_material(name, color, emissive=False):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = 0.6
        if emissive and "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = color
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = 3.0
    return mat


def _lantern_materials():
    return [
        _solid_material(LANTERN_MATERIAL_SPECS[0][0], LANTERN_MATERIAL_SPECS[0][1]),
        _solid_material(LANTERN_MATERIAL_SPECS[1][0], LANTERN_MATERIAL_SPECS[1][1]),
        _solid_material(LANTERN_MATERIAL_SPECS[2][0], LANTERN_MATERIAL_SPECS[2][1], emissive=True),
    ]


def _slat(bm, uv, center, half_extents, material_index, face_materials):
    faces = _lib.bm_add_cuboid(bm, uv, center, half_extents, "sand_gravel")
    face_materials.extend([material_index] * len(faces))
    return faces


def _build_visible_lantern_mesh():
    """A simple standing lantern in local axes; origin at ground, +Z up."""
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    fm = []

    # footing
    _slat(bm, uv, (0.0, 0.0, 0.07), (0.16, 0.16, 0.07), MAT_DARK, fm)
    # post
    _slat(bm, uv, (0.0, 0.0, 1.05), (0.06, 0.06, 1.0), MAT_DARK, fm)
    # lamp housing — light frame around the glow
    _slat(bm, uv, (0.0, 0.0, 2.18), (0.17, 0.17, 0.20), MAT_FRAME, fm)
    # glowing core (sits inside the frame, slightly inset so frame edges show)
    _slat(bm, uv, (0.0, 0.0, 2.18), (0.12, 0.12, 0.15), MAT_GLOW, fm)
    # cap
    _slat(bm, uv, (0.0, 0.0, 2.44), (0.15, 0.15, 0.06), MAT_DARK, fm)
    # finial
    _slat(bm, uv, (0.0, 0.0, 2.54), (0.04, 0.04, 0.06), MAT_DARK, fm)

    return bm, fm


def _load_benches():
    spec = importlib.util.spec_from_file_location("benchmod_for_lanterns", BENCH_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.BENCHES


def _world_offset(local_x, local_y, yaw):
    """Rotate a bench-local (x, y) offset into world ground-plane (x, z)."""
    c, s = math.cos(yaw), math.sin(yaw)
    dx = local_x * c - local_y * s
    dz = local_x * s + local_y * c
    return dx, dz


def _build_lantern(bench, materials):
    bx, bz = bench["location"]
    yaw = bench.get("yaw", 0.0)
    ox, oz = _world_offset(*LANTERN_LOCAL_OFFSET, yaw)
    x, z = bx + ox, bz + oz
    ground = _height_at(x, z)

    bm, fm = _build_visible_lantern_mesh()
    key = bench["key"]
    obj = _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"lantern_{key}_mesh",
        obj_name=f"lantern_{key}",
        location=(x, z, ground),
        collection_name=LANTERN_COLLECTION,
        material=materials[0],
        rotation_euler=(0.0, 0.0, yaw),
    )
    obj.data.materials.clear()
    for mat in materials:
        obj.data.materials.append(mat)
    for poly, mi in zip(obj.data.polygons, fm):
        poly.material_index = mi
    obj["phase"] = "04-decorations"

    # warm point light at the glow so it actually lights the bench at night
    light = bpy.data.lights.get(f"lanternLight_{key}") or bpy.data.lights.new(f"lanternLight_{key}", 'POINT')
    light.energy = 60.0
    light.color = (1.0, 0.78, 0.42)
    light.shadow_soft_size = 0.3
    lobj = bpy.data.objects.get(f"lanternLight_{key}") or bpy.data.objects.new(f"lanternLight_{key}", light)
    lobj.data = light
    lobj.location = (x, z, ground + 2.18)
    _lib.place_in(LANTERN_COLLECTION, lobj)

    print(f"  lantern_{key}: loc=({x:.2f}, {z:.2f}, {ground:.3f}) yaw={math.degrees(yaw):.1f}deg")
    return obj


def run():
    print("[04-decorations-lanterns] place one lantern beside each bench")
    materials = _lantern_materials()
    benches = _load_benches()
    built = [_build_lantern(b, materials) for b in benches]
    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")
    print(f"  built {len(built)} lanterns")


if __name__ == "__main__":
    run()
