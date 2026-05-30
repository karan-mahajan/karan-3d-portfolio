"""Bruno's 040_bushes.py - verbatim recreation.

130 MESH objects (Icosphere.NNN, all sharing mesh `Icosphere.002`) scattered
world-wide into collection `bushes`. Hand-authored locations sampled from the
terrain contour, with per-bush uniform scale (~0.75-1.09) and a handful of
discrete Z-rotations for orientation variety. The `palette` material rides on
the shared mesh datablock (yellow-green bush tint).

NOTE: at runtime Bruno's Foliage.js treats these 130 positions as SDF
foliage-cloud ANCHORS, not solid geometry. The .blend mesh is an authoring
proxy. (memory: reference_bruno_bushes_are_sdf)

Adds: 130 MESH to collection `bushes`.

Source: folio-2025/scripts/blender_world_steps/steps/040_bushes.py
"""
import bpy

def run():
    print('[040_bushes] bushes')
    coll = bpy.data.collections.get('bushes')
    if coll is None: coll = bpy.data.collections.new('bushes')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: Icosphere.001 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.001') or bpy.data.objects.new('Icosphere.001', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (22.679685592651367, -24.400585174560547, 1.3439249992370605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.002 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.002') or bpy.data.objects.new('Icosphere.002', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (20.138212203979492, -27.105648040771484, 1.1727571487426758)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0752686262130737, 1.0752686262130737, 1.0752686262130737)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.003 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.003') or bpy.data.objects.new('Icosphere.003', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (18.12603187561035, -24.453916549682617, 0.6900887489318848)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.004 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.004') or bpy.data.objects.new('Icosphere.004', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (57.659950256347656, -21.389053344726562, 0.9585583209991455)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.43312886357307434)
    ob.scale = (1.091712474822998, 1.091712474822998, 1.091712474822998)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.005 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.005') or bpy.data.objects.new('Icosphere.005', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (80.04498291015625, -15.389008522033691, 0.6391398906707764)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.43312886357307434)
    ob.scale = (0.9890879988670349, 0.9890879988670349, 0.9890879988670349)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.006 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.006') or bpy.data.objects.new('Icosphere.006', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (69.94895935058594, -61.96294021606445, 1.0091345310211182)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0115725994110107, 1.0115725994110107, 1.0115725994110107)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.007 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.007') or bpy.data.objects.new('Icosphere.007', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (77.38365173339844, -42.661041259765625, 1.1861821413040161)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9787534475326538, 0.9787534475326538, 0.9787534475326538)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.008 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.008') or bpy.data.objects.new('Icosphere.008', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (78.7024917602539, -36.899227142333984, 1.3979952335357666)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9412758350372314, 0.9412758350372314, 0.9412758350372314)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.009 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.009') or bpy.data.objects.new('Icosphere.009', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (61.66716003417969, -25.295747756958008, 0.8388587236404419)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0328147411346436, 1.0328147411346436, 1.0328147411346436)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.010 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.010') or bpy.data.objects.new('Icosphere.010', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (63.98786926269531, -23.896501541137695, 0.6392724514007568)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9385768175125122, 0.9385768175125122, 0.9385768175125122)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.012 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.012') or bpy.data.objects.new('Icosphere.012', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (0.1724560260772705, -1.3827309608459473, 1.2792298793792725)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.4821765124797821)
    ob.scale = (0.9799119234085083, 0.9799119234085083, 0.9799119234085083)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.017 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.017') or bpy.data.objects.new('Icosphere.017', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (13.840231895446777, -43.97511291503906, 0.9700474739074707)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9933256506919861, 0.9933256506919861, 0.9933256506919861)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.019 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.019') or bpy.data.objects.new('Icosphere.019', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (40.96516418457031, -55.10149383544922, 0.9159200191497803)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9627104997634888, 0.9627104997634888, 0.9627104997634888)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.020 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.020') or bpy.data.objects.new('Icosphere.020', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (39.60018539428711, -52.63501739501953, 0.882929801940918)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0444717407226562, 1.0444717407226562, 1.0444717407226562)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.021 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.021') or bpy.data.objects.new('Icosphere.021', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (58.20262145996094, -63.77557373046875, 1.2050296068191528)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.893242359161377, 0.893242359161377, 0.893242359161377)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.022 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.022') or bpy.data.objects.new('Icosphere.022', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (61.295379638671875, -64.93843841552734, 1.2005473375320435)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.965196967124939, 0.965196967124939, 0.965196967124939)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.025 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.025') or bpy.data.objects.new('Icosphere.025', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (79.57096099853516, -32.000755310058594, 1.018938422203064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9879469275474548, 0.9879469275474548, 0.9879469275474548)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.026 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.026') or bpy.data.objects.new('Icosphere.026', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (80.82972717285156, -27.7877254486084, 1.282313346862793)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9502503871917725, 0.9502503871917725, 0.9502503871917725)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.027 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.027') or bpy.data.objects.new('Icosphere.027', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (78.9906234741211, -26.231840133666992, 0.930968165397644)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0714809894561768, 1.0714809894561768, 1.0714809894561768)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.028 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.028') or bpy.data.objects.new('Icosphere.028', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (81.82133483886719, -25.665699005126953, 1.2613998651504517)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.899398148059845, 0.899398148059845, 0.899398148059845)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.029 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.029') or bpy.data.objects.new('Icosphere.029', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (82.7413101196289, -19.650442123413086, 1.2270481586456299)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.002970814704895, 1.002970814704895, 1.002970814704895)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.031 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.031') or bpy.data.objects.new('Icosphere.031', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (81.68038940429688, -10.04918098449707, 0.8538805246353149)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.43312886357307434)
    ob.scale = (1.078891396522522, 1.078891396522522, 1.078891396522522)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.036 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.036') or bpy.data.objects.new('Icosphere.036', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-4.805052757263184, -41.94911193847656, 1.0413446426391602)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0245286226272583, 1.0245286226272583, 1.0245286226272583)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.037 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.037') or bpy.data.objects.new('Icosphere.037', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-2.1193225383758545, -38.30595779418945, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.042 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.042') or bpy.data.objects.new('Icosphere.042', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (43.13175964355469, -71.59734344482422, 0.9518303871154785)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9614205360412598, 0.9614205360412598, 0.9614205360412598)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.043 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.043') or bpy.data.objects.new('Icosphere.043', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (45.06534194946289, -4.317457675933838, 0.7327064275741577)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.010648250579834, 1.010648250579834, 1.010648250579834)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.044 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.044') or bpy.data.objects.new('Icosphere.044', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (42.97755813598633, -1.9741692543029785, 0.9081296920776367)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.43312886357307434)
    ob.scale = (1.0712438821792603, 1.0712438821792603, 1.0712438821792603)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.045 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.045') or bpy.data.objects.new('Icosphere.045', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (78.26788330078125, -19.57787322998047, 0.7760609984397888)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.7452796101570129, 0.7452796101570129, 0.7452796101570129)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.046 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.046') or bpy.data.objects.new('Icosphere.046', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (78.25701904296875, -48.84804153442383, 1.2831556797027588)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.893242359161377, 0.893242359161377, 0.893242359161377)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.047 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.047') or bpy.data.objects.new('Icosphere.047', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (45.345455169677734, -48.15003204345703, 0.9700702428817749)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.5496704578399658)
    ob.scale = (0.9627104997634888, 0.9627104997634888, 0.9627104997634888)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.048 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.048') or bpy.data.objects.new('Icosphere.048', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (47.919944763183594, -48.69895553588867, 0.6291787028312683)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.5496704578399658)
    ob.scale = (1.0444717407226562, 1.0444717407226562, 1.0444717407226562)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.052 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.052') or bpy.data.objects.new('Icosphere.052', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (12.09388256072998, 5.985169887542725, 1.210798978805542)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.555677056312561)
    ob.scale = (0.9799119234085083, 0.9799119234085083, 0.9799119234085083)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.053 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.053') or bpy.data.objects.new('Icosphere.053', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (14.349808692932129, 6.6668829917907715, 1.1410659551620483)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.555677056312561)
    ob.scale = (0.9901148080825806, 0.9901148080825806, 0.9901148080825806)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.054 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.054') or bpy.data.objects.new('Icosphere.054', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (8.528304100036621, 9.001741409301758, 1.307465672492981)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.055 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.055') or bpy.data.objects.new('Icosphere.055', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (30.06296730041504, -25.434473037719727, 1.055806040763855)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.7655332684516907)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.056 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.056') or bpy.data.objects.new('Icosphere.056', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (31.752473831176758, -24.082612991333008, 0.6626973152160645)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.7655332684516907)
    ob.scale = (0.7754657864570618, 0.7754657864570618, 0.7754658460617065)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.060 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.060') or bpy.data.objects.new('Icosphere.060', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (54.90516662597656, -19.547473907470703, 0.3883714973926544)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.061 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.061') or bpy.data.objects.new('Icosphere.061', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (58.95918273925781, -12.294355392456055, 0.8314679861068726)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.062 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.062') or bpy.data.objects.new('Icosphere.062', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (39.93524932861328, -30.228439331054688, 1.1766457557678223)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.063 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.063') or bpy.data.objects.new('Icosphere.063', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (17.904569625854492, -77.92730712890625, 0.8215667009353638)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9979197382926941, 0.9979197382926941, 0.9979197382926941)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.064 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.064') or bpy.data.objects.new('Icosphere.064', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (22.107816696166992, -72.3375244140625, 0.9454903602600098)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0258523225784302, 1.0258523225784302, 1.0258523225784302)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.065 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.065') or bpy.data.objects.new('Icosphere.065', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (58.56475830078125, 4.35333776473999, 0.9081296920776367)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.43312886357307434)
    ob.scale = (1.0712438821792603, 1.0712438821792603, 1.0712438821792603)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.066 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.066') or bpy.data.objects.new('Icosphere.066', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (30.630403518676758, -49.331729888916016, 1.3439249992370605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.067 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.067') or bpy.data.objects.new('Icosphere.067', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (33.39353942871094, -34.88792419433594, 1.1766462326049805)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.068 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.068') or bpy.data.objects.new('Icosphere.068', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (42.94527053833008, -7.166286945343018, 0.7327064275741577)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.010648250579834, 1.010648250579834, 1.010648250579834)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.069 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.069') or bpy.data.objects.new('Icosphere.069', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (10.843525886535645, -8.25802230834961, 1.0213547945022583)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9644471406936646, 0.9644471406936646, 0.9644471406936646)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.070 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.070') or bpy.data.objects.new('Icosphere.070', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (14.156411170959473, -7.686407566070557, 1.2792303562164307)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.4821765124797821)
    ob.scale = (0.9799119234085083, 0.9799119234085083, 0.9799119234085083)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.071 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.071') or bpy.data.objects.new('Icosphere.071', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (1.2283413410186768, -10.777490615844727, 1.0213546752929688)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9644471406936646, 0.9644471406936646, 0.9644471406936646)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.023 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.023') or bpy.data.objects.new('Icosphere.023', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (8.232024192810059, -40.51759719848633, 0.9700477123260498)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9933256506919861, 0.9933256506919861, 0.9933256506919861)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.024 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.024') or bpy.data.objects.new('Icosphere.024', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (17.233020782470703, -41.86544418334961, 0.9700477123260498)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9933256506919861, 0.9933256506919861, 0.9933256506919861)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.038 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.038') or bpy.data.objects.new('Icosphere.038', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (8.138958930969238, 14.430444717407227, 1.1410659551620483)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.555677056312561)
    ob.scale = (0.9901148080825806, 0.9901148080825806, 0.9901148080825806)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.039 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.039') or bpy.data.objects.new('Icosphere.039', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (12.309100151062012, 20.95183563232422, 1.1410659551620483)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.555677056312561)
    ob.scale = (0.9901148080825806, 0.9901148080825806, 0.9901148080825806)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.040 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.040') or bpy.data.objects.new('Icosphere.040', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (10.93384075164795, 23.746719360351562, 1.1410659551620483)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.555677056312561)
    ob.scale = (0.9901148080825806, 0.9901148080825806, 0.9901148080825806)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.049 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.049') or bpy.data.objects.new('Icosphere.049', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (17.10032844543457, 24.900161743164062, 1.1410659551620483)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.555677056312561)
    ob.scale = (0.9901148080825806, 0.9901148080825806, 0.9901148080825806)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.050 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.050') or bpy.data.objects.new('Icosphere.050', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (21.802827835083008, 32.8411750793457, 1.1410659551620483)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.555677056312561)
    ob.scale = (0.9901148080825806, 0.9901148080825806, 0.9901148080825806)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.051 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.051') or bpy.data.objects.new('Icosphere.051', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (32.25205612182617, 36.26778793334961, 1.1410659551620483)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.555677056312561)
    ob.scale = (0.9901148080825806, 0.9901148080825806, 0.9901148080825806)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.057 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.057') or bpy.data.objects.new('Icosphere.057', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (36.99197006225586, 37.79435348510742, 1.1410659551620483)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.555677056312561)
    ob.scale = (0.9901148080825806, 0.9901148080825806, 0.9901148080825806)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.058 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.058') or bpy.data.objects.new('Icosphere.058', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (29.25584602355957, 30.93355941772461, 1.1410659551620483)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.555677056312561)
    ob.scale = (0.9901148080825806, 0.9901148080825806, 0.9901148080825806)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.059 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.059') or bpy.data.objects.new('Icosphere.059', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (37.108131408691406, 22.282733917236328, 1.1410659551620483)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.555677056312561)
    ob.scale = (0.9901148080825806, 0.9901148080825806, 0.9901148080825806)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.081 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.081') or bpy.data.objects.new('Icosphere.081', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (39.459381103515625, 20.59693145751953, 1.1410659551620483)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.555677056312561)
    ob.scale = (0.9901148080825806, 0.9901148080825806, 0.9901148080825806)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.082 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.082') or bpy.data.objects.new('Icosphere.082', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (38.52775573730469, 14.119905471801758, 1.1410659551620483)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.555677056312561)
    ob.scale = (0.9901148080825806, 0.9901148080825806, 0.9901148080825806)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.083 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.083') or bpy.data.objects.new('Icosphere.083', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (33.02671813964844, 10.260305404663086, 1.1410659551620483)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.555677056312561)
    ob.scale = (0.9901148080825806, 0.9901148080825806, 0.9901148080825806)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.084 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.084') or bpy.data.objects.new('Icosphere.084', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (46.79056167602539, 33.9219856262207, 1.1410659551620483)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.555677056312561)
    ob.scale = (0.9901148080825806, 0.9901148080825806, 0.9901148080825806)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.088 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.088') or bpy.data.objects.new('Icosphere.088', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-30.564180374145508, -75.71112823486328, 1.041795015335083)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9603079557418823, 0.9603079557418823, 0.9603079557418823)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.089 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.089') or bpy.data.objects.new('Icosphere.089', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-29.63421058654785, -80.12848663330078, 1.041795015335083)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9603079557418823, 0.9603079557418823, 0.9603079557418823)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.091 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.091') or bpy.data.objects.new('Icosphere.091', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-27.101938247680664, -77.00175476074219, 1.0417948961257935)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9603079557418823, 0.9603079557418823, 0.9603079557418823)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.097 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.097') or bpy.data.objects.new('Icosphere.097', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (22.125200271606445, -78.2076416015625, 1.1402353048324585)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9603079557418823, 0.9603079557418823, 0.9603079557418823)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.011 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.011') or bpy.data.objects.new('Icosphere.011', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-30.216676712036133, -20.13860321044922, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.013 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.013') or bpy.data.objects.new('Icosphere.013', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-22.450021743774414, -32.515567779541016, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.015 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.015') or bpy.data.objects.new('Icosphere.015', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-42.13734817504883, -52.717594146728516, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.033 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.033') or bpy.data.objects.new('Icosphere.033', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-46.51231002807617, -52.58892059326172, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.034 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.034') or bpy.data.objects.new('Icosphere.034', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-66.45698547363281, -56.835208892822266, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.035 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.035') or bpy.data.objects.new('Icosphere.035', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-77.90908813476562, -7.809902667999268, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.041 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.041') or bpy.data.objects.new('Icosphere.041', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-76.04438018798828, 1.9952216148376465, 1.3121612071990967)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.072 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.072') or bpy.data.objects.new('Icosphere.072', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-63.88347625732422, 16.12371063232422, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.073 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.073') or bpy.data.objects.new('Icosphere.073', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-52.81740188598633, 15.866360664367676, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.074 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.074') or bpy.data.objects.new('Icosphere.074', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-52.688724517822266, 13.550207138061523, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.075 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.075') or bpy.data.objects.new('Icosphere.075', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-49.85786819458008, 6.087037563323975, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.076 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.076') or bpy.data.objects.new('Icosphere.076', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-66.07096099853516, 38.38454818725586, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.077 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.077') or bpy.data.objects.new('Icosphere.077', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-50.3725700378418, 37.9985237121582, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.086 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.086') or bpy.data.objects.new('Icosphere.086', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-51.91667556762695, 46.10506820678711, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.087 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.087') or bpy.data.objects.new('Icosphere.087', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-62.33937454223633, 52.79618453979492, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.093 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.093') or bpy.data.objects.new('Icosphere.093', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-67.22903442382812, 61.16008377075195, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.094 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.094') or bpy.data.objects.new('Icosphere.094', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (0.19683575630187988, 43.66023635864258, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.095 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.095') or bpy.data.objects.new('Icosphere.095', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (17.05330467224121, 56.91379928588867, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.098 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.098') or bpy.data.objects.new('Icosphere.098', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-5.078852653503418, 33.75223922729492, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.099 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.099') or bpy.data.objects.new('Icosphere.099', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-27.46836280822754, 14.836965560913086, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.100 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.100') or bpy.data.objects.new('Icosphere.100', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-18.97579002380371, 14.45094108581543, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.101 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.101') or bpy.data.objects.new('Icosphere.101', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-14.858180046081543, 21.78543472290039, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.102 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.102') or bpy.data.objects.new('Icosphere.102', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-18.203737258911133, 18.954578399658203, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.103 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.103') or bpy.data.objects.new('Icosphere.103', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-26.181604385375977, 40.82938003540039, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.104 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.104') or bpy.data.objects.new('Icosphere.104', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-24.89484977722168, 44.1749382019043, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.105 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.105') or bpy.data.objects.new('Icosphere.105', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-28.497758865356445, 69.39530944824219, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.106 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.106') or bpy.data.objects.new('Icosphere.106', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-28.11173439025879, 64.24829864501953, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.107 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.107') or bpy.data.objects.new('Icosphere.107', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-29.69072151184082, 78.59005737304688, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.108 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.108') or bpy.data.objects.new('Icosphere.108', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-24.380155563354492, 78.91728973388672, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.109 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.109') or bpy.data.objects.new('Icosphere.109', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-3.973200559616089, 57.80856704711914, 1.3121609687805176)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9828339219093323, 0.9828339219093323, 0.9828339219093323)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.110 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.110') or bpy.data.objects.new('Icosphere.110', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-46.79850387573242, -79.30259704589844, 1.041795015335083)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9603079557418823, 0.9603079557418823, 0.9603079557418823)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.111 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.111') or bpy.data.objects.new('Icosphere.111', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-68.24874114990234, -81.35620880126953, 1.041795015335083)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9603079557418823, 0.9603079557418823, 0.9603079557418823)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.113 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.113') or bpy.data.objects.new('Icosphere.113', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-70.82278442382812, -80.15556335449219, 1.041795015335083)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9603079557418823, 0.9603079557418823, 0.9603079557418823)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.114 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.114') or bpy.data.objects.new('Icosphere.114', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (65.85053253173828, 55.508480072021484, 1.2792298793792725)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.4821765124797821)
    ob.scale = (0.9799119234085083, 0.9799119234085083, 0.9799119234085083)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.115 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.115') or bpy.data.objects.new('Icosphere.115', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (66.8930435180664, 65.93357849121094, 1.2792298793792725)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.4821765124797821)
    ob.scale = (0.9799119234085083, 0.9799119234085083, 0.9799119234085083)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.116 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.116') or bpy.data.objects.new('Icosphere.116', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (68.75466918945312, 68.76324462890625, 1.2792298793792725)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.4821765124797821)
    ob.scale = (0.9799119234085083, 0.9799119234085083, 0.9799119234085083)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.117 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.117') or bpy.data.objects.new('Icosphere.117', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (61.673248291015625, 42.27345657348633, 1.2792298793792725)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.4821765124797821)
    ob.scale = (0.9799119234085083, 0.9799119234085083, 0.9799119234085083)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.118 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.118') or bpy.data.objects.new('Icosphere.118', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-5.859213829040527, 68.16752624511719, 1.2792298793792725)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.4821765124797821)
    ob.scale = (0.9799119234085083, 0.9799119234085083, 0.9799119234085083)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.119 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.119') or bpy.data.objects.new('Icosphere.119', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-69.97352600097656, -34.6685676574707, 1.2792298793792725)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.4821765124797821)
    ob.scale = (0.9799119234085083, 0.9799119234085083, 0.9799119234085083)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.120 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.120') or bpy.data.objects.new('Icosphere.120', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-66.54814147949219, -33.32819747924805, 1.2792298793792725)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.4821765124797821)
    ob.scale = (0.9799119234085083, 0.9799119234085083, 0.9799119234085083)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.121 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.121') or bpy.data.objects.new('Icosphere.121', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (47.83000946044922, 63.32729721069336, 1.2792298793792725)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.4821765124797821)
    ob.scale = (0.9799119234085083, 0.9799119234085083, 0.9799119234085083)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.122 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.122') or bpy.data.objects.new('Icosphere.122', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (36.29246520996094, 88.51766967773438, 1.2792298793792725)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.4821765124797821)
    ob.scale = (0.9799119234085083, 0.9799119234085083, 0.9799119234085083)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.018 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.018') or bpy.data.objects.new('Icosphere.018', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-23.42995262145996, -73.36441040039062, 1.0417948961257935)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9603079557418823, 0.9603079557418823, 0.9603079557418823)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.079 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.079') or bpy.data.objects.new('Icosphere.079', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-23.222105026245117, -76.72462463378906, 1.0417948961257935)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (0.9603079557418823, 0.9603079557418823, 0.9603079557418823)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.085 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.085') or bpy.data.objects.new('Icosphere.085', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (34.00651550292969, -58.026363372802734, 0.915920078754425)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.749695897102356)
    ob.scale = (0.9627104997634888, 0.9627104997634888, 0.9627104997634888)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.092 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.092') or bpy.data.objects.new('Icosphere.092', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (36.67652130126953, -57.1220703125, 0.8829298615455627)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.749695897102356)
    ob.scale = (1.0444717407226562, 1.0444717407226562, 1.0444717407226562)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.096 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.096') or bpy.data.objects.new('Icosphere.096', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (54.58587646484375, 19.259387969970703, 0.9081292152404785)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.43312886357307434)
    ob.scale = (1.0712438821792603, 1.0712438821792603, 1.0712438821792603)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.112 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.112') or bpy.data.objects.new('Icosphere.112', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (57.01116180419922, 18.34241485595703, 0.9081301689147949)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.43312886357307434)
    ob.scale = (1.0712438821792603, 1.0712438821792603, 1.0712438821792603)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.123 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.123') or bpy.data.objects.new('Icosphere.123', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (64.57492065429688, 31.68236541748047, 1.2792298793792725)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.4821765124797821)
    ob.scale = (0.9799119234085083, 0.9799119234085083, 0.9799119234085083)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.124 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.124') or bpy.data.objects.new('Icosphere.124', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (68.68561553955078, 22.010135650634766, 1.2792298793792725)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.4821765124797821)
    ob.scale = (0.9799119234085083, 0.9799119234085083, 0.9799119234085083)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.125 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.125') or bpy.data.objects.new('Icosphere.125', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (83.59246063232422, 22.42217445373535, 1.2792298793792725)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.4821765124797821)
    ob.scale = (0.9799119234085083, 0.9799119234085083, 0.9799119234085083)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.126 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.126') or bpy.data.objects.new('Icosphere.126', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (85.7571029663086, 27.91019630432129, 1.2792298793792725)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.4821765124797821)
    ob.scale = (0.9799119234085083, 0.9799119234085083, 0.9799119234085083)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.030 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.030') or bpy.data.objects.new('Icosphere.030', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (74.53860473632812, -6.832277297973633, 1.9814298152923584)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.43312886357307434)
    ob.scale = (1.078891396522522, 1.078891396522522, 1.078891396522522)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.032 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.032') or bpy.data.objects.new('Icosphere.032', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (72.19851684570312, -2.210242748260498, 0.9034558534622192)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.43312886357307434)
    ob.scale = (1.078891396522522, 1.078891396522522, 1.078891396522522)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.127 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.127') or bpy.data.objects.new('Icosphere.127', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (65.23381805419922, -6.900278091430664, 0.9034558534622192)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.43312886357307434)
    ob.scale = (1.078891396522522, 1.078891396522522, 1.078891396522522)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.128 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.128') or bpy.data.objects.new('Icosphere.128', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (74.45204162597656, -8.345196723937988, 0.8857369422912598)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.43312886357307434)
    ob.scale = (1.078891396522522, 1.078891396522522, 1.078891396522522)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.129 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.129') or bpy.data.objects.new('Icosphere.129', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (71.54617309570312, -4.0115461349487305, 3.069551706314087)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.43312886357307434)
    ob.scale = (1.078891396522522, 1.078891396522522, 1.078891396522522)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.014 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.014') or bpy.data.objects.new('Icosphere.014', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (28.547760009765625, -51.48235321044922, 1.3439249992370605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.016 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.016') or bpy.data.objects.new('Icosphere.016', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (28.547760009765625, -51.48235321044922, 1.3439249992370605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.078 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.078') or bpy.data.objects.new('Icosphere.078', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (17.843223571777344, -55.31893539428711, 1.3439249992370605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.080 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.080') or bpy.data.objects.new('Icosphere.080', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-6.37074613571167, -59.781410217285156, 1.3439249992370605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.130 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.130') or bpy.data.objects.new('Icosphere.130', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (-8.794357299804688, -60.434078216552734, 1.3439249992370605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Icosphere.090 (type=MESH) ---
    ob = bpy.data.objects.get('Icosphere.090') or bpy.data.objects.new('Icosphere.090', bpy.data.meshes.get('Icosphere.002'))
    ob.location = (52.551536560058594, -36.78352737426758, 0.8388587236404419)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0328147411346436, 1.0328147411346436, 1.0328147411346436)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 130 objects to bushes')

if __name__ == '__main__': run()