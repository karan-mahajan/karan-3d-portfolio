import bpy

def run():
    print('[061_career] career')
    coll = bpy.data.collections.get('career')
    if coll is None: coll = bpy.data.collections.new('career')

    # --- object: Plane.048 (type=MESH) ---
    ob = bpy.data.objects.get('Plane.048') or bpy.data.objects.new('Plane.048', bpy.data.meshes.get('Plane.077'))
    ob.location = (23.051668167114258, -6.599363803863525, 0.03954815864562988)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Plane.049 (type=MESH) ---
    ob = bpy.data.objects.get('Plane.049') or bpy.data.objects.new('Plane.049', bpy.data.meshes.get('Plane.078'))
    ob.location = (23.051668167114258, -6.599363803863525, 0.0413644015789032)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refLine (type=EMPTY) ---
    ob = bpy.data.objects.get('refLine') or bpy.data.objects.new('refLine', None)
    ob.location = (27.06379508972168, -6.532436847686768, 0.0413644015789032)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'PLAIN_AXES'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    try: ob['hasEnd'] = True
    except Exception: pass
    try: ob['size'] = '4'
    except Exception: pass
    try: ob['color'] = 'blue'
    except Exception: pass
    try: ob['texture'] = 'careerHetic'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Plane.035 (type=MESH) ---
    ob = bpy.data.objects.get('Plane.035') or bpy.data.objects.new('Plane.035', bpy.data.meshes.get('Plane.098'))
    ob.location = (27.063796997070312, -6.532436370849609, 0.0413644015789032)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: stone (type=MESH) ---
    ob = bpy.data.objects.get('stone') or bpy.data.objects.new('stone', bpy.data.meshes.get('Plane.102'))
    ob.location = (-12.021645545959473, 30.739238739013672, 0.0413644015789032)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: careerText (type=MESH) ---
    ob = bpy.data.objects.get('careerText') or bpy.data.objects.new('careerText', bpy.data.meshes.get('Plane.076'))
    ob.location = (-11.156068801879883, 31.660669326782227, 0.7207581996917725)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (1.3089970350265503, -7.990412598246621e-08, 0.7853981256484985)
    ob.scale = (1.565000057220459, 0.29499998688697815, 1.0)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refLine.001 (type=EMPTY) ---
    ob = bpy.data.objects.get('refLine.001') or bpy.data.objects.new('refLine.001', None)
    ob.location = (27.06379508972168, -1.5337128639221191, 0.0413644015789032)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'PLAIN_AXES'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    try: ob['size'] = 2
    except Exception: pass
    try: ob['hasEnd'] = True
    except Exception: pass
    try: ob['color'] = 'orange'
    except Exception: pass
    try: ob['texture'] = 'careerUzik'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: stone.001 (type=MESH) ---
    ob = bpy.data.objects.get('stone.001') or bpy.data.objects.new('stone.001', bpy.data.meshes.get('Plane.095'))
    ob.location = (-12.021645545959473, 30.739238739013672, 0.0413644015789032)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: careerText.001 (type=MESH) ---
    ob = bpy.data.objects.get('careerText.001') or bpy.data.objects.new('careerText.001', bpy.data.meshes.get('Plane.097'))
    ob.location = (-11.690288543701172, 31.207935333251953, 0.717738151550293)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (1.3089970350265503, -7.990412598246621e-08, 0.7853981256484985)
    ob.scale = (0.8299999833106995, 0.29499998688697815, 1.0)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refLine.002 (type=EMPTY) ---
    ob = bpy.data.objects.get('refLine.002') or bpy.data.objects.new('refLine.002', None)
    ob.location = (27.06379508972168, 1.4863333702087402, 0.0413644015789032)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'PLAIN_AXES'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    try: ob['size'] = 2
    except Exception: pass
    try: ob['hasEnd'] = True
    except Exception: pass
    try: ob['color'] = 'orange'
    except Exception: pass
    try: ob['texture'] = 'careerImmersiveGarden'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Plane.018 (type=MESH) ---
    ob = bpy.data.objects.get('Plane.018') or bpy.data.objects.new('Plane.018', bpy.data.meshes.get('Plane.079'))
    ob.location = (27.063796997070312, 1.4863338470458984, 0.0413644015789032)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: stone.002 (type=MESH) ---
    ob = bpy.data.objects.get('stone.002') or bpy.data.objects.new('stone.002', bpy.data.meshes.get('Plane.081'))
    ob.location = (-12.021645545959473, 30.739238739013672, 0.0413644015789032)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: careerText.002 (type=MESH) ---
    ob = bpy.data.objects.get('careerText.002') or bpy.data.objects.new('careerText.002', bpy.data.meshes.get('Plane.082'))
    ob.location = (-11.025640487670898, 31.664073944091797, 0.6836532950401306)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (1.3089970350265503, -7.990412598246621e-08, 0.7853981256484985)
    ob.scale = (1.690000057220459, 0.29499998688697815, 1.0)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refLine.003 (type=EMPTY) ---
    ob = bpy.data.objects.get('refLine.003') or bpy.data.objects.new('refLine.003', None)
    ob.location = (27.06379508972168, 4.461507320404053, 0.0413644015789032)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'PLAIN_AXES'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    try: ob['size'] = 6
    except Exception: pass
    try: ob['hasEnd'] = False
    except Exception: pass
    try: ob['color'] = 'purple'
    except Exception: pass
    try: ob['texture'] = 'careerOnlineTeacher'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: stone.003 (type=MESH) ---
    ob = bpy.data.objects.get('stone.003') or bpy.data.objects.new('stone.003', bpy.data.meshes.get('Plane.087'))
    ob.location = (-12.021645545959473, 30.739238739013672, 0.0413644015789032)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: careerText.003 (type=MESH) ---
    ob = bpy.data.objects.get('careerText.003') or bpy.data.objects.new('careerText.003', bpy.data.meshes.get('Plane.088'))
    ob.location = (-11.155184745788574, 31.69133949279785, 0.7628021240234375)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (1.3089970350265503, -7.990412598246621e-08, 0.7853981256484985)
    ob.scale = (1.659999966621399, 0.45500001311302185, 1.0)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refLine.004 (type=EMPTY) ---
    ob = bpy.data.objects.get('refLine.004') or bpy.data.objects.new('refLine.004', None)
    ob.location = (29.05409049987793, -3.5350441932678223, 0.0413644015789032)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'PLAIN_AXES'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    try: ob['hasEnd'] = False
    except Exception: pass
    try: ob['color'] = 'orange'
    except Exception: pass
    try: ob['size'] = 14
    except Exception: pass
    try: ob['texture'] = 'careerFreelancer'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: stone.004 (type=MESH) ---
    ob = bpy.data.objects.get('stone.004') or bpy.data.objects.new('stone.004', bpy.data.meshes.get('Plane.103'))
    ob.location = (-12.021645545959473, 30.739238739013672, 0.0413644015789032)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: careerText.004 (type=MESH) ---
    ob = bpy.data.objects.get('careerText.004') or bpy.data.objects.new('careerText.004', bpy.data.meshes.get('Plane.104'))
    ob.location = (-11.413111686706543, 31.475378036499023, 0.5850260257720947)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (1.3089970350265503, -7.990412598246621e-08, 0.7853981256484985)
    ob.scale = (1.2000000476837158, 0.29499998688697815, 1.0)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refLine.005 (type=EMPTY) ---
    ob = bpy.data.objects.get('refLine.005') or bpy.data.objects.new('refLine.005', None)
    ob.location = (25.050939559936523, -1.5219216346740723, 0.0413644015789032)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'PLAIN_AXES'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    try: ob['hasEnd'] = True
    except Exception: pass
    try: ob['color'] = 'purple'
    except Exception: pass
    try: ob['size'] = 9
    except Exception: pass
    try: ob['texture'] = 'careerIRLTeacher'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Plane.022 (type=MESH) ---
    ob = bpy.data.objects.get('Plane.022') or bpy.data.objects.new('Plane.022', bpy.data.meshes.get('Plane.105'))
    ob.location = (25.050941467285156, -1.5219230651855469, 0.0413644015789032)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: stone.005 (type=MESH) ---
    ob = bpy.data.objects.get('stone.005') or bpy.data.objects.new('stone.005', bpy.data.meshes.get('Plane.123'))
    ob.location = (-12.021645545959473, 30.739238739013672, 0.0413644015789032)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: careerText.005 (type=MESH) ---
    ob = bpy.data.objects.get('careerText.005') or bpy.data.objects.new('careerText.005', bpy.data.meshes.get('Plane.124'))
    ob.location = (-11.27207088470459, 31.59507942199707, 1.150992751121521)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (1.3089970350265503, -7.990412598246621e-08, 0.7853981256484985)
    ob.scale = (1.3250000476837158, 0.45500001311302185, 1.0)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refYear (type=EMPTY) ---
    ob = bpy.data.objects.get('refYear') or bpy.data.objects.new('refYear', None)
    ob.location = (23.038597106933594, -6.526758670806885, 0.07861466705799103)
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

    # --- object: digit0 (type=MESH) ---
    ob = bpy.data.objects.get('digit0') or bpy.data.objects.new('digit0', bpy.data.meshes.get('Plane.108'))
    ob.location = (-16.67180061340332, 33.53141784667969, 0.12764152884483337)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.14335614442825317, 0.14335614442825317, 0.14335614442825317)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: digit0.004 (type=MESH) ---
    ob = bpy.data.objects.get('digit0.004') or bpy.data.objects.new('digit0.004', bpy.data.meshes.get('Plane.114'))
    ob.location = (-16.25381088256836, 33.53141784667969, 0.12764152884483337)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.14335614442825317, 0.14335614442825317, 0.14335614442825317)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: digit0.005 (type=MESH) ---
    ob = bpy.data.objects.get('digit0.005') or bpy.data.objects.new('digit0.005', bpy.data.meshes.get('Plane.115'))
    ob.location = (-15.835821151733398, 33.53141784667969, 0.12764152884483337)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.14335614442825317, 0.14335614442825317, 0.14335614442825317)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: digit0.006 (type=MESH) ---
    ob = bpy.data.objects.get('digit0.006') or bpy.data.objects.new('digit0.006', bpy.data.meshes.get('Plane.116'))
    ob.location = (-15.417831420898438, 33.53141784667969, 0.12764152884483337)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.14335614442825317, 0.14335614442825317, 0.14335614442825317)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Plane.030 (type=MESH) ---
    ob = bpy.data.objects.get('Plane.030') or bpy.data.objects.new('Plane.030', bpy.data.meshes.get('Plane.075'))
    ob.location = (-16.046842575073242, 33.675926208496094, 0.07861466705799103)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refZoneBounding.001 (type=EMPTY) ---
    ob = bpy.data.objects.get('refZoneBounding.001') or bpy.data.objects.new('refZoneBounding.001', None)
    ob.location = (25.844032287597656, 0.9047669172286987, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (10.885139465332031, 10.885139465332031, 10.885139465332031)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: career (type=EMPTY) ---
    ob = bpy.data.objects.get('career') or bpy.data.objects.new('career', None)
    ob.location = (25.844032287597656, 0.9047669172286987, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
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

    # --- object: refZoneFrustum.001 (type=EMPTY) ---
    ob = bpy.data.objects.get('refZoneFrustum.001') or bpy.data.objects.new('refZoneFrustum.001', None)
    ob.location = (25.974700927734375, 1.688776969909668, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (9.904455184936523, 9.904455184936523, 9.904455184936523)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 32 objects to career')

if __name__ == '__main__': run()