import bpy

def run():
    print('[12_world] world shader')

    # --- World ---
    w = bpy.data.worlds.get('World') or bpy.data.worlds.new('World')
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeOutputWorld')
    n.name = 'World Output'
    n.location = (300.0, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    nodes_by_name['World Output'] = n
    n = nt.nodes.new('ShaderNodeBackground')
    n.name = 'Background'
    n.location = (10.0, 300.0)
    try: n.inputs[0].default_value = (0.34719762206077576, 0.2566399574279785, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.0
    except Exception: pass
    nodes_by_name['Background'] = n
    try: nt.links.new(nodes_by_name['Background'].outputs[0], nodes_by_name['World Output'].inputs[0])
    except Exception: pass
    bpy.context.scene.world = w

if __name__ == '__main__': run()