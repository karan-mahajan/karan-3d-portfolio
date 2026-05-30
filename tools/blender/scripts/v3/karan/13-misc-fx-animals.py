"""Section 13 — ambient ANIMALS (the "sudo"-character reimagining).

Bruno's hidden rigged dev character + panther become four chunky low-poly
critters that bring the world to life: a cat + dog as pets near the NE cabin,
and a deer + rabbit roaming the north meadow. Each animal's parts parent to a
single base PIVOT empty so the Three.js runtime drives idle / hop / graze /
wander by animating ONE transform (skills-sphere hierarchy approach). The pivot
carries a `wanderRadius` + `species` so the runtime knows how to move it.

Blender owns: static posed geometry + base pivot + custom props.
Three.js owns later: idle bob / hop / graze / wander within the radius.

Additive delta — run standalone on the open world-v3-karan.blend:
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/13-misc-fx-animals.py').read())
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

COLLECTION = "miscFx"

# species -> (preferred anchor, yaw deg, wander radius). Pets by cabin (~22.7,22.4),
# wild deer + rabbit in the north meadow near experience (8,36).
ANIMALS = [
    {"species": "cat",    "anchor": (20.0, 18.0), "yaw": -120.0, "wander": 3.0},
    {"species": "dog",    "anchor": (24.0, 15.5), "yaw": -150.0, "wander": 5.0},
    {"species": "deer",   "anchor": (4.0, 28.0),  "yaw": 200.0,  "wander": 7.0},
    {"species": "rabbit", "anchor": (-3.0, 24.0), "yaw": 150.0,  "wander": 4.0},
]

MATERIALS = {
    "misc_animal_deer": (0.55, 0.36, 0.20, 1.0),
    "misc_animal_deer_antler": (0.46, 0.35, 0.22, 1.0),
    "misc_animal_dog": (0.54, 0.39, 0.22, 1.0),
    "misc_animal_cat": (0.30, 0.30, 0.34, 1.0),
    "misc_animal_rabbit": (0.82, 0.80, 0.74, 1.0),
    "misc_animal_rabbit_tail": (0.96, 0.96, 0.93, 1.0),
    "misc_animal_dark": (0.06, 0.06, 0.07, 1.0),
}


def _cleanup():
    mc.remove_objects_with_prefix("animalPivot_", "animal_")
    mc.remove_orphan_data(mesh_prefix="miscMesh_animal")


def _build_animal(spec, x, z, ground, mats):
    species = spec["species"]
    yaw = math.radians(spec["yaw"])
    pfx = "miscMesh_animal"
    parts = []

    def lc(tag, lx, ly, lz, size, mat, rot_x=0.0, rot_y=0.0):
        o = mc.local_cuboid(f"animal_{species}_{tag}", x, z, ground, yaw,
                            lx, ly, lz, size, mat, rot_x=rot_x, rot_y=rot_y,
                            collection=COLLECTION, bevel_w=0.02, mesh_prefix=pfx)
        parts.append(o)
        return o

    def ls(tag, lx, ly, lz, r, mat, scale=(1.0, 1.0, 1.0)):
        wx, wz = mc.world_xy(x, z, yaw, lx, ly)
        o = mc.sphere(f"animal_{species}_{tag}", r, (wx, wz, ground + lz), mat,
                      segments=12, ring_count=8, scale=scale,
                      collection=COLLECTION, mesh_prefix=pfx)
        parts.append(o)
        return o

    if species == "deer":
        m = mats["deer"]
        lc("body", 0.0, 0.0, 0.92, (0.46, 1.05, 0.50), m)
        lc("neck", 0.0, 0.46, 1.18, (0.24, 0.26, 0.52), m, rot_x=math.radians(-22))
        lc("head", 0.0, 0.64, 1.46, (0.24, 0.40, 0.26), m)
        ls("nose", 0.0, 0.86, 1.44, 0.06, mats["dark"])
        for s, lx in (("l", -0.09), ("r", 0.09)):
            lc(f"ear_{s}", lx, 0.58, 1.62, (0.07, 0.04, 0.16), m, rot_y=math.radians(18 if s == "r" else -18))
            lc(f"antler_{s}", lx * 1.4, 0.60, 1.78, (0.05, 0.05, 0.34), mats["deer_antler"], rot_y=math.radians(20 if s == "r" else -20))
            lc(f"antler_{s}_b", lx * 2.0, 0.60, 1.92, (0.04, 0.04, 0.18), mats["deer_antler"], rot_y=math.radians(40 if s == "r" else -40))
        for s, lx, ly in (("fl", -0.16, 0.40), ("fr", 0.16, 0.40), ("bl", -0.16, -0.40), ("br", 0.16, -0.40)):
            lc(f"leg_{s}", lx, ly, 0.34, (0.10, 0.10, 0.68), m)
        lc("tail", 0.0, -0.56, 1.02, (0.08, 0.16, 0.10), m)

    elif species == "dog":
        m = mats["dog"]
        lc("body", 0.0, 0.0, 0.48, (0.32, 0.66, 0.34), m)
        lc("head", 0.0, 0.42, 0.58, (0.26, 0.26, 0.28), m)
        lc("snout", 0.0, 0.58, 0.52, (0.16, 0.20, 0.16), m)
        ls("nose", 0.0, 0.70, 0.54, 0.05, mats["dark"])
        for s, lx in (("l", -0.12), ("r", 0.12)):
            lc(f"ear_{s}", lx, 0.40, 0.66, (0.07, 0.05, 0.18), m, rot_y=math.radians(26 if s == "r" else -26))
        for s, lx, ly in (("fl", -0.13, 0.26), ("fr", 0.13, 0.26), ("bl", -0.13, -0.26), ("br", 0.13, -0.26)):
            lc(f"leg_{s}", lx, ly, 0.23, (0.10, 0.10, 0.46), m)
        lc("tail", 0.0, -0.40, 0.62, (0.07, 0.24, 0.08), m, rot_x=math.radians(-42))

    elif species == "cat":
        m = mats["cat"]
        lc("body", 0.0, 0.0, 0.34, (0.22, 0.50, 0.24), m)
        lc("head", 0.0, 0.32, 0.42, (0.20, 0.18, 0.20), m)
        ls("nose", 0.0, 0.42, 0.40, 0.035, mats["dark"])
        for s, lx in (("l", -0.08), ("r", 0.08)):
            lc(f"ear_{s}", lx, 0.34, 0.55, (0.07, 0.05, 0.10), m, rot_y=math.radians(14 if s == "r" else -14))
        for s, lx, ly in (("fl", -0.09, 0.18), ("fr", 0.09, 0.18), ("bl", -0.09, -0.18), ("br", 0.09, -0.18)):
            lc(f"leg_{s}", lx, ly, 0.15, (0.07, 0.07, 0.30), m)
        lc("tail_a", 0.0, -0.30, 0.40, (0.06, 0.20, 0.06), m, rot_x=math.radians(-50))
        lc("tail_b", 0.0, -0.40, 0.58, (0.06, 0.06, 0.18), m)

    elif species == "rabbit":
        m = mats["rabbit"]
        lc("body", 0.0, 0.0, 0.26, (0.24, 0.36, 0.28), m)
        lc("head", 0.0, 0.24, 0.36, (0.18, 0.18, 0.20), m)
        ls("nose", 0.0, 0.34, 0.34, 0.035, mats["dark"])
        for s, lx in (("l", -0.06), ("r", 0.06)):
            lc(f"ear_{s}", lx, 0.20, 0.58, (0.06, 0.05, 0.32), m, rot_y=math.radians(10 if s == "r" else -10))
        for s, lx, ly in (("fl", -0.08, 0.14), ("fr", 0.08, 0.14)):
            lc(f"leg_{s}", lx, ly, 0.10, (0.07, 0.07, 0.20), m)
        for s, lx, ly in (("bl", -0.10, -0.14), ("br", 0.10, -0.14)):
            lc(f"leg_{s}", lx, ly, 0.12, (0.10, 0.16, 0.24), m)
        ls("tail", 0.0, -0.22, 0.30, 0.08, mats["rabbit_tail"])

    pivot = mc.pivot_empty(
        f"animalPivot_{species}", (x, z, ground), yaw=yaw,
        props={"interaction": "animal", "species": species,
               "wanderRadius": spec["wander"], "idle": "bob"},
        size=0.6)
    bpy.context.view_layer.update()
    for p in parts:
        mc.parent_to(p, pivot, keep_transform=True)
    return len(parts)


def run():
    print("[13-misc-fx-animals] build cat, dog, deer, rabbit")
    _cleanup()
    mats = {k.replace("misc_animal_", ""): mc.material(k, v)
            for k, v in MATERIALS.items()}

    boxes = mc.obstacle_boxes()
    placed = []
    built = 0
    for spec in ANIMALS:
        spot = mc.find_spot(spec["anchor"], boxes, placed, min_spacing=3.0, max_radius=18.0)
        if spot is None:
            print(f"  [skip] {spec['species']}: no clear spot near {spec['anchor']}")
            continue
        x, z, ground = spot
        n = _build_animal(spec, x, z, ground, mats)
        placed.append((x, z))
        built += 1
        print(f"  {spec['species']}: ({x:.1f},{z:.1f},{ground:.3f}) {n} parts")

    if placed:
        mc.cull_foliage_near(placed, radius=0.7)
    bpy.ops.object.select_all(action="DESELECT")
    mc.save()
    print(f"  built {built}/{len(ANIMALS)} animals")


if __name__ == "__main__":
    run()
