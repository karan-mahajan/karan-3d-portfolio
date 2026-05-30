"""Bruno's 129_easter.py - verbatim recreation.

`easter` collection stub — creates the named collection slot, adds 0 objects.
Content is authored by other easter-related scripts.

Adds: 0 objects to collection `easter`.

Section 13 (food / misc / fx). Collection is linked to the scene root here
(Bruno relies on 999_finalize for that; we do not run it yet), matching the
section-02..06 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/129_easter.py

"""
import bpy

def run():
    print('[129_easter] easter')
    coll = bpy.data.collections.get('easter')
    if coll is None: coll = bpy.data.collections.new('easter')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    print('  added 0 objects to easter')

if __name__ == '__main__': run()
