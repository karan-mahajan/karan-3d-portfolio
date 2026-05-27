"""
Phase 11C: Foliage references for runtime SDF-quad foliage.

Run after phase-11-foliage.py (and optionally phase-11b-better-trees.py) and
before phase-13-export-glb.py:

  Blender --background tools/blender/world.blend \
    --python tools/blender/scripts/phase-11c-foliage-refs.py

This pass switches the project from baked canopies to Bruno-Simon style
runtime foliage:

  1. Rebuilds each shared variant source mesh as TRUNK + BRANCHES ONLY
     (`tree_pine_var_1..10_src_mesh`, `tree_birch_var_1..5_src_mesh`,
     `tree_hero_pine_src_mesh`). Canopy geometry is dropped — the runtime
     spawns it as SDF-alpha quads instead.
  2. Empties out `gc_bush_var_1..4_src_mesh` (bushes are 100% canopy →
     pure runtime).
  3. Emits one `refTreeLeaves_<inst_name>` / `refBushLeaves_<inst_name>`
     empty per instance at the canopy's world centre, scaled to the
     canopy radius. The runtime `Foliage.js` reads these refs.

Custom property `species` on each ref tells the runtime which pair of
two-tone colors to use ("pine" / "birch" / "hero" / "bush").

Everything else (instance count, positions, rotations, scales, collections,
push-spot detection, hero refs, colliders) is preserved.
"""

from __future__ import annotations

import argparse
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector


def _script_dir():
    candidates = []
    if "__file__" in globals():
        candidates.append(os.path.dirname(os.path.abspath(__file__)))
    blend_path = bpy.data.filepath
    if blend_path:
        blend_dir = os.path.dirname(os.path.abspath(blend_path))
        candidates.append(os.path.join(blend_dir, "scripts"))
        candidates.append(blend_dir)
    candidates.append(os.getcwd())
    candidates.append(os.path.join(os.getcwd(), "tools", "blender", "scripts"))
    for path in candidates:
        if os.path.isfile(os.path.join(path, "_lib.py")):
            return path
    raise RuntimeError("Could not locate _lib.py - tried: " + ", ".join(candidates))


SCRIPT_DIR = _script_dir()
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import _lib  # noqa: E402


PINE_MESHES = [f"tree_pine_var_{i}_src_mesh" for i in range(1, 11)]
BIRCH_MESHES = [f"tree_birch_var_{i}_src_mesh" for i in range(1, 6)]
HERO_MESH = "tree_hero_pine_src_mesh"
BUSH_MESHES = [f"gc_bush_var_{i}_src_mesh" for i in range(1, 5)]

TRUNK = "wood_lantern_body"
BIRCH_BARK = "sunlit_snow"
SHADE = "deep_shade"


# Per-variant canopy geometry. `trunk_top` is the Blender-Z where the trunk
# stops and the canopy begins. `canopy_center` is the local-Z of the canopy's
# centre (used to place the ref empty), `canopy_radius` is the radius the
# runtime quad sphere should spawn at scale=1. Numbers mirror phase-11b's
# specs so per-variant silhouettes still differ.
PINE_VARIANTS = [
    # (trunk_top, canopy_center, canopy_radius, height)
    dict(trunk_top=0.92, canopy_center=2.55, canopy_radius=1.10, height=4.2),
    dict(trunk_top=1.06, canopy_center=2.95, canopy_radius=1.20, height=4.8),
    dict(trunk_top=1.17, canopy_center=3.25, canopy_radius=1.30, height=5.3),
    dict(trunk_top=1.67, canopy_center=4.65, canopy_radius=1.10, height=7.6),
    dict(trunk_top=0.84, canopy_center=2.30, canopy_radius=1.65, height=3.8),
    dict(trunk_top=1.28, canopy_center=3.55, canopy_radius=1.40, height=5.8),
    dict(trunk_top=1.39, canopy_center=3.85, canopy_radius=1.55, height=6.3),
    dict(trunk_top=1.06, canopy_center=2.95, canopy_radius=1.20, height=4.8),
    dict(trunk_top=1.19, canopy_center=3.30, canopy_radius=1.35, height=5.4),
    dict(trunk_top=1.14, canopy_center=3.20, canopy_radius=1.30, height=5.2),
]
# Per-variant leaf cluster strategy. The runtime spawns ONE quad-sphere
# foliage cloud per refTreeLeaves_* empty. Bruno's trick is to have many
# small clouds (one per branch tip) instead of one big cloud per tree —
# that's what makes his pines read as "real trees" instead of "ball on a
# stick". Per-variant settings here let some trees be sparse (variant 4,
# tall thin) while others are dense (variant 7, bushy fir).
#
# CORE_PROB: chance of an extra big "core" cluster at canopy centre.
# BRANCH_CLUSTER_RATIO: leaf radius as a fraction of canopy radius per
# branch tip. Smaller ratio = wispier per-branch puffs.
PINE_CORE_PROB        = [0.9, 0.9, 0.9, 0.7, 0.0, 0.6, 0.0, 0.9, 0.7, 0.8]
PINE_CORE_RADIUS      = [0.55, 0.55, 0.55, 0.45, 0.0,  0.50, 0.0,  0.55, 0.50, 0.55]
PINE_BRANCH_LEAF_R    = [0.32, 0.32, 0.34, 0.26, 0.40, 0.34, 0.42, 0.32, 0.34, 0.34]

# `LEAF_ANCHORS_PER_VARIANT` is populated as each src_mesh's trunk is built.
# Maps src_mesh_name → list of (local_x, local_y, local_z, leaf_radius).
# Read later by _emit_tree_leaf_refs to spawn one empty per anchor.
LEAF_ANCHORS_PER_VARIANT = {}

# Per-variant trunk thickness + style. `branches` is how many angled branch
# stubs sprout inside the canopy volume. `style` keys: 'standard', 'tall',
# 'squat', 'lean', 'bushy', 'forked'. Widened so the 10 pine variants don't
# all read as the same pole.
PINE_TRUNK_R = [
    0.10,  # 1 — classic slim
    0.11,  # 2 — slightly thicker
    0.12,  # 3 — broader
    0.09,  # 4 — tall thin
    0.18,  # 5 — squat fat christmas tree
    0.13,  # 6 — leaning
    0.16,  # 7 — bushy fir
    0.11,  # 8 — autumn
    0.13,  # 9 — deep-shade dark
    0.12,  # 10 — meadow
]
PINE_BRANCH_COUNT = [5, 6, 7, 4, 9, 6, 10, 5, 6, 7]
PINE_BRANCH_SPREAD = [0.65, 0.72, 0.78, 0.42, 0.95, 0.78, 0.92, 0.68, 0.70, 0.74]
# Low branches that sprout near the trunk BASE (below the canopy). Adds the
# "stems coming from the middle, then from the top" feel the user asked for.
PINE_LOW_BRANCHES = [1, 2, 2, 1, 3, 2, 3, 1, 2, 2]
# Variants that get a multi-stem (2-3 trunks from a shared base).
PINE_MULTI_STEM_PROB = [0.0, 0.0, 0.3, 0.0, 0.65, 0.45, 0.55, 0.0, 0.35, 0.25]

BIRCH_VARIANTS = [
    # (trunk_top, canopy_center, canopy_radius, branch_count, lean)
    dict(trunk_top=5.20, canopy_center=5.40, canopy_radius=1.10, branch_count=4, lean=0.00),
    dict(trunk_top=3.80, canopy_center=4.00, canopy_radius=0.95, branch_count=3, lean=0.06),
    dict(trunk_top=4.50, canopy_center=4.70, canopy_radius=1.05, branch_count=4, lean=0.26),
    dict(trunk_top=5.00, canopy_center=5.20, canopy_radius=1.15, branch_count=5, lean=0.00),
    dict(trunk_top=4.00, canopy_center=4.20, canopy_radius=0.85, branch_count=2, lean=-0.14),
]
BIRCH_TRUNK_R = [0.10, 0.13, 0.09, 0.14, 0.08]
BIRCH_FORK_PROB = [0.0, 0.0, 0.65, 0.45, 0.85]  # variant 3,4,5 are multi-stem

HERO_VARIANT = dict(trunk_top=2.42, canopy_center=6.71, canopy_radius=2.55,
                    trunk_radius=0.58, height=11.0)

# Bushes don't have a trunk — the empty mesh is enough. One ref empty per
# instance at bush-centre. Radius matches `_build_bush_variant_source` average
# (2..4 clumps stacked ~0.18..0.30m → roughly 0.45m total spread).
BUSH_CANOPY_CENTER = 0.32
BUSH_CANOPY_RADIUS = 0.42


# ============================================================================
# Trunk-only source mesh builders.
# ============================================================================


def _add_tapered_cylinder(bm, uv, z0, z1, r0, r1, key, segments=10,
                          x0=0.0, y0=0.0, x1=0.0, y1=0.0):
    verts0 = []
    verts1 = []
    for i in range(segments):
        a = (i / segments) * math.tau
        ca = math.cos(a)
        sa = math.sin(a)
        verts0.append(bm.verts.new((x0 + ca * r0, y0 + sa * r0, z0)))
        verts1.append(bm.verts.new((x1 + ca * r1, y1 + sa * r1, z1)))

    for i in range(segments):
        j = (i + 1) % segments
        f = bm.faces.new((verts0[i], verts1[i], verts1[j], verts0[j]))
        _lib.paint_face(f, uv, key)
    try:
        cap0 = bm.faces.new(list(reversed(verts0)))
        _lib.paint_face(cap0, uv, SHADE)
    except ValueError:
        pass
    try:
        cap1 = bm.faces.new(verts1)
        _lib.paint_face(cap1, uv, key)
    except ValueError:
        pass


def _add_branch(bm, uv, start, direction, length, radius, key,
                segments=6, curvature=0.0, curve_axis=None,
                length_segments=1):
    """Add a tapered branch from `start` along `direction` for `length` meters.

    When `curvature == 0` and `length_segments == 1` this is the legacy
    straight tapered cylinder. When `curvature != 0` or `length_segments > 1`
    the branch becomes a multi-ring curved tube — each ring shifted along
    `curve_axis` by `t^2 * curvature * length`. Positive curvature bends in
    the +curve_axis direction; negative bends the opposite way.

    If `curve_axis` is None, a sensible perpendicular axis is computed.
    Returns the tip Vector.
    """
    sx, sy, sz = start
    d = Vector(direction)
    if d.length < 0.001:
        d = Vector((1.0, 0.0, 0.2))
    d.normalize()

    # Resolve curve_axis: pick a direction perpendicular to `d` so the branch
    # bends "sideways" not along its own length.
    if curve_axis is None:
        candidate = d.cross(Vector((0.0, 0.0, 1.0)))
        if candidate.length < 0.001:
            candidate = Vector((1.0, 0.0, 0.0))
        curve_axis = candidate.normalized()
    else:
        curve_axis = Vector(curve_axis)
        if curve_axis.length > 0.001:
            curve_axis = curve_axis.normalized()
        else:
            curve_axis = Vector((1.0, 0.0, 0.0))

    n_rings = max(2, length_segments + 1)
    rings = []     # list of list-of-verts per ring
    tangents = []  # local tangent at each ring center

    prev_pos = None
    for ri in range(n_rings):
        t = ri / (n_rings - 1)
        pos = Vector((sx, sy, sz)) + d * (t * length)
        # Quadratic bend: rings drift in curve_axis as t increases.
        pos = pos + curve_axis * (curvature * (t * t) * length)
        # Local tangent: difference to previous ring (or `d` for the first).
        if prev_pos is None:
            tangent = d.copy()
        else:
            tangent = (pos - prev_pos)
            if tangent.length < 0.001:
                tangent = d.copy()
            else:
                tangent.normalize()
        tangents.append(tangent)

        # Local frame for the ring.
        up = Vector((0.0, 0.0, 1.0))
        side = tangent.cross(up)
        if side.length < 0.001:
            side = Vector((1.0, 0.0, 0.0))
        side.normalize()
        side2 = tangent.cross(side).normalized()

        # Taper: base → 55% of base at tip, smoothly.
        r_t = radius * (1.0 - 0.45 * t)

        verts = []
        for i in range(segments):
            a = (i / segments) * math.tau
            offset = side * (math.cos(a) * r_t) + side2 * (math.sin(a) * r_t)
            verts.append(bm.verts.new(pos + offset))
        rings.append(verts)
        prev_pos = pos

    # Connect successive rings into quads.
    for ri in range(n_rings - 1):
        ring_a = rings[ri]
        ring_b = rings[ri + 1]
        for i in range(segments):
            j = (i + 1) % segments
            f = bm.faces.new((ring_a[i], ring_b[i], ring_b[j], ring_a[j]))
            _lib.paint_face(f, uv, key)

    return prev_pos


def _build_pine_trunk(idx, variant):
    """Pine: trunk extends THROUGH the canopy (no gap) + branches at MULTIPLE
    levels — base, mid-trunk, and inside-canopy — plus optional multi-stem
    siblings for some variants. Sub-branch forks on ~25-30% of primary
    branches for additional silhouette break.

    Returns (bmesh, leaf_anchors). leaf_anchors is a list of
    (local_x, local_y, local_z, leaf_radius) — one entry per leaf cluster
    we want at runtime. Variants without a "core" cluster (5, 7) only put
    leaves at branch tips, so the silhouette reads as a cluster of puffs
    rather than a single sphere.
    """
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)

    rng = random.Random(f"pine-trunk:{idx}")

    r = PINE_TRUNK_R[idx]
    bare_top = variant["trunk_top"]
    canopy_c = variant["canopy_center"]
    canopy_r = variant["canopy_radius"]

    # Trunk pokes through canopy, ending just past the top — like a real leader.
    trunk_total = canopy_c + canopy_r * 0.50
    # Slight root flare: an extra-thick base for the bottom 0.4m.
    base_r = r * 1.55
    flare_top_r = r * 1.20
    flare_z = min(0.42, trunk_total * 0.18)
    _add_tapered_cylinder(
        bm, uv,
        z0=0.0, z1=flare_z,
        r0=base_r, r1=flare_top_r,
        key=TRUNK, segments=12,
    )
    # Main trunk: flare_top → leader top.
    _add_tapered_cylinder(
        bm, uv,
        z0=flare_z, z1=trunk_total,
        r0=flare_top_r, r1=r * 0.28,
        key=TRUNK, segments=11,
    )

    # Optional multi-stem: 1-2 sibling trunks growing from the flare base.
    sibling_trunks = []
    if rng.random() < PINE_MULTI_STEM_PROB[idx]:
        n_sibs = 1 + (1 if rng.random() < 0.4 else 0)
        for s in range(n_sibs):
            a = rng.random() * math.tau
            off_r = r * (1.6 + rng.random() * 0.6)
            sx = math.cos(a) * off_r
            sy = math.sin(a) * off_r
            s_height = trunk_total * (0.65 + rng.random() * 0.25)
            s_base_r = r * (0.62 + rng.random() * 0.18)
            s_lean_x = sx * 0.35
            s_lean_y = sy * 0.35
            _add_tapered_cylinder(
                bm, uv,
                z0=0.0, z1=s_height,
                r0=s_base_r * 1.25, r1=s_base_r * 0.30,
                key=TRUNK, segments=10,
                x0=sx, y0=sy,
                x1=sx + s_lean_x, y1=sy + s_lean_y,
            )
            sibling_trunks.append((sx + s_lean_x, sy + s_lean_y, s_height, s_base_r))

    # Low branches: 1-3 short branches near the BASE (below the canopy).
    low_branch_count = PINE_LOW_BRANCHES[idx]
    for i in range(low_branch_count):
        z = flare_z + 0.12 + i * (max(0.08, bare_top - flare_z) / max(1, low_branch_count))
        z += rng.uniform(-0.08, 0.10)
        if z > bare_top - 0.05:
            z = bare_top - 0.10
        angle = rng.random() * math.tau
        reach = canopy_r * 0.22 + rng.random() * 0.18
        direction = (
            math.cos(angle) * 0.78,
            math.sin(angle) * 0.78,
            -0.08 + rng.random() * 0.18,
        )
        _add_branch(
            bm, uv,
            start=(rng.uniform(-0.02, 0.02), rng.uniform(-0.02, 0.02), z),
            direction=direction,
            length=reach,
            radius=r * 0.32 + 0.005,
            key=TRUNK,
            segments=5,
        )

    # Collect leaf anchors as we build branches.
    anchors = []  # (lx, ly, lz, leaf_radius)
    branch_leaf_r = canopy_r * PINE_BRANCH_LEAF_R[idx]

    # Optional CORE cluster — a bigger leaf puff at canopy centre. Variants
    # 5 and 7 (squat fat, bushy fir) skip this so the silhouette is broken
    # into pure branch-tip puffs.
    if rng.random() < PINE_CORE_PROB[idx]:
        core_r = canopy_r * PINE_CORE_RADIUS[idx]
        anchors.append((0.0, 0.0, canopy_c, core_r))

    # Primary canopy branches: stagger through the canopy volume. Each branch
    # has its OWN curvature so the tree skeleton reads organic, not a stack
    # of straight cones.
    branch_count = PINE_BRANCH_COUNT[idx]
    spread = PINE_BRANCH_SPREAD[idx]
    canopy_bottom = max(bare_top - 0.10, canopy_c - canopy_r * 0.85)
    canopy_top    = canopy_c + canopy_r * 0.40
    for i in range(branch_count):
        t = i / max(1, branch_count - 1)
        z = canopy_bottom + (canopy_top - canopy_bottom) * (0.05 + pow(t, 0.65) * 0.92)
        angle = i * math.tau * 0.618 + rng.uniform(-0.5, 0.5)
        reach = canopy_r * spread * (0.55 + rng.random() * 0.55) * (1.0 - 0.35 * t)
        z_dir = -0.05 + t * 0.55 + rng.uniform(-0.12, 0.12)
        direction = (math.cos(angle) * 0.70, math.sin(angle) * 0.70, z_dir)
        # Curvature: lower branches arch downward (gravity), upper arch
        # upward (toward sun). Some branches randomly curl sideways.
        gravity_bend = -0.18 + t * 0.42 + rng.uniform(-0.12, 0.12)
        # Curve axis: by default _add_branch picks perpendicular; we
        # explicitly choose either gravity (Z+/Z-) or sideways for variety.
        if rng.random() < 0.45:
            curve_axis = (0.0, 0.0, 1.0)  # bend along Z (up/down)
            curvature = gravity_bend
        else:
            # Bend sideways perpendicular to the branch growth direction.
            curve_axis = None
            curvature = rng.uniform(-0.22, 0.22)
        tip = _add_branch(
            bm, uv,
            start=(rng.uniform(-0.02, 0.02), rng.uniform(-0.02, 0.02), z),
            direction=direction,
            length=reach,
            radius=r * (0.42 - t * 0.18) + 0.012,
            key=TRUNK,
            segments=6,
            curvature=curvature,
            curve_axis=curve_axis,
            length_segments=4,
        )
        # ONE leaf cluster per branch tip — sized to wrap the branch end.
        # Slightly bigger for low branches, smaller for upper ones.
        tip_leaf_r = branch_leaf_r * (0.90 + (1.0 - t) * 0.35)
        anchors.append((tip.x, tip.y, tip.z, tip_leaf_r))

        # ~30% of primary branches get a small sub-branch fork near the tip.
        if rng.random() < 0.30:
            sub_a = angle + rng.uniform(-1.0, 1.0)
            sub_len = reach * (0.35 + rng.random() * 0.25)
            sub_dir = (math.cos(sub_a) * 0.65, math.sin(sub_a) * 0.65,
                       z_dir + rng.uniform(0.1, 0.35))
            # Start 65% along the primary branch.
            sub_start = (
                tip.x * 0.65,
                tip.y * 0.65,
                z + (tip.z - z) * 0.65,
            )
            sub_tip = _add_branch(
                bm, uv,
                start=sub_start,
                direction=sub_dir,
                length=sub_len,
                radius=r * (0.32 - t * 0.16) + 0.006,
                key=TRUNK,
                segments=5,
            )
            # A smaller leaf puff at the sub-branch tip too.
            anchors.append((sub_tip.x, sub_tip.y, sub_tip.z, tip_leaf_r * 0.75))

    # Each sibling trunk also gets a couple of branches + leaf clusters.
    for (sx, sy, sz, s_base_r) in sibling_trunks:
        for i in range(3):
            a = i * math.tau / 3 + rng.uniform(-0.3, 0.3)
            length = canopy_r * (0.30 + rng.random() * 0.20)
            tip = _add_branch(
                bm, uv,
                start=(sx, sy, sz * 0.92),
                direction=(math.cos(a) * 0.6, math.sin(a) * 0.6, 0.25 + rng.random() * 0.25),
                length=length,
                radius=s_base_r * 0.4 + 0.005,
                key=TRUNK,
                segments=5,
            )
            anchors.append((tip.x, tip.y, tip.z, branch_leaf_r * 0.85))

    return bm, anchors


def _build_birch_trunk(idx, variant):
    """Birch: pale tapered trunk + birch scars + 2-5 forking branches up into
    the canopy. Variants 3, 4, 5 also get a secondary multi-stem trunk for the
    classic clumped-birch silhouette.

    Returns (bmesh, leaf_anchors). One leaf cluster per fork tip; multi-stem
    siblings get clusters per their branches too.
    """
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)

    r = BIRCH_TRUNK_R[idx]
    lean = variant["lean"]
    canopy_c = variant["canopy_center"]
    canopy_r = variant["canopy_radius"]
    bc = variant["branch_count"]

    # Main trunk reaches ~25% up into the canopy.
    trunk_top = canopy_c + canopy_r * 0.25
    lean_top_x = lean * (trunk_top / max(0.01, variant["trunk_top"]))

    _add_tapered_cylinder(
        bm, uv,
        z0=0.0, z1=trunk_top,
        r0=r * 1.12, r1=r * 0.48,
        key=BIRCH_BARK, segments=12,
        x1=lean_top_x,
    )

    rng = random.Random(f"birch-trunk:{idx}")

    # Multi-stem: 50–85% chance of a sibling trunk leaning the other way.
    sibling_offset_x = 0.0
    sibling_top = None
    if rng.random() < BIRCH_FORK_PROB[idx]:
        sibling_lean = -lean * 1.4 if abs(lean) > 0.02 else rng.uniform(-0.22, 0.22)
        sibling_offset_x = r * 1.6 * (1 if sibling_lean >= 0 else -1)
        sibling_height = trunk_top * (0.78 + rng.random() * 0.18)
        sibling_lean_top = sibling_lean * (sibling_height / max(0.01, trunk_top))
        _add_tapered_cylinder(
            bm, uv,
            z0=0.0, z1=sibling_height,
            r0=r * 0.88, r1=r * 0.36,
            key=BIRCH_BARK, segments=10,
            x0=sibling_offset_x, y0=0.0,
            x1=sibling_offset_x + sibling_lean_top, y1=0.0,
        )
        sibling_top = (sibling_offset_x + sibling_lean_top, 0.0, sibling_height)

    # Birch scars on main trunk (small dark bands).
    z = 0.55
    while z < trunk_top - 0.5:
        a = rng.random() * math.tau
        x = math.cos(a) * r * 1.05 + lean * (z / max(0.01, variant["trunk_top"]))
        y = math.sin(a) * r * 1.05
        _add_tapered_cylinder(
            bm, uv,
            z0=z - 0.025, z1=z + 0.025,
            r0=r * 0.56, r1=r * 0.56,
            key=SHADE, segments=5,
            x0=x, y0=y, x1=x, y1=y,
        )
        z += 0.6 + rng.random() * 0.30

    # Collect leaf anchors as branches grow.
    anchors = []
    fork_leaf_r = canopy_r * 0.40  # bigger puff per fork

    # Forking branches from upper trunk reaching toward canopy top.
    fork_z = trunk_top - r * 0.4
    canopy_top = canopy_c + canopy_r * 0.55
    for i in range(bc):
        a = i * math.tau / max(1, bc) + rng.uniform(-0.3, 0.3)
        # Target a point inside upper canopy.
        target_xy = canopy_r * (0.55 + rng.random() * 0.40)
        target_z  = canopy_top - rng.random() * canopy_r * 0.5
        direction = (
            math.cos(a) * 0.6,
            math.sin(a) * 0.6,
            (target_z - fork_z) / max(0.2, target_xy) * 0.7 + 0.25,
        )
        length = target_xy * 1.05
        # Birch branches curve upward most of the time (toward sun).
        birch_curvature = rng.uniform(0.10, 0.35)
        tip = _add_branch(
            bm, uv,
            start=(lean_top_x, 0.0, fork_z),
            direction=direction,
            length=length,
            radius=r * 0.45,
            key=BIRCH_BARK,
            segments=5,
            curvature=birch_curvature,
            curve_axis=(0.0, 0.0, 1.0),
            length_segments=4,
        )
        # ONE leaf cluster at each fork tip — birches read as multiple
        # canopy puffs sitting on a multi-fork frame.
        anchors.append((tip.x, tip.y, tip.z, fork_leaf_r))

        # ~35% of main fork branches get a sub-branch — birches love forks.
        if rng.random() < 0.35:
            sub_a = a + rng.uniform(-1.1, 1.1)
            sub_tip = _add_branch(
                bm, uv,
                start=(tip.x * 0.6, tip.y * 0.6, fork_z + (tip.z - fork_z) * 0.55),
                direction=(math.cos(sub_a) * 0.55, math.sin(sub_a) * 0.55,
                           0.25 + rng.random() * 0.30),
                length=length * (0.38 + rng.random() * 0.22),
                radius=r * 0.30,
                key=BIRCH_BARK,
                segments=5,
            )
            anchors.append((sub_tip.x, sub_tip.y, sub_tip.z, fork_leaf_r * 0.75))

    # 1-2 mid-trunk branches near the half-way point (the "stems from the
    # middle" silhouette the user asked for).
    mid_count = 1 + (1 if rng.random() < 0.6 else 0)
    for i in range(mid_count):
        z = trunk_top * (0.42 + rng.random() * 0.18)
        a = rng.random() * math.tau
        length = canopy_r * (0.18 + rng.random() * 0.14)
        tip = _add_branch(
            bm, uv,
            start=(lean * (z / max(0.01, variant["trunk_top"])), 0.0, z),
            direction=(math.cos(a) * 0.78, math.sin(a) * 0.78, 0.12 + rng.random() * 0.20),
            length=length,
            radius=r * 0.32,
            key=BIRCH_BARK,
            segments=5,
        )
        # Small leaf cluster at mid-trunk branch tip too.
        anchors.append((tip.x, tip.y, tip.z, fork_leaf_r * 0.62))

    # If multi-stem, give the sibling trunk a couple of branches + leaves.
    if sibling_top is not None:
        for i in range(max(1, bc - 2)):
            a = i * math.tau / max(1, bc - 1) + rng.uniform(-0.4, 0.4)
            target_xy = canopy_r * (0.4 + rng.random() * 0.35)
            target_z  = canopy_top - rng.random() * canopy_r * 0.4
            direction = (
                math.cos(a) * 0.55,
                math.sin(a) * 0.55,
                (target_z - sibling_top[2]) / max(0.2, target_xy) * 0.7 + 0.25,
            )
            tip = _add_branch(
                bm, uv,
                start=sibling_top,
                direction=direction,
                length=target_xy * 1.0,
                radius=r * 0.36,
                key=BIRCH_BARK,
                segments=5,
            )
            anchors.append((tip.x, tip.y, tip.z, fork_leaf_r * 0.85))
    return bm, anchors


def _build_hero_trunk():
    """Hero pine: 11m trunk with a dramatic root flare, mid-trunk + canopy
    branches, and sub-branch forks. Hero trees are landmarks — they get the
    most skeleton detail and the widest base of any tree in the world.

    Returns (bmesh, leaf_anchors). One central core + clusters at every
    primary and sub-branch tip — densely leafy.
    """
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)

    r = HERO_VARIANT["trunk_radius"]
    canopy_c = HERO_VARIANT["canopy_center"]
    canopy_r = HERO_VARIANT["canopy_radius"]
    trunk_total = canopy_c + canopy_r * 0.55
    rng = random.Random("hero-branches")

    # Dramatic root flare — bottom 0.9m is much wider.
    flare_z = 0.85
    _add_tapered_cylinder(
        bm, uv,
        z0=0.0, z1=flare_z,
        r0=r * 1.55, r1=r * 1.15,
        key=TRUNK, segments=18,
    )
    _add_tapered_cylinder(
        bm, uv,
        z0=flare_z, z1=trunk_total,
        r0=r * 1.15, r1=r * 0.26,
        key=TRUNK, segments=16,
    )

    # Low / mid-trunk branches — give the giant landmark some scale.
    bare_top = HERO_VARIANT["trunk_top"]
    for i in range(3):
        z = flare_z + 0.2 + i * 0.55
        if z > bare_top - 0.3:
            break
        a = rng.random() * math.tau
        _add_branch(
            bm, uv,
            start=(0.0, 0.0, z),
            direction=(math.cos(a) * 0.78, math.sin(a) * 0.78,
                       -0.05 + rng.random() * 0.18),
            length=canopy_r * (0.30 + rng.random() * 0.25),
            radius=r * 0.38 + 0.015,
            key=TRUNK,
            segments=6,
        )

    # Collect leaf anchors.
    anchors = []
    # Core central cluster — hero is iconic; it gets a clearly-visible mass.
    anchors.append((0.0, 0.0, canopy_c, canopy_r * 0.65))
    hero_branch_leaf_r = canopy_r * 0.42

    # Canopy branches (denser than scattered pines).
    canopy_bottom = canopy_c - canopy_r * 0.88
    canopy_top    = canopy_c + canopy_r * 0.45
    for i in range(13):
        t = i / 12
        z = canopy_bottom + (canopy_top - canopy_bottom) * (0.04 + pow(t, 0.6) * 0.93)
        a = i * math.tau * 0.618 + rng.uniform(-0.4, 0.4)
        reach = canopy_r * (0.55 + rng.random() * 0.40) * (1.0 - 0.30 * t)
        z_dir = -0.05 + t * 0.5 + rng.uniform(-0.10, 0.10)
        # Hero branch curvature: lower curves down (gravity), upper curves up.
        hero_curv = -0.22 + t * 0.55 + rng.uniform(-0.10, 0.10)
        tip = _add_branch(
            bm, uv,
            start=(rng.uniform(-0.04, 0.04), rng.uniform(-0.04, 0.04), z),
            direction=(math.cos(a) * 0.72, math.sin(a) * 0.72, z_dir),
            length=reach,
            radius=r * (0.48 - t * 0.22) + 0.03,
            key=TRUNK,
            segments=8,
            curvature=hero_curv,
            curve_axis=(0.0, 0.0, 1.0),
            length_segments=5,
        )
        anchors.append((tip.x, tip.y, tip.z, hero_branch_leaf_r * (0.85 + (1.0 - t) * 0.30)))

        # Sub-branches on ~30% of primary branches.
        if rng.random() < 0.32:
            sub_a = a + rng.uniform(-1.0, 1.0)
            sub_tip = _add_branch(
                bm, uv,
                start=(tip.x * 0.6, tip.y * 0.6, z + (tip.z - z) * 0.6),
                direction=(math.cos(sub_a) * 0.65, math.sin(sub_a) * 0.65,
                           z_dir + rng.uniform(0.1, 0.30)),
                length=reach * (0.32 + rng.random() * 0.22),
                radius=r * (0.34 - t * 0.18) + 0.015,
                key=TRUNK,
                segments=6,
            )
            anchors.append((sub_tip.x, sub_tip.y, sub_tip.z, hero_branch_leaf_r * 0.78))
    return bm, anchors


def _commit_bmesh(mesh_name, bm):
    mesh = bpy.data.meshes.get(mesh_name)
    if mesh is None:
        bm.free()
        raise RuntimeError(
            f"Required mesh {mesh_name!r} not found. Run phase-11-foliage.py first."
        )
    material = _lib.get_palette_material()
    mesh.clear_geometry()
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    mesh.materials.clear()
    mesh.materials.append(material)


def _clear_mesh(mesh_name):
    mesh = bpy.data.meshes.get(mesh_name)
    if mesh is None:
        return
    mesh.clear_geometry()
    mesh.update()


# ============================================================================
# Ref-empty emission.
# ============================================================================


def _purge_existing_leaf_refs():
    """Remove any refTreeLeaves_* / refBushLeaves_* from a previous 11c run."""
    purged = 0
    for obj in list(bpy.data.objects):
        if obj.name.startswith("refTreeLeaves_") or obj.name.startswith("refBushLeaves_"):
            bpy.data.objects.remove(obj, do_unlink=True)
            purged += 1
    return purged


def _make_leaf_ref(name, location, radius, userdata):
    """Create a foliage ref empty and switch its display to a wireframe sphere.

    `_lib.ref_empty` defaults to PLAIN_AXES which renders as the noisy black
    cross-shapes the user pointed at. Sphere display shows the canopy
    boundary instead — much more informative in the editor and visually
    cleaner.
    """
    ref = _lib.ref_empty(name=name, location=location, radius=radius, userdata=userdata)
    ref.empty_display_type = 'SPHERE'
    ref.empty_display_size = 1.0  # the scale (=radius) already sizes the sphere
    return ref


def _emit_anchors_for_instance(obj, species, variant_idx, src_mesh_name):
    """Emit one refTreeLeaves_<inst>_<NN> per recorded leaf anchor.

    Each anchor's local position is transformed into the instance's world
    space via matrix_world. Radii are scaled uniformly by the instance's
    scale.x so per-instance size variation propagates to leaf cluster size.
    """
    anchors = LEAF_ANCHORS_PER_VARIANT.get(src_mesh_name) or []
    if not anchors:
        return 0
    emitted = 0
    inst_scale = obj.scale.x
    for ai, (lx, ly, lz, lr) in enumerate(anchors):
        world_pos = obj.matrix_world @ Vector((lx, ly, lz))
        _make_leaf_ref(
            f"refTreeLeaves_{obj.name}_{ai:02d}",
            location=tuple(world_pos),
            radius=lr * inst_scale,
            userdata={
                "species": species,
                "variant": variant_idx,
                "cluster": ai,
            },
        )
        emitted += 1
    return emitted


def _emit_tree_leaf_refs():
    """One refTreeLeaves_<inst>_<NN> empty per leaf anchor recorded by the
    trunk builders. Trees that have N anchors get N refs — branch-tip
    clusters spread the foliage across the actual skeleton rather than a
    single big sphere per tree.
    """
    refs = 0

    # Pines: tree_pine_inst_NNN → mesh data is tree_pine_var_K_src_mesh.
    for obj in [o for o in bpy.data.objects if o.name.startswith("tree_pine_inst_")]:
        if obj.data is None:
            continue
        try:
            idx = int(obj.data.name.split("_var_")[1].split("_")[0]) - 1
        except (IndexError, ValueError):
            continue
        if idx < 0 or idx >= len(PINE_VARIANTS):
            continue
        refs += _emit_anchors_for_instance(obj, "pine", idx + 1, obj.data.name)

    # Birches.
    for obj in [o for o in bpy.data.objects if o.name.startswith("tree_birch_inst_")]:
        if obj.data is None:
            continue
        try:
            idx = int(obj.data.name.split("_var_")[1].split("_")[0]) - 1
        except (IndexError, ValueError):
            continue
        if idx < 0 or idx >= len(BIRCH_VARIANTS):
            continue
        refs += _emit_anchors_for_instance(obj, "birch", idx + 1, obj.data.name)

    # Hero trees: hero_tree_1..5, all referencing tree_hero_pine_src_mesh.
    for obj in [o for o in bpy.data.objects if o.name.startswith("hero_tree_")]:
        refs += _emit_anchors_for_instance(obj, "hero", 0, HERO_MESH)

    return refs


def _emit_bush_leaf_refs():
    """One refBushLeaves_<inst_name> empty per bush instance."""
    refs = 0
    for obj in [o for o in bpy.data.objects if o.name.startswith("gc_bush_inst_")]:
        local_canopy = Vector((0.0, 0.0, BUSH_CANOPY_CENTER))
        world_pos = obj.matrix_world @ local_canopy
        radius = BUSH_CANOPY_RADIUS * obj.scale.x
        _make_leaf_ref(
            f"refBushLeaves_{obj.name}",
            location=tuple(world_pos),
            radius=radius,
            userdata={"species": "bush"},
        )
        refs += 1
    return refs


# ============================================================================
# Validation.
# ============================================================================


def _validate_contracts():
    missing = [name for name in [*PINE_MESHES, *BIRCH_MESHES, HERO_MESH, *BUSH_MESHES]
               if bpy.data.meshes.get(name) is None]
    if missing:
        raise RuntimeError("Missing source meshes: " + ", ".join(missing))

    counts = {
        "pine_instances": len([o for o in bpy.data.objects if o.name.startswith("tree_pine_inst_")]),
        "birch_instances": len([o for o in bpy.data.objects if o.name.startswith("tree_birch_inst_")]),
        "hero_trees": len([o for o in bpy.data.objects if o.name.startswith("hero_tree_")]),
        "bush_instances": len([o for o in bpy.data.objects if o.name.startswith("gc_bush_inst_")]),
    }
    if counts["pine_instances"] == 0 or counts["birch_instances"] == 0:
        raise RuntimeError(f"Tree instances missing; refusing to continue: {counts}")
    if counts["hero_trees"] != 5:
        raise RuntimeError(f"Hero tree contract changed; refusing to continue: {counts}")
    return counts


# ============================================================================
# Entry point.
# ============================================================================


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-save", action="store_true")
    args = parser.parse_args(argv)

    counts = _validate_contracts()
    print(f"{_lib.LOG_PREFIX}[phase-11c] contract OK: {counts}")

    if args.dry_run:
        print(f"{_lib.LOG_PREFIX}[phase-11c] dry run only; no mesh / ref changes.")
        return

    # 1. Rebuild each shared variant mesh as trunk-only + record leaf anchors.
    LEAF_ANCHORS_PER_VARIANT.clear()
    for idx, mesh_name in enumerate(PINE_MESHES):
        bm, anchors = _build_pine_trunk(idx, PINE_VARIANTS[idx])
        LEAF_ANCHORS_PER_VARIANT[mesh_name] = anchors
        _commit_bmesh(mesh_name, bm)
    for idx, mesh_name in enumerate(BIRCH_MESHES):
        bm, anchors = _build_birch_trunk(idx, BIRCH_VARIANTS[idx])
        LEAF_ANCHORS_PER_VARIANT[mesh_name] = anchors
        _commit_bmesh(mesh_name, bm)
    hero_bm, hero_anchors = _build_hero_trunk()
    LEAF_ANCHORS_PER_VARIANT[HERO_MESH] = hero_anchors
    _commit_bmesh(HERO_MESH, hero_bm)

    # 2. Empty bush variant meshes — runtime is the bush.
    for mesh_name in BUSH_MESHES:
        _clear_mesh(mesh_name)

    # 3. Re-emit foliage ref empties (idempotent: purge then create).
    purged = _purge_existing_leaf_refs()
    tree_refs = _emit_tree_leaf_refs()
    bush_refs = _emit_bush_leaf_refs()
    print(
        f"{_lib.LOG_PREFIX}[phase-11c] purged {purged} stale refs; "
        f"created {tree_refs} refTreeLeaves_* and {bush_refs} refBushLeaves_*"
    )

    if not args.no_save:
        blend_path = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "world.blend"))
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"{_lib.LOG_PREFIX}[phase-11c] saved -> {blend_path}")
    else:
        print(f"{_lib.LOG_PREFIX}[phase-11c] --no-save; changes in-memory only.")


if __name__ == "__main__":
    script_args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    main(script_args)
