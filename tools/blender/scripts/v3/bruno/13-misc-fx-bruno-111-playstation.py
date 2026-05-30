"""Bruno's 111_playstation.py - verbatim recreation.

`playstation` zone — 4 MESH objects (Cube.006, Cylinder, Cube.007, Plane.005)
clustered near (-54.5, 67.2). Cube.006 and Cylinder carry a NODES 'Smooth by
Angle' modifier; Cylinder also has a MIRROR modifier (X axis, clip + merge).

Adds: 4 objects (4 MESH) to collection `playstation`.

Section 13 (food / misc / fx). Collection is linked to the scene root here
(Bruno relies on 999_finalize for that; we do not run it yet), matching the
section-02..06 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/111_playstation.py

"""
import bpy

def run():
    print('[111_playstation] playstation')
    coll = bpy.data.collections.get('playstation')
    if coll is None: coll = bpy.data.collections.new('playstation')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: Cube.006 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.006') or bpy.data.objects.new('Cube.006', bpy.data.meshes.get('Cube.010'))
    ob.location = (-54.50775146484375, 67.58922576904297, 0.14765632152557373)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.1823259592056274, 1.1823259592056274, 1.1823259592056274)
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

    # --- object: Cylinder (type=MESH) ---
    ob = bpy.data.objects.get('Cylinder') or bpy.data.objects.new('Cylinder', bpy.data.meshes.get('Cylinder'))
    ob.location = (-53.63414764404297, 67.47512817382812, 0.1935395747423172)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-0.20532365143299103, 0.48519235849380493, -0.3971726894378662)
    ob.scale = (0.8567297458648682, 0.8567298054695129, 0.8567297458648682)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    m = ob.modifiers.new('Mirror', 'MIRROR')
    try: m.use_pin_to_last = False
    except Exception: pass
    try: m.use_apply_on_spline = False
    except Exception: pass
    try: m.use_axis = (True, False, False)
    except Exception: pass
    try: m.use_bisect_axis = (False, False, False)
    except Exception: pass
    try: m.use_bisect_flip_axis = (False, False, False)
    except Exception: pass
    try: m.use_clip = True
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
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.007 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.007') or bpy.data.objects.new('Cube.007', bpy.data.meshes.get('Cube.013'))
    ob.location = (-55.05248260498047, 67.07539367675781, 0.2765493392944336)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Plane.005 (type=MESH) ---
    ob = bpy.data.objects.get('Plane.005') or bpy.data.objects.new('Plane.005', bpy.data.meshes.get('Plane.062'))
    ob.location = (-54.7165412902832, 66.89444732666016, 0.059486713260412216)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 4 objects to playstation')

if __name__ == '__main__': run()