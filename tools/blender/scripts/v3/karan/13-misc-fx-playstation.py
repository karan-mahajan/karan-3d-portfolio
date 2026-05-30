"""Section 13 — a PLAYSTATION easter-egg prop tucked by the cabin.

A chunky low-poly console + controller sitting on a small wooden crate, with a
faint blue power-LED. Pure static discoverable prop (no runtime motion); a
`playstationRef` anchor lets the runtime hang an interaction on it if desired.

Additive delta — run standalone on the open world-v3-karan.blend:
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/13-misc-fx-playstation.py').read())
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

ANCHOR = (26.0, 19.0)          # near the NE cabin (~22.7, 22.4)
COLLECTION = "miscFx"

MATERIALS = {
    "misc_ps_crate": (0.40, 0.24, 0.11, 1.0),
    "misc_ps_body": (0.16, 0.18, 0.22, 1.0),
    "misc_ps_dark": (0.06, 0.07, 0.09, 1.0),
    "misc_ps_led": (0.25, 0.66, 0.98, 1.0),
    "misc_ps_pad": (0.20, 0.22, 0.27, 1.0),
}


def _cleanup():
    mc.remove_objects_with_prefix("playstation_", "playstationRef")
    mc.remove_orphan_data(mesh_prefix="miscMesh_playstation")


def run():
    print("[13-misc-fx-playstation] build playstation prop")
    _cleanup()

    boxes = mc.obstacle_boxes()
    spot = mc.find_spot(ANCHOR, boxes, [], min_spacing=4.0, max_radius=16.0)
    if spot is None:
        print(f"  [ABORT] no clear spot near {ANCHOR}")
        return
    x, z, ground = spot
    yaw = math.atan2(-x, -z)       # face the interior / approaching player

    crate = mc.material("misc_ps_crate", MATERIALS["misc_ps_crate"])
    body = mc.material("misc_ps_body", MATERIALS["misc_ps_body"])
    dark = mc.material("misc_ps_dark", MATERIALS["misc_ps_dark"])
    led = mc.material("misc_ps_led", MATERIALS["misc_ps_led"], roughness=0.3,
                      emissive_strength=3.0)
    pad = mc.material("misc_ps_pad", MATERIALS["misc_ps_pad"])

    pfx = "miscMesh_playstation"
    crate_h = 0.62
    # crate
    mc.local_cuboid("playstation_crate", x, z, ground, yaw, 0.0, 0.0, crate_h * 0.5,
                    (1.30, 1.00, crate_h), crate, collection=COLLECTION,
                    bevel_w=0.04, mesh_prefix=pfx)
    top = crate_h
    # console body
    mc.local_cuboid("playstation_console", x, z, ground, yaw, -0.10, 0.0, top + 0.13,
                    (0.86, 0.62, 0.26), body, collection=COLLECTION,
                    bevel_w=0.03, mesh_prefix=pfx)
    # disc-slot stripe
    mc.local_cuboid("playstation_slot", x, z, ground, yaw, -0.10, -0.32, top + 0.16,
                    (0.66, 0.04, 0.05), dark, collection=COLLECTION,
                    bevel_w=0.0, mesh_prefix=pfx)
    # power LED
    lwx, lwz = mc.world_xy(x, z, yaw, 0.30, -0.32)
    mc.sphere("playstation_led", 0.045, (lwx, lwz, ground + top + 0.16), led,
              segments=10, ring_count=6, collection=COLLECTION, mesh_prefix=pfx)
    # controller body + grips + sticks, beside the console
    cwx, cwz = mc.world_xy(x, z, yaw, 0.46, 0.18)
    mc.cuboid("playstation_pad_body", (cwx, cwz, ground + top + 0.05),
              (0.30, 0.20, 0.07), pad, yaw=yaw, collection=COLLECTION,
              bevel_w=0.035, mesh_prefix=pfx)
    for side, lx in (("l", 0.34), ("r", 0.58)):
        gwx, gwz = mc.world_xy(x, z, yaw, lx, 0.30)
        mc.cuboid(f"playstation_pad_grip_{side}", (gwx, gwz, ground + top + 0.02),
                  (0.09, 0.13, 0.10), pad, yaw=yaw, collection=COLLECTION,
                  bevel_w=0.04, mesh_prefix=pfx)
    for side, lx in (("l", 0.40), ("r", 0.52)):
        swx, swz = mc.world_xy(x, z, yaw, lx, 0.14)
        mc.sphere(f"playstation_pad_stick_{side}", 0.03, (swx, swz, ground + top + 0.10),
                  dark, segments=8, ring_count=5, collection=COLLECTION, mesh_prefix=pfx)

    mc.ref_anchor("playstationRef", (x, z, ground + top + 0.6), yaw=yaw,
                  props={"interaction": "playstation", "static": True}, size=0.6)
    mc.collider_box("playstation", x, z, ground, yaw, (1.5, 1.2, crate_h + 0.4))
    mc.cull_foliage_near([(x, z)], radius=1.1)

    bpy.ops.object.select_all(action="DESELECT")
    mc.save()
    print(f"  built playstation at ({x:.1f},{z:.1f},{ground:.3f}) yaw={math.degrees(yaw):.1f}")


if __name__ == "__main__":
    run()
