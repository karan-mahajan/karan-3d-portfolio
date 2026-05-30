"""Bruno's 042_fences.py - verbatim recreation.

32 MESH objects into collection `fences`, alternating in pairs:
  - 16 visible fence planks (`fencePhysicalDynamic.NNN`, mesh `Cube.200`),
    hand-placed with per-fence Z-rotation to follow terrain paths.
  - 16 hidden wire collider cuboids (`cuboid.NNN`, mesh `Cube.056`), all
    collocated at the authoring template position (5.34, 4.82, 0.62) - the
    runtime physics clones the shape onto each fence by name prefix.

Adds: 32 MESH (16 visible + 16 wire) to collection `fences`.

Source: folio-2025/scripts/blender_world_steps/steps/042_fences.py
"""
import bpy

def run():
    print('[042_fences] fences')
    coll = bpy.data.collections.get('fences')
    if coll is None: coll = bpy.data.collections.new('fences')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: fencePhysicalDynamic.001 (type=MESH) ---
    ob = bpy.data.objects.get('fencePhysicalDynamic.001') or bpy.data.objects.new('fencePhysicalDynamic.001', bpy.data.meshes.get('Cube.200'))
    ob.location = (52.58647155761719, -21.144054412841797, 1.0418543815612793)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.18311543762683868)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.114 (type=MESH) ---
    ob = bpy.data.objects.get('cuboid.114') or bpy.data.objects.new('cuboid.114', bpy.data.meshes.get('Cube.056'))
    ob.location = (5.337918758392334, 4.819903373718262, 0.6206963658332825)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.7498611807823181)
    ob.scale = (2.134873867034912, 0.29328399896621704, 1.2495167255401611)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: fencePhysicalDynamic.002 (type=MESH) ---
    ob = bpy.data.objects.get('fencePhysicalDynamic.002') or bpy.data.objects.new('fencePhysicalDynamic.002', bpy.data.meshes.get('Cube.200'))
    ob.location = (55.2321662902832, -26.284879684448242, 1.0418543815612793)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.6665629148483276)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.115 (type=MESH) ---
    ob = bpy.data.objects.get('cuboid.115') or bpy.data.objects.new('cuboid.115', bpy.data.meshes.get('Cube.056'))
    ob.location = (5.337918758392334, 4.819903373718262, 0.6206963658332825)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.7498611807823181)
    ob.scale = (2.134873867034912, 0.29328399896621704, 1.2495167255401611)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: fencePhysicalDynamic.003 (type=MESH) ---
    ob = bpy.data.objects.get('fencePhysicalDynamic.003') or bpy.data.objects.new('fencePhysicalDynamic.003', bpy.data.meshes.get('Cube.200'))
    ob.location = (61.62055969238281, -29.833984375, 1.0418543815612793)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 1.1717818975448608)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.116 (type=MESH) ---
    ob = bpy.data.objects.get('cuboid.116') or bpy.data.objects.new('cuboid.116', bpy.data.meshes.get('Cube.056'))
    ob.location = (5.337918758392334, 4.819903373718262, 0.6206963658332825)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.7498611807823181)
    ob.scale = (2.134873867034912, 0.29328399896621704, 1.2495167255401611)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: fencePhysicalDynamic.004 (type=MESH) ---
    ob = bpy.data.objects.get('fencePhysicalDynamic.004') or bpy.data.objects.new('fencePhysicalDynamic.004', bpy.data.meshes.get('Cube.200'))
    ob.location = (62.717552185058594, -35.7276496887207, 1.0418543815612793)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 3.8629329204559326)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.117 (type=MESH) ---
    ob = bpy.data.objects.get('cuboid.117') or bpy.data.objects.new('cuboid.117', bpy.data.meshes.get('Cube.056'))
    ob.location = (5.337918758392334, 4.819903373718262, 0.6206963658332825)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.7498611807823181)
    ob.scale = (2.134873867034912, 0.29328399896621704, 1.2495167255401611)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: fencePhysicalDynamic.005 (type=MESH) ---
    ob = bpy.data.objects.get('fencePhysicalDynamic.005') or bpy.data.objects.new('fencePhysicalDynamic.005', bpy.data.meshes.get('Cube.200'))
    ob.location = (39.955116271972656, -32.218841552734375, 1.0418543815612793)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 7.105599403381348)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.118 (type=MESH) ---
    ob = bpy.data.objects.get('cuboid.118') or bpy.data.objects.new('cuboid.118', bpy.data.meshes.get('Cube.056'))
    ob.location = (5.337918758392334, 4.819903373718262, 0.6206963658332825)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.7498611807823181)
    ob.scale = (2.134873867034912, 0.29328399896621704, 1.2495167255401611)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: fencePhysicalDynamic.017 (type=MESH) ---
    ob = bpy.data.objects.get('fencePhysicalDynamic.017') or bpy.data.objects.new('fencePhysicalDynamic.017', bpy.data.meshes.get('Cube.200'))
    ob.location = (42.276649475097656, -14.586359024047852, 1.0418543815612793)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 4.458303451538086)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.130 (type=MESH) ---
    ob = bpy.data.objects.get('cuboid.130') or bpy.data.objects.new('cuboid.130', bpy.data.meshes.get('Cube.056'))
    ob.location = (5.337918758392334, 4.819903373718262, 0.6206963658332825)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.7498611807823181)
    ob.scale = (2.134873867034912, 0.29328399896621704, 1.2495167255401611)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: fencePhysicalDynamic.006 (type=MESH) ---
    ob = bpy.data.objects.get('fencePhysicalDynamic.006') or bpy.data.objects.new('fencePhysicalDynamic.006', bpy.data.meshes.get('Cube.200'))
    ob.location = (19.031627655029297, -40.86900329589844, 1.0418543815612793)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 8.954172134399414)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.119 (type=MESH) ---
    ob = bpy.data.objects.get('cuboid.119') or bpy.data.objects.new('cuboid.119', bpy.data.meshes.get('Cube.056'))
    ob.location = (5.337918758392334, 4.819903373718262, 0.6206963658332825)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.7498611807823181)
    ob.scale = (2.134873867034912, 0.29328399896621704, 1.2495167255401611)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: fencePhysicalDynamic.013 (type=MESH) ---
    ob = bpy.data.objects.get('fencePhysicalDynamic.013') or bpy.data.objects.new('fencePhysicalDynamic.013', bpy.data.meshes.get('Cube.200'))
    ob.location = (8.963541030883789, -38.598758697509766, 1.0418543815612793)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 9.443100929260254)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.007 (type=MESH) ---
    ob = bpy.data.objects.get('cuboid.007') or bpy.data.objects.new('cuboid.007', bpy.data.meshes.get('Cube.056'))
    ob.location = (5.337918758392334, 4.819903373718262, 0.6206963658332825)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.7498611807823181)
    ob.scale = (2.134873867034912, 0.29328399896621704, 1.2495167255401611)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: fencePhysicalDynamic.015 (type=MESH) ---
    ob = bpy.data.objects.get('fencePhysicalDynamic.015') or bpy.data.objects.new('fencePhysicalDynamic.015', bpy.data.meshes.get('Cube.200'))
    ob.location = (47.97075653076172, -45.96127700805664, 1.0418543815612793)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 3.0202977657318115)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.128 (type=MESH) ---
    ob = bpy.data.objects.get('cuboid.128') or bpy.data.objects.new('cuboid.128', bpy.data.meshes.get('Cube.056'))
    ob.location = (5.337918758392334, 4.819903373718262, 0.6206963658332825)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.7498611807823181)
    ob.scale = (2.134873867034912, 0.29328399896621704, 1.2495167255401611)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: fencePhysicalDynamic.011 (type=MESH) ---
    ob = bpy.data.objects.get('fencePhysicalDynamic.011') or bpy.data.objects.new('fencePhysicalDynamic.011', bpy.data.meshes.get('Cube.200'))
    ob.location = (75.29545593261719, 11.552993774414062, 0.9859189987182617)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.08252571523189545)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.129 (type=MESH) ---
    ob = bpy.data.objects.get('cuboid.129') or bpy.data.objects.new('cuboid.129', bpy.data.meshes.get('Cube.056'))
    ob.location = (5.337918758392334, 4.819903373718262, 0.6206963658332825)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.7498611807823181)
    ob.scale = (2.134873867034912, 0.29328399896621704, 1.2495167255401611)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: fencePhysicalDynamic.012 (type=MESH) ---
    ob = bpy.data.objects.get('fencePhysicalDynamic.012') or bpy.data.objects.new('fencePhysicalDynamic.012', bpy.data.meshes.get('Cube.200'))
    ob.location = (72.40026092529297, 12.707399368286133, 0.9607653617858887)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 5.615769386291504)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.200 (type=MESH) ---
    ob = bpy.data.objects.get('cuboid.200') or bpy.data.objects.new('cuboid.200', bpy.data.meshes.get('Cube.056'))
    ob.location = (5.337918758392334, 4.819903373718262, 0.6206963658332825)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.7498611807823181)
    ob.scale = (2.134873867034912, 0.29328399896621704, 1.2495167255401611)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: fencePhysicalDynamic.018 (type=MESH) ---
    ob = bpy.data.objects.get('fencePhysicalDynamic.018') or bpy.data.objects.new('fencePhysicalDynamic.018', bpy.data.meshes.get('Cube.200'))
    ob.location = (44.69112777709961, -25.242280960083008, 1.0418543815612793)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 5.96016788482666)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.161 (type=MESH) ---
    ob = bpy.data.objects.get('cuboid.161') or bpy.data.objects.new('cuboid.161', bpy.data.meshes.get('Cube.056'))
    ob.location = (5.337918758392334, 4.819903373718262, 0.6206963658332825)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.7498611807823181)
    ob.scale = (2.134873867034912, 0.29328399896621704, 1.2495167255401611)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: fencePhysicalDynamic.008 (type=MESH) ---
    ob = bpy.data.objects.get('fencePhysicalDynamic.008') or bpy.data.objects.new('fencePhysicalDynamic.008', bpy.data.meshes.get('Cube.200'))
    ob.location = (18.447494506835938, -73.57841491699219, 1.0418543815612793)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 3.693303346633911)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.121 (type=MESH) ---
    ob = bpy.data.objects.get('cuboid.121') or bpy.data.objects.new('cuboid.121', bpy.data.meshes.get('Cube.056'))
    ob.location = (5.337918758392334, 4.819903373718262, 0.6206963658332825)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.7498611807823181)
    ob.scale = (2.134873867034912, 0.29328399896621704, 1.2495167255401611)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: fencePhysicalDynamic.009 (type=MESH) ---
    ob = bpy.data.objects.get('fencePhysicalDynamic.009') or bpy.data.objects.new('fencePhysicalDynamic.009', bpy.data.meshes.get('Cube.200'))
    ob.location = (15.143651008605957, -76.73111724853516, 1.0418543815612793)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 4.198568344116211)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.122 (type=MESH) ---
    ob = bpy.data.objects.get('cuboid.122') or bpy.data.objects.new('cuboid.122', bpy.data.meshes.get('Cube.056'))
    ob.location = (5.337918758392334, 4.819903373718262, 0.6206963658332825)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.7498611807823181)
    ob.scale = (2.134873867034912, 0.29328399896621704, 1.2495167255401611)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: fencePhysicalDynamic.007 (type=MESH) ---
    ob = bpy.data.objects.get('fencePhysicalDynamic.007') or bpy.data.objects.new('fencePhysicalDynamic.007', bpy.data.meshes.get('Cube.200'))
    ob.location = (59.318519592285156, 10.421165466308594, 0.9859189987182617)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 1.2948966026306152)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.126 (type=MESH) ---
    ob = bpy.data.objects.get('cuboid.126') or bpy.data.objects.new('cuboid.126', bpy.data.meshes.get('Cube.056'))
    ob.location = (5.337918758392334, 4.819903373718262, 0.6206963658332825)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.7498611807823181)
    ob.scale = (2.134873867034912, 0.29328399896621704, 1.2495167255401611)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: fencePhysicalDynamic.010 (type=MESH) ---
    ob = bpy.data.objects.get('fencePhysicalDynamic.010') or bpy.data.objects.new('fencePhysicalDynamic.010', bpy.data.meshes.get('Cube.200'))
    ob.location = (57.6292610168457, 7.801774024963379, 0.9607653617858887)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 6.993191719055176)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.127 (type=MESH) ---
    ob = bpy.data.objects.get('cuboid.127') or bpy.data.objects.new('cuboid.127', bpy.data.meshes.get('Cube.056'))
    ob.location = (5.337918758392334, 4.819903373718262, 0.6206963658332825)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.7498611807823181)
    ob.scale = (2.134873867034912, 0.29328399896621704, 1.2495167255401611)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 32 objects to fences')

if __name__ == '__main__': run()