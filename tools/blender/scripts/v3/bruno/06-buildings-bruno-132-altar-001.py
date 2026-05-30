"""Bruno's 132_altar.001.py - verbatim recreation.

EXCLUDED minimap stand-in — altarEmissive mesh (`Plane.004`, `mapPortal`
material) in collection `altar.001`. Only the minimap camera renders it.
Kept for faithfulness; foundation nests `altar.001` under `map`.

Adds: 1 MESH to collection `altar.001`.

Section 06 (buildings & structures). Collection is linked to the scene
root here (Bruno relies on 999_finalize for that; we do not run it yet),
matching the section-02..05 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/132_altar.001.py

"""
import bpy

def run():
    print('[132_altar.001] altar.001')
    coll = bpy.data.collections.get('altar.001')
    if coll is None: coll = bpy.data.collections.new('altar.001')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: altarEmissive (type=MESH) ---
    ob = bpy.data.objects.get('altarEmissive') or bpy.data.objects.new('altarEmissive', bpy.data.meshes.get('Plane.004'))
    ob.location = (52.74610137939453, 11.098175048828125, 0.03775975853204727)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.844484806060791, 3.844484806060791, 3.844484806060791)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 1 objects to altar.001')

if __name__ == '__main__': run()