"""Bruno's 080_easter.001.py - verbatim recreation.

`easter.001` zone — a dynamic-egg easter egg cluster around (53.4, -36.4):
6 MESH (eggPhysicalDynamic x6 + basketPhysicalDynamic) + 15 EMPTY (easter
root, ball refs, frustum, interactive point, basket collision cuboids).

Adds: 21 objects (6 MESH + 15 EMPTY) to collection `easter.001`.

Section 13 (food / misc / fx). Collection is linked to the scene root here
(Bruno relies on 999_finalize for that; we do not run it yet), matching the
section-02..06 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/080_easter.001.py

"""
import bpy

def run():
    print('[080_easter.001] easter.001')
    coll = bpy.data.collections.get('easter.001')
    if coll is None: coll = bpy.data.collections.new('easter.001')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: eggPhysicalDynamic (type=MESH) ---
    ob = bpy.data.objects.get('eggPhysicalDynamic') or bpy.data.objects.new('eggPhysicalDynamic', bpy.data.meshes.get('Sphere'))
    ob.location = (53.345211029052734, -36.62298583984375, 0.9559670686721802)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.3490658104419708)
    ob.scale = (0.5025457143783569, 0.5025457143783569, 0.5025457143783569)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: easter (type=EMPTY) ---
    ob = bpy.data.objects.get('easter') or bpy.data.objects.new('easter', None)
    ob.location = (53.47407531738281, -36.41196060180664, 0.8951517343521118)
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

    # --- object: ball.002 (type=EMPTY) ---
    ob = bpy.data.objects.get('ball.002') or bpy.data.objects.new('ball.002', None)
    ob.location = (53.7476806640625, -36.33066940307617, 0.9712316989898682)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.5291034579277039, 0.5291034579277039, 0.5291034579277039)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'SPHERE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refInteractivePoint.007 (type=EMPTY) ---
    ob = bpy.data.objects.get('refInteractivePoint.007') or bpy.data.objects.new('refInteractivePoint.007', None)
    ob.location = (56.15900802612305, -36.62894821166992, 1.7493627071380615)
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

    # --- object: refZoneFrustum.013 (type=EMPTY) ---
    ob = bpy.data.objects.get('refZoneFrustum.013') or bpy.data.objects.new('refZoneFrustum.013', None)
    ob.location = (54.053157806396484, -36.80424499511719, 3.2733685970306396)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.5707961320877075, 0.0, 0.0)
    ob.scale = (4.006772041320801, 4.006772041320801, 4.006772041320801)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: basketPhysicalDynamic (type=MESH) ---
    ob = bpy.data.objects.get('basketPhysicalDynamic') or bpy.data.objects.new('basketPhysicalDynamic', bpy.data.meshes.get('Cylinder.019'))
    ob.location = (53.53419494628906, -36.17994689941406, 0.8893823623657227)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.3490658104419708)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.089 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.089') or bpy.data.objects.new('cuboid.089', None)
    ob.location = (0.8730944991111755, 0.0, -0.32601529359817505)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.22008377313613892, 0.0)
    ob.scale = (0.2075352519750595, 2.117274522781372, 1.0732406377792358)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.090 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.090') or bpy.data.objects.new('cuboid.090', None)
    ob.location = (1.8477439880371094e-06, 0.8730888366699219, -0.32601529359817505)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.5269472797285744e-08, 0.22008377313613892, 1.570796251296997)
    ob.scale = (0.2075352519750595, 2.117274522781372, 1.0732406377792358)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.091 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.091') or bpy.data.objects.new('cuboid.091', None)
    ob.location = (-0.8730908036231995, 1.4386888490432181e-15, -0.32601529359817505)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.5269472797285744e-08, 0.22008375823497772, 3.141592502593994)
    ob.scale = (0.2075352519750595, 2.117274522781372, 1.0732406377792358)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.232 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.232') or bpy.data.objects.new('cuboid.232', None)
    ob.location = (1.8477439880371094e-06, -0.8730888366699219, -0.32601529359817505)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-3.053894559457149e-08, 0.22008375823497772, 4.71238899230957)
    ob.scale = (0.2075352519750595, 2.117274522781372, 1.0732406377792358)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.233 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.233') or bpy.data.objects.new('cuboid.233', None)
    ob.location = (0.0, 0.0, -0.8122097849845886)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.8284680843353271, 1.8284680843353271, 0.15293610095977783)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: eggPhysicalDynamic.001 (type=MESH) ---
    ob = bpy.data.objects.get('eggPhysicalDynamic.001') or bpy.data.objects.new('eggPhysicalDynamic.001', bpy.data.meshes.get('Sphere.002'))
    ob.location = (53.65577697753906, -35.757083892822266, 0.9559670686721802)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.42592334747314453, 0.29951760172843933, 0.6106359362602234)
    ob.scale = (0.5025457143783569, 0.5025457143783569, 0.5025457143783569)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: ball.003 (type=EMPTY) ---
    ob = bpy.data.objects.get('ball.003') or bpy.data.objects.new('ball.003', None)
    ob.location = (53.7476806640625, -36.33066940307617, 0.9712316989898682)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.5291034579277039, 0.5291033983230591, 0.5291035175323486)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'SPHERE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: eggPhysicalDynamic.002 (type=MESH) ---
    ob = bpy.data.objects.get('eggPhysicalDynamic.002') or bpy.data.objects.new('eggPhysicalDynamic.002', bpy.data.meshes.get('Sphere.004'))
    ob.location = (52.884403228759766, -35.916744232177734, 1.446761965751648)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.42592334747314453, 0.29951760172843933, 0.6106359362602234)
    ob.scale = (0.5025457143783569, 0.5025457143783569, 0.5025457143783569)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: ball.004 (type=EMPTY) ---
    ob = bpy.data.objects.get('ball.004') or bpy.data.objects.new('ball.004', None)
    ob.location = (53.7476806640625, -36.33066940307617, 0.9712316989898682)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.5291034579277039, 0.5291033983230591, 0.5291035175323486)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'SPHERE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: eggPhysicalDynamic.003 (type=MESH) ---
    ob = bpy.data.objects.get('eggPhysicalDynamic.003') or bpy.data.objects.new('eggPhysicalDynamic.003', bpy.data.meshes.get('Sphere.006'))
    ob.location = (54.131935119628906, -36.478965759277344, 1.296808123588562)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0840267539024353, -0.573762834072113, 0.9677577018737793)
    ob.scale = (0.5025457143783569, 0.5025457143783569, 0.5025457143783569)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: ball.005 (type=EMPTY) ---
    ob = bpy.data.objects.get('ball.005') or bpy.data.objects.new('ball.005', None)
    ob.location = (53.7476806640625, -36.33066940307617, 0.9712316989898682)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (0.5291035175323486, 0.5291035175323486, 0.5291035175323486)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'SPHERE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: eggPhysicalDynamic.004 (type=MESH) ---
    ob = bpy.data.objects.get('eggPhysicalDynamic.004') or bpy.data.objects.new('eggPhysicalDynamic.004', bpy.data.meshes.get('Sphere.008'))
    ob.location = (54.224342346191406, -37.55651092529297, 0.4351850748062134)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-0.44639620184898376, -0.1745290905237198, 0.8587167263031006)
    ob.scale = (0.5025457143783569, 0.5025457143783569, 0.5025457143783569)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: ball.006 (type=EMPTY) ---
    ob = bpy.data.objects.get('ball.006') or bpy.data.objects.new('ball.006', None)
    ob.location = (53.7476806640625, -36.33066940307617, 0.9712316989898682)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-0.4362475574016571, 0.2772289514541626, 0.048336293548345566)
    ob.scale = (0.5291035175323486, 0.5291035175323486, 0.5291035175323486)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'SPHERE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: eggPhysicalDynamic.005 (type=MESH) ---
    ob = bpy.data.objects.get('eggPhysicalDynamic.005') or bpy.data.objects.new('eggPhysicalDynamic.005', bpy.data.meshes.get('Sphere.011'))
    ob.location = (52.40146255493164, -37.53445053100586, 0.5064300298690796)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.3407617509365082, 0.013476991094648838, 0.819459080696106)
    ob.scale = (0.5025457143783569, 0.5025457143783569, 0.5025457143783569)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: ball.007 (type=EMPTY) ---
    ob = bpy.data.objects.get('ball.007') or bpy.data.objects.new('ball.007', None)
    ob.location = (53.7476806640625, -36.33066940307617, 0.9712316989898682)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.1468818485736847, 0.5630579590797424, -0.2305326759815216)
    ob.scale = (0.5291035175323486, 0.5291035175323486, 0.5291035175323486)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'SPHERE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 21 objects to easter.001')

if __name__ == '__main__': run()
