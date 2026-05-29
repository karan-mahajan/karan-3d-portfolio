"""Bruno's 119_benches.py - verbatim recreation.

7 world-scattered benches (mesh Cube.158) each with a 2-cuboid compound
collider (benchPhysicalDynamic + cuboid.NNN empties), all created in-script.

Adds: 21 objects (7 MESH, 14 EMPTY) to collection `benches`.

Source: folio-2025/scripts/blender_world_steps/steps/119_benches.py
"""
import bpy

def run():
    print('[119_benches] benches')
    coll = bpy.data.collections.get('benches')
    if coll is None: coll = bpy.data.collections.new('benches')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: benchPhysicalDynamic (type=MESH) ---
    ob = bpy.data.objects.get('benchPhysicalDynamic') or bpy.data.objects.new('benchPhysicalDynamic', bpy.data.meshes.get('Cube.158'))
    ob.location = (19.800460815429688, -33.053138732910156, 0.7560859322547913)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.18319064378738403)
    ob.scale = (1.0919357538223267, 1.0919357538223267, 1.0919357538223267)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.014 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.014') or bpy.data.objects.new('cuboid.014', None)
    ob.location = (20.127033233642578, -33.66490173339844, 1.0490659475326538)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (2.3001911640167236, 0.328475683927536, 0.8132531046867371)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.015 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.015') or bpy.data.objects.new('cuboid.015', None)
    ob.location = (20.127033233642578, -34.13309860229492, 0.3106675446033478)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (2.3001911640167236, 1.294737458229065, 0.6471762657165527)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: benchPhysicalDynamic.001 (type=MESH) ---
    ob = bpy.data.objects.get('benchPhysicalDynamic.001') or bpy.data.objects.new('benchPhysicalDynamic.001', bpy.data.meshes.get('Cube.158'))
    ob.location = (37.971248626708984, -35.9785270690918, 0.756085991859436)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.7420735359191895)
    ob.scale = (1.0919357538223267, 1.0919357538223267, 1.0919357538223267)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.016 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.016') or bpy.data.objects.new('cuboid.016', None)
    ob.location = (20.127033233642578, -33.66490173339844, 1.0490659475326538)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (2.3001911640167236, 0.328475683927536, 0.8132531046867371)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.017 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.017') or bpy.data.objects.new('cuboid.017', None)
    ob.location = (20.127033233642578, -34.13309860229492, 0.3106675446033478)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (2.3001911640167236, 1.294737458229065, 0.6471762657165527)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: benchPhysicalDynamic.002 (type=MESH) ---
    ob = bpy.data.objects.get('benchPhysicalDynamic.002') or bpy.data.objects.new('benchPhysicalDynamic.002', bpy.data.meshes.get('Cube.158'))
    ob.location = (63.1190185546875, -17.26290512084961, 0.7560859322547913)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 2.2034144401550293)
    ob.scale = (1.0919357538223267, 1.0919357538223267, 1.0919357538223267)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.050 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.050') or bpy.data.objects.new('cuboid.050', None)
    ob.location = (20.127033233642578, -33.66490173339844, 1.0490659475326538)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (2.3001911640167236, 0.328475683927536, 0.8132531046867371)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.059 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.059') or bpy.data.objects.new('cuboid.059', None)
    ob.location = (20.127033233642578, -34.13309860229492, 0.3106675446033478)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (2.3001911640167236, 1.294737458229065, 0.6471762657165527)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: benchPhysicalDynamic.003 (type=MESH) ---
    ob = bpy.data.objects.get('benchPhysicalDynamic.003') or bpy.data.objects.new('benchPhysicalDynamic.003', bpy.data.meshes.get('Cube.158'))
    ob.location = (20.17071533203125, -8.83448600769043, 0.7560850381851196)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 1.3635456562042236)
    ob.scale = (1.0919357538223267, 1.0919357538223267, 1.0919357538223267)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.067 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.067') or bpy.data.objects.new('cuboid.067', None)
    ob.location = (20.127033233642578, -33.66490173339844, 1.0490659475326538)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (2.3001911640167236, 0.328475683927536, 0.8132531046867371)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.068 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.068') or bpy.data.objects.new('cuboid.068', None)
    ob.location = (20.127033233642578, -34.13309860229492, 0.3106675446033478)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (2.3001911640167236, 1.294737458229065, 0.6471762657165527)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: benchPhysicalDynamic.004 (type=MESH) ---
    ob = bpy.data.objects.get('benchPhysicalDynamic.004') or bpy.data.objects.new('benchPhysicalDynamic.004', bpy.data.meshes.get('Cube.158'))
    ob.location = (31.75165367126465, -50.856224060058594, 0.7560850381851196)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.9437110424041748)
    ob.scale = (1.0919357538223267, 1.0919357538223267, 1.0919357538223267)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.070 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.070') or bpy.data.objects.new('cuboid.070', None)
    ob.location = (20.127033233642578, -33.66490173339844, 1.0490659475326538)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (2.3001911640167236, 0.328475683927536, 0.8132531046867371)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.078 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.078') or bpy.data.objects.new('cuboid.078', None)
    ob.location = (20.127033233642578, -34.13309860229492, 0.3106675446033478)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (2.3001911640167236, 1.294737458229065, 0.6471762657165527)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: benchPhysicalDynamic.005 (type=MESH) ---
    ob = bpy.data.objects.get('benchPhysicalDynamic.005') or bpy.data.objects.new('benchPhysicalDynamic.005', bpy.data.meshes.get('Cube.158'))
    ob.location = (51.90874481201172, -47.349056243896484, 0.7560849785804749)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 1.9486019611358643)
    ob.scale = (1.0919357538223267, 1.0919357538223267, 1.0919357538223267)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.081 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.081') or bpy.data.objects.new('cuboid.081', None)
    ob.location = (20.127033233642578, -33.66490173339844, 1.0490659475326538)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (2.3001911640167236, 0.328475683927536, 0.8132531046867371)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.193 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.193') or bpy.data.objects.new('cuboid.193', None)
    ob.location = (20.127033233642578, -34.13309860229492, 0.3106675446033478)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (2.3001911640167236, 1.294737458229065, 0.6471762657165527)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: benchPhysicalDynamic.006 (type=MESH) ---
    ob = bpy.data.objects.get('benchPhysicalDynamic.006') or bpy.data.objects.new('benchPhysicalDynamic.006', bpy.data.meshes.get('Cube.158'))
    ob.location = (43.656410217285156, 35.148712158203125, 0.7560831308364868)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.8164312243461609)
    ob.scale = (1.0919357538223267, 1.0919357538223267, 1.0919357538223267)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.217 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.217') or bpy.data.objects.new('cuboid.217', None)
    ob.location = (20.127033233642578, -33.66490173339844, 1.0490659475326538)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (2.3001911640167236, 0.328475683927536, 0.8132531046867371)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.218 (type=EMPTY) ---
    ob = bpy.data.objects.get('cuboid.218') or bpy.data.objects.new('cuboid.218', None)
    ob.location = (20.127033233642578, -34.13309860229492, 0.3106675446033478)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (2.3001911640167236, 1.294737458229065, 0.6471762657165527)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CUBE'
    except Exception: pass
    try: ob.empty_display_size = 0.5
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 21 objects to benches')

if __name__ == '__main__': run()