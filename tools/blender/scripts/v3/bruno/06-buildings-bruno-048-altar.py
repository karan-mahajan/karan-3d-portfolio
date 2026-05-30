"""Bruno's 048_altar.py - verbatim recreation.

Ritual `altar` zone — 10 MESH (8 hidden WIRE collision cuboid/trimesh shapes +
2 visible: refSkullEyes5, Cube.173) + 5 EMPTY zone anchors (root, bounding/
frustum CIRCLEs, refCounter, refAltar, physicalFixed). Centre ~(75.34, 27.95).

Adds: 15 objects to collection `altar`.

Section 06 (buildings & structures). Collection is linked to the scene
root here (Bruno relies on 999_finalize for that; we do not run it yet),
matching the section-02..05 bruno scripts so the build is viewable.

Source: folio-2025/scripts/blender_world_steps/steps/048_altar.py

"""
import bpy

def run():
    print('[048_altar] altar')
    coll = bpy.data.collections.get('altar')
    if coll is None: coll = bpy.data.collections.new('altar')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: trimesh.001 (type=MESH) ---
    ob = bpy.data.objects.get('trimesh.001') or bpy.data.objects.new('trimesh.001', bpy.data.meshes.get('Cylinder.020'))
    ob.location = (27.62302017211914, 27.774839401245117, -0.1803593635559082)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.072 (type=MESH) ---
    ob = bpy.data.objects.get('cuboid.072') or bpy.data.objects.new('cuboid.072', bpy.data.meshes.get('Cube.039'))
    ob.location = (31.745285034179688, 23.656280517578125, 1.2598564624786377)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.5283854007720947)
    ob.scale = (2.05944561958313, 1.5460275411605835, 2.5571084022521973)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.073 (type=MESH) ---
    ob = bpy.data.objects.get('cuboid.073') or bpy.data.objects.new('cuboid.073', bpy.data.meshes.get('Cube.039'))
    ob.location = (33.27054214477539, 28.569345474243164, 1.2598564624786377)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 1.650030255317688)
    ob.scale = (1.2773332595825195, 1.2955574989318848, 2.1070592403411865)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.074 (type=MESH) ---
    ob = bpy.data.objects.get('cuboid.074') or bpy.data.objects.new('cuboid.074', bpy.data.meshes.get('Cube.039'))
    ob.location = (31.46568489074707, 32.272254943847656, 2.2881436347961426)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 2.4385359287261963)
    ob.scale = (2.1226491928100586, 2.152933120727539, 5.013810634613037)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.075 (type=MESH) ---
    ob = bpy.data.objects.get('cuboid.075') or bpy.data.objects.new('cuboid.075', bpy.data.meshes.get('Cube.039'))
    ob.location = (26.312177658081055, 33.59269714355469, 2.2881433963775635)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, -2.9376001358032227)
    ob.scale = (2.2009358406066895, 2.2323365211486816, 5.013810634613037)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.076 (type=MESH) ---
    ob = bpy.data.objects.get('cuboid.076') or bpy.data.objects.new('cuboid.076', bpy.data.meshes.get('Cube.039'))
    ob.location = (22.3729305267334, 30.529794692993164, 2.2881433963775635)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, -2.07018780708313)
    ob.scale = (2.2009360790252686, 2.2323367595672607, 5.013810634613037)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: cuboid.077 (type=MESH) ---
    ob = bpy.data.objects.get('cuboid.077') or bpy.data.objects.new('cuboid.077', bpy.data.meshes.get('Cube.039'))
    ob.location = (25.065099716186523, 22.589574813842773, 1.6937228441238403)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, -0.4222200810909271)
    ob.scale = (1.714015007019043, 1.7384690046310425, 3.384026527404785)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'WIRE'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: physicalFixed.005 (type=EMPTY) ---
    ob = bpy.data.objects.get('physicalFixed.005') or bpy.data.objects.new('physicalFixed.005', None)
    ob.location = (75.34883117675781, 27.941041946411133, 0.9431422352790833)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.0)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.hide_render = True
    except Exception: pass
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'PLAIN_AXES'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refAltar (type=EMPTY) ---
    ob = bpy.data.objects.get('refAltar') or bpy.data.objects.new('refAltar', None)
    ob.location = (75.34408569335938, 27.94936180114746, 0.0)
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

    # --- object: refCounter (type=EMPTY) ---
    ob = bpy.data.objects.get('refCounter') or bpy.data.objects.new('refCounter', None)
    ob.location = (79.9752197265625, 22.932350158691406, 1.6403694152832031)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.5233656764030457)
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

    # --- object: refZoneBounding.006 (type=EMPTY) ---
    ob = bpy.data.objects.get('refZoneBounding.006') or bpy.data.objects.new('refZoneBounding.006', None)
    ob.location = (76.09484100341797, 24.828371047973633, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (12.350135803222656, 12.350135803222656, 12.350135803222656)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: altar (type=EMPTY) ---
    ob = bpy.data.objects.get('altar') or bpy.data.objects.new('altar', None)
    ob.location = (75.34408569335938, 27.94936180114746, 0.0)
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

    # --- object: refZoneFrustum.006 (type=EMPTY) ---
    ob = bpy.data.objects.get('refZoneFrustum.006') or bpy.data.objects.new('refZoneFrustum.006', None)
    ob.location = (74.9166030883789, 27.014631271362305, 3.2733683586120605)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-1.570796251296997, 0.0, 0.0)
    ob.scale = (12.872903823852539, 12.872903823852539, 12.872903823852539)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    try: ob.empty_display_type = 'CIRCLE'
    except Exception: pass
    try: ob.empty_display_size = 1.0
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: refSkullEyes5 (type=MESH) ---
    ob = bpy.data.objects.get('refSkullEyes5') or bpy.data.objects.new('refSkullEyes5', bpy.data.meshes.get('Plane.016'))
    ob.location = (75.50125122070312, 32.26530838012695, 0.9949032664299011)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.9992598295211792)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.173 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.173') or bpy.data.objects.new('Cube.173', bpy.data.meshes.get('Cube.083'))
    ob.location = (71.19155883789062, 24.855253219604492, -0.14109733700752258)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.2563174366950989)
    ob.scale = (0.6619588136672974, 0.6619588136672974, 0.6619588136672974)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 15 objects to altar')

if __name__ == '__main__': run()