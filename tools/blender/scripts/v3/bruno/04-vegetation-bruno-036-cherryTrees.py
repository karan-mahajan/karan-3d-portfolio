"""Bruno's 036_cherryTrees.py - verbatim recreation.

Empty container collection `cherryTrees` (12-line stub). Instances arrive
in 135_cherryTrees.001.py.

Adds: 0 objects.

Source: folio-2025/scripts/blender_world_steps/steps/036_cherryTrees.py
"""
import bpy

def run():
    print('[036_cherryTrees] cherryTrees')
    coll = bpy.data.collections.get('cherryTrees')
    if coll is None: coll = bpy.data.collections.new('cherryTrees')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    print('  added 0 objects to cherryTrees')

if __name__ == '__main__': run()