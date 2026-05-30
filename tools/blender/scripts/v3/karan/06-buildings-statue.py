"""Build Karan's personalized stone bust as a V3 section-06 structure.

Uses only existing project assets:
  - static/models/character/avatar.glb for Karan's face/head structure
  - static/models/nature/statue-column.glb for the pedestal

Runs AFTER section-05 foliage on the built V3 Karan world:
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/06-buildings-statue.py').read())

Headless from this folder:
    /Applications/Blender.app/Contents/MacOS/Blender \
      --background ../../../world-v3-karan.blend \
      --python 06-buildings-statue.py
"""
import math
import os
import sys
from pathlib import Path

import bmesh
import bpy
import mathutils

KARAN_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() \
    else "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan"
if KARAN_DIR not in sys.path:
    sys.path.append(KARAN_DIR)

import buildings_common as bc

ROOT = Path(KARAN_DIR).parents[4]
AVATAR = ROOT / "static/models/character/avatar.glb"
BASE = ROOT / "static/models/nature/statue-column.glb"

KEY = "karan_statue"
ANCHOR = (-5.5, -5.5)
YAW = math.radians(135)
BUST_YAW = YAW
HEAD_HEIGHT = 0.78
FOOTPRINT = (1.8, 1.8, 2.35)
# The visible pedestal+bust footprint is only ~0.5m square (base 0.495,
# collider 0.551). Clear grass to a 0.35 half-extent (0.7m square) so blades
# stop just outside the pedestal — small enough that grass reads right up to the
# base, large enough that nothing pokes through it. clear_grass_under feathers a
# further 0.65m, so G fully recovers ~1m out. (Was 1.25 → a 2.5m bald patch.)
GRASS_CLEAR_HALF = (0.35, 0.35)

COLORS = {
    "stone": (0.55, 0.52, 0.46, 1.0),
    "hair": (0.42, 0.40, 0.36, 1.0),
    "base": (0.34, 0.33, 0.30, 1.0),
    "collider": (0.18, 0.16, 0.11, 0.2),
}


def _mats():
    return {
        "stone": bc.material("karan_statue_warm_stone", COLORS["stone"], 0.78),
        "hair": bc.material("karan_statue_dark_stone", COLORS["hair"], 0.82),
        "base": bc.material("karan_statue_base_stone", COLORS["base"], 0.86),
        "collider": bc.material("structure_footprint", COLORS["collider"], 0.9),
    }


def _collection():
    return bc.get_collection("statue")


def _link(obj):
    coll = _collection()
    if obj.name not in {o.name for o in coll.objects}:
        coll.objects.link(obj)
    root = bpy.context.scene.collection
    if obj.name in {o.name for o in root.objects}:
        root.objects.unlink(obj)
    return obj


def _bbox_world(obj):
    bpy.context.view_layer.update()
    pts = [obj.matrix_basis @ mathutils.Vector(c) for c in obj.bound_box]
    return (
        mathutils.Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
        mathutils.Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))),
    )


def _group_bbox(objs):
    minv = mathutils.Vector((999, 999, 999))
    maxv = mathutils.Vector((-999, -999, -999))
    for obj in objs:
        lo, hi = _bbox_world(obj)
        minv.x, minv.y, minv.z = min(minv.x, lo.x), min(minv.y, lo.y), min(minv.z, lo.z)
        maxv.x, maxv.y, maxv.z = max(maxv.x, hi.x), max(maxv.y, hi.y), max(maxv.z, hi.z)
    return minv, maxv


def _imported_meshes(filepath):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(filepath))
    return [obj for obj in bpy.data.objects if obj not in before and obj.type == "MESH"]


def _remove_previous():
    bc.remove_objects_with_prefix(
        "karan_statue_",
        "cuboid_karan_statue",
        "structureFootprint_karan_statue",
    )


def _static_mesh_from(source, name, mesh_name, mat):
    verts = [source.matrix_world @ vert.co for vert in source.data.vertices]
    faces = [tuple(poly.vertices) for poly in source.data.polygons]
    mesh = bpy.data.meshes.get(mesh_name) or bpy.data.meshes.new(mesh_name)
    mesh.clear_geometry()
    mesh.from_pydata([tuple(v) for v in verts], [], faces)
    mesh.update()
    for poly in mesh.polygons:
        poly.use_smooth = True
    mesh.materials.clear()
    mesh.materials.append(mat)

    obj = bpy.data.objects.get(name) or bpy.data.objects.new(name, mesh)
    obj.data = mesh
    _link(obj)
    return obj


def _extract_head(body, mat):
    source_mesh = body.data
    head_groups = {g.index for g in body.vertex_groups if g.name in {"Head", "Neck"}}
    keep = set()
    for vert in source_mesh.vertices:
        weight = sum(group.weight for group in vert.groups if group.group in head_groups)
        world = body.matrix_world @ vert.co
        if weight > 0.45 and world.z > 1.46:
            keep.add(vert.index)

    faces = [
        tuple(poly.vertices)
        for poly in source_mesh.polygons
        if all(index in keep for index in poly.vertices)
    ]
    used = sorted({index for face in faces for index in face})
    index_map = {old: new for new, old in enumerate(used)}
    verts = [body.matrix_world @ source_mesh.vertices[index].co for index in used]
    remapped = [tuple(index_map[index] for index in face) for face in faces]

    mesh = bpy.data.meshes.get("structureMesh_karan_statue_head") or bpy.data.meshes.new(
        "structureMesh_karan_statue_head")
    mesh.clear_geometry()
    mesh.from_pydata([tuple(v) for v in verts], [], remapped)
    mesh.update()
    for poly in mesh.polygons:
        poly.use_smooth = True
    mesh.materials.clear()
    mesh.materials.append(mat)

    obj = bpy.data.objects.get("karan_statue_head") or bpy.data.objects.new("karan_statue_head", mesh)
    obj.data = mesh
    _link(obj)
    return obj


def _place_bust(objs, bx, bz, base_top):
    minv, maxv = _group_bbox(objs)
    center = (minv + maxv) * 0.5
    scale = HEAD_HEIGHT / max(maxv.z - minv.z, 0.001)
    c = math.cos(BUST_YAW)
    s = math.sin(BUST_YAW)
    for obj in objs:
        for vert in obj.data.vertices:
            world = obj.matrix_basis @ vert.co
            lx = (world.x - center.x) * scale
            ly = (world.y - center.y) * scale
            vert.co = (
                bx + lx * c - ly * s,
                bz + lx * s + ly * c,
                (world.z - minv.z) * scale + base_top + 0.03,
            )
        obj.location = (0, 0, 0)
        obj.rotation_euler = (0, 0, 0)
        obj.scale = (1, 1, 1)
        obj.data.update()


def _build_base(bx, bz, ground, mat):
    meshes = _imported_meshes(BASE)
    if not meshes:
        raise RuntimeError(f"No mesh imported from {BASE}")
    base = meshes[0]
    base.name = "karan_statue_base"
    base.data.name = "structureMesh_karan_statue_base"
    base.data.materials.clear()
    base.data.materials.append(mat)
    base.location = (bx, bz, ground)
    base.rotation_euler.z = YAW
    base.scale = (1.65, 1.65, 1.22)
    _link(base)
    lo, _hi = _bbox_world(base)
    base.location.z += ground - lo.z
    return base


def _cleanup_avatar(keep):
    keep_names = {obj.name for obj in keep}
    for obj in list(bpy.data.objects):
        if obj.name in keep_names:
            continue
        if obj.name.startswith("avaturn_") or obj.type == "ARMATURE":
            bpy.data.objects.remove(obj, do_unlink=True)


def _build_collider(visible, mat):
    minv, maxv = _group_bbox(visible)
    size = maxv - minv
    center = (minv + maxv) * 0.5
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    obj = bpy.context.object
    obj.name = "cuboid_karan_statue"
    obj.data.name = "structureMesh_cuboid_karan_statue"
    obj.dimensions = (size.x, size.y, size.z)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    obj.display_type = "WIRE"
    obj.hide_render = True
    bc._link(obj, "colliders")
    root = bpy.context.scene.collection
    if obj.name in {o.name for o in root.objects}:
        root.objects.unlink(obj)
    return obj


def run():
    print("[06-buildings-statue] build personalized Karan statue")
    _remove_previous()
    mats = _mats()

    boxes = bc.obstacle_boxes()
    spot = bc.find_spot(ANCHOR, boxes, placed=[], footprint_radius=1.2, min_spacing=0.0, max_radius=8.0)
    if spot is None:
        print(f"  [ABORT] no clear dry-land spot near {ANCHOR}")
        return
    bx, bz, ground = spot

    base = _build_base(bx, bz, ground, mats["base"])
    _imported_meshes(AVATAR)
    body = bpy.data.objects.get("avaturn_body")
    hair = bpy.data.objects.get("avaturn_hair_0")
    if body is None or hair is None:
        raise RuntimeError("avatar.glb did not contain expected Avaturn body/hair meshes")

    head_obj = _extract_head(body, mats["stone"])
    hair_obj = _static_mesh_from(hair, "karan_statue_hair", "structureMesh_karan_statue_hair", mats["hair"])
    _cleanup_avatar([head_obj, hair_obj, base])

    base_top = _bbox_world(base)[1].z
    _place_bust([head_obj, hair_obj], bx, bz, base_top)
    _build_collider([base, head_obj, hair_obj], mats["collider"])

    bc.add_footprint(KEY, bx, bz, ground, YAW, FOOTPRINT, mats["collider"])
    bc.clear_grass_under(bx, bz, YAW, GRASS_CLEAR_HALF)
    bc.clear_foliage_under(bx, bz, YAW, GRASS_CLEAR_HALF)

    bc.save()
    print(f"  built Karan statue at ({bx:.1f},{bz:.1f},{ground:.3f})")


if __name__ == "__main__":
    run()
