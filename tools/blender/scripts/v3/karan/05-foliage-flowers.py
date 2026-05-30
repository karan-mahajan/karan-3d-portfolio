"""Section 05 — flowers (karan delta).

Bruno's 041_flowers were flat identical decal planes scattered at random. Ours
are little low-poly 3D flowers (green stem + 5 petals + gold centre) used two
ways under the section-framing plan:

  - WELCOME MATS: two small clusters flanking each section's approach threshold,
    tinted to THAT section's accent colour (projects=blue, experience=orange,
    skills=green, contact=pink) so the foliage reinforces section identity.
  - MEADOW SCATTER: a lighter spread across open valid land in mixed sunset
    colours (peach / coral / red / gold), not section-coded.

Every flower Z comes from a terrain raycast; clusters/scatter reject water,
rock, bridge, slab and section footprints via the shared validation.

    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/05-foliage-flowers.py').read())
"""
import math
import random
import sys

import bmesh
import bpy
from mathutils import Vector

_KARAN_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan"
if _KARAN_DIR not in sys.path:
    sys.path.append(_KARAN_DIR)
import foliage_common as fc

COLLECTION = "flowers"
SEED = 73
MEADOW_COUNT = 16

SLOT_PETAL = 0
SLOT_CENTER = 1
SLOT_STEM = 2

_CENTER_GOLD = (0.95, 0.80, 0.25, 1.0)
_STEM_GREEN = (0.20, 0.42, 0.20, 1.0)


def _flower_mesh(name, petal_color):
    """Build one flower mesh: stem cylinder + 5 radial petals + gold centre.
    ~0.5 m tall before per-instance scale. Slots: petal / centre / stem."""
    petal_mat = fc.solid_material(f"flower_petal_{name}", petal_color, roughness=0.7)
    center_mat = fc.solid_material("flower_center_gold", _CENTER_GOLD, roughness=0.6)
    stem_mat = fc.solid_material("flower_stem_green", _STEM_GREEN, roughness=0.8)

    bm = bmesh.new()
    plan = []

    # stem
    stem = bmesh.ops.create_cone(bm, cap_ends=True, segments=6,
                                 radius1=0.035, radius2=0.028, depth=0.38)
    for v in stem["verts"]:
        v.co.z += 0.19
    plan += [(f, SLOT_STEM) for f in fc.faces_of(stem["verts"])]

    head_z = 0.40
    # 5 petals — small squashed spheres tilted outward around the head
    for k in range(5):
        ang = k * (math.tau / 5.0)
        petal = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.13)
        vs = petal["verts"]
        for v in vs:
            v.co.x *= 1.0
            v.co.y *= 0.55      # flatten into a petal
            v.co.z *= 0.32
        # move out along the petal's radial direction, lift to head height
        offset = Vector((math.cos(ang) * 0.16, math.sin(ang) * 0.16, head_z))
        for v in vs:
            # rotate the flattened petal to face outward
            rx, ry = v.co.x, v.co.y
            v.co.x = rx * math.cos(ang) - ry * math.sin(ang)
            v.co.y = rx * math.sin(ang) + ry * math.cos(ang)
            v.co += offset
        plan += [(f, SLOT_PETAL) for f in fc.faces_of(vs)]

    # gold centre
    core = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.085)
    for v in core["verts"]:
        v.co.z *= 0.7
        v.co += Vector((0.0, 0.0, head_z + 0.02))
    plan += [(f, SLOT_CENTER) for f in fc.faces_of(core["verts"])]

    return fc.build_mesh(name, bm, plan, [petal_mat, center_mat, stem_mat])


def _place(coll, mesh, name, x, z, rng):
    ground = fc.height_at(x, z) or 0.02
    s = rng.uniform(0.85, 1.35)
    fc.link_object(name, mesh, (x, z, ground), coll,
                   rotation_z=rng.uniform(0.0, math.tau), scale=(s, s, s))


def _welcome_mats(coll, boxes, rng):
    """Two accent-tinted clusters flanking each section's approach threshold."""
    placed = 0
    for spec in fc.SECTIONS:
        cx, cz = fc.section_center(spec)
        radius = fc.section_ring_radius(spec)
        appr = fc.approach_dir(cx, cz)
        perp = Vector((-appr.y, appr.x))          # sideways across the opening
        mesh = _flower_mesh(spec["key"], fc.lighten(spec["accent"], 0.22))
        # threshold = just outside the ring on the approach side
        thx = cx + appr.x * (radius + 1.0)
        thz = cz + appr.y * (radius + 1.0)
        for side in (-1.0, 1.0):
            bx = thx + perp.x * side * 1.8
            bz = thz + perp.y * side * 1.8
            for _ in range(3):
                jx = bx + rng.uniform(-0.7, 0.7)
                jz = bz + rng.uniform(-0.7, 0.7)
                if fc.valid(jx, jz, [], boxes):
                    _place(coll, mesh, f"flower_{spec['key']}_{placed:02d}", jx, jz, rng)
                    placed += 1
    return placed


def _meadow(coll, boxes, rng):
    """Mixed sunset-colour flowers scattered across open valid land."""
    meshes = [_flower_mesh(f"meadow{i}", c)
              for i, c in enumerate(fc.MEADOW_FLOWER_COLORS)]
    cands = []
    for ang in range(0, 360, 17):
        for rad in (12, 20, 30, 42):
            a = math.radians(ang)
            cands.append((round(rad * math.cos(a) + rng.uniform(-4, 4), 2),
                          round(rad * math.sin(a) + rng.uniform(-4, 4), 2)))
    rng.shuffle(cands)
    placed = []
    n = 0
    for (x, z) in cands:
        if n >= MEADOW_COUNT:
            break
        if not fc.valid(x, z, placed, boxes, 5.0):
            continue
        placed.append((x, z))
        _place(coll, rng.choice(meshes), f"flower_meadow_{n:02d}", x, z, rng)
        n += 1
    return n


def run():
    print("[05-foliage-flowers] accent welcome-mats + mixed meadow scatter")
    fc.remove_objects_with_prefix("flower_")
    coll = fc.get_collection(COLLECTION)
    boxes = fc.obstacle_boxes()
    rng = random.Random(SEED)

    w = _welcome_mats(coll, boxes, rng)
    m = _meadow(coll, boxes, rng)
    print(f"  placed {w} welcome-mat + {m} meadow flowers -> collection '{COLLECTION}'")
    fc.save()


if __name__ == "__main__":
    run()
