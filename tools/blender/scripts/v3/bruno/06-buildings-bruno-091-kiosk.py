"""Bruno's 091_kiosk.py - verbatim recreation.

`kiosk` zone — a single refKioskInteractivePoint EMPTY at (45.18, -33.14, 1.5).
The kiosk mesh itself lives in the `landing` zone (not this script).

Adds: 1 EMPTY to collection `kiosk`.

Section 06 (buildings & structures). Collection is linked to the scene
root here (Bruno relies on 999_finalize for that; we do not run it yet),
matching the section-02..05 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/091_kiosk.py

"""
import bpy

def run():
    print('[091_kiosk] kiosk')
    coll = bpy.data.collections.get('kiosk')
    if coll is None: coll = bpy.data.collections.new('kiosk')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: refKioskInteractivePoint (type=EMPTY) ---
    ob = bpy.data.objects.get('refKioskInteractivePoint') or bpy.data.objects.new('refKioskInteractivePoint', None)
    ob.location = (45.17588806152344, -33.141292572021484, 1.4999996423721313)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-3.5391960917535064e-15, 3.096394583741507e-16, 0.0872664526104927)
    ob.scale = (0.9999999403953552, 0.9999999403953552, 0.9999999403953552)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'PLAIN_AXES'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 1 objects to kiosk')

if __name__ == '__main__': run()