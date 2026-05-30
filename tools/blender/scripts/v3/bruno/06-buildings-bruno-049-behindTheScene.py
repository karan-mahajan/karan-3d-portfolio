"""Bruno's 049_behindTheScene.py - verbatim recreation.

`behindTheScene` zone scaffold — 5 EMPTY anchors only (refCenter, interactive
point, bounding/frustum CIRCLEs, root). No geometry; later scripts fill its
child collections. Centre ~(52.46, 11.96).

Adds: 5 EMPTY to collection `behindTheScene`.

Section 06 (buildings & structures). Collection is linked to the scene
root here (Bruno relies on 999_finalize for that; we do not run it yet),
matching the section-02..05 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/049_behindTheScene.py

"""
import bpy

def run():
    print('[049_behindTheScene] behindTheScene')
    coll = bpy.data.collections.get('behindTheScene')
    if coll is None: coll = bpy.data.collections.new('behindTheScene')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: refCenter.001 (type=EMPTY) ---
    ob = bpy.data.objects.get('refCenter.001') or bpy.data.objects.new('refCenter.001', None)
    ob.location = (52.74610137939453, 11.098175048828125, 0.0)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
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

    # --- object: refInteractivePoint.004 (type=EMPTY) ---
    ob = bpy.data.objects.get('refInteractivePoint.004') or bpy.data.objects.new('refInteractivePoint.004', None)
    ob.location = (53.36176300048828, 10.306743621826172, 1.5)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
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

    # --- object: refZoneBounding.010 (type=EMPTY) ---
    ob = bpy.data.objects.get('refZoneBounding.010') or bpy.data.objects.new('refZoneBounding.010', None)
    ob.location = (52.45521545410156, 11.959333419799805, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (8.156733512878418, 8.156733512878418, 8.156733512878418)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: behindTheScene (type=EMPTY) ---
    ob = bpy.data.objects.get('behindTheScene') or bpy.data.objects.new('behindTheScene', None)
    ob.location = (52.45521545410156, 11.959333419799805, 3.2733683586120605)
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

    # --- object: refZoneFrustum.010 (type=EMPTY) ---
    ob = bpy.data.objects.get('refZoneFrustum.010') or bpy.data.objects.new('refZoneFrustum.010', None)
    ob.location = (52.615936279296875, 11.477174758911133, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (5.904889106750488, 5.904889106750488, 5.904889106750488)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 5 objects to behindTheScene')

if __name__ == '__main__': run()