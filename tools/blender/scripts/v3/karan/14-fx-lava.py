"""Drop a glowing LAVA POOL into the carved basin behind the Projects hut.

A karan-original landscape feature (no Bruno verbatim step).

THE DIP IS NOT CARVED HERE. Geometry Nodes only re-reads the terrain height
mask at build time, so the depression is authored alongside the water ponds in
the section-02 terrain build (`02-ground-grass-base.py` stamps terrainWater.R
via `lava_common.basin_intensity`; `02-ground-grass-water.py` zeroes B there so
it shows no teal water). That makes the ground genuinely sink ~0.63 m, exactly
like a water pond. This script runs LAST and only dresses that pre-carved dip:

  Blender owns (this script): the emissive lava surface + hot core mesh seated
  in the dip, the broken ring of cooled-lava crust stones on the rim, grass
  cleared from the basin, a hidden collider footprint, and a `lavaRef_pool`
  runtime anchor carrying motion hints (flow dir, glow strength, pulse speed,
  ember rate, surface object names).

  Three.js owns LATER (not here): glow pulsing, surface flow/scroll, ember
  particles — driven off the lavaRef_pool custom props + named meshes.

VERIFY WITH A FULL REBUILD, not a standalone run: this script raycasts the
terrain to seat the lava IN the dip, so the section-02 carve must already exist.
Run `14-section-run-all.py` (foundation -> ... -> 02 carves the basin -> ... ->
14 dresses it). Running this file alone on a world without the section-02 carve
will seat the lava on flat ground.

Standalone (only meaningful once the basin is carved, e.g. after a full rebuild):
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/14-fx-lava.py').read())
"""
import importlib
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

KARAN_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() \
    else "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan"
if KARAN_DIR not in sys.path:
    sys.path.append(KARAN_DIR)

import buildings_common as bc   # raycast, clear_grass/foliage, materials
import misc_common as mc        # ref_anchor / collider_box / cull_foliage_near
import lava_common as lc        # basin CENTER / RADIUS_M / PEAK_R (shared with section 02)
importlib.reload(bc)            # dodge Blender's stale module cache between runs
importlib.reload(mc)
importlib.reload(lc)

KEY = "pool"
COLLECTION = "lavaPool"

LAVA_RADIUS = lc.RADIUS_M
RIM_RADIUS = LAVA_RADIUS + 0.65
SURFACE_RADIUS = RIM_RADIUS + 0.18
CORE_RADIUS = LAVA_RADIUS * 0.32
MIN_SURFACE_FILL = 0.16      # fallback shallow fill above the carved bed
SURFACE_LIP_DROP = 0.04      # keep lava just below the basin rim, not buried
GRASS_IMAGE = "terrainGrass"
GRASS_OBJECT = "Plane.003"

# --- broken crust ring -------------------------------------------------------
STONE_SLOTS = 16
STONE_GAPS = {3, 8, 13}      # slots left open -> broken (not solid) crust
EXTRA_ROCKS = (
    {"angle": math.radians(32.0), "distance": 4.95, "radius": 0.72,
     "scale": (1.30, 0.88, 0.46), "mat": "crust_edge"},
    {"angle": math.radians(216.0), "distance": 4.70, "radius": 0.62,
     "scale": (1.18, 0.78, 0.42), "mat": "crust"},
)

# User hand-placed these two shore-rock duplicates beside the lava pool in
# Blender; keep them exact on every rebuild instead of replacing their look
# with procedural lavaRock stones.
MANUAL_SHORE_ROCKS = (
    {"source": "shoreRock282", "name": "shoreRock282.001",
     "loc": (37.804, -44.914, 0.0), "scale": (0.40, 0.328, 0.216),
     "yaw": math.radians(-50.0)},
    {"source": "shoreRock304", "name": "shoreRock304.001",
     "loc": (35.333, -42.740, 0.0), "scale": (0.58, 0.476, 0.313),
     "yaw": math.radians(-15.0)},
)

COLORS = {
    "surface":    (0.88, 0.025, 0.010, 1.0),  # molten red base
    "core":       (1.0, 0.20, 0.025, 1.0),    # hotter red-orange inner glow
    "crust":      (0.060, 0.055, 0.062, 1.0),  # near-black basalt
    "crust_edge": (0.14, 0.12, 0.12, 1.0),
    "crust_hot":  (0.78, 0.045, 0.015, 1.0),  # residual-heat glowing stone
}


def _mats():
    return {
        "surface":    bc.material("lava_surface_glow", COLORS["surface"], 0.48, 2.2),
        "core":       bc.material("lava_core_glow", COLORS["core"], 0.42, 3.4),
        "crust":      bc.material("lava_crust_stone", COLORS["crust"], 0.92),
        "crust_edge": bc.material("lava_crust_edge", COLORS["crust_edge"], 0.88),
        "crust_hot":  bc.material("lava_crust_hot", COLORS["crust_hot"], 0.7, 1.4),
    }


# ============================================================================
# terrain helpers
# ============================================================================
def _eval_height_at(x, z):
    """Downward raycast onto the EVALUATED terrain (sees the section-02 GN
    displacement, i.e. the carved dip). Blender-Z, or None off-terrain."""
    terr = bc.terrain()
    if terr is None:
        return None
    dg = bpy.context.evaluated_depsgraph_get()
    ev = terr.evaluated_get(dg)
    inv = ev.matrix_world.inverted()
    o = inv @ Vector((x, z, 80.0))
    d = (inv.to_3x3() @ Vector((0.0, 0.0, -1.0))).normalized()
    ok, loc, _n, _i = ev.ray_cast(o, d)
    if not ok:
        return None
    return (ev.matrix_world @ loc).z


def _surface_height(bx, bz, bed):
    """Fill the basin close to its rim so the lava reads as a surface pool.

    The terrain bed is intentionally carved ~0.63m down, but the visible lava
    should sit near the lip, like a shallow filled pond, not down at the bottom.
    """
    lips = []
    for i in range(28):
        a = math.tau * i / 28.0
        h = _eval_height_at(
            bx + math.cos(a) * RIM_RADIUS,
            bz + math.sin(a) * RIM_RADIUS,
        )
        if h is not None:
            lips.append(h)
    if not lips:
        return bed + MIN_SURFACE_FILL
    lowest_lip = min(lips)
    if lowest_lip <= bed + MIN_SURFACE_FILL:
        return bed + MIN_SURFACE_FILL
    return lowest_lip - SURFACE_LIP_DROP


def _reeval_grass():
    """Force the grass scatter to re-read the edited terrainGrass mask so the
    cleared basin loses its blades. (Editing image pixels doesn't propagate to
    GN by itself; a disk save + reload + modifier toggle does.)"""
    img = bpy.data.images.get(GRASS_IMAGE)
    if img is not None:
        try:
            os.makedirs(os.path.dirname(bc.GRASS_MASK_FILE), exist_ok=True)
            img.filepath_raw = bc.GRASS_MASK_FILE
            img.file_format = "OPEN_EXR"
            img.save()
            if img.packed_file is not None:
                img.unpack(method="USE_ORIGINAL")
            img.reload()
        except Exception as e:
            print(f"  [WARN] grass mask reload failed: {e}")
    plane = bpy.data.objects.get(GRASS_OBJECT)
    if plane is not None:
        for mod in plane.modifiers:
            if mod.type == "NODES":
                try:
                    mod.show_viewport = False
                    mod.show_viewport = True
                except Exception:
                    pass
    bpy.context.view_layer.update()


# ============================================================================
# geometry builders
# ============================================================================
def _blob_surface(name, center, radius, mat, segs=44, wobble=0.13, seed=1.0,
                  dome=0.0):
    """Irregular filled disc (lava surface), centre vertex optionally domed."""
    bm = bmesh.new()
    c = bm.verts.new((0.0, 0.0, dome))
    ring = []
    for i in range(segs):
        a = math.tau * i / segs
        rr = radius * (1.0 + wobble * math.sin(3.0 * a + seed)
                       + 0.5 * wobble * math.sin(5.0 * a + seed * 1.7))
        ring.append(bm.verts.new((math.cos(a) * rr, math.sin(a) * rr, 0.0)))
    for i in range(segs):
        bm.faces.new((c, ring[i], ring[(i + 1) % segs]))
    bm.normal_update()
    mesh = bpy.data.meshes.get(f"lavaMesh_{name}") or bpy.data.meshes.new(f"lavaMesh_{name}")
    mesh.clear_geometry()
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.clear()
    mesh.materials.append(mat)
    for p in mesh.polygons:
        p.use_smooth = True
    obj = bpy.data.objects.get(name) or bpy.data.objects.new(name, mesh)
    obj.data = mesh
    obj.location = center
    return mc.link(obj, COLLECTION)


def _crust_ring(bx, bz, m):
    """Broken ring of squashed basalt stones seated on the carved rim."""
    placed = 0
    for i in range(STONE_SLOTS):
        if i in STONE_GAPS:
            continue
        a = math.tau * i / STONE_SLOTS + 0.18 * math.sin(i * 1.7)
        rr = RIM_RADIUS + 0.18 * math.sin(i * 2.3)
        sx = bx + math.cos(a) * rr
        sy = bz + math.sin(a) * rr
        bed = _eval_height_at(sx, sy)
        if bed is None:
            continue
        base_r = 0.42 + 0.12 * ((i * 7) % 5) / 4.0
        sz = 0.50 + 0.10 * ((i * 3) % 4) / 3.0
        half_h = base_r * sz
        hot = (i % 4 == 0)
        mat = m["crust_hot"] if hot else (m["crust"] if i % 2 else m["crust_edge"])
        stone = mc.sphere(
            f"lavaCrust_{i:02d}", base_r, (sx, sy, bed + half_h * 0.55), mat,
            segments=10, ring_count=7,
            scale=(1.0 + 0.18 * math.sin(i), 0.78 + 0.12 * math.cos(i), sz),
            collection=COLLECTION, mesh_prefix="lavaMesh",
        )
        stone.rotation_mode = "XYZ"
        stone.rotation_euler = (0.0, 0.0, a + 0.4 * math.sin(i))
        for p in stone.data.polygons:        # faceted, like the basalt rocks
            p.use_smooth = False
        placed += 1
    return placed


def _extra_rocks(bx, bz, m):
    """A couple of larger basalt boulders near the lava, matching the nearby
    rock clusters instead of making the whole rim a perfect ring."""
    placed = 0
    for i, spec in enumerate(EXTRA_ROCKS):
        a = spec["angle"]
        sx = bx + math.cos(a) * spec["distance"]
        sy = bz + math.sin(a) * spec["distance"]
        ground = _eval_height_at(sx, sy)
        if ground is None:
            continue
        radius = spec["radius"]
        scale = spec["scale"]
        rock = mc.sphere(
            f"lavaRock_{i:02d}", radius,
            (sx, sy, ground + radius * scale[2] * 0.48),
            m[spec["mat"]],
            segments=10, ring_count=7, scale=scale,
            collection=COLLECTION, mesh_prefix="lavaMesh",
        )
        rock.rotation_mode = "XYZ"
        rock.rotation_euler = (0.0, 0.0, a + 0.35 * math.sin(i + 1.0))
        for p in rock.data.polygons:
            p.use_smooth = False
        placed += 1
    return placed


def _manual_shore_rocks():
    """Recreate the two user-placed shore-rock duplicates near the lava."""
    placed = 0
    for spec in MANUAL_SHORE_ROCKS:
        src = bpy.data.objects.get(spec["source"])
        ob = bpy.data.objects.get(spec["name"])
        if src is None:
            print(f"  [WARN] source rock {spec['source']!r} missing; cannot keep {spec['name']!r}")
            continue
        if ob is None:
            ob = src.copy()
            ob.data = src.data
            ob.name = spec["name"]
            mc.link(ob, COLLECTION)
        ob.location = spec["loc"]
        ob.scale = spec["scale"]
        ob.rotation_mode = "XYZ"
        ob.rotation_euler = (0.0, 0.0, spec["yaw"])
        placed += 1
    return placed


# ============================================================================
# run
# ============================================================================
def run():
    print("[14-fx-lava] dress the lava pool in the section-02 carved basin")
    mc.remove_objects_with_prefix("lavaSurface_", "lavaCrust_", "lavaRock_",
                                  "lavaRef_",
                                  f"miscFootprint_{KEY}")

    bx, bz = lc.CENTER
    bed = _eval_height_at(bx, bz)
    if bed is None:
        print(f"  [ABORT] target {lc.CENTER} is off-terrain (ocean)")
        return
    print(f"  basin centre ({bx:.2f},{bz:.2f}) bed={bed:.3f} "
          f"(should be ~{lc.PEAK_R * 1.5:.2f} m below the surrounding ground)")
    dip = lc.PEAK_R * 1.5

    m = _mats()

    # Clear grass + discrete foliage from the basin (so nothing pokes through),
    # then force the grass scatter to re-read the edited mask.
    bc.clear_grass_under(bx, bz, 0.0, (RIM_RADIUS + 0.4, RIM_RADIUS + 0.4))
    for spec in EXTRA_ROCKS:
        a = spec["angle"]
        bc.clear_grass_under(
            bx + math.cos(a) * spec["distance"],
            bz + math.sin(a) * spec["distance"],
            0.0,
            (spec["radius"] * 1.2, spec["radius"] * 1.2),
        )
    bc.clear_foliage_under(bx, bz, 0.0, (RIM_RADIUS + 0.4, RIM_RADIUS + 0.4))
    mc.cull_foliage_near([(bx, bz)], radius=RIM_RADIUS + 0.6)
    _reeval_grass()

    surface_z = _surface_height(bx, bz, bed)

    # Emissive molten surface + a smaller, brighter, slightly domed hot core.
    _blob_surface("lavaSurface_pool", (bx, bz, surface_z), SURFACE_RADIUS,
                  m["surface"], wobble=0.09, seed=1.0)
    _blob_surface("lavaSurface_core", (bx, bz, surface_z + 0.02),
                  CORE_RADIUS, m["core"], segs=36, wobble=0.18,
                  seed=2.3, dome=0.05)

    stones = _crust_ring(bx, bz, m)
    extra_stones = _extra_rocks(bx, bz, m)
    manual_stones = _manual_shore_rocks()

    # Hidden collider footprint over the basin (runtime no-walk / heat zone).
    mc.collider_box(KEY, bx, bz, bed, 0.0,
                    (RIM_RADIUS * 2.0, RIM_RADIUS * 2.0, dip + 0.5),
                    collection="colliders")

    # Runtime contract: ONE anchor carrying the motion hints + named surfaces.
    mc.ref_anchor(
        "lavaRef_pool", (bx, bz, surface_z), yaw=0.0,
        props={
            "interaction": "lavaPool",
            "surfaceObject": "lavaSurface_pool",
            "coreObject": "lavaSurface_core",
            "radius": LAVA_RADIUS,
            "flowDir": (1.0, 0.0),     # three.js scroll direction hint
            "glowStrength": 2.6,       # base emissive the runtime pulses around
            "pulseSpeed": 0.6,         # Hz-ish hint for the glow pulse
            "emberRate": 12.0,         # ember particles / sec hint
        },
        collection="refs",
    )

    mc.save()
    print(f"  dressed lava pool at ({bx:.1f},{bz:.1f}) bed={bed:.3f} "
          f"surface={surface_z:.3f} dip={dip:.2f}m | "
          f"crust stones={stones} extra rocks={extra_stones} "
          f"manual rocks kept={manual_stones}")


if __name__ == "__main__":
    run()
