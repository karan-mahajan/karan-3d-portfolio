"""Bruno's 028_oakTrees.py - verbatim recreation.

Empty container collection `oakTrees` (12-line stub). The actual placed
instances arrive in 136_oakTrees.001.py; this just claims the name early.

Adds: 0 objects.

Source: folio-2025/scripts/blender_world_steps/steps/028_oakTrees.py
"""
import bpy

def run():
    print('[028_oakTrees] oakTrees')
    coll = bpy.data.collections.get('oakTrees')
    if coll is None: coll = bpy.data.collections.new('oakTrees')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    print('  added 0 objects to oakTrees')

if __name__ == '__main__': run()