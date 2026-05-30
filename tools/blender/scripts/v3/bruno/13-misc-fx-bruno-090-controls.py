"""Bruno's 090_controls.py - verbatim recreation.

`controls` zone — 14 objects: 6 MESH (Plane.004, Plane.002,
gizmoPhysicalDynamic, body.002, qosdjqosjd, phonePhysicalDynamic,
phonePhysicalDynamic.002) + EMPTY refs/cuboids/tubes (cuboid.019, body refs,
gamepadPhysicalDynamic.001, cuboid.011, cuboid.009, tube.014,
refControlsInteractivePoint, phonePhysicalDynamic.001). Three meshes carry a
NODES 'Smooth by Angle' modifier.

Adds: 14 objects (7 MESH, 7 EMPTY) to collection `controls`.

Section 13 (food / misc / fx). Collection is linked to the scene root here
(Bruno relies on 999_finalize for that; we do not run it yet), matching the
section-02..06 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/090_controls.py

"""
import bpy

def run():
    print('[090_controls] controls')
    coll = bpy.data.collections.get('controls')
    if coll is None: coll = bpy.data.collections.new('controls')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: Plane.004 (type=MESH) ---
    ob = bpy.data.objects.get('Plane.004') or bpy.data.objects.new('Plane.004', bpy.data.meshes.get('Plane.024'))
    ob.location = (54.4803352355957, -29.70357322692871, 0.14976035058498383)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.17453287541866302, -4.099919959088538e-09, 0.3150350749492645)
    ob.scale = (0.5808245539665222, 0.5808244943618774, 0.5808245539665222)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Plane.002 (type=MESH) ---
    ob = bpy.data.objects.get('Plane.002') or bpy.data.objects.new('Plane.002', bpy.data.meshes.get('Plane.020'))
    ob.location = (54.4803352355957, -29.70357322692871, 0.14976035058498383)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.17453287541866302, -4.099919959088538e-09, 0.3150350749492645)
    ob.scale = (0.5808245539665222, 0.5808244943618774, 0.5808245539665222)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: gizmoPhysicalDynamic (type=MESH) ---
    ob = bpy.data.objects.get('gizmoPhysicalDynamic') or bpy.data.objects.new('gizmoPhysicalDynamic', bpy.data.meshes.get('sdfsdf'))
    ob.location = (55.27324295043945, -30.878061294555664, 0.9245792031288147)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, -7.16093850883226e-15, -1.570796251296997)
    ob.scale = (0.9999999403953552, 0.9999999403953552, 0.9999999403953552)
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
    try: m['Input_1'] = 0.9145525097846985
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

    # --- object: cuboid.019 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.019') or bpy.data.objects.new('cuboid.019', None)
    ob.location = (16.855388641357422, 5.697099208831787, 1.6188161373138428)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.7188177108764648, 1.7188177108764648, 1.7188177108764648)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: body.002 (type=MESH) ---
    ob = bpy.data.objects.get('body.002') or bpy.data.objects.new('body.002', bpy.data.meshes.get('Plane.066'))
    ob.location = (16.111330032348633, -1.3679430484771729, 0.5581168532371521)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: gamepadPhysicalDynamic.001 (type=EMPTY) ---
    ob = bpy.data.objects.get('gamepadPhysicalDynamic.001') or bpy.data.objects.new('gamepadPhysicalDynamic.001', None)
    ob.location = (57.47182083129883, -32.30831527709961, 0.6229889988899231)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-0.17796403169631958, -1.1054228643558872e-09, -0.44724422693252563)
    ob.scale = (0.9999997615814209, 0.9999997615814209, 0.9999997019767761)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'PLAIN_AXES'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: qosdjqosjd (type=MESH) ---
    ob = bpy.data.objects.get('qosdjqosjd') or bpy.data.objects.new('qosdjqosjd', bpy.data.meshes.get('Cylinder.026'))
    ob.location = (17.366491317749023, -1.0011950731277466, 1.3803925514221191)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-0.15441077947616577, 0.2998797297477722, -0.023372774943709373)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: phonePhysicalDynamic (type=MESH) ---
    ob = bpy.data.objects.get('phonePhysicalDynamic') or bpy.data.objects.new('phonePhysicalDynamic', bpy.data.meshes.get('Circle.005'))
    ob.location = (57.33203887939453, -30.28952407836914, 0.5146898627281189)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.1694449931383133, 1.0397689820251799e-08, 0.8138511776924133)
    ob.scale = (1.0, 0.9999999403953552, 0.9999999403953552)
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
    try: m['Input_1'] = 0.7853981852531433
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

    # --- object: cuboid.011 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.011') or bpy.data.objects.new('cuboid.011', None)
    ob.location = (18.346784591674805, 4.875518798828125, 0.45064467191696167)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-0.020846538245677948, 0.0019316459074616432, -0.43650469183921814)
    ob.scale = (3.18456768989563, 1.7602686882019043, 0.7566841840744019)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.009 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.009') or bpy.data.objects.new('cuboid.009', None)
    ob.location = (57.31891632080078, -30.27775001525879, 0.4140450954437256)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.16944502294063568, 2.031952606174059e-09, 0.8138510584831238)
    ob.scale = (1.769981026649475, 3.169975996017456, 0.2571156620979309)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: tube.014 (type=EMPTY) ---
    ob = bpy.data.objects.get('tube.014') or bpy.data.objects.new('tube.014', None)
    ob.location = (57.42589569091797, -30.378808975219727, 1.2742263078689575)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.16944502294063568, -1.198214860664848e-08, 0.8138508796691895)
    ob.scale = (0.800115168094635, 0.8001149892807007, 1.4505118131637573)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refControlsInteractivePoint (type=EMPTY) ---
    ob = bpy.data.objects.get('refControlsInteractivePoint') or bpy.data.objects.new('refControlsInteractivePoint', None)
    ob.location = (53.83684539794922, -32.53384017944336, 1.7493617534637451)
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

    # --- object: phonePhysicalDynamic.001 (type=EMPTY) ---
    ob = bpy.data.objects.get('phonePhysicalDynamic.001') or bpy.data.objects.new('phonePhysicalDynamic.001', None)
    ob.location = (57.332035064697266, -30.289522171020508, 0.514689564704895)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.16944505274295807, 7.344429509004158e-09, 0.8138511776924133)
    ob.scale = (0.9999998807907104, 0.9999996423721313, 0.9999997019767761)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'PLAIN_AXES'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: phonePhysicalDynamic.002 (type=MESH) ---
    ob = bpy.data.objects.get('phonePhysicalDynamic.002') or bpy.data.objects.new('phonePhysicalDynamic.002', bpy.data.meshes.get('Circle.015'))
    ob.location = (57.33203887939453, -30.28952407836914, 0.5146898627281189)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.1694449931383133, 1.0397689820251799e-08, 0.8138511776924133)
    ob.scale = (1.0, 0.9999999403953552, 0.9999999403953552)
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
    try: m['Input_1'] = 0.7853981852531433
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

    print('  added 14 objects to controls')

if __name__ == '__main__': run()