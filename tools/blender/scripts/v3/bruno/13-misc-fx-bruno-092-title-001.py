"""Bruno's 092_title.001.py - verbatim recreation.

`title.001` zone — the knockable second welcome-title line: 10 MESH letters
(refLettersPhysicalDynamic.010-.019, each carrying a `mass` = 0.2 custom prop
and a 'Smooth by Angle.003' NODES modifier) + 1 FONT source (Text.003, hidden
in viewport/render/select, with a SOLIDIFY modifier) + 10 EMPTY collision
CUBEs (cuboid.222-.231). Centre ~(43, -41).

Adds: 21 objects (10 MESH + 1 FONT + 10 EMPTY) to collection `title.001`.

Section 13 (food / misc / fx). Collection is linked to the scene root here
(Bruno relies on 999_finalize for that; we do not run it yet), matching the
section-02..06 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/092_title.001.py

"""
import bpy

def run():
    print('[092_title.001] title.001')
    coll = bpy.data.collections.get('title.001')
    if coll is None: coll = bpy.data.collections.new('title.001')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: refLettersPhysicalDynamic.010 (type=MESH) ---
    ob = bpy.data.objects.get('refLettersPhysicalDynamic.010') or bpy.data.objects.new('refLettersPhysicalDynamic.010', bpy.data.meshes.get('Text.002'))
    ob.location = (49.700618743896484, -38.968650817871094, 0.745518684387207)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-3.2198519651444263e-15, 1.501441814336145e-15, 0.4363324046134949)
    ob.scale = (0.9999998807907104, 0.9999998807907104, 0.9999999403953552)
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
    try: ob['mass'] = 0.20000000298023224
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Text.003 (type=FONT) ---
    ob = bpy.data.objects.get('Text.003') or bpy.data.objects.new('Text.003', bpy.data.curves.get('Text.001'))
    ob.location = (36.88291931152344, -39.800575256347656, -0.004469346255064011)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (1.570796251296997, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.hide_viewport = True
    except Exception: pass
    try: ob.hide_render = True
    except Exception: pass
    try: ob.hide_select = True
    except Exception: pass
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    m = ob.modifiers.new('Solidify', 'SOLIDIFY')
    try: m.use_pin_to_last = False
    except Exception: pass
    try: m.use_apply_on_spline = False
    except Exception: pass
    try: m.solidify_mode = 'EXTRUDE'
    except Exception: pass
    try: m.thickness = 0.4599999785423279
    except Exception: pass
    try: m.thickness_clamp = 0.0
    except Exception: pass
    try: m.use_thickness_angle_clamp = False
    except Exception: pass
    try: m.thickness_vertex_group = 0.0
    except Exception: pass
    try: m.offset = -1.0
    except Exception: pass
    try: m.edge_crease_inner = 0.0
    except Exception: pass
    try: m.edge_crease_outer = 0.0
    except Exception: pass
    try: m.edge_crease_rim = 0.0
    except Exception: pass
    try: m.material_offset = 0
    except Exception: pass
    try: m.material_offset_rim = 0
    except Exception: pass
    try: m.vertex_group = ''
    except Exception: pass
    try: m.shell_vertex_group = ''
    except Exception: pass
    try: m.rim_vertex_group = ''
    except Exception: pass
    try: m.use_rim = True
    except Exception: pass
    try: m.use_even_offset = False
    except Exception: pass
    try: m.use_quality_normals = False
    except Exception: pass
    try: m.invert_vertex_group = False
    except Exception: pass
    try: m.use_flat_faces = False
    except Exception: pass
    try: m.use_flip_normals = False
    except Exception: pass
    try: m.use_rim_only = False
    except Exception: pass
    try: m.nonmanifold_thickness_mode = 'CONSTRAINTS'
    except Exception: pass
    try: m.nonmanifold_boundary_mode = 'NONE'
    except Exception: pass
    try: m.nonmanifold_merge_threshold = 9.999999747378752e-05
    except Exception: pass
    try: m.bevel_convex = 0.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refLettersPhysicalDynamic.011 (type=MESH) ---
    ob = bpy.data.objects.get('refLettersPhysicalDynamic.011') or bpy.data.objects.new('refLettersPhysicalDynamic.011', bpy.data.meshes.get('Text.003'))
    ob.location = (48.36317443847656, -39.59231185913086, 0.745518684387207)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-3.2198519651444263e-15, 1.501441814336145e-15, 0.4363324046134949)
    ob.scale = (0.9999998807907104, 0.9999998807907104, 0.9999999403953552)
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
    try: ob['mass'] = 0.20000000298023224
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refLettersPhysicalDynamic.012 (type=MESH) ---
    ob = bpy.data.objects.get('refLettersPhysicalDynamic.012') or bpy.data.objects.new('refLettersPhysicalDynamic.012', bpy.data.meshes.get('Text.004'))
    ob.location = (46.91197967529297, -40.26901626586914, 0.745518684387207)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-3.2198519651444263e-15, 1.501441814336145e-15, 0.4363324046134949)
    ob.scale = (0.9999998807907104, 0.9999998807907104, 0.9999999403953552)
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
    try: ob['mass'] = 0.20000000298023224
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refLettersPhysicalDynamic.013 (type=MESH) ---
    ob = bpy.data.objects.get('refLettersPhysicalDynamic.013') or bpy.data.objects.new('refLettersPhysicalDynamic.013', bpy.data.meshes.get('Text.005'))
    ob.location = (45.89192581176758, -40.74467468261719, 0.745518684387207)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-3.2198519651444263e-15, 1.501441814336145e-15, 0.4363324046134949)
    ob.scale = (0.9999998807907104, 0.9999998807907104, 0.9999999403953552)
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
    try: ob['mass'] = 0.20000000298023224
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refLettersPhysicalDynamic.014 (type=MESH) ---
    ob = bpy.data.objects.get('refLettersPhysicalDynamic.014') or bpy.data.objects.new('refLettersPhysicalDynamic.014', bpy.data.meshes.get('Text.006'))
    ob.location = (45.034236907958984, -41.144622802734375, 0.745518684387207)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-3.2198519651444263e-15, 1.501441814336145e-15, 0.4363324046134949)
    ob.scale = (0.9999998807907104, 0.9999998807907104, 0.9999999403953552)
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
    try: ob['mass'] = 0.20000000298023224
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refLettersPhysicalDynamic.015 (type=MESH) ---
    ob = bpy.data.objects.get('refLettersPhysicalDynamic.015') or bpy.data.objects.new('refLettersPhysicalDynamic.015', bpy.data.meshes.get('Text.007'))
    ob.location = (43.45003128051758, -41.88334655761719, 0.745518684387207)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-3.2198519651444263e-15, 1.501441814336145e-15, 0.4363324046134949)
    ob.scale = (0.9999998807907104, 0.9999998807907104, 0.9999999403953552)
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
    try: ob['mass'] = 0.20000000298023224
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refLettersPhysicalDynamic.016 (type=MESH) ---
    ob = bpy.data.objects.get('refLettersPhysicalDynamic.016') or bpy.data.objects.new('refLettersPhysicalDynamic.016', bpy.data.meshes.get('Text.008'))
    ob.location = (42.112586975097656, -42.50701141357422, 0.745518684387207)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-3.2198519651444263e-15, 1.501441814336145e-15, 0.4363324046134949)
    ob.scale = (0.9999998807907104, 0.9999998807907104, 0.9999999403953552)
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
    try: ob['mass'] = 0.20000000298023224
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refLettersPhysicalDynamic.017 (type=MESH) ---
    ob = bpy.data.objects.get('refLettersPhysicalDynamic.017') or bpy.data.objects.new('refLettersPhysicalDynamic.017', bpy.data.meshes.get('Text.009'))
    ob.location = (40.83201217651367, -43.104148864746094, 0.7293243408203125)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-3.2198519651444263e-15, 1.501441814336145e-15, 0.4363324046134949)
    ob.scale = (0.9999998807907104, 0.9999998807907104, 0.9999999403953552)
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
    try: ob['mass'] = 0.20000000298023224
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refLettersPhysicalDynamic.018 (type=MESH) ---
    ob = bpy.data.objects.get('refLettersPhysicalDynamic.018') or bpy.data.objects.new('refLettersPhysicalDynamic.018', bpy.data.meshes.get('Text.020'))
    ob.location = (39.61381912231445, -43.672203063964844, 0.745518684387207)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-3.2198519651444263e-15, 1.501441814336145e-15, 0.4363324046134949)
    ob.scale = (0.9999998807907104, 0.9999998807907104, 0.9999999403953552)
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
    try: ob['mass'] = 0.20000000298023224
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refLettersPhysicalDynamic.019 (type=MESH) ---
    ob = bpy.data.objects.get('refLettersPhysicalDynamic.019') or bpy.data.objects.new('refLettersPhysicalDynamic.019', bpy.data.meshes.get('Text.021'))
    ob.location = (38.38277816772461, -44.246246337890625, 0.745518684387207)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.0325281652086033e-14, 1.5014416025779082e-15, 0.4363324046134949)
    ob.scale = (0.9999998807907104, 0.9999998807907104, 0.9999999403953552)
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
    try: ob['mass'] = 0.20000000298023224
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.222 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.222') or bpy.data.objects.new('cuboid.222', None)
    ob.location = (-1.0864124298095703, -5.822963714599609, 0.7192150354385376)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (2.524019180327741e-07, 7.875369334442439e-08, 0.43633216619491577)
    ob.scale = (1.1739226579666138, 0.4422047436237335, 1.4499430656433105)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.223 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.223') or bpy.data.objects.new('cuboid.223', None)
    ob.location = (0.13197946548461914, -5.254817485809326, 0.7192147970199585)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (2.384185791015625e-07, 7.845186900112822e-08, 0.43633225560188293)
    ob.scale = (1.1417648792266846, 0.4422047436237335, 1.449942946434021)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.224 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.224') or bpy.data.objects.new('cuboid.224', None)
    ob.location = (1.374258041381836, -4.675534248352051, 0.703020453453064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (2.3841856489070778e-07, 7.845186189570086e-08, 0.43633219599723816)
    ob.scale = (1.1991759538650513, 0.4422047436237335, 1.449942946434021)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.225 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.225') or bpy.data.objects.new('cuboid.225', None)
    ob.location = (2.6548309326171875, -4.07839298248291, 0.7192147970199585)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (2.3841856489070778e-07, 7.845186189570086e-08, 0.43633222579956055)
    ob.scale = (1.2333693504333496, 0.4422047436237335, 1.449942946434021)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.226 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.226') or bpy.data.objects.new('cuboid.226', None)
    ob.location = (3.992277145385742, -3.4547321796417236, 0.7192147970199585)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (2.3841856489070778e-07, 7.845186189570086e-08, 0.43633222579956055)
    ob.scale = (1.3513798713684082, 0.4422047436237335, 1.449942946434021)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.227 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.227') or bpy.data.objects.new('cuboid.227', None)
    ob.location = (6.434171676635742, -2.3160581588745117, 0.7192147970199585)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (2.3841856489070778e-07, 7.845186189570086e-08, 0.43633219599723816)
    ob.scale = (0.35772544145584106, 0.4422047436237335, 1.449942946434021)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.228 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.228') or bpy.data.objects.new('cuboid.228', None)
    ob.location = (5.576480865478516, -2.716005563735962, 0.7192147970199585)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (2.3841856489070778e-07, 7.845186189570086e-08, 0.43633222579956055)
    ob.scale = (1.1133092641830444, 0.4422047436237335, 1.449942946434021)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.229 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.229') or bpy.data.objects.new('cuboid.229', None)
    ob.location = (7.454225540161133, -1.8403992652893066, 0.7192147970199585)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (2.3841856489070778e-07, 7.845186189570086e-08, 0.43633219599723816)
    ob.scale = (1.4803125858306885, 0.4422047436237335, 1.449942946434021)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.230 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.230') or bpy.data.objects.new('cuboid.230', None)
    ob.location = (8.905420303344727, -1.1636962890625, 0.7192147970199585)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (2.3841856489070778e-07, 7.845186189570086e-08, 0.43633222579956055)
    ob.scale = (1.3753741979599, 0.4422047436237335, 1.449942946434021)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.231 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.231') or bpy.data.objects.new('cuboid.231', None)
    ob.location = (10.242863655090332, -0.5400352478027344, 0.7192147970199585)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (2.3841856489070778e-07, 7.845186189570086e-08, 0.43633222579956055)
    ob.scale = (1.2284659147262573, 0.4422047436237335, 1.449942946434021)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 21 objects to title.001')

if __name__ == '__main__': run()
