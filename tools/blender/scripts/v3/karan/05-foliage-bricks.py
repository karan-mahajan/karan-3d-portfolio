"""Section 05 — bricks: paving, kerb edging, loose piles (karan delta).

Bruno's 043_bricks were random tumbled piles only. Ours give the section
approaches a grounded floor under the section-framing plan:

  - PAVED THRESHOLD: a small grid of flat sandstone tiles paving the approach
    into each section, aligned to the approach direction.
  - KERB: a couple of taller bricks capping each side of the fence opening.
  - LOOSE PILES: a handful of tumbled 2-4 brick stacks scattered on open land
    for lived-in texture (the bit of Bruno we keep).

One shared unit-cube brick mesh is instanced with per-object scale/rotation
(Bruno's instancing approach). Every brick Z is terrain-sampled; paving/kerb
sit at each section's ring radius, piles reject water/rock/footprints.

    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/05-foliage-bricks.py').read())
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

COLLECTION = "bricks"
SEED = 91

# bricks are authored 4x larger than the original sketch, with ~2x the count
# (user tuning pass): chunky flagstone paving, heavier kerb, more loose piles.
SIZE_SCALE = 4.0
TILE = tuple(v * SIZE_SCALE for v in (0.72, 0.46, 0.08))   # flat paving flagstone
KERB = tuple(v * SIZE_SCALE for v in (0.50, 0.34, 0.26))   # heavy edging block
PILE = tuple(v * SIZE_SCALE for v in (0.60, 0.32, 0.18))   # loose pile brick

_SANDSTONE = (0.74, 0.52, 0.33, 1.0)
_KERB_COLOR = (0.60, 0.40, 0.25, 1.0)

PAVE_COLS = (-1.5, -0.5, 0.5, 1.5)   # across the approach (4 wide)
PAVE_ROWS = (0, 1, 2)                # outward from the threshold (3 deep)
PILE_COUNT = 10


def _unit_cube(name, color):
    """1x1x1 cube centred at origin with a solid material — instanced via
    per-object scale into tiles / kerb / pile bricks."""
    mat = fc.solid_material(name + "_mat", color, roughness=0.85)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    plan = [(f, 0) for f in bm.faces]   # fresh bm holds only the 6 cube faces
    return fc.build_mesh(name, bm, plan, [mat])


def _put(coll, mesh, name, x, z, dims, rng, lift=0.0, yaw=0.0,
         tilt=(0.0, 0.0)):
    ground = fc.height_at(x, z) or 0.02
    ob = fc.link_object(name, mesh, (x, z, ground + dims[2] * 0.5 + lift), coll,
                        rotation_z=yaw, scale=dims)
    if tilt != (0.0, 0.0):
        ob.rotation_euler = (tilt[0], tilt[1], yaw)
    return ob


def _paving_and_kerb(coll, tile_mesh, kerb_mesh, boxes, rng):
    placed = 0
    for spec in fc.SECTIONS:
        cx, cz = fc.section_center(spec)
        radius = fc.section_ring_radius(spec)
        appr = fc.approach_dir(cx, cz)
        appr_ang = math.atan2(appr.y, appr.x)
        perp = Vector((-appr.y, appr.x))
        across = 0.52 * SIZE_SCALE          # grid spacing scales with brick size
        along = 0.50 * SIZE_SCALE
        # threshold pad centre — just outside the ring on the approach side
        tx = cx + appr.x * (radius + 2.0)
        tz = cz + appr.y * (radius + 2.0)
        # 4 across x 3 deep flagstone grid
        for ci, col in enumerate(PAVE_COLS):
            for row in PAVE_ROWS:
                px = tx + perp.x * col * across + appr.x * row * along
                pz = tz + perp.y * col * across + appr.y * row * along
                if fc.valid(px, pz, [], boxes):
                    _put(coll, tile_mesh, f"brick_pave_{spec['key']}_{ci}{row}",
                         px, pz, TILE, rng, lift=-0.06, yaw=appr_ang)
                    placed += 1
        # kerb blocks capping each opening edge (2 per side along the ring)
        for side in (-1.0, 1.0):
            for j, frac in enumerate((0.32, 0.52)):
                ex = cx + perp.x * side * radius * frac + appr.x * radius
                ez = cz + perp.y * side * radius * frac + appr.y * radius
                if fc.valid(ex, ez, [], boxes):
                    _put(coll, kerb_mesh,
                         f"brick_kerb_{spec['key']}_{int(side)}_{j}",
                         ex, ez, KERB, rng, yaw=appr_ang)
                    placed += 1
    return placed


def _loose_piles(coll, pile_mesh, boxes, rng):
    cands = []
    for ang in range(0, 360, 23):
        for rad in (16, 26, 38):
            a = math.radians(ang)
            cands.append((round(rad * math.cos(a) + rng.uniform(-4, 4), 2),
                          round(rad * math.sin(a) + rng.uniform(-4, 4), 2)))
    rng.shuffle(cands)
    placed_pts = []
    bricks = 0
    piles = 0
    for (x, z) in cands:
        if piles >= PILE_COUNT:
            break
        if not fc.valid(x, z, placed_pts, boxes, 6.0):
            continue
        placed_pts.append((x, z))
        n = rng.randint(2, 4)
        spread = 0.22 * SIZE_SCALE          # jitter scales with brick size
        for k in range(n):
            jx = x + rng.uniform(-spread, spread)
            jz = z + rng.uniform(-spread, spread)
            _put(coll, pile_mesh, f"brick_pile_{piles:02d}_{k}", jx, jz, PILE, rng,
                 lift=k * PILE[2] * 0.8,
                 yaw=rng.uniform(0.0, math.tau),
                 tilt=(rng.uniform(-0.14, 0.14), rng.uniform(-0.14, 0.14)))
            bricks += 1
        piles += 1
    return piles, bricks


def run():
    print("[05-foliage-bricks] paved thresholds + kerb edging + loose piles")
    fc.remove_objects_with_prefix("brick_")
    coll = fc.get_collection(COLLECTION)
    boxes = fc.obstacle_boxes()
    rng = random.Random(SEED)

    tile_mesh = _unit_cube("brickPaveMesh", _SANDSTONE)
    kerb_mesh = _unit_cube("brickKerbMesh", _KERB_COLOR)
    pile_mesh = _unit_cube("brickPileMesh", _SANDSTONE)

    pk = _paving_and_kerb(coll, tile_mesh, kerb_mesh, boxes, rng)
    piles, pile_bricks = _loose_piles(coll, pile_mesh, boxes, rng)
    print(f"  {pk} paving+kerb bricks, {piles} piles ({pile_bricks} bricks) "
          f"-> collection '{COLLECTION}'")
    fc.save()


if __name__ == "__main__":
    run()
