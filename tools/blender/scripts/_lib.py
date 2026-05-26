"""
Shared helpers for the Phase 0..13 Blender build scripts.

All phase scripts import from here for collection management, ref-empty
creation, palette UV lookup, and collider naming. Keep this module
side-effect free at import time — every helper must be called explicitly.
"""

import bpy

import _palette


LOG_PREFIX = "[blender-build]"


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
