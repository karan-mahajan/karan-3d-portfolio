"""Section 05 — bush SDF-cloud anchors (karan delta).

Bruno's 040_bushes placed 130 hardcoded icospheres for his big game-world. Per
memory `reference_bruno_bushes_are_sdf` those are NOT solid geometry at runtime:
the Three.js Foliage class reads each position and renders an SDF-alpha leaf
cloud (same system as tree canopies). So here we author lightweight yellow-green
icosphere ANCHOR proxies on our own valid land — the runtime swaps them for
clouds later. The yellow-green palette is LOCKED per the section decision.

Placement: deterministic jittered scatter, denser near the 4 sections and
sparser at the open centre (Bruno's density-gradient idea), rejecting water /
rock / bridge / slab / section footprints via the shared validation. Each bush
is the same low-poly squashed icosphere mesh, instanced with per-bush scale +
Z-rotation for variety, and tagged `sdf_foliage = "bush"` for the runtime.

    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/05-foliage-bushes.py').read())
"""
import math
import random
import sys

import bmesh
import bpy

_KARAN_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan"
if _KARAN_DIR not in sys.path:
    sys.path.append(_KARAN_DIR)
import foliage_common as fc

COLLECTION = "bushes"
TARGET_COUNT = 46
MIN_SPACING = 4.2
SEED = 51


def _anchor_mesh():
    """One shared squashed low-poly icosphere = the bush SDF anchor proxy."""
    name = "bushAnchorMesh"
    mat = fc.solid_material("bush_foliage", fc.BUSH_COLOR_BASE, roughness=0.95)
    bm = bmesh.new()
    res = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
    for v in res["verts"]:
        v.co.z *= 0.78          # squash to a rounded dome
    plan = [(f, 0) for f in bm.faces]
    return fc.build_mesh(name, bm, plan, [mat])


def _candidates(rng):
    """Jittered polar grid; sorted so points nearer a section come first
    (yields the dense-near-sections / sparse-centre gradient)."""
    pts = []
    for ang in range(0, 360, 9):
        for rad in (10, 16, 22, 28, 34, 40, 46):
            a = math.radians(ang)
            x = rad * math.cos(a) + rng.uniform(-3.5, 3.5)
            z = rad * math.sin(a) + rng.uniform(-3.5, 3.5)
            pts.append((round(x, 2), round(z, 2)))
    rng.shuffle(pts)
    centers = [fc.section_center(s) for s in fc.SECTIONS]

    def nearest_section(p):
        return min(math.hypot(p[0] - cx, p[1] - cz) for cx, cz in centers)

    pts.sort(key=nearest_section)
    return pts


def run():
    print("[05-foliage-bushes] scatter yellow-green SDF anchors on valid land")
    fc.remove_objects_with_prefix("bushAnchor_")
    coll = fc.get_collection(COLLECTION)
    mesh = _anchor_mesh()
    boxes = fc.obstacle_boxes()
    rng = random.Random(SEED)

    placed = []
    for (x, z) in _candidates(rng):
        if len(placed) >= TARGET_COUNT:
            break
        if not fc.valid(x, z, placed, boxes, MIN_SPACING):
            continue
        placed.append((x, z))

    built = 0
    for i, (x, z) in enumerate(placed):
        ground = fc.height_at(x, z) or 0.02
        r = random.Random(SEED * 100 + i)
        s = r.uniform(0.70, 1.12)
        fc.link_object(
            f"bushAnchor_{i:02d}", mesh,
            (x, z, ground + 0.55 * s),          # sit the dome on the ground
            coll,
            rotation_z=r.uniform(0.0, math.tau),
            scale=(s, s, s * 0.92),
            userprops={"sdf_foliage": "bush"},
        )
        built += 1

    if built < TARGET_COUNT:
        print(f"  [note] placed {built}/{TARGET_COUNT} (island crowded near water/sections)")
    print(f"  placed {built} bush anchors -> collection '{COLLECTION}'")
    fc.save()


if __name__ == "__main__":
    run()
