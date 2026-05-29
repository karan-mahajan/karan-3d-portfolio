"""Bruno's 024_bridges.py - verbatim recreation.

2 visible bridge meshes (bridgePhysicalFixed*, meshes Cube.156/Cube.211)
+ 6 EMPTY cuboid collider proxies (deck + 2 rails per bridge). The empties
use empty_display_type='CUBE'; their scale encodes collider half-extents.

Adds: 8 objects (2 MESH + 6 EMPTY) to collection `bridges`.

Source: folio-2025/scripts/blender_world_steps/steps/024_bridges.py
"""
import bpy

def run():
    print('[024_bridges] bridges')
    coll = bpy.data.collections.get('bridges')
    if coll is None: coll = bpy.data.collections.new('bridges')

    # --- object: bridgePhysicalFixed.001 (type=MESH) ---
    ob = bpy.data.objects.get('bridgePhysicalFixed.001') or bpy.data.objects.new('bridgePhysicalFixed.001', bpy.data.meshes.get('Cube.156'))
    ob.location = (23.404743194580078, -39.83363723754883, -0.11670888960361481)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 4.395925045013428)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.022 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.022') or bpy.data.objects.new('cuboid.022', None)
    ob.location = (-12.738495826721191, -3.5405893325805664, -1.0033740997314453)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (6.706568013068424e-15, -1.4403380221915223e-14, -1.8923394680023193)
    ob.scale = (3.672971248626709, 10.302400588989258, 2.1849985122680664)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.024 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.024') or bpy.data.objects.new('cuboid.024', None)
    ob.location = (-13.097864151000977, -5.61314582824707, 0.055306583642959595)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (6.706568013068424e-15, -1.4403380221915223e-14, -1.8923394680023193)
    ob.scale = (0.2853115499019623, 8.598325729370117, 2.1849985122680664)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.023 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.023') or bpy.data.objects.new('cuboid.023', None)
    ob.location = (-11.77757453918457, -1.6495351791381836, 0.055306583642959595)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (6.706568013068424e-15, -1.4403380221915223e-14, -1.8923394680023193)
    ob.scale = (0.2853115499019623, 8.598325729370117, 2.1849985122680664)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: bridgePhysicalFixed (type=MESH) ---
    ob = bpy.data.objects.get('bridgePhysicalFixed') or bpy.data.objects.new('bridgePhysicalFixed', bpy.data.meshes.get('Cube.211'))
    ob.location = (47.08460998535156, -22.280319213867188, -0.11670882999897003)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 7.362985134124756)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid') or bpy.data.objects.new('cuboid', None)
    ob.location = (5.2709550857543945, 16.458595275878906, -1.0033740997314453)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (6.706568860101372e-15, -1.4403380221915223e-14, 1.0747207403182983)
    ob.scale = (3.672970771789551, 10.302399635314941, 2.1849985122680664)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.021 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.021') or bpy.data.objects.new('cuboid.021', None)
    ob.location = (5.984759330749512, 18.4372615814209, 0.05530664324760437)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (6.706570554167266e-15, -1.4403380221915223e-14, 1.0747207403182983)
    ob.scale = (0.2853115200996399, 8.5983247756958, 2.1849985122680664)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.020 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.020') or bpy.data.objects.new('cuboid.020', None)
    ob.location = (3.99625563621521, 14.763132095336914, 0.05530664324760437)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (6.706570554167266e-15, -1.4403380221915223e-14, 1.0747207403182983)
    ob.scale = (0.2853115200996399, 8.5983247756958, 2.1849985122680664)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 8 objects to bridges')

if __name__ == '__main__': run()
