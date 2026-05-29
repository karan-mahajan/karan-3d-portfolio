import bpy

def run():
    print('[044_areas] areas')
    coll = bpy.data.collections.get('areas')
    if coll is None: coll = bpy.data.collections.new('areas')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    print('  added 0 objects to areas')

if __name__ == '__main__': run()