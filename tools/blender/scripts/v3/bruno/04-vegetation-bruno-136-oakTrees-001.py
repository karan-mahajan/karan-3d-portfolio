"""Bruno's 136_oakTrees.001.py - verbatim recreation.

24 oak instances (treeBody.103..126) sharing flat mesh `Plane.017` (warm
autumn vertex color); the most numerous, broadest-spread species. Placed
at z~=0, Z-only yaw, scale 1. EXCLUDED from view layer in Bruno (Foliage.js
SDF anchors). Collection `oakTrees.001`, parented under `oakTrees`.

Adds: 24 MESH to collection `oakTrees.001`.

Source: folio-2025/scripts/blender_world_steps/steps/136_oakTrees.001.py
"""
import bpy

def run():
    print('[136_oakTrees.001] oakTrees.001')
    coll = bpy.data.collections.get('oakTrees.001')
    if coll is None: coll = bpy.data.collections.new('oakTrees.001')

    # --- object: treeBody.103 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.103') or bpy.data.objects.new('treeBody.103', bpy.data.meshes.get('Plane.017'))
    ob.location = (46.277462005615234, -29.82669448852539, 1.1641532182693481e-10)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -6.727506637573242)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.104 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.104') or bpy.data.objects.new('treeBody.104', bpy.data.meshes.get('Plane.017'))
    ob.location = (61.88151550292969, -27.291915893554688, 0.0)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -7.593414306640625)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.105 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.105') or bpy.data.objects.new('treeBody.105', bpy.data.meshes.get('Plane.017'))
    ob.location = (30.549020767211914, -51.94339370727539, 0.0)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -7.593414306640625)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.106 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.106') or bpy.data.objects.new('treeBody.106', bpy.data.meshes.get('Plane.017'))
    ob.location = (38.44166564941406, -5.6536946296691895, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -6.670223236083984)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.107 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.107') or bpy.data.objects.new('treeBody.107', bpy.data.meshes.get('Plane.017'))
    ob.location = (42.9735107421875, -6.4060845375061035, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -4.983443737030029)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.108 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.108') or bpy.data.objects.new('treeBody.108', bpy.data.meshes.get('Plane.017'))
    ob.location = (20.872060775756836, -79.699951171875, 1.1920928955078125e-07)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -7.593414306640625)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.109 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.109') or bpy.data.objects.new('treeBody.109', bpy.data.meshes.get('Plane.017'))
    ob.location = (62.18657684326172, -2.699270725250244, 0.0)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -9.79127311706543)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.110 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.110') or bpy.data.objects.new('treeBody.110', bpy.data.meshes.get('Plane.017'))
    ob.location = (2.0516369342803955, -34.98601150512695, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -6.670223236083984)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.111 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.111') or bpy.data.objects.new('treeBody.111', bpy.data.meshes.get('Plane.017'))
    ob.location = (12.719449043273926, 15.403276443481445, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -4.916852951049805)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.112 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.112') or bpy.data.objects.new('treeBody.112', bpy.data.meshes.get('Plane.017'))
    ob.location = (26.767805099487305, 32.07645797729492, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -2.2267677783966064)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.113 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.113') or bpy.data.objects.new('treeBody.113', bpy.data.meshes.get('Plane.017'))
    ob.location = (42.8125, 17.214778900146484, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -2.2267677783966064)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.114 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.114') or bpy.data.objects.new('treeBody.114', bpy.data.meshes.get('Plane.017'))
    ob.location = (-26.18809700012207, -30.742908477783203, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -6.670223236083984)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.115 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.115') or bpy.data.objects.new('treeBody.115', bpy.data.meshes.get('Plane.017'))
    ob.location = (-39.94656753540039, -51.5916862487793, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -3.9824776649475098)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.116 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.116') or bpy.data.objects.new('treeBody.116', bpy.data.meshes.get('Plane.017'))
    ob.location = (-32.42560958862305, -46.6025390625, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -3.9824776649475098)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.117 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.117') or bpy.data.objects.new('treeBody.117', bpy.data.meshes.get('Plane.017'))
    ob.location = (-19.394250869750977, 11.629018783569336, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -5.436121463775635)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.118 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.118') or bpy.data.objects.new('treeBody.118', bpy.data.meshes.get('Plane.017'))
    ob.location = (-47.02072525024414, -1.1044793128967285, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -5.436121463775635)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.119 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.119') or bpy.data.objects.new('treeBody.119', bpy.data.meshes.get('Plane.017'))
    ob.location = (-53.12685012817383, 38.28745651245117, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -5.436121463775635)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.120 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.120') or bpy.data.objects.new('treeBody.120', bpy.data.meshes.get('Plane.017'))
    ob.location = (-24.606794357299805, 38.28745651245117, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -4.171358108520508)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.121 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.121') or bpy.data.objects.new('treeBody.121', bpy.data.meshes.get('Plane.017'))
    ob.location = (-24.2385311126709, 77.24976348876953, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -7.561481475830078)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.122 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.122') or bpy.data.objects.new('treeBody.122', bpy.data.meshes.get('Plane.017'))
    ob.location = (14.11495304107666, 53.62722396850586, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -2.808187246322632)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.123 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.123') or bpy.data.objects.new('treeBody.123', bpy.data.meshes.get('Plane.017'))
    ob.location = (-70.24632263183594, -82.00679016113281, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -2.1311488151550293)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.124 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.124') or bpy.data.objects.new('treeBody.124', bpy.data.meshes.get('Plane.017'))
    ob.location = (-85.85380554199219, -85.7525405883789, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -7.643514633178711)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.125 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.125') or bpy.data.objects.new('treeBody.125', bpy.data.meshes.get('Plane.017'))
    ob.location = (58.5211181640625, 15.463268280029297, 0.0)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -12.052820205688477)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: treeBody.126 (type=MESH) ---
    ob = bpy.data.objects.get('treeBody.126') or bpy.data.objects.new('treeBody.126', bpy.data.meshes.get('Plane.017'))
    ob.location = (82.29840850830078, 33.99803161621094, -5.960464477539063e-08)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -2.2267677783966064)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 24 objects to oakTrees.001')

if __name__ == '__main__': run()