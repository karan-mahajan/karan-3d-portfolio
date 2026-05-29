import bpy

def run():
    print('[093_projects] projects')
    coll = bpy.data.collections.get('projects')
    if coll is None: coll = bpy.data.collections.new('projects')

    # --- object: refInteractivePoint (type=EMPTY) ---
    ob = bpy.data.objects.get('refInteractivePoint') or bpy.data.objects.new('refInteractivePoint', None)
    ob.location = (37.2390022277832, -14.257179260253906, 1.5)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.2857739329338074)
    ob.scale = (0.9999999403953552, 0.9999999403953552, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'PLAIN_AXES'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: physicalFixed.001 (type=EMPTY) ---
    ob = bpy.data.objects.get('physicalFixed.001') or bpy.data.objects.new('physicalFixed.001', None)
    ob.location = (36.698829650878906, -12.150222778320312, 5.97536563873291e-06)
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

    # --- object: cuboid.060 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.060') or bpy.data.objects.new('cuboid.060', None)
    ob.location = (-2.1139984130859375, 27.58566665649414, 0.5218616724014282)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, -1.3962630033493042)
    ob.scale = (1.1034810543060303, 2.2822999954223633, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.062 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.062') or bpy.data.objects.new('cuboid.062', None)
    ob.location = (-1.6344261169433594, 29.265703201293945, 1.7442834377288818)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, -1.0471974611282349)
    ob.scale = (0.5079601407051086, 1.2504092454910278, 3.5154268741607666)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.061 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.061') or bpy.data.objects.new('cuboid.061', None)
    ob.location = (-5.7784881591796875, 27.619495391845703, 2.1045455932617188)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, -0.872664749622345)
    ob.scale = (0.5079600214958191, 4.649426460266113, 4.141059875488281)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refZoneBounding.003 (type=EMPTY) ---
    ob = bpy.data.objects.get('refZoneBounding.003') or bpy.data.objects.new('refZoneBounding.003', None)
    ob.location = (35.759559631347656, -13.40835189819336, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (7.2188262939453125, 7.2188262939453125, 7.2188262939453125)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.065 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.065') or bpy.data.objects.new('Cube.065', bpy.data.meshes.get('Cube.049'))
    ob.location = (33.328590393066406, -9.692031860351562, 0.10018552839756012)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.6981317400932312)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: projects (type=EMPTY) ---
    ob = bpy.data.objects.get('projects') or bpy.data.objects.new('projects', None)
    ob.location = (35.759559631347656, -13.40835189819336, 3.2733683586120605)
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

    # --- object: refZoneFrustum.003 (type=EMPTY) ---
    ob = bpy.data.objects.get('refZoneFrustum.003') or bpy.data.objects.new('refZoneFrustum.003', None)
    ob.location = (34.79536819458008, -9.933792114257812, 3.3658716678619385)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (6.248077392578125, 6.248077392578125, 6.248077392578125)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 9 objects to projects')

if __name__ == '__main__': run()