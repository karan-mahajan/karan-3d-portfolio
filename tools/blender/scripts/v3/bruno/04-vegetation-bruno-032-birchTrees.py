"""Bruno's 032_birchTrees.py - verbatim recreation.

Empty container collection `birchTrees` (12-line stub). Instances arrive
in 134_birchTrees.001.py.

Adds: 0 objects.

Source: folio-2025/scripts/blender_world_steps/steps/032_birchTrees.py
"""
import bpy

def run():
    print('[032_birchTrees] birchTrees')
    coll = bpy.data.collections.get('birchTrees')
    if coll is None: coll = bpy.data.collections.new('birchTrees')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    print('  added 0 objects to birchTrees')

if __name__ == '__main__': run()