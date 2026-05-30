"""Bruno's 079_cookie.py - verbatim recreation.

`cookie` zone — Bruno's cookie/oven setup. 24 objects: a mix of MESH props
(refCookie, lava, refBanner, refOvenHeat, refCounterPanel, tablePhysicalDynamic,
Cube.135/054, refBlower.001) and EMPTY refs/cuboids (chimney, spawner, table,
interactive point, physics cuboids, zone bounding/frustum CIRCLEs, root).

Adds: 24 objects (9 MESH + 15 EMPTY) to collection `cookie`.

Section 13 (food / misc / fx). Collection is linked to the scene root here
(Bruno relies on 999_finalize for that; we do not run it yet), matching the
section-02..06 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/079_cookie.py

"""
import bpy

def run():
    print('[079_cookie] cookie')
    coll = bpy.data.collections.get('cookie')
    if coll is None: coll = bpy.data.collections.new('cookie')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: refCookie (type=MESH) ---
    ob = bpy.data.objects.get('refCookie') or bpy.data.objects.new('refCookie', bpy.data.meshes.get('Cube.092'))
    ob.location = (10.431934356689453, -33.99968338012695, 1.278944730758667)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob['preventAutoAdd'] = True
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.135 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.135') or bpy.data.objects.new('Cube.135', bpy.data.meshes.get('Cube.065'))
    ob.location = (-4.040179252624512, 26.570384979248047, 0.34767380356788635)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-0.0, -3.141592502593994, -0.0)
    ob.scale = (1.8886948823928833, 1.2987818717956543, 1.2987818717956543)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: lava (type=MESH) ---
    ob = bpy.data.objects.get('lava') or bpy.data.objects.new('lava', bpy.data.meshes.get('Cube.110'))
    ob.location = (-1.8180783987045288, 28.31726837158203, 1.2223553657531738)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 1.5707961320877075)
    ob.scale = (0.9208148121833801, 0.9208148121833801, 0.9208148121833801)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refBanner (type=MESH) ---
    ob = bpy.data.objects.get('refBanner') or bpy.data.objects.new('refBanner', bpy.data.meshes.get('Plane.018'))
    ob.location = (2.583139657974243, 27.019941329956055, 1.6329516172409058)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.39199498295783997)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refChimney (type=EMPTY) ---
    ob = bpy.data.objects.get('refChimney') or bpy.data.objects.new('refChimney', None)
    ob.location = (10.477789878845215, -30.902931213378906, 3.0634987354278564)
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

    # --- object: refOvenHeat (type=MESH) ---
    ob = bpy.data.objects.get('refOvenHeat') or bpy.data.objects.new('refOvenHeat', bpy.data.meshes.get('Cube.141'))
    ob.location = (-2.988520622253418, 28.441566467285156, 1.2721463441848755)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 0.9151352047920227, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refSpawner (type=EMPTY) ---
    ob = bpy.data.objects.get('refSpawner') or bpy.data.objects.new('refSpawner', None)
    ob.location = (10.477789878845215, -32.418087005615234, 1.2550771236419678)
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

    # --- object: refInteractivePoint.002 (type=EMPTY) ---
    ob = bpy.data.objects.get('refInteractivePoint.002') or bpy.data.objects.new('refInteractivePoint.002', None)
    ob.location = (10.4725923538208, -36.2530632019043, 1.5)
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

    # --- object: refTable (type=EMPTY) ---
    ob = bpy.data.objects.get('refTable') or bpy.data.objects.new('refTable', None)
    ob.location = (13.605717658996582, -39.008758544921875, 1.1679893732070923)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, -1.5707961320877075)
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

    # --- object: refCounterPanel (type=MESH) ---
    ob = bpy.data.objects.get('refCounterPanel') or bpy.data.objects.new('refCounterPanel', bpy.data.meshes.get('Cube.037'))
    ob.location = (-2.8345236778259277, 27.882539749145508, 2.5353479385375977)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-0.2317887395620346, -0.02009507454931736, 0.2641388475894928)
    ob.scale = (1.0, 0.9999999403953552, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refCounterLabel (type=EMPTY) ---
    ob = bpy.data.objects.get('refCounterLabel') or bpy.data.objects.new('refCounterLabel', None)
    ob.location = (10.659789085388184, -31.509506225585938, 2.551530122756958)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-0.2317887395620346, -0.02009507454931736, 0.2641388475894928)
    ob.scale = (1.0, 0.9999999403953552, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'PLAIN_AXES'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cookiePhysicalFixed (type=EMPTY) ---
    ob = bpy.data.objects.get('cookiePhysicalFixed') or bpy.data.objects.new('cookiePhysicalFixed', None)
    ob.location = (11.289132118225098, -31.94276237487793, 1.6915301084518433)
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

    # --- object: cuboid.006 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.006') or bpy.data.objects.new('cuboid.006', None)
    ob.location = (-28.60007667541504, 6.237129211425781, 2.5108137130737305)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.9802305573080048e-08, -0.0629979819059372, -1.570796012878418)
    ob.scale = (2.0150506496429443, 2.0999879837036133, 1.7711607217788696)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.004 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.004') or bpy.data.objects.new('cuboid.004', None)
    ob.location = (-28.60007667541504, 5.783170700073242, 0.388126939535141)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (1.55957593506173e-08, 0.04964043200016022, -1.570796012878418)
    ob.scale = (2.339566707611084, 3.1501803398132324, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.005 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.005') or bpy.data.objects.new('cuboid.005', None)
    ob.location = (-23.085025787353516, 5.105350494384766, 2.04758882522583)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, -2.756941795349121)
    ob.scale = (0.22222156822681427, 0.23158852756023407, 4.146590709686279)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: tablePhysicalDynamic (type=MESH) ---
    ob = bpy.data.objects.get('tablePhysicalDynamic') or bpy.data.objects.new('tablePhysicalDynamic', bpy.data.meshes.get('Cube.071'))
    ob.location = (13.66597843170166, -39.0045051574707, 0.49444714188575745)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, -1.570796012878418)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.008 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.008') or bpy.data.objects.new('cuboid.008', None)
    ob.location = (-25.494831085205078, -1.7273011207580566, 0.5113053321838379)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, -1.570796012878418)
    ob.scale = (1.162388563156128, 2.42402720451355, 0.9810947179794312)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refZoneBounding.005 (type=EMPTY) ---
    ob = bpy.data.objects.get('refZoneBounding.005') or bpy.data.objects.new('refZoneBounding.005', None)
    ob.location = (11.444122314453125, -34.19161605834961, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (7.3363213539123535, 7.3363213539123535, 7.3363213539123535)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.054 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.054') or bpy.data.objects.new('Cube.054', bpy.data.meshes.get('Cube.072'))
    ob.location = (-27.951976776123047, 18.696733474731445, 0.08591055870056152)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, -2.094395160675049)
    ob.scale = (0.7589893937110901, 3.928497552871704, 0.5194132924079895)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refBlower.001 (type=MESH) ---
    ob = bpy.data.objects.get('refBlower.001') or bpy.data.objects.new('refBlower.001', bpy.data.meshes.get('Cube.077'))
    ob.location = (33.383750915527344, -13.272953033447266, 0.2756183445453644)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 3.141592264175415)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: blowerPhysicalDynamic.001 (type=EMPTY) ---
    ob = bpy.data.objects.get('blowerPhysicalDynamic.001') or bpy.data.objects.new('blowerPhysicalDynamic.001', None)
    ob.location = (13.084171295166016, -31.000612258911133, 0.5265605449676514)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 1.5707961320877075)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'PLAIN_AXES'
    except Exception: pass
    try: ob.empty_display_size = 2.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.001 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.001') or bpy.data.objects.new('cuboid.001', None)
    ob.location = (-5.401218414306641, 23.453699111938477, 0.5265605449676514)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, -0.5235986709594727)
    ob.scale = (1.1322354078292847, 1.5110598802566528, 0.9385600686073303)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cookie (type=EMPTY) ---
    ob = bpy.data.objects.get('cookie') or bpy.data.objects.new('cookie', None)
    ob.location = (12.2511625289917, -35.2508544921875, 3.2733683586120605)
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

    # --- object: refZoneFrustum.005 (type=EMPTY) ---
    ob = bpy.data.objects.get('refZoneFrustum.005') or bpy.data.objects.new('refZoneFrustum.005', None)
    ob.location = (9.746870994567871, -29.996524810791016, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (4.32136344909668, 4.32136344909668, 4.32136344909668)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 24 objects to cookie')

if __name__ == '__main__': run()
