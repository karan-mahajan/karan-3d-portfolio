"""Bruno's 121_fwa.py - verbatim recreation.

`fwa` zone — a cluster of 6 explosive-crate MESHes (explosiveCrates.005..008,
.010, .011), all sharing mesh `Cube.053`, scattered/stacked around ~(20-30, 16-23).

Adds: 6 objects (6 MESH) to collection `fwa`.

Section 13 (food / misc / fx). Collection is linked to the scene root here
(Bruno relies on 999_finalize for that; we do not run it yet), matching the
section-02..06 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/121_fwa.py

"""
import bpy

def run():
    print('[121_fwa] fwa')
    coll = bpy.data.collections.get('fwa')
    if coll is None: coll = bpy.data.collections.new('fwa')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: explosiveCrates.005 (type=MESH) ---
    ob = bpy.data.objects.get('explosiveCrates.005') or bpy.data.objects.new('explosiveCrates.005', bpy.data.meshes.get('Cube.053'))
    ob.location = (29.749921798706055, 21.41513442993164, 0.5120429992675781)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (3.141592264175415, 0.042091693729162216, 3.2269389629364014)
    ob.scale = (0.9999999403953552, 0.9999999403953552, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: explosiveCrates.006 (type=MESH) ---
    ob = bpy.data.objects.get('explosiveCrates.006') or bpy.data.objects.new('explosiveCrates.006', bpy.data.meshes.get('Cube.053'))
    ob.location = (25.86532974243164, 22.838899612426758, 0.5120429992675781)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (3.141592264175415, 0.042091697454452515, -2.4837193489074707)
    ob.scale = (0.9999999403953552, 0.9999999403953552, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: explosiveCrates.007 (type=MESH) ---
    ob = bpy.data.objects.get('explosiveCrates.007') or bpy.data.objects.new('explosiveCrates.007', bpy.data.meshes.get('Cube.053'))
    ob.location = (23.474811553955078, 17.776626586914062, 0.5120429992675781)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (3.141592264175415, 0.042091697454452515, -2.7594709396362305)
    ob.scale = (0.9999999403953552, 0.9999999403953552, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: explosiveCrates.008 (type=MESH) ---
    ob = bpy.data.objects.get('explosiveCrates.008') or bpy.data.objects.new('explosiveCrates.008', bpy.data.meshes.get('Cube.053'))
    ob.location = (21.541303634643555, 21.73152732849121, 0.5120429992675781)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (3.141592264175415, 0.042091697454452515, -1.1074367761611938)
    ob.scale = (0.9999999403953552, 0.9999999403953552, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: explosiveCrates.010 (type=MESH) ---
    ob = bpy.data.objects.get('explosiveCrates.010') or bpy.data.objects.new('explosiveCrates.010', bpy.data.meshes.get('Cube.053'))
    ob.location = (21.562274932861328, 21.689556121826172, 1.626059889793396)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (3.178508758544922, 0.02022651582956314, -0.03764636069536209)
    ob.scale = (0.9999999403953552, 0.9999999403953552, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: explosiveCrates.011 (type=MESH) ---
    ob = bpy.data.objects.get('explosiveCrates.011') or bpy.data.objects.new('explosiveCrates.011', bpy.data.meshes.get('Cube.053'))
    ob.location = (20.584247589111328, 16.072805404663086, 0.5120429992675781)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-0.015911102294921875, 0.03897011652588844, -3.147216558456421)
    ob.scale = (0.9999999403953552, 0.9999999403953552, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 6 objects to fwa')

if __name__ == '__main__': run()
