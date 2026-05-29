"""Bruno's 025_road.001.py - verbatim recreation.

The road network baked from a bezier spline: 12 stacked Cube.* road
segments (shared origin), 1 refRoad mesh, and 1 hidden curveRoad CURVE
(authoring source, hidden in viewport/render/select).

Adds: 14 objects (13 MESH + 1 CURVE) to collection `road.001`.

Source: folio-2025/scripts/blender_world_steps/steps/025_road.001.py
"""
import bpy

def run():
    print('[025_road.001] road.001')
    coll = bpy.data.collections.get('road.001')
    if coll is None: coll = bpy.data.collections.new('road.001')

    # --- object: Cube.049 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.049') or bpy.data.objects.new('Cube.049', bpy.data.meshes.get('Cube.087'))
    ob.location = (-1.7313258647918701, -15.725229263305664, 0.9997153878211975)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.059 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.059') or bpy.data.objects.new('Cube.059', bpy.data.meshes.get('Cube.133'))
    ob.location = (-1.7313258647918701, -15.725229263305664, 0.9997153878211975)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.064 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.064') or bpy.data.objects.new('Cube.064', bpy.data.meshes.get('Cube.145'))
    ob.location = (-1.7313258647918701, -15.725229263305664, 0.9997153878211975)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.066 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.066') or bpy.data.objects.new('Cube.066', bpy.data.meshes.get('Cube.146'))
    ob.location = (-1.7313258647918701, -15.725229263305664, 0.9997153878211975)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.067 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.067') or bpy.data.objects.new('Cube.067', bpy.data.meshes.get('Cube.147'))
    ob.location = (-1.7313258647918701, -15.725229263305664, 0.9997153878211975)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.071 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.071') or bpy.data.objects.new('Cube.071', bpy.data.meshes.get('Cube.148'))
    ob.location = (-1.7313258647918701, -15.725229263305664, 0.9997153878211975)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.072 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.072') or bpy.data.objects.new('Cube.072', bpy.data.meshes.get('Cube.149'))
    ob.location = (-1.7313258647918701, -15.725229263305664, 0.9997153878211975)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.074 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.074') or bpy.data.objects.new('Cube.074', bpy.data.meshes.get('Cube.150'))
    ob.location = (-1.7313258647918701, -15.725229263305664, 0.9997153878211975)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.075 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.075') or bpy.data.objects.new('Cube.075', bpy.data.meshes.get('Cube.187'))
    ob.location = (-1.7313258647918701, -15.725229263305664, 0.9997153878211975)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.076 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.076') or bpy.data.objects.new('Cube.076', bpy.data.meshes.get('Cube.222'))
    ob.location = (-1.7313258647918701, -15.725229263305664, 0.9997153878211975)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.078 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.078') or bpy.data.objects.new('Cube.078', bpy.data.meshes.get('Cube.227'))
    ob.location = (-1.7313258647918701, -15.725229263305664, 0.9997153878211975)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.079 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.079') or bpy.data.objects.new('Cube.079', bpy.data.meshes.get('Cube.230'))
    ob.location = (-1.7313258647918701, -15.725229263305664, 0.9997153878211975)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refRoad (type=MESH) ---
    ob = bpy.data.objects.get('refRoad') or bpy.data.objects.new('refRoad', bpy.data.meshes.get('BézierCircle'))
    ob.location = (-45.32717514038086, -35.99003982543945, 0.019999999552965164)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: curveRoad (type=CURVE) ---
    ob = bpy.data.objects.get('curveRoad') or bpy.data.objects.new('curveRoad', bpy.data.curves.get('BézierCircle.001'))
    ob.location = (-66.79804229736328, 0.5890306830406189, 0.009999999776482582)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.hide_viewport = True
    except Exception: pass
    try: ob.hide_render = True
    except Exception: pass
    try: ob.hide_select = True
    except Exception: pass
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 14 objects to road.001')

if __name__ == '__main__': run()
