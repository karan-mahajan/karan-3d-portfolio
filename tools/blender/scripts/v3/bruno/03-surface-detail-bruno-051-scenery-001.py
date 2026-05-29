"""Bruno's 051_scenery.001.py - verbatim recreation.

behindTheScene corner's local props: 3 dynamic-physics cylinders
(refObjectsPhysicalDynamic.*, shared mesh Cylinder.042, mass=1.0,
Smooth by Angle ~55deg) + 5 EMPTY collider proxies.

NOTE: collection `scenery.001` lives under `behindTheScene` -> `areas`,
which is NOT mounted to scene root until section 06. These objects exist
in the Outliner but will not render until then. Faithful Bruno behavior.

Adds: 8 objects (3 MESH + 5 EMPTY) to collection `scenery.001`.

Source: folio-2025/scripts/blender_world_steps/steps/051_scenery.001.py
"""
import bpy

def run():
    print('[051_scenery.001] scenery.001')
    coll = bpy.data.collections.get('scenery.001')
    if coll is None: coll = bpy.data.collections.new('scenery.001')

    # --- object: refObjectsPhysicalDynamic.021 (type=MESH) ---
    ob = bpy.data.objects.get('refObjectsPhysicalDynamic.021') or bpy.data.objects.new('refObjectsPhysicalDynamic.021', bpy.data.meshes.get('Cylinder.042'))
    ob.location = (48.549644470214844, 13.89117431640625, 0.5304663181304932)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, -0.09239460527896881)
    ob.scale = (0.9999999403953552, 0.9999999403953552, 1.0)
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
    try: m['Input_1'] = 0.9599310755729675
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
    try: ob['mass'] = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.013 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.013') or bpy.data.objects.new('cuboid.013', None)
    ob.location = (-54.34841537475586, 57.40055847167969, 0.8344791531562805)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.3495641350746155, 0.3495641350746155, 1.0345559120178223)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.120 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.120') or bpy.data.objects.new('cuboid.120', None)
    ob.location = (-54.34841537475586, 57.40055847167969, 0.35095930099487305)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 3.141592502593994)
    ob.scale = (0.8849538564682007, 0.8849538564682007, 0.09648063778877258)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refObjectsPhysicalDynamic.022 (type=MESH) ---
    ob = bpy.data.objects.get('refObjectsPhysicalDynamic.022') or bpy.data.objects.new('refObjectsPhysicalDynamic.022', bpy.data.meshes.get('Cylinder.042'))
    ob.location = (51.56885528564453, 16.015426635742188, 0.5304663181304932)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, -0.8705193400382996)
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
    try: m['Input_1'] = 0.9599310755729675
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
    try: ob['mass'] = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.123 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.123') or bpy.data.objects.new('cuboid.123', None)
    ob.location = (-54.34841537475586, 57.40055847167969, 0.8344791531562805)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.3495641350746155, 0.3495641350746155, 1.0345559120178223)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.124 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.124') or bpy.data.objects.new('cuboid.124', None)
    ob.location = (-54.34841537475586, 57.40055847167969, 0.35095930099487305)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 3.141592502593994)
    ob.scale = (0.8849538564682007, 0.8849538564682007, 0.09648063778877258)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refObjectsPhysicalDynamic.023 (type=MESH) ---
    ob = bpy.data.objects.get('refObjectsPhysicalDynamic.023') or bpy.data.objects.new('refObjectsPhysicalDynamic.023', bpy.data.meshes.get('Cylinder.042'))
    ob.location = (52.464378356933594, 6.004127502441406, 0.4561639726161957)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.05662201717495918, -0.020915718749165535, -0.0797123983502388)
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
    try: m['Input_1'] = 0.9599310755729675
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
    try: ob['mass'] = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.125 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.125') or bpy.data.objects.new('cuboid.125', None)
    ob.location = (-54.34841537475586, 57.40055847167969, 0.8344791531562805)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.3495641350746155, 0.3495641350746155, 1.0345559120178223)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 8 objects to scenery.001')

if __name__ == '__main__': run()
