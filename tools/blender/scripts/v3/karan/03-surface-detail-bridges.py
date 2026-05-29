"""Place bridge meshes across karan's river — tune-by-iteration.

This is the section-03 bridges delta. It places Bruno's bridge mesh
(`Cube.211`, loaded by the foundation) over karan's water and links it into the
`bridges` collection, mounting `scenery.002` at scene root so it renders.

Placement is DERIVED, not hardcoded blindly:
  - The target sits on karan's MAIN_RIVER (see 02-ground-grass-base.py), default
    pixel (240, 285) — roughly mid-river, near world center.
  - Pixel->world uses the documented terrain axis mapping (Image X -> screen
    TOP->BOTTOM = world +Y->-Y; Image Y -> screen LEFT->RIGHT = world -X->+X)
    and the terrain object's ACTUAL world bounding box, read at runtime — so the
    world size/centre come from the live mesh, not a guessed 125m.
  - Yaw is set perpendicular to the local river tangent (so the deck crosses the
    channel rather than running along it).

What CAN'T be verified outside Blender (so they're exposed as knobs to tune):
  - The bridge mesh's real footprint / native long-axis -> BRIDGE_SCALE, YAW_DEG.
  - Exact deck height over the water -> BRIDGE_Z.
After running once, snap the 3D cursor (Shift+Right-click) onto the exact spot
you want and read N-panel > View > 3D Cursor XYZ; set TARGET_WORLD to that for
a pixel-perfect placement.

Keep-everything policy: only ADDS bridge objects + mounts an existing
collection. Removes nothing.

Run on the already-built karan world (open world-v3-karan.blend) for fast
placement iteration:
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/03-surface-detail-bridges.py').read())
"""
import math

import bmesh
import bpy
import numpy as np

BRIDGE_MESH = "Cube.211"          # Bruno's bridgePhysicalFixed mesh (foundation 005)
CURVED_BRIDGE_MESH = "Cube.211.bridge02.curved"
TERRAIN_OBJECT = "terrain"
WATER_IMAGE = "terrainWater"
BRIDGES_COLLECTION = "bridges"
CONTAINER_COLLECTION = "scenery.002"
BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"

# --- placement knobs (tune these after the first look) ---
# Target on the river, in terrainWater EXR pixel space (same space as base.py
# waypoints). (240, 285) ~ mid-river. Neighbours used for the flow tangent.
TARGET_PIXEL = (240, 285)
RIVER_NEIGHBOURS = ((160, 310), (310, 250))   # prev/next MAIN_RIVER waypoints
TARGET_WORLD = (0.513066291809082, 7.893685340881348)   # locked from manual placement in Blender (world X, Y)
# Terrain mesh-LOCAL XY (the N-panel "Local" readout in edit mode on the terrain).
# Converted to world via the terrain's real transform, so the 0.651 scale is handled.
# Set None to fall back to TARGET_PIXEL. Highest priority after TARGET_WORLD.
TARGET_TERRAIN_LOCAL = (-7.5, 11.25)   # midpoint of your two N-panel points
BRIDGE_Z = 0.0970078706741333           # deck height (locked from manual placement)
BRIDGE_WIDTH_SCALE = 0.800000011920929   # local X width, locked from Blender
BRIDGE_LENGTH_SCALE = 0.8134106993675232  # local Y span, locked from Blender
BRIDGE_HEIGHT_SCALE = 1.0  # local Z height, kept native
YAW_DEG = 158.19858759340923            # locked from manual placement (was auto perpendicular-to-river)

# Distinct bridge colour (object-level override, leaves Bruno's palette mesh
# untouched). Default = warm wood-brown. Just tell me a colour to change this.
BRIDGE_COLOR = (0.205, 0.095, 0.035, 1.0)   # deeper walnut-brown, less orange than the first pass
BRIDGE_SLAT_COLORS = (
    (0.95, 0.58, 0.045, 1.0), # saturated golden-yellow plank
    (0.72, 0.40, 0.025, 1.0), # dark mustard plank
    (1.00, 0.70, 0.08, 1.0),  # bright honey-yellow plank
)
BRIDGE_SUPPORT_COLOR = (0.58, 0.30, 0.018, 1.0)
BRIDGE_MATERIAL = "bridge"
BRIDGE02_COLOR = (0.86, 0.52, 0.035, 1.0)
BRIDGE02_DARK_COLOR = (0.62, 0.33, 0.018, 1.0)
BRIDGE02_MATERIAL = "bridge_curved_golden_oak"
BRIDGE02_DARK_MATERIAL = "bridge_curved_dark_amber"
BRIDGE_SLAT_MATERIALS = ("bridge_deck_slats_honey", "bridge_deck_slats_amber", "bridge_deck_slats_gold")
BRIDGE_SUPPORT_MATERIAL = "bridge_deck_supports"
BRIDGE_ENDCAP_MATERIAL = "bridge_end_caps"

BRIDGES = [
    {
        "name": "bridge01",
        "location": (0.513066291809082, 7.893685340881348, BRIDGE_Z),
        "yaw_deg": YAW_DEG,
        "scale": (BRIDGE_WIDTH_SCALE, BRIDGE_LENGTH_SCALE, BRIDGE_HEIGHT_SCALE),
    },
    {
        "name": "bridge02",
        # Derived from four 3D-cursor points:
        # left edge (31.50, 12.87), (34.14, 12.81)
        # right edge (45.09, 42.10), (48.09, 40.59)
        # The location compensates for Cube.211's off-centre mesh origin.
        "mesh": CURVED_BRIDGE_MESH,
        "source_mesh": BRIDGE_MESH,
        "location": (35.9207649230957, 18.34620475769043, 0.02),
        "yaw_deg": -25.78394021113604,
        "scale": (1.0743212699890137, 3.1088290214538574, 0.9691963195800781),
        "arch_height": 2.6,
        "bridge_color": BRIDGE02_COLOR,
        "bridge_material": BRIDGE02_MATERIAL,
        "bridge_dark_color": BRIDGE02_DARK_COLOR,
        "bridge_dark_material": BRIDGE02_DARK_MATERIAL,
        "deck_slats": {
            "count": 42,
            "x_min": -1.92,
            "x_max": 1.92,
            "y_padding": 0.08,
            "depth": 0.17,
            "thickness": 0.09,
            "deck_z": 0.245,
        },
        "deck_supports": {
            "x_positions": (-1.24, 0.0, 1.24),
            "width": 0.16,
            "thickness": 0.14,
            "segments": 58,
            "z_gap": 0.015,
            "landing_depth": 0.72,
            "landing_height": 0.62,
        },
        "end_caps": {
            "x_positions": (-2.06, 2.06),
            "post_width": 0.46,
            "end_depth": 0.52,
            "base_z": -0.65,
            "top_z": 1.65,
            "rail_width": 0.16,
            "rail_height": 0.14,
            "rail_y_padding": 0.18,
            "rail_z_levels": (0.72, 1.18, 1.50),
        },
        # far-left pillar clone retired: _symmetrize_across_x now mirrors the
        # real far-right pillar onto the left, so the clone would z-fight.
        "middle_pillar_covers": {
            "name": "bridge02_middle_pillar_covers",
            "x_ranges": ((-2.38, -1.80), (1.80, 2.38)),
            "y_ranges": ((1.72, 2.27), (4.48, 5.03)),
            "z_range": (0.45, 3.95),
        },
        "entrance_pillar_covers": {
            "name": "bridge02_entrance_pillar_covers",
            "x_ranges": ((-2.38, -1.80), (1.80, 2.38)),
            "y_range": (-0.97, -0.42),
            "z_range": (-0.80, 2.05),
        },
    },
]


def _terrain_extent():
    """World-space (centre_x, centre_y, size_x, size_y) of the terrain mesh."""
    ob = bpy.data.objects.get(TERRAIN_OBJECT)
    if ob is None:
        return None
    corners = [ob.matrix_world @ mathutils_vec(c) for c in ob.bound_box]
    xs = [c.x for c in corners]
    ys = [c.y for c in corners]
    return (
        (min(xs) + max(xs)) * 0.5,
        (min(ys) + max(ys)) * 0.5,
        max(xs) - min(xs),
        max(ys) - min(ys),
    )


def mathutils_vec(seq):
    import mathutils
    return mathutils.Vector(seq)


def _apply_bridge_color(ob, color=BRIDGE_COLOR, material_name=BRIDGE_MATERIAL):
    """Object-level material override so only this bridge recolours; mesh + palette stay Bruno's."""
    mat = bpy.data.materials.get(material_name)
    if mat is None:
        mat = bpy.data.materials.new(material_name)
    if not getattr(mat, "node_tree", None):
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF") if mat.node_tree else None
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = 0.78
    mat.diffuse_color = color  # solid-view fallback colour
    if not ob.material_slots:
        # mesh has no slots — give the object one without editing the shared mesh
        ob.data.materials.append(mat)
    for slot in ob.material_slots:
        slot.link = "OBJECT"
        slot.material = mat
    print(f"  colour: {material_name!r} base {tuple(round(c, 2) for c in color)} "
          f"(object-level override on {len(ob.material_slots)} slot(s))")


def _solid_material(name, color):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    if not getattr(mat, "node_tree", None):
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF") if mat.node_tree else None
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = 0.72
    return mat


def _apply_curved_bridge_materials(ob, spec):
    light = _solid_material(spec["bridge_material"], spec["bridge_color"])
    dark = _solid_material(spec["bridge_dark_material"], spec["bridge_dark_color"])
    ob.data.materials.clear()
    ob.data.materials.append(light)
    ob.data.materials.append(dark)
    for polygon in ob.data.polygons:
        center = polygon.center
        is_post_or_end = abs(center.x) > 1.65 or center.y < -0.25 or center.y > 7.2
        is_under_detail = center.z < 0.35
        polygon.material_index = 1 if is_post_or_end or is_under_detail else 0
    for slot in ob.material_slots:
        slot.link = "DATA"
    print(f"  colour: {spec['bridge_material']!r}/{spec['bridge_dark_material']!r} "
          "assigned by bridge part")


def _use_asset_materials(ob):
    """Clear stale object overrides so imported GLB materials drive the bridge."""
    for index in range(len(ob.data.materials) - 1, -1, -1):
        mat = ob.data.materials[index]
        if mat and mat.name == BRIDGE_MATERIAL and len(ob.data.materials) > 1:
            ob.data.materials.pop(index=index)
    for slot in ob.material_slots:
        slot.link = "DATA"


def _make_curved_bridge_mesh(source_name, mesh_name, arch_height):
    """Copy the Bruno bridge mesh and lift its middle into a broad arch."""
    source = bpy.data.meshes.get(source_name)
    if source is None:
        print(f"  [ABORT] bridge source mesh {source_name!r} not found.")
        return None

    existing = bpy.data.meshes.get(mesh_name)
    if existing is not None:
        for ob in bpy.data.objects:
            if ob.type == "MESH" and ob.data == existing:
                ob.data = source
        bpy.data.meshes.remove(existing, do_unlink=True)

    mesh = source.copy()
    mesh.name = mesh_name
    removed = _remove_original_deck_boards(mesh)
    removed += _remove_stray_side_plank(mesh)
    dropped, mirrored = _symmetrize_across_x(mesh)
    print(f"  symmetrized {mesh_name!r}: dropped {dropped} left faces, "
          f"mirrored {mirrored} right faces onto the left")
    y_values = [v.co.y for v in mesh.vertices]
    min_y = min(y_values)
    max_y = max(y_values)
    span = max(max_y - min_y, 0.0001)

    for vertex in mesh.vertices:
        t = ((vertex.co.y - min_y) / span) * 2.0 - 1.0
        vertex.co.z += arch_height * max(0.0, 1.0 - t * t)
    mesh.update()
    print(f"  removed {removed} original deck faces from {mesh_name!r}")
    return mesh


def _remove_original_deck_boards(mesh):
    """Remove Cube.211's broad centre deck boards so generated slats are the deck."""
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()
    remove_faces = []
    for face in bm.faces:
        center = face.calc_center_median()
        if abs(center.x) <= 1.83 and -0.25 <= center.z <= 0.45:
            remove_faces.append(face)
    bmesh.ops.delete(bm, geom=remove_faces, context="FACES")
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return len(remove_faces)


def _remove_stray_side_plank(mesh):
    """Remove the detached long side plank that sits outside the curved bridge."""
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()
    remove_faces = []
    for face in bm.faces:
        center = face.calc_center_median()
        negative_side_plank = center.x < -2.55 and center.y > 5.0
        positive_side_plank = center.x > 2.45 and 1.7 < center.y < 2.25
        weak_far_left_pillar = center.x < -1.65 and center.y > 7.15
        if negative_side_plank or positive_side_plank or weak_far_left_pillar:
            remove_faces.append(face)
    bmesh.ops.delete(bm, geom=remove_faces, context="FACES")
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return len(remove_faces)


def _symmetrize_across_x(mesh, tol=0.02):
    """Make the bridge mirror-symmetric by replacing the -X half with a mirror
    of the fuller +X half.

    Bruno's Cube.211 was modelled with a complete railing (all rail bars +
    corner posts) on +X and a stripped-down one on -X, so left/right never
    matched. Dropping the -X faces and mirroring the +X faces guarantees the
    four corner pillars, the four middle pillars, AND every rail line up.
    Centre-spine faces straddling x=0 are kept as-is (not duplicated).
    """
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()
    drop = [f for f in bm.faces if f.calc_center_median().x < -tol]
    bmesh.ops.delete(bm, geom=drop, context="FACES")
    bm.faces.ensure_lookup_table()
    src = [f for f in bm.faces if f.calc_center_median().x > tol]
    dup = bmesh.ops.duplicate(bm, geom=src)["geom"]
    for element in dup:
        if isinstance(element, bmesh.types.BMVert):
            element.co.x = -element.co.x
    dup_faces = [e for e in dup if isinstance(e, bmesh.types.BMFace)]
    bmesh.ops.reverse_faces(bm, faces=dup_faces)   # mirroring inverts winding
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return len(drop), len(dup_faces)


def _arched_z(y, min_y, max_y, deck_z, arch_height):
    span = max(max_y - min_y, 0.0001)
    t = ((y - min_y) / span) * 2.0 - 1.0
    return deck_z + arch_height * max(0.0, 1.0 - t * t)


def _cuboid_vertices(x_min, x_max, y_min, y_max, z_min, z_max):
    return [
        (x_min, y_min, z_min), (x_max, y_min, z_min),
        (x_max, y_max, z_min), (x_min, y_max, z_min),
        (x_min, y_min, z_max), (x_max, y_min, z_max),
        (x_max, y_max, z_max), (x_min, y_max, z_max),
    ]


def _append_cuboid(vertices, faces, x_min, x_max, y_min, y_max, z_min, z_max):
    offset = len(vertices)
    vertices.extend(_cuboid_vertices(x_min, x_max, y_min, y_max, z_min, z_max))
    faces.extend([
        (offset + 0, offset + 1, offset + 2, offset + 3),
        (offset + 4, offset + 7, offset + 6, offset + 5),
        (offset + 0, offset + 4, offset + 5, offset + 1),
        (offset + 1, offset + 5, offset + 6, offset + 2),
        (offset + 2, offset + 6, offset + 7, offset + 3),
        (offset + 3, offset + 7, offset + 4, offset + 0),
    ])


def _remove_object(name):
    ob = bpy.data.objects.get(name)
    if ob is not None:
        bpy.data.objects.remove(ob, do_unlink=True)


def _build_deck_slats(bridge_ob, coll, spec):
    slats = spec.get("deck_slats")
    if not slats:
        _remove_object(f"{bridge_ob.name}_deck_slats")
        _remove_object(f"{bridge_ob.name}_deck_supports")
        return

    mesh = bridge_ob.data
    y_values = [v.co.y for v in mesh.vertices]
    min_y = min(y_values)
    max_y = max(y_values)
    start_y = min_y + slats["y_padding"]
    end_y = max_y - slats["y_padding"]
    count = slats["count"]
    step = (end_y - start_y) / max(count - 1, 1)
    half_depth = slats["depth"] * 0.5
    half_thickness = slats["thickness"] * 0.5
    arch_height = spec.get("arch_height", 0.0)

    vertices = []
    faces = []
    for index in range(count):
        y = start_y + index * step
        z = _arched_z(y, min_y, max_y, slats["deck_z"], arch_height)
        _append_cuboid(
            vertices,
            faces,
            slats["x_min"],
            slats["x_max"],
            y - half_depth,
            y + half_depth,
            z - half_thickness,
            z + half_thickness,
        )

    slat_mesh_name = f"{bridge_ob.name}_deck_slats_mesh"
    old_mesh = bpy.data.meshes.get(slat_mesh_name)
    if old_mesh is not None:
        bpy.data.meshes.remove(old_mesh, do_unlink=True)
    slat_mesh = bpy.data.meshes.new(slat_mesh_name)
    slat_mesh.from_pydata(vertices, [], faces)
    slat_mesh.update()
    for material_name, color in zip(BRIDGE_SLAT_MATERIALS, BRIDGE_SLAT_COLORS):
        slat_mesh.materials.append(_solid_material(material_name, color))
    for index, face in enumerate(slat_mesh.polygons):
        face.material_index = (index // 6) % len(BRIDGE_SLAT_COLORS)

    slat_name = f"{bridge_ob.name}_deck_slats"
    _remove_object(slat_name)
    slat_ob = bpy.data.objects.new(slat_name, slat_mesh)
    slat_ob.location = bridge_ob.location
    slat_ob.rotation_mode = bridge_ob.rotation_mode
    slat_ob.rotation_euler = bridge_ob.rotation_euler
    slat_ob.scale = bridge_ob.scale
    coll.objects.link(slat_ob)
    print(f"  added {count} thinner deck slats on {bridge_ob.name!r}")
    _build_deck_supports(bridge_ob, coll, spec, min_y, max_y, start_y, end_y)


def _build_deck_supports(bridge_ob, coll, spec, min_y, max_y, start_y, end_y):
    supports = spec.get("deck_supports")
    slats = spec.get("deck_slats")
    if not supports:
        _remove_object(f"{bridge_ob.name}_deck_supports")
        return

    arch_height = spec.get("arch_height", 0.0)
    deck_z = slats["deck_z"]
    slat_half_thickness = slats["thickness"] * 0.5
    support_half_thickness = supports["thickness"] * 0.5
    x_half = supports["width"] * 0.5
    segments = supports["segments"]
    y_step = (end_y - start_y) / max(segments, 1)
    y_half = y_step * 0.49

    vertices = []
    faces = []
    for x in supports["x_positions"]:
        for index in range(segments):
            y = start_y + (index + 0.5) * y_step
            z = (
                _arched_z(y, min_y, max_y, deck_z, arch_height)
                - slat_half_thickness
                - support_half_thickness
                - supports["z_gap"]
            )
            _append_cuboid(
                vertices,
                faces,
                x - x_half,
                x + x_half,
                y - y_half,
                y + y_half,
                z - support_half_thickness,
                z + support_half_thickness,
            )
    _append_end_landings(
        vertices,
        faces,
        slats,
        supports,
        min_y,
        max_y,
        start_y,
        end_y,
        deck_z,
        arch_height,
    )

    support_mesh_name = f"{bridge_ob.name}_deck_supports_mesh"
    old_mesh = bpy.data.meshes.get(support_mesh_name)
    if old_mesh is not None:
        bpy.data.meshes.remove(old_mesh, do_unlink=True)
    support_mesh = bpy.data.meshes.new(support_mesh_name)
    support_mesh.from_pydata(vertices, [], faces)
    support_mesh.update()
    support_mesh.materials.append(_solid_material(BRIDGE_SUPPORT_MATERIAL, BRIDGE_SUPPORT_COLOR))

    support_name = f"{bridge_ob.name}_deck_supports"
    _remove_object(support_name)
    support_ob = bpy.data.objects.new(support_name, support_mesh)
    support_ob.location = bridge_ob.location
    support_ob.rotation_mode = bridge_ob.rotation_mode
    support_ob.rotation_euler = bridge_ob.rotation_euler
    support_ob.scale = bridge_ob.scale
    coll.objects.link(support_ob)
    print(f"  added {len(supports['x_positions'])} arched deck support beams on {bridge_ob.name!r}")
    _build_end_caps(bridge_ob, coll, spec, min_y, max_y)


def _append_end_landings(vertices, faces, slats, supports, min_y, max_y,
                         start_y, end_y, deck_z, arch_height):
    """Add shallow abutment blocks below the first/last boards so ends feel seated."""
    landing_depth = supports["landing_depth"]
    landing_height = supports["landing_height"]
    top_gap = supports["z_gap"]
    slat_half_thickness = slats["thickness"] * 0.5

    for y0, y1, sample_y in (
        (start_y, min(start_y + landing_depth, end_y), start_y),
        (max(end_y - landing_depth, start_y), end_y, end_y),
    ):
        top = (
            _arched_z(sample_y, min_y, max_y, deck_z, arch_height)
            - slat_half_thickness
            - top_gap
        )
        _append_cuboid(
            vertices,
            faces,
            slats["x_min"],
            slats["x_max"],
            y0,
            y1,
            top - landing_height,
            top,
        )


def _build_end_caps(bridge_ob, coll, spec, min_y, max_y):
    end_caps = spec.get("end_caps")
    if not end_caps:
        _remove_object(f"{bridge_ob.name}_end_caps")
        return

    half_rail_width = end_caps["rail_width"] * 0.5
    half_rail_height = end_caps["rail_height"] * 0.5
    rail_y_min = min_y + end_caps["rail_y_padding"]
    rail_y_max = max_y - end_caps["rail_y_padding"]
    vertices = []
    faces = []

    for z in end_caps["rail_z_levels"]:
        for x in end_caps["x_positions"]:
            _append_cuboid(
                vertices,
                faces,
                x - half_rail_width,
                x + half_rail_width,
                rail_y_min,
                rail_y_max,
                z - half_rail_height,
                z + half_rail_height,
            )

    endcap_mesh_name = f"{bridge_ob.name}_end_caps_mesh"
    old_mesh = bpy.data.meshes.get(endcap_mesh_name)
    if old_mesh is not None:
        bpy.data.meshes.remove(old_mesh, do_unlink=True)
    endcap_mesh = bpy.data.meshes.new(endcap_mesh_name)
    endcap_mesh.from_pydata(vertices, [], faces)
    endcap_mesh.update()
    endcap_mesh.materials.append(_solid_material(BRIDGE_ENDCAP_MATERIAL, BRIDGE02_DARK_COLOR))

    endcap_name = f"{bridge_ob.name}_end_caps"
    _remove_object(endcap_name)
    endcap_ob = bpy.data.objects.new(endcap_name, endcap_mesh)
    endcap_ob.location = bridge_ob.location
    endcap_ob.rotation_mode = bridge_ob.rotation_mode
    endcap_ob.rotation_euler = bridge_ob.rotation_euler
    endcap_ob.scale = bridge_ob.scale
    coll.objects.link(endcap_ob)
    print(f"  added matching end caps on {bridge_ob.name!r}")


def _build_missing_pillar_clone(bridge_ob, coll, spec):
    clone = spec.get("missing_pillar_clone")
    if not clone:
        _remove_object(f"{bridge_ob.name}_far_left_pillar_clone")
        return

    mesh = bridge_ob.data
    source_faces = [
        polygon for polygon in mesh.polygons
        if polygon.center.x > 1.65 and polygon.center.y > 7.15
    ]
    if not source_faces:
        print(f"  [WARN] no source faces found for {clone['name']!r}")
        return

    vertices = []
    faces = []
    material_indices = []
    vertex_map = {}
    for polygon in source_faces:
        face_indices = []
        for source_index in polygon.vertices:
            if source_index not in vertex_map:
                co = mesh.vertices[source_index].co
                vertex_map[source_index] = len(vertices)
                vertices.append((-co.x, co.y, co.z))
            face_indices.append(vertex_map[source_index])
        faces.append(tuple(face_indices))
        material_indices.append(polygon.material_index)

    clone_mesh_name = f"{clone['name']}_mesh"
    old_mesh = bpy.data.meshes.get(clone_mesh_name)
    if old_mesh is not None:
        bpy.data.meshes.remove(old_mesh, do_unlink=True)
    clone_mesh = bpy.data.meshes.new(clone_mesh_name)
    clone_mesh.from_pydata(vertices, [], faces)
    clone_mesh.update()
    for material in mesh.materials:
        clone_mesh.materials.append(material)
    for polygon, material_index in zip(clone_mesh.polygons, material_indices):
        polygon.material_index = material_index

    _remove_object(clone["name"])
    clone_ob = bpy.data.objects.new(clone["name"], clone_mesh)
    clone_ob.location = bridge_ob.location
    clone_ob.rotation_mode = bridge_ob.rotation_mode
    clone_ob.rotation_euler = bridge_ob.rotation_euler
    clone_ob.scale = bridge_ob.scale
    coll.objects.link(clone_ob)
    print(f"  cloned far-right pillar geometry into missing far-left corner")


def _build_middle_pillar_covers(bridge_ob, coll, spec):
    covers = spec.get("middle_pillar_covers")
    if not covers:
        _remove_object(f"{bridge_ob.name}_middle_pillar_covers")
        return

    vertices = []
    faces = []
    z_min, z_max = covers["z_range"]
    for x_min, x_max in covers["x_ranges"]:
        for y_min, y_max in covers["y_ranges"]:
            _append_cuboid(vertices, faces, x_min, x_max, y_min, y_max, z_min, z_max)

    cover_mesh_name = f"{covers['name']}_mesh"
    old_mesh = bpy.data.meshes.get(cover_mesh_name)
    if old_mesh is not None:
        bpy.data.meshes.remove(old_mesh, do_unlink=True)
    cover_mesh = bpy.data.meshes.new(cover_mesh_name)
    cover_mesh.from_pydata(vertices, [], faces)
    cover_mesh.update()
    cover_mesh.materials.append(_solid_material(BRIDGE_ENDCAP_MATERIAL, BRIDGE02_DARK_COLOR))

    _remove_object(covers["name"])
    cover_ob = bpy.data.objects.new(covers["name"], cover_mesh)
    cover_ob.location = bridge_ob.location
    cover_ob.rotation_mode = bridge_ob.rotation_mode
    cover_ob.rotation_euler = bridge_ob.rotation_euler
    cover_ob.scale = bridge_ob.scale
    coll.objects.link(cover_ob)
    print(f"  added matching covers for four middle pillars")


def _build_entrance_pillar_covers(bridge_ob, coll, spec):
    covers = spec.get("entrance_pillar_covers")
    if not covers:
        _remove_object(f"{bridge_ob.name}_entrance_pillar_covers")
        return

    vertices = []
    faces = []
    y_min, y_max = covers["y_range"]
    z_min, z_max = covers["z_range"]
    for x_min, x_max in covers["x_ranges"]:
        _append_cuboid(vertices, faces, x_min, x_max, y_min, y_max, z_min, z_max)

    cover_mesh_name = f"{covers['name']}_mesh"
    old_mesh = bpy.data.meshes.get(cover_mesh_name)
    if old_mesh is not None:
        bpy.data.meshes.remove(old_mesh, do_unlink=True)
    cover_mesh = bpy.data.meshes.new(cover_mesh_name)
    cover_mesh.from_pydata(vertices, [], faces)
    cover_mesh.update()
    cover_mesh.materials.append(_solid_material(BRIDGE_ENDCAP_MATERIAL, BRIDGE02_DARK_COLOR))

    _remove_object(covers["name"])
    cover_ob = bpy.data.objects.new(covers["name"], cover_mesh)
    cover_ob.location = bridge_ob.location
    cover_ob.rotation_mode = bridge_ob.rotation_mode
    cover_ob.rotation_euler = bridge_ob.rotation_euler
    cover_ob.scale = bridge_ob.scale
    coll.objects.link(cover_ob)
    print(f"  added matching covers for entrance pillars")


def _pixel_to_world(img_x, img_y, ext, w, h):
    """terrainWater pixel (col=img_x, row=img_y) -> world (x, y) via documented mapping."""
    cx, cy, sx, sy = ext
    wx = (img_y / (h - 1) - 0.5) * sx + cx      # Image Y -> screen L->R -> world X
    wy = (0.5 - img_x / (w - 1)) * sy + cy      # Image X -> screen T->B -> world Y
    return wx, wy


def _mesh_for_spec(default_mesh, spec):
    source_mesh = spec.get("source_mesh")
    if source_mesh:
        return _make_curved_bridge_mesh(
            source_mesh,
            spec["mesh"],
            spec.get("arch_height", 0.0),
        )
    return default_mesh


def _place_bridge(default_mesh, coll, spec):
    mesh = _mesh_for_spec(default_mesh, spec)
    if mesh is None:
        return
    ob = bpy.data.objects.get(spec["name"])
    if ob is None:
        ob = bpy.data.objects.new(spec["name"], mesh)
    ob.data = mesh
    ob.location = spec["location"]
    ob.rotation_mode = "XYZ"
    ob.rotation_euler = (0.0, 0.0, math.radians(spec["yaw_deg"]))
    ob.scale = spec["scale"]
    try:
        ob.display_type = "TEXTURED"
    except Exception:
        pass
    if ob.name not in {o.name for o in coll.objects}:
        try:
            coll.objects.link(ob)
        except Exception:
            pass
    if spec.get("bridge_dark_color") is not None:
        _apply_curved_bridge_materials(ob, spec)
    elif spec.get("bridge_color", BRIDGE_COLOR) is not None:
        _apply_bridge_color(
            ob,
            spec.get("bridge_color", BRIDGE_COLOR),
            spec.get("bridge_material", BRIDGE_MATERIAL),
        )
    else:
        _use_asset_materials(ob)
    _build_deck_slats(ob, coll, spec)
    _build_missing_pillar_clone(ob, coll, spec)
    _build_middle_pillar_covers(ob, coll, spec)
    _build_entrance_pillar_covers(ob, coll, spec)
    print(f"  placed {ob.name!r} at {tuple(round(v, 3) for v in ob.location)} "
          f"yaw {spec['yaw_deg']:.2f} scale {tuple(round(v, 3) for v in ob.scale)}")


def run():
    print("[03-surface-detail-bridges] place bridges across karan's river")

    mesh = bpy.data.meshes.get(BRIDGE_MESH)
    if mesh is None:
        print(f"  [ABORT] bridge mesh {BRIDGE_MESH!r} not found.")
        print(f"    diagnostics: {len(bpy.data.meshes)} meshes, "
              f"{len(bpy.data.objects)} objects loaded.")
        print(f"    Plane.134 (terrain mesh) present? {'Plane.134' in bpy.data.meshes}")
        print(f"    Cube.156 (other bridge mesh) present? {'Cube.156' in bpy.data.meshes}")
        print(f"    terrain object present? {'terrain' in bpy.data.objects}")
        near = [m.name for m in bpy.data.meshes if m.name.startswith('Cube.21')]
        print(f"    meshes named Cube.21*: {near[:12]}")
        print("    => if these are mostly empty/False, the open file is NOT the "
              "fully-built karan world. Rebuild it with karan/02-ground-grass-run-all.py "
              "(or reopen world-v3-karan.blend) and re-run this.")
        return

    ext = _terrain_extent()
    if ext is None:
        print(f"  [ABORT] terrain object {TERRAIN_OBJECT!r} not found")
        return
    cx, cy, sx, sy = ext
    print(f"  terrain extent: centre=({cx:.2f}, {cy:.2f}) size=({sx:.2f} x {sy:.2f}) m")

    img = bpy.data.images.get(WATER_IMAGE)
    w, h = (img.size if img else (512, 512))

    # --- target world position ---
    if TARGET_WORLD is not None:
        wx, wy = TARGET_WORLD
        print(f"  target: world override ({wx:.2f}, {wy:.2f})")
    elif TARGET_TERRAIN_LOCAL is not None:
        import mathutils
        terrain = bpy.data.objects.get(TERRAIN_OBJECT)
        local = mathutils.Vector((TARGET_TERRAIN_LOCAL[0], TARGET_TERRAIN_LOCAL[1], 0.0))
        wco = terrain.matrix_world @ local
        wx, wy = wco.x, wco.y
        print(f"  target: terrain-local {TARGET_TERRAIN_LOCAL} -> world ({wx:.2f}, {wy:.2f})")
    else:
        wx, wy = _pixel_to_world(TARGET_PIXEL[0], TARGET_PIXEL[1], ext, w, h)
        print(f"  target: pixel {TARGET_PIXEL} -> world ({wx:.2f}, {wy:.2f})")
        if img is not None:
            chans = img.channels
            px = np.asarray(img.pixels[:], dtype=np.float32).reshape((h, w, chans))
            r = float(px[TARGET_PIXEL[1], TARGET_PIXEL[0], 0])
            verdict = "WATER" if r > 0.05 else "DRY (!) move TARGET_PIXEL onto the river"
            print(f"  water-mask R at target = {r:.2f} -> {verdict}")

    # --- yaw: perpendicular to local river flow ---
    if YAW_DEG is not None:
        yaw = math.radians(YAW_DEG)
        print(f"  yaw: override {YAW_DEG} deg")
    else:
        (ax, ay), (bx, by) = RIVER_NEIGHBOURS
        wax, way = _pixel_to_world(ax, ay, ext, w, h)
        wbx, wby = _pixel_to_world(bx, by, ext, w, h)
        flow = (wbx - wax, wby - way)
        yaw = math.atan2(-flow[0], flow[1])   # perpendicular to flow vector
        print(f"  yaw: auto perpendicular-to-river = {math.degrees(yaw):.1f} deg")

    # --- collections: mount scenery.002 at root, link bridge under bridges ---
    container = bpy.data.collections.get(CONTAINER_COLLECTION)
    if container and container.name not in {c.name for c in bpy.context.scene.collection.children}:
        try:
            bpy.context.scene.collection.children.link(container)
        except Exception:
            pass
    coll = bpy.data.collections.get(BRIDGES_COLLECTION) or bpy.data.collections.new(BRIDGES_COLLECTION)

    for spec in BRIDGES:
        _place_bridge(mesh, coll, spec)

    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")


if __name__ == "__main__":
    run()
