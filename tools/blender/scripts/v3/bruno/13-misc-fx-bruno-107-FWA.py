"""Bruno's 107_FWA.py - verbatim recreation.

`FWA` zone — 2 MESH (refFwaPhysicalDynamic `Plane.059` QUATERNION,
Cube.004 `Cube.008`) + 2 EMPTY (cuboid.087/.088 CUBE bounds). Centre
~(26.0, 18.0). No materials/modifiers.

Adds: 4 objects (2 MESH + 2 EMPTY) to collection `FWA`.

Section 13 (food / misc / fx). Collection is linked to the scene root here
(Bruno relies on 999_finalize for that; we do not run it yet), matching the
section-02..06 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/107_FWA.py

"""
import bpy

def run():
    print('[107_FWA] FWA')
    coll = bpy.data.collections.get('FWA')
    if coll is None: coll = bpy.data.collections.new('FWA')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: refFwaPhysicalDynamic (type=MESH) ---
    ob = bpy.data.objects.get('refFwaPhysicalDynamic') or bpy.data.objects.new('refFwaPhysicalDynamic', bpy.data.meshes.get('Plane.059'))
    ob.location = (26.021589279174805, 18.0481014251709, 2.366135597229004)
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.004 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.004') or bpy.data.objects.new('Cube.004', bpy.data.meshes.get('Cube.008'))
    ob.location = (25.425378799438477, 17.618616104125977, -0.07086633890867233)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.087 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.087') or bpy.data.objects.new('cuboid.087', None)
    ob.location = (26.021589279174805, 18.0481014251709, 2.366135597229004)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (4.218541145324707, 0.882902979850769, 0.5314481258392334)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.088 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.088') or bpy.data.objects.new('cuboid.088', None)
    ob.location = (26.021589279174805, 18.0481014251709, 2.366135597229004)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (3.5866756439208984, 0.882902979850769, 1.1447217464447021)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 4 objects to FWA')

if __name__ == '__main__': run()
