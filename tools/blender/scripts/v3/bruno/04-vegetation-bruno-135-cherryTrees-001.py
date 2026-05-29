"""Bruno's 135_cherryTrees.001.py - verbatim recreation.

20 cherry instances (treeBody.127..146) sharing flat mesh `Plane.023`
(pink blossom vertex color). Hand-placed at z~=0, Z-only yaw, scale 1.
EXCLUDED from view layer in Bruno (Foliage.js SDF anchors). Collection
`cherryTrees.001`, parented under `cherryTrees` at finalize.

Adds: 20 MESH to collection `cherryTrees.001`.

Source: folio-2025/scripts/blender_world_steps/steps/135_cherryTrees.001.py
"""
import bpy

def run():
    print('[135_cherryTrees.001] cherryTrees.001')
    coll = bpy.data.collections.get('cherryTrees.001')
    if coll is None: coll = bpy.data.collections.new('cherryTrees.001')

    # --- object: treeBody.127 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.127') or bpy.data.objects.new('treeBody.127', bpy.data.meshes.get('Plane.023'))
    ob.location = (34.124698638916016, -70.9995346069336, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -2.9881744384765625)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.128 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.128') or bpy.data.objects.new('treeBody.128', bpy.data.meshes.get('Plane.023'))
    ob.location = (49.287559509277344, -51.48859786987305, 0.0)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -5.8206353187561035)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.129 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.129') or bpy.data.objects.new('treeBody.129', bpy.data.meshes.get('Plane.023'))
    ob.location = (17.4476375579834, 5.670838832855225, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.7009841799736023)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.130 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.130') or bpy.data.objects.new('treeBody.130', bpy.data.meshes.get('Plane.023'))
    ob.location = (15.092556953430176, -43.75678253173828, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.5126112699508667)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.131 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.131') or bpy.data.objects.new('treeBody.131', bpy.data.meshes.get('Plane.023'))
    ob.location = (64.32640075683594, -54.035648345947266, -9.834766387939453e-07)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -5.658109188079834)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.132 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.132') or bpy.data.objects.new('treeBody.132', bpy.data.meshes.get('Plane.023'))
    ob.location = (81.88268280029297, -12.660670280456543, -1.4603137969970703e-06)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 1.1562687158584595)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.133 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.133') or bpy.data.objects.new('treeBody.133', bpy.data.meshes.get('Plane.023'))
    ob.location = (37.106971740722656, -39.38603973388672, 1.1920928955078125e-07)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 3.0806407928466797)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.134 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.134') or bpy.data.objects.new('treeBody.134', bpy.data.meshes.get('Plane.023'))
    ob.location = (42.87666702270508, 21.55944061279297, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 2.4083170890808105)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.135 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.135') or bpy.data.objects.new('treeBody.135', bpy.data.meshes.get('Plane.023'))
    ob.location = (-1.2317607402801514, 36.70216751098633, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 2.4083170890808105)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.136 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.136') or bpy.data.objects.new('treeBody.136', bpy.data.meshes.get('Plane.023'))
    ob.location = (-1.2317607402801514, 54.2758903503418, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.11006379872560501)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.137 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.137') or bpy.data.objects.new('treeBody.137', bpy.data.meshes.get('Plane.023'))
    ob.location = (-26.177499771118164, 50.18032455444336, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.11006379872560501)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.138 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.138') or bpy.data.objects.new('treeBody.138', bpy.data.meshes.get('Plane.023'))
    ob.location = (-58.49526596069336, 68.42423248291016, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 3.4169585704803467)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.139 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.139') or bpy.data.objects.new('treeBody.139', bpy.data.meshes.get('Plane.023'))
    ob.location = (-46.58088302612305, 3.788693904876709, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 3.146549701690674)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.140 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.140') or bpy.data.objects.new('treeBody.140', bpy.data.meshes.get('Plane.023'))
    ob.location = (-61.920658111572266, -60.40005874633789, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 1.4951838254928589)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.141 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.141') or bpy.data.objects.new('treeBody.141', bpy.data.meshes.get('Plane.023'))
    ob.location = (-63.199256896972656, -83.22747039794922, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 3.3340258598327637)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.142 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.142') or bpy.data.objects.new('treeBody.142', bpy.data.meshes.get('Plane.023'))
    ob.location = (48.414031982421875, 5.913177490234375, -1.4603137969970703e-06)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.07532072067260742)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.143 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.143') or bpy.data.objects.new('treeBody.143', bpy.data.meshes.get('Plane.023'))
    ob.location = (84.6110610961914, 30.4686279296875, -1.4603137969970703e-06)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 3.133681535720825)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.144 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.144') or bpy.data.objects.new('treeBody.144', bpy.data.meshes.get('Plane.023'))
    ob.location = (60.51176834106445, -14.577919960021973, -1.4603137969970703e-06)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 3.2932333946228027)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.145 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.145') or bpy.data.objects.new('treeBody.145', bpy.data.meshes.get('Plane.023'))
    ob.location = (2.8521289825439453, -11.102949142456055, 1.7881393432617188e-07)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.1432551145553589)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.146 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.146') or bpy.data.objects.new('treeBody.146', bpy.data.meshes.get('Plane.023'))
    ob.location = (-21.871944427490234, -35.360740661621094, 1.7881393432617188e-07)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 3.045682430267334)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 20 objects to cherryTrees.001')

if __name__ == '__main__': run()