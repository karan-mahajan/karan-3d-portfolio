"""00_init: wipe the current scene clean so subsequent steps start fresh."""
import bpy

def run():
    print('[01_init] wiping scene')
    # Remove all object/data datablocks; leave scene + view layer skeleton intact
    for coll in (bpy.data.objects, bpy.data.meshes, bpy.data.materials,
                 bpy.data.curves, bpy.data.armatures, bpy.data.lights,
                 bpy.data.cameras, bpy.data.images, bpy.data.node_groups,
                 bpy.data.collections, bpy.data.worlds,
                 bpy.data.metaballs if hasattr(bpy.data, 'metaballs') else [],
                 bpy.data.linestyles if hasattr(bpy.data, 'linestyles') else [],
                 bpy.data.actions if hasattr(bpy.data, 'actions') else [],
                 bpy.data.texts if hasattr(bpy.data, 'texts') else []):
        for item in list(coll):
            try: coll.remove(item)
            except Exception: pass
    print('[01_init] done')

if __name__ == '__main__':
    run()