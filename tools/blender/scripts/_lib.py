"""
Shared helpers for the Phase 0..13 Blender build scripts.

All phase scripts import from here for collection management, ref-empty
creation, palette UV lookup, and collider naming. Keep this module
side-effect free at import time — every helper must be called explicitly.
"""

import math

import bpy
import bmesh
from mathutils import Vector

import _palette


LOG_PREFIX = "[blender-build]"

# Shared palette-material constants. The Phase 2 terrain script creates the
# canonical textured material under this name; later phases reuse it via
# get_palette_material(). UV layer name is shared so all phases author into
# the same channel.
PALETTE_MATERIAL_NAME = "world_palette_material"
PALETTE_UV_LAYER = "palette"


# Parent collections in the locked tree (spec section 11.5). Children are
# created on demand by get_collection(); this set is here so place_in()
# can detect mis-routed leaf names early.
_KNOWN_PARENTS = {
    "sections",
    "water",
    "trail",
    "foliage",
}


def _scene_root():
    return bpy.context.scene.collection


def _find_collection(name):
    return bpy.data.collections.get(name)


def get_collection(path):
    """
    Resolve (and create if missing) the collection at `path`.

    `path` is a slash-separated string: "sections/projects" returns the
    `projects` sub-collection nested inside `sections`. Intermediate
    parents are created and linked under the scene root if missing.
    Leaf names also created if missing. Always returns the leaf
    collection.
    """
    parts = [p for p in path.split("/") if p]
    if not parts:
        raise ValueError(f"empty collection path {path!r}")

    parent = _scene_root()
    parent_coll = None
    for i, name in enumerate(parts):
        existing = _find_collection(name)
        if existing is None:
            existing = bpy.data.collections.new(name)

        # Link under the intended parent if not already there.
        if i == 0:
            target_parent = _scene_root()
        else:
            target_parent = parent_coll

        if existing.name not in target_parent.children:
            # If it was linked elsewhere, unlink first so it ends up under
            # the correct parent.
            for other in list(bpy.data.collections) + [_scene_root()]:
                if other is target_parent:
                    continue
                if hasattr(other, "children") and existing.name in other.children:
                    other.children.unlink(existing)
            if existing.name in _scene_root().children and target_parent is not _scene_root():
                _scene_root().children.unlink(existing)
            target_parent.children.link(existing)

        parent_coll = existing

    return parent_coll


def clear_collection(name):
    """
    Remove every object inside the named collection (recursing into
    child collections) but keep the collection itself intact. If the
    collection doesn't exist it's created and returned empty.
    """
    coll = _find_collection(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        _scene_root().children.link(coll)
        return coll

    for obj in list(coll.objects):
        coll.objects.unlink(obj)
        if obj.users == 0:
            bpy.data.objects.remove(obj, do_unlink=True)

    for child in list(coll.children):
        clear_collection(child.name)

    return coll


def place_in(collection_name, obj):
    """
    Link `obj` into the named collection (resolved via get_collection so
    nested paths like "sections/projects" work). Unlink from the scene
    root collection if it's currently parked there.
    """
    target = get_collection(collection_name)
    if obj.name not in target.objects:
        target.objects.link(obj)
    root = _scene_root()
    if obj.name in root.objects:
        root.objects.unlink(obj)


def ref_empty(name, location, radius=1.0, userdata=None):
    """
    Create (or reuse by name) a Blender Empty inside the `refs`
    collection. Used by Phase 2+ to mark anchor points (spawn, section
    centres, viewpoint pivots, etc) that the runtime importer reads.

    Custom properties set from `userdata` map directly onto Blender's
    id_properties so they survive the GLB export.
    """
    existing = bpy.data.objects.get(name)
    if existing is None:
        existing = bpy.data.objects.new(name, None)

    existing.empty_display_type = 'PLAIN_AXES'
    existing.location = location
    existing.scale = (radius, radius, radius)

    if userdata:
        for key, value in userdata.items():
            existing[key] = value

    place_in("refs", existing)
    return existing


def palette_uv(color_key):
    """
    Return the (u, v) center of the palette cell for `color_key`. Lookup
    keys come from _palette.PALETTE_CELL_INDEX (e.g. "pine_canopy").
    """
    idx = _palette.PALETTE_CELL_INDEX.get(color_key)
    if idx is None:
        raise KeyError(
            f"unknown palette color {color_key!r} — must be one of "
            f"{sorted(_palette.PALETTE_CELL_INDEX)}"
        )
    return _palette.cell_uv(idx)


def height_at(x, z):
    """
    Raycast from above onto the terrain mesh to find ground height.

    Used by Phase 3+ scripts to sit props on the heightfield (mirrors the
    runtime `terrain.heightAt(x, z)` contract — CLAUDE.md rule 4).
    Arguments are runtime coordinates (Three.js Y-up): x = east-west,
    z = north-south. Returns runtime Y (height in meters).

    The terrain is authored in Blender's Z-up convention, so runtime
    (x, _, z) maps to Blender (x, z, _). We raycast from +50 Blender-Z
    downward; the hit point's Blender-Z is the runtime Y we want.

    Falls back to 0.02 (inner plateau height) if the terrain mesh hasn't
    been built yet — keeps Phase 3+ scripts importable in isolation.
    """
    obj = bpy.data.objects.get("terrain_mesh")
    if obj is None:
        return 0.02

    inv = obj.matrix_world.inverted()
    origin = inv @ Vector((x, z, 50.0))
    direction = inv.to_3x3() @ Vector((0.0, 0.0, -1.0))
    success, location, _normal, _face_index = obj.ray_cast(origin, direction)
    if not success:
        return 0.02
    world_hit = obj.matrix_world @ location
    return world_hit.z  # Blender Z = runtime Y


# ============================================================================
# Generic bmesh / mesh helpers (lifted from phase-03-spawn.py so Phases 4-7
# can reuse them without duplication). Each helper is side-effect free apart
# from bmesh/bpy mutation it explicitly performs.
# ============================================================================


def get_palette_material():
    """Reuse the Phase 2 palette material or warn-and-rebuild a minimal one.

    Phase 2 builds the canonical version with the texture wired. If a later
    phase runs in isolation (no terrain yet) we still want a slot-fillable
    material so the meshes are valid - the warn nudges the user to run
    Phase 2 first.
    """
    mat = bpy.data.materials.get(PALETTE_MATERIAL_NAME)
    if mat is not None:
        return mat

    print(
        f"{LOG_PREFIX} WARN: {PALETTE_MATERIAL_NAME!r} missing "
        "- run Phase 2 first for the textured version. Building stub."
    )
    mat = bpy.data.materials.new(PALETTE_MATERIAL_NAME)
    mat.use_nodes = True
    return mat


def replace_object(name, mesh_data):
    """If a bpy object with `name` exists, remove it; create a fresh one
    holding `mesh_data`. Returns the new object."""
    existing = bpy.data.objects.get(name)
    if existing is not None:
        bpy.data.objects.remove(existing, do_unlink=True)
    return bpy.data.objects.new(name, mesh_data)


def attach_palette_material(obj, material):
    obj.data.materials.clear()
    obj.data.materials.append(material)


def paint_face(face, uv_layer, color_key):
    """Set every loop UV of `face` to the palette cell center for `color_key`."""
    u, v = palette_uv(color_key)
    for loop in face.loops:
        loop[uv_layer].uv = (u, v)


def bm_finalize_to_object(bm, mesh_name, obj_name, location, collection_name,
                          material, rotation_euler=(0.0, 0.0, 0.0),
                          hide=False):
    """Write a bmesh to a fresh mesh datablock + object, link into the
    requested collection, attach the shared palette material, free the bmesh.

    `location` is in Blender axes (x, y_north, z_height). Caller is
    responsible for computing that from runtime coords.
    """
    mesh = bpy.data.meshes.get(mesh_name)
    if mesh is not None:
        bpy.data.meshes.remove(mesh, do_unlink=True)
    mesh = bpy.data.meshes.new(mesh_name)

    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()

    obj = replace_object(obj_name, mesh)
    obj.location = location
    obj.rotation_euler = rotation_euler
    obj.scale = (1.0, 1.0, 1.0)
    attach_palette_material(obj, material)
    place_in(collection_name, obj)

    if hide:
        obj.hide_viewport = True
        obj.hide_render = True

    return obj


def bm_add_cuboid(bm, uv_layer, center, half_extents, color_key):
    """Append an axis-aligned cuboid to `bm` at Blender-space `center`. All
    6 faces get the palette UV for `color_key`. Returns the list of new faces."""
    cx, cy, cz = center
    hx, hy, hz = half_extents
    verts = [
        bm.verts.new((cx - hx, cy - hy, cz - hz)),
        bm.verts.new((cx + hx, cy - hy, cz - hz)),
        bm.verts.new((cx + hx, cy + hy, cz - hz)),
        bm.verts.new((cx - hx, cy + hy, cz - hz)),
        bm.verts.new((cx - hx, cy - hy, cz + hz)),
        bm.verts.new((cx + hx, cy - hy, cz + hz)),
        bm.verts.new((cx + hx, cy + hy, cz + hz)),
        bm.verts.new((cx - hx, cy + hy, cz + hz)),
    ]
    # Quad winding: outward-facing CCW. Order = bottom, top, -Y, +Y, -X, +X.
    quad_indices = [
        (0, 3, 2, 1),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (3, 7, 6, 2),
        (0, 4, 7, 3),
        (1, 2, 6, 5),
    ]
    faces = []
    for idx in quad_indices:
        face = bm.faces.new((verts[idx[0]], verts[idx[1]],
                             verts[idx[2]], verts[idx[3]]))
        faces.append(face)

    for face in faces:
        paint_face(face, uv_layer, color_key)

    return faces


def bm_add_cylinder(bm, uv_layer, center, radius, height, color_key,
                    segments=24):
    """Append a Z-axis-aligned cylinder to `bm`. `center` is the cylinder's
    centre point (Blender axes), `height` is total along Z. Returns the
    list of new faces (1 cap below, 1 cap above, segments side quads)."""
    cx, cy, cz = center
    hz = height * 0.5

    bottom_ring = []
    top_ring = []
    for i in range(segments):
        angle = (i / segments) * math.tau
        x = cx + math.cos(angle) * radius
        y = cy + math.sin(angle) * radius
        bottom_ring.append(bm.verts.new((x, y, cz - hz)))
        top_ring.append(bm.verts.new((x, y, cz + hz)))

    faces = []
    for i in range(segments):
        j = (i + 1) % segments
        face = bm.faces.new((bottom_ring[i], top_ring[i],
                             top_ring[j], bottom_ring[j]))
        faces.append(face)

    # Caps as n-gons. Reversed bottom so its normal points -Z.
    bottom_cap = bm.faces.new(list(reversed(bottom_ring)))
    top_cap = bm.faces.new(top_ring)
    faces.extend([bottom_cap, top_cap])

    for face in faces:
        paint_face(face, uv_layer, color_key)

    return faces


def name_collider(obj, kind, parent_label):
    """
    Rename `obj` to `<kind>_<parent_label>`. `kind` must be one of
    cuboid|tube|trimesh — the runtime importer uses the prefix to pick
    a Rapier collider type. Parenting stays untouched here; Phase 2+
    scripts handle that next to the visible mesh.
    """
    if kind not in ("cuboid", "tube", "trimesh"):
        raise ValueError(
            f"collider kind must be cuboid|tube|trimesh, got {kind!r}"
        )
    obj.name = f"{kind}_{parent_label}"
    return obj
