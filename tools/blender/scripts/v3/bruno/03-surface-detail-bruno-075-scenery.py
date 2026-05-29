"""Bruno's 075_scenery.py - verbatim recreation.

The race-circuit's branded scenery: 10 visible MESH props (branded signs/
poles using circuitBrand/circuitWebgl/circuitWebgpu/palette, some with
BEVEL or Smooth-by-Angle modifiers) + 33 EMPTY collider proxies
(cuboid.* box + tube.* cylinder colliders).

NOTE: collection `scenery` lives under `circuit` -> `areas`, NOT mounted
to scene root until section 08. Objects exist in the Outliner but will not
render until then. Faithful Bruno behavior.

Adds: 43 objects (10 MESH + 33 EMPTY) to collection `scenery`.

Source: folio-2025/scripts/blender_world_steps/steps/075_scenery.py
"""
import bpy

def run():
    print('[075_scenery] scenery')
    coll = bpy.data.collections.get('scenery')
    if coll is None: coll = bpy.data.collections.new('scenery')

    # --- object: refObjectsPhysicalDynamic.013 (type=MESH) ---
    ob = bpy.data.objects.get('refObjectsPhysicalDynamic.013') or bpy.data.objects.new('refObjectsPhysicalDynamic.013', bpy.data.meshes.get('Plane.130'))
    ob.location = (-23.4140567779541, 2.2604422569274902, 0.4411274194717407)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.1645139455795288, 1.1645139455795288, 1.1645139455795288)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    m = ob.modifiers.new('Bevel', 'BEVEL')
    try: m.use_pin_to_last = False
    except Exception: pass
    try: m.use_apply_on_spline = False
    except Exception: pass
    try: m.width = 0.05000000074505806
    except Exception: pass
    try: m.width_pct = 0.05000000074505806
    except Exception: pass
    try: m.segments = 1
    except Exception: pass
    try: m.affect = 'EDGES'
    except Exception: pass
    try: m.limit_method = 'ANGLE'
    except Exception: pass
    try: m.edge_weight = 'bevel_weight_edge'
    except Exception: pass
    try: m.vertex_weight = 'bevel_weight_vert'
    except Exception: pass
    try: m.angle_limit = 0.5235987901687622
    except Exception: pass
    try: m.vertex_group = ''
    except Exception: pass
    try: m.invert_vertex_group = False
    except Exception: pass
    try: m.use_clamp_overlap = True
    except Exception: pass
    try: m.offset_type = 'OFFSET'
    except Exception: pass
    try: m.profile_type = 'SUPERELLIPSE'
    except Exception: pass
    try: m.profile = 0.5
    except Exception: pass
    try: m.material = -1
    except Exception: pass
    try: m.loop_slide = True
    except Exception: pass
    try: m.mark_seam = False
    except Exception: pass
    try: m.mark_sharp = False
    except Exception: pass
    try: m.harden_normals = False
    except Exception: pass
    try: m.face_strength_mode = 'FSTR_NONE'
    except Exception: pass
    try: m.miter_outer = 'MITER_SHARP'
    except Exception: pass
    try: m.miter_inner = 'MITER_SHARP'
    except Exception: pass
    try: m.spread = 0.10000000149011612
    except Exception: pass
    try: m.vmesh_method = 'ADJ'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refObjectsPhysicalDynamic.011 (type=MESH) ---
    ob = bpy.data.objects.get('refObjectsPhysicalDynamic.011') or bpy.data.objects.new('refObjectsPhysicalDynamic.011', bpy.data.meshes.get('Cube.220'))
    ob.location = (-24.845964431762695, 4.09045934677124, 0.5911454558372498)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, -0.5599629282951355)
    ob.scale = (1.1645139455795288, 1.1645139455795288, 1.1645139455795288)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.088 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.088') or bpy.data.objects.new('Cube.088', bpy.data.meshes.get('Cube.217'))
    ob.location = (-1.7313258647918701, -15.725229263305664, 0.9997153878211975)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
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
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refObjectsPhysicalDynamic.009 (type=MESH) ---
    ob = bpy.data.objects.get('refObjectsPhysicalDynamic.009') or bpy.data.objects.new('refObjectsPhysicalDynamic.009', bpy.data.meshes.get('Cylinder.069'))
    ob.location = (-20.309328079223633, 3.8416380882263184, 0.7538084983825684)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
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

    # --- object: Cylinder.039 (type=MESH) ---
    ob = bpy.data.objects.get('Cylinder.039') or bpy.data.objects.new('Cylinder.039', bpy.data.meshes.get('Cylinder.061'))
    ob.location = (-21.275835037231445, 7.84143590927124, 3.682002067565918)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, -3.141592502593994)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    m = ob.modifiers.new('Bevel', 'BEVEL')
    try: m.use_pin_to_last = False
    except Exception: pass
    try: m.use_apply_on_spline = False
    except Exception: pass
    try: m.width = 0.10000000149011612
    except Exception: pass
    try: m.width_pct = 0.10000000149011612
    except Exception: pass
    try: m.segments = 1
    except Exception: pass
    try: m.affect = 'EDGES'
    except Exception: pass
    try: m.limit_method = 'ANGLE'
    except Exception: pass
    try: m.edge_weight = 'bevel_weight_edge'
    except Exception: pass
    try: m.vertex_weight = 'bevel_weight_vert'
    except Exception: pass
    try: m.angle_limit = 0.5235987901687622
    except Exception: pass
    try: m.vertex_group = ''
    except Exception: pass
    try: m.invert_vertex_group = False
    except Exception: pass
    try: m.use_clamp_overlap = True
    except Exception: pass
    try: m.offset_type = 'OFFSET'
    except Exception: pass
    try: m.profile_type = 'SUPERELLIPSE'
    except Exception: pass
    try: m.profile = 0.5
    except Exception: pass
    try: m.material = -1
    except Exception: pass
    try: m.loop_slide = True
    except Exception: pass
    try: m.mark_seam = False
    except Exception: pass
    try: m.mark_sharp = False
    except Exception: pass
    try: m.harden_normals = False
    except Exception: pass
    try: m.face_strength_mode = 'FSTR_NONE'
    except Exception: pass
    try: m.miter_outer = 'MITER_SHARP'
    except Exception: pass
    try: m.miter_inner = 'MITER_SHARP'
    except Exception: pass
    try: m.spread = 0.10000000149011612
    except Exception: pass
    try: m.vmesh_method = 'ADJ'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.170 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.170') or bpy.data.objects.new('cuboid.170', None)
    ob.location = (-63.93140411376953, 41.35839080810547, 0.5911454558372498)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.3961279392242432, 1.7724859714508057, 1.1483426094055176)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.172 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.172') or bpy.data.objects.new('cuboid.172', None)
    ob.location = (-62.49949645996094, 39.52837371826172, 0.4411274194717407)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.2276972532272339, 1.2276972532272339, 0.8398918509483337)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: physicalFixed.006 (type=EMPTY) ---
    ob = bpy.data.objects.get('physicalFixed.006') or bpy.data.objects.new('physicalFixed.006', None)
    ob.location = (-24.44147300720215, -2.0299668312072754, 0.0)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'PLAIN_AXES'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: tube.027 (type=EMPTY) ---
    ob = bpy.data.objects.get('tube.027') or bpy.data.objects.new('tube.027', None)
    ob.location = (-59.39476776123047, 41.10957336425781, 0.7538084983825684)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.1699161529541016, 1.1699161529541016, 1.4995949268341064)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.173 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.173') or bpy.data.objects.new('cuboid.173', None)
    ob.location = (-66.8979263305664, 37.768287658691406, 2.7419228553771973)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.34906575083732605)
    ob.scale = (0.939760684967041, 0.939760684967041, 5.263763427734375)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refObjectsPhysicalDynamic.010 (type=MESH) ---
    ob = bpy.data.objects.get('refObjectsPhysicalDynamic.010') or bpy.data.objects.new('refObjectsPhysicalDynamic.010', bpy.data.meshes.get('Cylinder.069'))
    ob.location = (-26.534486770629883, -5.120447635650635, 0.7538084983825684)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
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

    # --- object: tube.028 (type=EMPTY) ---
    ob = bpy.data.objects.get('tube.028') or bpy.data.objects.new('tube.028', None)
    ob.location = (-59.39476776123047, 41.10957336425781, 0.7538084983825684)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.1699161529541016, 1.1699161529541016, 1.4995949268341064)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refObjectsPhysicalDynamic.008 (type=MESH) ---
    ob = bpy.data.objects.get('refObjectsPhysicalDynamic.008') or bpy.data.objects.new('refObjectsPhysicalDynamic.008', bpy.data.meshes.get('Cylinder.069'))
    ob.location = (-25.059083938598633, -4.4462456703186035, 0.7538084983825684)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
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

    # --- object: tube.029 (type=EMPTY) ---
    ob = bpy.data.objects.get('tube.029') or bpy.data.objects.new('tube.029', None)
    ob.location = (-59.39476776123047, 41.10957336425781, 0.7538084983825684)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.1699161529541016, 1.1699161529541016, 1.4995949268341064)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.174 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.174') or bpy.data.objects.new('cuboid.174', None)
    ob.location = (-40.820125579833984, 21.549739837646484, 2.7419228553771973)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -8.940696716308594e-08)
    ob.scale = (0.939760684967041, 0.939760684967041, 5.263763427734375)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.175 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.175') or bpy.data.objects.new('cuboid.175', None)
    ob.location = (-59.145408630371094, 20.85447120666504, 3.5689613819122314)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.939760684967041, 7.417290210723877, 7.133372783660889)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: tube.030 (type=EMPTY) ---
    ob = bpy.data.objects.get('tube.030') or bpy.data.objects.new('tube.030', None)
    ob.location = (-58.298763275146484, 25.641324996948242, 2.7998673915863037)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.14755062758922577, 0.14755062758922577, 5.628021717071533)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: tube.031 (type=EMPTY) ---
    ob = bpy.data.objects.get('tube.031') or bpy.data.objects.new('tube.031', None)
    ob.location = (-58.43733596801758, 37.235389709472656, 2.7998673915863037)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.14755062758922577, 0.14755062758922577, 5.628021717071533)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: tube.032 (type=EMPTY) ---
    ob = bpy.data.objects.get('tube.032') or bpy.data.objects.new('tube.032', None)
    ob.location = (-63.57501220703125, 29.69722557067871, 1.4799765348434448)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.14755062758922577, 0.14755062758922577, 2.9529266357421875)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: tube.034 (type=EMPTY) ---
    ob = bpy.data.objects.get('tube.034') or bpy.data.objects.new('tube.034', None)
    ob.location = (-68.51822662353516, 24.79233169555664, 1.4799765348434448)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.14755062758922577, 0.14755062758922577, 2.9529266357421875)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: tube.035 (type=EMPTY) ---
    ob = bpy.data.objects.get('tube.035') or bpy.data.objects.new('tube.035', None)
    ob.location = (-64.03413391113281, 47.51169204711914, 1.4799765348434448)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.14755062758922577, 0.14755062758922577, 2.9529266357421875)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: tube.036 (type=EMPTY) ---
    ob = bpy.data.objects.get('tube.036') or bpy.data.objects.new('tube.036', None)
    ob.location = (-64.03413391113281, 42.60679626464844, 1.4799765348434448)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.14755062758922577, 0.14755062758922577, 2.9529266357421875)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: tube.037 (type=EMPTY) ---
    ob = bpy.data.objects.get('tube.037') or bpy.data.objects.new('tube.037', None)
    ob.location = (-68.97734832763672, 42.60679626464844, 1.4799765348434448)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.14755062758922577, 0.14755062758922577, 2.9529266357421875)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: tube.038 (type=EMPTY) ---
    ob = bpy.data.objects.get('tube.038') or bpy.data.objects.new('tube.038', None)
    ob.location = (-57.85511779785156, 47.519676208496094, 1.4799765348434448)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.14755062758922577, 0.14755062758922577, 2.9529266357421875)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: tube.039 (type=EMPTY) ---
    ob = bpy.data.objects.get('tube.039') or bpy.data.objects.new('tube.039', None)
    ob.location = (-57.85511779785156, 42.61478042602539, 1.4799765348434448)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.14755062758922577, 0.14755062758922577, 2.9529266357421875)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: tube.040 (type=EMPTY) ---
    ob = bpy.data.objects.get('tube.040') or bpy.data.objects.new('tube.040', None)
    ob.location = (-62.79833221435547, 42.61478042602539, 1.4799765348434448)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.14755062758922577, 0.14755062758922577, 2.9529266357421875)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.176 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.176') or bpy.data.objects.new('cuboid.176', None)
    ob.location = (-59.177982330322266, 11.613347053527832, 0.5391743779182434)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.1656368970870972, 8.751059532165527, 1.0028969049453735)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.177 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.177') or bpy.data.objects.new('cuboid.177', None)
    ob.location = (-60.220726013183594, 11.613347053527832, 0.8772052526473999)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.1656368970870972, 8.751059532165527, 1.6675431728363037)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.178 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.178') or bpy.data.objects.new('cuboid.178', None)
    ob.location = (-61.32967758178711, 11.613347053527832, 1.2079153060913086)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.1656368970870972, 8.751059532165527, 2.41522479057312)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.179 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.179') or bpy.data.objects.new('cuboid.179', None)
    ob.location = (-61.896148681640625, 11.613347053527832, 1.7712241411209106)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.19263219833374023, 8.751059532165527, 3.5651607513427734)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.180 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.180') or bpy.data.objects.new('cuboid.180', None)
    ob.location = (-66.49684143066406, 23.07932472229004, 0.7168775796890259)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.8104988932609558)
    ob.scale = (1.0739758014678955, 3.690380096435547, 1.4525667428970337)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.181 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.181') or bpy.data.objects.new('cuboid.181', None)
    ob.location = (-41.8724365234375, 38.85771942138672, 0.7168775796890259)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.7696880102157593, 1.7825299501419067, 1.4525667428970337)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.182 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.182') or bpy.data.objects.new('cuboid.182', None)
    ob.location = (-41.896629333496094, 38.85114669799805, 2.431273937225342)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.7364826202392578, 1.7364799976348877, 4.820484161376953)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.183 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.183') or bpy.data.objects.new('cuboid.183', None)
    ob.location = (-47.663326263427734, 38.85114669799805, 3.974111557006836)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (9.873055458068848, 1.7364799976348877, 1.7364799976348877)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.184 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.184') or bpy.data.objects.new('cuboid.184', None)
    ob.location = (-60.3548469543457, 45.11763381958008, 2.906038284301758)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (5.275125026702881, 5.275117874145508, 0.525553822517395)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.185 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.185') or bpy.data.objects.new('cuboid.185', None)
    ob.location = (-66.54646301269531, 45.11763381958008, 2.906038284301758)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (5.275125026702881, 5.275117874145508, 0.525553822517395)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.186 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.186') or bpy.data.objects.new('cuboid.186', None)
    ob.location = (-66.05197143554688, 27.27779769897461, 2.906038284301758)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (5.275125026702881, 5.275117874145508, 0.525553822517395)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cylinder.022 (type=MESH) ---
    ob = bpy.data.objects.get('Cylinder.022') or bpy.data.objects.new('Cylinder.022', bpy.data.meshes.get('Cylinder.027'))
    ob.location = (-21.275835037231445, 7.84143590927124, 3.682002067565918)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, -3.141592502593994)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cylinder.037 (type=MESH) ---
    ob = bpy.data.objects.get('Cylinder.037') or bpy.data.objects.new('Cylinder.037', bpy.data.meshes.get('Cylinder.054'))
    ob.location = (-21.275835037231445, 7.84143590927124, 3.682002067565918)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, -3.141592502593994)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    m = ob.modifiers.new('Bevel', 'BEVEL')
    try: m.use_pin_to_last = False
    except Exception: pass
    try: m.use_apply_on_spline = False
    except Exception: pass
    try: m.width = 0.10000000149011612
    except Exception: pass
    try: m.width_pct = 0.10000000149011612
    except Exception: pass
    try: m.segments = 1
    except Exception: pass
    try: m.affect = 'EDGES'
    except Exception: pass
    try: m.limit_method = 'ANGLE'
    except Exception: pass
    try: m.edge_weight = 'bevel_weight_edge'
    except Exception: pass
    try: m.vertex_weight = 'bevel_weight_vert'
    except Exception: pass
    try: m.angle_limit = 0.5235987901687622
    except Exception: pass
    try: m.vertex_group = ''
    except Exception: pass
    try: m.invert_vertex_group = False
    except Exception: pass
    try: m.use_clamp_overlap = True
    except Exception: pass
    try: m.offset_type = 'OFFSET'
    except Exception: pass
    try: m.profile_type = 'SUPERELLIPSE'
    except Exception: pass
    try: m.profile = 0.5
    except Exception: pass
    try: m.material = -1
    except Exception: pass
    try: m.loop_slide = True
    except Exception: pass
    try: m.mark_seam = False
    except Exception: pass
    try: m.mark_sharp = False
    except Exception: pass
    try: m.harden_normals = False
    except Exception: pass
    try: m.face_strength_mode = 'FSTR_NONE'
    except Exception: pass
    try: m.miter_outer = 'MITER_SHARP'
    except Exception: pass
    try: m.miter_inner = 'MITER_SHARP'
    except Exception: pass
    try: m.spread = 0.10000000149011612
    except Exception: pass
    try: m.vmesh_method = 'ADJ'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.191 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.191') or bpy.data.objects.new('cuboid.191', None)
    ob.location = (-58.20966339111328, 17.619462966918945, 0.6979135870933533)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.8613864779472351, 3.891042470932007, 1.3350218534469604)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.192 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.192') or bpy.data.objects.new('cuboid.192', None)
    ob.location = (-41.552425384521484, 8.73681926727295, 0.7168775796890259)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.6577696204185486)
    ob.scale = (1.0739758014678955, 3.690380096435547, 1.4525667428970337)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refObjectsPhysicalDynamic.012 (type=MESH) ---
    ob = bpy.data.objects.get('refObjectsPhysicalDynamic.012') or bpy.data.objects.new('refObjectsPhysicalDynamic.012', bpy.data.meshes.get('Cube.234'))
    ob.location = (-25.15618324279785, 1.2763794660568237, 0.5911454558372498)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.22543515264987946)
    ob.scale = (1.1645138263702393, 1.1645138263702393, 1.1645139455795288)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.110 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.110') or bpy.data.objects.new('cuboid.110', None)
    ob.location = (-63.93140411376953, 41.35839080810547, 0.5911454558372498)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.3961279392242432, 1.7724859714508057, 1.1483426094055176)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 43 objects to scenery')

if __name__ == '__main__': run()
