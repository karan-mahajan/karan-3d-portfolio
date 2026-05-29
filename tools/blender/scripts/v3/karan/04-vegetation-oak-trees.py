"""Author Karan's Phase 4 oak trees — varied custom anchors, placed only on land.

Option A / Bruno-style: each oak is a low-poly ANCHOR body (brown trunk + green
canopy clusters); the detailed LEAVES are layered on in the Three.js runtime over
the green clusters. We build our own mesh (not Bruno's Plane.017) so we control
the trunk/canopy material split exactly and can vary the shape per tree.

Two requirements handled here:

1. VALID PLACEMENT — never water / ocean / bridge / rock. A candidate (x,z) is
   accepted only if:
     - terrain height there is on the flat land plateau or a hill (>= LAND_MIN);
       depressions (ponds/river) are carved below that, and ocean raycasts miss.
       Terrain height is ground truth — far more robust than the water EXR, whose
       screen-axis mapping is ambiguous.
     - it is not inside the XY bounding box (+margin) of any live bridge/rock/
       boulder/shard/basalt object in the scene (scanned at run time, so it works
       in your populated session even though those props aren't in every save).
     - it is >= MIN_SPACING from already-placed trees.
   Candidates are a deterministic jittered ring/grid; the first N valid, well-
   spread ones are kept. Re-running is deterministic (fixed SEED).

2. VARIED, ORGANIC SHAPE — every tree is its own mesh, generated from a per-tree
   random stream (seeded by index) so no two look alike: curved multi-segment
   trunk that leans, a different number/arrangement/size of canopy clusters, a
   different overall scale, and a small green-tint jitter.

Materials (two slots, edit either in Blender):
  slot 0 = oak_canopy_karan_NN (green)  slot 1 = oak_trunk_karan (brown)

    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/04-vegetation-oak-trees.py').read())
"""
import math
import random
import sys

import bmesh
import bpy
from mathutils import Vector, Quaternion

TOOLS_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts"
if TOOLS_DIR not in sys.path:
    sys.path.append(TOOLS_DIR)

BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"
OAK_COLLECTION = "vegetation/oakTrees"

TRUNK_MATERIAL = "oak_trunk_karan"
TRUNK_COLOR = (0.17, 0.09, 0.04, 1.0)        # dark brown
CANOPY_COLOR_BASE = (0.20, 0.40, 0.18, 1.0)  # leafy green (per-tree tint jitter)

SLOT_CANOPY = 0
SLOT_TRUNK = 1

# placement
TARGET_COUNT = 6
SEED = 7
MIN_SPACING = 11.0      # metres between trees
ISLAND_RADIUS = 52.0    # keep within walkable land
LAND_MIN = -0.05        # karan land plateau sits at height 0.0; ponds/river are
                        # carved to ~-0.6..-1.5 and ocean raycasts miss. Accept
                        # >= -0.05 so only the flat plateau passes (rejects all
                        # water + beach slopes). Verified: corr(R_water,h)=-0.998.
OBSTACLE_MARGIN = 1.6   # metres of clearance around bridges/rocks
OBSTACLE_KEYS = ("bridge", "basalt", "boulder", "shard", "rock", "sectionfootprint", "sectionmarker")

# bias trees toward these friendly anchors (slabs + bonfire) so the scatter
# clusters around the lived-in areas; purely a sort preference, not a gate.
FRIENDLY_SPOTS = [(18.0, -10.9), (-1.1, -10.2), (-2.6, 17.3), (9.5, 6.5)]


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
        return None  # off-terrain = ocean
    return (terr.matrix_world @ loc).z


def _obstacle_boxes():
    boxes = []
    for o in bpy.data.objects:
        if o.type != 'MESH':
            continue
        n = o.name.lower()
        if not any(k in n for k in OBSTACLE_KEYS):
            continue
        cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
        xs = [c.x for c in cs]; ys = [c.y for c in cs]
        boxes.append((min(xs) - OBSTACLE_MARGIN, max(xs) + OBSTACLE_MARGIN,
                      min(ys) - OBSTACLE_MARGIN, max(ys) + OBSTACLE_MARGIN))
    return boxes


def _valid(x, z, placed, boxes):
    if math.hypot(x, z) > ISLAND_RADIUS:
        return False
    h = _height_at(x, z)
    if h is None or h < LAND_MIN:        # ocean or carved water/river/pond
        return False
    for (xmin, xmax, ymin, ymax) in boxes:   # bridge / rock footprint
        if xmin <= x <= xmax and ymin <= z <= ymax:
            return False
    for (px, pz) in placed:
        if math.hypot(x - px, z - pz) < MIN_SPACING:
            return False
    return True


def _candidates(rng):
    pts = []
    for ang in range(0, 360, 12):
        for rad in (14, 20, 27, 34, 41, 48):
            a = math.radians(ang)
            x = rad * math.cos(a) + rng.uniform(-3, 3)
            z = rad * math.sin(a) + rng.uniform(-3, 3)
            pts.append((round(x, 2), round(z, 2)))
    rng.shuffle(pts)
    # prefer candidates closer to a friendly spot (slabs / bonfire)
    def closeness(p):
        return min(math.hypot(p[0] - fx, p[1] - fz) for fx, fz in FRIENDLY_SPOTS)
    pts.sort(key=closeness)
    return pts


def _solid_material(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = 0.8
    return mat


def _curved_trunk(bm, rng, plan, height):
    """Multi-segment trunk that leans/curves for an organic silhouette."""
    segs = rng.randint(4, 6)
    lean = Vector((rng.uniform(-0.25, 0.25), rng.uniform(-0.25, 0.25), 0.0))
    pos = Vector((0.0, 0.0, 0.0))
    base_r = rng.uniform(0.20, 0.26)
    seg_h = height / segs
    tip = Vector((0.0, 0.0, 0.0))
    for i in range(segs):
        t = i / segs
        r0 = base_r * (1.0 - 0.55 * t)
        r1 = base_r * (1.0 - 0.55 * (t + 1.0 / segs))
        # curve: accumulate lean, with a gentle sway
        sway = Vector((math.sin(t * 3.1 + rng.random()) * 0.12,
                       math.cos(t * 2.7 + rng.random()) * 0.12, 0.0))
        step = lean * seg_h + sway * seg_h
        nxt = pos + Vector((step.x, step.y, seg_h))
        mid = (pos + nxt) * 0.5
        axis = (nxt - pos)
        res = bmesh.ops.create_cone(bm, cap_ends=True, segments=6,
                                    radius1=r0, radius2=r1, depth=axis.length)
        quat = Vector((0, 0, 1)).rotation_difference(axis.normalized())
        vs = res["verts"]
        for v in vs:
            v.co = quat @ v.co
            v.co += mid
        faces = set()
        for v in vs:
            faces.update(v.link_faces)
        plan.extend([(f, SLOT_TRUNK) for f in faces])
        pos = nxt
        tip = nxt
    return tip  # crown sits on the trunk tip


def _branch(bm, start, vec, radius, plan):
    end = start + vec
    mid = (start + end) * 0.5
    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=5,
                                radius1=radius, radius2=radius * 0.6, depth=vec.length)
    quat = Vector((0, 0, 1)).rotation_difference(vec.normalized())
    vs = res["verts"]
    for v in vs:
        v.co = quat @ v.co
        v.co += mid
    faces = set()
    for v in vs:
        faces.update(v.link_faces)
    plan.extend([(f, SLOT_TRUNK) for f in faces])
    return end


def _cluster(bm, center, radius, plan):
    res = bmesh.ops.create_uvsphere(bm, u_segments=7, v_segments=5, radius=radius)
    vs = res["verts"]
    for v in vs:
        # squash slightly + jitter for an irregular, organic clump
        v.co.z *= 0.85
        v.co += Vector(center)
    faces = set()
    for v in vs:
        faces.update(v.link_faces)
    plan.extend([(f, SLOT_CANOPY) for f in faces])


def _build_oak_mesh(index, trunk_mat):
    rng = random.Random(SEED * 1000 + index)
    name = f"oakBody_{index:02d}"
    me = bpy.data.meshes.get(name)
    if me is not None:
        bpy.data.meshes.remove(me)
    me = bpy.data.meshes.new(name)

    # per-tree canopy tint jitter
    j = lambda base, d: max(0.0, min(1.0, base + rng.uniform(-d, d)))
    canopy_color = (j(CANOPY_COLOR_BASE[0], 0.04),
                    j(CANOPY_COLOR_BASE[1], 0.06),
                    j(CANOPY_COLOR_BASE[2], 0.04), 1.0)
    canopy_mat = _solid_material(f"oak_canopy_karan_{index:02d}", canopy_color)

    bm = bmesh.new()
    plan = []

    trunk_h = rng.uniform(2.6, 3.6)
    tip = _curved_trunk(bm, rng, plan, trunk_h)

    # a few branches fanning from near the tip
    nb = rng.randint(2, 4)
    for _ in range(nb):
        ang = rng.uniform(0, math.tau)
        vec = Vector((math.cos(ang), math.sin(ang), rng.uniform(0.7, 1.2))) * rng.uniform(0.9, 1.5)
        _branch(bm, tip + Vector((0, 0, rng.uniform(-0.3, 0.2))), vec, rng.uniform(0.08, 0.12), plan)

    # canopy: varied number/size/placement of clumps centred over the tip
    ncl = rng.randint(4, 7)
    crown_z = tip.z + rng.uniform(0.8, 1.3)
    spread = rng.uniform(0.7, 1.1)
    for _ in range(ncl):
        cx = tip.x + rng.uniform(-spread, spread)
        cy = tip.y + rng.uniform(-spread, spread)
        cz = crown_z + rng.uniform(-0.3, 0.9)
        r = rng.uniform(0.7, 1.4)
        _cluster(bm, (cx, cy, cz), r, plan)

    bm.faces.index_update()
    slot_by_index = {f.index: slot for f, slot in plan}
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()

    me.materials.clear()
    me.materials.append(canopy_mat)   # slot 0
    me.materials.append(trunk_mat)    # slot 1
    for p in me.polygons:
        p.material_index = slot_by_index.get(p.index, SLOT_CANOPY)
    return me


def _collection():
    name = OAK_COLLECTION.split("/")[-1]
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll


def _cleanup_old_oaks():
    """Remove leftover oak objects/meshes from earlier runs (boxy versions,
    extra count, preview trees) so re-running leaves a clean set."""
    n_obj = 0
    for o in list(bpy.data.objects):
        nm = o.name.lower()
        if nm.startswith("oak_") or nm.startswith("oak.") or nm == "oak" \
           or "oak_demo" in nm or "tree_preview" in nm or nm.startswith("oakbody"):
            bpy.data.objects.remove(o, do_unlink=True)
            n_obj += 1
    n_mesh = 0
    for m in list(bpy.data.meshes):
        if m.name.lower().startswith("oakbody") and m.users == 0:
            bpy.data.meshes.remove(m)
            n_mesh += 1
    print(f"  cleaned up {n_obj} old oak objects, {n_mesh} orphan meshes")


def run():
    print("[04-vegetation-oak-trees] place varied oak anchors on valid land only")
    rng = random.Random(SEED)
    trunk_mat = _solid_material(TRUNK_MATERIAL, TRUNK_COLOR)
    coll = _collection()
    _cleanup_old_oaks()

    boxes = _obstacle_boxes()
    print(f"  obstacle footprints found (bridge/rock): {len(boxes)}")

    placed = []
    cands = _candidates(rng)
    chosen = []
    for (x, z) in cands:
        if len(chosen) >= TARGET_COUNT:
            break
        if _valid(x, z, placed, boxes):
            placed.append((x, z))
            chosen.append((x, z))

    if len(chosen) < TARGET_COUNT:
        print(f"  [WARN] only {len(chosen)}/{TARGET_COUNT} valid spots found "
              f"(island may be crowded); placing what we have")

    built = []
    for i, (x, z) in enumerate(chosen):
        ground = _height_at(x, z) or 0.02
        mesh = _build_oak_mesh(i, trunk_mat)
        nm = f"oak_{i:02d}"
        ob = bpy.data.objects.get(nm)
        if ob is None:
            ob = bpy.data.objects.new(nm, mesh)
        else:
            ob.data = mesh
        ob.location = (x, z, ground)
        ob.rotation_mode = "XYZ"
        ob.rotation_euler = (0.0, 0.0, random.Random(SEED * 99 + i).uniform(0, math.tau))
        s = random.Random(SEED * 5 + i).uniform(0.85, 1.2)
        ob.scale = (s, s, s)
        ob["phase"] = "04-vegetation"
        if ob.name not in {o.name for o in coll.objects}:
            coll.objects.link(ob)
        built.append(ob)
        print(f"  {nm}: ({x:.1f},{z:.1f},{ground:.3f}) scale={s:.2f}")

    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")
    print(f"  placed {len(built)} distinct oaks (all on land; leaves added in Three.js)")


if __name__ == "__main__":
    run()
