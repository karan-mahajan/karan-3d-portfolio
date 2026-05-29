"""Bruno's 022_scenery.002.py - verbatim recreation.

Container-mount script. Ensures the `scenery.002` collection exists and is
linked at scene root. `scenery.002` was given its five children
(bridges, rocks, basaltRocks, slabs, road.001) back in 013-collections;
this mount makes that whole surface-detail subtree visible/rendered.

Adds: 0 objects. Mounts: scenery.002 -> scene root.

Source: folio-2025/scripts/blender_world_steps/steps/022_scenery.002.py
"""
import bpy

def run():
    print('[022_scenery.002] scenery.002')
    coll = bpy.data.collections.get('scenery.002')
    if coll is None: coll = bpy.data.collections.new('scenery.002')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    print('  added 0 objects to scenery.002')

if __name__ == '__main__': run()
