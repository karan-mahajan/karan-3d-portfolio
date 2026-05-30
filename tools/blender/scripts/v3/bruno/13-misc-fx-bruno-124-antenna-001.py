"""Bruno's 124_antenna.001.py - verbatim recreation.

`antenna.001` collection — 9 objects: 4 EMPTY (antennaHead, axle, antenna,
antennaHeadReference; PLAIN_AXES pivots) + 5 MESH (Plane.010, Sphere,
Cube.036, Cylinder.008, Cylinder.012). Sphere carries a NODES "Smooth by
Angle.003" modifier; Cube.036 carries a MIRROR modifier (Y axis).

Adds: 9 objects (4 EMPTY + 5 MESH) to collection `antenna.001`.

Section 13 (food / misc / fx). Collection is linked to the scene root here
(Bruno relies on 999_finalize for that; we do not run it yet), matching the
section-02..06 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/124_antenna.001.py

"""
import bpy

def run():
    print('[124_antenna.001] antenna.001')
    coll = bpy.data.collections.get('antenna.001')
    if coll is None: coll = bpy.data.collections.new('antenna.001')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: antennaHead (type=EMPTY) ---
    ob = bpy.data.objects.get('antennaHead') or bpy.data.objects.new('antennaHead', None)
    ob.location = (-0.6712612509727478, 0.4168592095375061, 1.9603358507156372)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 2.673651695251465)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'PLAIN_AXES'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: axle (type=EMPTY) ---
    ob = bpy.data.objects.get('axle') or bpy.data.objects.new('axle', None)
    ob.location = (-0.6498498916625977, 0.3799999952316284, 1.9514966011047363)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'PLAIN_AXES'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Plane.010 (type=MESH) ---
    ob = bpy.data.objects.get('Plane.010') or bpy.data.objects.new('Plane.010', bpy.data.meshes.get('Plane.013'))
    ob.location = (-0.6493871808052063, 0.38046276569366455, 1.9514966011047363)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (1.570796251296997, 1.570796251296997, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Sphere (type=MESH) ---
    ob = bpy.data.objects.get('Sphere') or bpy.data.objects.new('Sphere', bpy.data.meshes.get('Sphere.001'))
    ob.location = (-0.6493871808052063, 0.38046276569366455, 1.9514966011047363)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (1.570796251296997, 1.570796251296997, 0.0)
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

    # --- object: antenna (type=EMPTY) ---
    ob = bpy.data.objects.get('antenna') or bpy.data.objects.new('antenna', None)
    ob.location = (0.0, 0.0, 0.0)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'PLAIN_AXES'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: antennaHeadReference (type=EMPTY) ---
    ob = bpy.data.objects.get('antennaHeadReference') or bpy.data.objects.new('antennaHeadReference', None)
    ob.location = (-0.6879448890686035, 0.34176206588745117, 1.9495937824249268)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-3.8904140353679395e-08, -0.6981317400932312, -1.570796251296997)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'PLAIN_AXES'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.036 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.036') or bpy.data.objects.new('Cube.036', bpy.data.meshes.get('Cube.041'))
    ob.location = (-0.687944769859314, 0.49065911769866943, 1.827773928642273)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-5.542118941548324e-08, 0.8726645708084106, -1.5707966089248657)
    ob.scale = (0.029588505625724792, 0.029588503763079643, 0.029588505625724792)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    m = ob.modifiers.new('Mirror', 'MIRROR')
    try: m.use_pin_to_last = False
    except Exception: pass
    try: m.use_apply_on_spline = False
    except Exception: pass
    try: m.use_axis = (False, True, False)
    except Exception: pass
    try: m.use_bisect_axis = (False, False, False)
    except Exception: pass
    try: m.use_bisect_flip_axis = (False, False, False)
    except Exception: pass
    try: m.use_clip = False
    except Exception: pass
    try: m.use_mirror_vertex_groups = True
    except Exception: pass
    try: m.use_mirror_merge = True
    except Exception: pass
    try: m.use_mirror_u = False
    except Exception: pass
    try: m.use_mirror_v = False
    except Exception: pass
    try: m.use_mirror_udim = False
    except Exception: pass
    try: m.mirror_offset_u = 0.0
    except Exception: pass
    try: m.mirror_offset_v = 0.0
    except Exception: pass
    try: m.offset_u = 0.0
    except Exception: pass
    try: m.offset_v = 0.0
    except Exception: pass
    try: m.merge_threshold = 0.0010000000474974513
    except Exception: pass
    try: m.bisect_threshold = 0.0010000000474974513
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cylinder.008 (type=MESH) ---
    ob = bpy.data.objects.get('Cylinder.008') or bpy.data.objects.new('Cylinder.008', bpy.data.meshes.get('Cylinder.001'))
    ob.location = (0.0, 0.0, 0.0)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cylinder.012 (type=MESH) ---
    ob = bpy.data.objects.get('Cylinder.012') or bpy.data.objects.new('Cylinder.012', bpy.data.meshes.get('Cylinder.005'))
    ob.location = (0.0, 0.0, 0.0)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 9 objects to antenna.001')

if __name__ == '__main__': run()
