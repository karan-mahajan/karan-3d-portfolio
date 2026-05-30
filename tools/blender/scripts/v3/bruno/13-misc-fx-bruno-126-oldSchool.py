"""Bruno's 126_oldSchool.py - verbatim recreation.

`oldSchool` car — 5 MESH (wheel `Cylinder.081`, bodyBlack.002 `Cube.231`,
bodyPainted `Cube.240`, headlights.002 `Cube.228`, backLights.002 `Cube.215`,
most QUATERNION-rotated) + 3 EMPTY (chassis, wheelContainer, wheelCylinder
PLAIN_AXES rig). Centred near origin.

Adds: 8 objects (5 MESH + 3 EMPTY) to collection `oldSchool`.

Section 13 (food / misc / fx). Collection is linked to the scene root here
(Bruno relies on 999_finalize for that; we do not run it yet), matching the
section-02..06 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/126_oldSchool.py

"""
import bpy

def run():
    print('[126_oldSchool] oldSchool')
    coll = bpy.data.collections.get('oldSchool')
    if coll is None: coll = bpy.data.collections.new('oldSchool')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: chassis (type=EMPTY) ---
    ob = bpy.data.objects.get('chassis') or bpy.data.objects.new('chassis', None)
    ob.location = (2.9802322387695312e-08, 0.0, 0.9071758985519409)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
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

    # --- object: wheelContainer (type=EMPTY) ---
    ob = bpy.data.objects.get('wheelContainer') or bpy.data.objects.new('wheelContainer', None)
    ob.location = (0.8717746138572693, 0.6986314058303833, -0.41719210147857666)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
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

    # --- object: wheelCylinder (type=EMPTY) ---
    ob = bpy.data.objects.get('wheelCylinder') or bpy.data.objects.new('wheelCylinder', None)
    ob.location = (0.8717746138572693, 0.6986314058303833, -0.41719210147857666)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
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

    # --- object: wheel (type=MESH) ---
    ob = bpy.data.objects.get('wheel') or bpy.data.objects.new('wheel', bpy.data.meshes.get('Cylinder.081'))
    ob.location = (0.8717746138572693, 0.6986314058303833, -0.41719210147857666)
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = (0.0017776790773496032, 0.7111704349517822, 0.00246623158454895, -0.7030131220817566)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: bodyBlack.002 (type=MESH) ---
    ob = bpy.data.objects.get('bodyBlack.002') or bpy.data.objects.new('bodyBlack.002', bpy.data.meshes.get('Cube.231'))
    ob.location = (-0.16746635735034943, -2.266811236495414e-07, 1.171343207359314)
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = (0.5000000596046448, -0.4999999403953552, -0.5, 0.4999999403953552)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: bodyPainted (type=MESH) ---
    ob = bpy.data.objects.get('bodyPainted') or bpy.data.objects.new('bodyPainted', bpy.data.meshes.get('Cube.240'))
    ob.location = (-0.16746634244918823, -2.266811236495414e-07, 1.171343207359314)
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = (0.5000000596046448, -0.4999999403953552, -0.5, 0.4999999403953552)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: headlights.002 (type=MESH) ---
    ob = bpy.data.objects.get('headlights.002') or bpy.data.objects.new('headlights.002', bpy.data.meshes.get('Cube.228'))
    ob.location = (-0.16746631264686584, -4.787917191606539e-07, 1.171343445777893)
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = (0.5000000596046448, -0.4999999403953552, -0.4999999403953552, 0.4999999403953552)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: backLights.002 (type=MESH) ---
    ob = bpy.data.objects.get('backLights.002') or bpy.data.objects.new('backLights.002', bpy.data.meshes.get('Cube.215'))
    ob.location = (-0.16746635735034943, -2.266811236495414e-07, 1.171343207359314)
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = (0.5000000596046448, -0.4999999403953552, -0.5, 0.4999999403953552)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 8 objects to oldSchool')

if __name__ == '__main__': run()
