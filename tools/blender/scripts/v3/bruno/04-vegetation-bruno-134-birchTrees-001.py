"""Bruno's 134_birchTrees.001.py - verbatim recreation.

26 birch instances (treeBody.044..101) all sharing mesh `Icosphere.004`
(loaded in foundation 005). Hand-placed at z~=0, Z-only yaw, scale 1.
Bruno EXCLUDES this collection from the view layer in 999_finalize - the
solid icospheres are anchors his runtime Foliage.js renders an SDF canopy
onto. Collection `birchTrees.001`, parented under `birchTrees` at finalize.

Adds: 26 MESH to collection `birchTrees.001`.

Source: folio-2025/scripts/blender_world_steps/steps/134_birchTrees.001.py
"""
import bpy

def run():
    print('[134_birchTrees.001] birchTrees.001')
    coll = bpy.data.collections.get('birchTrees.001')
    if coll is None: coll = bpy.data.collections.new('birchTrees.001')

    # --- object: treeBody.044 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.044') or bpy.data.objects.new('treeBody.044', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (28.73230743408203, -48.62636184692383, 0.0)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.9193112254142761)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.077 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.077') or bpy.data.objects.new('treeBody.077', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (43.18186950683594, -27.994876861572266, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -4.867138862609863)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.078 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.078') or bpy.data.objects.new('treeBody.078', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (28.382057189941406, -26.000072479248047, 0.0)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -4.369649410247803)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.079 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.079') or bpy.data.objects.new('treeBody.079', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (44.00693130493164, -56.34975051879883, 0.0)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -3.182295799255371)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.080 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.080') or bpy.data.objects.new('treeBody.080', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (61.10455322265625, -20.23448944091797, 0.0)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -3.182295799255371)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.081 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.081') or bpy.data.objects.new('treeBody.081', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (21.95564079284668, -31.938716888427734, -7.450580596923828e-09)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -3.182295799255371)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.082 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.082') or bpy.data.objects.new('treeBody.082', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (60.58082580566406, -66.93000030517578, 0.0)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -3.182295799255371)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.083 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.083') or bpy.data.objects.new('treeBody.083', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (79.32377624511719, -46.58986282348633, 1.1920928955078125e-07)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -3.182295799255371)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.084 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.084') or bpy.data.objects.new('treeBody.084', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (37.975181579589844, -31.134462356567383, 0.0)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -4.059886932373047)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.085 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.085') or bpy.data.objects.new('treeBody.085', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (9.143519401550293, -8.46367073059082, -7.450580596923828e-09)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.6692831516265869)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.086 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.086') or bpy.data.objects.new('treeBody.086', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (12.375361442565918, -9.686868667602539, -7.450580596923828e-09)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.5253582000732422)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.087 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.087') or bpy.data.objects.new('treeBody.087', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (81.03364562988281, -33.51736068725586, 0.0)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -3.182295799255371)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.088 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.088') or bpy.data.objects.new('treeBody.088', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (13.64179515838623, 9.530828475952148, -4.6938657760620117e-07)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -2.13874888420105)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.089 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.089') or bpy.data.objects.new('treeBody.089', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (24.3629093170166, 27.978534698486328, -4.6938657760620117e-07)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -3.5753960609436035)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.090 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.090') or bpy.data.objects.new('treeBody.090', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (38.041568756103516, 36.25967025756836, -4.6938657760620117e-07)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.671168565750122)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.091 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.091') or bpy.data.objects.new('treeBody.091', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (4.039505958557129, 48.226009368896484, -4.6938657760620117e-07)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -3.268991708755493)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.092 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.092') or bpy.data.objects.new('treeBody.092', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (64.77538299560547, 45.64882278442383, -4.6938657760620117e-07)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -3.268991708755493)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.093 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.093') or bpy.data.objects.new('treeBody.093', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (75.45134735107422, 61.33182907104492, -4.6938657760620117e-07)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -4.472838401794434)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.094 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.094') or bpy.data.objects.new('treeBody.094', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (-48.756099700927734, 42.0454216003418, -4.6938657760620117e-07)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -4.472838401794434)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.095 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.095') or bpy.data.objects.new('treeBody.095', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (-57.09617233276367, 49.86423873901367, -4.6938657760620117e-07)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -6.086256980895996)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.096 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.096') or bpy.data.objects.new('treeBody.096', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (-53.149532318115234, -2.484591007232666, -4.6938657760620117e-07)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -6.086256980895996)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.097 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.097') or bpy.data.objects.new('treeBody.097', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (-76.82937622070312, -0.1761804223060608, -4.6938657760620117e-07)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -7.629447937011719)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.098 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.098') or bpy.data.objects.new('treeBody.098', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (-43.6924934387207, -48.20604705810547, -4.6938657760620117e-07)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -9.1395902633667)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.099 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.099') or bpy.data.objects.new('treeBody.099', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (-26.572153091430664, -40.01570510864258, -5.885958671569824e-07)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -6.570432186126709)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.100 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.100') or bpy.data.objects.new('treeBody.100', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (16.143630981445312, -55.67224884033203, 0.0)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.9193112254142761)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.101 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.101') or bpy.data.objects.new('treeBody.101', bpy.data.meshes.get('Icosphere.004'))
    ob.location = (66.72530364990234, 27.124570846557617, -4.6938657760620117e-07)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.338642954826355)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 26 objects to birchTrees.001')

if __name__ == '__main__': run()