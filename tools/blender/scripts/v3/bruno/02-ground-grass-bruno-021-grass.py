"""Bruno's 021_grass.py — verbatim recreation.

Source: folio-2025/scripts/blender_world_steps/steps/021_grass.py

Instantiates the grass-scatter MESH object: a 3-vert triangle (mesh
datablock `Plane.012` from 01-foundation-bruno-005d-meshes-03) named
`Plane.003`, with the `Geometry Nodes.001` scatter group bound as a
GeometryNodes modifier. The group samples `terrainGrass` EXR's G
channel on a 192×192m grid and instances ~78k blades where G < 0.4.

Object name `Plane.003` ≠ mesh datablock name `Plane.012` — Bruno's
authoring quirk, harmless at runtime.

Depends on: 01-foundation-bruno-* having run first.

Adds: 1 MESH object `Plane.003` to collection `grass` at world origin.
"""
import bpy


def run():
    print('[021_grass] grass')
    coll = bpy.data.collections.get('grass')
    if coll is None:
        coll = bpy.data.collections.new('grass')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try:
            bpy.context.scene.collection.children.link(coll)
        except Exception:
            pass

    # --- object: Plane.003 (type=MESH) ---
    ob = bpy.data.objects.get('Plane.003') or bpy.data.objects.new('Plane.003', bpy.data.meshes.get('Plane.012'))
    ob.location = (0.0, 0.0, 0.0)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    m = ob.modifiers.new('GeometryNodes', 'NODES')
    try: m.use_pin_to_last = False
    except Exception: pass
    try: m.use_apply_on_spline = False
    except Exception: pass
    try: m.node_group = bpy.data.node_groups.get('Geometry Nodes.001')
    except Exception: pass
    try: m.bake_directory = ''
    except Exception: pass
    try: m.bake_target = 'PACKED'
    except Exception: pass
    try: m.show_manage_panel = True
    except Exception: pass
    try: m.open_output_attributes_panel = False
    except Exception: pass
    try: m.open_manage_panel = False
    except Exception: pass
    try: m.open_bake_panel = False
    except Exception: pass
    try: m.open_named_attributes_panel = False
    except Exception: pass
    try: m.open_bake_data_blocks_panel = False
    except Exception: pass
    try: m.open_warnings_panel = True
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try:
            coll.objects.link(ob)
        except Exception:
            pass

    print('  added 1 objects to grass')


if __name__ == '__main__':
    run()
