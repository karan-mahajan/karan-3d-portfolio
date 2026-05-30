"""Bruno's 115_cabin.py - verbatim recreation.

`cabin` — 2 MESH (refMoon `Cube.153`, wood.002 `Cube.135`) + 1 hidden META
(metaMoss `Mball.004`, the only-other metaball in the world) + 2 EMPTY
(refCabinPhysicalDynamic with mass=5.0, cuboid.079 CUBE collider).

Adds: 5 objects to collection `cabin`.

Section 06 (buildings & structures). Collection is linked to the scene
root here (Bruno relies on 999_finalize for that; we do not run it yet),
matching the section-02..05 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/115_cabin.py

"""
import bpy

def run():
    print('[115_cabin] cabin')
    coll = bpy.data.collections.get('cabin')
    if coll is None: coll = bpy.data.collections.new('cabin')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: metaMoss (type=META) ---
    ob = bpy.data.objects.get('metaMoss') or bpy.data.objects.new('metaMoss', bpy.data.metaballs.get('Mball.004'))
    ob.location = (68.94917297363281, -70.65040588378906, 3.2854506969451904)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.2617993950843811)
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

    # --- object: refCabinPhysicalDynamic (type=EMPTY) ---
    ob = bpy.data.objects.get('refCabinPhysicalDynamic') or bpy.data.objects.new('refCabinPhysicalDynamic', None)
    ob.location = (65.53412628173828, -63.54985427856445, 1.8935344219207764)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.4363324046134949)
    ob.scale = (0.9999999403953552, 0.9999999403953552, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'PLAIN_AXES'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    try: ob['mass'] = 5.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.079 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.079') or bpy.data.objects.new('cuboid.079', None)
    ob.location = (-14.446552276611328, -18.186521530151367, 1.7471919059753418)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.2617993950843811)
    ob.scale = (1.9396051168441772, 1.9396051168441772, 3.505701780319214)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refMoon (type=MESH) ---
    ob = bpy.data.objects.get('refMoon') or bpy.data.objects.new('refMoon', bpy.data.meshes.get('Cube.153'))
    ob.location = (-17.331653594970703, -17.606264114379883, -0.11670877039432526)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: wood.002 (type=MESH) ---
    ob = bpy.data.objects.get('wood.002') or bpy.data.objects.new('wood.002', bpy.data.meshes.get('Cube.135'))
    ob.location = (-17.331653594970703, -17.551206588745117, -0.11670877039432526)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 5 objects to cabin')

if __name__ == '__main__': run()