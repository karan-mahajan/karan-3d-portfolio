"""Place Bruno's cobblestone slabs (027) on karan's island — tune-by-iteration.

Section-03 slabs delta. Bruno's slabs are 3 flat tile meshes that lie on the
ground as paved patches:
  - slab01  (mesh Cube.063) — plain slab, slightly sunk
  - slab02  (mesh Cube.001) — carries a `Smooth by Angle` NODES modifier that
              rounds the tile normals (added here only if the node group exists)
  - slab03  (mesh Cube.002) — larger slab, flipped 180 deg about Y

Each slab keeps Bruno's native local transform, but LOCATION and SCALE are
multiplied by SLAB_SHRINK (0.651, the terrain shrink 125/192) so they land
proportionally inside karan's smaller island. They start near Bruno's original
spots — snap the 3D cursor where you want each one and read N-panel > View >
3D Cursor XYZ, give me the values, and I bake them into each spec.

Keeps Bruno's native `palette` material (no colour override yet — tell me if you
want them recoloured). Keep-everything policy: only ADDS objects + mounts an
existing collection; removes nothing.

Run additively on the open world (already has bridges + rocks):
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/03-surface-detail-slabs.py').read())
"""
import math
import os

import bpy

SLABS_COLLECTION = "slabs"
CONTAINER_COLLECTION = "scenery.002"
SMOOTH_NODE_GROUP = "Smooth by Angle.003"
BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"
# Fallback source for Bruno meshes if the open file has only a partial foundation.
BRUNO_BLEND = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-bruno.blend"

# --- placement knobs ---
# Shrinks Bruno's native slab positions + sizes into karan's smaller island.
SLAB_SHRINK = 0.651   # terrain shrink (125/192); tune to taste

# Per-slab specs: native transforms read verbatim from Bruno's 027_slabs.py.
# location/scale get multiplied by SLAB_SHRINK at placement time; euler is kept.
SLABS = [
    {
        "name": "slab01",
        "mesh": "Cube.063",
        "location": (27.687625885009766, -16.76808738708496, -0.39402085542678833),
        "euler": (0.0, 0.0, -0.9477261900901794),
        "scale": (0.8134506940841675, 0.8134506940841675, 1.0),
        "smooth": False,
    },
    {
        "name": "slab02",
        "mesh": "Cube.001",
        "location": (-1.7313258647918701, -15.725229263305664, 0.9997153878211975),
        "euler": (0.0, 0.0, 0.0),
        "scale": (1.0, 1.0, 1.0),
        "smooth": True,   # Bruno's Smooth by Angle (~30 deg) on this tile
    },
    {
        "name": "slab03",
        "mesh": "Cube.002",
        "location": (-4.040179252624512, 26.570384979248047, 0.34767380356788635),
        "euler": (-0.0, -3.141592502593994, -0.0),
        "scale": (1.8886948823928833, 1.2987818717956543, 1.2987818717956543),
        "smooth": False,
    },
]


def _ensure_slab_meshes():
    """Append slab meshes from world-v3-bruno.blend if the open file lacks them."""
    needed = {spec["mesh"] for spec in SLABS}
    missing = [mn for mn in needed if bpy.data.meshes.get(mn) is None]
    if not missing:
        return True
    if not os.path.exists(BRUNO_BLEND):
        print(f"  [ABORT] {len(missing)} slab meshes missing and {BRUNO_BLEND} not found.")
        return False
    with bpy.data.libraries.load(BRUNO_BLEND, link=False) as (src, dst):
        dst.meshes = [m for m in missing if m in src.meshes]
    still = [mn for mn in needed if bpy.data.meshes.get(mn) is None]
    got = len(missing) - len(still)
    print(f"  appended {got} slab mesh(es) from world-v3-bruno.blend (open file had a partial foundation)")
    if still:
        print(f"  [ABORT] still missing after append: {still}")
        return False
    return True


def _add_smooth_modifier(ob):
    """Round the slab's tile normals like Bruno (Smooth by Angle ~30 deg)."""
    ng = bpy.data.node_groups.get(SMOOTH_NODE_GROUP)
    if ng is None:
        print(f"  [note] {ob.name}: node group {SMOOTH_NODE_GROUP!r} absent — skipping smooth modifier")
        return
    if any(m.type == "NODES" and m.node_group is ng for m in ob.modifiers):
        return
    m = ob.modifiers.new(SMOOTH_NODE_GROUP, "NODES")
    m.node_group = ng
    try:
        m["Input_1"] = 0.5235987901687622   # ~30 deg
    except Exception:
        pass


def _place_slab(coll, spec):
    mesh = bpy.data.meshes.get(spec["mesh"])
    if mesh is None:
        print(f"  [skip] {spec['name']}: mesh {spec['mesh']!r} not found")
        return False
    ob = bpy.data.objects.get(spec["name"]) or bpy.data.objects.new(spec["name"], mesh)
    ob.location = tuple(v * SLAB_SHRINK for v in spec["location"])
    ob.rotation_mode = "XYZ"
    ob.rotation_euler = spec["euler"]
    ob.scale = tuple(v * SLAB_SHRINK for v in spec["scale"])
    try:
        ob.display_type = "TEXTURED"
    except Exception:
        pass
    if spec.get("smooth"):
        _add_smooth_modifier(ob)
    if ob.name not in {o.name for o in coll.objects}:
        try:
            coll.objects.link(ob)
        except Exception:
            pass
    print(f"  placed {ob.name!r} ({spec['mesh']}) at {tuple(round(v, 2) for v in ob.location)} "
          f"scale {tuple(round(v, 2) for v in ob.scale)}")
    return True


def run():
    print("[03-surface-detail-slabs] place Bruno's cobblestone slabs on karan's island")

    if not _ensure_slab_meshes():
        return

    container = bpy.data.collections.get(CONTAINER_COLLECTION)
    if container and container.name not in {c.name for c in bpy.context.scene.collection.children}:
        try:
            bpy.context.scene.collection.children.link(container)
        except Exception:
            pass
    coll = bpy.data.collections.get(SLABS_COLLECTION) or bpy.data.collections.new(SLABS_COLLECTION)

    placed = sum(_place_slab(coll, spec) for spec in SLABS)
    print(f"  placed {placed}/{len(SLABS)} slabs (shrink x{SLAB_SHRINK})")

    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")


if __name__ == "__main__":
    run()
