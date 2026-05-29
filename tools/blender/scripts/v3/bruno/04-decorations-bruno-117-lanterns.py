"""Bruno's 117_lanterns.py - verbatim recreation.

17 world-scattered lanterns via template-stack instancing: per lantern a
`base.NNN` body mesh (Cube.011) + `lantern.NNN` light mesh (Cube.022),
all created in-script. Hardcoded positions across the whole map.

Adds: 51 objects (34 MESH, 17 EMPTY) to collection `lanterns`.

Source: folio-2025/scripts/blender_world_steps/steps/117_lanterns.py
"""
import bpy

def run():
    print('[117_lanterns] lanterns')
    coll = bpy.data.collections.get('lanterns')
    if coll is None: coll = bpy.data.collections.new('lanterns')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: base (type=MESH) ---
    ob = bpy.data.objects.get('base') or bpy.data.objects.new('base', bpy.data.meshes.get('Cube.022'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: light (type=MESH) ---
    ob = bpy.data.objects.get('light') or bpy.data.objects.new('light', bpy.data.meshes.get('Cube.011'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: lantern (type=EMPTY) ---
    ob = bpy.data.objects.get('lantern') or bpy.data.objects.new('lantern', None)
    ob.location = (60.178096771240234, -47.141544342041016, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 1.4901161193847656e-08)
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

    # --- object: base.001 (type=MESH) ---
    ob = bpy.data.objects.get('base.001') or bpy.data.objects.new('base.001', bpy.data.meshes.get('Cube.022'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: light.001 (type=MESH) ---
    ob = bpy.data.objects.get('light.001') or bpy.data.objects.new('light.001', bpy.data.meshes.get('Cube.011'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: lantern.001 (type=EMPTY) ---
    ob = bpy.data.objects.get('lantern.001') or bpy.data.objects.new('lantern.001', None)
    ob.location = (64.8569564819336, -53.28731918334961, 0.48336055874824524)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-0.1132751926779747, 0.09949441999197006, -0.010916185565292835)
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

    # --- object: base.002 (type=MESH) ---
    ob = bpy.data.objects.get('base.002') or bpy.data.objects.new('base.002', bpy.data.meshes.get('Cube.022'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: light.002 (type=MESH) ---
    ob = bpy.data.objects.get('light.002') or bpy.data.objects.new('light.002', bpy.data.meshes.get('Cube.011'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: lantern.002 (type=EMPTY) ---
    ob = bpy.data.objects.get('lantern.002') or bpy.data.objects.new('lantern.002', None)
    ob.location = (67.87187194824219, -62.998207092285156, 0.503322422504425)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.1057509183883667)
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

    # --- object: base.003 (type=MESH) ---
    ob = bpy.data.objects.get('base.003') or bpy.data.objects.new('base.003', bpy.data.meshes.get('Cube.022'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: light.003 (type=MESH) ---
    ob = bpy.data.objects.get('light.003') or bpy.data.objects.new('light.003', bpy.data.meshes.get('Cube.011'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: lantern.003 (type=EMPTY) ---
    ob = bpy.data.objects.get('lantern.003') or bpy.data.objects.new('lantern.003', None)
    ob.location = (73.79798889160156, -10.043404579162598, 0.5120187997817993)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.4180251359939575)
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

    # --- object: base.004 (type=MESH) ---
    ob = bpy.data.objects.get('base.004') or bpy.data.objects.new('base.004', bpy.data.meshes.get('Cube.022'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: light.004 (type=MESH) ---
    ob = bpy.data.objects.get('light.004') or bpy.data.objects.new('light.004', bpy.data.meshes.get('Cube.011'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: lantern.004 (type=EMPTY) ---
    ob = bpy.data.objects.get('lantern.004') or bpy.data.objects.new('lantern.004', None)
    ob.location = (50.797664642333984, -21.37541961669922, 0.512020468711853)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.0290955305099487)
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

    # --- object: base.005 (type=MESH) ---
    ob = bpy.data.objects.get('base.005') or bpy.data.objects.new('base.005', bpy.data.meshes.get('Cube.022'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: light.005 (type=MESH) ---
    ob = bpy.data.objects.get('light.005') or bpy.data.objects.new('light.005', bpy.data.meshes.get('Cube.011'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: lantern.005 (type=EMPTY) ---
    ob = bpy.data.objects.get('lantern.005') or bpy.data.objects.new('lantern.005', None)
    ob.location = (33.5164680480957, -40.11678695678711, 0.5184165239334106)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.8598452806472778)
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

    # --- object: base.006 (type=MESH) ---
    ob = bpy.data.objects.get('base.006') or bpy.data.objects.new('base.006', bpy.data.meshes.get('Cube.022'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: light.006 (type=MESH) ---
    ob = bpy.data.objects.get('light.006') or bpy.data.objects.new('light.006', bpy.data.meshes.get('Cube.011'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: lantern.006 (type=EMPTY) ---
    ob = bpy.data.objects.get('lantern.006') or bpy.data.objects.new('lantern.006', None)
    ob.location = (21.034976959228516, -54.35683822631836, 0.5118030309677124)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -2.0630452632904053)
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

    # --- object: base.007 (type=MESH) ---
    ob = bpy.data.objects.get('base.007') or bpy.data.objects.new('base.007', bpy.data.meshes.get('Cube.022'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: light.007 (type=MESH) ---
    ob = bpy.data.objects.get('light.007') or bpy.data.objects.new('light.007', bpy.data.meshes.get('Cube.011'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: lantern.007 (type=EMPTY) ---
    ob = bpy.data.objects.get('lantern.007') or bpy.data.objects.new('lantern.007', None)
    ob.location = (23.06202507019043, -31.854101181030273, 1.9661411046981812)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.8352396488189697)
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

    # --- object: base.008 (type=MESH) ---
    ob = bpy.data.objects.get('base.008') or bpy.data.objects.new('base.008', bpy.data.meshes.get('Cube.022'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: light.008 (type=MESH) ---
    ob = bpy.data.objects.get('light.008') or bpy.data.objects.new('light.008', bpy.data.meshes.get('Cube.011'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: lantern.008 (type=EMPTY) ---
    ob = bpy.data.objects.get('lantern.008') or bpy.data.objects.new('lantern.008', None)
    ob.location = (-0.2358025312423706, -38.60416793823242, 0.5110964179039001)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.8352396488189697)
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

    # --- object: base.009 (type=MESH) ---
    ob = bpy.data.objects.get('base.009') or bpy.data.objects.new('base.009', bpy.data.meshes.get('Cube.022'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: light.009 (type=MESH) ---
    ob = bpy.data.objects.get('light.009') or bpy.data.objects.new('light.009', bpy.data.meshes.get('Cube.011'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: lantern.009 (type=EMPTY) ---
    ob = bpy.data.objects.get('lantern.009') or bpy.data.objects.new('lantern.009', None)
    ob.location = (30.20859718322754, -12.639383316040039, 0.5038201212882996)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -2.309014320373535)
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

    # --- object: base.010 (type=MESH) ---
    ob = bpy.data.objects.get('base.010') or bpy.data.objects.new('base.010', bpy.data.meshes.get('Cube.022'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: light.010 (type=MESH) ---
    ob = bpy.data.objects.get('light.010') or bpy.data.objects.new('light.010', bpy.data.meshes.get('Cube.011'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: lantern.010 (type=EMPTY) ---
    ob = bpy.data.objects.get('lantern.010') or bpy.data.objects.new('lantern.010', None)
    ob.location = (16.397497177124023, -10.959135055541992, 0.521390974521637)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.8018938302993774)
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

    # --- object: base.011 (type=MESH) ---
    ob = bpy.data.objects.get('base.011') or bpy.data.objects.new('base.011', bpy.data.meshes.get('Cube.022'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: light.011 (type=MESH) ---
    ob = bpy.data.objects.get('light.011') or bpy.data.objects.new('light.011', bpy.data.meshes.get('Cube.011'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: lantern.011 (type=EMPTY) ---
    ob = bpy.data.objects.get('lantern.011') or bpy.data.objects.new('lantern.011', None)
    ob.location = (73.98867797851562, 24.289873123168945, 1.2451081275939941)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.8018938302993774)
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

    # --- object: base.012 (type=MESH) ---
    ob = bpy.data.objects.get('base.012') or bpy.data.objects.new('base.012', bpy.data.meshes.get('Cube.022'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: light.012 (type=MESH) ---
    ob = bpy.data.objects.get('light.012') or bpy.data.objects.new('light.012', bpy.data.meshes.get('Cube.011'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: lantern.012 (type=EMPTY) ---
    ob = bpy.data.objects.get('lantern.012') or bpy.data.objects.new('lantern.012', None)
    ob.location = (40.938323974609375, 33.88887023925781, 0.5174238085746765)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.3026314973831177)
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

    # --- object: base.013 (type=MESH) ---
    ob = bpy.data.objects.get('base.013') or bpy.data.objects.new('base.013', bpy.data.meshes.get('Cube.022'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: light.013 (type=MESH) ---
    ob = bpy.data.objects.get('light.013') or bpy.data.objects.new('light.013', bpy.data.meshes.get('Cube.011'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: lantern.013 (type=EMPTY) ---
    ob = bpy.data.objects.get('lantern.013') or bpy.data.objects.new('lantern.013', None)
    ob.location = (-56.80698013305664, 66.64297485351562, 0.4688224792480469)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.02400694414973259, 0.005451634991914034, -1.294184923171997)
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

    # --- object: base.014 (type=MESH) ---
    ob = bpy.data.objects.get('base.014') or bpy.data.objects.new('base.014', bpy.data.meshes.get('Cube.022'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: light.014 (type=MESH) ---
    ob = bpy.data.objects.get('light.014') or bpy.data.objects.new('light.014', bpy.data.meshes.get('Cube.011'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: lantern.014 (type=EMPTY) ---
    ob = bpy.data.objects.get('lantern.014') or bpy.data.objects.new('lantern.014', None)
    ob.location = (-64.39108276367188, -26.705116271972656, 0.37072595953941345)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.3026314973831177)
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

    # --- object: base.016 (type=MESH) ---
    ob = bpy.data.objects.get('base.016') or bpy.data.objects.new('base.016', bpy.data.meshes.get('Cube.022'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: light.015 (type=MESH) ---
    ob = bpy.data.objects.get('light.015') or bpy.data.objects.new('light.015', bpy.data.meshes.get('Cube.011'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: lantern.015 (type=EMPTY) ---
    ob = bpy.data.objects.get('lantern.015') or bpy.data.objects.new('lantern.015', None)
    ob.location = (46.6634635925293, -31.220855712890625, 0.512020468711853)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.3789390325546265)
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

    # --- object: base.017 (type=MESH) ---
    ob = bpy.data.objects.get('base.017') or bpy.data.objects.new('base.017', bpy.data.meshes.get('Cube.022'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.45100679993629456)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: light.016 (type=MESH) ---
    ob = bpy.data.objects.get('light.016') or bpy.data.objects.new('light.016', bpy.data.meshes.get('Cube.011'))
    ob.location = (62.646270751953125, -45.66196060180664, 1.9549851417541504)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.45100679993629456)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: lantern.016 (type=EMPTY) ---
    ob = bpy.data.objects.get('lantern.016') or bpy.data.objects.new('lantern.016', None)
    ob.location = (53.226966857910156, -39.91443634033203, 1.2621697187423706)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.9279322028160095)
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

    print('  added 51 objects to lanterns')

if __name__ == '__main__': run()