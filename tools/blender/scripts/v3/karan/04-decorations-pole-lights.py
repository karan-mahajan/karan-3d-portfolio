"""Author Karan's Phase 4 pole lights beside the benches.

Bruno's `04-decorations-bruno-118-poleLights.py` builds a pole-light set as
three pieces per lamp: a body mesh, a warm glass mesh, and a placement empty.
This keeps that same stack, but authors fresh Karan geometry and materials so
we can tune the style without importing Bruno's meshes.

Placement is locked from manual Blender tuning in world-v3-karan.blend. Keep
the object names stable so rerunning this script updates the tuned lights
instead of leaving duplicates behind.

Run on the already-built karan world:
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/04-decorations-pole-lights.py').read())
"""
import sys
import math

import bmesh
import bpy

TOOLS_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts"
if TOOLS_DIR not in sys.path:
    sys.path.append(TOOLS_DIR)

import _lib

BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"
POLE_LIGHT_COLLECTION = "decorations/pole_lights"
COLLIDER_COLLECTION = "colliders"
REF_COLLECTION = "refs"

# X/Z locations are extracted from the saved blend after manual placement.
POLE_LIGHTS = [
    {
        "key": "bench_slab01_south",
        "bench": "bench_slab01_south",
        "body": "pole_light_bench_slab01_south_body",
        "location": (27.021294, -10.415137),
    },
    {
        "key": "bench_slab01_south_001",
        "bench": "bench_slab01_south.001",
        "body": "pole_light_bench_slab01_south_001_body",
        "location": (9.643325, -40.366558),
    },
    {
        "key": "bench_slab02_west",
        "bench": "bench_slab02_west",
        "body": "pole_light_bench_slab02_west_body",
        "location": (-17.370008, -7.505277),
    },
    {
        "key": "manual_slab02_west_001",
        "body": "pole_light_bench_slab02_west_body.001",
        "location": (-38.168419, -10.233992),
    },
    {
        "key": "manual_slab02_west_002",
        "body": "pole_light_bench_slab02_west_body.002",
        "location": (-36.331604, -48.484764),
    },
    {
        "key": "manual_slab02_west_003",
        "body": "pole_light_bench_slab02_west_body.003",
        "location": (-13.182346, -39.876030),
    },
    {
        "key": "manual_slab02_west_004",
        "body": "pole_light_bench_slab02_west_body.004",
        "location": (25.967564, -27.526608),
    },
    {
        "key": "bench_slab03_west",
        "bench": "bench_slab03_west",
        "body": "pole_light_bench_slab03_west_body",
        "location": (-0.280565, 37.051285),
    },
    {
        "key": "manual_slab03_west_001",
        "body": "pole_light_bench_slab03_west_body.001",
        "location": (-3.403707, 9.745534),
    },
    {
        "key": "manual_slab03_west_002",
        "body": "pole_light_bench_slab03_west_body.002",
        "location": (20.109612, 11.678280),
    },
    {
        "key": "manual_slab03_west_003",
        "body": "pole_light_bench_slab03_west_body.003",
        "location": (18.773569, 50.847843),
    },
    {
        "key": "bench_slab03_west_001",
        "bench": "bench_slab03_west.001",
        "body": "pole_light_bench_slab03_west_001_body",
        "location": (-44.550900, 32.837234),
    },
]


def _solid_material(name, color, roughness=0.74):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
    return mat


def _emissive_material(name, color, strength=2.2):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Emission Color"].default_value = color
        bsdf.inputs["Emission Strength"].default_value = strength
        bsdf.inputs["Alpha"].default_value = 0.78
        bsdf.inputs["Roughness"].default_value = 0.36
    mat.blend_method = "BLEND"
    mat.use_screen_refraction = True
    return mat


def _materials():
    return {
        "body": _solid_material("pole_light_bench_dark_brown", (0.24, 0.12, 0.055, 1.0)),
        "glass": _emissive_material("pole_light_warm_glass", (1.0, 0.88, 0.56, 0.86)),
        "collider": _solid_material("pole_light_shadow_collider", (0.25, 0.28, 0.25, 1.0)),
    }


def _add_cuboid(bm, uv, center, half_extents, color_key="sand_gravel"):
    return _lib.bm_add_cuboid(bm, uv, center, half_extents, color_key)


def _add_cuboid_yrot(bm, uv, center, half_extents, angle, color_key="sand_gravel"):
    faces = _add_cuboid(bm, uv, center, half_extents, color_key)
    cx, _cy, cz = center
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    verts = {vert for face in faces for vert in face.verts}
    for vert in verts:
        dx = vert.co.x - cx
        dz = vert.co.z - cz
        vert.co.x = cx + dx * cos_a + dz * sin_a
        vert.co.z = cz - dx * sin_a + dz * cos_a
    return faces


def _add_torus(bm, uv, center, major_radius, minor_radius, color_key="sand_gravel", major_segments=24, minor_segments=8):
    cx, cy, cz = center
    rings = []
    for i in range(major_segments):
        theta = (i / major_segments) * math.tau
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        ring = []
        for j in range(minor_segments):
            phi = (j / minor_segments) * math.tau
            r = major_radius + math.cos(phi) * minor_radius
            ring.append(
                bm.verts.new((
                    cx + cos_t * r,
                    cy + sin_t * r,
                    cz + math.sin(phi) * minor_radius,
                ))
            )
        rings.append(ring)

    faces = []
    for i in range(major_segments):
        ni = (i + 1) % major_segments
        for j in range(minor_segments):
            nj = (j + 1) % minor_segments
            face = bm.faces.new((rings[i][j], rings[ni][j], rings[ni][nj], rings[i][nj]))
            faces.append(face)
            _lib.paint_face(face, uv, color_key)
    return faces


def _build_body_mesh(spec, material):
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)

    # Bruno's body template is roughly 3.56m tall. Keep that scale, but make
    # the visible form simple: stone base, thin post, square lantern frame.
    _lib.bm_add_cylinder(bm, uv, (0.0, 0.0, 0.08), 0.22, 0.16, "deep_crevice", segments=16)
    _lib.bm_add_cylinder(bm, uv, (0.0, 0.0, 1.33), 0.07, 2.50, "deep_crevice", segments=14)
    _lib.bm_add_cylinder(bm, uv, (0.0, 0.0, 2.54), 0.14, 0.10, "dirt_path", segments=14)
    _add_torus(bm, uv, (0.0, 0.0, 0.25), 0.15, 0.025, "dirt_path")
    _add_torus(bm, uv, (0.0, 0.0, 2.38), 0.15, 0.025, "dirt_path")

    # Lantern cage around the warm glass.
    for x in (-0.25, 0.25):
        for y in (-0.25, 0.25):
            _add_cuboid(bm, uv, (x, y, 2.84), (0.035, 0.035, 0.36), "deep_crevice")
    _add_cuboid(bm, uv, (0.0, 0.0, 2.48), (0.34, 0.34, 0.045), "dirt_path")
    _add_cuboid(bm, uv, (0.0, 0.0, 3.20), (0.34, 0.34, 0.055), "dirt_path")
    _add_cuboid(bm, uv, (0.0, 0.0, 3.33), (0.25, 0.25, 0.08), "deep_crevice")
    for y in (-0.285, 0.285):
        _add_cuboid_yrot(bm, uv, (0.0, y, 2.84), (0.36, 0.026, 0.024), 0.82, "deep_crevice")
        _add_cuboid_yrot(bm, uv, (0.0, y, 2.84), (0.36, 0.026, 0.024), -0.82, "deep_crevice")

    obj = _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"{spec['body']}_mesh",
        obj_name=spec["body"],
        location=(0.0, 0.0, 0.0),
        collection_name=POLE_LIGHT_COLLECTION,
        material=material,
    )
    obj["phase"] = "04-decorations"
    obj["source_pattern"] = "bruno body/glass/ref poleLight stack"
    return obj


def _build_glass_mesh(key, material):
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _add_cuboid(bm, uv, (0.0, 0.0, 2.84), (0.22, 0.22, 0.28), "lantern_warm")
    obj = _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"pole_light_{key}_glass_mesh",
        obj_name=f"pole_light_{key}_glass_emissive",
        location=(0.0, 0.0, 0.0),
        collection_name=POLE_LIGHT_COLLECTION,
        material=material,
    )
    obj["phase"] = "04-decorations"
    return obj


def _place_ref(key, x, z, ground):
    ref = bpy.data.objects.get(f"refPoleLight_{key}") or bpy.data.objects.new(f"refPoleLight_{key}", None)
    ref.empty_display_type = "PLAIN_AXES"
    ref.location = (x, z, ground + 2.84)
    ref.scale = (0.40, 0.40, 0.40)
    ref["phase"] = "04-decorations"
    _lib.place_in(REF_COLLECTION, ref)
    return ref


def _place_preview_light(key, x, z, ground):
    light_data = bpy.data.lights.get(f"lightPole_{key}") or bpy.data.lights.new(f"lightPole_{key}", "POINT")
    light_data.color = (1.0, 0.72, 0.42)
    light_data.energy = 180
    light_data.shadow_soft_size = 4.5
    obj = bpy.data.objects.get(f"lightPole_{key}") or bpy.data.objects.new(f"lightPole_{key}", light_data)
    obj.data = light_data
    obj.location = (x, z, ground + 2.84)
    _lib.place_in(POLE_LIGHT_COLLECTION, obj)
    return obj


def _build_collider(key, x, z, ground, material):
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)
    _lib.bm_add_cylinder(bm, uv, (0.0, 0.0, 1.72), 0.22, 3.44, "sand_gravel", segments=16)
    obj = _lib.bm_finalize_to_object(
        bm,
        mesh_name=f"tube_pole_light_{key}_mesh",
        obj_name=f"tube_pole_light_{key}",
        location=(x, z, ground),
        collection_name=COLLIDER_COLLECTION,
        material=material,
        hide=True,
    )
    obj.display_type = "WIRE"
    return obj


def _build_pole_light(spec, materials):
    x, z = spec["location"]
    ground = _lib.height_at(x, z)
    key = spec["key"]

    body = _build_body_mesh(spec, materials["body"])
    glass = _build_glass_mesh(key, materials["glass"])
    for obj in (body, glass):
        obj.location = (x, z, ground)
        obj["bench"] = spec.get("bench", "")

    collider = _build_collider(key, x, z, ground, materials["collider"])
    ref = _place_ref(key, x, z, ground)
    preview = _place_preview_light(key, x, z, ground)

    print(
        f"  pole_light_{key}: loc=({x:.2f}, {z:.2f}, {ground:.3f}) "
        f"body={body.name} glass={glass.name} ref={ref.name} "
        f"collider={collider.name} preview={preview.name}"
    )
    return body, glass


def run():
    print("[04-decorations-pole-lights] build Karan pole lights beside benches")
    materials = _materials()
    built = [_build_pole_light(spec, materials) for spec in POLE_LIGHTS]

    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")
    print(f"  built {len(built)} pole light(s)")


if __name__ == "__main__":
    run()
