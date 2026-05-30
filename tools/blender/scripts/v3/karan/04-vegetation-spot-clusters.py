"""Author Karan's hand-picked tree clusters — extra trees at 17 curated map
points (3D-cursor locations), on grass only, gap-spaced, never overlapping an
existing tree / rock / structure / prop.

Each CLUSTER is a world (x, z) the user marked plus a tree count. This script
scatters `count` trees around that point and MIXES species (cherry / birch /
oak), reusing the exact builders from the sibling section-04 scripts so the new
trees are visually identical and carry the same colliders + foliage leaf-anchor
refs + collection membership. Section 15 (finalize) then wires them under the
existing root_cherryTrees / root_birchTrees / root_oakTrees like every other tree.

Placement rules (per the request):
  - GRASS ONLY: terrain height there must be on the land plateau (>= LAND_MIN);
    ponds / river / lava are carved below that and ocean raycasts miss.
  - NO OVERLAP: every tree stays >= a per-cluster GAP from any other tree (new
    or pre-existing) and >= CLEARANCE from the XY bbox of any rock / structure /
    prop already in the scene.
  - GAP ADAPTS TO THE AREA: probed from the nearest non-tree prop — open spots
    get a wide ~4.5 m spread, medium ~2.5 m, tight ~1.3 m.

Runs LAST among the 04-vegetation-* scripts (filename sorts after -oak-) so the
obstacle scan already sees the oak / cherry / birch trees placed earlier.

    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/04-vegetation-spot-clusters.py').read())
"""
import importlib.util
import math
import os
import random

import bpy
from mathutils import Vector

KARAN_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan"

LAND_MIN = -0.05          # land plateau ~0.0; water/lava carved below; ocean misses
CLEARANCE = 1.1           # metres a trunk must keep from any prop's XY bbox
SEED = 41

# Curated points (world x, z) + how many trees the user asked for there.
CLUSTERS = [
    {"xz": (42.06, -13.66), "count": 4},
    {"xz": (45.48,  12.54), "count": 2},
    {"xz": (11.05,   9.52), "count": 1},
    {"xz": (-45.33, 20.43), "count": 6},
    {"xz": (-26.91, -5.96), "count": 2},
    {"xz": (-24.24, 48.57), "count": 4},
    {"xz": (28.06,  50.22), "count": 2},
    {"xz": (-15.75, 29.12), "count": 3},
    {"xz": (-47.76, -38.29), "count": 1},
    {"xz": (45.56, -45.95), "count": 2},
    {"xz": (22.61, -48.35), "count": 2},
    {"xz": (-16.39, -46.87), "count": 2},
    {"xz": (-25.67,  7.22), "count": 2},
    {"xz": (-0.58, -29.17), "count": 2},
    {"xz": (-45.61, -46.56), "count": 1},
    {"xz": (49.61,  46.19), "count": 1},
    {"xz": (-43.78, -3.80), "count": 1},
]

SPECIES = ("cherry", "birch", "oak")

# names that mark an obstacle to KEEP CLEAR OF (props, rocks, structures) — used
# as XY bounding boxes. Trees themselves are handled separately (gap spacing).
PROP_KEYS = (
    "rock", "basalt", "boulder", "shard", "bridge", "slab",
    "cabin", "outhouse", "statue", "projecthut", "contactboard", "skillsphere",
    "controls", "playstation", "bonfire", "bench", "lantern", "lightpole",
    "pole_light", "brick", "fence", "lava", "footprint", "sectionmarker",
)
TREE_NAME_HINTS = ("tree", "oak_", "oakbody")  # existing trees -> spacing, not bbox


def _load(filename):
    path = os.path.join(KARAN_DIR, filename)
    name = "_clustermod_" + os.path.splitext(filename)[0].replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _terrain():
    return bpy.data.objects.get("terrain") or bpy.data.objects.get("terrain_mesh")


def _height_at(x, z):
    terr = _terrain()
    if terr is None:
        return 0.02
    inv = terr.matrix_world.inverted()
    o = inv @ Vector((x, z, 80.0))
    d = inv.to_3x3() @ Vector((0.0, 0.0, -1.0))
    ok, loc, _n, _i = terr.ray_cast(o, d)
    if not ok:
        return None
    return (terr.matrix_world @ loc).z


def _world_matrix(o):
    """True world matrix computed from matrix_basis + matrix_parent_inverse up
    the parent chain. Both are always current (unlike matrix_world / the
    evaluated depsgraph, which stay stale in --background mid-build), so this is
    correct for BOTH unparented objects and props parented during their build."""
    if o.parent is None:
        return o.matrix_basis.copy()
    return _world_matrix(o.parent) @ o.matrix_parent_inverse @ o.matrix_basis


def _prop_boxes():
    """XY bboxes of existing rocks/structures/props (NOT trees)."""
    boxes = []
    for o in bpy.data.objects:
        if o.type != 'MESH':
            continue
        n = o.name.lower()
        if any(t in n for t in TREE_NAME_HINTS):
            continue
        if not any(k in n for k in PROP_KEYS):
            continue
        mw = _world_matrix(o)
        cs = [mw @ Vector(c) for c in o.bound_box]
        xs = [c.x for c in cs]
        ys = [c.y for c in cs]
        boxes.append((min(xs), max(xs), min(ys), max(ys)))
    return boxes


def _existing_tree_xy():
    """World XY of every tree already in the scene (for gap spacing)."""
    pts = []
    for o in bpy.data.objects:
        if o.type != 'MESH':
            continue
        n = o.name.lower()
        if ("_tree_" in n or n.startswith("tree_") or n.startswith("oak_")
                or "cherry_tree" in n or "birch" in n) and "tube_" not in n \
                and "leaves" not in n:
            w = _world_matrix(o).translation
            pts.append((w.x, w.y))
    return pts


def _box_dist(x, z, box):
    xmin, xmax, ymin, ymax = box
    dx = max(xmin - x, 0.0, x - xmax)
    dy = max(ymin - z, 0.0, z - ymax)
    return math.hypot(dx, dy)


def _on_grass(x, z):
    h = _height_at(x, z)
    return h is not None and h >= LAND_MIN


def _clear_of_props(x, z, boxes):
    return all(_box_dist(x, z, b) >= CLEARANCE for b in boxes)


def _adaptive_gap(cx, cz, boxes):
    """Wider spread where the spot is open, tighter where props crowd it."""
    nd = min((_box_dist(cx, cz, b) for b in boxes), default=99.0)
    if nd > 7.0:
        return 4.5
    if nd > 4.0:
        return 2.5
    return 1.3


def _scatter(cx, cz, count, gap, boxes, tree_xy, rng):
    """Return up to `count` accepted (x, z) around (cx, cz)."""
    chosen = []
    # candidate ring set: centre first, then expanding rings of jittered points
    cands = [(cx, cz)]
    for ring in range(1, 7):
        r = gap * ring
        steps = max(8, int(r * 2.2))
        for k in range(steps):
            a = (k / steps) * math.tau + rng.uniform(-0.18, 0.18)
            cands.append((cx + r * math.cos(a) + rng.uniform(-0.4, 0.4),
                          cz + r * math.sin(a) + rng.uniform(-0.4, 0.4)))
    for (x, z) in cands:
        if len(chosen) >= count:
            break
        if not _on_grass(x, z):
            continue
        if not _clear_of_props(x, z, boxes):
            continue
        if any(math.hypot(x - px, z - pz) < gap for px, pz in chosen):
            continue
        if any(math.hypot(x - tx, z - tz) < gap for tx, tz in tree_xy):
            continue
        chosen.append((round(x, 3), round(z, 3)))
    return chosen


def run():
    print("[04-vegetation-spot-clusters] place curated tree clusters on grass")
    # earlier scripts placed trees/props this run; flush so matrix_world (used by
    # the obstacle bbox scan + existing-tree spacing) is current, not stale-at-origin.
    bpy.context.view_layer.update()
    cherry = _load("04-vegetation-cherry-trees.py")
    birch = _load("04-vegetation-birch-trees.py")
    oak = _load("04-vegetation-oak-trees.py")
    cherry_mats = cherry._materials()
    birch_mats = birch._materials()
    oak_trunk = oak._solid_material(oak.TRUNK_MATERIAL, oak.TRUNK_COLOR)
    oak_coll = oak._collection()

    boxes = _prop_boxes()
    tree_xy = _existing_tree_xy()
    print(f"  obstacle props={len(boxes)}  existing trees={len(tree_xy)}")

    rng = random.Random(SEED)
    built = 0
    per_species = {"cherry": 0, "birch": 0, "oak": 0}
    for ci, cluster in enumerate(CLUSTERS):
        cx, cz = cluster["xz"]
        want = cluster["count"]
        gap = _adaptive_gap(cx, cz, boxes)
        spots = _scatter(cx, cz, want, gap, boxes, tree_xy, rng)
        if len(spots) < want:
            print(f"  [c{ci:02d}] ({cx:.1f},{cz:.1f}) gap={gap:.1f}m: only "
                  f"{len(spots)}/{want} fit (crowded) ")
        else:
            print(f"  [c{ci:02d}] ({cx:.1f},{cz:.1f}) gap={gap:.1f}m: {len(spots)} tree(s)")
        for ti, (x, z) in enumerate(spots):
            species = SPECIES[built % 3]   # even round-robin across all trees
            key = f"cluster_{ci:02d}_{ti}"
            yaw = rng.uniform(0.0, math.tau)
            scale = round(rng.uniform(0.85, 1.18), 3)
            variant = (ci + ti) % 4
            if species == "cherry":
                cherry._build_tree(
                    {"key": key, "object": f"cherry_tree_{key}", "location": (x, z),
                     "yaw": yaw, "scale": scale, "variant": variant}, cherry_mats)
            elif species == "birch":
                birch._build_birch(
                    {"key": key, "object": f"tree_birch_karan_{key}", "location": (x, z),
                     "yaw": yaw, "scale": scale, "variant": variant}, birch_mats)
            else:
                idx = 100 + ci * 10 + ti
                mesh = oak._build_oak_mesh(idx, oak_trunk)
                nm = f"oak_{key}"
                ob = bpy.data.objects.get(nm) or bpy.data.objects.new(nm, mesh)
                ob.data = mesh
                ob.location = (x, z, _height_at(x, z) or 0.02)
                ob.rotation_mode = "XYZ"
                ob.rotation_euler = (0.0, 0.0, yaw)
                ob.scale = (scale, scale, scale)
                ob["phase"] = "04-vegetation"
                if ob.name not in {o.name for o in oak_coll.objects}:
                    oak_coll.objects.link(ob)
            per_species[species] += 1
            tree_xy.append((x, z))   # later clusters avoid this one too
            built += 1

    print(f"  built {built} cluster tree(s): "
          f"cherry={per_species['cherry']} birch={per_species['birch']} oak={per_species['oak']}")


if __name__ == "__main__":
    run()
