"""
Phase 0: Blender scene skeleton for the v2 alpine misty highlands world.

What this produces (after Run Script + save):
- The locked collection tree from spec section 11.5 — every parent and
  every leaf collection exists, even ones later phases fill in.
- Scene units = metric / meters / scale 1.0.
- A `PreviewSun` light at ~12 degrees elevation, warm color #f4d6b0. This
  is PREVIEW ONLY (not the runtime sun authority — runtime keeps its own
  TimeOfDay sun). Helps the artist see the scene tinted the way runtime
  will render it.
- Viewport: clip end 400m, shading background #e0d4c0 (mist-horizon — the
  color the misty-dawn world averages to visually).
- World ambient background #aab2b5 (overcast_mid from the palette).
- Default Cube / Camera / Light removed if present.

Idempotent: safe to re-run on an existing world.blend. Collections are
reused; the PreviewSun is reused by name; no duplicates accumulate.

How to run:
  1. Launch Blender 4.2+ (from Terminal so prints are visible).
  2. File -> New -> General.
  3. Scripting workspace -> Text Editor -> Open -> phase-00-setup.py.
  4. Run Script (Alt+P).
  5. File -> Save (Ctrl+S). The script also tries to save itself to
     tools/blender/world.blend, but a manual save belt-and-braces it.
"""

import os
import sys
import math

import bpy


# Make sure tools/blender/scripts/ is on sys.path so _lib + _palette
# import cleanly even when Blender's CWD is elsewhere.
def _script_dir():
    # Blender's Text Editor sets __file__ to the buffer name ("/Text"),
    # NOT the disk path — so we can't trust it alone. Collect every
    # plausible candidate and return the first one that actually contains
    # _lib.py.
    candidates = []
    try:
        if __file__ and os.path.isabs(__file__):
            candidates.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass

    space = getattr(bpy.context, "space_data", None)
    text = getattr(space, "text", None) if space else None
    if text and text.filepath:
        candidates.append(
            os.path.dirname(os.path.abspath(bpy.path.abspath(text.filepath)))
        )

    candidates.append(
        os.path.expanduser(
            "~/Documents/Projects/karan-portfolio/tools/blender/scripts"
        )
    )

    for path in candidates:
        if os.path.isfile(os.path.join(path, "_lib.py")):
            return path

    raise RuntimeError(
        "Could not locate _lib.py — tried: " + ", ".join(candidates)
    )


SCRIPT_DIR = _script_dir()
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import _lib       # noqa: E402
import _palette   # noqa: E402


# Spec section 11.5 — the locked collection tree. Each entry is either
# a leaf name or a "parent/leaf" path; _lib.get_collection handles
# nesting.
COLLECTION_PATHS = [
    "terrain",
    "spawn",
    "sections/projects",
    "sections/experience",
    "sections/skills",
    "sections/contact",
    "lighthouse",
    "water/river",
    "water/tributary",
    "water/waterfall",
    "water/ocean",
    "bridges",
    "trail/perimeter",
    "trail/detour_nw",
    "trail/detour_summit",
    "trail/detour_se",
    "viewpoints",
    "foliage/trees",
    "foliage/hero_trees",
    "foliage/ground_cover",
    "foliage/grass",
    "mountains",
    "refs",
]


def _srgb_to_linear(c):
    # Cheap gamma 2.2 approximation — good enough for a preview sun that
    # the artist eyeballs against the runtime renderer.
    return c ** 2.2


def _hex_to_linear_rgba(hex_str, alpha=1.0):
    r, g, b = _palette.hex_to_rgb_floats(hex_str)
    return (_srgb_to_linear(r), _srgb_to_linear(g), _srgb_to_linear(b), alpha)


def _delete_default_objects():
    for name in ("Cube", "Camera", "Light"):
        obj = bpy.data.objects.get(name)
        if obj is not None:
            bpy.data.objects.remove(obj, do_unlink=True)


def _delete_default_collection():
    # The default "Collection" data-block that ships in every new .blend.
    # Distinct from `Scene Collection` (the scene root, untouchable).
    # Must be removed AFTER our tree is built so we don't strand children.
    coll = bpy.data.collections.get("Collection")
    if coll is None:
        return
    # Move any stray children up to Scene Collection before purging, just
    # in case a manual edit linked something into it.
    scene_root = bpy.context.scene.collection
    for child in list(coll.children):
        coll.children.unlink(child)
        if child.name not in {c.name for c in scene_root.children}:
            scene_root.children.link(child)
    for obj in list(coll.objects):
        coll.objects.unlink(obj)
        if obj.name not in {o.name for o in scene_root.objects}:
            scene_root.objects.link(obj)
    bpy.data.collections.remove(coll)


def _build_collection_tree():
    for path in COLLECTION_PATHS:
        _lib.get_collection(path)


def _configure_units():
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.length_unit = 'METERS'
    scene.unit_settings.scale_length = 1.0


def _configure_viewports():
    # mist_horizon — the world averages to this in the misty-dawn lighting.
    r, g, b = _palette.hex_to_rgb_floats(_palette.PALETTE_COLORS["mist_horizon"])
    bg = (_srgb_to_linear(r), _srgb_to_linear(g), _srgb_to_linear(b))

    touched = 0
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type != 'VIEW_3D':
                continue
            for space in area.spaces:
                if space.type != 'VIEW_3D':
                    continue
                space.clip_end = 400.0
                space.shading.background_type = 'VIEWPORT'
                space.shading.background_color = bg
                touched += 1
    return touched


def _ensure_preview_sun():
    name = "PreviewSun"

    light_data = bpy.data.lights.get(name)
    if light_data is None:
        light_data = bpy.data.lights.new(name=name, type='SUN')
    else:
        light_data.type = 'SUN'

    light_data.energy = 3.0
    # sun_glow #f4d6b0. Blender lights take linear RGB; converting from
    # the sRGB hex in the spec keeps the on-screen tint matching what the
    # palette PNG and runtime renderer will produce.
    r, g, b = _palette.hex_to_rgb_floats(_palette.PALETTE_COLORS["sun_glow"])
    light_data.color = (_srgb_to_linear(r), _srgb_to_linear(g), _srgb_to_linear(b))

    obj = bpy.data.objects.get(name)
    if obj is None:
        obj = bpy.data.objects.new(name=name, object_data=light_data)
    else:
        obj.data = light_data

    # Sun lights point along -Z by default. Pitch the sun up so its rays
    # come in 12 degrees above the horizon (low golden-hour angle). Yaw
    # 45 degrees so it lights the scene from a NE direction — Phase 2+
    # terrain shading reads better that way.
    obj.rotation_euler = (math.radians(90.0 - 12.0), 0.0, math.radians(45.0))
    obj.location = (0.0, 0.0, 50.0)

    # Park in the scene root collection (preview helper, not part of the
    # locked tree).
    root = bpy.context.scene.collection
    if obj.name not in root.objects:
        # Make sure it isn't double-linked under any locked collection.
        for coll in bpy.data.collections:
            if obj.name in coll.objects:
                coll.objects.unlink(obj)
        root.objects.link(obj)


def _configure_world_background():
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world

    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node is None:
        bg_node = world.node_tree.nodes.new(type='ShaderNodeBackground')
    bg_node.inputs["Color"].default_value = _hex_to_linear_rgba(
        _palette.PALETTE_COLORS["overcast_mid"]
    )
    bg_node.inputs["Strength"].default_value = 1.0


def _save_blend():
    blend_path = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "world.blend"))
    os.makedirs(os.path.dirname(blend_path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    return blend_path


def main():
    _delete_default_objects()
    _build_collection_tree()
    _delete_default_collection()
    _configure_units()
    viewports_touched = _configure_viewports()
    _ensure_preview_sun()
    _configure_world_background()
    blend_path = _save_blend()

    n_collections = len(bpy.data.collections)
    print(
        f"{_lib.LOG_PREFIX}[phase-00] OK — collections initialised, "
        f"{n_collections} collections, scene units metric, preview sun at 12 deg"
    )
    print(f"{_lib.LOG_PREFIX}[phase-00] saved -> {blend_path}")
    print(f"{_lib.LOG_PREFIX}[phase-00] viewports configured: {viewports_touched}")


if __name__ == "__main__":
    main()
