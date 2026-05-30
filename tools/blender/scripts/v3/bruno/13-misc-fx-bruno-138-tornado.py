"""Bruno's 138_tornado.py - verbatim recreation.

`tornado` collection — 17 EMPTY objects (tornado.000..tornado.016), all
PLAIN_AXES pivots at a fixed z=3.2733683586120605, scattered across the map
to trace the tornado's path. No meshes, materials, or modifiers.

Adds: 17 objects (17 EMPTY) to collection `tornado`.

Section 13 (food / misc / fx). Collection is linked to the scene root here
(Bruno relies on 999_finalize for that; we do not run it yet), matching the
section-02..06 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/138_tornado.py

"""
import bpy

def run():
    print('[138_tornado] tornado')
    coll = bpy.data.collections.get('tornado')
    if coll is None: coll = bpy.data.collections.new('tornado')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: tornado.000 (type=EMPTY) ---
    ob = bpy.data.objects.get('tornado.000') or bpy.data.objects.new('tornado.000', None)
    ob.location = (63.66011428833008, 0.24352645874023438, 3.2733683586120605)
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

    # --- object: tornado.001 (type=EMPTY) ---
    ob = bpy.data.objects.get('tornado.001') or bpy.data.objects.new('tornado.001', None)
    ob.location = (75.43683624267578, 14.113993644714355, 3.2733683586120605)
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

    # --- object: tornado.002 (type=EMPTY) ---
    ob = bpy.data.objects.get('tornado.002') or bpy.data.objects.new('tornado.002', None)
    ob.location = (58.399864196777344, 21.561159133911133, 3.2733683586120605)
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

    # --- object: tornado.003 (type=EMPTY) ---
    ob = bpy.data.objects.get('tornado.003') or bpy.data.objects.new('tornado.003', None)
    ob.location = (38.92744445800781, 25.038375854492188, 3.2733683586120605)
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

    # --- object: tornado.004 (type=EMPTY) ---
    ob = bpy.data.objects.get('tornado.004') or bpy.data.objects.new('tornado.004', None)
    ob.location = (38.92744445800781, 13.633103370666504, 3.2733683586120605)
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

    # --- object: tornado.005 (type=EMPTY) ---
    ob = bpy.data.objects.get('tornado.005') or bpy.data.objects.new('tornado.005', None)
    ob.location = (26.82672691345215, 11.824950218200684, 3.2733683586120605)
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

    # --- object: tornado.006 (type=EMPTY) ---
    ob = bpy.data.objects.get('tornado.006') or bpy.data.objects.new('tornado.006', None)
    ob.location = (24.601306915283203, -14.045546531677246, 3.2733683586120605)
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

    # --- object: tornado.007 (type=EMPTY) ---
    ob = bpy.data.objects.get('tornado.007') or bpy.data.objects.new('tornado.007', None)
    ob.location = (12.917855262756348, -22.808134078979492, 3.2733683586120605)
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

    # --- object: tornado.008 (type=EMPTY) ---
    ob = bpy.data.objects.get('tornado.008') or bpy.data.objects.new('tornado.008', None)
    ob.location = (16.534162521362305, -36.43882751464844, 3.2733683586120605)
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

    # --- object: tornado.009 (type=EMPTY) ---
    ob = bpy.data.objects.get('tornado.009') or bpy.data.objects.new('tornado.009', None)
    ob.location = (2.2080249786376953, -53.824913024902344, 3.2733683586120605)
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

    # --- object: tornado.010 (type=EMPTY) ---
    ob = bpy.data.objects.get('tornado.010') or bpy.data.objects.new('tornado.010', None)
    ob.location = (3.0425572395324707, -67.87287139892578, 3.2733683586120605)
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

    # --- object: tornado.011 (type=EMPTY) ---
    ob = bpy.data.objects.get('tornado.011') or bpy.data.objects.new('tornado.011', None)
    ob.location = (23.071331024169922, -65.23018646240234, 3.2733683586120605)
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

    # --- object: tornado.012 (type=EMPTY) ---
    ob = bpy.data.objects.get('tornado.012') or bpy.data.objects.new('tornado.012', None)
    ob.location = (32.80754089355469, -47.148658752441406, 3.2733683586120605)
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

    # --- object: tornado.013 (type=EMPTY) ---
    ob = bpy.data.objects.get('tornado.013') or bpy.data.objects.new('tornado.013', None)
    ob.location = (51.44542694091797, -45.618682861328125, 3.2733683586120605)
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

    # --- object: tornado.014 (type=EMPTY) ---
    ob = bpy.data.objects.get('tornado.014') or bpy.data.objects.new('tornado.014', None)
    ob.location = (58.399864196777344, -32.68343734741211, 3.2733683586120605)
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

    # --- object: tornado.015 (type=EMPTY) ---
    ob = bpy.data.objects.get('tornado.015') or bpy.data.objects.new('tornado.015', None)
    ob.location = (72.72599792480469, -23.503583908081055, 3.2733683586120605)
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

    # --- object: tornado.016 (type=EMPTY) ---
    ob = bpy.data.objects.get('tornado.016') or bpy.data.objects.new('tornado.016', None)
    ob.location = (62.5725212097168, -12.932843208312988, 3.2733683586120605)
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

    print('  added 17 objects to tornado')

if __name__ == '__main__': run()
