"""Bruno's 105_statue.py - verbatim recreation.

`statue` collection stub — creates the named collection slot, adds 0 objects.
Content (statue mesh + FWA badges) is authored by later scripts.

Adds: 0 objects to collection `statue`.

Section 06 (buildings & structures). Collection is linked to the scene
root here (Bruno relies on 999_finalize for that; we do not run it yet),
matching the section-02..05 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/105_statue.py

"""
import bpy

def run():
    print('[105_statue] statue')
    coll = bpy.data.collections.get('statue')
    if coll is None: coll = bpy.data.collections.new('statue')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    print('  added 0 objects to statue')

if __name__ == '__main__': run()