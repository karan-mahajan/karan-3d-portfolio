"""Bruno's 110_cups.py - verbatim recreation.

`cups` zone — 3 MESH (cupPhysicalDynamic + .001/.002, all sharing `Cube.015`,
each with a 'Smooth by Angle' NODES modifier) + 3 EMPTY (tube.033/.041/.042
CUBE bounds). Centre ~(-54.0, 69.1).

Adds: 6 objects (3 MESH + 3 EMPTY) to collection `cups`.

Section 13 (food / misc / fx). Collection is linked to the scene root here
(Bruno relies on 999_finalize for that; we do not run it yet), matching the
section-02..06 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/110_cups.py

"""
import bpy

def run():
    print('[110_cups] cups')
    coll = bpy.data.collections.get('cups')
    if coll is None: coll = bpy.data.collections.new('cups')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: cupPhysicalDynamic (type=MESH) ---
    ob = bpy.data.objects.get('cupPhysicalDynamic') or bpy.data.objects.new('cupPhysicalDynamic', bpy.data.meshes.get('Cube.015'))
    ob.location = (-54.02385711669922, 69.1495132446289, 2.2334752082824707)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    m = ob.modifiers.new('Smooth by Angle', 'NODES')
    try: m.use_pin_to_last = True
    except Exception: pass
    try: m.use_apply_on_spline = False
    except Exception: pass
    try: m.node_group = bpy.data.node_groups.get('Smooth by Angle')
    except Exception: pass
    try: m.bake_directory = ''
    except Exception: pass
    try: m.bake_target = 'PACKED'
    except Exception: pass
    try: m.show_manage_panel = False
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
    try: m['Input_1'] = 0.8480554819107056
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

    # --- object: tube.033 (type=EMPTY) ---
    ob = bpy.data.objects.get('tube.033') or bpy.data.objects.new('tube.033', None)
    ob.location = (-54.02385330200195, 69.14950561523438, 2.251760721206665)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.44370079040527344, 0.44370079040527344, 0.5492181181907654)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cupPhysicalDynamic.001 (type=MESH) ---
    ob = bpy.data.objects.get('cupPhysicalDynamic.001') or bpy.data.objects.new('cupPhysicalDynamic.001', bpy.data.meshes.get('Cube.015'))
    ob.location = (-54.47144317626953, 69.3852767944336, 2.2334752082824707)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    m = ob.modifiers.new('Smooth by Angle', 'NODES')
    try: m.use_pin_to_last = True
    except Exception: pass
    try: m.use_apply_on_spline = False
    except Exception: pass
    try: m.node_group = bpy.data.node_groups.get('Smooth by Angle')
    except Exception: pass
    try: m.bake_directory = ''
    except Exception: pass
    try: m.bake_target = 'PACKED'
    except Exception: pass
    try: m.show_manage_panel = False
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
    try: m['Input_1'] = 0.8480554819107056
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

    # --- object: tube.041 (type=EMPTY) ---
    ob = bpy.data.objects.get('tube.041') or bpy.data.objects.new('tube.041', None)
    ob.location = (-54.02385330200195, 69.14950561523438, 2.251760721206665)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.44370079040527344, 0.44370079040527344, 0.5492181181907654)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cupPhysicalDynamic.002 (type=MESH) ---
    ob = bpy.data.objects.get('cupPhysicalDynamic.002') or bpy.data.objects.new('cupPhysicalDynamic.002', bpy.data.meshes.get('Cube.015'))
    ob.location = (-53.26644515991211, 69.08492279052734, 0.1466829776763916)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-0.12329666316509247, 0.10690174251794815, -0.0717586800456047)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    m = ob.modifiers.new('Smooth by Angle', 'NODES')
    try: m.use_pin_to_last = True
    except Exception: pass
    try: m.use_apply_on_spline = False
    except Exception: pass
    try: m.node_group = bpy.data.node_groups.get('Smooth by Angle')
    except Exception: pass
    try: m.bake_directory = ''
    except Exception: pass
    try: m.bake_target = 'PACKED'
    except Exception: pass
    try: m.show_manage_panel = False
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
    try: m['Input_1'] = 0.8480554819107056
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

    # --- object: tube.042 (type=EMPTY) ---
    ob = bpy.data.objects.get('tube.042') or bpy.data.objects.new('tube.042', None)
    ob.location = (-54.02385330200195, 69.14950561523438, 2.251760721206665)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.44370079040527344, 0.44370079040527344, 0.5492181181907654)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 6 objects to cups')

if __name__ == '__main__': run()
