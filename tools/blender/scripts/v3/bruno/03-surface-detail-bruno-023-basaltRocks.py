"""Bruno's 023_basaltRocks.py - verbatim recreation.

13 basalt-column rock objects in collection `basaltRocks` (5 visible
TEXTURED rocks named basaltRocksPhysicalStatic.* + 8 WIRE collision
hulls, hide_render). Pure placement: each binds a pre-authored
Cylinder.* mesh datablock (foundation 005); no modifiers, no props.

Adds: 13 MESH to collection `basaltRocks` (child of scenery.002).

Source: folio-2025/scripts/blender_world_steps/steps/023_basaltRocks.py
"""
import bpy

def run():
    print('[023_basaltRocks] basaltRocks')
    coll = bpy.data.collections.get('basaltRocks')
    if coll is None: coll = bpy.data.collections.new('basaltRocks')

    # --- object: basaltRocksPhysicalStatic.002 (type=MESH) ---
    ob = bpy.data.objects.get('basaltRocksPhysicalStatic.002') or bpy.data.objects.new('basaltRocksPhysicalStatic.002', bpy.data.meshes.get('Cylinder.015'))
    ob.location = (36.96566390991211, -45.28578567504883, -0.48030030727386475)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: hull.011 (type=MESH) ---
    ob = bpy.data.objects.get('hull.011') or bpy.data.objects.new('hull.011', bpy.data.meshes.get('Cylinder.032'))
    ob.location = (-2.7088794708251953, -10.691850662231445, -0.5713266134262085)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: hull.012 (type=MESH) ---
    ob = bpy.data.objects.get('hull.012') or bpy.data.objects.new('hull.012', bpy.data.meshes.get('Cylinder.033'))
    ob.location = (-1.6067276000976562, -4.730314254760742, -0.008845925331115723)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: hull.013 (type=MESH) ---
    ob = bpy.data.objects.get('hull.013') or bpy.data.objects.new('hull.013', bpy.data.meshes.get('Cylinder.037'))
    ob.location = (16.30176544189453, 22.076059341430664, 0.04898864030838013)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: hull.014 (type=MESH) ---
    ob = bpy.data.objects.get('hull.014') or bpy.data.objects.new('hull.014', bpy.data.meshes.get('Cylinder.036'))
    ob.location = (10.180301666259766, 23.643287658691406, -0.4986915588378906)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: hull.015 (type=MESH) ---
    ob = bpy.data.objects.get('hull.015') or bpy.data.objects.new('hull.015', bpy.data.meshes.get('Cylinder.035'))
    ob.location = (-14.699234008789062, 9.067131042480469, -0.22777044773101807)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: hull.016 (type=MESH) ---
    ob = bpy.data.objects.get('hull.016') or bpy.data.objects.new('hull.016', bpy.data.meshes.get('Cylinder.034'))
    ob.location = (-16.198867797851562, 5.218223571777344, -0.2695850133895874)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: basaltRocksPhysicalStatic.001 (type=MESH) ---
    ob = bpy.data.objects.get('basaltRocksPhysicalStatic.001') or bpy.data.objects.new('basaltRocksPhysicalStatic.001', bpy.data.meshes.get('Cylinder.011'))
    ob.location = (23.818246841430664, -29.556121826171875, -0.7747273445129395)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: basaltRocksPhysicalStatic (type=MESH) ---
    ob = bpy.data.objects.get('basaltRocksPhysicalStatic') or bpy.data.objects.new('basaltRocksPhysicalStatic', bpy.data.meshes.get('Cylinder.022'))
    ob.location = (51.53984069824219, -14.209840774536133, -0.6500133275985718)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: basaltRocksPhysicalStatic.003 (type=MESH) ---
    ob = bpy.data.objects.get('basaltRocksPhysicalStatic.003') or bpy.data.objects.new('basaltRocksPhysicalStatic.003', bpy.data.meshes.get('Cylinder.014'))
    ob.location = (59.56986618041992, -8.163019180297852, 1.315825343132019)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: hull.002 (type=MESH) ---
    ob = bpy.data.objects.get('hull.002') or bpy.data.objects.new('hull.002', bpy.data.meshes.get('Cylinder.021'))
    ob.location = (59.56986618041992, -8.163019180297852, 1.315825343132019)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: basaltRocksPhysicalStatic.004 (type=MESH) ---
    ob = bpy.data.objects.get('basaltRocksPhysicalStatic.004') or bpy.data.objects.new('basaltRocksPhysicalStatic.004', bpy.data.meshes.get('Cylinder.040'))
    ob.location = (79.80693054199219, 0.33034515380859375, 0.7268602848052979)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: hull.001 (type=MESH) ---
    ob = bpy.data.objects.get('hull.001') or bpy.data.objects.new('hull.001', bpy.data.meshes.get('Cylinder.018'))
    ob.location = (79.80693054199219, 0.33034515380859375, 0.7268602848052979)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 13 objects to basaltRocks')

if __name__ == '__main__': run()
