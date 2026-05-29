import bpy

def run():
    print('[081_lab] lab')
    coll = bpy.data.collections.get('lab')
    if coll is None: coll = bpy.data.collections.new('lab')

    # --- object: refInteractivePoint.001 (type=EMPTY) ---
    ob = bpy.data.objects.get('refInteractivePoint.001') or bpy.data.objects.new('refInteractivePoint.001', None)
    ob.location = (13.67009449005127, -18.607881546020508, 1.4999995231628418)
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

    # --- object: physicalFixed (type=EMPTY) ---
    ob = bpy.data.objects.get('physicalFixed') or bpy.data.objects.new('physicalFixed', None)
    ob.location = (13.190083503723145, -16.659812927246094, 1.0036048889160156)
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

    # --- object: cuboid.069 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.069') or bpy.data.objects.new('cuboid.069', None)
    ob.location = (-28.417091369628906, 22.049022674560547, 1.9729840755462646)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 2.257000207901001)
    ob.scale = (0.5434275269508362, 4.712501525878906, 3.9839961528778076)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.071 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.071') or bpy.data.objects.new('cuboid.071', None)
    ob.location = (-25.100513458251953, 24.339332580566406, 2.4955809116363525)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 2.0876731872558594)
    ob.scale = (0.5434275269508362, 2.706019878387451, 4.898336410522461)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refCarpet.001 (type=MESH) ---
    ob = bpy.data.objects.get('refCarpet.001') or bpy.data.objects.new('refCarpet.001', bpy.data.meshes.get('Plane.028'))
    ob.location = (13.687878608703613, -18.654367446899414, 0.019051702693104744)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.2617994546890259)
    ob.scale = (0.9999998211860657, 0.9999998211860657, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refWood (type=MESH) ---
    ob = bpy.data.objects.get('refWood') or bpy.data.objects.new('refWood', bpy.data.meshes.get('Cube.095'))
    ob.location = (11.110730171203613, -17.56622886657715, 0.04742095246911049)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.4067942500114441, 0.4290562570095062, 3.116767406463623)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refZoneBounding.004 (type=EMPTY) ---
    ob = bpy.data.objects.get('refZoneBounding.004') or bpy.data.objects.new('refZoneBounding.004', None)
    ob.location = (13.136816024780273, -17.684432983398438, 3.2733683586120605)
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

    # --- object: refFire (type=EMPTY) ---
    ob = bpy.data.objects.get('refFire') or bpy.data.objects.new('refFire', None)
    ob.location = (11.13591480255127, -17.302471160888672, 0.3688110411167145)
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

    # --- object: lab (type=EMPTY) ---
    ob = bpy.data.objects.get('lab') or bpy.data.objects.new('lab', None)
    ob.location = (13.136816024780273, -17.684432983398438, 3.2733683586120605)
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

    # --- object: refZoneFrustum.004 (type=EMPTY) ---
    ob = bpy.data.objects.get('refZoneFrustum.004') or bpy.data.objects.new('refZoneFrustum.004', None)
    ob.location = (12.0995512008667, -14.697568893432617, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (5.798162937164307, 5.798162937164307, 5.798162937164307)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.003 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.003') or bpy.data.objects.new('Cube.003', bpy.data.meshes.get('Cube.003'))
    ob.location = (10.774601936340332, -15.340337753295898, 1.8209261894226074)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.6981317400932312)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 11 objects to lab')

if __name__ == '__main__': run()