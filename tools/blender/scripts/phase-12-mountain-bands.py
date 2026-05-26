"""
Phase 12: Mountain cardboard bands — 4 textured tilted quads ringing the
playable area.

What this produces (after Run Script + save):
- Top-level `mountains` collection. Visible mesh objects:
    * `mountain_band_front_ridge`     — 180m wide x 50m tall quad centred at
                                        Blender (0, +110, 25). Tilted ~15 deg
                                        from vertical so the top leans toward
                                        spawn (-Y). Sharpest contrast (closest
                                        layer). Material samples the user-
                                        painted `mountain-front-ridge.png`.
    * `mountain_band_mid_peaks`       — 220x60 quad at (0, +145, 30), tilted
                                        ~18 deg. Painted snow caps prominent.
                                        Loads `mountain-mid-peaks.png`.
    * `mountain_band_far_snow`        — 260x70 quad at (0, +180, 35), tilted
                                        ~20 deg. Heavily faded; farthest layer.
                                        Loads `mountain-far-snow.png`.
    * `mountain_band_foothills_east`  — 160x30 quad at (+120, +20, 15), facing
                                        west (-X) toward spawn (yawed -90 deg
                                        around Z), tilted ~15 deg. Loads
                                        `mountain-foothills-east.png`.

- 4 material clones of `world_palette_material`, one per band, each carrying
  the `*mountain*` name token so the runtime can apply the heavy-fog override
  material per spec section 10.2. Names:
    * `world_palette_mountain_front_ridge_material`
    * `world_palette_mountain_mid_peaks_material`
    * `world_palette_mountain_far_snow_material`
    * `world_palette_mountain_foothills_east_material`
  Each clone has its Principled BSDF Base Color + Alpha rewired from the
  shared palette image texture to the band's own user-painted PNG. Material
  `blend_method` set to CLIP so the alpha channel cuts out sky cleanly.

- No colliders, no refs. Past r=120 is the player soft-clamp, so these planes
  are visual-only horizon dressing — the player cannot reach them.
- No palette UV snap on these quads: the band's colour comes from the painted
  PNG, not the palette texture. The `*mountain*` material name token is the
  runtime hook for the heavy-fog override (spec section 10.2 / plan line 583).

Asset gate: the script aborts with sys.exit(1) if any of the 4 PNGs are
missing from `static/textures/mountains/`. CLAUDE.md rule 1 — no procedural
placeholders for user-authored assets.

Coordinate convention: authored in Blender Z-up. Each band is built in local
space with the X axis = quad width, Z axis = quad height, normal facing -Y.
`obj.rotation_euler` then applies the tilt (around X for the 3 northern
bands; around Y after a -90 deg Z yaw for the eastern band). `obj.location`
parks it in world.

Idempotent: re-running clears the top-level `mountains` collection and
removes the 4 stale material clones first.

How to run:
  1. Open tools/blender/world.blend in Blender 4.2+.
  2. Scripting workspace -> Text Editor -> Open -> phase-12-mountain-bands.py.
  3. Run Script (Alt+P).
  4. Script saves world.blend automatically (wm.save_as_mainfile).
"""

import os
import sys
import math

import bpy
import bmesh


# Mirror Phase 0..11's _script_dir() - Blender's Text Editor sets __file__
# to the buffer name, so collect every plausible disk path and pick the
# first that actually has _lib.py.
def _script_dir():
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
        "Could not locate _lib.py - tried: " + ", ".join(candidates)
    )


SCRIPT_DIR = _script_dir()
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import _lib       # noqa: E402


COLLECTION = "mountains"

# `static/textures/mountains/` is three levels above the scripts dir:
#   tools/blender/scripts/  ->  ../../..  ->  repo root  ->  static/...
TEXTURE_DIR = os.path.abspath(
    os.path.join(SCRIPT_DIR, "..", "..", "..", "static", "textures", "mountains")
)


# Per-band geometry + texture spec. Order = back-to-front in author space so
# the final draw order in the viewport reads naturally; runtime depth handles
# the actual sort.
#
# Fields:
#   key:        used in object name + material clone name + texture filename
#   center:     (Blender X, Y, Z) for the quad's centre
#   size:       (width_m, height_m)
#   tilt_rad:   rotation off vertical; top leans toward spawn
#   yaw_rad:    rotation around Z (Blender). 0 for north bands; -pi/2 for the
#               eastern foothills so its normal swings from -Y to -X.
#   png:        filename inside TEXTURE_DIR
BANDS = [
    {
        "key": "far_snow",
        "center": (0.0, 180.0, 35.0),
        "size": (260.0, 70.0),
        "tilt_rad": math.radians(20.0),
        "yaw_rad": 0.0,
        "png": "mountain-far-snow.png",
    },
    {
        "key": "mid_peaks",
        "center": (0.0, 145.0, 30.0),
        "size": (220.0, 60.0),
        "tilt_rad": math.radians(18.0),
        "yaw_rad": 0.0,
        "png": "mountain-mid-peaks.png",
    },
    {
        "key": "front_ridge",
        "center": (0.0, 110.0, 25.0),
        "size": (180.0, 50.0),
        "tilt_rad": math.radians(15.0),
        "yaw_rad": 0.0,
        "png": "mountain-front-ridge.png",
    },
    {
        "key": "foothills_east",
        "center": (120.0, 20.0, 15.0),
        "size": (160.0, 30.0),
        "tilt_rad": math.radians(15.0),
        # -pi/2 yaw turns a -Y-facing quad into a -X-facing quad so the
        # foothills look westward toward spawn from the eastern shore.
        "yaw_rad": math.radians(-90.0),
        "png": "mountain-foothills-east.png",
    },
]


# ============================================================================
# Asset gate
# ============================================================================


def _verify_assets():
    """Check all 4 PNGs exist before building any geometry.

    CLAUDE.md rule 1: do NOT fabricate placeholders. If any file is missing,
    print the offenders and abort.
    """
    missing = []
    for band in BANDS:
        path = os.path.join(TEXTURE_DIR, band["png"])
        if not os.path.isfile(path):
            missing.append(path)
    if missing:
        print(
            f"{_lib.LOG_PREFIX}[phase-12] ABORT - missing user-painted PNGs:"
        )
        for path in missing:
            print(f"  - {path}")
        print(
            f"{_lib.LOG_PREFIX}[phase-12] paint the silhouettes into "
            f"static/textures/mountains/ (2048x512 sRGB w/ alpha) and re-run."
        )
        sys.exit(1)


# ============================================================================
# Per-band material — clone of palette material with a custom image texture
# ============================================================================


def _clone_palette_material_with_image(target_name, image):
    """Build a clone of world_palette_material, then rewire its Principled
    BSDF Base Color + Alpha inputs to sample `image` instead of the palette
    PNG. `*mountain*` name token lets the runtime detect these for the
    heavy-fog override.

    Rebuilt every run (existing clone removed) so stale image links can't
    persist across re-runs.
    """
    src = bpy.data.materials.get(_lib.PALETTE_MATERIAL_NAME)
    if src is None:
        src = _lib.get_palette_material()

    existing = bpy.data.materials.get(target_name)
    if existing is not None:
        bpy.data.materials.remove(existing, do_unlink=True)

    clone = src.copy()
    clone.name = target_name
    clone.use_nodes = True

    nodes = clone.node_tree.nodes
    links = clone.node_tree.links

    bsdf = next(
        (n for n in nodes if n.type == "BSDF_PRINCIPLED"),
        None,
    )
    if bsdf is None:
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")

    # Disconnect anything currently feeding Base Color / Alpha (likely the
    # palette image texture inherited from the source material). We're
    # replacing both inputs with the band's PNG.
    for socket_name in ("Base Color", "Alpha"):
        socket = bsdf.inputs.get(socket_name)
        if socket is None:
            continue
        for link in list(socket.links):
            links.remove(link)

    tex_node = nodes.new("ShaderNodeTexImage")
    tex_node.image = image
    tex_node.interpolation = "Closest"
    tex_node.location = (bsdf.location.x - 320.0, bsdf.location.y)

    links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(tex_node.outputs["Alpha"], bsdf.inputs["Alpha"])

    # Alpha CLIP gives a hard sky/silhouette cutoff — these are cardboard
    # cutouts, no semi-transparent edges expected.
    clone.blend_method = "CLIP"

    return clone


# ============================================================================
# Per-band quad geometry
# ============================================================================


def _build_band_quad(band, material):
    """Build one textured tilted quad and link it into `mountains`.

    Local-space layout: X axis = width, Z axis = height, normal pointing -Y.
    Vertices wound CCW when viewed from -Y so the normal stays -Y after the
    bmesh face is created:
        BL (-W/2, 0, -H/2)  ->  BR (+W/2, 0, -H/2)
        ->  TR (+W/2, 0, +H/2)  ->  TL (-W/2, 0, +H/2)
    UVs map the PNG left->right, bottom->top.

    `rotation_euler` (XYZ order) applies tilt-around-X first, then yaw-
    around-Z. For the 3 northern bands the yaw is 0 so a positive X tilt
    leans the top in -Y (toward spawn). For the eastern foothills the
    -pi/2 Z yaw swings the -Y-facing normal to -X first, after which the
    same +X tilt still leans the top toward spawn (now in -X).
    """
    key = band["key"]
    width, height = band["size"]
    hw = width * 0.5
    hh = height * 0.5

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    bl = bm.verts.new((-hw, 0.0, -hh))
    br = bm.verts.new((+hw, 0.0, -hh))
    tr = bm.verts.new((+hw, 0.0, +hh))
    tl = bm.verts.new((-hw, 0.0, +hh))
    face = bm.faces.new((bl, br, tr, tl))

    uv_coords = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    for loop, uv in zip(face.loops, uv_coords):
        loop[uv_layer].uv = uv

    mesh_name = f"mountain_band_{key}_mesh"
    obj_name = f"mountain_band_{key}"

    existing_mesh = bpy.data.meshes.get(mesh_name)
    if existing_mesh is not None:
        bpy.data.meshes.remove(existing_mesh, do_unlink=True)
    mesh = bpy.data.meshes.new(mesh_name)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()

    obj = _lib.replace_object(obj_name, mesh)
    obj.location = band["center"]
    obj.rotation_euler = (band["tilt_rad"], 0.0, band["yaw_rad"])
    obj.scale = (1.0, 1.0, 1.0)
    obj.data.materials.clear()
    obj.data.materials.append(material)
    _lib.place_in(COLLECTION, obj)

    return obj


# ============================================================================
# Entry point
# ============================================================================


def main():
    _verify_assets()
    _lib.clear_collection(COLLECTION)

    for band in BANDS:
        png_path = os.path.join(TEXTURE_DIR, band["png"])
        image = bpy.data.images.load(filepath=png_path, check_existing=True)
        image.colorspace_settings.name = "sRGB"

        material_name = f"world_palette_mountain_{band['key']}_material"
        material = _clone_palette_material_with_image(material_name, image)

        _build_band_quad(band, material)

    blend_path = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "world.blend"))
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    print(
        f"{_lib.LOG_PREFIX}[phase-12] OK - 4 mountain bands loaded, sizes: "
        f"front=180x50 mid=220x60 far=260x70 east=160x30"
    )
    print(f"{_lib.LOG_PREFIX}[phase-12] saved -> {blend_path}")


if __name__ == "__main__":
    main()
