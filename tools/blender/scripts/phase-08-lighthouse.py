"""
Phase 8: Lighthouse + offshore islet (NW, runtime (-130, -1, +35)).

What this produces (after Run Script + save):
- Top-level `lighthouse` collection (NOT under sections/ — spec section 11.5
  treats the offshore islet as its own visual group, mirrored in
  `_lib.place_in("lighthouse", ...)`). Visible mesh objects:
    * `islet_rock`               - 4m-radius low-poly cylinder, 3m tall,
                                   spanning runtime y=-1..+2. 16 side
                                   segments. Side ring vertices have their
                                   radial distance jittered +/- 15% via
                                   random.Random(seed=8); the same jitter
                                   is applied to the top + bottom rings for
                                   each angle so the silhouette stays
                                   consistent vertically. Body palette
                                   `rock_mid`; the bottom 0.6m of side faces
                                   (runtime y=-1..-0.4, the sediment fringe
                                   below the future ocean plane + tideline)
                                   gets `sand_gravel` painted on so it reads
                                   as a sandy band that the runtime ocean
                                   plane will half-cover.
    * `lighthouse_body`          - 8m-tall tapered cylinder, 24 side
                                   segments, base radius 1.0m to top radius
                                   0.8m linearly. Authored as 8 stacked
                                   rings (4 body segments + 3 white band
                                   segments), so the side ring faces split
                                   cleanly into body rows (palette
                                   `fog_faded_distant`) and band rows
                                   (palette `sunlit_snow`). Bands are 0.2m
                                   tall centred at runtime y=4, y=6, y=8.
    * `lighthouse_cupola`        - 0.9m-radius onion-dome at the lighthouse
                                   top. Implementation: a short cylinder
                                   (0.9m radius, 0.6m tall, runtime y=10..
                                   10.6) topped with a half-sphere (0.9m
                                   radius, 0.4m tall, runtime y=10.6..11)
                                   authored as 4 latitude rings + apex.
                                   Material `world_palette_glass_material`
                                   (palette PNG clone, name carries the
                                   `glass` token so the runtime can detect
                                   transparency-hint props by material name
                                   per spec section 4.6). Palette
                                   `glacial_river`.
    * `lighthouse_lamp_emissive` - 0.25m-radius low-poly sphere (8 rings x
                                   12 segments lat-long) inside the cupola
                                   at runtime y=10.5. Palette
                                   `lantern_warm`. The `_emissive` suffix
                                   is the runtime contract for material
                                   swap + flicker (precedent:
                                   `hearth_embers_emissive`,
                                   `brazier_flame_emissive`).
    * `lighthouse_beam`          - 20m-long thin cone, 8 side segments,
                                   tapering radius 0.1m to 1.5m. Authored
                                   along Blender +X so the beam points east
                                   in author space. Material
                                   `world_palette_beam_material` (palette
                                   PNG clone, name carries the `beam`
                                   token). Parented to the beam pivot
                                   empty so runtime rotation of the empty
                                   about Blender Z sweeps the beam over
                                   the horizon. Palette `lantern_warm`.
                                   Object name also contains `beam` for
                                   double safety.

- No colliders. Per spec section 4.6 the islet sits past the r=120 soft-clamp
  so the player is pushed back before reaching it; the lighthouse is purely
  visual.

- 2 ref empties in `refs`:
    `refLighthouseLamp`        - runtime y=+10.5, radius 0.3. Runtime
                                  attaches a warm point light here.
    `refLighthouseBeamPivot`   - same position as the lamp, radius 0.3.
                                  Runtime tweens this empty's rotation
                                  ~6 deg/s about its Z axis; the beam mesh
                                  is parented to it so it sweeps.

Special material names (single-source-of-truth here):
- `world_palette_glass_material` - cupola; `*glass*` token per spec section
  4.6 lets the runtime detect transparency-hint props by material name.
- `world_palette_beam_material`  - beam; `*beam*` token per spec section
  4.6 lets the runtime detect low-opacity volumetric props.

Both new materials are full clones of `world_palette_material` (same image
texture, Closest interpolation, sRGB) - they exist purely so the runtime can
discriminate by name. The geometry still UV-snaps to the palette PNG cells.

Coordinate convention: authored in Blender Z-up. Runtime (x, y, z) maps
to Blender (x, z, y). No terrain sampling - the islet is offshore.

Idempotent: re-running clears the top-level `lighthouse` collection first.

How to run:
  1. Open tools/blender/world.blend in Blender 4.2+.
  2. Scripting workspace -> Text Editor -> Open -> phase-08-lighthouse.py.
  3. Run Script (Alt+P).
  4. Script saves world.blend automatically (wm.save_as_mainfile).
"""

import os
import sys
import math
import random

import bpy
import bmesh


# Mirror Phase 0..7's _script_dir() - Blender's Text Editor sets __file__
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


COLLECTION = "lighthouse"

# Runtime XY centre of the islet + lighthouse stack. Y=0 is sea level in
# runtime; the islet base sits 1m below sea level so the future ocean plane
# half-covers the sediment fringe.
RUNTIME_X = -130.0
RUNTIME_Z = 35.0      # runtime Z (north-south); maps to Blender Y

# Islet.
ISLET_RADIUS = 4.0
ISLET_BASE_Y = -1.0       # runtime Y at islet base (below sea level)
ISLET_TOP_Y = 2.0         # runtime Y at islet top (3m above sea level)
ISLET_SEGMENTS = 16
ISLET_JITTER = 0.15       # +/- 15% radial jitter on side ring vertices
ISLET_SAND_FRINGE_TOP_Y = -0.4   # bottom 0.6m gets sand_gravel side faces
ISLET_SEED = 8

# Lighthouse body.
TOWER_BASE_Y = ISLET_TOP_Y           # 2.0
TOWER_TOP_Y = ISLET_TOP_Y + 8.0      # 10.0
TOWER_BASE_RADIUS = 1.0
TOWER_TOP_RADIUS = 0.8
TOWER_SEGMENTS = 24

# Band centres (runtime Y) + thickness. Three bands at y=4, y=6, y=8.
BAND_CENTRES_Y = (4.0, 6.0, 8.0)
BAND_THICKNESS = 0.2

# Cupola: cylinder + hemisphere stack.
CUPOLA_RADIUS = 0.9
CUPOLA_CYL_BASE_Y = TOWER_TOP_Y                # 10.0
CUPOLA_CYL_HEIGHT = 0.6
CUPOLA_DOME_BASE_Y = CUPOLA_CYL_BASE_Y + CUPOLA_CYL_HEIGHT  # 10.6
CUPOLA_DOME_HEIGHT = 0.4
CUPOLA_SEGMENTS = 16
CUPOLA_DOME_RINGS = 4    # latitude rings between base ring and apex

# Lamp.
LAMP_RADIUS = 0.25
LAMP_Y = 10.5    # runtime Y, mid-height of cupola
LAMP_LAT_RINGS = 8
LAMP_LONG_SEGMENTS = 12

# Beam.
BEAM_LENGTH = 20.0
BEAM_BASE_RADIUS = 0.1      # at lamp end
BEAM_FAR_RADIUS = 1.5
BEAM_SEGMENTS = 8


# ============================================================================
# Material variants (glass + beam) — clones of world_palette_material with
# distinct names so the runtime can discriminate by material name token.
# ============================================================================


def _clone_palette_material(target_name):
    """Build a full clone of world_palette_material under `target_name`.

    Blender's bpy.data.materials.copy() preserves the node graph + image
    references, which is exactly what we want — the cloned material samples
    the same palette PNG so geometry that UV-snaps to palette cells still
    renders identically. The only thing that differs is the data-block name,
    so the runtime can detect by name token (*glass*, *beam*).

    Rebuilt every run (removed and recreated) so stale clones can't drift
    out of sync with the source material.
    """
    src = bpy.data.materials.get(_lib.PALETTE_MATERIAL_NAME)
    if src is None:
        src = _lib.get_palette_material()

    existing = bpy.data.materials.get(target_name)
    if existing is not None:
        bpy.data.materials.remove(existing, do_unlink=True)

    clone = src.copy()
    clone.name = target_name
    return clone


# ============================================================================
# Islet
# ============================================================================


def _build_islet(material):
    """Low-poly 4m-radius cylinder spanning runtime y=-1..+2.

    Side ring vertices have their radial distance jittered +/- ISLET_JITTER
    per angle (same jitter applied to top + bottom rings) so the silhouette
    looks like a natural sea-stack rather than a perfect cylinder. Top + bottom
    caps stay axis-aligned (cap UVs paint rock_mid). The bottom 0.6m of side
    faces (the sediment / tideline band runtime y=-1..-0.4) is painted
    sand_gravel so the ocean plane Phase 9 will add at y=0 half-covers a
    visible sand fringe.

    Authored at the origin then placed via bm_finalize_to_object so the obj's
    runtime XY centre sits at (RUNTIME_X, RUNTIME_Z).
    """
    height = ISLET_TOP_Y - ISLET_BASE_Y
    centre_runtime_y = (ISLET_BASE_Y + ISLET_TOP_Y) * 0.5
    half_h = height * 0.5

    rng = random.Random(ISLET_SEED)
    jittered_radii = []
    for _ in range(ISLET_SEGMENTS):
        factor = 1.0 + rng.uniform(-ISLET_JITTER, ISLET_JITTER)
        jittered_radii.append(ISLET_RADIUS * factor)

    # Three rings so the sand_gravel fringe is its own face row rather than
    # requiring a post-build face split. Bottom at islet base, fringe at the
    # tideline cut-off, top at islet top.
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)

    fringe_local_z = -half_h + (ISLET_SAND_FRINGE_TOP_Y - ISLET_BASE_Y)
    bottom_ring = []
    fringe_ring = []
    top_ring = []
    for i in range(ISLET_SEGMENTS):
        angle = (i / ISLET_SEGMENTS) * math.tau
        r = jittered_radii[i]
        x = math.cos(angle) * r
        y = math.sin(angle) * r
        bottom_ring.append(bm.verts.new((x, y, -half_h)))
        fringe_ring.append(bm.verts.new((x, y, fringe_local_z)))
        top_ring.append(bm.verts.new((x, y, +half_h)))

    bottom_faces = []
    top_faces = []
    for i in range(ISLET_SEGMENTS):
        j = (i + 1) % ISLET_SEGMENTS
        bottom_face = bm.faces.new((bottom_ring[i], fringe_ring[i],
                                    fringe_ring[j], bottom_ring[j]))
        bottom_faces.append(bottom_face)
        top_face = bm.faces.new((fringe_ring[i], top_ring[i],
                                 top_ring[j], fringe_ring[j]))
        top_faces.append(top_face)

    bottom_cap = bm.faces.new(list(reversed(bottom_ring)))
    top_cap = bm.faces.new(top_ring)

    for face in bottom_faces:
        _lib.paint_face(face, uv, "sand_gravel")
    for face in top_faces:
        _lib.paint_face(face, uv, "rock_mid")
    _lib.paint_face(bottom_cap, uv, "rock_mid")
    _lib.paint_face(top_cap, uv, "rock_mid")

    return _lib.bm_finalize_to_object(
        bm,
        mesh_name="islet_rock_mesh",
        obj_name="islet_rock",
        location=(RUNTIME_X, RUNTIME_Z, centre_runtime_y),
        collection_name=COLLECTION,
        material=material,
    )


# ============================================================================
# Lighthouse body — tapered cylinder, 4 body segments + 3 white bands
# ============================================================================


def _tower_radius_at(runtime_y):
    """Linear taper between TOWER_BASE_RADIUS and TOWER_TOP_RADIUS."""
    t = (runtime_y - TOWER_BASE_Y) / (TOWER_TOP_Y - TOWER_BASE_Y)
    return TOWER_BASE_RADIUS + (TOWER_TOP_RADIUS - TOWER_BASE_RADIUS) * t


def _build_tower(material):
    """8m-tall tapered cylinder built as 8 stacked rings (7 quad-ring side
    bands between them). Ring Y values in runtime are interleaved so that
    the band-row faces sit at the right heights: each band is 0.2m thick
    centred at y=4, y=6, y=8, and the body fills the gaps.

    Ring runtime Y values (bottom to top):
      r0 = 2.0   (tower base)
      r1 = 3.9   (just below first band)
      r2 = 4.1   (just above first band)
      r3 = 5.9
      r4 = 6.1
      r5 = 7.9
      r6 = 8.1
      r7 = 10.0  (tower top)

    Side face rows (band assignment):
      r0-r1: body
      r1-r2: BAND (centred y=4)
      r2-r3: body
      r3-r4: BAND (centred y=6)
      r4-r5: body
      r5-r6: BAND (centred y=8)
      r6-r7: body
    """
    half_thickness = BAND_THICKNESS * 0.5
    ring_runtime_ys = [TOWER_BASE_Y]
    for centre in BAND_CENTRES_Y:
        ring_runtime_ys.append(centre - half_thickness)
        ring_runtime_ys.append(centre + half_thickness)
    ring_runtime_ys.append(TOWER_TOP_Y)
    # Sanity: 1 + 2*3 + 1 = 8 rings.

    # bmesh authored in tower-local Z; obj origin sits at tower midpoint.
    centre_runtime_y = (TOWER_BASE_Y + TOWER_TOP_Y) * 0.5
    ring_local_zs = [y - centre_runtime_y for y in ring_runtime_ys]

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)

    rings = []
    for ring_idx, runtime_y in enumerate(ring_runtime_ys):
        radius = _tower_radius_at(runtime_y)
        z_local = ring_local_zs[ring_idx]
        ring = []
        for i in range(TOWER_SEGMENTS):
            angle = (i / TOWER_SEGMENTS) * math.tau
            x = math.cos(angle) * radius
            y = math.sin(angle) * radius
            ring.append(bm.verts.new((x, y, z_local)))
        rings.append(ring)

    # Side face rows. is_band flags rows 1, 3, 5 (0-indexed).
    band_row_indices = {1, 3, 5}
    side_face_rows = []
    for row in range(len(rings) - 1):
        ring_a = rings[row]
        ring_b = rings[row + 1]
        row_faces = []
        for i in range(TOWER_SEGMENTS):
            j = (i + 1) % TOWER_SEGMENTS
            face = bm.faces.new((ring_a[i], ring_b[i],
                                 ring_b[j], ring_a[j]))
            row_faces.append(face)
        side_face_rows.append(row_faces)

    bottom_cap = bm.faces.new(list(reversed(rings[0])))
    top_cap = bm.faces.new(rings[-1])

    for row_idx, row_faces in enumerate(side_face_rows):
        key = "sunlit_snow" if row_idx in band_row_indices else "fog_faded_distant"
        for face in row_faces:
            _lib.paint_face(face, uv, key)

    # Caps are inside the cupola anyway, but paint them with the body colour
    # so a peek from below/above reads consistent.
    _lib.paint_face(bottom_cap, uv, "fog_faded_distant")
    _lib.paint_face(top_cap, uv, "fog_faded_distant")

    return _lib.bm_finalize_to_object(
        bm,
        mesh_name="lighthouse_body_mesh",
        obj_name="lighthouse_body",
        location=(RUNTIME_X, RUNTIME_Z, centre_runtime_y),
        collection_name=COLLECTION,
        material=material,
    )


# ============================================================================
# Cupola — short cylinder + hemisphere dome
# ============================================================================


def _build_cupola(material):
    """0.9m radius cupola: cylinder base (0.6m tall) + half-sphere dome
    (0.4m tall). Authored as a single bmesh so it's one object. The half
    sphere uses CUPOLA_DOME_RINGS latitude rings between the dome base and
    the apex vertex.

    All faces paint `glacial_river`. Material is `world_palette_glass_material`
    (a name-clone of the palette material) so the runtime can detect
    transparency-hint props by material name.
    """
    centre_runtime_y = (CUPOLA_CYL_BASE_Y + CUPOLA_DOME_BASE_Y +
                        CUPOLA_DOME_HEIGHT) * 0.5
    # Local Z values: bottom of cylinder is the lowest point.
    cyl_bottom_local_z = CUPOLA_CYL_BASE_Y - centre_runtime_y
    cyl_top_local_z = CUPOLA_DOME_BASE_Y - centre_runtime_y
    apex_local_z = (CUPOLA_DOME_BASE_Y + CUPOLA_DOME_HEIGHT) - centre_runtime_y

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)

    # Cylinder rings (bottom + top of the cylindrical base).
    bottom_ring = []
    cyl_top_ring = []
    for i in range(CUPOLA_SEGMENTS):
        angle = (i / CUPOLA_SEGMENTS) * math.tau
        x = math.cos(angle) * CUPOLA_RADIUS
        y = math.sin(angle) * CUPOLA_RADIUS
        bottom_ring.append(bm.verts.new((x, y, cyl_bottom_local_z)))
        cyl_top_ring.append(bm.verts.new((x, y, cyl_top_local_z)))

    # Dome latitude rings between the dome base (same ring as cyl_top_ring)
    # and the apex. Use sin/cos to sweep latitude from 0..pi/2 (excluding
    # the endpoints so we don't duplicate cyl_top_ring or the apex vert).
    dome_rings = [cyl_top_ring]
    for lat_idx in range(1, CUPOLA_DOME_RINGS + 1):
        lat = (lat_idx / (CUPOLA_DOME_RINGS + 1)) * (math.pi * 0.5)
        ring_radius = CUPOLA_RADIUS * math.cos(lat)
        ring_local_z = cyl_top_local_z + CUPOLA_DOME_HEIGHT * math.sin(lat)
        ring = []
        for i in range(CUPOLA_SEGMENTS):
            angle = (i / CUPOLA_SEGMENTS) * math.tau
            x = math.cos(angle) * ring_radius
            y = math.sin(angle) * ring_radius
            ring.append(bm.verts.new((x, y, ring_local_z)))
        dome_rings.append(ring)
    apex = bm.verts.new((0.0, 0.0, apex_local_z))

    faces = []
    # Cylinder side quads (bottom_ring -> cyl_top_ring).
    for i in range(CUPOLA_SEGMENTS):
        j = (i + 1) % CUPOLA_SEGMENTS
        faces.append(bm.faces.new((bottom_ring[i], cyl_top_ring[i],
                                   cyl_top_ring[j], bottom_ring[j])))
    # Dome side quads.
    for ring_idx in range(len(dome_rings) - 1):
        ring_a = dome_rings[ring_idx]
        ring_b = dome_rings[ring_idx + 1]
        for i in range(CUPOLA_SEGMENTS):
            j = (i + 1) % CUPOLA_SEGMENTS
            faces.append(bm.faces.new((ring_a[i], ring_b[i],
                                       ring_b[j], ring_a[j])))
    # Apex triangles cap the top.
    top_ring = dome_rings[-1]
    for i in range(CUPOLA_SEGMENTS):
        j = (i + 1) % CUPOLA_SEGMENTS
        faces.append(bm.faces.new((top_ring[i], apex, top_ring[j])))
    # Bottom cap (reversed so normal points -Z).
    faces.append(bm.faces.new(list(reversed(bottom_ring))))

    for face in faces:
        _lib.paint_face(face, uv, "glacial_river")

    glass_mat = _clone_palette_material("world_palette_glass_material")

    return _lib.bm_finalize_to_object(
        bm,
        mesh_name="lighthouse_cupola_mesh",
        obj_name="lighthouse_cupola",
        location=(RUNTIME_X, RUNTIME_Z, centre_runtime_y),
        collection_name=COLLECTION,
        material=glass_mat,
    )


# ============================================================================
# Lamp — small emissive sphere inside the cupola
# ============================================================================


def _build_lamp(material):
    """Low-poly lat-long sphere, LAMP_LAT_RINGS rings * LAMP_LONG_SEGMENTS
    segments. Authored centred on origin then placed at (RUNTIME_X,
    RUNTIME_Z, LAMP_Y)."""
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)

    rings = []
    # Latitude rings: skip the poles (those are single verts).
    for lat_idx in range(1, LAMP_LAT_RINGS):
        # lat = 0 is bottom pole, lat = pi is top pole. Interior rings at
        # (lat_idx / LAMP_LAT_RINGS) * pi.
        lat = (lat_idx / LAMP_LAT_RINGS) * math.pi
        ring_radius = LAMP_RADIUS * math.sin(lat)
        z = -LAMP_RADIUS * math.cos(lat)
        ring = []
        for i in range(LAMP_LONG_SEGMENTS):
            angle = (i / LAMP_LONG_SEGMENTS) * math.tau
            x = math.cos(angle) * ring_radius
            y = math.sin(angle) * ring_radius
            ring.append(bm.verts.new((x, y, z)))
        rings.append(ring)

    bottom_pole = bm.verts.new((0.0, 0.0, -LAMP_RADIUS))
    top_pole = bm.verts.new((0.0, 0.0, +LAMP_RADIUS))

    faces = []
    # Triangles fan from bottom_pole to rings[0].
    first_ring = rings[0]
    for i in range(LAMP_LONG_SEGMENTS):
        j = (i + 1) % LAMP_LONG_SEGMENTS
        faces.append(bm.faces.new((bottom_pole, first_ring[i], first_ring[j])))
    # Quad strips between interior rings.
    for ring_idx in range(len(rings) - 1):
        ring_a = rings[ring_idx]
        ring_b = rings[ring_idx + 1]
        for i in range(LAMP_LONG_SEGMENTS):
            j = (i + 1) % LAMP_LONG_SEGMENTS
            faces.append(bm.faces.new((ring_a[i], ring_b[i],
                                       ring_b[j], ring_a[j])))
    # Triangles fan from last ring to top_pole.
    last_ring = rings[-1]
    for i in range(LAMP_LONG_SEGMENTS):
        j = (i + 1) % LAMP_LONG_SEGMENTS
        faces.append(bm.faces.new((last_ring[i], last_ring[j], top_pole)))

    for face in faces:
        _lib.paint_face(face, uv, "lantern_warm")

    return _lib.bm_finalize_to_object(
        bm,
        mesh_name="lighthouse_lamp_emissive_mesh",
        obj_name="lighthouse_lamp_emissive",
        location=(RUNTIME_X, RUNTIME_Z, LAMP_Y),
        collection_name=COLLECTION,
        material=material,
    )


# ============================================================================
# Beam — long thin cone parented to the pivot empty
# ============================================================================


def _build_beam(pivot_empty):
    """Author a 20m cone along Blender +X, narrow at the lamp end, wide at
    the far end. Object origin sits at the lamp centre (so the pivot's
    rotation about Z sweeps the beam tangentially). The beam mesh is built
    from base ring + far ring + base cap (sealing the lamp end).

    Material `world_palette_beam_material` carries the `*beam*` token so
    the runtime can detect low-opacity volumetric props by material name.
    Object name also contains `beam` for double safety.

    Parented to the pivot empty so runtime rotation of the pivot sweeps
    the beam over the horizon (~6 deg/s per spec section 4.6).
    """
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new(_lib.PALETTE_UV_LAYER)

    base_ring = []
    far_ring = []
    for i in range(BEAM_SEGMENTS):
        angle = (i / BEAM_SEGMENTS) * math.tau
        # The cone runs along +X, so the ring lies in the Y-Z plane and is
        # parameterised by angle around the X axis.
        y = math.cos(angle)
        z = math.sin(angle)
        base_ring.append(bm.verts.new((0.0,
                                       y * BEAM_BASE_RADIUS,
                                       z * BEAM_BASE_RADIUS)))
        far_ring.append(bm.verts.new((BEAM_LENGTH,
                                      y * BEAM_FAR_RADIUS,
                                      z * BEAM_FAR_RADIUS)))

    faces = []
    for i in range(BEAM_SEGMENTS):
        j = (i + 1) % BEAM_SEGMENTS
        faces.append(bm.faces.new((base_ring[i], far_ring[i],
                                   far_ring[j], base_ring[j])))
    # Caps. Base cap normal -X, far cap normal +X.
    faces.append(bm.faces.new(list(reversed(base_ring))))
    faces.append(bm.faces.new(far_ring))

    for face in faces:
        _lib.paint_face(face, uv, "lantern_warm")

    beam_mat = _clone_palette_material("world_palette_beam_material")

    # Object origin at lamp centre; the +X side of the mesh extends out as
    # the sweeping beam. Parented to the pivot empty so the pivot's Z
    # rotation rotates the beam tangentially around the lamp.
    beam_obj = _lib.bm_finalize_to_object(
        bm,
        mesh_name="lighthouse_beam_mesh",
        obj_name="lighthouse_beam",
        location=(RUNTIME_X, RUNTIME_Z, LAMP_Y),
        collection_name=COLLECTION,
        material=beam_mat,
    )
    beam_obj.parent = pivot_empty
    # Parenting with a non-identity parent transform would otherwise leave a
    # mismatched parent inverse; reset so the beam's world transform stays
    # at the lamp centre.
    beam_obj.matrix_parent_inverse.identity()
    return beam_obj


# ============================================================================
# Refs
# ============================================================================


def _place_refs():
    lamp_loc = (RUNTIME_X, RUNTIME_Z, LAMP_Y)
    lamp_empty = _lib.ref_empty("refLighthouseLamp", lamp_loc, radius=0.3)
    pivot_empty = _lib.ref_empty(
        "refLighthouseBeamPivot", lamp_loc, radius=0.3
    )
    return lamp_empty, pivot_empty


# ============================================================================
# Entry point
# ============================================================================


def main():
    _lib.clear_collection(COLLECTION)

    material = _lib.get_palette_material()

    _build_islet(material)
    _build_tower(material)
    _build_cupola(material)
    _build_lamp(material)

    _, pivot_empty = _place_refs()
    _build_beam(pivot_empty)

    lighthouse_coll = bpy.data.collections[COLLECTION]
    visible_count = len([o for o in lighthouse_coll.objects
                         if not o.hide_viewport])

    blend_path = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "world.blend"))
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    print(
        f"{_lib.LOG_PREFIX}[phase-08] OK - lighthouse: islet + tower + "
        f"cupola + beam, 0 colliders, 2 refs"
    )
    print(f"{_lib.LOG_PREFIX}[phase-08] saved -> {blend_path}")


if __name__ == "__main__":
    main()
