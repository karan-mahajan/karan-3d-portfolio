import bpy

def run():
    print('[04_materials] building materials')

    # --- airDancer ---
    mat = bpy.data.materials.get('airDancer') or bpy.data.materials.new('airDancer')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (-200.0, 100.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (200.0, 100.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture'
    n.location = (-549.3529663085938, 43.89528274536133)
    n.width = 240.0
    try: n.interpolation = 'Linear'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'EXTEND'
    except Exception: pass
    n.image = bpy.data.images.get('circuitAirDancerFace.png')
    try: n.inputs[0].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Image Texture'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image Texture'].outputs[0], nodes_by_name['Principled BSDF'].inputs[0])
    except Exception: pass

    # --- black ---
    mat = bpy.data.materials.get('black') or bpy.data.materials.new('black')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (10.0, 300.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[0].default_value = (0.06847876310348511, 0.05286135897040367, 0.045185573399066925, 1.0)
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (300.0, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass

    # --- blackboardLabels ---
    mat = bpy.data.materials.get('blackboardLabels') or bpy.data.materials.new('blackboardLabels')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (-200.0, 100.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (200.0, 100.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture'
    n.location = (-586.6051025390625, 15.604625701904297)
    n.width = 240.0
    try: n.interpolation = 'Linear'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'EXTEND'
    except Exception: pass
    n.image = bpy.data.images.get('blackboardLabels.png')
    try: n.inputs[0].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Image Texture'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image Texture'].outputs[0], nodes_by_name['Principled BSDF'].inputs[0])
    except Exception: pass

    # --- bowlingLabelStrike ---
    mat = bpy.data.materials.get('bowlingLabelStrike') or bpy.data.materials.new('bowlingLabelStrike')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (-200.0, 100.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (200.0, 100.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture'
    n.location = (-592.2940673828125, 2.695526123046875)
    n.width = 240.0
    try: n.interpolation = 'Linear'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'EXTEND'
    except Exception: pass
    n.image = bpy.data.images.get('bowlingLabelStrike.png')
    try: n.inputs[0].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Image Texture'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image Texture'].outputs[0], nodes_by_name['Principled BSDF'].inputs[0])
    except Exception: pass
    try: mat['prevent'] = True
    except Exception: pass

    # --- careerTextFreelancer ---
    mat = bpy.data.materials.get('careerTextFreelancer') or bpy.data.materials.new('careerTextFreelancer')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (10.0, 300.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (300.0, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture'
    n.location = (-298.99853515625, 280.0235595703125)
    n.width = 240.0
    try: n.interpolation = 'Linear'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'EXTEND'
    except Exception: pass
    n.image = bpy.data.images.get('careerFreelancer.png')
    try: n.inputs[0].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Image Texture'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass
    try: mat['prevent'] = True
    except Exception: pass

    # --- careerTextHetic ---
    mat = bpy.data.materials.get('careerTextHetic') or bpy.data.materials.new('careerTextHetic')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (10.0, 300.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (300.0, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture'
    n.location = (-298.99853515625, 280.0235595703125)
    n.width = 240.0
    try: n.interpolation = 'Linear'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'EXTEND'
    except Exception: pass
    n.image = bpy.data.images.get('careerHetic.png')
    try: n.inputs[0].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Image Texture'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass
    try: mat['prevent'] = True
    except Exception: pass

    # --- careerTextImmersive ---
    mat = bpy.data.materials.get('careerTextImmersive') or bpy.data.materials.new('careerTextImmersive')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (10.0, 300.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (300.0, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture'
    n.location = (-298.99853515625, 280.0235595703125)
    n.width = 240.0
    try: n.interpolation = 'Linear'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'EXTEND'
    except Exception: pass
    n.image = bpy.data.images.get('careerImmersiveGarden.png')
    try: n.inputs[0].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Image Texture'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass
    try: mat['prevent'] = True
    except Exception: pass

    # --- careerTextIRLTeacher ---
    mat = bpy.data.materials.get('careerTextIRLTeacher') or bpy.data.materials.new('careerTextIRLTeacher')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (10.0, 300.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (300.0, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture'
    n.location = (-298.99853515625, 280.0235595703125)
    n.width = 240.0
    try: n.interpolation = 'Linear'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'EXTEND'
    except Exception: pass
    n.image = bpy.data.images.get('careerIRLTeacher.png')
    try: n.inputs[0].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Image Texture'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass
    try: mat['prevent'] = True
    except Exception: pass

    # --- careerTextOnlineTeacher ---
    mat = bpy.data.materials.get('careerTextOnlineTeacher') or bpy.data.materials.new('careerTextOnlineTeacher')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (10.0, 300.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (300.0, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture'
    n.location = (-298.99853515625, 280.0235595703125)
    n.width = 240.0
    try: n.interpolation = 'Linear'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'EXTEND'
    except Exception: pass
    n.image = bpy.data.images.get('careerOnlineTeacher.png')
    try: n.inputs[0].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Image Texture'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass
    try: mat['prevent'] = True
    except Exception: pass

    # --- careerTextUzik ---
    mat = bpy.data.materials.get('careerTextUzik') or bpy.data.materials.new('careerTextUzik')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (10.0, 300.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (300.0, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture'
    n.location = (-298.99853515625, 280.0235595703125)
    n.width = 240.0
    try: n.interpolation = 'Linear'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'EXTEND'
    except Exception: pass
    n.image = bpy.data.images.get('careerUzik.png')
    try: n.inputs[0].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Image Texture'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass
    try: mat['prevent'] = True
    except Exception: pass

    # --- circuitBrand ---
    mat = bpy.data.materials.get('circuitBrand') or bpy.data.materials.new('circuitBrand')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (10.0, 300.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (300.0, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture'
    n.location = (-379.61431884765625, 275.1842956542969)
    n.width = 240.0
    try: n.interpolation = 'Linear'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'EXTEND'
    except Exception: pass
    n.image = bpy.data.images.get('circuitBrand.png')
    try: n.inputs[0].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Image Texture'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image Texture'].outputs[0], nodes_by_name['Principled BSDF'].inputs[0])
    except Exception: pass

    # --- circuitThreejs ---
    mat = bpy.data.materials.get('circuitThreejs') or bpy.data.materials.new('circuitThreejs')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (10.0, 300.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (300.0, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture'
    n.location = (-463.1771545410156, 270.5379638671875)
    n.width = 274.8178405761719
    try: n.interpolation = 'Linear'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'EXTEND'
    except Exception: pass
    n.image = bpy.data.images.get('circuitLogoThreejs.png')
    try: n.inputs[0].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Image Texture'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image Texture'].outputs[0], nodes_by_name['Principled BSDF'].inputs[0])
    except Exception: pass

    # --- circuitWebgl ---
    mat = bpy.data.materials.get('circuitWebgl') or bpy.data.materials.new('circuitWebgl')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (-200.0, 100.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (200.0, 100.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture'
    n.location = (-547.50341796875, 70.07939910888672)
    n.width = 240.0
    try: n.interpolation = 'Linear'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'EXTEND'
    except Exception: pass
    n.image = bpy.data.images.get('circuitLogoWebgl.png')
    try: n.inputs[0].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Image Texture'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image Texture'].outputs[0], nodes_by_name['Principled BSDF'].inputs[0])
    except Exception: pass

    # --- circuitWebgpu ---
    mat = bpy.data.materials.get('circuitWebgpu') or bpy.data.materials.new('circuitWebgpu')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (10.0, 300.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (300.0, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture'
    n.location = (-463.1771545410156, 270.5379638671875)
    n.width = 274.8178405761719
    try: n.interpolation = 'Linear'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'EXTEND'
    except Exception: pass
    n.image = bpy.data.images.get('circuitLogoWebgpu.png')
    try: n.inputs[0].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Image Texture'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image Texture'].outputs[0], nodes_by_name['Principled BSDF'].inputs[0])
    except Exception: pass

    # --- cookieBanner ---
    mat = bpy.data.materials.get('cookieBanner') or bpy.data.materials.new('cookieBanner')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (10.0, 300.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 1.0
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (300.0, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture'
    n.location = (-324.8487243652344, 203.01437377929688)
    n.width = 240.0
    try: n.interpolation = 'Linear'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'REPEAT'
    except Exception: pass
    n.image = bpy.data.images.get('cookieBanner.png')
    try: n.inputs[0].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Image Texture'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image Texture'].outputs[0], nodes_by_name['Principled BSDF'].inputs[0])
    except Exception: pass

    # --- darkGray ---
    mat = bpy.data.materials.get('darkGray') or bpy.data.materials.new('darkGray')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (10.0, 300.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[0].default_value = (0.1743464469909668, 0.1454935520887375, 0.10320667922496796, 1.0)
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (300.0, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass

    # --- Dots Stroke ---
    mat = bpy.data.materials.get('Dots Stroke') or bpy.data.materials.new('Dots Stroke')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.5
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('NodeFrame')
    n.name = 'Frame'
    n.label = 'Versioning: Use Nodes was removed'
    n.location = (0.0, 0.0)
    n.width = 150.0
    nodes_by_name['Frame'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (480.0, 0.0)
    try: n.target = 'EEVEE'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (0.0, 0.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output.001'
    n.location = (450.0, 0.0)
    try: n.target = 'CYCLES'
    except Exception: pass
    try: n.is_active_output = False
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output.001'] = n
    n = nt.nodes.new('ShaderNodeBsdfDiffuse')
    n.name = 'Diffuse BSDF'
    n.location = (0.0, 0.0)
    n.width = 150.0
    try: n.inputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Diffuse BSDF'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Diffuse BSDF'].outputs[0], nodes_by_name['Material Output.001'].inputs[0])
    except Exception: pass
    try: mat['yp'] = []
    except Exception: pass

    # --- emissiveBlueRadialGradient ---
    mat = bpy.data.materials.get('emissiveBlueRadialGradient') or bpy.data.materials.new('emissiveBlueRadialGradient')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (300.0, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeRGB')
    n.name = 'RGB'
    n.location = (45.696983337402344, 239.06565856933594)
    n.outputs[0].default_value = (0.4994472861289978, 0.18731802701950073, 1.0, 1.0)
    nodes_by_name['RGB'] = n
    n = nt.nodes.new('ShaderNodeEmission')
    n.name = 'Emission'
    n.location = (51.39771270751953, 388.82977294921875)
    try: n.inputs[0].default_value = (0.0, 0.09212113171815872, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[1].default_value = 18.899999618530273
    except Exception: pass
    try: n.inputs[2].default_value = 0.0
    except Exception: pass
    nodes_by_name['Emission'] = n
    try: nt.links.new(nodes_by_name['Emission'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass

    # --- emissiveGreenRadialGradient ---
    mat = bpy.data.materials.get('emissiveGreenRadialGradient') or bpy.data.materials.new('emissiveGreenRadialGradient')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (300.0, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeRGB')
    n.name = 'RGB'
    n.location = (44.88832092285156, 254.4332733154297)
    n.outputs[0].default_value = (1.0, 0.2620239853858948, 0.0, 1.0)
    nodes_by_name['RGB'] = n
    n = nt.nodes.new('ShaderNodeEmission')
    n.name = 'Emission'
    n.location = (54.354835510253906, 450.0172424316406)
    try: n.inputs[0].default_value = (1.0, 0.1943838894367218, 0.0, 1.0)
    except Exception: pass
    try: n.inputs[1].default_value = 16.69999885559082
    except Exception: pass
    try: n.inputs[2].default_value = 0.0
    except Exception: pass
    nodes_by_name['Emission'] = n
    try: nt.links.new(nodes_by_name['Emission'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass

    # --- emissiveOrangeRadialGradient ---
    mat = bpy.data.materials.get('emissiveOrangeRadialGradient') or bpy.data.materials.new('emissiveOrangeRadialGradient')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (300.0, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeRGB')
    n.name = 'RGB'
    n.location = (44.88832092285156, 254.4332733154297)
    n.outputs[0].default_value = (1.0, 0.2620239853858948, 0.0, 1.0)
    nodes_by_name['RGB'] = n
    n = nt.nodes.new('ShaderNodeEmission')
    n.name = 'Emission'
    n.location = (54.354835510253906, 450.0172424316406)
    try: n.inputs[0].default_value = (1.0, 0.17247378826141357, 0.0, 1.0)
    except Exception: pass
    try: n.inputs[1].default_value = 16.69999885559082
    except Exception: pass
    try: n.inputs[2].default_value = 0.0
    except Exception: pass
    nodes_by_name['Emission'] = n
    try: nt.links.new(nodes_by_name['Emission'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass

    # --- emissivePurpleRadialGradient ---
    mat = bpy.data.materials.get('emissivePurpleRadialGradient') or bpy.data.materials.new('emissivePurpleRadialGradient')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (300.0, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeRGB')
    n.name = 'RGB'
    n.location = (45.696983337402344, 239.06565856933594)
    n.outputs[0].default_value = (0.4994472861289978, 0.18731802701950073, 1.0, 1.0)
    nodes_by_name['RGB'] = n
    n = nt.nodes.new('ShaderNodeEmission')
    n.name = 'Emission'
    n.location = (51.39771270751953, 388.82977294921875)
    try: n.inputs[0].default_value = (0.4755324125289917, 0.10525605082511902, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[1].default_value = 12.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.0
    except Exception: pass
    nodes_by_name['Emission'] = n
    try: nt.links.new(nodes_by_name['Emission'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass

    # --- emissiveWhiteRadialGradient ---
    mat = bpy.data.materials.get('emissiveWhiteRadialGradient') or bpy.data.materials.new('emissiveWhiteRadialGradient')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (300.0, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeRGB')
    n.name = 'RGB'
    n.location = (45.696983337402344, 239.06565856933594)
    n.outputs[0].default_value = (0.4994472861289978, 0.18731802701950073, 1.0, 1.0)
    nodes_by_name['RGB'] = n
    n = nt.nodes.new('ShaderNodeEmission')
    n.name = 'Emission'
    n.location = (51.39771270751953, 388.82977294921875)
    try: n.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[1].default_value = 8.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.0
    except Exception: pass
    nodes_by_name['Emission'] = n
    try: nt.links.new(nodes_by_name['Emission'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass

    # --- grass ---
    mat = bpy.data.materials.get('grass') or bpy.data.materials.new('grass')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (762.3067626953125, 509.7737121582031)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 1.0
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (1077.851318359375, 509.043701171875)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeRGB')
    n.name = 'RGB'
    n.location = (309.9255065917969, 212.5396728515625)
    n.outputs[0].default_value = (0.4161919951438904, 0.40170401334762573, 0.009488999843597412, 1.0)
    nodes_by_name['RGB'] = n
    n = nt.nodes.new('ShaderNodeRGB')
    n.name = 'RGB.001'
    n.location = (310.7077331542969, 425.5711669921875)
    n.outputs[0].default_value = (0.0911799967288971, 0.16469800472259521, 0.05682599917054176, 1.0)
    nodes_by_name['RGB.001'] = n
    n = nt.nodes.new('ShaderNodeUVMap')
    n.name = 'UV Map'
    n.location = (108.87852478027344, 579.2874755859375)
    n.width = 150.0
    try: n.uv_map = ''
    except Exception: pass
    try: n.from_instancer = False
    except Exception: pass
    nodes_by_name['UV Map'] = n
    n = nt.nodes.new('ShaderNodeSeparateXYZ')
    n.name = 'Separate XYZ'
    n.location = (315.8355712890625, 581.8182373046875)
    nodes_by_name['Separate XYZ'] = n
    n = nt.nodes.new('ShaderNodeMix')
    n.name = 'Mix'
    n.location = (545.1216430664062, 514.8388061523438)
    try: n.data_type = 'RGBA'
    except Exception: pass
    try: n.blend_type = 'MIX'
    except Exception: pass
    try: n.factor_mode = 'UNIFORM'
    except Exception: pass
    try: n.clamp_factor = True
    except Exception: pass
    try: n.clamp_result = False
    except Exception: pass
    try: n.inputs[1].default_value = (0.5, 0.5, 0.5)
    except Exception: pass
    try: n.inputs[2].default_value = 0.0
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    try: n.inputs[4].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[8].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[9].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Mix'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['UV Map'].outputs[0], nodes_by_name['Separate XYZ'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Separate XYZ'].outputs[1], nodes_by_name['Mix'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Mix'].outputs[2], nodes_by_name['Principled BSDF'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['RGB.001'].outputs[0], nodes_by_name['Mix'].inputs[6])
    except Exception: pass
    try: nt.links.new(nodes_by_name['RGB'].outputs[0], nodes_by_name['Mix'].inputs[7])
    except Exception: pass

    # --- gray ---
    mat = bpy.data.materials.get('gray') or bpy.data.materials.new('gray')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (10.0, 300.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[0].default_value = (0.2788924276828766, 0.23074033856391907, 0.1620294749736786, 1.0)
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (300.0, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass

    # --- green ---
    mat = bpy.data.materials.get('green') or bpy.data.materials.new('green')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (10.0, 300.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[0].default_value = (0.34191200137138367, 0.42869099974632263, 0.03310500085353851, 1.0)
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 1.0
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (300.0, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass

    # --- labCarpet ---
    mat = bpy.data.materials.get('labCarpet') or bpy.data.materials.new('labCarpet')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (10.0, 300.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (300.0, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture'
    n.location = (-359.4944152832031, 237.34707641601562)
    n.width = 240.0
    try: n.interpolation = 'Linear'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'REPEAT'
    except Exception: pass
    n.image = bpy.data.images.get('labCarpet.png')
    try: n.inputs[0].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Image Texture'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image Texture'].outputs[0], nodes_by_name['Principled BSDF'].inputs[0])
    except Exception: pass

    # --- mapAltar ---
    mat = bpy.data.materials.get('mapAltar') or bpy.data.materials.new('mapAltar')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (1482.418701171875, 515.6754760742188)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeUVMap')
    n.name = 'UV Map'
    n.location = (-447.10272216796875, 591.5139770507812)
    n.width = 150.0
    try: n.uv_map = ''
    except Exception: pass
    try: n.from_instancer = False
    except Exception: pass
    nodes_by_name['UV Map'] = n
    n = nt.nodes.new('ShaderNodeMix')
    n.name = 'Mix'
    n.location = (1320.3504638671875, 346.5047607421875)
    try: n.data_type = 'RGBA'
    except Exception: pass
    try: n.blend_type = 'MIX'
    except Exception: pass
    try: n.factor_mode = 'UNIFORM'
    except Exception: pass
    try: n.clamp_factor = True
    except Exception: pass
    try: n.clamp_result = False
    except Exception: pass
    try: n.inputs[1].default_value = (0.5, 0.5, 0.5)
    except Exception: pass
    try: n.inputs[2].default_value = 0.0
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    try: n.inputs[4].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[8].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[9].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Mix'] = n
    n = nt.nodes.new('ShaderNodeRGB')
    n.name = 'Color'
    n.location = (726.7630004882812, 477.9284973144531)
    n.outputs[0].default_value = (0.027212277054786682, 0.00788235291838646, 0.0, 1.0)
    nodes_by_name['Color'] = n
    n = nt.nodes.new('ShaderNodeRGB')
    n.name = 'Color.001'
    n.location = (722.1192626953125, 248.28378295898438)
    n.outputs[0].default_value = (1.0, 0.05380270630121231, 0.039327338337898254, 1.0)
    nodes_by_name['Color.001'] = n
    n = nt.nodes.new('ShaderNodeVectorMath')
    n.name = 'Vector Math'
    n.location = (1061.4075927734375, 183.0592041015625)
    try: n.operation = 'MULTIPLY'
    except Exception: pass
    try: n.inputs[1].default_value = (22.0, 22.0, 22.0)
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 1.0
    except Exception: pass
    nodes_by_name['Vector Math'] = n
    n = nt.nodes.new('ShaderNodeFloatCurve')
    n.name = 'Float Curve'
    n.location = (971.8075561523438, 805.9791259765625)
    n.width = 240.0
    try: n.inputs[0].default_value = 1.0
    except Exception: pass
    nodes_by_name['Float Curve'] = n
    n = nt.nodes.new('ShaderNodeSeparateXYZ')
    n.name = 'Separate XYZ'
    n.location = (-234.85009765625, 805.9791870117188)
    nodes_by_name['Separate XYZ'] = n
    n = nt.nodes.new('ShaderNodeMath')
    n.name = 'Math.002'
    n.location = (-36.82332229614258, 953.3148803710938)
    try: n.operation = 'SUBTRACT'
    except Exception: pass
    try: n.use_clamp = False
    except Exception: pass
    try: n.inputs[1].default_value = 0.5
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    nodes_by_name['Math.002'] = n
    n = nt.nodes.new('ShaderNodeMath')
    n.name = 'Math.003'
    n.location = (156.85118103027344, 959.8449096679688)
    try: n.operation = 'ABSOLUTE'
    except Exception: pass
    try: n.use_clamp = False
    except Exception: pass
    try: n.inputs[1].default_value = 0.5
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    nodes_by_name['Math.003'] = n
    n = nt.nodes.new('ShaderNodeMath')
    n.name = 'Math.004'
    n.location = (375.7510986328125, 946.7069091796875)
    try: n.operation = 'MULTIPLY'
    except Exception: pass
    try: n.use_clamp = False
    except Exception: pass
    try: n.inputs[1].default_value = 2.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    nodes_by_name['Math.004'] = n
    n = nt.nodes.new('ShaderNodeMath')
    n.name = 'Math.005'
    n.location = (-40.087501525878906, 786.7989501953125)
    try: n.operation = 'SUBTRACT'
    except Exception: pass
    try: n.use_clamp = False
    except Exception: pass
    try: n.inputs[1].default_value = 0.5
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    nodes_by_name['Math.005'] = n
    n = nt.nodes.new('ShaderNodeMath')
    n.name = 'Math.006'
    n.location = (153.58700561523438, 793.3289794921875)
    try: n.operation = 'ABSOLUTE'
    except Exception: pass
    try: n.use_clamp = False
    except Exception: pass
    try: n.inputs[1].default_value = 0.5
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    nodes_by_name['Math.006'] = n
    n = nt.nodes.new('ShaderNodeMath')
    n.name = 'Math.007'
    n.location = (372.4869079589844, 780.19091796875)
    try: n.operation = 'MULTIPLY'
    except Exception: pass
    try: n.use_clamp = False
    except Exception: pass
    try: n.inputs[1].default_value = 2.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    nodes_by_name['Math.007'] = n
    n = nt.nodes.new('ShaderNodeMath')
    n.name = 'Math.008'
    n.location = (579.0614013671875, 897.3358764648438)
    try: n.operation = 'MAXIMUM'
    except Exception: pass
    try: n.use_clamp = False
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    nodes_by_name['Math.008'] = n
    n = nt.nodes.new('ShaderNodeVectorMath')
    n.name = 'Vector Math.001'
    n.location = (-201.09970092773438, 556.5018310546875)
    try: n.operation = 'DISTANCE'
    except Exception: pass
    try: n.inputs[1].default_value = (0.5, 0.5, 0.0)
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 1.0
    except Exception: pass
    nodes_by_name['Vector Math.001'] = n
    try: nt.links.new(nodes_by_name['Color'].outputs[0], nodes_by_name['Mix'].inputs[6])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Vector Math'].outputs[0], nodes_by_name['Mix'].inputs[7])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Color.001'].outputs[0], nodes_by_name['Vector Math'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Float Curve'].outputs[0], nodes_by_name['Mix'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['UV Map'].outputs[0], nodes_by_name['Separate XYZ'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Separate XYZ'].outputs[0], nodes_by_name['Math.002'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Math.002'].outputs[0], nodes_by_name['Math.003'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Math.003'].outputs[0], nodes_by_name['Math.004'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Math.005'].outputs[0], nodes_by_name['Math.006'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Math.006'].outputs[0], nodes_by_name['Math.007'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Separate XYZ'].outputs[1], nodes_by_name['Math.005'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Math.004'].outputs[0], nodes_by_name['Math.008'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Math.007'].outputs[0], nodes_by_name['Math.008'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Mix'].outputs[2], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['UV Map'].outputs[0], nodes_by_name['Vector Math.001'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Vector Math.001'].outputs[1], nodes_by_name['Float Curve'].inputs[1])
    except Exception: pass

    # --- mapPortal ---
    mat = bpy.data.materials.get('mapPortal') or bpy.data.materials.new('mapPortal')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (1482.418701171875, 515.6754760742188)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeUVMap')
    n.name = 'UV Map'
    n.location = (-447.10272216796875, 591.5139770507812)
    n.width = 150.0
    try: n.uv_map = ''
    except Exception: pass
    try: n.from_instancer = False
    except Exception: pass
    nodes_by_name['UV Map'] = n
    n = nt.nodes.new('ShaderNodeMix')
    n.name = 'Mix'
    n.location = (1320.3504638671875, 346.5047607421875)
    try: n.data_type = 'RGBA'
    except Exception: pass
    try: n.blend_type = 'MIX'
    except Exception: pass
    try: n.factor_mode = 'UNIFORM'
    except Exception: pass
    try: n.clamp_factor = True
    except Exception: pass
    try: n.clamp_result = False
    except Exception: pass
    try: n.inputs[1].default_value = (0.5, 0.5, 0.5)
    except Exception: pass
    try: n.inputs[2].default_value = 0.0
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    try: n.inputs[4].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[8].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[9].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Mix'] = n
    n = nt.nodes.new('ShaderNodeRGB')
    n.name = 'Color'
    n.location = (721.3226928710938, 459.4266662597656)
    n.outputs[0].default_value = (0.007369596045464277, 0.0035670206416398287, 0.021980978548526764, 1.0)
    nodes_by_name['Color'] = n
    n = nt.nodes.new('ShaderNodeRGB')
    n.name = 'Color.001'
    n.location = (722.1192626953125, 248.28378295898438)
    n.outputs[0].default_value = (0.27530309557914734, 0.6433497667312622, 1.0, 1.0)
    nodes_by_name['Color.001'] = n
    n = nt.nodes.new('ShaderNodeVectorMath')
    n.name = 'Vector Math'
    n.location = (1061.4075927734375, 183.0592041015625)
    try: n.operation = 'MULTIPLY'
    except Exception: pass
    try: n.inputs[1].default_value = (10.0, 10.0, 10.0)
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 1.0
    except Exception: pass
    nodes_by_name['Vector Math'] = n
    n = nt.nodes.new('ShaderNodeFloatCurve')
    n.name = 'Float Curve'
    n.location = (971.8075561523438, 805.9791259765625)
    n.width = 240.0
    try: n.inputs[0].default_value = 1.0
    except Exception: pass
    nodes_by_name['Float Curve'] = n
    n = nt.nodes.new('ShaderNodeSeparateXYZ')
    n.name = 'Separate XYZ'
    n.location = (-234.85009765625, 805.9791870117188)
    nodes_by_name['Separate XYZ'] = n
    n = nt.nodes.new('ShaderNodeMath')
    n.name = 'Math.002'
    n.location = (-36.82332229614258, 953.3148803710938)
    try: n.operation = 'SUBTRACT'
    except Exception: pass
    try: n.use_clamp = False
    except Exception: pass
    try: n.inputs[1].default_value = 0.5
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    nodes_by_name['Math.002'] = n
    n = nt.nodes.new('ShaderNodeMath')
    n.name = 'Math.003'
    n.location = (156.85118103027344, 959.8449096679688)
    try: n.operation = 'ABSOLUTE'
    except Exception: pass
    try: n.use_clamp = False
    except Exception: pass
    try: n.inputs[1].default_value = 0.5
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    nodes_by_name['Math.003'] = n
    n = nt.nodes.new('ShaderNodeMath')
    n.name = 'Math.004'
    n.location = (375.7510986328125, 946.7069091796875)
    try: n.operation = 'MULTIPLY'
    except Exception: pass
    try: n.use_clamp = False
    except Exception: pass
    try: n.inputs[1].default_value = 2.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    nodes_by_name['Math.004'] = n
    n = nt.nodes.new('ShaderNodeMath')
    n.name = 'Math.005'
    n.location = (-40.087501525878906, 786.7989501953125)
    try: n.operation = 'SUBTRACT'
    except Exception: pass
    try: n.use_clamp = False
    except Exception: pass
    try: n.inputs[1].default_value = 0.5
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    nodes_by_name['Math.005'] = n
    n = nt.nodes.new('ShaderNodeMath')
    n.name = 'Math.006'
    n.location = (153.58700561523438, 793.3289794921875)
    try: n.operation = 'ABSOLUTE'
    except Exception: pass
    try: n.use_clamp = False
    except Exception: pass
    try: n.inputs[1].default_value = 0.5
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    nodes_by_name['Math.006'] = n
    n = nt.nodes.new('ShaderNodeMath')
    n.name = 'Math.007'
    n.location = (372.4869079589844, 780.19091796875)
    try: n.operation = 'MULTIPLY'
    except Exception: pass
    try: n.use_clamp = False
    except Exception: pass
    try: n.inputs[1].default_value = 2.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    nodes_by_name['Math.007'] = n
    n = nt.nodes.new('ShaderNodeMath')
    n.name = 'Math.008'
    n.location = (579.0614013671875, 897.3358764648438)
    try: n.operation = 'MAXIMUM'
    except Exception: pass
    try: n.use_clamp = False
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    nodes_by_name['Math.008'] = n
    try: nt.links.new(nodes_by_name['Color'].outputs[0], nodes_by_name['Mix'].inputs[6])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Vector Math'].outputs[0], nodes_by_name['Mix'].inputs[7])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Color.001'].outputs[0], nodes_by_name['Vector Math'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Float Curve'].outputs[0], nodes_by_name['Mix'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['UV Map'].outputs[0], nodes_by_name['Separate XYZ'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Separate XYZ'].outputs[0], nodes_by_name['Math.002'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Math.002'].outputs[0], nodes_by_name['Math.003'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Math.003'].outputs[0], nodes_by_name['Math.004'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Math.005'].outputs[0], nodes_by_name['Math.006'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Math.006'].outputs[0], nodes_by_name['Math.007'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Separate XYZ'].outputs[1], nodes_by_name['Math.005'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Math.004'].outputs[0], nodes_by_name['Math.008'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Math.007'].outputs[0], nodes_by_name['Math.008'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Math.008'].outputs[0], nodes_by_name['Float Curve'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Mix'].outputs[2], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass

    # --- palette ---
    mat = bpy.data.materials.get('palette') or bpy.data.materials.new('palette')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (-200.0, 100.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 1.0
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (200.0, 100.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture'
    n.location = (-570.0226440429688, 110.85371398925781)
    n.width = 240.0
    try: n.interpolation = 'Closest'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'REPEAT'
    except Exception: pass
    n.image = bpy.data.images.get('palette')
    try: n.inputs[0].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Image Texture'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image Texture'].outputs[0], nodes_by_name['Principled BSDF'].inputs[0])
    except Exception: pass

    # --- projectsCarpet ---
    mat = bpy.data.materials.get('projectsCarpet') or bpy.data.materials.new('projectsCarpet')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (10.0, 300.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (300.0, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture'
    n.location = (-359.4944152832031, 237.34707641601562)
    n.width = 240.0
    try: n.interpolation = 'Linear'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'REPEAT'
    except Exception: pass
    n.image = bpy.data.images.get('projectsCarpet.png')
    try: n.inputs[0].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Image Texture'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image Texture'].outputs[0], nodes_by_name['Principled BSDF'].inputs[0])
    except Exception: pass

    # --- projectsLabels ---
    mat = bpy.data.materials.get('projectsLabels') or bpy.data.materials.new('projectsLabels')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'BLEND'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (20.224624633789062, 300.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (310.22467041015625, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture'
    n.location = (-358.80810546875, 221.0803680419922)
    n.width = 240.0
    try: n.interpolation = 'Linear'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'REPEAT'
    except Exception: pass
    n.image = bpy.data.images.get('projectsLabels.png')
    try: n.inputs[0].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Image Texture'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image Texture'].outputs[0], nodes_by_name['Principled BSDF'].inputs[4])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image Texture'].outputs[0], nodes_by_name['Principled BSDF'].inputs[0])
    except Exception: pass

    # --- redGradient ---
    mat = bpy.data.materials.get('redGradient') or bpy.data.materials.new('redGradient')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (10.0, 300.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[0].default_value = (1.0, 0.04817177727818489, 0.0, 1.0)
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 1.0
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (300.0, 300.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass

    # --- stylizedMap ---
    mat = bpy.data.materials.get('stylizedMap') or bpy.data.materials.new('stylizedMap')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (-200.0, 100.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 1.0
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (200.0, 100.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture'
    n.location = (-570.0226440429688, 110.85371398925781)
    n.width = 240.0
    try: n.interpolation = 'Closest'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'REPEAT'
    except Exception: pass
    n.image = bpy.data.images.get('stylized-map.png')
    try: n.inputs[0].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Image Texture'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image Texture'].outputs[0], nodes_by_name['Principled BSDF'].inputs[0])
    except Exception: pass

    # --- terrain ---
    mat = bpy.data.materials.get('terrain') or bpy.data.materials.new('terrain')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (654.61328125, 1299.382080078125)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture'
    n.location = (-1525.037353515625, -318.5476989746094)
    n.width = 240.0
    try: n.interpolation = 'Linear'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'REPEAT'
    except Exception: pass
    n.image = bpy.data.images.get('terrain.png')
    try: n.inputs[0].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Image Texture'] = n
    n = nt.nodes.new('ShaderNodeRGB')
    n.name = 'RGB'
    n.location = (-1034.6031494140625, -30.623619079589844)
    n.outputs[0].default_value = (0.34191229939460754, 0.428691029548645, 0.03310488909482956, 1.0)
    nodes_by_name['RGB'] = n
    n = nt.nodes.new('ShaderNodeRGB')
    n.name = 'RGB.001'
    n.location = (-1029.6165771484375, 171.55587768554688)
    n.outputs[0].default_value = (1.0, 0.39675527811050415, 0.07618542015552521, 1.0)
    nodes_by_name['RGB.001'] = n
    n = nt.nodes.new('ShaderNodeRGB')
    n.name = 'RGB.002'
    n.location = (-508.1683654785156, 360.07598876953125)
    n.outputs[0].default_value = (0.10461651533842087, 0.539479672908783, 0.485150009393692, 1.0)
    nodes_by_name['RGB.002'] = n
    n = nt.nodes.new('ShaderNodeRGB')
    n.name = 'RGB.003'
    n.location = (-281.3335266113281, 600.885986328125)
    n.outputs[0].default_value = (0.006512092426419258, 0.0382043793797493, 0.11443541198968887, 1.0)
    nodes_by_name['RGB.003'] = n
    n = nt.nodes.new('ShaderNodeMix')
    n.name = 'Mix'
    n.location = (-748.6282958984375, 339.0909423828125)
    try: n.data_type = 'RGBA'
    except Exception: pass
    try: n.blend_type = 'MIX'
    except Exception: pass
    try: n.factor_mode = 'UNIFORM'
    except Exception: pass
    try: n.clamp_factor = True
    except Exception: pass
    try: n.clamp_result = False
    except Exception: pass
    try: n.inputs[1].default_value = (0.5, 0.5, 0.5)
    except Exception: pass
    try: n.inputs[2].default_value = 0.0
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    try: n.inputs[4].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[8].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[9].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Mix'] = n
    n = nt.nodes.new('ShaderNodeMapRange')
    n.name = 'Map Range'
    n.location = (-511.6192321777344, 847.5491943359375)
    try: n.inputs[1].default_value = 0.10000000149011612
    except Exception: pass
    try: n.inputs[2].default_value = 0.30000001192092896
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = 4.0
    except Exception: pass
    try: n.inputs[6].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[7].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[8].default_value = (1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[9].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[10].default_value = (1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[11].default_value = (4.0, 4.0, 4.0)
    except Exception: pass
    nodes_by_name['Map Range'] = n
    n = nt.nodes.new('ShaderNodeMix')
    n.name = 'Mix.001'
    n.location = (-284.1355285644531, 857.47900390625)
    try: n.data_type = 'RGBA'
    except Exception: pass
    try: n.blend_type = 'MIX'
    except Exception: pass
    try: n.factor_mode = 'UNIFORM'
    except Exception: pass
    try: n.clamp_factor = True
    except Exception: pass
    try: n.clamp_result = False
    except Exception: pass
    try: n.inputs[1].default_value = (0.5, 0.5, 0.5)
    except Exception: pass
    try: n.inputs[2].default_value = 0.0
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    try: n.inputs[4].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[8].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[9].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Mix.001'] = n
    n = nt.nodes.new('ShaderNodeMapRange')
    n.name = 'Map Range.001'
    n.location = (-280.6786804199219, 1112.75341796875)
    try: n.inputs[1].default_value = 0.30000001192092896
    except Exception: pass
    try: n.inputs[2].default_value = 1.0
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = 4.0
    except Exception: pass
    try: n.inputs[6].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[7].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[8].default_value = (1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[9].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[10].default_value = (1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[11].default_value = (4.0, 4.0, 4.0)
    except Exception: pass
    nodes_by_name['Map Range.001'] = n
    n = nt.nodes.new('ShaderNodeMix')
    n.name = 'Mix.002'
    n.location = (-98.22006225585938, 1111.9337158203125)
    try: n.data_type = 'RGBA'
    except Exception: pass
    try: n.blend_type = 'MIX'
    except Exception: pass
    try: n.factor_mode = 'UNIFORM'
    except Exception: pass
    try: n.clamp_factor = True
    except Exception: pass
    try: n.clamp_result = False
    except Exception: pass
    try: n.inputs[1].default_value = (0.5, 0.5, 0.5)
    except Exception: pass
    try: n.inputs[2].default_value = 0.0
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    try: n.inputs[4].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[8].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[9].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Mix.002'] = n
    n = nt.nodes.new('ShaderNodeRGB')
    n.name = 'RGB.004'
    n.location = (-763.466552734375, 74.8343276977539)
    n.outputs[0].default_value = (0.09117960929870605, 0.16469822824001312, 0.05682612210512161, 1.0)
    nodes_by_name['RGB.004'] = n
    n = nt.nodes.new('ShaderNodeMix')
    n.name = 'Mix.003'
    n.location = (-510.7373352050781, 600.7465209960938)
    try: n.data_type = 'RGBA'
    except Exception: pass
    try: n.blend_type = 'MIX'
    except Exception: pass
    try: n.factor_mode = 'UNIFORM'
    except Exception: pass
    try: n.clamp_factor = True
    except Exception: pass
    try: n.clamp_result = False
    except Exception: pass
    try: n.inputs[1].default_value = (0.5, 0.5, 0.5)
    except Exception: pass
    try: n.inputs[2].default_value = 0.0
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    try: n.inputs[4].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[8].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[9].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Mix.003'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture.001'
    n.location = (-1510.97900390625, 657.8955688476562)
    n.width = 240.0
    try: n.interpolation = 'Linear'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'REPEAT'
    except Exception: pass
    n.image = bpy.data.images.get('terrainGrass')
    try: n.inputs[0].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Image Texture.001'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture.002'
    n.location = (-1501.7259521484375, 974.2200317382812)
    n.width = 240.0
    try: n.interpolation = 'Linear'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'REPEAT'
    except Exception: pass
    n.image = bpy.data.images.get('terrainFurnitures')
    try: n.inputs[0].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Image Texture.002'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture.003'
    n.location = (-1514.0633544921875, 377.06103515625)
    n.width = 240.0
    try: n.interpolation = 'Linear'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'REPEAT'
    except Exception: pass
    n.image = bpy.data.images.get('terrainWater')
    try: n.inputs[0].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Image Texture.003'] = n
    n = nt.nodes.new('ShaderNodeSeparateColor')
    n.name = 'Separate Color.001'
    n.location = (-1234.5914306640625, 339.313720703125)
    try: n.mode = 'RGB'
    except Exception: pass
    nodes_by_name['Separate Color.001'] = n
    n = nt.nodes.new('ShaderNodeSeparateColor')
    n.name = 'Separate Color.002'
    n.location = (-1231.2569580078125, 629.5733642578125)
    try: n.mode = 'RGB'
    except Exception: pass
    nodes_by_name['Separate Color.002'] = n
    n = nt.nodes.new('ShaderNodeSeparateColor')
    n.name = 'Separate Color.003'
    n.location = (-1168.8343505859375, 914.6050415039062)
    try: n.mode = 'RGB'
    except Exception: pass
    nodes_by_name['Separate Color.003'] = n
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (374.1347351074219, 1296.447021484375)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeTexImage')
    n.name = 'Image Texture.004'
    n.location = (-761.89599609375, 1499.5169677734375)
    n.width = 240.0
    try: n.interpolation = 'Linear'
    except Exception: pass
    try: n.projection = 'FLAT'
    except Exception: pass
    try: n.extension = 'REPEAT'
    except Exception: pass
    n.image = bpy.data.images.get('slabs.png')
    nodes_by_name['Image Texture.004'] = n
    n = nt.nodes.new('ShaderNodeNewGeometry')
    n.name = 'Geometry'
    n.location = (-1151.279541015625, 1510.4947509765625)
    nodes_by_name['Geometry'] = n
    n = nt.nodes.new('ShaderNodeVectorMath')
    n.name = 'Vector Math'
    n.location = (-952.5772705078125, 1513.520263671875)
    try: n.operation = 'MULTIPLY'
    except Exception: pass
    try: n.inputs[1].default_value = (0.20000000298023224, 0.20000000298023224, 0.20000000298023224)
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 1.0
    except Exception: pass
    nodes_by_name['Vector Math'] = n
    n = nt.nodes.new('ShaderNodeMix')
    n.name = 'Mix.004'
    n.location = (138.77102661132812, 1297.9034423828125)
    try: n.data_type = 'RGBA'
    except Exception: pass
    try: n.blend_type = 'MIX'
    except Exception: pass
    try: n.factor_mode = 'UNIFORM'
    except Exception: pass
    try: n.clamp_factor = True
    except Exception: pass
    try: n.clamp_result = False
    except Exception: pass
    try: n.inputs[1].default_value = (0.5, 0.5, 0.5)
    except Exception: pass
    try: n.inputs[2].default_value = 0.0
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    try: n.inputs[4].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[8].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[9].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Mix.004'] = n
    n = nt.nodes.new('ShaderNodeMix')
    n.name = 'Mix.005'
    n.location = (-103.57536315917969, 1648.3218994140625)
    try: n.data_type = 'RGBA'
    except Exception: pass
    try: n.blend_type = 'MIX'
    except Exception: pass
    try: n.factor_mode = 'UNIFORM'
    except Exception: pass
    try: n.clamp_factor = True
    except Exception: pass
    try: n.clamp_result = False
    except Exception: pass
    try: n.inputs[1].default_value = (0.5, 0.5, 0.5)
    except Exception: pass
    try: n.inputs[2].default_value = 0.0
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    try: n.inputs[4].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = (0.39157015085220337, 0.18447518348693848, 0.1221388429403305, 1.0)
    except Exception: pass
    try: n.inputs[7].default_value = (1.0, 0.6239606738090515, 0.25818297266960144, 1.0)
    except Exception: pass
    try: n.inputs[8].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[9].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Mix.005'] = n
    try: nt.links.new(nodes_by_name['RGB.001'].outputs[0], nodes_by_name['Mix'].inputs[6])
    except Exception: pass
    try: nt.links.new(nodes_by_name['RGB'].outputs[0], nodes_by_name['Mix'].inputs[7])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Mix.003'].outputs[2], nodes_by_name['Mix.001'].inputs[6])
    except Exception: pass
    try: nt.links.new(nodes_by_name['RGB.002'].outputs[0], nodes_by_name['Mix.001'].inputs[7])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Map Range'].outputs[0], nodes_by_name['Mix.001'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Map Range.001'].outputs[0], nodes_by_name['Mix.002'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Mix.001'].outputs[2], nodes_by_name['Mix.002'].inputs[6])
    except Exception: pass
    try: nt.links.new(nodes_by_name['RGB.003'].outputs[0], nodes_by_name['Mix.002'].inputs[7])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Mix'].outputs[2], nodes_by_name['Mix.003'].inputs[6])
    except Exception: pass
    try: nt.links.new(nodes_by_name['RGB.004'].outputs[0], nodes_by_name['Mix.003'].inputs[7])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image Texture.002'].outputs[0], nodes_by_name['Separate Color.003'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image Texture.001'].outputs[0], nodes_by_name['Separate Color.002'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image Texture.003'].outputs[0], nodes_by_name['Separate Color.001'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Separate Color.001'].outputs[2], nodes_by_name['Map Range'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Separate Color.001'].outputs[2], nodes_by_name['Map Range.001'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Separate Color.002'].outputs[1], nodes_by_name['Mix'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Separate Color.002'].outputs[1], nodes_by_name['Mix.003'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Vector Math'].outputs[0], nodes_by_name['Image Texture.004'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Geometry'].outputs[0], nodes_by_name['Vector Math'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Mix.004'].outputs[2], nodes_by_name['Principled BSDF'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Separate Color.003'].outputs[0], nodes_by_name['Mix.004'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Mix.002'].outputs[2], nodes_by_name['Mix.004'].inputs[6])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image Texture.004'].outputs[0], nodes_by_name['Mix.005'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Mix.005'].outputs[2], nodes_by_name['Mix.004'].inputs[7])
    except Exception: pass

    # --- waterfall ---
    mat = bpy.data.materials.get('waterfall') or bpy.data.materials.new('waterfall')
    mat.use_fake_user = True
    mat.use_nodes = True
    mat.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    mat.metallic = 0.0
    mat.roughness = 0.4000000059604645
    try: mat.blend_method = 'HASHED'
    except Exception: pass
    try: mat.alpha_threshold = 0.5
    except Exception: pass
    try: mat.use_backface_culling = False
    except Exception: pass
    nt = mat.node_tree
    nt.nodes.clear()
    nodes_by_name = {}
    n = nt.nodes.new('ShaderNodeBsdfPrincipled')
    n.name = 'Principled BSDF'
    n.location = (-200.0, 100.0)
    n.width = 240.0
    try: n.distribution = 'MULTI_GGX'
    except Exception: pass
    try: n.subsurface_method = 'RANDOM_WALK'
    except Exception: pass
    try: n.inputs[0].default_value = (0.09572657942771912, 0.14451098442077637, 0.5077293515205383, 1.0)
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    try: n.inputs[3].default_value = 1.5
    except Exception: pass
    try: n.inputs[4].default_value = 1.0
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = 0.0
    except Exception: pass
    try: n.inputs[7].default_value = 0.0
    except Exception: pass
    try: n.inputs[8].default_value = 0.0
    except Exception: pass
    try: n.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    except Exception: pass
    try: n.inputs[10].default_value = 0.05000000074505806
    except Exception: pass
    try: n.inputs[11].default_value = 1.399999976158142
    except Exception: pass
    try: n.inputs[12].default_value = 0.0
    except Exception: pass
    try: n.inputs[13].default_value = 0.5
    except Exception: pass
    try: n.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[15].default_value = 0.0
    except Exception: pass
    try: n.inputs[16].default_value = 0.0
    except Exception: pass
    try: n.inputs[17].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[18].default_value = 0.0
    except Exception: pass
    try: n.inputs[19].default_value = 0.0
    except Exception: pass
    try: n.inputs[20].default_value = 0.029999999329447746
    except Exception: pass
    try: n.inputs[21].default_value = 1.5
    except Exception: pass
    try: n.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[23].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[24].default_value = 0.0
    except Exception: pass
    try: n.inputs[25].default_value = 0.5
    except Exception: pass
    try: n.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    except Exception: pass
    try: n.inputs[28].default_value = 0.0
    except Exception: pass
    try: n.inputs[29].default_value = 0.0
    except Exception: pass
    try: n.inputs[30].default_value = 1.3300000429153442
    except Exception: pass
    nodes_by_name['Principled BSDF'] = n
    n = nt.nodes.new('ShaderNodeOutputMaterial')
    n.name = 'Material Output'
    n.location = (200.0, 100.0)
    try: n.target = 'ALL'
    except Exception: pass
    try: n.is_active_output = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = 0.0
    except Exception: pass
    nodes_by_name['Material Output'] = n
    try: nt.links.new(nodes_by_name['Principled BSDF'].outputs[0], nodes_by_name['Material Output'].inputs[0])
    except Exception: pass

if __name__ == '__main__': run()