"""Section 05 — rope & post fences (karan delta).

Bruno's 042_fences were flat solid plank panels. Ours are rope-and-post: chunky
wooden posts arranged on a ring around each section clearing, with a draped rope
swag between neighbours. The ring is left OPEN on the approach side (toward the
island centre) so the player walks straight in, and each ring auto-sizes to sit
just outside that section's footprint (so the skills sphere / projects hut /
contact board are framed, never clipped).

One combined mesh per section (`fence_<key>`, slots: post wood / rope), built in
world space with each post's base sampled from the terrain raycast. Posts that
would land in water / rock / a footprint are skipped, and rope is only strung
between neighbouring posts that both survived (never across the opening or a gap).

    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/05-foliage-fences.py').read())
"""
import math
import sys

import bmesh
import bpy
from mathutils import Vector

_KARAN_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan"
if _KARAN_DIR not in sys.path:
    sys.path.append(_KARAN_DIR)
import foliage_common as fc

COLLECTION = "fences"

SLOT_POST = 0
SLOT_ROPE = 1

POST_HEIGHT = 1.05
POST_RADIUS = 0.11
ROPE_RADIUS = 0.045
ROPE_SAG = 0.34
POST_SPACING = 3.4           # target metres between posts along the ring
OPENING_HALF_DEG = 52.0      # half-width of the approach gap (no posts here)

_WOOD = (0.40, 0.24, 0.12, 1.0)
_ROPE = (0.78, 0.66, 0.42, 1.0)


def _tube(bm, p0, p1, radius, slot, plan, segments=6):
    """Append a capped cylinder spanning p0->p1 (both Vector, world space)."""
    p0 = Vector(p0)
    p1 = Vector(p1)
    axis = p1 - p0
    length = axis.length
    if length < 1e-5:
        return
    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=segments,
                                radius1=radius, radius2=radius, depth=length)
    quat = Vector((0, 0, 1)).rotation_difference(axis.normalized())
    mid = (p0 + p1) * 0.5
    for v in res["verts"]:
        v.co = quat @ v.co
        v.co += mid
    plan += [(f, slot) for f in fc.faces_of(res["verts"])]


def _post(bm, x, z, ground, plan):
    """Vertical post + rounded cap; returns the world-space top point."""
    base = Vector((x, z, ground))
    top = Vector((x, z, ground + POST_HEIGHT))
    _tube(bm, base, top, POST_RADIUS, SLOT_POST, plan, segments=8)
    cap = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=POST_RADIUS * 1.25)
    for v in cap["verts"]:
        v.co += top
    plan += [(f, SLOT_POST) for f in fc.faces_of(cap["verts"])]
    return top


def _rope(bm, t0, t1, plan):
    """Sagging rope of short tubes between two post tops (parabolic droop)."""
    n = 6
    prev = Vector(t0)
    for i in range(1, n + 1):
        u = i / n
        p = Vector(t0).lerp(Vector(t1), u)
        p.z -= ROPE_SAG * 4.0 * u * (1.0 - u)
        _tube(bm, prev, p, ROPE_RADIUS, SLOT_ROPE, plan, segments=5)
        prev = p


def _section_fence(spec, boxes):
    cx, cz = fc.section_center(spec)
    radius = fc.section_ring_radius(spec)
    appr = fc.approach_dir(cx, cz)
    appr_ang = math.atan2(appr.y, appr.x)
    opening = math.radians(OPENING_HALF_DEG)

    # post angles span the ring EXCEPT the approach opening
    circ = 2.0 * math.pi * radius
    step = max(math.radians(18.0), POST_SPACING / radius)
    start = appr_ang + opening
    end = appr_ang + (2.0 * math.pi - opening)
    count = max(2, int(round((end - start) / step)))
    step = (end - start) / count

    posts = []   # (angle, top Vector) for valid posts only
    bm = bmesh.new()
    plan = []
    for i in range(count + 1):
        ang = start + i * step
        x = cx + math.cos(ang) * radius
        z = cz + math.sin(ang) * radius
        if not fc.valid(x, z, [], boxes):
            posts.append(None)        # placeholder keeps neighbour adjacency
            continue
        ground = fc.height_at(x, z) or 0.02
        top = _post(bm, x, z, ground, plan)
        posts.append((ang, top))

    # rope only between immediate neighbours that both exist
    strung = 0
    for a, b in zip(posts, posts[1:]):
        if a is not None and b is not None:
            _rope(bm, a[1], b[1], plan)
            strung += 1

    n_posts = sum(1 for p in posts if p is not None)
    if n_posts == 0:
        bm.free()
        return 0, 0

    wood = fc.solid_material("fence_post_wood", _WOOD, roughness=0.8)
    rope = fc.solid_material("fence_rope", _ROPE, roughness=0.9)
    mesh = fc.build_mesh(f"fenceMesh_{spec['key']}", bm, plan, [wood, rope])
    coll = fc.get_collection(COLLECTION)
    fc.link_object(f"fence_{spec['key']}", mesh, (0.0, 0.0, 0.0), coll)
    return n_posts, strung


def run():
    print("[05-foliage-fences] rope & post rings framing each section opening")
    fc.remove_objects_with_prefix("fence_")
    boxes = fc.obstacle_boxes()
    total_posts = 0
    total_rope = 0
    for spec in fc.SECTIONS:
        p, r = _section_fence(spec, boxes)
        total_posts += p
        total_rope += r
        print(f"  {spec['key']}: {p} posts, {r} rope spans")
    print(f"  built {total_posts} posts / {total_rope} rope spans -> collection '{COLLECTION}'")
    fc.save()


if __name__ == "__main__":
    run()
