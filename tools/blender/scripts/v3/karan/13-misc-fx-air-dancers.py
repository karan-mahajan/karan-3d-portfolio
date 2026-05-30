"""Section 13 — two AIR DANCERS flanking the east approach to Projects.

The inflatable wacky-waving tube-guys, re-styled chunky. Each dancer is built
as an FK CHAIN: a base pivot empty at the ground, then ~5 tapered tube segments
parented bottom-to-top (segment N is a child of segment N-1). Authored in a
neutral near-upright pose; the Three.js runtime rotates each joint
progressively to drive the iconic flail. Two floppy arms hang off the top
segment. Stripes come from alternating sunset materials.

Blender owns: the static segment chain geometry + base pivot + custom-prop
sway hints. Three.js owns later: the per-joint wave animation.

Additive delta — run standalone on the open world-v3-karan.blend:
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/13-misc-fx-air-dancers.py').read())
"""
import math
import sys

import bmesh
import bpy

KARAN_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan"
if KARAN_DIR not in sys.path:
    sys.path.append(KARAN_DIR)

import importlib

import misc_common as mc
importlib.reload(mc)   # pick up edits even if Blender cached an older copy

# Flank the spawn->projects (38,10) corridor, offset to either side.
FLANKS = [(25.0, 3.0), (29.0, 17.0)]
SEGMENTS = 5
SEG_LEN = 0.64
R_BOTTOM = 0.24
R_TOP = 0.10
COLLECTION = "miscFx"

MATERIALS = {
    "misc_airdancer_red": (0.86, 0.16, 0.12, 1.0),
    "misc_airdancer_orange": (0.95, 0.48, 0.12, 1.0),
    "misc_airdancer_yellow": (0.96, 0.82, 0.20, 1.0),
    "misc_airdancer_base": (0.18, 0.18, 0.20, 1.0),
}


def _cleanup():
    mc.remove_objects_with_prefix("airDancerPivot_", "airDancerSeg_",
                                  "airDancerArm_", "airDancerBase_")
    mc.remove_orphan_data(mesh_prefix="miscMesh_airDancer")


def _tube(name, base_world, length, r_bottom, r_top, yaw, mat, segments=10):
    """A tapered tube whose ORIGIN is at its BASE (local z 0..length)."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segments,
                          radius1=r_bottom, radius2=r_top, depth=length)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0.0, 0.0, length * 0.5))
    mesh = bpy.data.meshes.new(f"miscMesh_airDancer_{name}")
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(mat)
    for poly in mesh.polygons:
        poly.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    obj.location = base_world
    obj.rotation_mode = "XYZ"
    obj.rotation_euler = (0.0, 0.0, yaw)
    return mc.link(obj, COLLECTION)


def _build_dancer(idx, x, z, ground, mats):
    yaw = math.atan2(-x, -z)   # face roughly toward spawn/interior
    pivot = mc.pivot_empty(
        f"airDancerPivot_{idx:02d}", (x, z, ground), yaw=yaw,
        props={"interaction": "airDancer", "segments": SEGMENTS,
               "swayAmplitudeDeg": 22.0, "swaySpeed": 1.6, "flail": True},
        size=0.8)

    # small fan/base housing (parented to pivot)
    base = mc.cylinder(f"airDancerBase_{idx:02d}", 0.34, 0.30, (x, z, ground + 0.15),
                       mats["base"], vertices=16, rotation=(0.0, 0.0, yaw),
                       collection=COLLECTION, bevel_w=0.03,
                       mesh_prefix="miscMesh_airDancer")

    stripe = [mats["red"], mats["orange"], mats["yellow"]]
    segs = []
    for i in range(SEGMENTS):
        t = i / max(1, SEGMENTS - 1)
        rb = R_BOTTOM * (1.0 - t) + R_TOP * t
        rt = R_BOTTOM * (1.0 - (i + 1) / SEGMENTS) + R_TOP * ((i + 1) / SEGMENTS)
        seg = _tube(f"airDancerSeg_{idx:02d}_{i}", (x, z, ground + i * SEG_LEN),
                    SEG_LEN, rb, rt, yaw, stripe[i % 3])
        segs.append(seg)

    # two floppy arms off the top segment
    top_z = ground + SEGMENTS * SEG_LEN
    arms = []
    for side, ang in (("l", 1.0), ("r", -1.0)):
        arm = _tube(f"airDancerArm_{idx:02d}_{side}", (x, z, top_z - 0.5),
                    0.7, 0.10, 0.05, yaw, mats["red"], segments=8)
        arm.rotation_euler = (0.0, math.radians(58.0) * ang, yaw)
        arms.append(arm)

    # parent the FK chain (after a view-layer update so matrix_world is live)
    bpy.context.view_layer.update()
    mc.parent_to(base, pivot, keep_transform=True)
    mc.parent_to(segs[0], pivot, keep_transform=True)
    for i in range(1, SEGMENTS):
        mc.parent_to(segs[i], segs[i - 1], keep_transform=True)
    for arm in arms:
        mc.parent_to(arm, segs[-1], keep_transform=True)
    return pivot


def run():
    print("[13-misc-fx-air-dancers] build 2 air dancers")
    _cleanup()
    mats = {
        "red": mc.material("misc_airdancer_red", MATERIALS["misc_airdancer_red"],
                           roughness=0.5, emissive_strength=0.10),
        "orange": mc.material("misc_airdancer_orange", MATERIALS["misc_airdancer_orange"],
                              roughness=0.5, emissive_strength=0.10),
        "yellow": mc.material("misc_airdancer_yellow", MATERIALS["misc_airdancer_yellow"],
                              roughness=0.5, emissive_strength=0.12),
        "base": mc.material("misc_airdancer_base", MATERIALS["misc_airdancer_base"]),
    }

    boxes = mc.obstacle_boxes()
    placed = []
    built = 0
    for idx, anchor in enumerate(FLANKS):
        spot = mc.find_spot(anchor, boxes, placed, min_spacing=8.0, max_radius=16.0)
        if spot is None:
            print(f"  [skip] air dancer {idx}: no clear spot near {anchor}")
            continue
        x, z, ground = spot
        _build_dancer(idx, x, z, ground, mats)
        placed.append((x, z))
        built += 1
        print(f"  air dancer {idx}: ({x:.1f},{z:.1f},{ground:.3f})")

    if placed:
        mc.cull_foliage_near(placed, radius=0.9)
    bpy.ops.object.select_all(action="DESELECT")
    mc.save()
    print(f"  built {built}/2 air dancers ({SEGMENTS}-segment chains)")


if __name__ == "__main__":
    run()
