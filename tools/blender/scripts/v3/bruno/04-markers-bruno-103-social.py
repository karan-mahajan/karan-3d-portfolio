import bpy

def run():
    print('[103_social] social')
    coll = bpy.data.collections.get('social')
    if coll is None: coll = bpy.data.collections.new('social')

    # --- object: cuboid.041 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.041') or bpy.data.objects.new('cuboid.041', None)
    ob.location = (-5.28632116317749, 55.3609504699707, 0.08236762136220932)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.6122956275939941, 1.6122956275939941, 0.5008735060691833)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: physicalFixed.002 (type=EMPTY) ---
    ob = bpy.data.objects.get('physicalFixed.002') or bpy.data.objects.new('physicalFixed.002', None)
    ob.location = (25.95060920715332, 18.093017578125, 0.0)
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

    # --- object: cuboid.042 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.042') or bpy.data.objects.new('cuboid.042', None)
    ob.location = (-6.065268516540527, 58.76982116699219, 0.08236762136220932)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.44929808378219604)
    ob.scale = (1.6122956275939941, 1.6122956275939941, 0.5008735060691833)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.043 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.043') or bpy.data.objects.new('cuboid.043', None)
    ob.location = (-8.253053665161133, 61.506465911865234, 0.08236762881278992)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.8995013236999512)
    ob.scale = (1.6122955083847046, 1.6122955083847046, 0.5008735060691833)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.044 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.044') or bpy.data.objects.new('cuboid.044', None)
    ob.location = (-11.420791625976562, 63.0200080871582, 0.08236762136220932)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 1.3506317138671875)
    ob.scale = (1.6122956275939941, 1.6122956275939941, 0.5008735060691833)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.045 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.045') or bpy.data.objects.new('cuboid.045', None)
    ob.location = (-14.899587631225586, 63.008480072021484, 0.08236762136220932)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 1.7975879907608032)
    ob.scale = (1.6122956275939941, 1.6122956275939941, 0.5008735060691833)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.046 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.046') or bpy.data.objects.new('cuboid.046', None)
    ob.location = (-18.027620315551758, 61.49769973754883, 0.08236762136220932)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 2.243884801864624)
    ob.scale = (1.6122956275939941, 1.6122956275939941, 0.5008735060691833)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.047 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.047') or bpy.data.objects.new('cuboid.047', None)
    ob.location = (-20.202482223510742, 58.77377700805664, 0.08236762136220932)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 2.691734790802002)
    ob.scale = (1.6122956275939941, 1.6122956275939941, 0.5008735060691833)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.048 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.048') or bpy.data.objects.new('cuboid.048', None)
    ob.location = (-20.983335494995117, 55.368343353271484, 0.08236762136220932)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 3.140650749206543)
    ob.scale = (1.6122956275939941, 1.6122956275939941, 0.5008735060691833)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: hull (type=MESH) ---
    ob = bpy.data.objects.get('hull') or bpy.data.objects.new('hull', bpy.data.meshes.get('Cube.198'))
    ob.location = (-13.134831428527832, 55.3609504699707, 0.0001842975616455078)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.049 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.049') or bpy.data.objects.new('cuboid.049', None)
    ob.location = (0.3737841248512268, 70.44456481933594, 0.08236762136220932)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.6122956275939941, 1.6122956275939941, 0.5008735060691833)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refZoneBounding.002 (type=EMPTY) ---
    ob = bpy.data.objects.get('refZoneBounding.002') or bpy.data.objects.new('refZoneBounding.002', None)
    ob.location = (30.268720626831055, 25.780366897583008, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (15.810952186584473, 15.810952186584473, 15.810952186584473)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.133 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.133') or bpy.data.objects.new('Cube.133', bpy.data.meshes.get('Cube.197'))
    ob.location = (25.95060920715332, 18.093017578125, 0.0001842975616455078)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: social (type=EMPTY) ---
    ob = bpy.data.objects.get('social') or bpy.data.objects.new('social', None)
    ob.location = (28.901012420654297, 21.8236141204834, 3.2733683586120605)
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

    # --- object: refZoneFrustum.002 (type=EMPTY) ---
    ob = bpy.data.objects.get('refZoneFrustum.002') or bpy.data.objects.new('refZoneFrustum.002', None)
    ob.location = (29.657194137573242, 24.980676651000977, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (14.816764831542969, 14.816764831542969, 14.816764831542969)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 15 objects to social')

if __name__ == '__main__': run()