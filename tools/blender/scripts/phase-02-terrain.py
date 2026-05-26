"""
Phase 2: 260x260m sculpted heightfield + trimesh collider + height_at helper.

What this produces (after Run Script + save):
- `terrain` collection populated with two meshes:
    * `terrain_mesh`     — 193x193 verts (~37k verts, ~36k quads) visible
                           heightfield, palette-UV-mapped per face, single
                           `world_palette_material` slot.
    * `trimesh_terrain`  — triangulated copy of the visible mesh; the
                           `trimesh_` prefix tells the runtime importer to
                           build a Rapier heightfield/trimesh from it.
                           Hidden in viewport + render.
- 6 ref empties in the `refs` collection:
    refSpawnPoint, refRespawn_origin, refPath_N, refPath_E, refPath_S,
    refPath_W. Heights sampled from the heightfield so they sit on the
    visible surface.
- Heightfield shape (deterministic, mathutils.noise.noise):
    * Inner plateau r<=20m: y=0.02 flat floor.
    * Plateau undulation 20<r<=85m: 3-octave fbm, amp 0..0.8m.
    * Shore slope 85<r<=95m: smoothstep down to y=-2.
    * Ocean floor r>95m: y=-2 with low-amp ripple.
    * Additive NE ridge along (0,0)->(15,95), peak +12m, 12m wide.
    * Negative W cliff: x<-78 AND |z|<60 drops up to 25m (waterfall lip).

Also extends `_lib.py` with `height_at(x, z)` — raycasts +50Y down onto
`terrain_mesh` and returns runtime Y in meters. Used by Phase 3+ to sit
props on the surface (CLAUDE.md rule 4 contract).

Coordinate convention: authored in Blender Z-up (Blender X = runtime X
east-west, Blender Y = runtime Z north-south, Blender Z = runtime Y
height). The glTF exporter in Phase 13 performs the Z-up -> Y-up swap.

Idempotent: re-running clears the `terrain` collection first, then
rebuilds. Materials and palette image references are reused by name.

How to run:
  1. Open tools/blender/world.blend in Blender 4.2+.
  2. Scripting workspace -> Text Editor -> Open -> phase-02-terrain.py.
  3. Run Script (Alt+P). Expect 5-30 seconds to build ~37k verts.
  4. Script saves world.blend automatically (wm.save_mainfile).
"""

import os
import sys
import math

import bpy
import bmesh
from mathutils import Vector
from mathutils import noise as mu_noise


# Mirror Phase 0's _script_dir() — Blender's Text Editor sets __file__
# to the buffer name, so collect every plausible disk path and pick the
# first that actually has _lib.py.
def _script_dir():
    candidates = []
    try:
        if __file__ and os.path.isabs(__file__):
            candidates.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass

    space = getattr(bpy.context, "space_data", None)
    text = getattr(space, "text", None) if space else None
    if text and text.filepath:
        candidates.append(
            os.path.dirname(os.path.abspath(bpy.path.abspath(text.filepath)))
        )

    candidates.append(
        os.path.expanduser(
            "~/Documents/Projects/karan-portfolio/tools/blender/scripts"
        )
    )

    for path in candidates:
        if os.path.isfile(os.path.join(path, "_lib.py")):
            return path

    raise RuntimeError(
        "Could not locate _lib.py - tried: " + ", ".join(candidates)
    )


SCRIPT_DIR = _script_dir()
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import _lib       # noqa: E402
import _palette   # noqa: E402


# Grid resolution + extents. 193x193 verts -> 192x192 quads ~= 37,249 verts /
# 36,864 quads (~73,728 tris after triangulation). Comfortably under the
# 100k-tri spec budget for the whole world, and Blender handles it without
# breaking a sweat on a mid laptop.
GRID_RES = 193
EXTENT = 130.0  # +/- 130m -> 260m square


# Heightfield region radii (runtime XZ distance from origin, in meters).
R_INNER_PLATEAU = 20.0
R_PLATEAU_OUTER = 85.0
R_SHORE = 95.0

# NE ridge endpoints (in runtime XZ — x east-west, z north-south).
RIDGE_A = (0.0, 0.0)
RIDGE_B = (15.0, 95.0)
RIDGE_WIDTH = 12.0
RIDGE_PEAK_H = 12.0

# Western cliff zone — additive NEGATIVE drop. This is the waterfall lip
# that Phase 9 will spill over; smoothstep ramps keep it from z-fighting
# the regular shore.
CLIFF_X_START = -78.0
CLIFF_X_END = -90.0
CLIFF_Z_HALF_INNER = 50.0
CLIFF_Z_HALF_OUTER = 60.0
CLIFF_DROP_MAX = 25.0

OCEAN_FLOOR_Y = -2.0


# ----- generic math helpers (terrain-specific; kept out of _lib.py) -----

def _smoothstep(a, b, x):
    if a == b:
        return 0.0 if x < a else 1.0
    t = (x - a) / (b - a)
    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0
    return t * t * (3.0 - 2.0 * t)


def _mix(a, b, t):
    return a + (b - a) * t


def _clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def _dist_to_segment(px, pz, ax, az, bx, bz):
    """2D point-to-segment distance in the XZ runtime plane."""
    abx = bx - ax
    abz = bz - az
    ab_len_sq = abx * abx + abz * abz
    if ab_len_sq <= 1e-9:
        dx = px - ax
        dz = pz - az
        return math.sqrt(dx * dx + dz * dz)
    apx = px - ax
    apz = pz - az
    t = (apx * abx + apz * abz) / ab_len_sq
    t = _clamp(t, 0.0, 1.0)
    cx = ax + abx * t
    cz = az + abz * t
    dx = px - cx
    dz = pz - cz
    return math.sqrt(dx * dx + dz * dz)


def _seg_t(px, pz, ax, az, bx, bz):
    """Parameter t in [0..1] of the closest point on segment AB to P."""
    abx = bx - ax
    abz = bz - az
    ab_len_sq = abx * abx + abz * abz
    if ab_len_sq <= 1e-9:
        return 0.0
    apx = px - ax
    apz = pz - az
    t = (apx * abx + apz * abz) / ab_len_sq
    return _clamp(t, 0.0, 1.0)


def _noise(x, z):
    """Deterministic 2D noise via mathutils.noise.noise.

    The coordinate is the seed — noise.noise() returns the same value for
    the same Vector input, so re-running this script produces byte-identical
    geometry. Returns roughly in -1..+1.
    """
    return mu_noise.noise(Vector((x, z, 0.0)))


def _fbm_plateau(x, z):
    """3-octave fbm normalised to roughly -1..+1, weighted (1, 0.5, 0.25)."""
    n = (
        _noise(x * 0.05, z * 0.05) +
        _noise(x * 0.12, z * 0.12) * 0.5 +
        _noise(x * 0.25, z * 0.25) * 0.25
    )
    return n / 1.75


def _ridge_contribution(x, z):
    """Additive NE ridge bump centred on RIDGE_A->RIDGE_B.

    Height ramps from 0 at the spawn end to RIDGE_PEAK_H at (15, 95) along
    the segment, with a radial falloff RIDGE_WIDTH meters wide perpendicular.
    """
    d = _dist_to_segment(x, z, RIDGE_A[0], RIDGE_A[1], RIDGE_B[0], RIDGE_B[1])
    falloff = max(0.0, 1.0 - d / RIDGE_WIDTH)
    if falloff <= 0.0:
        return 0.0
    t_along = _seg_t(x, z, RIDGE_A[0], RIDGE_A[1], RIDGE_B[0], RIDGE_B[1])
    return falloff * (t_along * RIDGE_PEAK_H)


def _cliff_drop(x, z):
    """Negative drop in the western cliff zone, smoothstep-ramped at edges."""
    if x >= CLIFF_X_START or abs(z) >= CLIFF_Z_HALF_OUTER:
        return 0.0
    t_x = _smoothstep(CLIFF_X_START, CLIFF_X_END, x)         # 0 outside, 1 deep
    t_z = 1.0 - _smoothstep(CLIFF_Z_HALF_INNER, CLIFF_Z_HALF_OUTER, abs(z))
    return CLIFF_DROP_MAX * t_x * t_z


def _base_layer_height(x, z):
    """Pre-ridge, pre-cliff radial base shape. Separating this lets us
    sample the plateau height at r=85 without infinite recursion on the
    shore branch."""
    r = math.sqrt(x * x + z * z)
    if r <= R_INNER_PLATEAU:
        return 0.02
    if r <= R_PLATEAU_OUTER:
        t = (r - R_INNER_PLATEAU) / (R_PLATEAU_OUTER - R_INNER_PLATEAU)
        amp = _smoothstep(0.0, 1.0, t) * 0.8
        return 0.02 + _fbm_plateau(x, z) * amp
    if r <= R_SHORE:
        # Sample plateau at the same azimuth at r=R_PLATEAU_OUTER so the
        # shore ramp starts at the actual plateau height, not a fixed
        # number — keeps the seam smooth where the noise bobs.
        if r <= 1e-6:
            scale = 1.0
        else:
            scale = R_PLATEAU_OUTER / r
        plateau_h = 0.02 + _fbm_plateau(x * scale, z * scale) * 0.8
        t = (r - R_PLATEAU_OUTER) / (R_SHORE - R_PLATEAU_OUTER)
        return _mix(plateau_h, OCEAN_FLOOR_Y, _smoothstep(0.0, 1.0, t))
    return OCEAN_FLOOR_Y + 0.05 * _noise(x * 0.03, z * 0.03)


def _height(x, z):
    """Final terrain height at runtime XZ (x east-west, z north-south).

    The cliff override drops the western strip up to 25m below ocean
    floor — that's the waterfall plunge pool. It IS visible in the
    raw mesh as a rectangular trench, but the Phase 9 ocean surface
    plane at y~=0 hides it at runtime and fog past 30m obscures the
    far edges. Keeping the geometric depth gives the waterfall a real
    landing pool instead of a 2m shallow puddle.
    """
    y = _base_layer_height(x, z)
    y += _ridge_contribution(x, z)
    y -= _cliff_drop(x, z)
    return y


# ----- face color classification -------------------------------------------

def _face_color_key(fx, fz, ridge_h_at_face):
    """Pick the palette cell for a face whose center is at (fx, fz)."""
    fr = math.sqrt(fx * fx + fz * fz)

    # Ridge override — runs from spawn to (15, 95) so its upper half is
    # past fr=75; without this hoist, the ridge-top would alternate
    # meadow/sand based on radius alone and read as striped instead of
    # rocky.
    if ridge_h_at_face > 8.0:
        return "rock_mid"

    if fr <= R_INNER_PLATEAU:
        # 3m wide dirt corridors along +/- X and +/- Z. The "abs sum > 2"
        # gate keeps the spawn-tile (where both axes are near 0) as meadow
        # rather than a tiny dirt cross at the origin.
        if min(abs(fx), abs(fz)) < 1.5 and (abs(fx) + abs(fz)) > 2.0:
            return "dirt_path"
        return "meadow_grass"

    if fr <= R_PLATEAU_OUTER:
        return "meadow_grass" if fr < 78.0 else "sand_gravel"

    if fr <= R_SHORE:
        return "sand_gravel"

    return "deeper_water"


# ----- mesh construction ---------------------------------------------------

def _build_terrain_mesh():
    """Build the visible 193x193 heightfield and link into the `terrain`
    collection. Returns the new bpy object."""
    print(
        f"{_lib.LOG_PREFIX}[phase-02] building {GRID_RES}x{GRID_RES} grid "
        f"({GRID_RES * GRID_RES} verts) ..."
    )

    mesh = bpy.data.meshes.get("terrain_mesh")
    if mesh is not None:
        bpy.data.meshes.remove(mesh, do_unlink=True)
    mesh = bpy.data.meshes.new("terrain_mesh")

    bm = bmesh.new()

    # Pre-compute axis coords so we don't redo division per row.
    step = (2.0 * EXTENT) / (GRID_RES - 1)
    xs = [(-EXTENT) + i * step for i in range(GRID_RES)]
    zs = [(-EXTENT) + j * step for j in range(GRID_RES)]

    # Author in Blender's Z-up convention: Blender X = runtime X,
    # Blender Y = runtime Z, Blender Z = runtime Y (see Phase 13 exporter
    # for the Y-up swap).
    vert_grid = [[None] * GRID_RES for _ in range(GRID_RES)]
    for j, z in enumerate(zs):
        for i, x in enumerate(xs):
            y = _height(x, z)
            vert_grid[j][i] = bm.verts.new((x, z, y))

    bm.verts.ensure_lookup_table()

    for j in range(GRID_RES - 1):
        for i in range(GRID_RES - 1):
            v00 = vert_grid[j][i]
            v10 = vert_grid[j][i + 1]
            v11 = vert_grid[j + 1][i + 1]
            v01 = vert_grid[j + 1][i]
            bm.faces.new((v00, v10, v11, v01))

    bm.faces.ensure_lookup_table()

    # UV map: every loop of a face gets the SAME UV (the center of the
    # palette cell). Combined with NearestFilter sampling, this paints the
    # whole face a single flat color from the palette PNG.
    uv_layer = bm.loops.layers.uv.new("palette")

    for face in bm.faces:
        cx = sum(v.co.x for v in face.verts) / len(face.verts)
        # Blender Y axis = runtime Z (north-south). Read it back as fz.
        cz = sum(v.co.y for v in face.verts) / len(face.verts)
        ridge_h = _ridge_contribution(cx, cz)
        color_key = _face_color_key(cx, cz, ridge_h)
        u, v = _lib.palette_uv(color_key)
        for loop in face.loops:
            loop[uv_layer].uv = (u, v)

    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.get("terrain_mesh")
    if obj is not None:
        bpy.data.objects.remove(obj, do_unlink=True)
    obj = bpy.data.objects.new("terrain_mesh", mesh)
    obj.location = (0.0, 0.0, 0.0)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.scale = (1.0, 1.0, 1.0)
    _lib.place_in("terrain", obj)
    return obj


def _ensure_palette_material(terrain_obj):
    """Create (or reuse) the world_palette_material and attach to slot 0.

    Configured with the palette PNG sampled at NearestFilter (Closest) so
    Blender's viewport preview matches what the runtime palette material
    will render. Runtime swaps this for SmoothLitPaletteMaterial at load.
    """
    mat_name = "world_palette_material"
    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        mat = bpy.data.materials.new(mat_name)
    mat.use_nodes = True

    nt = mat.node_tree
    # Wipe existing nodes so a re-run can't pile up duplicates.
    for node in list(nt.nodes):
        nt.nodes.remove(node)

    output = nt.nodes.new("ShaderNodeOutputMaterial")
    output.location = (300, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.location = (-400, 0)
    uv_node = nt.nodes.new("ShaderNodeUVMap")
    uv_node.location = (-600, 0)
    uv_node.uv_map = "palette"

    palette_path = os.path.abspath(
        os.path.join(SCRIPT_DIR, "..", "..", "..", "static", "textures", "palette.png")
    )
    image = None
    # Reuse by basename so a re-run doesn't accumulate ".001" suffixes.
    existing_name = os.path.basename(palette_path)
    image = bpy.data.images.get(existing_name)
    if image is None and os.path.isfile(palette_path):
        image = bpy.data.images.load(palette_path)
    if image is not None:
        image.colorspace_settings.name = 'sRGB'
        tex.image = image
    tex.interpolation = 'Closest'  # NearestFilter — sharp cell edges

    nt.links.new(uv_node.outputs["UV"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    # Attach to terrain mesh. Clear existing slots so a re-run rebuilds.
    mesh = terrain_obj.data
    mesh.materials.clear()
    mesh.materials.append(mat)
    return mat


def _make_trimesh_collider(source_obj):
    """Duplicate the visible mesh data, triangulate, and link as
    `trimesh_terrain`. Hidden in viewport + render."""
    src_mesh = source_obj.data
    new_mesh = src_mesh.copy()
    new_mesh.name = "trimesh_terrain"

    bm = bmesh.new()
    bm.from_mesh(new_mesh)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.to_mesh(new_mesh)
    bm.free()

    obj = bpy.data.objects.get("trimesh_terrain")
    if obj is not None:
        bpy.data.objects.remove(obj, do_unlink=True)
    obj = bpy.data.objects.new("trimesh_terrain", new_mesh)
    obj.location = (0.0, 0.0, 0.0)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.scale = (1.0, 1.0, 1.0)
    obj.hide_viewport = True
    obj.hide_render = True
    _lib.place_in("terrain", obj)
    return obj


def _place_terrain_refs():
    """Spawn + cardinal-path-stub anchor empties. Heights sampled from the
    heightfield so they sit on the visible surface. Locations use Blender
    Z-up authoring: (runtime_x, runtime_z, runtime_y_height)."""
    h_origin = _height(0.0, 0.0)
    _lib.ref_empty("refSpawnPoint", (0.0, 0.0, h_origin), radius=0.5)
    _lib.ref_empty("refRespawn_origin", (0.0, 0.0, h_origin), radius=0.5)
    _lib.ref_empty("refPath_N", (0.0, 4.0, _height(0.0, 4.0)), radius=0.3)
    _lib.ref_empty("refPath_E", (4.0, 0.0, _height(4.0, 0.0)), radius=0.3)
    _lib.ref_empty("refPath_S", (0.0, -4.0, _height(0.0, -4.0)), radius=0.3)
    _lib.ref_empty("refPath_W", (-4.0, 0.0, _height(-4.0, 0.0)), radius=0.3)


def main():
    _lib.clear_collection("terrain")
    terrain_obj = _build_terrain_mesh()
    _ensure_palette_material(terrain_obj)
    _make_trimesh_collider(terrain_obj)
    _place_terrain_refs()
    # Always save to the canonical world.blend, not whatever's currently
    # open. save_mainfile() saves to wherever Blender thinks the file is,
    # which silently writes to a stale name if the user did Save As earlier.
    blend_path = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "world.blend"))
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(
        f"{_lib.LOG_PREFIX}[phase-02] OK - terrain 260x260m, "
        f"{GRID_RES}x{GRID_RES} verts, NE ridge, W cliff, 6 refs"
    )
    print(f"{_lib.LOG_PREFIX}[phase-02] saved -> {blend_path}")


if __name__ == "__main__":
    main()
