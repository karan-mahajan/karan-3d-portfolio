"""Bruno's 041_flowers.py - verbatim recreation.

108 MESH objects (flowers, flowers.001 ... all sharing mesh `Plane.010`)
scattered world-wide into collection `flowers`. Maximally uniform: every
instance is rotation=(0,0,0), scale=(3.14, 3.14, 3.14), and a near-constant
z=0.384 (Bruno baked one flat-meadow height rather than terrain-sampling).
Flat ground-decal patches carrying flower vertex colour from the `palette`.

Adds: 108 MESH to collection `flowers`.

Source: folio-2025/scripts/blender_world_steps/steps/041_flowers.py
"""
import bpy

def run():
    print('[041_flowers] flowers')
    coll = bpy.data.collections.get('flowers')
    if coll is None: coll = bpy.data.collections.new('flowers')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: flowers (type=MESH) ---
    ob = bpy.data.objects.get('flowers') or bpy.data.objects.new('flowers', bpy.data.meshes.get('Plane.010'))
    ob.location = (38.08772659301758, -40.82295608520508, 0.38395655155181885)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.001 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.001') or bpy.data.objects.new('flowers.001', bpy.data.meshes.get('Plane.010'))
    ob.location = (18.32338523864746, -30.728914260864258, 0.38395655155181885)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.002 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.002') or bpy.data.objects.new('flowers.002', bpy.data.meshes.get('Plane.010'))
    ob.location = (29.59324073791504, -47.120243072509766, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.003 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.003') or bpy.data.objects.new('flowers.003', bpy.data.meshes.get('Plane.010'))
    ob.location = (32.29926681518555, -47.901363372802734, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.004 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.004') or bpy.data.objects.new('flowers.004', bpy.data.meshes.get('Plane.010'))
    ob.location = (34.05113983154297, -38.968074798583984, 0.38395610451698303)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.005 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.005') or bpy.data.objects.new('flowers.005', bpy.data.meshes.get('Plane.010'))
    ob.location = (27.694820404052734, -27.623973846435547, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.006 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.006') or bpy.data.objects.new('flowers.006', bpy.data.meshes.get('Plane.010'))
    ob.location = (26.61747169494629, -25.188230514526367, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.007 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.007') or bpy.data.objects.new('flowers.007', bpy.data.meshes.get('Plane.010'))
    ob.location = (58.296485900878906, -11.293672561645508, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.011 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.011') or bpy.data.objects.new('flowers.011', bpy.data.meshes.get('Plane.010'))
    ob.location = (14.939848899841309, -41.51005172729492, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.012 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.012') or bpy.data.objects.new('flowers.012', bpy.data.meshes.get('Plane.010'))
    ob.location = (15.490090370178223, -25.945322036743164, 0.3839561939239502)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.013 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.013') or bpy.data.objects.new('flowers.013', bpy.data.meshes.get('Plane.010'))
    ob.location = (27.457094192504883, -22.049104690551758, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.015 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.015') or bpy.data.objects.new('flowers.015', bpy.data.meshes.get('Plane.010'))
    ob.location = (-3.501436948776245, -39.755855560302734, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.016 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.016') or bpy.data.objects.new('flowers.016', bpy.data.meshes.get('Plane.010'))
    ob.location = (-0.5972812175750732, -35.680667877197266, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.017 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.017') or bpy.data.objects.new('flowers.017', bpy.data.meshes.get('Plane.010'))
    ob.location = (5.125302314758301, -6.331362247467041, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.018 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.018') or bpy.data.objects.new('flowers.018', bpy.data.meshes.get('Plane.010'))
    ob.location = (9.0502290725708, -26.462553024291992, 0.38395583629608154)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.021 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.021') or bpy.data.objects.new('flowers.021', bpy.data.meshes.get('Plane.010'))
    ob.location = (41.336631774902344, -50.466426849365234, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.022 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.022') or bpy.data.objects.new('flowers.022', bpy.data.meshes.get('Plane.010'))
    ob.location = (56.485286712646484, -65.38764953613281, 0.3839561939239502)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.023 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.023') or bpy.data.objects.new('flowers.023', bpy.data.meshes.get('Plane.010'))
    ob.location = (46.05192184448242, -53.6324348449707, 0.38395601511001587)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.024 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.024') or bpy.data.objects.new('flowers.024', bpy.data.meshes.get('Plane.010'))
    ob.location = (78.11300659179688, -29.971384048461914, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.025 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.025') or bpy.data.objects.new('flowers.025', bpy.data.meshes.get('Plane.010'))
    ob.location = (78.11699676513672, -45.65391159057617, 0.38395583629608154)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.026 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.026') or bpy.data.objects.new('flowers.026', bpy.data.meshes.get('Plane.010'))
    ob.location = (76.83126068115234, -23.455106735229492, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.027 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.027') or bpy.data.objects.new('flowers.027', bpy.data.meshes.get('Plane.010'))
    ob.location = (59.317848205566406, -23.432876586914062, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.028 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.028') or bpy.data.objects.new('flowers.028', bpy.data.meshes.get('Plane.010'))
    ob.location = (63.27879333496094, -21.97643280029297, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.030 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.030') or bpy.data.objects.new('flowers.030', bpy.data.meshes.get('Plane.010'))
    ob.location = (33.6932373046875, -4.233763217926025, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.031 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.031') or bpy.data.objects.new('flowers.031', bpy.data.meshes.get('Plane.010'))
    ob.location = (40.252315521240234, -4.08471155166626, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.032 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.032') or bpy.data.objects.new('flowers.032', bpy.data.meshes.get('Plane.010'))
    ob.location = (39.5987548828125, -31.493030548095703, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.033 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.033') or bpy.data.objects.new('flowers.033', bpy.data.meshes.get('Plane.010'))
    ob.location = (37.71358108520508, -72.21282958984375, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.034 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.034') or bpy.data.objects.new('flowers.034', bpy.data.meshes.get('Plane.010'))
    ob.location = (26.171968460083008, -73.23418426513672, 0.38395583629608154)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.035 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.035') or bpy.data.objects.new('flowers.035', bpy.data.meshes.get('Plane.010'))
    ob.location = (27.46748161315918, -75.46602630615234, 0.38395583629608154)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.036 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.036') or bpy.data.objects.new('flowers.036', bpy.data.meshes.get('Plane.010'))
    ob.location = (21.546871185302734, -74.98233032226562, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.037 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.037') or bpy.data.objects.new('flowers.037', bpy.data.meshes.get('Plane.010'))
    ob.location = (49.281211853027344, -40.3465461730957, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.038 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.038') or bpy.data.objects.new('flowers.038', bpy.data.meshes.get('Plane.010'))
    ob.location = (71.48689270019531, -57.5926399230957, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.014 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.014') or bpy.data.objects.new('flowers.014', bpy.data.meshes.get('Plane.010'))
    ob.location = (3.1723110675811768, -13.240446090698242, 0.38395577669143677)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.029 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.029') or bpy.data.objects.new('flowers.029', bpy.data.meshes.get('Plane.010'))
    ob.location = (13.27428913116455, -9.654611587524414, 0.38395583629608154)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.008 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.008') or bpy.data.objects.new('flowers.008', bpy.data.meshes.get('Plane.010'))
    ob.location = (51.222354888916016, -38.34952926635742, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.009 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.009') or bpy.data.objects.new('flowers.009', bpy.data.meshes.get('Plane.010'))
    ob.location = (9.244645118713379, -41.456207275390625, 0.3839561939239502)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.010 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.010') or bpy.data.objects.new('flowers.010', bpy.data.meshes.get('Plane.010'))
    ob.location = (60.55792999267578, -17.234712600708008, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.044 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.044') or bpy.data.objects.new('flowers.044', bpy.data.meshes.get('Plane.010'))
    ob.location = (38.61417007446289, 17.175270080566406, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.045 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.045') or bpy.data.objects.new('flowers.045', bpy.data.meshes.get('Plane.010'))
    ob.location = (34.39966583251953, 12.206594467163086, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.046 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.046') or bpy.data.objects.new('flowers.046', bpy.data.meshes.get('Plane.010'))
    ob.location = (41.088409423828125, 24.554061889648438, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.047 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.047') or bpy.data.objects.new('flowers.047', bpy.data.meshes.get('Plane.010'))
    ob.location = (31.51605796813965, 30.750415802001953, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.048 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.048') or bpy.data.objects.new('flowers.048', bpy.data.meshes.get('Plane.010'))
    ob.location = (22.95395851135254, 29.463886260986328, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.049 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.049') or bpy.data.objects.new('flowers.049', bpy.data.meshes.get('Plane.010'))
    ob.location = (23.30886459350586, 31.105327606201172, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.050 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.050') or bpy.data.objects.new('flowers.050', bpy.data.meshes.get('Plane.010'))
    ob.location = (12.750420570373535, 26.003559112548828, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.051 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.051') or bpy.data.objects.new('flowers.051', bpy.data.meshes.get('Plane.010'))
    ob.location = (9.451081275939941, 17.280757904052734, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.052 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.052') or bpy.data.objects.new('flowers.052', bpy.data.meshes.get('Plane.010'))
    ob.location = (9.068276405334473, 20.59124755859375, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.053 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.053') or bpy.data.objects.new('flowers.053', bpy.data.meshes.get('Plane.010'))
    ob.location = (14.036955833435059, 13.360044479370117, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.054 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.054') or bpy.data.objects.new('flowers.054', bpy.data.meshes.get('Plane.010'))
    ob.location = (11.641343116760254, 10.609525680541992, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.055 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.055') or bpy.data.objects.new('flowers.055', bpy.data.meshes.get('Plane.010'))
    ob.location = (16.432571411132812, 9.988439559936523, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.057 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.057') or bpy.data.objects.new('flowers.057', bpy.data.meshes.get('Plane.010'))
    ob.location = (18.16434669494629, -78.43999481201172, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.058 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.058') or bpy.data.objects.new('flowers.058', bpy.data.meshes.get('Plane.010'))
    ob.location = (16.772907257080078, -79.14222717285156, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.059 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.059') or bpy.data.objects.new('flowers.059', bpy.data.meshes.get('Plane.010'))
    ob.location = (-22.28260612487793, -74.78642272949219, 0.38395625352859497)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.062 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.062') or bpy.data.objects.new('flowers.062', bpy.data.meshes.get('Plane.010'))
    ob.location = (42.94221115112305, -11.234867095947266, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.063 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.063') or bpy.data.objects.new('flowers.063', bpy.data.meshes.get('Plane.010'))
    ob.location = (60.553653717041016, -29.51873016357422, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.064 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.064') or bpy.data.objects.new('flowers.064', bpy.data.meshes.get('Plane.010'))
    ob.location = (58.306175231933594, -26.82256507873535, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.039 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.039') or bpy.data.objects.new('flowers.039', bpy.data.meshes.get('Plane.010'))
    ob.location = (-54.23307418823242, -80.52442169189453, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.040 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.040') or bpy.data.objects.new('flowers.040', bpy.data.meshes.get('Plane.010'))
    ob.location = (-85.26524353027344, -85.63109588623047, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.041 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.041') or bpy.data.objects.new('flowers.041', bpy.data.meshes.get('Plane.010'))
    ob.location = (-66.44117736816406, -81.57318115234375, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.042 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.042') or bpy.data.objects.new('flowers.042', bpy.data.meshes.get('Plane.010'))
    ob.location = (-63.78406524658203, -58.195247650146484, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.043 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.043') or bpy.data.objects.new('flowers.043', bpy.data.meshes.get('Plane.010'))
    ob.location = (-48.66471481323242, -54.656673431396484, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.061 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.061') or bpy.data.objects.new('flowers.061', bpy.data.meshes.get('Plane.010'))
    ob.location = (-49.200862884521484, -50.045806884765625, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.066 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.066') or bpy.data.objects.new('flowers.066', bpy.data.meshes.get('Plane.010'))
    ob.location = (-38.15623092651367, -45.86385726928711, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.067 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.067') or bpy.data.objects.new('flowers.067', bpy.data.meshes.get('Plane.010'))
    ob.location = (-26.875078201293945, -28.144878387451172, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.068 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.068') or bpy.data.objects.new('flowers.068', bpy.data.meshes.get('Plane.010'))
    ob.location = (-51.45268630981445, 1.424344539642334, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.069 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.069') or bpy.data.objects.new('flowers.069', bpy.data.meshes.get('Plane.010'))
    ob.location = (-48.23580551147461, 13.005128860473633, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.070 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.070') or bpy.data.objects.new('flowers.070', bpy.data.meshes.get('Plane.010'))
    ob.location = (-60.6744270324707, 12.897897720336914, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.071 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.071') or bpy.data.objects.new('flowers.071', bpy.data.meshes.get('Plane.010'))
    ob.location = (-73.53300476074219, 4.004683494567871, 0.38395601511001587)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.072 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.072') or bpy.data.objects.new('flowers.072', bpy.data.meshes.get('Plane.010'))
    ob.location = (-74.60530090332031, 1.4311742782592773, 0.38395601511001587)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.073 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.073') or bpy.data.objects.new('flowers.073', bpy.data.meshes.get('Plane.010'))
    ob.location = (-23.14410972595215, 14.93525505065918, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.074 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.074') or bpy.data.objects.new('flowers.074', bpy.data.meshes.get('Plane.010'))
    ob.location = (-3.7355754375457764, 37.667903900146484, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.075 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.075') or bpy.data.objects.new('flowers.075', bpy.data.meshes.get('Plane.010'))
    ob.location = (-0.6259219646453857, 49.24868392944336, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.077 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.077') or bpy.data.objects.new('flowers.077', bpy.data.meshes.get('Plane.010'))
    ob.location = (-26.707866668701172, 78.76640319824219, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.078 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.078') or bpy.data.objects.new('flowers.078', bpy.data.meshes.get('Plane.010'))
    ob.location = (-25.824846267700195, 66.61986541748047, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.079 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.079') or bpy.data.objects.new('flowers.079', bpy.data.meshes.get('Plane.010'))
    ob.location = (-27.969438552856445, 57.07643508911133, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.080 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.080') or bpy.data.objects.new('flowers.080', bpy.data.meshes.get('Plane.010'))
    ob.location = (-27.862207412719727, 48.176387786865234, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.081 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.081') or bpy.data.objects.new('flowers.081', bpy.data.meshes.get('Plane.010'))
    ob.location = (-52.41775894165039, 41.742618560791016, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.082 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.082') or bpy.data.objects.new('flowers.082', bpy.data.meshes.get('Plane.010'))
    ob.location = (-66.67927551269531, 47.53300857543945, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.083 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.083') or bpy.data.objects.new('flowers.083', bpy.data.meshes.get('Plane.010'))
    ob.location = (-66.78651428222656, 50.32097244262695, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.084 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.084') or bpy.data.objects.new('flowers.084', bpy.data.meshes.get('Plane.010'))
    ob.location = (-69.46725463867188, 57.71980667114258, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.085 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.085') or bpy.data.objects.new('flowers.085', bpy.data.meshes.get('Plane.010'))
    ob.location = (-61.63949966430664, 49.35590744018555, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.086 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.086') or bpy.data.objects.new('flowers.086', bpy.data.meshes.get('Plane.010'))
    ob.location = (-65.07083892822266, 41.31369400024414, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.087 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.087') or bpy.data.objects.new('flowers.087', bpy.data.meshes.get('Plane.010'))
    ob.location = (-66.97416687011719, -31.492122650146484, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.088 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.088') or bpy.data.objects.new('flowers.088', bpy.data.meshes.get('Plane.010'))
    ob.location = (-65.41039276123047, -29.034778594970703, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.089 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.089') or bpy.data.objects.new('flowers.089', bpy.data.meshes.get('Plane.010'))
    ob.location = (-4.1257429122924805, 69.92913818359375, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.090 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.090') or bpy.data.objects.new('flowers.090', bpy.data.meshes.get('Plane.010'))
    ob.location = (-4.721461296081543, 60.993343353271484, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.091 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.091') or bpy.data.objects.new('flowers.091', bpy.data.meshes.get('Plane.010'))
    ob.location = (-5.391646385192871, 53.17452621459961, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.092 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.092') or bpy.data.objects.new('flowers.092', bpy.data.meshes.get('Plane.010'))
    ob.location = (68.70097351074219, 74.76936340332031, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.093 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.093') or bpy.data.objects.new('flowers.093', bpy.data.meshes.get('Plane.010'))
    ob.location = (66.54148864746094, 71.34397888183594, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.094 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.094') or bpy.data.objects.new('flowers.094', bpy.data.meshes.get('Plane.010'))
    ob.location = (70.48812866210938, 60.17423629760742, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.095 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.095') or bpy.data.objects.new('flowers.095', bpy.data.meshes.get('Plane.010'))
    ob.location = (66.09469604492188, 51.908626556396484, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.096 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.096') or bpy.data.objects.new('flowers.096', bpy.data.meshes.get('Plane.010'))
    ob.location = (47.55292892456055, 66.57821655273438, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.097 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.097') or bpy.data.objects.new('flowers.097', bpy.data.meshes.get('Plane.010'))
    ob.location = (44.42539978027344, 70.22699737548828, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.098 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.098') or bpy.data.objects.new('flowers.098', bpy.data.meshes.get('Plane.010'))
    ob.location = (7.49981689453125, 87.69918823242188, 0.3839561343193054)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.076 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.076') or bpy.data.objects.new('flowers.076', bpy.data.meshes.get('Plane.010'))
    ob.location = (64.33892822265625, -53.58357238769531, 0.38395583629608154)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.019 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.019') or bpy.data.objects.new('flowers.019', bpy.data.meshes.get('Plane.010'))
    ob.location = (-28.483409881591797, -72.50009155273438, 0.38395625352859497)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.020 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.020') or bpy.data.objects.new('flowers.020', bpy.data.meshes.get('Plane.010'))
    ob.location = (-11.7794189453125, -60.47016143798828, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.056 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.056') or bpy.data.objects.new('flowers.056', bpy.data.meshes.get('Plane.010'))
    ob.location = (48.87049102783203, 6.027275085449219, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.060 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.060') or bpy.data.objects.new('flowers.060', bpy.data.meshes.get('Plane.010'))
    ob.location = (57.925575256347656, 15.485742568969727, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.065 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.065') or bpy.data.objects.new('flowers.065', bpy.data.meshes.get('Plane.010'))
    ob.location = (65.75884246826172, 40.37952423095703, 0.38395559787750244)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.099 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.099') or bpy.data.objects.new('flowers.099', bpy.data.meshes.get('Plane.010'))
    ob.location = (67.73233032226562, 41.6260986328125, 0.38395562767982483)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.100 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.100') or bpy.data.objects.new('flowers.100', bpy.data.meshes.get('Plane.010'))
    ob.location = (48.27412414550781, 31.32312774658203, 0.38395562767982483)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.102 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.102') or bpy.data.objects.new('flowers.102', bpy.data.meshes.get('Plane.010'))
    ob.location = (62.39008712768555, -2.0284335613250732, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.103 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.103') or bpy.data.objects.new('flowers.103', bpy.data.meshes.get('Plane.010'))
    ob.location = (63.16252136230469, -0.21489083766937256, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.104 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.104') or bpy.data.objects.new('flowers.104', bpy.data.meshes.get('Plane.010'))
    ob.location = (82.95964050292969, 20.868635177612305, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.105 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.105') or bpy.data.objects.new('flowers.105', bpy.data.meshes.get('Plane.010'))
    ob.location = (85.07012176513672, 25.51323890686035, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.106 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.106') or bpy.data.objects.new('flowers.106', bpy.data.meshes.get('Plane.010'))
    ob.location = (83.2323989868164, 30.687881469726562, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.107 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.107') or bpy.data.objects.new('flowers.107', bpy.data.meshes.get('Plane.010'))
    ob.location = (66.20927429199219, 28.801795959472656, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: flowers.108 (type=MESH) ---
    ob = bpy.data.objects.get('flowers.108') or bpy.data.objects.new('flowers.108', bpy.data.meshes.get('Plane.010'))
    ob.location = (65.29041290283203, 30.97804832458496, 0.38395607471466064)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, 0.0)
    ob.scale = (3.142632246017456, 3.142632246017456, 3.142632246017456)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 108 objects to flowers')

if __name__ == '__main__': run()