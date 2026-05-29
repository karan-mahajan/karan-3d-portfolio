"""Bruno's 026_rocks.py - verbatim recreation.

A single large landmark rock (object Cube.157, mesh Cube.070) at the far
south-east corner (~57, -50), 3-axis tumbled rotation, 0.94x scale.

Adds: 1 MESH to collection `rocks`.

Source: folio-2025/scripts/blender_world_steps/steps/026_rocks.py
"""
import bpy

def run():
    print('[026_rocks] rocks')
    coll = bpy.data.collections.get('rocks')
    if coll is None: coll = bpy.data.collections.new('rocks')

    # --- object: Cube.157 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.157') or bpy.data.objects.new('Cube.157', bpy.data.meshes.get('Cube.070'))
    ob.location = (57.463096618652344, -50.010379791259766, -0.1420145034790039)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.9388081431388855, 0.6182178854942322, -1.2236969470977783)
    ob.scale = (0.9428627490997314, 0.9428629875183105, 0.9428628087043762)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 1 objects to rocks')

if __name__ == '__main__': run()
