"""Bruno's 108_timeMachine.py - verbatim recreation.

`timeMachine` prop+zone — 2 MESH (Cube.008/009, same `Cube.014` datablock with
opposing ~5 deg Y tilts) + 7 EMPTY (root, physicalFixed, interactive point,
bounding/frustum CIRCLEs, 2 CUBE colliders). Prop ~(-54.53, 67.40), zone
anchors ~(69.88, -9.72) — Bruno authors them in two separate spaces.

Adds: 9 objects to collection `timeMachine`.

Section 06 (buildings & structures). Collection is linked to the scene
root here (Bruno relies on 999_finalize for that; we do not run it yet),
matching the section-02..05 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/108_timeMachine.py

"""
import bpy

def run():
    print('[108_timeMachine] timeMachine')
    coll = bpy.data.collections.get('timeMachine')
    if coll is None: coll = bpy.data.collections.new('timeMachine')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: refInteractivePoint.006 (type=EMPTY) ---
    ob = bpy.data.objects.get('refInteractivePoint.006') or bpy.data.objects.new('refInteractivePoint.006', None)
    ob.location = (70.5761489868164, -10.320069313049316, 1.7493621110916138)
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

    # --- object: refZoneBounding.012 (type=EMPTY) ---
    ob = bpy.data.objects.get('refZoneBounding.012') or bpy.data.objects.new('refZoneBounding.012', None)
    ob.location = (69.879638671875, -9.718117713928223, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (7.271302700042725, 7.271302700042725, 7.271302700042725)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: timeMachine (type=EMPTY) ---
    ob = bpy.data.objects.get('timeMachine') or bpy.data.objects.new('timeMachine', None)
    ob.location = (-54.53236389160156, 67.39844512939453, 3.2733685970306396)
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

    # --- object: refZoneFrustum.012 (type=EMPTY) ---
    ob = bpy.data.objects.get('refZoneFrustum.012') or bpy.data.objects.new('refZoneFrustum.012', None)
    ob.location = (70.25017547607422, -9.810166358947754, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (4.7563700675964355, 4.7563700675964355, 4.7563700675964355)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: physicalFixed.010 (type=EMPTY) ---
    ob = bpy.data.objects.get('physicalFixed.010') or bpy.data.objects.new('physicalFixed.010', None)
    ob.location = (-54.53236389160156, 67.39844512939453, 0.6883361339569092)
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

    # --- object: cuboid.220 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.220') or bpy.data.objects.new('cuboid.220', None)
    ob.location = (-54.29082489013672, 67.60501861572266, -0.2720968425273895)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.884123682975769, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.221 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.221') or bpy.data.objects.new('cuboid.221', None)
    ob.location = (-56.500545501708984, 68.8007583618164, 0.1471189260482788)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.023767540231347084, -0.007056980859488249, -0.6300500631332397)
    ob.scale = (1.3405181169509888, 1.1497234106063843, 0.479152113199234)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.008 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.008') or bpy.data.objects.new('Cube.008', bpy.data.meshes.get('Cube.014'))
    ob.location = (-56.44211196899414, 68.75231170654297, 0.13122108578681946)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.038240283727645874, -0.007802931126207113, 0.4942087233066559)
    ob.scale = (0.8208666443824768, 0.8208665251731873, 0.820866584777832)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.009 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.009') or bpy.data.objects.new('Cube.009', bpy.data.meshes.get('Cube.014'))
    ob.location = (-56.418479919433594, 68.75851440429688, 0.34933730959892273)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.03019758127629757, -0.02472788468003273, 0.9789620637893677)
    ob.scale = (0.8208665251731873, 0.8208665251731873, 0.820866584777832)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 9 objects to timeMachine')

if __name__ == '__main__': run()