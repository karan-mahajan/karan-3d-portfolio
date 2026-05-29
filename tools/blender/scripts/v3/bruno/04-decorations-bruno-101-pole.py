"""Bruno's 101_pole.py - verbatim recreation.

Projects-zone signage pole: post/sign meshes (Cube.079/088/106) plus flat
label planes (Plane.034..041) for role/at/with text and `refel` badges.
All text-anchor empties (role/at/with/refAttributes) are self-created here.

Adds: 13 objects (9 MESH, 4 EMPTY) to collection `pole`.

Source: folio-2025/scripts/blender_world_steps/steps/101_pole.py
"""
import bpy

def run():
    print('[101_pole] pole')
    coll = bpy.data.collections.get('pole')
    if coll is None: coll = bpy.data.collections.new('pole')

    # --- object: cube.021 (type=MESH) ---
    ob = bpy.data.objects.get('cube.021') or bpy.data.objects.new('cube.021', bpy.data.meshes.get('Cube.079'))
    ob.location = (-23.445392608642578, 24.361835479736328, 3.5126471519470215)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-0.00289551867172122, -0.010805781930685043, 0.5236144661903381)
    ob.scale = (0.5414859056472778, 0.5414859056472778, 0.5414858460426331)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cube.026 (type=MESH) ---
    ob = bpy.data.objects.get('cube.026') or bpy.data.objects.new('cube.026', bpy.data.meshes.get('Cube.088'))
    ob.location = (-23.533100128173828, 24.30191993713379, 1.9562957286834717)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.048554785549640656, 3.188087224960327, 0.5130941271781921)
    ob.scale = (0.5414858460426331, 0.5414859056472778, 0.5414859056472778)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cube.033 (type=MESH) ---
    ob = bpy.data.objects.get('cube.033') or bpy.data.objects.new('cube.033', bpy.data.meshes.get('Cube.106'))
    ob.location = (-23.314897537231445, 24.423307418823242, 2.761237859725952)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0161563940346241, 0.12511727213859558, 0.5151353478431702)
    ob.scale = (0.5414859056472778, 0.5414859056472778, 0.5414859652519226)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: role (type=EMPTY) ---
    ob = bpy.data.objects.get('role') or bpy.data.objects.new('role', None)
    ob.location = (-23.440242767333984, 24.33686065673828, 3.313305377960205)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.5235987901687622)
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

    # --- object: at (type=EMPTY) ---
    ob = bpy.data.objects.get('at') or bpy.data.objects.new('at', None)
    ob.location = (-23.440242767333984, 24.33686065673828, 2.568195343017578)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.5235987901687622)
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

    # --- object: with (type=EMPTY) ---
    ob = bpy.data.objects.get('with') or bpy.data.objects.new('with', None)
    ob.location = (-23.440242767333984, 24.33686065673828, 1.8272244930267334)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.5235987901687622)
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

    # --- object: refAttributes (type=EMPTY) ---
    ob = bpy.data.objects.get('refAttributes') or bpy.data.objects.new('refAttributes', None)
    ob.location = (37.84706115722656, -7.961084842681885, 2.5549123287200928)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.5235987901687622)
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

    # --- object: text.001 (type=MESH) ---
    ob = bpy.data.objects.get('text.001') or bpy.data.objects.new('text.001', bpy.data.meshes.get('Plane.037'))
    ob.location = (-23.924795150756836, 24.057104110717773, 3.180105209350586)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (1.570796251296997, 1.4614496279818923e-09, 0.5235987901687622)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refel.002 (type=MESH) ---
    ob = bpy.data.objects.get('refel.002') or bpy.data.objects.new('refel.002', bpy.data.meshes.get('Plane.034'))
    ob.location = (-23.527067184448242, 24.280715942382812, 3.4714505672454834)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (1.5707961320877075, -6.299876176285579e-09, 0.1745329201221466)
    ob.scale = (0.9999999403953552, 1.0, 0.9999999403953552)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refel.001 (type=MESH) ---
    ob = bpy.data.objects.get('refel.001') or bpy.data.objects.new('refel.001', bpy.data.meshes.get('Plane.035'))
    ob.location = (-23.445375442504883, 24.316307067871094, 2.7408175468444824)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (1.5707961320877075, -6.299876176285579e-09, 0.1745329201221466)
    ob.scale = (0.9999999403953552, 1.0, 0.9999999403953552)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refel (type=MESH) ---
    ob = bpy.data.objects.get('refel') or bpy.data.objects.new('refel', bpy.data.meshes.get('Plane.040'))
    ob.location = (-23.516979217529297, 24.272260665893555, 1.9913222789764404)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (1.520620584487915, 0.09683078527450562, 0.1682904213666916)
    ob.scale = (0.9999999403953552, 1.0, 0.9999999403953552)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: text.002 (type=MESH) ---
    ob = bpy.data.objects.get('text.002') or bpy.data.objects.new('text.002', bpy.data.meshes.get('Plane.039'))
    ob.location = (-23.924795150756836, 24.057104110717773, 1.6945656538009644)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (1.570796251296997, 1.4614496279818923e-09, 0.5235987901687622)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: text (type=MESH) ---
    ob = bpy.data.objects.get('text') or bpy.data.objects.new('text', bpy.data.meshes.get('Plane.041'))
    ob.location = (-23.924795150756836, 24.057104110717773, 2.4402267932891846)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (1.570796251296997, 1.4614496279818923e-09, 0.5235987901687622)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 13 objects to pole')

if __name__ == '__main__': run()