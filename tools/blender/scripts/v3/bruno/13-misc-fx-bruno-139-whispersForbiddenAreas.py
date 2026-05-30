"""Bruno's 139_whispersForbiddenAreas.py - verbatim recreation.

`whispersForbiddenAreas` collection — 12 EMPTY objects (forbidden.000..011),
all CIRCLE empties X-tilted by -pi/2, varying scale, scattered across the
east/central map (no meshes, no modifiers). Marker zones only.

Adds: 12 objects (12 EMPTY) to collection `whispersForbiddenAreas`.

Section 13 (food / misc / fx). Collection is linked to the scene root here
(Bruno relies on 999_finalize for that; we do not run it yet), matching the
section-02..06 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/139_whispersForbiddenAreas.py

"""
import bpy

def run():
    print('[139_whispersForbiddenAreas] whispersForbiddenAreas')
    coll = bpy.data.collections.get('whispersForbiddenAreas')
    if coll is None: coll = bpy.data.collections.new('whispersForbiddenAreas')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: forbidden.000 (type=EMPTY) ---
    ob = bpy.data.objects.get('forbidden.000') or bpy.data.objects.new('forbidden.000', None)
    ob.location = (45.186466217041016, -33.126190185546875, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (2.349933624267578, 2.349933624267578, 2.349933624267578)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: forbidden.001 (type=EMPTY) ---
    ob = bpy.data.objects.get('forbidden.001') or bpy.data.objects.new('forbidden.001', None)
    ob.location = (39.62091064453125, -37.83202362060547, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (3.4071810245513916, 3.4071810245513916, 3.4071810245513916)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: forbidden.002 (type=EMPTY) ---
    ob = bpy.data.objects.get('forbidden.002') or bpy.data.objects.new('forbidden.002', None)
    ob.location = (54.97031021118164, -31.855266571044922, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (3.4071810245513916, 3.4071810245513916, 3.4071810245513916)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: forbidden.003 (type=EMPTY) ---
    ob = bpy.data.objects.get('forbidden.003') or bpy.data.objects.new('forbidden.003', None)
    ob.location = (55.241981506347656, -46.38965606689453, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (2.9637625217437744, 2.9637625217437744, 2.9637625217437744)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: forbidden.004 (type=EMPTY) ---
    ob = bpy.data.objects.get('forbidden.004') or bpy.data.objects.new('forbidden.004', None)
    ob.location = (69.65140533447266, -16.984004974365234, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (2.9637625217437744, 2.9637625217437744, 2.9637625217437744)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: forbidden.005 (type=EMPTY) ---
    ob = bpy.data.objects.get('forbidden.005') or bpy.data.objects.new('forbidden.005', None)
    ob.location = (53.22074890136719, 10.807270050048828, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (3.5485029220581055, 3.5485029220581055, 3.5485029220581055)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: forbidden.006 (type=EMPTY) ---
    ob = bpy.data.objects.get('forbidden.006') or bpy.data.objects.new('forbidden.006', None)
    ob.location = (25.934125900268555, 18.138904571533203, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (1.8121118545532227, 1.8121118545532227, 1.8121118545532227)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: forbidden.007 (type=EMPTY) ---
    ob = bpy.data.objects.get('forbidden.007') or bpy.data.objects.new('forbidden.007', None)
    ob.location = (39.3916130065918, 31.048704147338867, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (1.7317336797714233, 1.7317336797714233, 1.7317336797714233)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: forbidden.008 (type=EMPTY) ---
    ob = bpy.data.objects.get('forbidden.008') or bpy.data.objects.new('forbidden.008', None)
    ob.location = (12.866828918457031, -16.095458984375, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (4.367616176605225, 4.367616176605225, 4.367616176605225)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: forbidden.009 (type=EMPTY) ---
    ob = bpy.data.objects.get('forbidden.009') or bpy.data.objects.new('forbidden.009', None)
    ob.location = (35.77330780029297, -11.366978645324707, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (4.4545817375183105, 4.4545817375183105, 4.4545817375183105)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: forbidden.010 (type=EMPTY) ---
    ob = bpy.data.objects.get('forbidden.010') or bpy.data.objects.new('forbidden.010', None)
    ob.location = (16.636960983276367, -69.22044372558594, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (2.7817533016204834, 2.7817533016204834, 2.7817533016204834)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: forbidden.011 (type=EMPTY) ---
    ob = bpy.data.objects.get('forbidden.011') or bpy.data.objects.new('forbidden.011', None)
    ob.location = (24.330678939819336, -56.571449279785156, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (2.086829662322998, 2.086829662322998, 2.086829662322998)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 12 objects to whispersForbiddenAreas')

if __name__ == '__main__': run()
