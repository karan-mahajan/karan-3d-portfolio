"""Bruno's 114_toilet.py - verbatim recreation.

`toilet` zone — 1 MESH (rocks.001, `Cube.118`, heavily X-tilted) + 3 EMPTY
(bounding/frustum CIRCLEs, root). Centre ~(66.88, -66.74).

Adds: 4 objects to collection `toilet`.

Section 06 (buildings & structures). Collection is linked to the scene
root here (Bruno relies on 999_finalize for that; we do not run it yet),
matching the section-02..05 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/114_toilet.py

"""
import bpy

def run():
    print('[114_toilet] toilet')
    coll = bpy.data.collections.get('toilet')
    if coll is None: coll = bpy.data.collections.new('toilet')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: rocks.001 (type=MESH) ---
    ob = bpy.data.objects.get('rocks.001') or bpy.data.objects.new('rocks.001', bpy.data.meshes.get('Cube.118'))
    ob.location = (66.7220458984375, -63.312652587890625, -0.013609997928142548)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-2.1347413063049316, 0.023513179272413254, -0.2600748836994171)
    ob.scale = (0.47743168473243713, 0.47743168473243713, 0.47743162512779236)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refZoneBounding.007 (type=EMPTY) ---
    ob = bpy.data.objects.get('refZoneBounding.007') or bpy.data.objects.new('refZoneBounding.007', None)
    ob.location = (66.87518310546875, -66.73855590820312, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (6.0817060470581055, 6.0817060470581055, 6.0817060470581055)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: toilet (type=EMPTY) ---
    ob = bpy.data.objects.get('toilet') or bpy.data.objects.new('toilet', None)
    ob.location = (66.87518310546875, -66.73855590820312, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'PLAIN_AXES'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refZoneFrustum.007 (type=EMPTY) ---
    ob = bpy.data.objects.get('refZoneFrustum.007') or bpy.data.objects.new('refZoneFrustum.007', None)
    ob.location = (64.55250549316406, -63.536598205566406, 3.6803317070007324)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (12.177029609680176, 12.177029609680176, 12.177029609680176)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 4 objects to toilet')

if __name__ == '__main__': run()