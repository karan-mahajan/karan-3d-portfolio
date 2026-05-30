"""Bruno's 063_airDancers.py - verbatim recreation.

The 2 inflatable tube-guys at the race-track entrance. Both objects share the
same mesh datablock `Cylinder.059` (which carries the dedicated `airDancer`
wave-animation material); the visual interest is the runtime shader, not the
geometry.

Adds: 2 objects (2 MESH) to collection `airDancers`.

Section 13 (food / misc / fx). Collection is linked to the scene root here
(Bruno relies on 999_finalize for that; we do not run it yet), matching the
section-02..06 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/063_airDancers.py

"""
import bpy

def run():
    print('[063_airDancers] airDancers')
    coll = bpy.data.collections.get('airDancers')
    if coll is None: coll = bpy.data.collections.new('airDancers')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: refAirDancers (type=MESH) ---
    ob = bpy.data.objects.get('refAirDancers') or bpy.data.objects.new('refAirDancers', bpy.data.meshes.get('Cylinder.059'))
    ob.location = (-1.7313258647918701, -15.725229263305664, 0.9997153878211975)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, -1.7484555314695172e-07)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refAirDancers.001 (type=MESH) ---
    ob = bpy.data.objects.get('refAirDancers.001') or bpy.data.objects.new('refAirDancers.001', bpy.data.meshes.get('Cylinder.059'))
    ob.location = (-27.81248664855957, 0.500356137752533, 0.9997153878211975)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.3388579487800598)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 2 objects to airDancers')

if __name__ == '__main__': run()
