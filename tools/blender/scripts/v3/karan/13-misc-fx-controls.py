"""Section 13 — the CONTROLS board beside spawn.

A wooden A-frame signboard on two posts that onboards the player: a baked
"CONTROLS" header plus simple painted glyph blocks (WASD keys, a mouse, a wide
run key) with FONT labels (MOVE / LOOK / RUN). A `controlsRef` anchor sits in
front of the board so the Three.js runtime can attach the live control overlay
/ prompt.

Blender owns: the static board + posts + glyph blocks + labels + ref + collider.
Three.js owns later: the live, platform-aware control hints.

Additive delta — run standalone on the open world-v3-karan.blend:
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/13-misc-fx-controls.py').read())
"""
import math
import sys

import bpy

KARAN_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan"
if KARAN_DIR not in sys.path:
    sys.path.append(KARAN_DIR)

import importlib

import misc_common as mc
importlib.reload(mc)   # pick up edits even if Blender cached an older copy

ANCHOR = (11.0, 5.0)           # beside spawn, east; board faces back to spawn
COLLECTION = "miscFx"

MATERIALS = {
    "misc_controls_post": (0.34, 0.17, 0.06, 1.0),
    "misc_controls_frame": (0.46, 0.24, 0.10, 1.0),
    "misc_controls_face": (0.10, 0.07, 0.05, 1.0),
    "misc_controls_key": (0.86, 0.82, 0.70, 1.0),
    "misc_controls_key_accent": (0.95, 0.66, 0.28, 1.0),
    "misc_controls_text": (0.96, 0.90, 0.74, 1.0),
    "misc_controls_mouse": (0.62, 0.66, 0.62, 1.0),
}


def _cleanup():
    mc.remove_objects_with_prefix("controlsBoard_", "controlsRef",
                                  "controlsLabel_", "controlsKey_")
    mc.remove_orphan_data(mesh_prefix="miscMesh_controls",
                          curve_prefix="miscControlsCurve_")


def _label(name, body, base_x, base_z, ground, yaw, lx, lz, size, mat):
    curve = bpy.data.curves.new(f"miscControlsCurve_{name}", "FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0.01
    curve.materials.append(mat)
    obj = bpy.data.objects.new(f"controlsLabel_{name}", curve)
    wx, wz = mc.world_xy(base_x, base_z, yaw, lx, -0.40)
    obj.location = (wx, wz, ground + lz)
    obj.rotation_mode = "XYZ"
    obj.rotation_euler = (math.radians(90.0), 0.0, yaw)
    return mc.link(obj, COLLECTION)


def _key(name, base_x, base_z, ground, yaw, lx, lz, size, mat):
    """A small chunky key cap on the board face (slightly proud of the panel)."""
    return mc.local_cuboid(
        f"controlsKey_{name}", base_x, base_z, ground, yaw,
        lx, -0.30, lz, (size[0], 0.06, size[1]), mat,
        collection=COLLECTION, bevel_w=0.012, mesh_prefix="miscMesh_controls")


def run():
    print("[13-misc-fx-controls] build controls board")
    _cleanup()

    boxes = mc.obstacle_boxes()
    spot = mc.find_spot(ANCHOR, boxes, [], min_spacing=4.0, max_radius=14.0)
    if spot is None:
        print(f"  [ABORT] no clear spot near {ANCHOR}")
        return
    x, z, ground = spot
    yaw = math.atan2(-x, z)        # board front (-local_y) points back to spawn

    post = mc.material("misc_controls_post", MATERIALS["misc_controls_post"])
    frame = mc.material("misc_controls_frame", MATERIALS["misc_controls_frame"])
    face = mc.material("misc_controls_face", MATERIALS["misc_controls_face"])
    key = mc.material("misc_controls_key", MATERIALS["misc_controls_key"])
    key_accent = mc.material("misc_controls_key_accent", MATERIALS["misc_controls_key_accent"])
    text = mc.material("misc_controls_text", MATERIALS["misc_controls_text"])
    mouse = mc.material("misc_controls_mouse", MATERIALS["misc_controls_mouse"])

    # --- posts ---
    for i, lx in enumerate((-1.18, 1.18)):
        wx, wz = mc.world_xy(x, z, yaw, lx, 0.0)
        mc.cylinder(f"controlsBoard_post_{i:02d}", 0.11, 1.78, (wx, wz, ground + 0.80),
                    post, vertices=12, rotation=(0.0, 0.0, yaw),
                    collection=COLLECTION, bevel_w=0.02, mesh_prefix="miscMesh_controls")

    # --- panel + frame ---
    mc.local_cuboid("controlsBoard_panel", x, z, ground, yaw, 0.0, 0.0, 1.78,
                    (2.56, 0.16, 1.34), face, collection=COLLECTION,
                    bevel_w=0.02, mesh_prefix="miscMesh_controls")
    for ly_name, lz, sz in (("top", 2.46, (2.74, 0.20)), ("bottom", 1.10, (2.74, 0.16))):
        mc.local_cuboid(f"controlsBoard_frame_{ly_name}", x, z, ground, yaw, 0.0, 0.0, lz,
                        (sz[0], 0.22, sz[1]), frame, collection=COLLECTION,
                        bevel_w=0.02, mesh_prefix="miscMesh_controls")
    for side, lx in (("l", -1.36), ("r", 1.36)):
        mc.local_cuboid(f"controlsBoard_frame_{side}", x, z, ground, yaw, lx, 0.0, 1.78,
                        (0.18, 0.22, 1.52), frame, collection=COLLECTION,
                        bevel_w=0.02, mesh_prefix="miscMesh_controls")
    # peaked A-frame cap
    for side, lx, rot in (("l", -0.62, 0.42), ("r", 0.62, -0.42)):
        mc.local_cuboid(f"controlsBoard_cap_{side}", x, z, ground, yaw, lx, 0.0, 2.74,
                        (1.5, 0.2, 0.18), frame, rot_y=rot, collection=COLLECTION,
                        bevel_w=0.02, mesh_prefix="miscMesh_controls")

    # --- header ---
    _label("header", "CONTROLS", x, z, ground, yaw, 0.0, 2.30, 0.30, text)

    # --- WASD cluster (left) + MOVE ---
    kw = (0.20, 0.20)
    _key("w", x, z, ground, yaw, -0.92, 1.92, kw, key)
    _key("a", x, z, ground, yaw, -1.16, 1.66, kw, key)
    _key("s", x, z, ground, yaw, -0.92, 1.66, kw, key)
    _key("d", x, z, ground, yaw, -0.68, 1.66, kw, key)
    _label("move", "MOVE", x, z, ground, yaw, -0.92, 1.40, 0.16, text)

    # --- mouse (centre) + LOOK ---
    mwx, mwz = mc.world_xy(x, z, yaw, 0.18, -0.30)
    mc.cuboid("controlsKey_mouse", (mwx, mwz, ground + 1.80), (0.26, 0.10, 0.36),
              mouse, yaw=yaw, collection=COLLECTION, bevel_w=0.05,
              mesh_prefix="miscMesh_controls")
    _label("look", "LOOK", x, z, ground, yaw, 0.18, 1.42, 0.16, text)

    # --- run key (right) + RUN ---
    _key("run", x, z, ground, yaw, 1.16, 1.84, (0.62, 0.20), key_accent)
    _label("run", "RUN", x, z, ground, yaw, 1.16, 1.50, 0.16, text)

    # --- ref + collider ---
    rwx, rwz = mc.world_xy(x, z, yaw, 0.0, -1.0)
    mc.ref_anchor("controlsRef", (rwx, rwz, ground + 1.2), yaw=yaw,
                  props={"interaction": "controls",
                         "hint": "move | look | run",
                         "prompt": "controls"}, size=0.7)
    mc.collider_box("controls", x, z, ground, yaw, (2.9, 0.5, 2.7))
    mc.cull_foliage_near([(x, z)], radius=1.7)

    bpy.ops.object.select_all(action="DESELECT")
    mc.save()
    print(f"  built controls board at ({x:.1f},{z:.1f},{ground:.3f}) "
          f"yaw={math.degrees(yaw):.1f}")


if __name__ == "__main__":
    run()
