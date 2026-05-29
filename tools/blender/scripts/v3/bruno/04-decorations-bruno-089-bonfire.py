"""Bruno's 089_bonfire.py - verbatim recreation.

Landing-zone bonfire centerpiece: skull (post_skull_skull.001), sword,
log/ember meshes (Cube.090, Plane.003/021) + a burn-marker empty. Uses
node-group Smooth by Angle.001. All meshes from foundation 005.

Adds: 5 objects (4 MESH, 1 EMPTY) to collection `bonfire`.

Source: folio-2025/scripts/blender_world_steps/steps/089_bonfire.py
"""
import bpy

def run():
    print('[089_bonfire] bonfire')
    coll = bpy.data.collections.get('bonfire')
    if coll is None: coll = bpy.data.collections.new('bonfire')

    # --- object: base.015 (type=MESH) ---
    ob = bpy.data.objects.get('base.015') or bpy.data.objects.new('base.015', bpy.data.meshes.get('post_skull_skull.001'))
    ob.location = (56.15682601928711, -47.36214828491211, 0.3120451867580414)
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = (0.9004167318344116, -0.16380609571933746, 0.14997506141662598, 0.37406522035598755)
    ob.scale = (85.9679183959961, 85.9679183959961, 85.96792602539062)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refBonfireInteractivePoint (type=EMPTY) ---
    ob = bpy.data.objects.get('refBonfireInteractivePoint') or bpy.data.objects.new('refBonfireInteractivePoint', None)
    ob.location = (53.704891204833984, -46.304481506347656, 1.4999994039535522)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-3.5527141023169746e-15, 0.0, 0.0)
    ob.scale = (0.9999999403953552, 0.9999999403953552, 0.9999999403953552)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'PLAIN_AXES'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refBonfireHashes (type=MESH) ---
    ob = bpy.data.objects.get('refBonfireHashes') or bpy.data.objects.new('refBonfireHashes', bpy.data.meshes.get('Plane.021'))
    ob.location = (55.59833526611328, -47.34086227416992, -0.012700692750513554)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-3.5527141023169746e-15, 0.0, 0.0)
    ob.scale = (0.9999999403953552, 0.9999999403953552, 0.9999999403953552)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: sword (type=MESH) ---
    ob = bpy.data.objects.get('sword') or bpy.data.objects.new('sword', bpy.data.meshes.get('Cube.090'))
    ob.location = (56.265926361083984, -46.974308013916016, 1.1956934928894043)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-0.14427399635314941, 0.28823086619377136, -0.12526464462280273)
    ob.scale = (0.9999998807907104, 0.9999999403953552, 0.9999999403953552)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    m = ob.modifiers.new('Smooth by Angle.001', 'NODES')
    try: m.use_pin_to_last = True
    except Exception: pass
    try: m.use_apply_on_spline = False
    except Exception: pass
    try: m.node_group = bpy.data.node_groups.get('Smooth by Angle.001')
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

    # --- object: refBonfireBurn.001 (type=MESH) ---
    ob = bpy.data.objects.get('refBonfireBurn.001') or bpy.data.objects.new('refBonfireBurn.001', bpy.data.meshes.get('Plane.003'))
    ob.location = (55.59833526611328, -47.34086227416992, -0.025096924975514412)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-3.5527141023169746e-15, 0.0, 0.0)
    ob.scale = (0.9999999403953552, 0.9999999403953552, 0.9999999403953552)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 5 objects to bonfire')

if __name__ == '__main__': run()