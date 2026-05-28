"""Bruno's 020_terrain.py — verbatim recreation.

Source: folio-2025/scripts/blender_world_steps/steps/020_terrain.py

Instantiates THE island as a single MESH object backed by mesh datablock
`Plane.134` (created in 01-foundation-bruno-005f-meshes-05) and binds the
`Geometry Nodes` node group (built in 01-foundation-bruno-003-node-groups)
as a GeometryNodes modifier. The node group samples `terrainWater` EXR
and displaces Z to carve river/pond depressions.

Depends on: 01-foundation-bruno-* having run first (mesh + node group +
collections + materials must exist).

Adds: 1 MESH object `terrain` to collection `terrain` at world origin.
"""
import bpy


def run():
    print('[020_terrain] terrain')
    coll = bpy.data.collections.get('terrain')
    if coll is None:
        coll = bpy.data.collections.new('terrain')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try:
            bpy.context.scene.collection.children.link(coll)
        except Exception:
            pass

    # --- object: terrain (type=MESH) ---
    ob = bpy.data.objects.get('terrain') or bpy.data.objects.new('terrain', bpy.data.meshes.get('Plane.134'))
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
    try: m.node_group = bpy.data.node_groups.get('Geometry Nodes')
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

    print('  added 1 objects to terrain')


if __name__ == '__main__':
    run()
