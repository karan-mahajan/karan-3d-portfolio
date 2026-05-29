"""Place bridge meshes across karan's river — tune-by-iteration.

This is the section-03 bridges delta. It instantiates Bruno's bridge mesh
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

import bpy
import numpy as np

BRIDGE_MESH = "Cube.211"          # Bruno's bridgePhysicalFixed mesh (foundation 005)
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
BRIDGE_COLOR = (0.2541521489620209, 0.10224173218011856, 0.043735045939683914, 1.0)   # sRGB #8a5a3b (locked from Blender)
BRIDGE_MATERIAL = "bridge"

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
        "location": (35.9207649230957, 18.34620475769043, BRIDGE_Z),
        "yaw_deg": -25.78394021113604,
        "scale": (1.0743212699890137, 3.1088290214538574, 0.9691963195800781),
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


def _apply_bridge_color(ob):
    """Object-level material override so only this bridge recolours; mesh + palette stay Bruno's."""
    mat = bpy.data.materials.get(BRIDGE_MATERIAL)
    if mat is None:
        mat = bpy.data.materials.new(BRIDGE_MATERIAL)
    if not getattr(mat, "node_tree", None):
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF") if mat.node_tree else None
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = BRIDGE_COLOR
    mat.diffuse_color = BRIDGE_COLOR  # solid-view fallback colour
    if not ob.material_slots:
        # mesh has no slots — give the object one without editing the shared mesh
        ob.data.materials.append(mat)
    for slot in ob.material_slots:
        slot.link = "OBJECT"
        slot.material = mat
    print(f"  colour: {BRIDGE_MATERIAL!r} base {tuple(round(c, 2) for c in BRIDGE_COLOR)} "
          f"(object-level override on {len(ob.material_slots)} slot(s))")


def _pixel_to_world(img_x, img_y, ext, w, h):
    """terrainWater pixel (col=img_x, row=img_y) -> world (x, y) via documented mapping."""
    cx, cy, sx, sy = ext
    wx = (img_y / (h - 1) - 0.5) * sx + cx      # Image Y -> screen L->R -> world X
    wy = (0.5 - img_x / (w - 1)) * sy + cy      # Image X -> screen T->B -> world Y
    return wx, wy


def _place_bridge(mesh, coll, spec):
    ob = bpy.data.objects.get(spec["name"])
    if ob is None:
        ob = bpy.data.objects.new(spec["name"], mesh)
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
    _apply_bridge_color(ob)
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
