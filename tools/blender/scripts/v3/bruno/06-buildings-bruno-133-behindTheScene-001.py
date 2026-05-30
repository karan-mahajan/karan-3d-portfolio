"""Bruno's 133_behindTheScene.001.py - verbatim recreation.

EXCLUDED minimap stand-in — behindTheSceneEmissive mesh (`Plane.006`,
`mapAltar` material) in collection `behindTheScene.001`. Minimap-only.

Adds: 1 MESH to collection `behindTheScene.001`.

Section 06 (buildings & structures). Collection is linked to the scene
root here (Bruno relies on 999_finalize for that; we do not run it yet),
matching the section-02..05 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/133_behindTheScene.001.py

"""
import bpy

def run():
    print('[133_behindTheScene.001] behindTheScene.001')
    coll = bpy.data.collections.get('behindTheScene.001')
    if coll is None: coll = bpy.data.collections.new('behindTheScene.001')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: behindTheSceneEmissive (type=MESH) ---
    ob = bpy.data.objects.get('behindTheSceneEmissive') or bpy.data.objects.new('behindTheSceneEmissive', bpy.data.meshes.get('Plane.006'))
    ob.location = (75.34883117675781, 27.941041946411133, 0.4309896230697632)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.103895902633667, 3.103895902633667, 3.103895902633667)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 1 objects to behindTheScene.001')

if __name__ == '__main__': run()