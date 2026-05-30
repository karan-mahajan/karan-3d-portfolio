"""Bruno's 130_egg.py - verbatim recreation.

`egg` collection — the hero floating egg prop at origin: 2 MESH (the egg
itself `Sphere.005` at z≈2.98, plus its rotated light `beams` plane).

Adds: 2 objects (2 MESH) to collection `egg`.

Section 13 (food / misc / fx). Collection is linked to the scene root here
(Bruno relies on 999_finalize for that; we do not run it yet), matching the
section-02..06 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/130_egg.py

"""
import bpy

def run():
    print('[130_egg] egg')
    coll = bpy.data.collections.get('egg')
    if coll is None: coll = bpy.data.collections.new('egg')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: egg (type=MESH) ---
    ob = bpy.data.objects.get('egg') or bpy.data.objects.new('egg', bpy.data.meshes.get('Sphere.005'))
    ob.location = (0.0, 0.0, 2.980494737625122)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 1.2402859926223755)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: beams (type=MESH) ---
    ob = bpy.data.objects.get('beams') or bpy.data.objects.new('beams', bpy.data.meshes.get('Plane.032'))
    ob.location = (-0.016592523083090782, 0.020028846338391304, 2.974958896636963)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.415816068649292, -1.1111319065093994, 2.1076738834381104)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 2 objects to egg')

if __name__ == '__main__': run()
