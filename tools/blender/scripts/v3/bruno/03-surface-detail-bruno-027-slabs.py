"""Bruno's 027_slabs.py - verbatim recreation.

3 cobblestone slab meshes (slabes/Cube.001/Cube.002). Cube.001 carries a
`Smooth by Angle.003` NODES modifier (angle ~30deg) to round its tile
normals; the other two keep raw normals. All share the `palette` material.

Adds: 3 MESH to collection `slabs`.

Source: folio-2025/scripts/blender_world_steps/steps/027_slabs.py
"""
import bpy

def run():
    print('[027_slabs] slabs')
    coll = bpy.data.collections.get('slabs')
    if coll is None: coll = bpy.data.collections.new('slabs')

    # --- object: slabes (type=MESH) ---
    ob = bpy.data.objects.get('slabes') or bpy.data.objects.new('slabes', bpy.data.meshes.get('Cube.063'))
    ob.location = (27.687625885009766, -16.76808738708496, -0.39402085542678833)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, -0.9477261900901794)
    ob.scale = (0.8134506940841675, 0.8134506940841675, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.001 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.001') or bpy.data.objects.new('Cube.001', bpy.data.meshes.get('Cube.001'))
    ob.location = (-1.7313258647918701, -15.725229263305664, 0.9997153878211975)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    m = ob.modifiers.new('Smooth by Angle.003', 'NODES')
    try: m.use_pin_to_last = True
    except Exception: pass
    try: m.use_apply_on_spline = False
    except Exception: pass
    try: m.node_group = bpy.data.node_groups.get('Smooth by Angle.003')
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
    try: m['Input_1'] = 0.5235987901687622
    except Exception: pass
    try: m['Input_1_use_attribute'] = 0
    except Exception: pass
    try: m['Input_1_attribute_name'] = ''
    except Exception: pass
    try: m['Socket_1'] = False
    except Exception: pass
    try: m['Socket_1_use_attribute'] = 0
    except Exception: pass
    try: m['Socket_1_attribute_name'] = ''
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.002 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.002') or bpy.data.objects.new('Cube.002', bpy.data.meshes.get('Cube.002'))
    ob.location = (-4.040179252624512, 26.570384979248047, 0.34767380356788635)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-0.0, -3.141592502593994, -0.0)
    ob.scale = (1.8886948823928833, 1.2987818717956543, 1.2987818717956543)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 3 objects to slabs')

if __name__ == '__main__': run()
