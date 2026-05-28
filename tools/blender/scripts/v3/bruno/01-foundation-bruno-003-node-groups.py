import bpy

def run():
    print('[03_node_groups] building node groups')
    if 'Auto Smooth' not in bpy.data.node_groups:
        bpy.data.node_groups.new('Auto Smooth', 'GeometryNodeTree')
    if 'Geometry Nodes' not in bpy.data.node_groups:
        bpy.data.node_groups.new('Geometry Nodes', 'GeometryNodeTree')
    if 'Geometry Nodes.001' not in bpy.data.node_groups:
        bpy.data.node_groups.new('Geometry Nodes.001', 'GeometryNodeTree')
    if 'Geometry Nodes.002' not in bpy.data.node_groups:
        bpy.data.node_groups.new('Geometry Nodes.002', 'GeometryNodeTree')
    if 'Smooth by Angle.001' not in bpy.data.node_groups:
        bpy.data.node_groups.new('Smooth by Angle.001', 'GeometryNodeTree')
    if 'Smooth by Angle.002' not in bpy.data.node_groups:
        bpy.data.node_groups.new('Smooth by Angle.002', 'GeometryNodeTree')
    if 'Smooth by Angle.003' not in bpy.data.node_groups:
        bpy.data.node_groups.new('Smooth by Angle.003', 'GeometryNodeTree')
    if 'terrain' not in bpy.data.node_groups:
        bpy.data.node_groups.new('terrain', 'CompositorNodeTree')
    if 'Smooth by Angle' not in bpy.data.node_groups:
        bpy.data.node_groups.new('Smooth by Angle', 'GeometryNodeTree')

    # --- Auto Smooth (GeometryNodeTree) ---
    nt = bpy.data.node_groups['Auto Smooth']
    nt.nodes.clear()
    nodes_by_name = {}
    sk = nt.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    sk = nt.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    sk = nt.interface.new_socket('Angle', in_out='INPUT', socket_type='NodeSocketFloat')
    try: sk.default_value = 0.0
    except Exception: pass
    n = nt.nodes.new('NodeGroupOutput')
    n.name = 'Group Output'
    n.location = (480.0, -100.0)
    nodes_by_name['Group Output'] = n
    n = nt.nodes.new('NodeGroupInput')
    n.name = 'Group Input'
    n.location = (-420.0, -300.0)
    nodes_by_name['Group Input'] = n
    n = nt.nodes.new('NodeGroupInput')
    n.name = 'Group Input.001'
    n.location = (-60.0, -100.0)
    nodes_by_name['Group Input.001'] = n
    n = nt.nodes.new('GeometryNodeSetShadeSmooth')
    n.name = 'Set Shade Smooth'
    n.location = (120.0, -100.0)
    try: n.domain = 'EDGE'
    except Exception: pass
    nodes_by_name['Set Shade Smooth'] = n
    n = nt.nodes.new('GeometryNodeSetShadeSmooth')
    n.name = 'Set Shade Smooth.001'
    n.location = (300.0, -100.0)
    try: n.domain = 'FACE'
    except Exception: pass
    try: n.inputs[1].default_value = True
    except Exception: pass
    try: n.inputs[2].default_value = True
    except Exception: pass
    nodes_by_name['Set Shade Smooth.001'] = n
    n = nt.nodes.new('GeometryNodeInputMeshEdgeAngle')
    n.name = 'Edge Angle'
    n.location = (-420.0, -220.0)
    nodes_by_name['Edge Angle'] = n
    n = nt.nodes.new('GeometryNodeInputEdgeSmooth')
    n.name = 'Is Edge Smooth'
    n.location = (-60.0, -160.0)
    nodes_by_name['Is Edge Smooth'] = n
    n = nt.nodes.new('GeometryNodeInputShadeSmooth')
    n.name = 'Is Face Smooth'
    n.location = (-240.0, -340.0)
    nodes_by_name['Is Face Smooth'] = n
    n = nt.nodes.new('FunctionNodeBooleanMath')
    n.name = 'Boolean Math'
    n.location = (-60.0, -220.0)
    nodes_by_name['Boolean Math'] = n
    n = nt.nodes.new('FunctionNodeCompare')
    n.name = 'Compare'
    n.location = (-240.0, -180.0)
    try: n.inputs[2].default_value = 0
    except Exception: pass
    try: n.inputs[3].default_value = 0
    except Exception: pass
    try: n.inputs[4].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    except Exception: pass
    try: n.inputs[7].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    except Exception: pass
    try: n.inputs[8].default_value = ''
    except Exception: pass
    try: n.inputs[9].default_value = ''
    except Exception: pass
    try: n.inputs[10].default_value = 0.8999999761581421
    except Exception: pass
    try: n.inputs[11].default_value = 0.08726649731397629
    except Exception: pass
    try: n.inputs[12].default_value = 0.0010000000474974513
    except Exception: pass
    nodes_by_name['Compare'] = n
    try: nt.links.new(nodes_by_name['Edge Angle'].outputs[0], nodes_by_name['Compare'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Set Shade Smooth.001'].outputs[0], nodes_by_name['Group Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Group Input'].outputs[1], nodes_by_name['Compare'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Compare'].outputs[0], nodes_by_name['Boolean Math'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Is Face Smooth'].outputs[0], nodes_by_name['Boolean Math'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Group Input.001'].outputs[0], nodes_by_name['Set Shade Smooth'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Is Edge Smooth'].outputs[0], nodes_by_name['Set Shade Smooth'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Set Shade Smooth'].outputs[0], nodes_by_name['Set Shade Smooth.001'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Boolean Math'].outputs[0], nodes_by_name['Set Shade Smooth'].inputs[2])
    except Exception: pass

    # --- Geometry Nodes (GeometryNodeTree) ---
    nt = bpy.data.node_groups['Geometry Nodes']
    nt.nodes.clear()
    nodes_by_name = {}
    sk = nt.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    sk = nt.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    n = nt.nodes.new('NodeGroupInput')
    n.name = 'Group Input'
    n.location = (130.52708435058594, -56.32093811035156)
    nodes_by_name['Group Input'] = n
    n = nt.nodes.new('NodeGroupOutput')
    n.name = 'Group Output'
    n.location = (498.783203125, -65.27698516845703)
    nodes_by_name['Group Output'] = n
    n = nt.nodes.new('GeometryNodeImageTexture')
    n.name = 'Image Texture'
    n.location = (-558.5320434570312, -159.46678161621094)
    n.width = 240.0
    try: n.inputs[0].default_value = bpy.data.images.get('terrainWater')
    except Exception: pass
    try: n.inputs[2].default_value = 0
    except Exception: pass
    nodes_by_name['Image Texture'] = n
    n = nt.nodes.new('FunctionNodeSeparateColor')
    n.name = 'Separate Color'
    n.location = (-267.82855224609375, -166.15911865234375)
    nodes_by_name['Separate Color'] = n
    n = nt.nodes.new('GeometryNodeInputNamedAttribute')
    n.name = 'Named Attribute'
    n.location = (-741.4432373046875, -162.8309326171875)
    try: n.data_type = 'FLOAT_VECTOR'
    except Exception: pass
    try: n.inputs[0].default_value = 'UVMap'
    except Exception: pass
    nodes_by_name['Named Attribute'] = n
    n = nt.nodes.new('GeometryNodeSetPosition')
    n.name = 'Set Position'
    n.location = (320.3641357421875, -63.04653549194336)
    try: n.inputs[1].default_value = True
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Set Position'] = n
    n = nt.nodes.new('ShaderNodeCombineXYZ')
    n.name = 'Combine XYZ'
    n.location = (134.8363494873047, -165.59832763671875)
    try: n.inputs[0].default_value = 0.0
    except Exception: pass
    try: n.inputs[1].default_value = 0.0
    except Exception: pass
    nodes_by_name['Combine XYZ'] = n
    n = nt.nodes.new('ShaderNodeMath')
    n.name = 'Math'
    n.location = (-56.560394287109375, -164.3095245361328)
    try: n.operation = 'MULTIPLY'
    except Exception: pass
    try: n.use_clamp = False
    except Exception: pass
    try: n.inputs[1].default_value = -1.5
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    nodes_by_name['Math'] = n
    try: nt.links.new(nodes_by_name['Set Position'].outputs[0], nodes_by_name['Group Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image Texture'].outputs[0], nodes_by_name['Separate Color'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Named Attribute'].outputs[0], nodes_by_name['Image Texture'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Group Input'].outputs[0], nodes_by_name['Set Position'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Math'].outputs[0], nodes_by_name['Combine XYZ'].inputs[2])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Combine XYZ'].outputs[0], nodes_by_name['Set Position'].inputs[3])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Separate Color'].outputs[0], nodes_by_name['Math'].inputs[0])
    except Exception: pass

    # --- Geometry Nodes.001 (GeometryNodeTree) ---
    nt = bpy.data.node_groups['Geometry Nodes.001']
    nt.nodes.clear()
    nodes_by_name = {}
    sk = nt.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    sk = nt.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    n = nt.nodes.new('NodeGroupInput')
    n.name = 'Group Input'
    n.location = (173.2432861328125, 292.37091064453125)
    nodes_by_name['Group Input'] = n
    n = nt.nodes.new('NodeGroupOutput')
    n.name = 'Group Output'
    n.location = (906.6412963867188, 520.7447509765625)
    nodes_by_name['Group Output'] = n
    n = nt.nodes.new('GeometryNodeMeshGrid')
    n.name = 'Grid'
    n.location = (-674.8223876953125, 479.3186950683594)
    try: n.inputs[0].default_value = 192.0
    except Exception: pass
    try: n.inputs[1].default_value = 192.0
    except Exception: pass
    try: n.inputs[2].default_value = 512
    except Exception: pass
    try: n.inputs[3].default_value = 512
    except Exception: pass
    nodes_by_name['Grid'] = n
    n = nt.nodes.new('GeometryNodeInstanceOnPoints')
    n.name = 'Instance on Points'
    n.location = (537.75341796875, 526.5955200195312)
    try: n.inputs[1].default_value = True
    except Exception: pass
    try: n.inputs[4].default_value = 0
    except Exception: pass
    try: n.inputs[5].default_value = (-0.9913469552993774, 0.0, 0.0)
    except Exception: pass
    nodes_by_name['Instance on Points'] = n
    n = nt.nodes.new('GeometryNodeImageTexture')
    n.name = 'Image Texture'
    n.location = (-383.2730712890625, 36.96678924560547)
    n.width = 240.0
    try: n.inputs[0].default_value = bpy.data.images.get('terrainGrass')
    except Exception: pass
    try: n.inputs[2].default_value = 0
    except Exception: pass
    nodes_by_name['Image Texture'] = n
    n = nt.nodes.new('FunctionNodeSeparateColor')
    n.name = 'Separate Color'
    n.location = (-99.09478759765625, 37.738548278808594)
    nodes_by_name['Separate Color'] = n
    n = nt.nodes.new('ShaderNodeMath')
    n.name = 'Math'
    n.location = (168.59654235839844, 147.46099853515625)
    try: n.operation = 'LESS_THAN'
    except Exception: pass
    try: n.use_clamp = False
    except Exception: pass
    try: n.inputs[1].default_value = 0.4000000059604645
    except Exception: pass
    try: n.inputs[2].default_value = 0.5
    except Exception: pass
    nodes_by_name['Math'] = n
    n = nt.nodes.new('GeometryNodeRealizeInstances')
    n.name = 'Realize Instances'
    n.location = (709.2031860351562, 521.5108032226562)
    try: n.inputs[1].default_value = True
    except Exception: pass
    try: n.inputs[2].default_value = True
    except Exception: pass
    try: n.inputs[3].default_value = 0
    except Exception: pass
    nodes_by_name['Realize Instances'] = n
    n = nt.nodes.new('GeometryNodeTransform')
    n.name = 'Transform Geometry'
    n.location = (357.55279541015625, 486.8039855957031)
    try: n.inputs[1].default_value = 'Components'
    except Exception: pass
    try: n.inputs[2].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[3].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[4].default_value = (1.0, 1.0, 1.0)
    except Exception: pass
    nodes_by_name['Transform Geometry'] = n
    n = nt.nodes.new('GeometryNodeDistributePointsOnFaces')
    n.name = 'Distribute Points on Faces'
    n.location = (26.535598754882812, 567.5331420898438)
    n.width = 170.0
    try: n.inputs[1].default_value = True
    except Exception: pass
    try: n.inputs[2].default_value = 0.0
    except Exception: pass
    try: n.inputs[3].default_value = 10.0
    except Exception: pass
    try: n.inputs[4].default_value = 10.0
    except Exception: pass
    try: n.inputs[5].default_value = 1.0
    except Exception: pass
    try: n.inputs[6].default_value = 0
    except Exception: pass
    nodes_by_name['Distribute Points on Faces'] = n
    try: nt.links.new(nodes_by_name['Realize Instances'].outputs[0], nodes_by_name['Group Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Transform Geometry'].outputs[0], nodes_by_name['Instance on Points'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Group Input'].outputs[0], nodes_by_name['Instance on Points'].inputs[2])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image Texture'].outputs[0], nodes_by_name['Separate Color'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Separate Color'].outputs[1], nodes_by_name['Math'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Math'].outputs[0], nodes_by_name['Instance on Points'].inputs[3])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Grid'].outputs[1], nodes_by_name['Image Texture'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Instance on Points'].outputs[0], nodes_by_name['Realize Instances'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Grid'].outputs[0], nodes_by_name['Distribute Points on Faces'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Distribute Points on Faces'].outputs[0], nodes_by_name['Transform Geometry'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Separate Color'].outputs[1], nodes_by_name['Instance on Points'].inputs[6])
    except Exception: pass

    # --- Geometry Nodes.002 (GeometryNodeTree) ---
    nt = bpy.data.node_groups['Geometry Nodes.002']
    nt.nodes.clear()
    nodes_by_name = {}
    sk = nt.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    sk = nt.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    n = nt.nodes.new('NodeGroupInput')
    n.name = 'Group Input'
    n.location = (-340.0, 0.0)
    nodes_by_name['Group Input'] = n
    n = nt.nodes.new('NodeGroupOutput')
    n.name = 'Group Output'
    n.location = (582.7945556640625, 0.0)
    nodes_by_name['Group Output'] = n
    n = nt.nodes.new('GeometryNodeCurveToPoints')
    n.name = 'Curve to Points'
    n.location = (19.794551849365234, 52.252357482910156)
    try: n.inputs[1].default_value = 233
    except Exception: pass
    try: n.inputs[2].default_value = 4.0
    except Exception: pass
    nodes_by_name['Curve to Points'] = n
    n = nt.nodes.new('GeometryNodeInstanceOnPoints')
    n.name = 'Instance on Points'
    n.location = (223.28512573242188, 210.17059326171875)
    try: n.inputs[1].default_value = True
    except Exception: pass
    try: n.inputs[3].default_value = False
    except Exception: pass
    try: n.inputs[4].default_value = 0
    except Exception: pass
    try: n.inputs[6].default_value = (1.0, 1.0, 1.0)
    except Exception: pass
    nodes_by_name['Instance on Points'] = n
    n = nt.nodes.new('GeometryNodeObjectInfo')
    n.name = 'Object Info'
    n.location = (-147.395263671875, -186.94735717773438)
    try: n.inputs[0].default_value = bpy.data.objects.get('archivePoleInstance')
    except Exception: pass
    try: n.inputs[1].default_value = False
    except Exception: pass
    nodes_by_name['Object Info'] = n
    n = nt.nodes.new('GeometryNodeRealizeInstances')
    n.name = 'Realize Instances'
    n.location = (403.0000305175781, 112.63874816894531)
    try: n.inputs[1].default_value = True
    except Exception: pass
    try: n.inputs[2].default_value = True
    except Exception: pass
    try: n.inputs[3].default_value = 0
    except Exception: pass
    nodes_by_name['Realize Instances'] = n
    n = nt.nodes.new('GeometryNodeMeshToCurve')
    n.name = 'Mesh to Curve'
    n.location = (-159.99998474121094, -41.165252685546875)
    try: n.inputs[1].default_value = True
    except Exception: pass
    nodes_by_name['Mesh to Curve'] = n
    try: nt.links.new(nodes_by_name['Mesh to Curve'].outputs[0], nodes_by_name['Curve to Points'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Realize Instances'].outputs[0], nodes_by_name['Group Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Curve to Points'].outputs[0], nodes_by_name['Instance on Points'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Object Info'].outputs[4], nodes_by_name['Instance on Points'].inputs[2])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Curve to Points'].outputs[3], nodes_by_name['Instance on Points'].inputs[5])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Instance on Points'].outputs[0], nodes_by_name['Realize Instances'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Group Input'].outputs[0], nodes_by_name['Mesh to Curve'].inputs[0])
    except Exception: pass

    # --- Smooth by Angle.001 (GeometryNodeTree) ---
    nt = bpy.data.node_groups['Smooth by Angle.001']
    nt.nodes.clear()
    nodes_by_name = {}
    sk = nt.interface.new_socket('Mesh', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    sk = nt.interface.new_socket('Mesh', in_out='INPUT', socket_type='NodeSocketGeometry')
    sk = nt.interface.new_socket('Angle', in_out='INPUT', socket_type='NodeSocketFloat')
    try: sk.default_value = 0.5235987901687622
    except Exception: pass
    sk = nt.interface.new_socket('Ignore Sharpness', in_out='INPUT', socket_type='NodeSocketBool')
    try: sk.default_value = False
    except Exception: pass
    n = nt.nodes.new('GeometryNodeSetShadeSmooth')
    n.name = 'Set Shade Smooth'
    n.location = (120.0, -80.0)
    try: n.domain = 'EDGE'
    except Exception: pass
    nodes_by_name['Set Shade Smooth'] = n
    n = nt.nodes.new('GeometryNodeSetShadeSmooth')
    n.name = 'Set Shade Smooth.001'
    n.location = (300.0, -80.0)
    try: n.domain = 'FACE'
    except Exception: pass
    try: n.inputs[1].default_value = True
    except Exception: pass
    try: n.inputs[2].default_value = True
    except Exception: pass
    nodes_by_name['Set Shade Smooth.001'] = n
    n = nt.nodes.new('NodeGroupOutput')
    n.name = 'Group Output'
    n.location = (480.0, -80.0)
    nodes_by_name['Group Output'] = n
    n = nt.nodes.new('GeometryNodeInputMeshEdgeAngle')
    n.name = 'Edge Angle'
    n.location = (-440.0, -240.0)
    nodes_by_name['Edge Angle'] = n
    n = nt.nodes.new('NodeGroupInput')
    n.name = 'Group Input'
    n.location = (-80.0, -80.0)
    nodes_by_name['Group Input'] = n
    n = nt.nodes.new('GeometryNodeInputEdgeSmooth')
    n.name = 'Is Edge Smooth'
    n.location = (-260.0, -120.0)
    nodes_by_name['Is Edge Smooth'] = n
    n = nt.nodes.new('GeometryNodeInputShadeSmooth')
    n.name = 'Is Shade Smooth'
    n.location = (-439.5191650390625, -396.6327819824219)
    nodes_by_name['Is Shade Smooth'] = n
    n = nt.nodes.new('FunctionNodeCompare')
    n.name = 'Compare'
    n.location = (-260.0, -260.0)
    try: n.inputs[2].default_value = 0
    except Exception: pass
    try: n.inputs[3].default_value = 0
    except Exception: pass
    try: n.inputs[4].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = (0.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[7].default_value = (0.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[8].default_value = ''
    except Exception: pass
    try: n.inputs[9].default_value = ''
    except Exception: pass
    try: n.inputs[10].default_value = 0.8999999761581421
    except Exception: pass
    try: n.inputs[11].default_value = 0.08726649731397629
    except Exception: pass
    try: n.inputs[12].default_value = 0.0010000000474974513
    except Exception: pass
    nodes_by_name['Compare'] = n
    n = nt.nodes.new('FunctionNodeBooleanMath')
    n.name = 'Boolean Math.001'
    n.location = (-80.0, -260.0)
    nodes_by_name['Boolean Math.001'] = n
    n = nt.nodes.new('NodeGroupInput')
    n.name = 'Group Input.001'
    n.location = (-439.5191650390625, -329.1396179199219)
    nodes_by_name['Group Input.001'] = n
    n = nt.nodes.new('NodeGroupInput')
    n.name = 'Group Input.002'
    n.location = (-259.0383605957031, -188.6585693359375)
    nodes_by_name['Group Input.002'] = n
    n = nt.nodes.new('FunctionNodeBooleanMath')
    n.name = 'Boolean Math'
    n.location = (-80.0, -149.1396026611328)
    nodes_by_name['Boolean Math'] = n
    n = nt.nodes.new('FunctionNodeBooleanMath')
    n.name = 'Boolean Math.002'
    n.location = (-260.0, -380.0)
    nodes_by_name['Boolean Math.002'] = n
    n = nt.nodes.new('NodeGroupInput')
    n.name = 'Group Input.003'
    n.location = (-440.0, -460.0)
    nodes_by_name['Group Input.003'] = n
    try: nt.links.new(nodes_by_name['Edge Angle'].outputs[0], nodes_by_name['Compare'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Set Shade Smooth.001'].outputs[0], nodes_by_name['Group Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Group Input.001'].outputs[1], nodes_by_name['Compare'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Compare'].outputs[0], nodes_by_name['Boolean Math.001'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Group Input'].outputs[0], nodes_by_name['Set Shade Smooth'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Set Shade Smooth'].outputs[0], nodes_by_name['Set Shade Smooth.001'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Boolean Math.001'].outputs[0], nodes_by_name['Set Shade Smooth'].inputs[2])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Group Input.002'].outputs[2], nodes_by_name['Boolean Math'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Is Edge Smooth'].outputs[0], nodes_by_name['Boolean Math'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Boolean Math'].outputs[0], nodes_by_name['Set Shade Smooth'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Group Input.003'].outputs[2], nodes_by_name['Boolean Math.002'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Is Shade Smooth'].outputs[0], nodes_by_name['Boolean Math.002'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Boolean Math.002'].outputs[0], nodes_by_name['Boolean Math.001'].inputs[1])
    except Exception: pass

    # --- Smooth by Angle.002 (GeometryNodeTree) ---
    nt = bpy.data.node_groups['Smooth by Angle.002']
    nt.nodes.clear()
    nodes_by_name = {}
    sk = nt.interface.new_socket('Mesh', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    sk = nt.interface.new_socket('Mesh', in_out='INPUT', socket_type='NodeSocketGeometry')
    sk = nt.interface.new_socket('Angle', in_out='INPUT', socket_type='NodeSocketFloat')
    try: sk.default_value = 0.5235987901687622
    except Exception: pass
    sk = nt.interface.new_socket('Ignore Sharpness', in_out='INPUT', socket_type='NodeSocketBool')
    try: sk.default_value = False
    except Exception: pass
    n = nt.nodes.new('GeometryNodeSetShadeSmooth')
    n.name = 'Set Shade Smooth'
    n.location = (120.0, -80.0)
    try: n.domain = 'EDGE'
    except Exception: pass
    nodes_by_name['Set Shade Smooth'] = n
    n = nt.nodes.new('GeometryNodeSetShadeSmooth')
    n.name = 'Set Shade Smooth.001'
    n.location = (300.0, -80.0)
    try: n.domain = 'FACE'
    except Exception: pass
    try: n.inputs[1].default_value = True
    except Exception: pass
    try: n.inputs[2].default_value = True
    except Exception: pass
    nodes_by_name['Set Shade Smooth.001'] = n
    n = nt.nodes.new('NodeGroupOutput')
    n.name = 'Group Output'
    n.location = (480.0, -80.0)
    nodes_by_name['Group Output'] = n
    n = nt.nodes.new('GeometryNodeInputMeshEdgeAngle')
    n.name = 'Edge Angle'
    n.location = (-440.0, -240.0)
    nodes_by_name['Edge Angle'] = n
    n = nt.nodes.new('NodeGroupInput')
    n.name = 'Group Input'
    n.location = (-80.0, -80.0)
    nodes_by_name['Group Input'] = n
    n = nt.nodes.new('GeometryNodeInputEdgeSmooth')
    n.name = 'Is Edge Smooth'
    n.location = (-260.0, -120.0)
    nodes_by_name['Is Edge Smooth'] = n
    n = nt.nodes.new('GeometryNodeInputShadeSmooth')
    n.name = 'Is Shade Smooth'
    n.location = (-439.5191650390625, -396.6327819824219)
    nodes_by_name['Is Shade Smooth'] = n
    n = nt.nodes.new('FunctionNodeCompare')
    n.name = 'Compare'
    n.location = (-260.0, -260.0)
    try: n.inputs[2].default_value = 0
    except Exception: pass
    try: n.inputs[3].default_value = 0
    except Exception: pass
    try: n.inputs[4].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = (0.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[7].default_value = (0.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[8].default_value = ''
    except Exception: pass
    try: n.inputs[9].default_value = ''
    except Exception: pass
    try: n.inputs[10].default_value = 0.8999999761581421
    except Exception: pass
    try: n.inputs[11].default_value = 0.08726649731397629
    except Exception: pass
    try: n.inputs[12].default_value = 0.0010000000474974513
    except Exception: pass
    nodes_by_name['Compare'] = n
    n = nt.nodes.new('FunctionNodeBooleanMath')
    n.name = 'Boolean Math.001'
    n.location = (-80.0, -260.0)
    nodes_by_name['Boolean Math.001'] = n
    n = nt.nodes.new('NodeGroupInput')
    n.name = 'Group Input.001'
    n.location = (-439.5191650390625, -329.1396179199219)
    nodes_by_name['Group Input.001'] = n
    n = nt.nodes.new('NodeGroupInput')
    n.name = 'Group Input.002'
    n.location = (-259.0383605957031, -188.6585693359375)
    nodes_by_name['Group Input.002'] = n
    n = nt.nodes.new('FunctionNodeBooleanMath')
    n.name = 'Boolean Math'
    n.location = (-80.0, -149.1396026611328)
    nodes_by_name['Boolean Math'] = n
    n = nt.nodes.new('FunctionNodeBooleanMath')
    n.name = 'Boolean Math.002'
    n.location = (-260.0, -380.0)
    nodes_by_name['Boolean Math.002'] = n
    n = nt.nodes.new('NodeGroupInput')
    n.name = 'Group Input.003'
    n.location = (-440.0, -460.0)
    nodes_by_name['Group Input.003'] = n
    try: nt.links.new(nodes_by_name['Edge Angle'].outputs[0], nodes_by_name['Compare'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Set Shade Smooth.001'].outputs[0], nodes_by_name['Group Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Group Input.001'].outputs[1], nodes_by_name['Compare'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Compare'].outputs[0], nodes_by_name['Boolean Math.001'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Group Input'].outputs[0], nodes_by_name['Set Shade Smooth'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Set Shade Smooth'].outputs[0], nodes_by_name['Set Shade Smooth.001'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Boolean Math.001'].outputs[0], nodes_by_name['Set Shade Smooth'].inputs[2])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Group Input.002'].outputs[2], nodes_by_name['Boolean Math'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Is Edge Smooth'].outputs[0], nodes_by_name['Boolean Math'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Boolean Math'].outputs[0], nodes_by_name['Set Shade Smooth'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Group Input.003'].outputs[2], nodes_by_name['Boolean Math.002'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Is Shade Smooth'].outputs[0], nodes_by_name['Boolean Math.002'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Boolean Math.002'].outputs[0], nodes_by_name['Boolean Math.001'].inputs[1])
    except Exception: pass

    # --- Smooth by Angle.003 (GeometryNodeTree) ---
    nt = bpy.data.node_groups['Smooth by Angle.003']
    nt.nodes.clear()
    nodes_by_name = {}
    sk = nt.interface.new_socket('Mesh', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    sk = nt.interface.new_socket('Mesh', in_out='INPUT', socket_type='NodeSocketGeometry')
    sk = nt.interface.new_socket('Angle', in_out='INPUT', socket_type='NodeSocketFloat')
    try: sk.default_value = 0.5235987901687622
    except Exception: pass
    sk = nt.interface.new_socket('Ignore Sharpness', in_out='INPUT', socket_type='NodeSocketBool')
    try: sk.default_value = False
    except Exception: pass
    n = nt.nodes.new('GeometryNodeSetShadeSmooth')
    n.name = 'Set Shade Smooth'
    n.location = (120.0, -80.0)
    try: n.domain = 'EDGE'
    except Exception: pass
    nodes_by_name['Set Shade Smooth'] = n
    n = nt.nodes.new('GeometryNodeSetShadeSmooth')
    n.name = 'Set Shade Smooth.001'
    n.location = (300.0, -80.0)
    try: n.domain = 'FACE'
    except Exception: pass
    try: n.inputs[1].default_value = True
    except Exception: pass
    try: n.inputs[2].default_value = True
    except Exception: pass
    nodes_by_name['Set Shade Smooth.001'] = n
    n = nt.nodes.new('NodeGroupOutput')
    n.name = 'Group Output'
    n.location = (480.0, -80.0)
    nodes_by_name['Group Output'] = n
    n = nt.nodes.new('GeometryNodeInputMeshEdgeAngle')
    n.name = 'Edge Angle'
    n.location = (-440.0, -240.0)
    nodes_by_name['Edge Angle'] = n
    n = nt.nodes.new('NodeGroupInput')
    n.name = 'Group Input'
    n.location = (-80.0, -80.0)
    nodes_by_name['Group Input'] = n
    n = nt.nodes.new('GeometryNodeInputEdgeSmooth')
    n.name = 'Is Edge Smooth'
    n.location = (-260.0, -120.0)
    nodes_by_name['Is Edge Smooth'] = n
    n = nt.nodes.new('GeometryNodeInputShadeSmooth')
    n.name = 'Is Shade Smooth'
    n.location = (-439.5191650390625, -396.6327819824219)
    nodes_by_name['Is Shade Smooth'] = n
    n = nt.nodes.new('FunctionNodeCompare')
    n.name = 'Compare'
    n.location = (-260.0, -260.0)
    try: n.inputs[2].default_value = 0
    except Exception: pass
    try: n.inputs[3].default_value = 0
    except Exception: pass
    try: n.inputs[4].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = (0.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[7].default_value = (0.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[8].default_value = ''
    except Exception: pass
    try: n.inputs[9].default_value = ''
    except Exception: pass
    try: n.inputs[10].default_value = 0.8999999761581421
    except Exception: pass
    try: n.inputs[11].default_value = 0.08726649731397629
    except Exception: pass
    try: n.inputs[12].default_value = 0.0010000000474974513
    except Exception: pass
    nodes_by_name['Compare'] = n
    n = nt.nodes.new('FunctionNodeBooleanMath')
    n.name = 'Boolean Math.001'
    n.location = (-80.0, -260.0)
    nodes_by_name['Boolean Math.001'] = n
    n = nt.nodes.new('NodeGroupInput')
    n.name = 'Group Input.001'
    n.location = (-439.5191650390625, -329.1396179199219)
    nodes_by_name['Group Input.001'] = n
    n = nt.nodes.new('NodeGroupInput')
    n.name = 'Group Input.002'
    n.location = (-259.0383605957031, -188.6585693359375)
    nodes_by_name['Group Input.002'] = n
    n = nt.nodes.new('FunctionNodeBooleanMath')
    n.name = 'Boolean Math'
    n.location = (-80.0, -149.1396026611328)
    nodes_by_name['Boolean Math'] = n
    n = nt.nodes.new('FunctionNodeBooleanMath')
    n.name = 'Boolean Math.002'
    n.location = (-260.0, -380.0)
    nodes_by_name['Boolean Math.002'] = n
    n = nt.nodes.new('NodeGroupInput')
    n.name = 'Group Input.003'
    n.location = (-440.0, -460.0)
    nodes_by_name['Group Input.003'] = n
    try: nt.links.new(nodes_by_name['Edge Angle'].outputs[0], nodes_by_name['Compare'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Set Shade Smooth.001'].outputs[0], nodes_by_name['Group Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Group Input.001'].outputs[1], nodes_by_name['Compare'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Compare'].outputs[0], nodes_by_name['Boolean Math.001'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Group Input'].outputs[0], nodes_by_name['Set Shade Smooth'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Set Shade Smooth'].outputs[0], nodes_by_name['Set Shade Smooth.001'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Boolean Math.001'].outputs[0], nodes_by_name['Set Shade Smooth'].inputs[2])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Group Input.002'].outputs[2], nodes_by_name['Boolean Math'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Is Edge Smooth'].outputs[0], nodes_by_name['Boolean Math'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Boolean Math'].outputs[0], nodes_by_name['Set Shade Smooth'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Group Input.003'].outputs[2], nodes_by_name['Boolean Math.002'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Is Shade Smooth'].outputs[0], nodes_by_name['Boolean Math.002'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Boolean Math.002'].outputs[0], nodes_by_name['Boolean Math.001'].inputs[1])
    except Exception: pass

    # --- terrain (CompositorNodeTree) ---
    nt = bpy.data.node_groups['terrain']
    nt.nodes.clear()
    nodes_by_name = {}
    sk = nt.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    try: sk.default_value = (0.0, 0.0, 0.0, 1.0)
    except Exception: pass
    sk = nt.interface.new_socket('Image', in_out='INPUT', socket_type='NodeSocketColor')
    try: sk.default_value = (0.0, 0.0, 0.0, 1.0)
    except Exception: pass
    n = nt.nodes.new('CompositorNodeImage')
    n.name = 'Image'
    n.location = (-222.05010986328125, 1132.1878662109375)
    nodes_by_name['Image'] = n
    n = nt.nodes.new('CompositorNodeImage')
    n.name = 'Image.001'
    n.location = (-380.79241943359375, 953.7112426757812)
    nodes_by_name['Image.001'] = n
    n = nt.nodes.new('CompositorNodeImage')
    n.name = 'Image.002'
    n.location = (-535.050537109375, 732.9610595703125)
    nodes_by_name['Image.002'] = n
    n = nt.nodes.new('CompositorNodeCombineColor')
    n.name = 'Combine Color'
    n.location = (-46.910858154296875, 657.26611328125)
    nodes_by_name['Combine Color'] = n
    n = nt.nodes.new('CompositorNodeImage')
    n.name = 'Image.003'
    n.location = (-715.0123291015625, 574.41357421875)
    nodes_by_name['Image.003'] = n
    n = nt.nodes.new('CompositorNodeSetAlpha')
    n.name = 'Set Alpha'
    n.location = (145.7672119140625, 652.789794921875)
    try: n.inputs[1].default_value = 1.0
    except Exception: pass
    try: n.inputs[2].default_value = 'Replace Alpha'
    except Exception: pass
    nodes_by_name['Set Alpha'] = n
    n = nt.nodes.new('NodeGroupOutput')
    n.name = 'Group Output'
    n.location = (305.7672119140625, 652.789794921875)
    nodes_by_name['Group Output'] = n
    try: nt.links.new(nodes_by_name['Combine Color'].outputs[0], nodes_by_name['Set Alpha'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image'].outputs[0], nodes_by_name['Combine Color'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image.001'].outputs[0], nodes_by_name['Combine Color'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image.002'].outputs[0], nodes_by_name['Combine Color'].inputs[2])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Image.003'].outputs[0], nodes_by_name['Combine Color'].inputs[3])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Set Alpha'].outputs[0], nodes_by_name['Group Output'].inputs[0])
    except Exception: pass

    # --- Smooth by Angle (GeometryNodeTree) ---
    nt = bpy.data.node_groups['Smooth by Angle']
    nt.nodes.clear()
    nodes_by_name = {}
    sk = nt.interface.new_socket('Mesh', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    sk = nt.interface.new_socket('Mesh', in_out='INPUT', socket_type='NodeSocketGeometry')
    sk = nt.interface.new_socket('Angle', in_out='INPUT', socket_type='NodeSocketFloat')
    try: sk.default_value = 0.5235987901687622
    except Exception: pass
    sk = nt.interface.new_socket('Ignore Sharpness', in_out='INPUT', socket_type='NodeSocketBool')
    try: sk.default_value = False
    except Exception: pass
    n = nt.nodes.new('GeometryNodeSetShadeSmooth')
    n.name = 'Set Shade Smooth'
    n.location = (120.0, -80.0)
    try: n.domain = 'EDGE'
    except Exception: pass
    nodes_by_name['Set Shade Smooth'] = n
    n = nt.nodes.new('GeometryNodeSetShadeSmooth')
    n.name = 'Set Shade Smooth.001'
    n.location = (300.0, -80.0)
    try: n.domain = 'FACE'
    except Exception: pass
    try: n.inputs[1].default_value = True
    except Exception: pass
    try: n.inputs[2].default_value = True
    except Exception: pass
    nodes_by_name['Set Shade Smooth.001'] = n
    n = nt.nodes.new('NodeGroupOutput')
    n.name = 'Group Output'
    n.location = (480.0, -80.0)
    nodes_by_name['Group Output'] = n
    n = nt.nodes.new('GeometryNodeInputMeshEdgeAngle')
    n.name = 'Edge Angle'
    n.location = (-440.0, -240.0)
    nodes_by_name['Edge Angle'] = n
    n = nt.nodes.new('NodeGroupInput')
    n.name = 'Group Input'
    n.location = (-80.0, -80.0)
    n.use_custom_color = True
    n.color = (0.5098000168800354, 0.20784400403499603, 0.2980409860610962)
    nodes_by_name['Group Input'] = n
    n = nt.nodes.new('GeometryNodeInputEdgeSmooth')
    n.name = 'Is Edge Smooth'
    n.location = (-260.0, -120.0)
    nodes_by_name['Is Edge Smooth'] = n
    n = nt.nodes.new('GeometryNodeInputShadeSmooth')
    n.name = 'Is Shade Smooth'
    n.location = (-439.5191650390625, -396.6327819824219)
    nodes_by_name['Is Shade Smooth'] = n
    n = nt.nodes.new('FunctionNodeCompare')
    n.name = 'Compare'
    n.location = (-260.0, -260.0)
    try: n.inputs[2].default_value = 0
    except Exception: pass
    try: n.inputs[3].default_value = 0
    except Exception: pass
    try: n.inputs[4].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[5].default_value = (0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[6].default_value = (0.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[7].default_value = (0.0, 0.0, 0.0, 0.0)
    except Exception: pass
    try: n.inputs[8].default_value = ''
    except Exception: pass
    try: n.inputs[9].default_value = ''
    except Exception: pass
    try: n.inputs[10].default_value = 0.8999999761581421
    except Exception: pass
    try: n.inputs[11].default_value = 0.08726649731397629
    except Exception: pass
    try: n.inputs[12].default_value = 0.0010000000474974513
    except Exception: pass
    nodes_by_name['Compare'] = n
    n = nt.nodes.new('FunctionNodeBooleanMath')
    n.name = 'Boolean Math.001'
    n.location = (-80.0, -260.0)
    nodes_by_name['Boolean Math.001'] = n
    n = nt.nodes.new('NodeGroupInput')
    n.name = 'Group Input.001'
    n.location = (-439.5191650390625, -329.1396179199219)
    n.use_custom_color = True
    n.color = (0.5098000168800354, 0.20784400403499603, 0.2980409860610962)
    nodes_by_name['Group Input.001'] = n
    n = nt.nodes.new('NodeGroupInput')
    n.name = 'Group Input.002'
    n.location = (-259.0383605957031, -188.6585693359375)
    n.use_custom_color = True
    n.color = (0.5098000168800354, 0.20784400403499603, 0.2980409860610962)
    nodes_by_name['Group Input.002'] = n
    n = nt.nodes.new('FunctionNodeBooleanMath')
    n.name = 'Boolean Math'
    n.location = (-80.0, -149.1396026611328)
    nodes_by_name['Boolean Math'] = n
    n = nt.nodes.new('FunctionNodeBooleanMath')
    n.name = 'Boolean Math.002'
    n.location = (-260.0, -380.0)
    nodes_by_name['Boolean Math.002'] = n
    n = nt.nodes.new('NodeGroupInput')
    n.name = 'Group Input.003'
    n.location = (-440.0, -460.0)
    n.use_custom_color = True
    n.color = (0.5098000168800354, 0.20784400403499603, 0.2980409860610962)
    nodes_by_name['Group Input.003'] = n
    try: nt.links.new(nodes_by_name['Edge Angle'].outputs[0], nodes_by_name['Compare'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Set Shade Smooth.001'].outputs[0], nodes_by_name['Group Output'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Group Input.001'].outputs[1], nodes_by_name['Compare'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Compare'].outputs[0], nodes_by_name['Boolean Math.001'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Group Input'].outputs[0], nodes_by_name['Set Shade Smooth'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Set Shade Smooth'].outputs[0], nodes_by_name['Set Shade Smooth.001'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Boolean Math.001'].outputs[0], nodes_by_name['Set Shade Smooth'].inputs[2])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Group Input.002'].outputs[2], nodes_by_name['Boolean Math'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Is Edge Smooth'].outputs[0], nodes_by_name['Boolean Math'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Boolean Math'].outputs[0], nodes_by_name['Set Shade Smooth'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Group Input.003'].outputs[2], nodes_by_name['Boolean Math.002'].inputs[1])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Is Shade Smooth'].outputs[0], nodes_by_name['Boolean Math.002'].inputs[0])
    except Exception: pass
    try: nt.links.new(nodes_by_name['Boolean Math.002'].outputs[0], nodes_by_name['Boolean Math.001'].inputs[1])
    except Exception: pass

if __name__ == '__main__': run()