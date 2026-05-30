import bpy, mathutils as _mu

def run():
    print('[99_finalize] parents + view layer + compositor + scene settings')

    # ----- parent relationships -----
    _o = bpy.data.objects.get('antenna')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('antennaHeadReference')
    if _o is not None:
        _o.parent = bpy.data.objects.get('antenna')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 0.6879448890686035), (-0.0, 1.0, -0.0, -0.38128378987312317), (0.0, 0.0, 1.0, -1.4936151504516602), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('at')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refAttributes')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, 0.5, 0.0, 8.272603988647461), (-0.5, 0.8660253882408142, -0.0, -32.93546676635742), (0.0, 0.0, 1.0, -2.5549123287200928), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('awwwards')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refDistinctions')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9848079681396484, 0.17364826798439026, -0.0, -34.72690200805664), (-0.17364826798439026, 0.9848079681396484, 0.0, 15.958059310913086), (-0.0, -0.0, 1.0, -0.9833912253379822), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('axle')
    if _o is not None:
        _o.parent = bpy.data.objects.get('antennaHead')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 0.6498498916625977), (-0.0, 1.0, -0.0, -0.3799999952316284), (0.0, 0.0, 1.0, -1.9514966011047363), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('backLights')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('backLights.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('baguiraMesh')
    if _o is not None:
        _o.parent = bpy.data.objects.get('baguira')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.1558645963668823, -1.496463166430421e-16, -2.332819528082377e-16, 13.156891822814941), (1.496463166430421e-16, 1.1558645963668823, 2.2690889721180325e-39, -63.47093963623047), (2.332819528082377e-16, -3.0202314310302894e-32, 1.1558645963668823, -1.6257846355438232), (-0.0, -0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('baguiraMesh.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('baguiraPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 12.991448402404785), (-0.0, 1.0, -0.0, -56.204349517822266), (0.0, 0.0, 1.0, -1.5329850912094116), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('baguiraPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('social')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -28.901012420654297), (-0.0, 1.0, -0.0, -21.8236141204834), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('ball')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cauldronPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 27.94952392578125), (-0.0, 1.0, -0.0, -19.96546173095703), (0.0, 0.0, 1.0, -0.6250946521759033), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('ball.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refBallPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 33.91387939453125), (-0.0, 1.0, -0.0, 36.97185516357422), (-0.0, 0.0, 1.0, -0.973094642162323), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('ball.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('eggPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.9898686408996582, -0.0, -0.0, -106.95083618164062), (-0.0, 1.9898686408996582, 0.0, 72.29326629638672), (-0.0, -0.0, 1.9898686408996582, -1.7812343835830688), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('ball.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('eggPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.9898686408996582, -0.0, -0.0, -106.95083618164062), (-0.0, 1.9898686408996582, 0.0, 72.29326629638672), (-0.0, -0.0, 1.9898686408996582, -1.7812343835830688), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('ball.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('eggPhysicalDynamic.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.9898686408996582, -0.0, -0.0, -106.95083618164062), (-0.0, 1.9898686408996582, 0.0, 72.29326629638672), (-0.0, -0.0, 1.9898686408996582, -1.7812343835830688), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('ball.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('eggPhysicalDynamic.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.9898686408996582, -0.0, -0.0, -106.95083618164062), (-0.0, 1.9898686408996582, 0.0, 72.29326629638672), (-0.0, -0.0, 1.9898686408996582, -1.7812343835830688), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('ball.006')
    if _o is not None:
        _o.parent = bpy.data.objects.get('eggPhysicalDynamic.004')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.9898686408996582, -0.0, -0.0, -106.95083618164062), (-0.0, 1.9898686408996582, 0.0, 72.29326629638672), (-0.0, -0.0, 1.9898686408996582, -1.7812343835830688), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('ball.007')
    if _o is not None:
        _o.parent = bpy.data.objects.get('eggPhysicalDynamic.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.9898686408996582, -0.0, -0.0, -106.95083618164062), (-0.0, 1.9898686408996582, 0.0, 72.29326629638672), (-0.0, -0.0, 1.9898686408996582, -1.7812343835830688), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('barPhysicalDynamic.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('base')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('base.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('base.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('base.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('base.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.004')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('base.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('base.006')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('base.007')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.007')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('base.008')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('base.009')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.009')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('base.010')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.010')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('base.011')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.011')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('base.012')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.012')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('base.013')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.013')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('base.014')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.014')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('base.015')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('base.016')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.015')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('base.017')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.016')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('basketPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('easter')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -53.7476806640625), (-0.0, 1.0, 0.0, 36.33066940307617), (-0.0, -0.0, 1.0, -0.8951517343521118), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('blackBoardPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('blackBoardPhysicalDynamic.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('blinkerLeft.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('blinkerLeft.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('blinkerRight.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('blinkerRight.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('blocks')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('blowerPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('blowerPhysicalDynamic.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cookie')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -12.2511625289917), (-0.0, 1.0, 0.0, 35.2508544921875), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('blueskyPhysicalDynamic.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('social')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -28.901012420654297), (-0.0, 1.0, -0.0, -21.8236141204834), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('body.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cauldronPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 44.29610824584961), (-0.0, 1.0, -0.0, -15.101877212524414), (0.0, 0.0, 1.0, -0.679256021976471), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('body.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('gamepadPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -16.111330032348633), (0.0, 1.0, 0.0, 1.3679430484771729), (0.0, -0.0, 1.0, -1.1724846363067627), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('body.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('body.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('body.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.013')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('body.006')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.012')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('body.007')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.011')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('body.008')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.010')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('body.009')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.009')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('body.010')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('body.011')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.007')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('body.012')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('body.013')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('body.014')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.004')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('body.015')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('bodyBlack.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('bodyPainted')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('bodyPainted.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('bodyPainted.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('boyMesh')
    if _o is not None:
        _o.parent = bpy.data.objects.get('boyPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 12.151752471923828), (-0.0, 1.0, -0.0, -54.49577331542969), (0.0, 0.0, 1.0, -1.532984972000122), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('boyPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('social')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -28.901012420654297), (-0.0, 1.0, -0.0, -21.8236141204834), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('brunoMesh.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bruno.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 19.124013900756836), (-0.0, 1.0, -0.0, 0.0), (0.0, 0.0, 1.0, -4.069920539855957), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('bumpersPhysicalFixed.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('careerText')
    if _o is not None:
        _o.parent = bpy.data.objects.get('stone')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 12.021645545959473), (-0.0, 1.0, -0.0, -30.739238739013672), (0.0, 0.0, 1.0, -0.0413644015789032), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('careerText.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('stone.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 12.021645545959473), (-0.0, 1.0, -0.0, -30.739238739013672), (0.0, 0.0, 1.0, -0.0413644015789032), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('careerText.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('stone.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 12.021645545959473), (-0.0, 1.0, -0.0, -30.739238739013672), (0.0, 0.0, 1.0, -0.0413644015789032), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('careerText.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('stone.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 12.021645545959473), (-0.0, 1.0, -0.0, -30.739238739013672), (0.0, 0.0, 1.0, -0.0413644015789032), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('careerText.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('stone.004')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 12.021645545959473), (-0.0, 1.0, -0.0, -30.739238739013672), (0.0, 0.0, 1.0, -0.0413644015789032), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('careerText.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('stone.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 12.021645545959473), (-0.0, 1.0, -0.0, -30.739238739013672), (0.0, 0.0, 1.0, -0.0413644015789032), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('carpet')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cauldronPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cell1.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cell1.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cell2.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cell2.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cell3.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cell3.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cellsCage.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cell1.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 0.0), (-0.0, 1.0, -0.0, 0.0), (0.0, 0.0, 1.0, -1.0762403011322021), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cellsCage.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cell2.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.0), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -1.1071759462356567), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cellsCage.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cell1.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 0.0), (-0.0, 1.0, -0.0, 0.0), (0.0, 0.0, 1.0, -1.0762403011322021), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cellsCage.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cell2.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.0), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -1.1071759462356567), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cellsCage.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cell3.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.0), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -1.1071759462356567), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cellsCage.006')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cell3.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.0), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -1.1071759462356567), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cellsEnergy.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cell1.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 0.0), (-0.0, 1.0, -0.0, 0.0), (0.0, 0.0, 1.0, -1.0762403011322021), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cellsEnergy.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cell2.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.0), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -1.1071759462356567), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cellsEnergy.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cell1.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 0.0), (-0.0, 1.0, -0.0, 0.0), (0.0, 0.0, 1.0, -1.0762403011322021), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cellsEnergy.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cell2.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.0), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -1.1071759462356567), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cellsEnergy.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cell3.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.0), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -1.1071759462356567), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cellsEnergy.006')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cell3.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.0), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -1.1071759462356567), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('chainPulleyArrayReference')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Circle.006')
    if _o is not None:
        _o.parent = bpy.data.objects.get('sideTablePhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8191520571708679, -0.5735764503479004, 0.0, 42.40606689453125), (0.5735764503479004, 0.8191520571708679, -0.0, 8.884500503540039), (0.0, 0.0, 1.0, -0.5333474278450012), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('common')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('common.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lightGeneratorPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -51.62207794189453), (-0.0, 1.0, -0.0, -18.26632308959961), (0.0, -0.0, 1.0, -1.8614680767059326), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('common.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lightGeneratorPhysicalDynamic.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -51.62207794189453), (-0.0, 1.0, -0.0, -18.26632308959961), (0.0, -0.0, 1.0, -1.8614680767059326), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('common.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cookiePhysicalFixed')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cookie')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -12.2511625289917), (-0.0, 1.0, 0.0, 35.2508544921875), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('couchPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('couchPhysicalDynamic.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('couchPhysicalDynamic.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('couchPhysicalDynamic.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cssda')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refDistinctions')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9848079681396484, 0.17364826798439026, -0.0, -34.72690200805664), (-0.17364826798439026, 0.9848079681396484, 0.0, 15.958059310913086), (-0.0, -0.0, 1.0, -0.9833912253379822), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refTvPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.50775146484375), (-0.0, 1.0, -0.0, -69.14649963378906), (0.0, 0.0, 1.0, -1.1553428173065186), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cookiePhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 2.1771774291992188), (-0.0, 1.0, -0.0, -27.35611915588379), (0.0, 0.0, 1.0, -1.6915301084518433), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('social')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -28.901012420654297), (-0.0, 1.0, -0.0, -21.8236141204834), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refTvPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.50775146484375), (-0.0, 1.0, -0.0, -69.14649963378906), (0.0, 0.0, 1.0, -1.1553428173065186), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.006')
    if _o is not None:
        _o.parent = bpy.data.objects.get('timeMachine')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.53236389160156), (-0.0, 1.0, -0.0, -67.39844512939453), (0.0, 0.0, 1.0, -3.2733685970306396), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.007')
    if _o is not None:
        _o.parent = bpy.data.objects.get('timeMachine')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.53236389160156), (-0.0, 1.0, -0.0, -67.39844512939453), (0.0, 0.0, 1.0, -3.2733685970306396), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.008')
    if _o is not None:
        _o.parent = bpy.data.objects.get('timeMachine')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.53236389160156), (-0.0, 1.0, -0.0, -67.39844512939453), (0.0, 0.0, 1.0, -3.2733685970306396), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.009')
    if _o is not None:
        _o.parent = bpy.data.objects.get('timeMachine')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.53236389160156), (-0.0, 1.0, -0.0, -67.39844512939453), (0.0, 0.0, 1.0, -3.2733685970306396), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cube.021')
    if _o is not None:
        _o.parent = bpy.data.objects.get('role')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, 0.5, 0.0, 8.131414413452148), (-0.5, 0.8660253882408142, 0.0, -32.79646301269531), (0.0, 0.0, 1.0, -3.313305377960205), (-0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('cube.023')
    if _o is not None:
        _o.parent = bpy.data.objects.get('inner.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660443782806396, 0.6427875757217407, 0.0, 9.405397415161133), (-0.6427875757217407, 0.7660443782806396, 0.0, -35.6238899230957), (0.0, 0.0, 1.0, -3.7142975330352783), (-0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('cube.024')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cube.026')
    if _o is not None:
        _o.parent = bpy.data.objects.get('with')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, 0.5, 0.0, 8.131414413452148), (-0.5, 0.8660253882408142, 0.0, -32.79646301269531), (0.0, 0.0, 1.0, -1.8272244930267334), (-0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('cube.033')
    if _o is not None:
        _o.parent = bpy.data.objects.get('at')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, 0.5, 0.0, 8.131414413452148), (-0.5, 0.8660253882408142, 0.0, -32.79646301269531), (0.0, 0.0, 1.0, -2.568195343017578), (-0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.036')
    if _o is not None:
        _o.parent = bpy.data.objects.get('antenna')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 0.6879448890686035), (-0.0, 1.0, -0.0, -0.38128378987312317), (0.0, 0.0, 1.0, -1.4936151504516602), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.048')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refTimer')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 53.291934967041016), (-0.0, 1.0, -0.0, -49.608760833740234), (0.0, 0.0, 1.0, -1.9830751419067383), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.054')
    if _o is not None:
        _o.parent = bpy.data.objects.get('blowerPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, -0.5, 0.0, 33.56097412109375), (0.5, 0.8660253882408142, 0.0, -1.710902214050293), (0.0, 0.0, 1.0, -0.5265605449676514), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.065')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.073')
    if _o is not None:
        _o.parent = bpy.data.objects.get('grinderPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, 0.5, 0.0, 7.615090370178223), (-0.5, 0.8660253882408142, -0.0, -30.908390045166016), (0.0, 0.0, 1.0, -0.9612043499946594), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.077')
    if _o is not None:
        _o.parent = bpy.data.objects.get('inner.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427875757217407, 0.0, 5.4031219482421875), (-0.6427875757217407, 0.7660444974899292, -0.0, -35.623870849609375), (0.0, 0.0, 1.0, -3.697094440460205), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.080')
    if _o is not None:
        _o.parent = bpy.data.objects.get('inner.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427875757217407, 0.0, 7.40006160736084), (-0.6427875757217407, 0.7660444974899292, -0.0, -35.49038314819336), (0.0, 0.0, 1.0, -3.4301838874816895), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.082')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refBlackBoard.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 30.20697593688965), (-0.0, 1.0, -0.0, -19.768173217773438), (0.0, 0.0, 1.0, -0.006079263985157013), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.088')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.089')
    if _o is not None:
        _o.parent = bpy.data.objects.get('achievements')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -70.5515365600586), (-0.0, 1.0, 0.0, 9.938889503479004), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.090')
    if _o is not None:
        _o.parent = bpy.data.objects.get('mainTablePhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 25.229873657226562), (-0.0, 1.0, -0.0, -20.01036262512207), (0.0, 0.0, 1.0, -0.5333474278450012), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.092')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refOvenPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, -0.5, 0.0, 33.56899642944336), (0.5, 0.8660253882408142, 0.0, -3.0404090881347656), (0.0, 0.0, 1.0, -0.5658632516860962), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.094')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refAnvilPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 22.37274932861328), (-0.0, 1.0, -0.0, -20.72515106201172), (0.0, 0.0, 1.0, -0.7425217032432556), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.100')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refBlackBoard.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 30.197139739990234), (-0.0, 1.0, -0.0, -19.999855041503906), (0.0, 0.0, 1.0, -0.006079263985157013), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.101')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refOvenPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, -0.5, 0.0, 33.56899642944336), (0.5, 0.8660253882408142, 0.0, -3.0404090881347656), (0.0, 0.0, 1.0, -0.5658632516860962), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.110')
    if _o is not None:
        _o.parent = bpy.data.objects.get('achievements')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -70.5515365600586), (-0.0, 1.0, 0.0, 9.938889503479004), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.121')
    if _o is not None:
        _o.parent = bpy.data.objects.get('blowerPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, -0.5, 0.0, 33.56097412109375), (0.5, 0.8660253882408142, 0.0, -1.710902214050293), (0.0, 0.0, 1.0, -0.5265605449676514), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.133')
    if _o is not None:
        _o.parent = bpy.data.objects.get('social')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -28.901012420654297), (-0.0, 1.0, -0.0, -21.8236141204834), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.135')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cookiePhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 2.1771774291992188), (-0.0, 1.0, -0.0, -27.35611915588379), (0.0, 0.0, 1.0, -1.6915301084518433), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.166')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refMini')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 41.129356384277344), (0.0, 1.0, 0.0, -18.678844451904297), (0.0, 0.0, 1.0, -2.700789213180542), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.173')
    if _o is not None:
        _o.parent = bpy.data.objects.get('altar')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -75.34408569335938), (-0.0, 1.0, -0.0, -27.94936180114746), (0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.177')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refScreenPhysicalKinematicPositionBased')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 32.43721008300781), (0.0, 1.0, -0.0, 27.827552795410156), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.178')
    if _o is not None:
        _o.parent = bpy.data.objects.get('inner.007')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427875757217407, 0.0, 7.40006160736084), (-0.6427875757217407, 0.7660444974899292, -0.0, -35.49038314819336), (0.0, 0.0, 1.0, -3.4301838874816895), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.180')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refScreenPhysicalKinematicPositionBased')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 32.43721008300781), (0.0, 1.0, -0.0, 27.827552795410156), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.182')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refScreenPhysicalKinematicPositionBased')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 32.43721008300781), (0.0, 1.0, -0.0, 27.827552795410156), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cube.183')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bridgePhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.47150495648384094, 0.881863534450531, 0.0, -16.988679885864258), (-0.881863534450531, 0.47150495648384094, -0.0, -0.012554647400975227), (0.0, -0.0, 1.0, 0.11670883744955063), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('blowerPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, -0.5, 0.0, 16.40443992614746), (0.5, 0.8660253882408142, -0.0, -17.610889434814453), (0.0, 0.0, 1.0, -0.5265605449676514), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('stoolPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -7.217398643493652), (-0.0, 1.0, 0.0, 78.09744262695312), (-0.0, -0.0, 1.0, -0.8157365918159485), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('stoolPhysicalDynamic.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -7.217398643493652), (-0.0, 1.0, 0.0, 78.09744262695312), (-0.0, -0.0, 1.0, -0.8157365918159485), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cookiePhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 27.796306610107422), (-0.0, 1.0, -0.0, -5.325170516967773), (0.0, 0.0, 1.0, -1.6915301084518433), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cookiePhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 27.796306610107422), (-0.0, 1.0, -0.0, -5.325170516967773), (0.0, 0.0, 1.0, -1.6915301084518433), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.006')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cookiePhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 27.796306610107422), (-0.0, 1.0, -0.0, -5.325170516967773), (0.0, 0.0, 1.0, -1.6915301084518433), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.007')
    if _o is not None:
        _o.parent = bpy.data.objects.get('fencePhysicalDynamic.013')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7317835092544556, 0.6815371513366699, 0.0, -7.1911444664001465), (-0.6815371513366699, 0.7317835092544556, -0.0, 0.09533357620239258), (0.0, -0.0, 1.0, -1.0418543815612793), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.008')
    if _o is not None:
        _o.parent = bpy.data.objects.get('tablePhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(3.1391647326017846e-07, -1.0, 0.0, -1.7365630865097046), (1.0, 3.1391647326017846e-07, -0.0, 25.41946029663086), (-0.0, 0.0, 1.0, -0.49444714188575745), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.009')
    if _o is not None:
        _o.parent = bpy.data.objects.get('phonePhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.6867039799690247, 0.7269372344017029, -7.450581485102248e-09, -17.351560592651367), (-0.7165263891220093, 0.6768693923950195, 0.168635293841362, 61.49517822265625), (0.12258728593587875, -0.11580253392457962, 0.9856785535812378, -11.04310131072998), (-0.0, -0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.010')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.009')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9407244920730591, -0.33917224407196045, 2.980233304583635e-08, -53.854732513427734), (0.29867202043533325, 0.8283934593200684, 0.47387707233428955, 10.167898178100586), (-0.16072596609592438, -0.4457877278327942, 0.8805912137031555, -9.188942909240723), (0.0, -0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.011')
    if _o is not None:
        _o.parent = bpy.data.objects.get('gamepadPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9016424417495728, -0.43248251080513, 7.450581485102248e-09, -14.432997703552246), (0.4256519377231598, 0.8874020576477051, -0.17702607810497284, -12.117087364196777), (0.07656067609786987, 0.1596142053604126, 0.9842062592506409, -2.8124489784240723), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.012')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.009')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9407244920730591, -0.33917224407196045, 2.980233304583635e-08, -53.854732513427734), (0.29867202043533325, 0.8283934593200684, 0.47387707233428955, 10.167898178100586), (-0.16072596609592438, -0.4457877278327942, 0.8805912137031555, -9.188942909240723), (0.0, -0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.013')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.021')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.34841537475586), (-0.0, 1.0, -0.0, -57.40055847167969), (0.0, 0.0, 1.0, -0.8098715543746948), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.014')
    if _o is not None:
        _o.parent = bpy.data.objects.get('benchPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9158047437667847, -0.0, -0.0, -18.43243408203125), (-0.0, 0.9158047437667847, 0.0, 31.259254455566406), (-0.0, -0.0, 0.9158047437667847, -0.6924270391464233), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.015')
    if _o is not None:
        _o.parent = bpy.data.objects.get('benchPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9158047437667847, -0.0, -0.0, -18.43243408203125), (-0.0, 0.9158047437667847, 0.0, 31.259254455566406), (-0.0, -0.0, 0.9158047437667847, -0.6924270391464233), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.016')
    if _o is not None:
        _o.parent = bpy.data.objects.get('benchPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9158047437667847, -0.0, -0.0, -18.43243408203125), (-0.0, 0.9158047437667847, 0.0, 31.259254455566406), (-0.0, -0.0, 0.9158047437667847, -0.6924270391464233), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.017')
    if _o is not None:
        _o.parent = bpy.data.objects.get('benchPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9158047437667847, -0.0, -0.0, -18.43243408203125), (-0.0, 0.9158047437667847, 0.0, 31.259254455566406), (-0.0, -0.0, 0.9158047437667847, -0.6924270391464233), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.018')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.009')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9407244920730591, -0.33917224407196045, 2.980233304583635e-08, -53.854732513427734), (0.29867202043533325, 0.8283934593200684, 0.47387707233428955, 10.167898178100586), (-0.16072596609592438, -0.4457877278327942, 0.8805912137031555, -9.188942909240723), (0.0, -0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.019')
    if _o is not None:
        _o.parent = bpy.data.objects.get('gizmoPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(7.549790126404332e-08, -1.0, 4.235164736271502e-22, 6.38986873626709), (7.549790126404332e-08, 5.699933306244206e-15, -1.0, 0.9245782494544983), (1.0, 7.549790126404332e-08, 7.549790126404332e-08, -16.187807083129883), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.020')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bridgePhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.47150495648384094, 0.881863534450531, 0.0, -16.988679885864258), (-0.881863534450531, 0.47150495648384094, -0.0, -0.012554647400975227), (0.0, -0.0, 1.0, 0.11670883744955063), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.021')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bridgePhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.47150495648384094, 0.881863534450531, 0.0, -16.988679885864258), (-0.881863534450531, 0.47150495648384094, -0.0, -0.012554647400975227), (0.0, -0.0, 1.0, 0.11670883744955063), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.022')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bridgePhysicalFixed.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(-0.311208039522171, -0.9503418207168579, 0.0, -7.318254470825195), (0.9503418207168579, -0.311208039522171, -0.0, 14.103553771972656), (-0.0, 0.0, 1.0, 0.11670888960361481), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.023')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bridgePhysicalFixed.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(-0.311208039522171, -0.9503418207168579, 0.0, -7.318254470825195), (0.9503418207168579, -0.311208039522171, -0.0, 14.103553771972656), (-0.0, 0.0, 1.0, 0.11670888960361481), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.024')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bridgePhysicalFixed.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(-0.311208039522171, -0.9503418207168579, 0.0, -7.318254470825195), (0.9503418207168579, -0.311208039522171, -0.0, 14.103553771972656), (-0.0, 0.0, 1.0, 0.11670888960361481), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.025')
    if _o is not None:
        _o.parent = bpy.data.objects.get('youtubePhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 8.214757919311523), (-0.0, 1.0, -0.0, -61.48014831542969), (0.0, 0.0, 1.0, -1.3187533617019653), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.026')
    if _o is not None:
        _o.parent = bpy.data.objects.get('xPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 5.267263412475586), (-0.0, 1.0, -0.0, -55.380550384521484), (0.0, 0.0, 1.0, -1.381777286529541), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.027')
    if _o is not None:
        _o.parent = bpy.data.objects.get('twitchPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 14.87314510345459), (-0.0, 1.0, -0.0, -63.082584381103516), (0.0, 0.0, 1.0, -1.4648783206939697), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.028')
    if _o is not None:
        _o.parent = bpy.data.objects.get('onlyfansPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078761100769, 0.4226183295249939, 0.0, -30.22110939025879), (-0.4226183295249939, 0.9063078761100769, -0.0, -63.667572021484375), (0.0, -0.0, 1.0, -1.3725606203079224), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.029')
    if _o is not None:
        _o.parent = bpy.data.objects.get('mailPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 11.401809692382812), (-0.0, 1.0, -0.0, -62.448055267333984), (0.0, 0.0, 1.0, -1.0587997436523438), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.030')
    if _o is not None:
        _o.parent = bpy.data.objects.get('mailPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 11.401809692382812), (-0.0, 1.0, -0.0, -62.448055267333984), (0.0, 0.0, 1.0, -1.0587997436523438), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.031')
    if _o is not None:
        _o.parent = bpy.data.objects.get('linkedInPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 20.237064361572266), (-0.0, 1.0, -0.0, -58.766326904296875), (0.0, 0.0, 1.0, -1.5351345539093018), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.032')
    if _o is not None:
        _o.parent = bpy.data.objects.get('discordPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 20.948291778564453), (-0.0, 1.0, -0.0, -55.41241455078125), (0.0, 0.0, 1.0, -1.5671449899673462), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.033')
    if _o is not None:
        _o.parent = bpy.data.objects.get('blueskyPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, 6.034337997436523), (-0.0, 5.52335052361741e-07, 1.0, -1.6397473812103271), (0.0, -1.0, 5.52335052361741e-07, 58.615726470947266), (0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.034')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refStatuePhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 13.120894432067871), (-0.0, 1.0, -0.0, -55.72157287597656), (0.0, 0.0, 1.0, -3.30832839012146), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.035')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refStatuePhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 13.120894432067871), (-0.0, 1.0, -0.0, -55.72157287597656), (0.0, 0.0, 1.0, -3.30832839012146), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.036')
    if _o is not None:
        _o.parent = bpy.data.objects.get('boyPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 12.151752471923828), (-0.0, 1.0, -0.0, -54.49577331542969), (0.0, 0.0, 1.0, -1.532984972000122), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.037')
    if _o is not None:
        _o.parent = bpy.data.objects.get('baguiraPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 12.991448402404785), (-0.0, 1.0, -0.0, -56.204349517822266), (0.0, 0.0, 1.0, -1.5329850912094116), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.038')
    if _o is not None:
        _o.parent = bpy.data.objects.get('baguiraPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 12.991448402404785), (-0.0, 1.0, -0.0, -56.204349517822266), (0.0, 0.0, 1.0, -1.5329850912094116), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.039')
    if _o is not None:
        _o.parent = bpy.data.objects.get('sudoPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.1558645963668823, -0.0, 0.0, 15.835517883300781), (-0.0, 1.1558645963668823, -0.0, -63.338401794433594), (0.0, 0.0, 1.1558645963668823, -1.771923303604126), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.040')
    if _o is not None:
        _o.parent = bpy.data.objects.get('sudoPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.1558645963668823, -0.0, 0.0, 15.835517883300781), (-0.0, 1.1558645963668823, -0.0, -63.338401794433594), (0.0, 0.0, 1.1558645963668823, -1.771923303604126), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.041')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 13.134831428527832), (-0.0, 1.0, -0.0, -55.3609504699707), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.042')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 13.134831428527832), (-0.0, 1.0, -0.0, -55.3609504699707), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.043')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 13.134831428527832), (-0.0, 1.0, -0.0, -55.3609504699707), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.044')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 13.134831428527832), (-0.0, 1.0, -0.0, -55.3609504699707), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.045')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 13.134831428527832), (-0.0, 1.0, -0.0, -55.3609504699707), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.046')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 13.134831428527832), (-0.0, 1.0, -0.0, -55.3609504699707), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.047')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 13.134831428527832), (-0.0, 1.0, -0.0, -55.3609504699707), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.048')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 13.134831428527832), (-0.0, 1.0, -0.0, -55.3609504699707), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.049')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 13.134831428527832), (-0.0, 1.0, -0.0, -55.3609504699707), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.050')
    if _o is not None:
        _o.parent = bpy.data.objects.get('benchPhysicalDynamic.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9158047437667847, -0.0, -0.0, -18.43243408203125), (-0.0, 0.9158047437667847, 0.0, 31.259254455566406), (-0.0, -0.0, 0.9158047437667847, -0.6924270391464233), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.051')
    if _o is not None:
        _o.parent = bpy.data.objects.get('mainTablePhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 2.4704689979553223), (-0.0, 1.0, -0.0, -25.117738723754883), (0.0, 0.0, 1.0, -0.5333474278450012), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.052')
    if _o is not None:
        _o.parent = bpy.data.objects.get('blowerPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, -0.5, 0.0, 16.40443992614746), (0.5, 0.8660253882408142, -0.0, -17.610889434814453), (0.0, 0.0, 1.0, -0.5265605449676514), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.053')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refOvenPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, -0.5, 0.0, 16.41246223449707), (0.5, 0.8660253882408142, -0.0, -18.84322738647461), (0.0, 0.0, 1.0, -0.5658632516860962), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.054')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refAnvilPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.38665521144866943), (-0.0, 1.0, -0.0, -25.8325252532959), (0.0, -0.0, 1.0, -0.7425217032432556), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.055')
    if _o is not None:
        _o.parent = bpy.data.objects.get('grinderPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, 0.5, 0.0, -14.648819923400879), (-0.5, 0.8660253882408142, -0.0, -23.951805114746094), (0.0, -0.0, 1.0, -0.9612043499946594), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.056')
    if _o is not None:
        _o.parent = bpy.data.objects.get('quenchPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -40.03736114501953), (-0.0, 1.0, 0.0, 7.570041656494141), (-0.0, -0.0, 1.0, -1.1520915031433105), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.057')
    if _o is not None:
        _o.parent = bpy.data.objects.get('blackBoardPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 7.447571277618408), (-0.0, 1.0, -0.0, -24.875547409057617), (0.0, 0.0, 1.0, -0.006079278886318207), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.058')
    if _o is not None:
        _o.parent = bpy.data.objects.get('blackBoardPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 7.447571277618408), (-0.0, 1.0, -0.0, -24.875547409057617), (0.0, 0.0, 1.0, -0.006079278886318207), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.059')
    if _o is not None:
        _o.parent = bpy.data.objects.get('benchPhysicalDynamic.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9158047437667847, -0.0, -0.0, -18.43243408203125), (-0.0, 0.9158047437667847, 0.0, 31.259254455566406), (-0.0, -0.0, 0.9158047437667847, -0.6924270391464233), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.060')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 2.3866066932678223), (-0.0, 1.0, -0.0, -25.117708206176758), (0.0, 0.0, 1.0, -5.97536563873291e-06), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.061')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 2.3866066932678223), (-0.0, 1.0, -0.0, -25.117708206176758), (0.0, 0.0, 1.0, -5.97536563873291e-06), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.062')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 2.3866066932678223), (-0.0, 1.0, -0.0, -25.117708206176758), (0.0, 0.0, 1.0, -5.97536563873291e-06), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.063')
    if _o is not None:
        _o.parent = bpy.data.objects.get('mainTablePhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 25.909557342529297), (-0.0, 1.0, -0.0, -20.579763412475586), (0.0, 0.0, 1.0, -0.533346951007843), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.064')
    if _o is not None:
        _o.parent = bpy.data.objects.get('blackBoardPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 30.09182357788086), (-0.0, 1.0, -0.0, -19.688919067382812), (0.0, 0.0, 1.0, -0.00607878714799881), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.065')
    if _o is not None:
        _o.parent = bpy.data.objects.get('blackBoardPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 30.09182357788086), (-0.0, 1.0, -0.0, -19.688919067382812), (0.0, 0.0, 1.0, -0.00607878714799881), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.066')
    if _o is not None:
        _o.parent = bpy.data.objects.get('sideTablePhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8191520571708679, -0.5735764503479004, 0.0, 31.74034881591797), (0.5735764503479004, 0.8191520571708679, -0.0, -4.393115043640137), (0.0, 0.0, 1.0, -0.533346951007843), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.067')
    if _o is not None:
        _o.parent = bpy.data.objects.get('benchPhysicalDynamic.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9158047437667847, -0.0, -0.0, -18.43243408203125), (-0.0, 0.9158047437667847, 0.0, 31.259254455566406), (-0.0, -0.0, 0.9158047437667847, -0.6924270391464233), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.068')
    if _o is not None:
        _o.parent = bpy.data.objects.get('benchPhysicalDynamic.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9158047437667847, -0.0, -0.0, -18.43243408203125), (-0.0, 0.9158047437667847, 0.0, 31.259254455566406), (-0.0, -0.0, 0.9158047437667847, -0.6924270391464233), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.069')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 25.895355224609375), (-0.0, 1.0, -0.0, -20.60811996459961), (0.0, 0.0, 1.0, -1.0036048889160156), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.070')
    if _o is not None:
        _o.parent = bpy.data.objects.get('benchPhysicalDynamic.004')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9158047437667847, -0.0, -0.0, -18.43243408203125), (-0.0, 0.9158047437667847, 0.0, 31.259254455566406), (-0.0, -0.0, 0.9158047437667847, -0.6924270391464233), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.071')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 25.895355224609375), (-0.0, 1.0, -0.0, -20.60811996459961), (0.0, 0.0, 1.0, -1.0036048889160156), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.072')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, -27.631092071533203), (0.0, 1.0, 0.0, -27.807859420776367), (0.0, 0.0, 1.0, -0.9431422352790833), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.073')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, -27.631092071533203), (0.0, 1.0, 0.0, -27.807859420776367), (0.0, 0.0, 1.0, -0.9431422352790833), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.074')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, -27.631092071533203), (0.0, 1.0, 0.0, -27.807859420776367), (0.0, 0.0, 1.0, -0.9431422352790833), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.075')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, -27.631092071533203), (0.0, 1.0, 0.0, -27.807859420776367), (0.0, 0.0, 1.0, -0.9431422352790833), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.076')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, -27.631092071533203), (0.0, 1.0, 0.0, -27.807859420776367), (0.0, 0.0, 1.0, -0.9431422352790833), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.077')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, -27.631092071533203), (0.0, 1.0, 0.0, -27.807859420776367), (0.0, 0.0, 1.0, -0.9431422352790833), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.078')
    if _o is not None:
        _o.parent = bpy.data.objects.get('benchPhysicalDynamic.004')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9158047437667847, -0.0, -0.0, -18.43243408203125), (-0.0, 0.9158047437667847, 0.0, 31.259254455566406), (-0.0, -0.0, 0.9158047437667847, -0.6924270391464233), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.079')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refCabinPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.965925931930542, 0.2588190734386444, 0.0, 18.661317825317383), (-0.2588190734386444, 0.965925931930542, -0.0, 13.827789306640625), (-0.0, 0.0, 1.0, -1.893534541130066), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.080')
    if _o is not None:
        _o.parent = bpy.data.objects.get('stoolPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.821792483329773, -0.5697867274284363, 0.0, -0.773553729057312), (0.5697867274284363, 0.821792483329773, -0.0, 22.998315811157227), (-0.0, 0.0, 1.0, -0.6590005159378052), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.081')
    if _o is not None:
        _o.parent = bpy.data.objects.get('benchPhysicalDynamic.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9158047437667847, -0.0, -0.0, -18.43243408203125), (-0.0, 0.9158047437667847, 0.0, 31.259254455566406), (-0.0, -0.0, 0.9158047437667847, -0.6924270391464233), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.087')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refFwaPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -26.021589279174805), (-0.0, 1.0, -0.0, -18.0481014251709), (0.0, -0.0, 1.0, -2.366135597229004), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.088')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refFwaPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -26.021589279174805), (-0.0, 1.0, -0.0, -18.0481014251709), (0.0, -0.0, 1.0, -2.366135597229004), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.089')
    if _o is not None:
        _o.parent = bpy.data.objects.get('basketPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 0.0), (0.0, 1.0, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.090')
    if _o is not None:
        _o.parent = bpy.data.objects.get('basketPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 0.0), (0.0, 1.0, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.091')
    if _o is not None:
        _o.parent = bpy.data.objects.get('basketPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 0.0), (0.0, 1.0, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.092')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refScreenPhysicalKinematicPositionBased')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 32.43721008300781), (-0.0, 1.0, -0.0, 32.000701904296875), (-0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.093')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refBumpersPhysicalKinematicPositionBased')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 32.124351501464844), (-0.0, 1.0, -0.0, 33.53919982910156), (-0.0, -0.0, 1.0, 0.819842517375946), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.094')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refBumpersPhysicalKinematicPositionBased')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 32.124351501464844), (-0.0, 1.0, -0.0, 33.53919982910156), (-0.0, -0.0, 1.0, 0.819842517375946), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.095')
    if _o is not None:
        _o.parent = bpy.data.objects.get('barPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -6.65526008605957), (-0.0, 1.0, 0.0, 75.9970703125), (-0.0, -0.0, 1.0, -1.006199598312378), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.096')
    if _o is not None:
        _o.parent = bpy.data.objects.get('couchPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 3.019916050561733e-07, 0.0, 46.92392349243164), (-3.019916050561733e-07, 1.0, -0.0, 28.65625), (-0.0, 0.0, 1.0, -1.1119685173034668), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.097')
    if _o is not None:
        _o.parent = bpy.data.objects.get('couchPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 3.019916050561733e-07, 0.0, 46.92392349243164), (-3.019916050561733e-07, 1.0, -0.0, 28.65625), (-0.0, 0.0, 1.0, -1.1119685173034668), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.098')
    if _o is not None:
        _o.parent = bpy.data.objects.get('tablePhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 45.094486236572266), (-0.0, 1.0, -0.0, 28.685636520385742), (-0.0, 0.0, 1.0, -1.1682040691375732), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.099')
    if _o is not None:
        _o.parent = bpy.data.objects.get('tablePhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 45.094486236572266), (-0.0, 1.0, -0.0, 28.685636520385742), (-0.0, 0.0, 1.0, -1.1682040691375732), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.100')
    if _o is not None:
        _o.parent = bpy.data.objects.get('stoolPhysicalDynamic.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -7.217398643493652), (-0.0, 1.0, 0.0, 78.09744262695312), (-0.0, -0.0, 1.0, -0.8157365918159485), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.101')
    if _o is not None:
        _o.parent = bpy.data.objects.get('couchPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 3.019916050561733e-07, 0.0, 46.92392349243164), (-3.019916050561733e-07, 1.0, -0.0, 28.65625), (-0.0, 0.0, 1.0, -1.1119685173034668), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.102')
    if _o is not None:
        _o.parent = bpy.data.objects.get('couchPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 3.019916050561733e-07, 0.0, 46.92392349243164), (-3.019916050561733e-07, 1.0, -0.0, 28.65625), (-0.0, 0.0, 1.0, -1.1119685173034668), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.103')
    if _o is not None:
        _o.parent = bpy.data.objects.get('tablePhysicalDynamic.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 45.094486236572266), (-0.0, 1.0, -0.0, 28.685636520385742), (-0.0, 0.0, 1.0, -1.1682040691375732), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.104')
    if _o is not None:
        _o.parent = bpy.data.objects.get('tablePhysicalDynamic.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 45.094486236572266), (-0.0, 1.0, -0.0, 28.685636520385742), (-0.0, 0.0, 1.0, -1.1682040691375732), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.105')
    if _o is not None:
        _o.parent = bpy.data.objects.get('couchPhysicalDynamic.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 3.019916050561733e-07, 0.0, 46.92392349243164), (-3.019916050561733e-07, 1.0, -0.0, 28.65625), (-0.0, 0.0, 1.0, -1.1119685173034668), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.106')
    if _o is not None:
        _o.parent = bpy.data.objects.get('couchPhysicalDynamic.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 3.019916050561733e-07, 0.0, 46.92392349243164), (-3.019916050561733e-07, 1.0, -0.0, 28.65625), (-0.0, 0.0, 1.0, -1.1119685173034668), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.107')
    if _o is not None:
        _o.parent = bpy.data.objects.get('couchPhysicalDynamic.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 3.019916050561733e-07, 0.0, 46.92392349243164), (-3.019916050561733e-07, 1.0, -0.0, 28.65625), (-0.0, 0.0, 1.0, -1.1119685173034668), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.108')
    if _o is not None:
        _o.parent = bpy.data.objects.get('couchPhysicalDynamic.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 3.019916050561733e-07, 0.0, 46.92392349243164), (-3.019916050561733e-07, 1.0, -0.0, 28.65625), (-0.0, 0.0, 1.0, -1.1119685173034668), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.109')
    if _o is not None:
        _o.parent = bpy.data.objects.get('stoolPhysicalDynamic.007')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -7.217398643493652), (-0.0, 1.0, 0.0, 78.09744262695312), (-0.0, -0.0, 1.0, -0.8157365918159485), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.110')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.012')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8587274551391602, -0.0, 0.0, 54.899654388427734), (-0.0, 0.8587274551391602, -0.0, -35.51558303833008), (0.0, 0.0, 0.8587274551391602, -0.5076327919960022), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.111')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lightGeneratorPhysicalDynamic.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.08715568482875824, 0.9961947202682495, 0.0, -13.15548038482666), (-0.9961947202682495, 0.08715568482875824, -0.0, 46.516605377197266), (0.0, -0.0, 1.0, -1.8614680767059326), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.112')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refJukeboxPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 25.274452209472656), (-0.0, 1.0, -0.0, 27.206775665283203), (-0.0, 0.0, 1.0, -1.4499417543411255), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.113')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.007')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 40.49323272705078), (-0.0, 1.0, -0.0, 36.959476470947266), (-0.0, 0.0, 1.0, -0.03489186242222786), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.114')
    if _o is not None:
        _o.parent = bpy.data.objects.get('fencePhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7317835092544556, 0.6815371513366699, 0.0, -7.1911444664001465), (-0.6815371513366699, 0.7317835092544556, -0.0, 0.09533357620239258), (0.0, -0.0, 1.0, -1.0418543815612793), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.115')
    if _o is not None:
        _o.parent = bpy.data.objects.get('fencePhysicalDynamic.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7317835092544556, 0.6815371513366699, 0.0, -7.1911444664001465), (-0.6815371513366699, 0.7317835092544556, -0.0, 0.09533357620239258), (0.0, -0.0, 1.0, -1.0418543815612793), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.116')
    if _o is not None:
        _o.parent = bpy.data.objects.get('fencePhysicalDynamic.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7317835092544556, 0.6815371513366699, 0.0, -7.1911444664001465), (-0.6815371513366699, 0.7317835092544556, -0.0, 0.09533357620239258), (0.0, -0.0, 1.0, -1.0418543815612793), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.117')
    if _o is not None:
        _o.parent = bpy.data.objects.get('fencePhysicalDynamic.004')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7317835092544556, 0.6815371513366699, 0.0, -7.1911444664001465), (-0.6815371513366699, 0.7317835092544556, -0.0, 0.09533357620239258), (0.0, -0.0, 1.0, -1.0418543815612793), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.118')
    if _o is not None:
        _o.parent = bpy.data.objects.get('fencePhysicalDynamic.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7317835092544556, 0.6815371513366699, 0.0, -7.1911444664001465), (-0.6815371513366699, 0.7317835092544556, -0.0, 0.09533357620239258), (0.0, 0.0, 1.0, -1.0418543815612793), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.119')
    if _o is not None:
        _o.parent = bpy.data.objects.get('fencePhysicalDynamic.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7317835092544556, 0.6815371513366699, 0.0, -7.1911444664001465), (-0.6815371513366699, 0.7317835092544556, -0.0, 0.09533357620239258), (0.0, -0.0, 1.0, -1.0418543815612793), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.120')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.021')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.34841537475586), (-0.0, 1.0, -0.0, -57.40055847167969), (0.0, 0.0, 1.0, -0.8098715543746948), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.121')
    if _o is not None:
        _o.parent = bpy.data.objects.get('fencePhysicalDynamic.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7317835092544556, 0.6815371513366699, 0.0, -7.1911444664001465), (-0.6815371513366699, 0.7317835092544556, -0.0, 0.09533357620239258), (0.0, -0.0, 1.0, -1.0418543815612793), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.122')
    if _o is not None:
        _o.parent = bpy.data.objects.get('fencePhysicalDynamic.009')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7317835092544556, 0.6815371513366699, 0.0, -7.1911444664001465), (-0.6815371513366699, 0.7317835092544556, -0.0, 0.09533357620239258), (0.0, -0.0, 1.0, -1.0418543815612793), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.123')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.022')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.34841537475586), (-0.0, 1.0, -0.0, -57.40055847167969), (0.0, 0.0, 1.0, -0.8098715543746948), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.124')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.022')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.34841537475586), (-0.0, 1.0, -0.0, -57.40055847167969), (0.0, 0.0, 1.0, -0.8098715543746948), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.125')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.023')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.34841537475586), (-0.0, 1.0, -0.0, -57.40055847167969), (0.0, 0.0, 1.0, -0.8098715543746948), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.126')
    if _o is not None:
        _o.parent = bpy.data.objects.get('fencePhysicalDynamic.007')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7317835092544556, 0.6815371513366699, 0.0, -7.1911444664001465), (-0.6815371513366699, 0.7317835092544556, -0.0, 0.09533357620239258), (0.0, -0.0, 1.0, -1.0418543815612793), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.127')
    if _o is not None:
        _o.parent = bpy.data.objects.get('fencePhysicalDynamic.010')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7317835092544556, 0.6815371513366699, 0.0, -7.1911444664001465), (-0.6815371513366699, 0.7317835092544556, -0.0, 0.09533357620239258), (0.0, -0.0, 1.0, -1.0418543815612793), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.128')
    if _o is not None:
        _o.parent = bpy.data.objects.get('fencePhysicalDynamic.015')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7317835092544556, 0.6815371513366699, 0.0, -7.1911444664001465), (-0.6815371513366699, 0.7317835092544556, -0.0, 0.09533357620239258), (0.0, -0.0, 1.0, -1.0418543815612793), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.129')
    if _o is not None:
        _o.parent = bpy.data.objects.get('fencePhysicalDynamic.011')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7317835092544556, 0.6815371513366699, 0.0, -7.1911444664001465), (-0.6815371513366699, 0.7317835092544556, -0.0, 0.09533357620239258), (0.0, -0.0, 1.0, -1.0418543815612793), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.130')
    if _o is not None:
        _o.parent = bpy.data.objects.get('fencePhysicalDynamic.017')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7317835092544556, 0.6815371513366699, 0.0, -7.1911444664001465), (-0.6815371513366699, 0.7317835092544556, -0.0, 0.09533357620239258), (0.0, -0.0, 1.0, -1.0418543815612793), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.131')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.004')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 64.37726593017578), (-0.0, 1.0, -0.0, -41.04517364501953), (0.0, 0.0, 1.0, -0.009999999776482582), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.132')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bumpersPhysicalFixed.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 119.94792175292969), (-0.0, 1.0, -0.0, 3.6904983520507812), (0.0, 0.0, 1.0, -0.009999999776482582), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.133')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bumpersPhysicalFixed.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 119.94792175292969), (-0.0, 1.0, -0.0, 3.6904983520507812), (0.0, 0.0, 1.0, -0.009999999776482582), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.134')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.020')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.34841537475586), (-0.0, 1.0, -0.0, -57.40055847167969), (0.0, 0.0, 1.0, -0.8098715543746948), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.135')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.020')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.34841537475586), (-0.0, 1.0, -0.0, -57.40055847167969), (0.0, 0.0, 1.0, -0.8098715543746948), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.136')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bumpersPhysicalFixed.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 119.94792175292969), (-0.0, 1.0, -0.0, 3.6904983520507812), (0.0, 0.0, 1.0, -0.009999999776482582), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.137')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bumpersPhysicalFixed.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 119.94792175292969), (-0.0, 1.0, -0.0, 3.6904983520507812), (0.0, 0.0, 1.0, -0.009999999776482582), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.138')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refRoadPhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.139')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refRoadPhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.140')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refRoadPhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.141')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refRoadPhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.142')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refRoadPhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.143')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refRoadPhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.144')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refRoadPhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.145')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refRoadPhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.146')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refRoadPhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.147')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refRoadPhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.148')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObstaclesPhysicalKinematicPositionBased.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 4.642963886260986), (-0.0, 1.0, -0.0, -117.50546264648438), (0.0, 0.0, 1.0, -2.193068265914917), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.149')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObstaclesPhysicalKinematicPositionBased.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 4.642963886260986), (-0.0, 1.0, -0.0, -117.50546264648438), (0.0, 0.0, 1.0, -2.193068265914917), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.150')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObstaclesPhysicalKinematicPositionBased.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 4.642963886260986), (-0.0, 1.0, -0.0, -117.50546264648438), (0.0, 0.0, 1.0, -2.193068265914917), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.151')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObstaclesPhysicalKinematicPositionBased.004')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 4.642963886260986), (-0.0, 1.0, -0.0, -117.50546264648438), (0.0, 0.0, 1.0, -2.193068265914917), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.152')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refRoadPhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.153')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObstaclesPhysicalKinematicPositionBased.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 4.642963886260986), (-0.0, 1.0, -0.0, -117.50546264648438), (0.0, 0.0, 1.0, -2.193068265914917), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.154')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObstaclesPhysicalKinematicPositionBased.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 4.642963886260986), (-0.0, 1.0, -0.0, -117.50546264648438), (0.0, 0.0, 1.0, -2.193068265914917), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.155')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refRoadPhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.156')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refRoadPhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.157')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.019')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.34841537475586), (-0.0, 1.0, -0.0, -57.40055847167969), (0.0, 0.0, 1.0, -0.8098715543746948), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.158')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.019')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.34841537475586), (-0.0, 1.0, -0.0, -57.40055847167969), (0.0, 0.0, 1.0, -0.8098715543746948), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.159')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.018')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.34841537475586), (-0.0, 1.0, -0.0, -57.40055847167969), (0.0, 0.0, 1.0, -0.8098715543746948), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.160')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.018')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.34841537475586), (-0.0, 1.0, -0.0, -57.40055847167969), (0.0, 0.0, 1.0, -0.8098715543746948), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.161')
    if _o is not None:
        _o.parent = bpy.data.objects.get('fencePhysicalDynamic.018')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7317835092544556, 0.6815371513366699, 0.0, -7.1911444664001465), (-0.6815371513366699, 0.7317835092544556, -0.0, 0.09533357620239258), (0.0, -0.0, 1.0, -1.0418543815612793), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.162')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.017')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.34841537475586), (-0.0, 1.0, -0.0, -57.40055847167969), (0.0, 0.0, 1.0, -0.8098715543746948), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.163')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.017')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.34841537475586), (-0.0, 1.0, -0.0, -57.40055847167969), (0.0, 0.0, 1.0, -0.8098715543746948), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.164')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.016')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.34841537475586), (-0.0, 1.0, -0.0, -57.40055847167969), (0.0, 0.0, 1.0, -0.8098715543746948), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.165')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.016')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.34841537475586), (-0.0, 1.0, -0.0, -57.40055847167969), (0.0, 0.0, 1.0, -0.8098715543746948), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.166')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.015')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.34841537475586), (-0.0, 1.0, -0.0, -57.40055847167969), (0.0, 0.0, 1.0, -0.8098715543746948), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.167')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.015')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.34841537475586), (-0.0, 1.0, -0.0, -57.40055847167969), (0.0, 0.0, 1.0, -0.8098715543746948), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.168')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.014')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.34841537475586), (-0.0, 1.0, -0.0, -57.40055847167969), (0.0, 0.0, 1.0, -0.8098715543746948), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.169')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.014')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.34841537475586), (-0.0, 1.0, -0.0, -57.40055847167969), (0.0, 0.0, 1.0, -0.8098715543746948), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.170')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.011')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8587274551391602, -0.0, 0.0, 54.899654388427734), (-0.0, 0.8587274551391602, -0.0, -35.51558303833008), (0.0, 0.0, 0.8587274551391602, -0.5076327919960022), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.171')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lightGeneratorPhysicalDynamic.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(-4.371138828673793e-08, 1.0, 0.0, -9.051231384277344), (-1.0, -4.371138828673793e-08, -0.0, 47.48617172241211), (0.0, -0.0, 1.0, -1.8614680767059326), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.172')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.013')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8587274551391602, -0.0, 0.0, 53.6700325012207), (-0.0, 0.8587274551391602, -0.0, -33.94409942626953), (0.0, 0.0, 0.8587274551391602, -0.37880823016166687), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.173')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.174')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.175')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.176')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.177')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.178')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.179')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.180')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.181')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.182')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.183')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.184')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.185')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.186')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.187')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refPodiumPhysicalFixed.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(7.549790126404332e-08, -1.0, 0.0, 21.84227752685547), (1.0, 7.549790126404332e-08, -0.0, 52.76458740234375), (0.0, 0.0, 1.0, -1.010000467300415), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.188')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refPodiumPhysicalFixed.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(7.549790126404332e-08, -1.0, 0.0, 21.84227752685547), (1.0, 7.549790126404332e-08, -0.0, 52.76458740234375), (0.0, 0.0, 1.0, -1.010000467300415), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.189')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refPodiumPhysicalFixed.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(7.549790126404332e-08, -1.0, 0.0, 21.84227752685547), (1.0, 7.549790126404332e-08, -0.0, 52.76458740234375), (0.0, 0.0, 1.0, -1.010000467300415), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.190')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refPodiumPhysicalFixed.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(7.549790126404332e-08, -1.0, 0.0, 21.84227752685547), (1.0, 7.549790126404332e-08, -0.0, 52.76458740234375), (0.0, 0.0, 1.0, -1.010000467300415), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.191')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.192')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.193')
    if _o is not None:
        _o.parent = bpy.data.objects.get('benchPhysicalDynamic.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9158047437667847, -0.0, -0.0, -18.43243408203125), (-0.0, 0.9158047437667847, 0.0, 31.259254455566406), (-0.0, -0.0, 0.9158047437667847, -0.6924270391464233), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.194')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lightGeneratorPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(-4.371138828673793e-08, 1.0, 0.0, -9.051231384277344), (-1.0, -4.371138828673793e-08, -0.0, 47.48617172241211), (0.0, -0.0, 1.0, -1.8614680767059326), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.195')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lightGeneratorPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(-4.371138828673793e-08, 1.0, 0.0, -9.051231384277344), (-1.0, -4.371138828673793e-08, -0.0, 47.48617172241211), (0.0, -0.0, 1.0, -1.8614680767059326), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.196')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lightGeneratorPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(-4.371138828673793e-08, 1.0, 0.0, -9.051231384277344), (-1.0, -4.371138828673793e-08, -0.0, 47.48617172241211), (0.0, -0.0, 1.0, -1.8614680767059326), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.197')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lightGeneratorPhysicalDynamic.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(-4.371138828673793e-08, 1.0, 0.0, -9.051231384277344), (-1.0, -4.371138828673793e-08, -0.0, 47.48617172241211), (0.0, -0.0, 1.0, -1.8614680767059326), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.198')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refTvPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.50775146484375), (-0.0, 1.0, -0.0, -69.14649963378906), (0.0, 0.0, 1.0, -1.1553428173065186), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.199')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refTvPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.50775146484375), (-0.0, 1.0, -0.0, -69.14649963378906), (0.0, 0.0, 1.0, -1.1553428173065186), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.200')
    if _o is not None:
        _o.parent = bpy.data.objects.get('fencePhysicalDynamic.012')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7317835092544556, 0.6815371513366699, 0.0, -7.1911444664001465), (-0.6815371513366699, 0.7317835092544556, -0.0, 0.09533357620239258), (0.0, -0.0, 1.0, -1.0418543815612793), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.201')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -69.664794921875), (-0.0, 1.0, 0.0, 12.41357707977295), (-0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.202')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -69.664794921875), (-0.0, 1.0, 0.0, 12.41357707977295), (-0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.203')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -69.664794921875), (-0.0, 1.0, 0.0, 12.41357707977295), (-0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.204')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -69.664794921875), (-0.0, 1.0, 0.0, 12.41357707977295), (-0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.205')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -69.664794921875), (-0.0, 1.0, 0.0, 12.41357707977295), (-0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.206')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -69.664794921875), (-0.0, 1.0, 0.0, 12.41357707977295), (-0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.207')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -69.664794921875), (-0.0, 1.0, 0.0, 12.41357707977295), (-0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.208')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -69.664794921875), (-0.0, 1.0, 0.0, 12.41357707977295), (-0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.209')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -69.664794921875), (-0.0, 1.0, 0.0, 12.41357707977295), (-0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.210')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -69.664794921875), (-0.0, 1.0, 0.0, 12.41357707977295), (-0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.211')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -69.664794921875), (-0.0, 1.0, 0.0, 12.41357707977295), (-0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.212')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -69.664794921875), (-0.0, 1.0, 0.0, 12.41357707977295), (-0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.213')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -69.664794921875), (-0.0, 1.0, 0.0, 12.41357707977295), (-0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.214')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -69.664794921875), (-0.0, 1.0, 0.0, 12.41357707977295), (-0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.215')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -69.664794921875), (-0.0, 1.0, 0.0, 12.41357707977295), (-0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.216')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -69.664794921875), (-0.0, 1.0, 0.0, 12.41357707977295), (-0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.217')
    if _o is not None:
        _o.parent = bpy.data.objects.get('benchPhysicalDynamic.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9158047437667847, -0.0, -0.0, -18.43243408203125), (-0.0, 0.9158047437667847, 0.0, 31.259254455566406), (-0.0, -0.0, 0.9158047437667847, -0.6924270391464233), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.218')
    if _o is not None:
        _o.parent = bpy.data.objects.get('benchPhysicalDynamic.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9158047437667847, -0.0, -0.0, -18.43243408203125), (-0.0, 0.9158047437667847, 0.0, 31.259254455566406), (-0.0, -0.0, 0.9158047437667847, -0.6924270391464233), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.219')
    if _o is not None:
        _o.parent = bpy.data.objects.get('stoolPhysicalDynamic.004')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7308138012886047, 0.6821148991584778, -0.0251074880361557, -4.83381986618042), (-0.6805515885353088, 0.7253209948539734, -0.10372556746006012, -84.5299301147461), (-0.052541762590408325, 0.09289103001356125, 0.9942890405654907, -9.98294734954834), (-0.0, -0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.220')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.010')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.53236389160156), (-0.0, 1.0, -0.0, -67.39844512939453), (0.0, 0.0, 1.0, -0.6883361339569092), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.221')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.010')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.53236389160156), (-0.0, 1.0, -0.0, -67.39844512939453), (0.0, 0.0, 1.0, -0.6883361339569092), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.222')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refLettersPhysicalDynamic.019')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078761100769, 0.4226183295249939, 0.0, 3.4328954219818115), (-0.4226183295249939, 0.9063078761100769, -7.105429898699844e-15, 4.8182597160339355), (-3.0028844757052373e-15, 6.4397064713876944e-15, 1.0, -0.7192147970199585), (-0.0, -0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.223')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refLettersPhysicalDynamic.018')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078761100769, 0.4226183295249939, -0.0, 2.074594497680664), (-0.4226183295249939, 0.9063078761100769, 0.0, 4.8182597160339355), (-0.0, -0.0, 1.0, -0.7192147970199585), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.224')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refLettersPhysicalDynamic.017')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078761100769, 0.4226183295249939, -0.0, 0.7304655909538269), (-0.4226183295249939, 0.9063078761100769, 0.0, 4.818260192871094), (-0.0, -0.0, 1.0, -0.703020453453064), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.225')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refLettersPhysicalDynamic.016')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078761100769, 0.4226183295249939, -0.0, -0.6824905276298523), (-0.4226183295249939, 0.9063078761100769, 0.0, 4.8182597160339355), (-0.0, -0.0, 1.0, -0.7192147970199585), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.226')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refLettersPhysicalDynamic.015')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078761100769, 0.4226183295249939, -0.0, -2.1581990718841553), (-0.4226183295249939, 0.9063078761100769, 0.0, 4.818260192871094), (-0.0, -0.0, 1.0, -0.7192147970199585), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.227')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refLettersPhysicalDynamic.013')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078761100769, 0.4226183295249939, -0.0, -4.852531909942627), (-0.4226183295249939, 0.9063078761100769, 0.0, 4.818260669708252), (-0.0, -0.0, 1.0, -0.7192147970199585), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.228')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refLettersPhysicalDynamic.014')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078761100769, 0.4226183295249939, -0.0, -3.906175136566162), (-0.4226183295249939, 0.9063078761100769, 0.0, 4.8182597160339355), (-0.0, -0.0, 1.0, -0.7192147970199585), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.229')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refLettersPhysicalDynamic.012')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078761100769, 0.4226183295249939, -0.0, -5.978036880493164), (-0.4226183295249939, 0.9063078761100769, 0.0, 4.818260192871094), (-0.0, -0.0, 1.0, -0.7192147970199585), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.230')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refLettersPhysicalDynamic.011')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078761100769, 0.4226183295249939, -0.0, -7.579253196716309), (-0.4226183295249939, 0.9063078761100769, 0.0, 4.818260669708252), (-0.0, -0.0, 1.0, -0.7192147970199585), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.231')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refLettersPhysicalDynamic.010')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078761100769, 0.4226183295249939, -0.0, -9.054959297180176), (-0.4226183295249939, 0.9063078761100769, 0.0, 4.8182597160339355), (-0.0, -0.0, 1.0, -0.7192147970199585), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.232')
    if _o is not None:
        _o.parent = bpy.data.objects.get('basketPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 0.0), (0.0, 1.0, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('cuboid.233')
    if _o is not None:
        _o.parent = bpy.data.objects.get('basketPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 0.0), (0.0, 1.0, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('cupPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('timeMachine')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.53236389160156), (-0.0, 1.0, -0.0, -67.39844512939453), (0.0, 0.0, 1.0, -3.2733685970306396), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cupPhysicalDynamic.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('timeMachine')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.53236389160156), (-0.0, 1.0, -0.0, -67.39844512939453), (0.0, 0.0, 1.0, -3.2733685970306396), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('cupPhysicalDynamic.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('timeMachine')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.53236389160156), (-0.0, 1.0, -0.0, -67.39844512939453), (0.0, 0.0, 1.0, -3.2733685970306396), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cylinder')
    if _o is not None:
        _o.parent = bpy.data.objects.get('timeMachine')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.53236389160156), (-0.0, 1.0, -0.0, -67.39844512939453), (0.0, 0.0, 1.0, -3.2733685970306396), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cylinder.008')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cylinder.012')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cylinder.022')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cylinder.031')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refGrinder')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, 0.5, 0.0, 7.615090370178223), (-0.5, 0.8660253882408142, -0.0, -30.908390045166016), (0.0, 0.0, 1.0, -0.9612043499946594), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cylinder.037')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Cylinder.039')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('digit0')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refYear')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 16.046842575073242), (-0.0, 1.0, -0.0, -33.675926208496094), (0.0, 0.0, 1.0, -0.07861466705799103), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('digit0.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refYear')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 16.046842575073242), (-0.0, 1.0, -0.0, -33.675926208496094), (0.0, 0.0, 1.0, -0.07861466705799103), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('digit0.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refYear')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 16.046842575073242), (-0.0, 1.0, -0.0, -33.675926208496094), (0.0, 0.0, 1.0, -0.07861466705799103), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('digit0.006')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refYear')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 16.046842575073242), (-0.0, 1.0, -0.0, -33.675926208496094), (0.0, 0.0, 1.0, -0.07861466705799103), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('discordPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('social')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -28.901012420654297), (-0.0, 1.0, -0.0, -21.8236141204834), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('eggPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('easter')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -53.7476806640625), (-0.0, 1.0, 0.0, 36.33066940307617), (-0.0, -0.0, 1.0, -0.8951517343521118), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('eggPhysicalDynamic.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('easter')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -53.7476806640625), (-0.0, 1.0, 0.0, 36.33066940307617), (-0.0, -0.0, 1.0, -0.8951517343521118), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('eggPhysicalDynamic.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('easter')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -53.7476806640625), (-0.0, 1.0, 0.0, 36.33066940307617), (-0.0, -0.0, 1.0, -0.8951517343521118), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('eggPhysicalDynamic.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('easter')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -53.7476806640625), (-0.0, 1.0, 0.0, 36.33066940307617), (-0.0, -0.0, 1.0, -0.8951517343521118), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('eggPhysicalDynamic.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('easter')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -53.7476806640625), (-0.0, 1.0, 0.0, 36.33066940307617), (-0.0, -0.0, 1.0, -0.8951517343521118), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('eggPhysicalDynamic.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('easter')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -53.7476806640625), (-0.0, 1.0, 0.0, 36.33066940307617), (-0.0, -0.0, 1.0, -0.8951517343521118), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('emissive.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('barPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -6.65526008605957), (-0.0, 1.0, 0.0, 75.9970703125), (-0.0, -0.0, 1.0, -1.006199598312378), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('emissive.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lightGeneratorPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -51.62207794189453), (-0.0, 1.0, -0.0, -18.26632308959961), (0.0, -0.0, 1.0, -1.8614680767059326), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('emissive.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lightGeneratorPhysicalDynamic.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -51.62207794189453), (-0.0, 1.0, -0.0, -18.26632308959961), (0.0, -0.0, 1.0, -1.8614680767059326), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('energy.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('energy.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('fwa')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refDistinctions')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9848079681396484, 0.17364826798439026, -0.0, -34.72690200805664), (-0.17364826798439026, 0.9848079681396484, 0.0, 15.958059310913086), (-0.0, -0.0, 1.0, -0.9833912253379822), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('gamepadPhysicalDynamic.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('gitHubPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('social')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -28.901012420654297), (-0.0, 1.0, -0.0, -21.8236141204834), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('gizmoPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('glass.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('glass.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('glass.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('glass.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.004')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('glass.006')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('glass.007')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('glass.008')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.007')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('glass.009')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('glass.010')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.009')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('glass.011')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.010')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('glass.012')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.011')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('glass.013')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.012')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('glass.014')
    if _o is not None:
        _o.parent = bpy.data.objects.get('poleLight.013')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -36.124229431152344), (-0.0, 1.0, 0.0, 40.54395294189453), (-0.0, -0.0, 1.0, -1.7487437725067139), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('grinderPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('headlights.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('headlights.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('headlights.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('hull')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 13.134831428527832), (-0.0, 1.0, -0.0, -55.3609504699707), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('hull.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('basaltRocksPhysicalStatic.004')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -79.80693054199219), (-0.0, 1.0, -0.0, -0.33034515380859375), (0.0, -0.0, 1.0, -0.7268602848052979), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('hull.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('basaltRocksPhysicalStatic.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -59.56986618041992), (-0.0, 1.0, 0.0, 8.163019180297852), (-0.0, -0.0, 1.0, -1.315825343132019), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('hull.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -69.664794921875), (-0.0, 1.0, 0.0, 12.41357707977295), (-0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('hull.011')
    if _o is not None:
        _o.parent = bpy.data.objects.get('basaltRocksPhysicalStatic.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 2.1197738647460938), (-0.0, 1.0, -0.0, 8.017854690551758), (-0.0, -0.0, 1.0, 0.48030030727386475), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('hull.012')
    if _o is not None:
        _o.parent = bpy.data.objects.get('basaltRocksPhysicalStatic.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 2.1197738647460938), (-0.0, 1.0, -0.0, 8.017854690551758), (-0.0, -0.0, 1.0, 0.48030030727386475), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('hull.013')
    if _o is not None:
        _o.parent = bpy.data.objects.get('basaltRocksPhysicalStatic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -12.454404830932617), (-0.0, 1.0, -0.0, -23.058090209960938), (0.0, -0.0, 1.0, 0.6500133275985718), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('hull.014')
    if _o is not None:
        _o.parent = bpy.data.objects.get('basaltRocksPhysicalStatic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -12.454404830932617), (-0.0, 1.0, -0.0, -23.058090209960938), (0.0, -0.0, 1.0, 0.6500133275985718), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('hull.015')
    if _o is not None:
        _o.parent = bpy.data.objects.get('basaltRocksPhysicalStatic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 15.267191886901855), (-0.0, 1.0, -0.0, -7.711810111999512), (0.0, -0.0, 1.0, 0.7747273445129395), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('hull.016')
    if _o is not None:
        _o.parent = bpy.data.objects.get('basaltRocksPhysicalStatic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 15.267191886901855), (-0.0, 1.0, -0.0, -7.711810111999512), (0.0, -0.0, 1.0, 0.7747273445129395), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('image')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refMini')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 41.129356384277344), (0.0, 1.0, 0.0, -18.678844451904297), (0.0, 0.0, 1.0, -2.700789213180542), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('inner')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refPagination')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427875757217407, 0.0, 7.373540878295898), (-0.6427875757217407, 0.7660444974899292, -0.0, -35.33338928222656), (0.0, 0.0, 1.0, -0.5842220187187195), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('inner.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refNext')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427875757217407, 0.0, 5.245940208435059), (-0.6427875757217407, 0.7660444974899292, 0.0, -35.62387466430664), (0.0, 0.0, 1.0, -3.6854190826416016), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('inner.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refPrevious')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.766044557094574, 0.6427876353263855, 0.0, 9.696937561035156), (-0.6427876353263855, 0.766044557094574, -0.0, -35.62387466430664), (0.0, 0.0, 1.0, -3.702622652053833), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('inner.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refTitle')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427875757217407, 0.0, 7.40006160736084), (-0.6427875757217407, 0.7660444974899292, -0.0, -35.49038314819336), (0.0, 0.0, 1.0, -3.4301838874816895), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('inner.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refUrl')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427875757217407, 0.0, 7.401689529418945), (-0.6427875757217407, 0.7660444974899292, -0.0, -35.41754913330078), (0.0, 0.0, 1.0, -3.0517988204956055), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('inner.006')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refUrl.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427875757217407, 0.0, 7.401689529418945), (-0.6427875757217407, 0.7660444974899292, -0.0, -35.41754913330078), (0.0, 0.0, 1.0, -3.0517988204956055), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('inner.007')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refTitle.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427875757217407, 0.0, 7.40006160736084), (-0.6427875757217407, 0.7660444974899292, -0.0, -35.49038314819336), (0.0, 0.0, 1.0, -3.4301838874816895), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('intersect')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refMini')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.866025447845459, 0.49999991059303284, 0.0, 26.756439208984375), (-0.49999991059303284, 0.866025447845459, 0.0, -37.59203338623047), (0.0, 0.0, 1.0, -2.8408772945404053), (-0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('jump')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('lava')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cookiePhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 2.1771774291992188), (-0.0, 1.0, -0.0, -27.35611915588379), (0.0, 0.0, 1.0, -1.6915301084518433), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('light')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('light.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('light.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('light.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('light.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.004')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('light.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('light.006')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('light.007')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.007')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('light.008')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('light.009')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.009')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('light.010')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.010')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('light.011')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.011')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('light.012')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.012')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('light.013')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.013')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('light.014')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.014')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('light.015')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.015')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('light.016')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lantern.016')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9063078165054321, -0.42261824011802673, -0.0, -76.07438659667969), (0.42261824011802673, 0.9063078165054321, -0.0, 14.908336639404297), (-0.0, -0.0, 1.0, -1.9549851417541504), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('lightGeneratorPhysicalDynamic.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('behindTheScene')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -52.45521545410156), (-0.0, 1.0, -0.0, -11.959333419799805), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('lightGeneratorPhysicalDynamic.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('behindTheScene')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -52.45521545410156), (-0.0, 1.0, -0.0, -11.959333419799805), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('linkedInPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('social')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -28.901012420654297), (-0.0, 1.0, -0.0, -21.8236141204834), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('mailPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('social')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -28.901012420654297), (-0.0, 1.0, -0.0, -21.8236141204834), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('mainTablePhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('mainTablePhysicalDynamic.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('medal')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('onlyfansPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('social')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -28.901012420654297), (-0.0, 1.0, -0.0, -21.8236141204834), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('panel')
    if _o is not None:
        _o.parent = bpy.data.objects.get('inner.004')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427875757217407, 0.0, 7.4016876220703125), (-0.6427875757217407, 0.7660444974899292, -0.0, -35.417545318603516), (0.0, 0.0, 1.0, -3.0517988204956055), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('panel.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refMini')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 41.129356384277344), (0.0, 1.0, 0.0, -18.678844451904297), (0.0, 0.0, 1.0, -2.700789213180542), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('panel.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('inner.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427875757217407, 0.0, 7.4016876220703125), (-0.6427875757217407, 0.7660444974899292, -0.0, -35.417545318603516), (0.0, 0.0, 1.0, -3.0517988204956055), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('paperPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('toilet')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -66.87518310546875), (-0.0, 1.0, 0.0, 66.73855590820312), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('paperPhysicalDynamic.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('toilet')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -66.87518310546875), (-0.0, 1.0, 0.0, 66.73855590820312), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('paperPhysicalDynamic.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('toilet')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -66.87518310546875), (-0.0, 1.0, 0.0, 66.73855590820312), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('phonePhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('phonePhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.6867039799690247, 0.7269372344017029, -7.450581485102248e-09, -17.351560592651367), (-0.7165263891220093, 0.6768693923950195, 0.168635293841362, 61.49517822265625), (0.12258728593587875, -0.11580253392457962, 0.9856785535812378, -11.04310131072998), (-0.0, -0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('phonePhysicalDynamic.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('phonePhysicalDynamic.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('phonePhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.6867039799690247, 0.7269372344017029, -7.450581485102248e-09, -17.351560592651367), (-0.7165263891220093, 0.6768693923950195, 0.168635293841362, 61.49517822265625), (0.12258728593587875, -0.11580253392457962, 0.9856785535812378, -11.04310131072998), (-0.0, -0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('physicalFixed')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('physicalFixed.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('physicalFixed.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('social')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -28.901012420654297), (-0.0, 1.0, -0.0, -21.8236141204834), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('physicalFixed.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('physicalFixed.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('physicalFixed.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('altar')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -75.34408569335938), (-0.0, 1.0, -0.0, -27.94936180114746), (0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('physicalFixed.006')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('physicalFixed.007')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('physicalFixed.008')
    if _o is not None:
        _o.parent = bpy.data.objects.get('achievements')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -70.5515365600586), (-0.0, 1.0, 0.0, 9.938889503479004), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('physicalFixed.009')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('physicalFixed.010')
    if _o is not None:
        _o.parent = bpy.data.objects.get('timeMachine')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.53236389160156), (-0.0, 1.0, -0.0, -67.39844512939453), (0.0, 0.0, 1.0, -3.2733685970306396), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('pin0')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refPinPositions')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 39.085426330566406), (0.0, 1.0, 0.0, -41.441078186035156), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('pin1')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refPinPositions')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 39.085426330566406), (0.0, 1.0, 0.0, -41.441078186035156), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('pin2')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refPinPositions')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 39.085426330566406), (0.0, 1.0, 0.0, -41.441078186035156), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('pin3')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refPinPositions')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 39.085426330566406), (0.0, 1.0, 0.0, -41.441078186035156), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('pin4')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refPinPositions')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 39.085426330566406), (0.0, 1.0, 0.0, -41.441078186035156), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('pin5')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refPinPositions')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 39.085426330566406), (0.0, 1.0, 0.0, -41.441078186035156), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('pin6')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refPinPositions')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 39.085426330566406), (0.0, 1.0, 0.0, -41.441078186035156), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('pin7')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refPinPositions')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 39.085426330566406), (0.0, 1.0, 0.0, -41.441078186035156), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('pin8')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refPinPositions')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 39.085426330566406), (0.0, 1.0, 0.0, -41.441078186035156), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('pin9')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refPinPositions')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 39.085426330566406), (0.0, 1.0, 0.0, -41.441078186035156), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('plane')
    if _o is not None:
        _o.parent = bpy.data.objects.get('inner')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427875757217407, 0.0, 7.373539924621582), (-0.6427875757217407, 0.7660444974899292, -0.0, -35.33339309692383), (0.0, 0.0, 1.0, -0.5842220187187195), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('plane.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('inner')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427875757217407, 0.0, 7.373539924621582), (-0.6427875757217407, 0.7660444974899292, -0.0, -35.33339309692383), (0.0, 0.0, 1.0, -0.5842220187187195), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('plane.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('inner')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427875757217407, 0.0, 7.373539924621582), (-0.6427875757217407, 0.7660444974899292, -0.0, -35.33339309692383), (0.0, 0.0, 1.0, -0.5842220187187195), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Plane.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('plane.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('inner')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427875757217407, 0.0, 7.373539924621582), (-0.6427875757217407, 0.7660444974899292, -0.0, -35.33339309692383), (0.0, 0.0, 1.0, -0.5842220187187195), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Plane.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('plane.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('inner')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427875757217407, 0.0, 7.373539924621582), (-0.6427875757217407, 0.7660444974899292, -0.0, -35.33339309692383), (0.0, 0.0, 1.0, -0.5842220187187195), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Plane.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('timeMachine')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.53236389160156), (-0.0, 1.0, -0.0, -67.39844512939453), (0.0, 0.0, 1.0, -3.2733685970306396), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Plane.010')
    if _o is not None:
        _o.parent = bpy.data.objects.get('axle')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 0.6498498916625977), (-0.0, 1.0, -0.0, -0.3799999952316284), (0.0, 0.0, 1.0, -1.9514966011047363), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Plane.018')
    if _o is not None:
        _o.parent = bpy.data.objects.get('career')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -25.844032287597656), (-0.0, 1.0, -0.0, -0.9047669172286987), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Plane.022')
    if _o is not None:
        _o.parent = bpy.data.objects.get('career')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -25.844032287597656), (-0.0, 1.0, -0.0, -0.9047669172286987), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Plane.030')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refYear')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 16.046842575073242), (-0.0, 1.0, -0.0, -33.675926208496094), (0.0, 0.0, 1.0, -0.07861466705799103), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Plane.035')
    if _o is not None:
        _o.parent = bpy.data.objects.get('career')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -25.844032287597656), (-0.0, 1.0, -0.0, -0.9047669172286987), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Plane.042')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Plane.043')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Plane.048')
    if _o is not None:
        _o.parent = bpy.data.objects.get('career')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -25.844032287597656), (-0.0, 1.0, -0.0, -0.9047669172286987), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Plane.049')
    if _o is not None:
        _o.parent = bpy.data.objects.get('career')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -25.844032287597656), (-0.0, 1.0, -0.0, -0.9047669172286987), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('qosdjqosjd')
    if _o is not None:
        _o.parent = bpy.data.objects.get('gamepadPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -16.111330032348633), (0.0, 1.0, 0.0, 1.3679430484771729), (0.0, -0.0, 1.0, -1.1724846363067627), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('qosdufhoqsfhosqdhf')
    if _o is not None:
        _o.parent = bpy.data.objects.get('barPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -6.65526008605957), (-0.0, 1.0, 0.0, 75.9970703125), (-0.0, -0.0, 1.0, -1.006199598312378), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('quenchPhysicalDynamic.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refAirDancers')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refAirDancers.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refAltar')
    if _o is not None:
        _o.parent = bpy.data.objects.get('altar')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -75.34408569335938), (-0.0, 1.0, -0.0, -27.94936180114746), (0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refAnvilPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refArrowNext')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refArrowNextImage')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refArrowNextProject')
    if _o is not None:
        _o.parent = bpy.data.objects.get('inner.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427875757217407, 0.0, 5.4031219482421875), (-0.6427875757217407, 0.7660444974899292, -0.0, -35.623870849609375), (0.0, 0.0, 1.0, -3.697094440460205), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refArrowPrevious')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refArrowPreviousImage')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refArrowPreviousProject')
    if _o is not None:
        _o.parent = bpy.data.objects.get('inner.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660443782806396, 0.6427875757217407, 0.0, 9.405397415161133), (-0.6427875757217407, 0.7660443782806396, 0.0, -35.6238899230957), (0.0, 0.0, 1.0, -3.7142975330352783), (-0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('refAttributes')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refBallPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refBalls')
    if _o is not None:
        _o.parent = bpy.data.objects.get('mainTablePhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 42.26213073730469), (-0.0, 1.0, -0.0, -15.820982933044434), (0.0, 0.0, 1.0, -0.5333474278450012), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refBalls.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('mainTablePhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 42.26213073730469), (-0.0, 1.0, -0.0, -15.820982933044434), (0.0, 0.0, 1.0, -0.5333474278450012), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refBanner')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cookiePhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 2.1771774291992188), (-0.0, 1.0, -0.0, -27.35611915588379), (0.0, 0.0, 1.0, -1.6915301084518433), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refBanners')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refBanners.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refBlackBoard.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('blackBoardPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 46.44439697265625), (-0.0, 1.0, -0.0, -14.93013858795166), (0.0, 0.0, 1.0, -0.006079263985157013), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refBlackBoard.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('blackBoardPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 46.44439697265625), (-0.0, 1.0, -0.0, -14.93013858795166), (0.0, 0.0, 1.0, -0.006079263985157013), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refBlackboardLabelsGamepadPlaystation')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refBlackBoard.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 30.20697593688965), (-0.0, 1.0, -0.0, -19.768173217773438), (0.0, 0.0, 1.0, -0.006079263985157013), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refBlackboardLabelsGamepadPlaystation.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refBlackBoard.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 46.44439697265625), (-0.0, 1.0, -0.0, -14.93013858795166), (0.0, 0.0, 1.0, -0.006079263985157013), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refBlackboardLabelsGamepadXbox')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refBlackBoard.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 30.20697593688965), (-0.0, 1.0, -0.0, -19.768173217773438), (0.0, 0.0, 1.0, -0.006079263985157013), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refBlackboardLabelsGamepadXbox.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refBlackBoard.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 46.44439697265625), (-0.0, 1.0, -0.0, -14.93013858795166), (0.0, 0.0, 1.0, -0.006079263985157013), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refBlackboardLabelsMouseKeyboard')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refBlackBoard.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 46.44439697265625), (-0.0, 1.0, -0.0, -14.93013858795166), (0.0, 0.0, 1.0, -0.006079263985157013), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refBlackboardLabelsMouseKeyboard.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refBlackBoard.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 30.20697593688965), (-0.0, 1.0, -0.0, -19.768173217773438), (0.0, 0.0, 1.0, -0.006079263985157013), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refBlade')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refAnvilPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 22.37274932861328), (-0.0, 1.0, -0.0, -20.72515106201172), (0.0, 0.0, 1.0, -0.7425217032432556), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refBlower')
    if _o is not None:
        _o.parent = bpy.data.objects.get('blowerPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(-4.371138828673793e-08, -1.0, 0.0, -13.282617568969727), (1.0, -4.371138828673793e-08, 0.0, -33.37266159057617), (-0.0, -0.0, 1.0, -0.5265605449676514), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refBlower.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('blowerPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(-4.371138828673793e-08, -1.0, 0.0, -13.282617568969727), (1.0, -4.371138828673793e-08, 0.0, -33.37266159057617), (-0.0, -0.0, 1.0, -0.5265605449676514), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refBonfireBurn.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refBonfireHashes')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refBonfireInteractivePoint')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refBumpersInteractivePoint.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refBumpersPhysicalKinematicPositionBased')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refCabinPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('toilet')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -66.87518310546875), (-0.0, 1.0, 0.0, 66.73855590820312), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refCandleFlame')
    if _o is not None:
        _o.parent = bpy.data.objects.get('mainTablePhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 42.26213073730469), (-0.0, 1.0, -0.0, -15.820982933044434), (0.0, 0.0, 1.0, -0.5333474278450012), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refCandleFlame.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('sideTablePhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8191520571708679, -0.5735764503479004, 0.0, 42.40606689453125), (0.5735764503479004, 0.8191520571708679, -0.0, 8.884500503540039), (0.0, 0.0, 1.0, -0.5333474278450012), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refCarpet.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refCenter')
    if _o is not None:
        _o.parent = bpy.data.objects.get('social')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -28.901012420654297), (-0.0, 1.0, -0.0, -21.8236141204834), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refCenter.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('behindTheScene')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -52.45521545410156), (-0.0, 1.0, -0.0, -11.959333419799805), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refChainLeft')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refChainPulley')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refChainRight')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refCharcoal')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refOvenPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, -0.5, 0.0, 33.56899642944336), (0.5, 0.8660253882408142, 0.0, -3.0404090881347656), (0.0, 0.0, 1.0, -0.5658632516860962), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refCheckpoints.000')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refCheckpoints.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refCheckpoints.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refCheckpoints.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refCheckpoints.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refCheckpoints.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refCheckpoints.006')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refCheckpoints.007')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refChimney')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cookie')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -12.2511625289917), (-0.0, 1.0, 0.0, 35.2508544921875), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refControlsInteractivePoint')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refCookie')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cookie')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -12.2511625289917), (-0.0, 1.0, 0.0, 35.2508544921875), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refCounter')
    if _o is not None:
        _o.parent = bpy.data.objects.get('altar')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -75.34408569335938), (-0.0, 1.0, -0.0, -27.94936180114746), (0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refCounterLabel')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cookie')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -12.2511625289917), (-0.0, 1.0, 0.0, 35.2508544921875), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refCounterPanel')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cookiePhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 2.1771774291992188), (-0.0, 1.0, -0.0, -27.35611915588379), (0.0, 0.0, 1.0, -1.6915301084518433), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refCrosses')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refScreenPhysicalKinematicPositionBased')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 32.43721008300781), (0.0, 1.0, -0.0, 27.827552795410156), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refDiscs')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refScreenPhysicalKinematicPositionBased')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 32.43721008300781), (0.0, 1.0, -0.0, 27.827552795410156), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refDistinctions')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refel')
    if _o is not None:
        _o.parent = bpy.data.objects.get('with')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, 0.5, 0.0, 8.131414413452148), (-0.5, 0.8660253882408142, 0.0, -32.79646301269531), (0.0, 0.0, 1.0, -1.8272244930267334), (-0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('refel.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('at')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, 0.5, 0.0, 8.131414413452148), (-0.5, 0.8660253882408142, 0.0, -32.79646301269531), (0.0, 0.0, 1.0, -2.568195343017578), (-0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('refel.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('role')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, 0.5, 0.0, 8.131414413452148), (-0.5, 0.8660253882408142, 0.0, -32.79646301269531), (0.0, 0.0, 1.0, -3.313305377960205), (-0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('refel.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refFan')
    if _o is not None:
        _o.parent = bpy.data.objects.get('social')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -28.901012420654297), (-0.0, 1.0, -0.0, -21.8236141204834), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refFire')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refFwaPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('social')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -28.901012420654297), (-0.0, 1.0, -0.0, -21.8236141204834), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refGearA')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refGearB')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refGearC')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refGrinder')
    if _o is not None:
        _o.parent = bpy.data.objects.get('grinderPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, 0.5, 0.0, 7.615090370178223), (-0.5, 0.8660253882408142, -0.0, -30.908390045166016), (0.0, 0.0, 1.0, -0.9612043499946594), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refHammer')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refAnvilPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -39.47209167480469), (-0.0, 1.0, 0.0, 11.435405731201172), (-0.0, -0.0, 1.0, -0.7425217032432556), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refHeat.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cauldronPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 44.29610824584961), (-0.0, 1.0, -0.0, -15.101877212524414), (0.0, 0.0, 1.0, -0.679256021976471), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refImages')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refImages.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refInteractivePoint')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refInteractivePoint.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refInteractivePoint.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cookie')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -12.2511625289917), (-0.0, 1.0, 0.0, 35.2508544921875), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refInteractivePoint.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refInteractivePoint.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('behindTheScene')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -52.45521545410156), (-0.0, 1.0, -0.0, -11.959333419799805), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refInteractivePoint.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('achievements')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -70.5515365600586), (-0.0, 1.0, 0.0, 9.938889503479004), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refInteractivePoint.006')
    if _o is not None:
        _o.parent = bpy.data.objects.get('timeMachine')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -70.5515365600586), (-0.0, 1.0, 0.0, 9.938889503479004), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refInteractivePoint.007')
    if _o is not None:
        _o.parent = bpy.data.objects.get('easter')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -53.7476806640625), (-0.0, 1.0, 0.0, 36.33066940307617), (-0.0, -0.0, 1.0, -0.8951517343521118), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refIntersectNext')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refIntersectNextImage')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refIntersectNextProject')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refIntersectPagination')
    if _o is not None:
        _o.parent = bpy.data.objects.get('plane')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427876353263855, -0.0, 7.37353515625), (2.8097138837779312e-08, -3.348486288246022e-08, 1.0, -0.5842204689979553), (0.6427876353263855, -0.7660444974899292, -4.371139183945161e-08, 35.33339309692383), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refIntersectPagination.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('plane.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427876353263855, -0.0, 7.37353515625), (2.8097138837779312e-08, -3.348486288246022e-08, 1.0, -0.5842204689979553), (0.6427876353263855, -0.7660444974899292, -4.371139183945161e-08, 35.33339309692383), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refIntersectPagination.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('plane.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427876353263855, -0.0, 7.37353515625), (2.8097138837779312e-08, -3.348486288246022e-08, 1.0, -0.5842204689979553), (0.6427876353263855, -0.7660444974899292, -4.371139183945161e-08, 35.33339309692383), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refIntersectPagination.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('plane.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427876353263855, -0.0, 7.37353515625), (2.8097138837779312e-08, -3.348486288246022e-08, 1.0, -0.5842204689979553), (0.6427876353263855, -0.7660444974899292, -4.371139183945161e-08, 35.33339309692383), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refIntersectPagination.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('plane.004')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427876353263855, -0.0, 7.37353515625), (2.8097138837779312e-08, -3.348486288246022e-08, 1.0, -0.5842204689979553), (0.6427876353263855, -0.7660444974899292, -4.371139183945161e-08, 35.33339309692383), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refIntersectPrevious')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refIntersectPreviousImage')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refIntersectPreviousProject')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refIntersectUrl')
    if _o is not None:
        _o.parent = bpy.data.objects.get('panel')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7632371187210083, 0.6461185216903687, -0.00014143437147140503, 7.247766971588135), (-0.6460901498794556, 0.7632015943527222, -0.00953189842402935, -35.418766021728516), (-0.006050792522728443, 0.007366477977484465, 0.9999545812606812, -3.388535976409912), (-0.0, -0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refIntersectUrl.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('panel.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7632371187210083, 0.6461185216903687, -0.00014143437147140503, 7.247766971588135), (-0.6460901498794556, 0.7632015943527222, -0.00953189842402935, -35.418766021728516), (-0.006050792522728443, 0.007366477977484465, 0.9999545812606812, -3.388535976409912), (-0.0, -0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refJukeboxInteractivePoint')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refJukeboxPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refKioskInteractivePoint')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refLabelStrike')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refScreenPhysicalKinematicPositionBased')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 32.43721008300781), (-0.0, 1.0, -0.0, 32.000701904296875), (-0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refLeaderboard')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refLeaderboardReset')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refLettersPhysicalDynamic.010')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refLettersPhysicalDynamic.011')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refLettersPhysicalDynamic.012')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refLettersPhysicalDynamic.013')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refLettersPhysicalDynamic.014')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refLettersPhysicalDynamic.015')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refLettersPhysicalDynamic.016')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refLettersPhysicalDynamic.017')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refLettersPhysicalDynamic.018')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refLettersPhysicalDynamic.019')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refLine')
    if _o is not None:
        _o.parent = bpy.data.objects.get('career')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -25.844032287597656), (-0.0, 1.0, -0.0, -0.9047669172286987), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refLine.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('career')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -25.844032287597656), (-0.0, 1.0, -0.0, -0.9047669172286987), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refLine.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('career')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -25.844032287597656), (-0.0, 1.0, -0.0, -0.9047669172286987), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refLine.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('career')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -25.844032287597656), (-0.0, 1.0, -0.0, -0.9047669172286987), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refLine.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('career')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -25.844032287597656), (-0.0, 1.0, -0.0, -0.9047669172286987), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refLine.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('career')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -25.844032287597656), (-0.0, 1.0, -0.0, -0.9047669172286987), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refLiquid')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cauldronPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 44.29610824584961), (-0.0, 1.0, -0.0, -15.101877212524414), (0.0, 0.0, 1.0, -0.679256021976471), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refMecanism')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refMini')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refMoon')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refCabinPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 14.251117706298828), (0.0, 1.0, -0.0, 18.108078002929688), (0.0, 0.0, 1.0, -1.8276546001434326), (0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refNext')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic.006')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic.007')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic.008')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic.009')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic.010')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic.011')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic.012')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic.013')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic.014')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic.015')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic.016')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic.017')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic.018')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic.019')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic.020')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic.021')
    if _o is not None:
        _o.parent = bpy.data.objects.get('behindTheScene')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -52.45521545410156), (-0.0, 1.0, -0.0, -11.959333419799805), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic.022')
    if _o is not None:
        _o.parent = bpy.data.objects.get('behindTheScene')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -52.45521545410156), (-0.0, 1.0, -0.0, -11.959333419799805), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObjectsPhysicalDynamic.023')
    if _o is not None:
        _o.parent = bpy.data.objects.get('behindTheScene')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -52.45521545410156), (-0.0, 1.0, -0.0, -11.959333419799805), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObstaclesPhysicalKinematicPositionBased.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObstaclesPhysicalKinematicPositionBased.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObstaclesPhysicalKinematicPositionBased.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObstaclesPhysicalKinematicPositionBased.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refObstaclesPhysicalKinematicPositionBased.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refOnlyFans')
    if _o is not None:
        _o.parent = bpy.data.objects.get('social')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -28.901012420654297), (-0.0, 1.0, -0.0, -21.8236141204834), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refOvenHeat')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cookiePhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 2.1771774291992188), (-0.0, 1.0, -0.0, -27.35611915588379), (0.0, 0.0, 1.0, -1.6915301084518433), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refOvenPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refPagination')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refPillar')
    if _o is not None:
        _o.parent = bpy.data.objects.get('achievements')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -70.5515365600586), (-0.0, 1.0, 0.0, 9.938889503479004), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refPinPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refPinPositions')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refPodiumConfettiA')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refPodiumConfettiB')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refPodiumPhysicalFixed.008')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refPrevious')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refRailsPhysicalFixed')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refRestartInteractivePoint')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refRoadPhysicalFixed')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refScreen')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refTvPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.50775146484375), (-0.0, 1.0, -0.0, -69.14649963378906), (0.0, 0.0, 1.0, -1.1553428173065186), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refScreenPhysicalKinematicPositionBased')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refSkullEyes5')
    if _o is not None:
        _o.parent = bpy.data.objects.get('altar')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -75.34408569335938), (-0.0, 1.0, -0.0, -27.94936180114746), (0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refSpawner')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cookie')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -12.2511625289917), (-0.0, 1.0, 0.0, 35.2508544921875), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refStart')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refStartingLights')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refStatuePhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('social')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -28.901012420654297), (-0.0, 1.0, -0.0, -21.8236141204834), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refTable')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cookie')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -12.2511625289917), (-0.0, 1.0, 0.0, 35.2508544921875), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refTimer')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refTitle')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refTitle.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refTvPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('timeMachine')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.53236389160156), (-0.0, 1.0, -0.0, -67.39844512939453), (0.0, 0.0, 1.0, -3.2733685970306396), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refUrl')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refUrl.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refWaterfallDrop')
    if _o is not None:
        _o.parent = bpy.data.objects.get('achievements')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -70.5515365600586), (-0.0, 1.0, 0.0, 9.938889503479004), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refWaterfallParticles')
    if _o is not None:
        _o.parent = bpy.data.objects.get('achievements')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -70.5515365600586), (-0.0, 1.0, 0.0, 9.938889503479004), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refWaterfallStill')
    if _o is not None:
        _o.parent = bpy.data.objects.get('achievements')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -70.5515365600586), (-0.0, 1.0, 0.0, 9.938889503479004), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refWaterfallZone')
    if _o is not None:
        _o.parent = bpy.data.objects.get('achievements')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -70.5515365600586), (-0.0, 1.0, 0.0, 9.938889503479004), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refWood')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refYear')
    if _o is not None:
        _o.parent = bpy.data.objects.get('career')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -25.844032287597656), (-0.0, 1.0, -0.0, -0.9047669172286987), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneBounding')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneBounding.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('career')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -25.844032287597656), (-0.0, 1.0, -0.0, -0.9047669172286987), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneBounding.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('social')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -28.901012420654297), (-0.0, 1.0, -0.0, -21.8236141204834), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneBounding.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneBounding.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneBounding.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cookie')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -12.2511625289917), (-0.0, 1.0, 0.0, 35.2508544921875), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneBounding.006')
    if _o is not None:
        _o.parent = bpy.data.objects.get('altar')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -75.34408569335938), (-0.0, 1.0, -0.0, -27.94936180114746), (0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneBounding.007')
    if _o is not None:
        _o.parent = bpy.data.objects.get('toilet')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -66.87518310546875), (-0.0, 1.0, 0.0, 66.73855590820312), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneBounding.008')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneBounding.009')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneBounding.010')
    if _o is not None:
        _o.parent = bpy.data.objects.get('behindTheScene')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -52.45521545410156), (-0.0, 1.0, -0.0, -11.959333419799805), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneBounding.011')
    if _o is not None:
        _o.parent = bpy.data.objects.get('achievements')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -70.5515365600586), (-0.0, 1.0, 0.0, 9.938889503479004), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneBounding.012')
    if _o is not None:
        _o.parent = bpy.data.objects.get('timeMachine')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -70.5515365600586), (-0.0, 1.0, 0.0, 9.938889503479004), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneFrustum')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneFrustum.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('career')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -25.844032287597656), (-0.0, 1.0, -0.0, -0.9047669172286987), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneFrustum.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('social')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -28.901012420654297), (-0.0, 1.0, -0.0, -21.8236141204834), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneFrustum.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneFrustum.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneFrustum.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cookie')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -12.2511625289917), (-0.0, 1.0, 0.0, 35.2508544921875), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneFrustum.006')
    if _o is not None:
        _o.parent = bpy.data.objects.get('altar')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -75.34408569335938), (-0.0, 1.0, -0.0, -27.94936180114746), (0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneFrustum.007')
    if _o is not None:
        _o.parent = bpy.data.objects.get('toilet')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -66.87518310546875), (-0.0, 1.0, 0.0, 66.73855590820312), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneFrustum.008')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneFrustum.009')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneFrustum.010')
    if _o is not None:
        _o.parent = bpy.data.objects.get('behindTheScene')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -52.45521545410156), (-0.0, 1.0, -0.0, -11.959333419799805), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneFrustum.011')
    if _o is not None:
        _o.parent = bpy.data.objects.get('achievements')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -70.5515365600586), (-0.0, 1.0, 0.0, 9.938889503479004), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneFrustum.012')
    if _o is not None:
        _o.parent = bpy.data.objects.get('timeMachine')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -70.5515365600586), (-0.0, 1.0, 0.0, 9.938889503479004), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('refZoneFrustum.013')
    if _o is not None:
        _o.parent = bpy.data.objects.get('easter')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -53.7476806640625), (-0.0, 1.0, 0.0, 36.33066940307617), (-0.0, -0.0, 1.0, -0.8951517343521118), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('rocks.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('toilet')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -66.87518310546875), (-0.0, 1.0, 0.0, 66.73855590820312), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('role')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refAttributes')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, 0.5, 0.0, 8.272603988647461), (-0.5, 0.8660253882408142, -0.0, -32.93546676635742), (0.0, 0.0, 1.0, -2.5549123287200928), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('sauceKetchupPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('sauceKetchupPhysicalDynamic.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('sauceKetchupPhysicalDynamic.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('sauceMustardPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('sauceMustardPhysicalDynamic.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('sauceMustardPhysicalDynamic.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('sideTablePhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('lab')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -13.136816024780273), (-0.0, 1.0, 0.0, 17.684432983398438), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('sign.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('sign.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('socialArrayReference')
    if _o is not None:
        _o.parent = bpy.data.objects.get('social')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -28.901012420654297), (-0.0, 1.0, -0.0, -21.8236141204834), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('Sphere')
    if _o is not None:
        _o.parent = bpy.data.objects.get('axle')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 0.6498498916625977), (-0.0, 1.0, -0.0, -0.3799999952316284), (0.0, 0.0, 1.0, -1.9514966011047363), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('stone')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refLine')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 12.021645545959473), (-0.0, 1.0, -0.0, -30.739238739013672), (0.0, 0.0, 1.0, -0.0413644015789032), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('stone.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refLine.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 12.021645545959473), (-0.0, 1.0, -0.0, -30.739238739013672), (0.0, 0.0, 1.0, -0.0413644015789032), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('stone.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refLine.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 12.021645545959473), (-0.0, 1.0, -0.0, -30.739238739013672), (0.0, 0.0, 1.0, -0.0413644015789032), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('stone.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refLine.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 12.021645545959473), (-0.0, 1.0, -0.0, -30.739238739013672), (0.0, 0.0, 1.0, -0.0413644015789032), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('stone.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refLine.004')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 12.021645545959473), (-0.0, 1.0, -0.0, -30.739238739013672), (0.0, 0.0, 1.0, -0.0413644015789032), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('stone.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refLine.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 12.021645545959473), (-0.0, 1.0, -0.0, -30.739238739013672), (0.0, 0.0, 1.0, -0.0413644015789032), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('stoolPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('toilet')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -66.87518310546875), (-0.0, 1.0, 0.0, 66.73855590820312), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('stoolPhysicalDynamic.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('stoolPhysicalDynamic.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('stoolPhysicalDynamic.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('stoolPhysicalDynamic.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('timeMachine')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.53236389160156), (-0.0, 1.0, -0.0, -67.39844512939453), (0.0, 0.0, 1.0, -3.2733685970306396), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('stoolPhysicalDynamic.007')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('stopLights.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('stopLights.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('chassis.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -2.9802322387695312e-08), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.9071758985519409), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('sudoMesh.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('sudo.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.1558645963668823, -1.496463166430421e-16, -2.332819528082377e-16, 16.312192916870117), (1.496463166430421e-16, 1.1558645963668823, 2.2690889721180325e-39, -63.47093963623047), (2.332819528082377e-16, -3.0202314310302894e-32, 1.1558645963668823, -1.6257846355438232), (-0.0, -0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('sudoMesh.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('sudoPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.1558645963668823, -0.0, 0.0, 15.835517883300781), (-0.0, 1.1558645963668823, -0.0, -63.338401794433594), (0.0, 0.0, 1.1558645963668823, -1.771923303604126), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('sudoPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('social')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -28.901012420654297), (-0.0, 1.0, -0.0, -21.8236141204834), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('sword')
    if _o is not None:
        _o.parent = bpy.data.objects.get('landing')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -49.2523078918457), (-0.0, 1.0, 0.0, 38.5212516784668), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('table.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('projects')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -35.759559631347656), (-0.0, 1.0, 0.0, 13.40835189819336), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('table.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('mainTablePhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 42.26213073730469), (-0.0, 1.0, -0.0, -15.820982933044434), (0.0, 0.0, 1.0, -0.5333474278450012), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tablePhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cookie')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -12.2511625289917), (-0.0, 1.0, 0.0, 35.2508544921875), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tablePhysicalDynamic.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tablePhysicalDynamic.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bowling')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -2.3131165504455566), (-0.0, 1.0, 0.0, 68.90996551513672), (-0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('text')
    if _o is not None:
        _o.parent = bpy.data.objects.get('at')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, 0.5, 0.0, 8.131414413452148), (-0.5, 0.8660253882408142, 0.0, -32.79646301269531), (0.0, 0.0, 1.0, -2.568195343017578), (-0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('text.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('role')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, 0.5, 0.0, 8.131414413452148), (-0.5, 0.8660253882408142, 0.0, -32.79646301269531), (0.0, 0.0, 1.0, -3.313305377960205), (-0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('text.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('with')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, 0.5, 0.0, 8.131414413452148), (-0.5, 0.8660253882408142, 0.0, -32.79646301269531), (0.0, 0.0, 1.0, -1.8272244930267334), (-0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('Text.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('circuit')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 17.744478225708008), (-0.0, 1.0, -0.0, 7.070260047912598), (-0.0, 0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('text.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('inner.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427875757217407, 0.0, 5.4031219482421875), (-0.6427875757217407, 0.7660444974899292, -0.0, -35.623870849609375), (0.0, 0.0, 1.0, -3.697094440460205), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('text.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('inner.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660443782806396, 0.6427875757217407, 0.0, 9.405397415161133), (-0.6427875757217407, 0.7660443782806396, 0.0, -35.6238899230957), (0.0, 0.0, 1.0, -3.7142975330352783), (-0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('text.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('inner.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427875757217407, 0.0, 7.40006160736084), (-0.6427875757217407, 0.7660444974899292, -0.0, -35.49038314819336), (0.0, 0.0, 1.0, -3.4301838874816895), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('text.006')
    if _o is not None:
        _o.parent = bpy.data.objects.get('inner.004')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427875757217407, 0.0, 7.4016876220703125), (-0.6427875757217407, 0.7660444974899292, -0.0, -35.417545318603516), (0.0, 0.0, 1.0, -3.0517988204956055), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('text.007')
    if _o is not None:
        _o.parent = bpy.data.objects.get('inner.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427875757217407, 0.0, 7.4016876220703125), (-0.6427875757217407, 0.7660444974899292, -0.0, -35.417545318603516), (0.0, 0.0, 1.0, -3.0517988204956055), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('text.008')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refMini')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.866025447845459, 0.49999991059303284, 0.0, 25.95591926574707), (-0.49999991059303284, 0.866025447845459, 0.0, -37.36631774902344), (0.0, 0.0, 1.0, -2.700789213180542), (-0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('text.009')
    if _o is not None:
        _o.parent = bpy.data.objects.get('inner.007')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.7660444974899292, 0.6427875757217407, 0.0, 7.40006160736084), (-0.6427875757217407, 0.7660444974899292, -0.0, -35.49038314819336), (0.0, 0.0, 1.0, -3.4301838874816895), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('trimesh')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refRailsPhysicalFixed')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 66.79804229736328), (-0.0, 1.0, -0.0, -0.5890306830406189), (0.0, 0.0, 1.0, 0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('trimesh.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, -27.631092071533203), (0.0, 1.0, 0.0, -27.807859420776367), (0.0, 0.0, 1.0, -0.9431422352790833), (0.0, 0.0, 0.0, 1.0)])
    _o = bpy.data.objects.get('tube')
    if _o is not None:
        _o.parent = bpy.data.objects.get('gitHubPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 18.036468505859375), (-0.0, 1.0, -0.0, -61.49617004394531), (0.0, 0.0, 1.0, -1.5137088298797607), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('paperPhysicalDynamic.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.9176062345504761, 0.39749065041542053, 0.0, 21.754817962646484), (-0.39749065041542053, 0.9176062345504761, -0.0, 12.59012222290039), (-0.0, 0.0, 1.0, -1.5360146760940552), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('paperPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.924915611743927, -0.3801725208759308, 0.0, 6.024631023406982), (0.3801725208759308, 0.924915611743927, -0.0, 24.51481056213379), (-0.0, 0.0, 1.0, -1.2028170824050903), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('paperPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.5518975853919983, -0.8339120149612427, 0.0, -8.439383506774902), (0.8339120149612427, 0.5518975853919983, -0.0, 23.539648056030273), (-0.0, 0.0, 1.0, -1.2100577354431152), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refPinPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.0), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refPinPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.0), (-0.0, 1.0, -0.0, 0.0), (0.0, -0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.006')
    if _o is not None:
        _o.parent = bpy.data.objects.get('barPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, -0.0, -6.65526008605957), (-0.0, 1.0, 0.0, 75.9970703125), (-0.0, -0.0, 1.0, -1.006199598312378), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.007')
    if _o is not None:
        _o.parent = bpy.data.objects.get('sauceKetchupPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 45.094486236572266), (-0.0, 1.0, -0.0, 28.685636520385742), (-0.0, 0.0, 1.0, -1.6018928289413452), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.008')
    if _o is not None:
        _o.parent = bpy.data.objects.get('sauceMustardPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 44.90091323852539), (-0.0, 1.0, -0.0, 28.341936111450195), (-0.0, 0.0, 1.0, -1.6018928289413452), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.009')
    if _o is not None:
        _o.parent = bpy.data.objects.get('sauceKetchupPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 45.094486236572266), (-0.0, 1.0, -0.0, 28.685636520385742), (-0.0, 0.0, 1.0, -1.6018928289413452), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.010')
    if _o is not None:
        _o.parent = bpy.data.objects.get('sauceMustardPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 44.90091323852539), (-0.0, 1.0, -0.0, 28.341936111450195), (-0.0, 0.0, 1.0, -1.6018928289413452), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.011')
    if _o is not None:
        _o.parent = bpy.data.objects.get('sauceKetchupPhysicalDynamic.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 45.094486236572266), (-0.0, 1.0, -0.0, 28.685636520385742), (-0.0, 0.0, 1.0, -1.6018928289413452), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.012')
    if _o is not None:
        _o.parent = bpy.data.objects.get('sauceMustardPhysicalDynamic.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 44.90091323852539), (-0.0, 1.0, -0.0, 28.341936111450195), (-0.0, 0.0, 1.0, -1.6018928289413452), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.013')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.007')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 40.49323272705078), (-0.0, 1.0, -0.0, 36.959476470947266), (-0.0, 0.0, 1.0, -0.03489186242222786), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.014')
    if _o is not None:
        _o.parent = bpy.data.objects.get('phonePhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.6867039799690247, 0.7269372344017029, -7.450581485102248e-09, -17.351560592651367), (-0.7165263891220093, 0.6768693923950195, 0.168635293841362, 61.49517822265625), (0.12258728593587875, -0.11580253392457962, 0.9856785535812378, -11.04310131072998), (-0.0, -0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.015')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 53.5989990234375), (-0.0, 1.0, -0.0, -57.884761810302734), (0.0, 0.0, 1.0, -0.8378028869628906), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.016')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 53.5989990234375), (-0.0, 1.0, -0.0, -57.884761810302734), (0.0, 0.0, 1.0, -0.8378028869628906), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.017')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 53.5989990234375), (-0.0, 1.0, -0.0, -57.884761810302734), (0.0, 0.0, 1.0, -0.8378028869628906), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.018')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 53.5989990234375), (-0.0, 1.0, -0.0, -57.884761810302734), (0.0, 0.0, 1.0, -0.8378028869628906), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.019')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.004')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 53.5989990234375), (-0.0, 1.0, -0.0, -57.884761810302734), (0.0, 0.0, 1.0, -0.8378028869628906), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.020')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 53.5989990234375), (-0.0, 1.0, -0.0, -57.884761810302734), (0.0, 0.0, 1.0, -0.8378028869628906), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.021')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 53.5989990234375), (-0.0, 1.0, -0.0, -57.884761810302734), (0.0, 0.0, 1.0, -0.8378028869628906), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.022')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.007')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 53.5989990234375), (-0.0, 1.0, -0.0, -57.884761810302734), (0.0, 0.0, 1.0, -0.8378028869628906), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.023')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bumpersPhysicalFixed.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 119.94792175292969), (-0.0, 1.0, -0.0, 3.6904983520507812), (0.0, 0.0, 1.0, -0.009999999776482582), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.024')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bumpersPhysicalFixed.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 119.94792175292969), (-0.0, 1.0, -0.0, 3.6904983520507812), (0.0, 0.0, 1.0, -0.009999999776482582), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.025')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bumpersPhysicalFixed.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 119.94792175292969), (-0.0, 1.0, -0.0, 3.6904983520507812), (0.0, 0.0, 1.0, -0.009999999776482582), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.026')
    if _o is not None:
        _o.parent = bpy.data.objects.get('bumpersPhysicalFixed.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 119.94792175292969), (-0.0, 1.0, -0.0, 3.6904983520507812), (0.0, 0.0, 1.0, -0.009999999776482582), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.027')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.009')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 59.39476776123047), (-0.0, 1.0, -0.0, -41.10956954956055), (0.0, 0.0, 1.0, -0.7538084983825684), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.028')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.010')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 59.39476776123047), (-0.0, 1.0, -0.0, -41.10956954956055), (0.0, 0.0, 1.0, -0.7538084983825684), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.029')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refObjectsPhysicalDynamic.008')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 59.39476776123047), (-0.0, 1.0, -0.0, -41.10956954956055), (0.0, 0.0, 1.0, -0.7538084983825684), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.030')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.031')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.032')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.033')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cupPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.02385711669922), (-0.0, 1.0, -0.0, -69.1495132446289), (0.0, 0.0, 1.0, -2.2334752082824707), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.034')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.035')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.036')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.037')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.038')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.039')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.040')
    if _o is not None:
        _o.parent = bpy.data.objects.get('physicalFixed.006')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 63.526912689208984), (-0.0, 1.0, -0.0, -35.23796463012695), (0.0, 0.0, 1.0, -0.0), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.041')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cupPhysicalDynamic.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.02385711669922), (-0.0, 1.0, -0.0, -69.1495132446289), (0.0, 0.0, 1.0, -2.2334752082824707), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('tube.042')
    if _o is not None:
        _o.parent = bpy.data.objects.get('cupPhysicalDynamic.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, 54.02385711669922), (-0.0, 1.0, -0.0, -69.1495132446289), (0.0, 0.0, 1.0, -2.2334752082824707), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('twitchPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('social')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -28.901012420654297), (-0.0, 1.0, -0.0, -21.8236141204834), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheel')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelCylinder')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheel.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelCylinder.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheel.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelCylinder.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheel.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelCylinder.004')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheel.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelCylinder.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheel.006')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelCylinder.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheelCylinder')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelContainer')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheelCylinder.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelContainer.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheelCylinder.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelContainer.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheelCylinder.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelContainer.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheelCylinder.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelContainer.004')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheelCylinder.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelContainer.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheelGuard.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelContainer.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheelGuard.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelContainer.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheelGuard.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelContainer.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheelGuard.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelContainer.004')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheelGuard.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelContainer.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheelPainted')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelCylinder.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheelPainted.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelCylinder.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheelPainted.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelCylinder.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheelPainted.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelCylinder.004')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheelPainted.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelCylinder.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheelSuspension.001')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelContainer.002')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheelSuspension.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelContainer.001')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheelSuspension.003')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelContainer.003')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheelSuspension.004')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelContainer.004')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wheelSuspension.005')
    if _o is not None:
        _o.parent = bpy.data.objects.get('wheelContainer.005')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -0.8717746138572693), (-0.0, 1.0, -0.0, -0.6986314058303833), (0.0, -0.0, 1.0, 0.41719210147857666), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wings')
    if _o is not None:
        _o.parent = bpy.data.objects.get('sudoPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.1558645963668823, -0.0, 0.0, 15.835517883300781), (-0.0, 1.1558645963668823, -0.0, -63.338401794433594), (0.0, 0.0, 1.1558645963668823, -1.771923303604126), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('with')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refAttributes')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(0.8660253882408142, 0.5, 0.0, 8.272603988647461), (-0.5, 0.8660253882408142, -0.0, -32.93546676635742), (0.0, 0.0, 1.0, -2.5549123287200928), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('wood.002')
    if _o is not None:
        _o.parent = bpy.data.objects.get('refCabinPhysicalDynamic')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, 0.0, 0.0, 14.251117706298828), (0.0, 1.0, -0.0, 18.108078002929688), (0.0, 0.0, 1.0, -1.8276546001434326), (0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('xPhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('social')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -28.901012420654297), (-0.0, 1.0, -0.0, -21.8236141204834), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])
    _o = bpy.data.objects.get('youtubePhysicalDynamic')
    if _o is not None:
        _o.parent = bpy.data.objects.get('social')
        _o.parent_type = 'OBJECT'
        _o.matrix_parent_inverse = _mu.Matrix([(1.0, -0.0, 0.0, -28.901012420654297), (-0.0, 1.0, -0.0, -21.8236141204834), (0.0, -0.0, 1.0, -3.2733683586120605), (-0.0, 0.0, -0.0, 1.0)])

    # ----- view-layer collection settings (exclude / hide / holdout) -----
    def _walk(lc):
        yield lc
        for ch in lc.children: yield from _walk(ch)
    _vl_settings = {}
    _vl_settings['ViewLayer'] = {'archives.003': {'exclude': True, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'sudo': {'exclude': True, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'vehicle': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'antenna.001': {'exclude': True, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'oldSchool': {'exclude': True, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'default.001': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'easter': {'exclude': True, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'egg': {'exclude': True, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'map': {'exclude': True, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'altar.001': {'exclude': True, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'behindTheScene.001': {'exclude': True, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'birchTrees.001': {'exclude': True, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'oakTrees.001': {'exclude': True, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'cherryTrees.001': {'exclude': True, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'vehicle.001': {'exclude': True, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'terrain': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'grass': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'tornado': {'exclude': True, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'respawns': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'whispersForbiddenAreas': {'exclude': True, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'oakTrees': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'archives.001': {'exclude': True, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'visual.004': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'references.002': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'birchTrees': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'archives.002': {'exclude': True, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'visual.002': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'references': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'cherryTrees': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'archives': {'exclude': True, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'visual.005': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'references.003': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'bricks': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'flowers': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'bushes': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'explosiveCrates': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'fwa': {'exclude': True, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'poleLights': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'lanterns': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'benches': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'fences': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'scenery.002': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'bridges': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'rocks': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'basaltRocks': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'slabs': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'road.001': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'areas': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'landing': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'title.001': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'controls': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'kiosk': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'bonfire': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'career': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'social': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'icons': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'statue': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'default': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'FWA': {'exclude': True, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'projects': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'board': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'pole': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'distinctions': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'mainTable.001': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'oven': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'anvil': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'grinder': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'quench': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'blackBoard.002': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'lab': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'mainTable': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'scroller': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'board.001': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'blackBoard.001': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'cauldron': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'sideTable': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'cookie': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'altar': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'toilet': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'cabin': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'stool': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'bowling': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'pins': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'screen': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'bumpers': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'sign': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'furnitures': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'jukebox': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'pinsPosition': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'alley': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'circuit': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'checkpoints': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'cones': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'barrels': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'startingLights': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'timer': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'road': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'zigzag': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'obstacles': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'jump': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'rails': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'scenery': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'airDancers': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'banners': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'leaderboard': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'podium': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'leaderboardReset': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'behindTheScene': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'lightGenerators': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'scenery.001': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'achievements': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'archive.001': {'exclude': True, 'hide_viewport': True, 'holdout': False, 'indirect_only': False}, 'building': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'timeMachine': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'archives.004': {'exclude': True, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'tv': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'playstation': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'stool.001': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'cups': {'exclude': False, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}, 'easter.001': {'exclude': True, 'hide_viewport': False, 'holdout': False, 'indirect_only': False}}
    for vl in bpy.context.scene.view_layers:
        cfg = _vl_settings.get(vl.name, {})
        for lc in _walk(vl.layer_collection):
            s = cfg.get(lc.collection.name)
            if not s: continue
            try: lc.exclude = bool(s.get('exclude', False))
            except Exception: pass
            try: lc.hide_viewport = bool(s.get('hide_viewport', False))
            except Exception: pass
            try: lc.holdout = bool(s.get('holdout', False))
            except Exception: pass
            try: lc.indirect_only = bool(s.get('indirect_only', False))
            except Exception: pass

    # ----- scene settings -----
    sc = bpy.context.scene
    try: sc.frame_start = 1
    except Exception: pass
    try: sc.frame_end = 250
    except Exception: pass
    try: sc.frame_current = 148
    except Exception: pass
    try: sc.frame_step = 1
    except Exception: pass
    try: sc.render.engine = 'CYCLES'
    except Exception: pass
    try: sc.render.resolution_x = 512
    except Exception: pass
    try: sc.render.resolution_y = 512
    except Exception: pass
    try: sc.render.resolution_percentage = 100
    except Exception: pass
    try: sc.render.fps = 24
    except Exception: pass
    try: sc.render.fps_base = 1.0
    except Exception: pass
    try: sc.render.film_transparent = True
    except Exception: pass
    try: sc.unit_settings.system = 'METRIC'
    except Exception: pass
    try: sc.unit_settings.scale_length = 1.0
    except Exception: pass
    try: sc.unit_settings.length_unit = 'METERS'
    except Exception: pass
    try: sc.unit_settings.mass_unit = 'KILOGRAMS'
    except Exception: pass
    try: sc.unit_settings.time_unit = 'SECONDS'
    except Exception: pass
    sc.camera = bpy.data.objects.get('cameraTerrain')

    # ----- compositor link (Blender 5.x: scene.compositing_node_group) -----
    try: sc.compositing_node_group = bpy.data.node_groups.get('terrain')
    except Exception: pass

    # ----- node-tree datablock-ref fixup (for object/collection refs in node sockets) -----
    _fixups = [('ng', 'Geometry Nodes', 'Image Texture', 0, 'images', 'terrainWater'), ('ng', 'Geometry Nodes.001', 'Image Texture', 0, 'images', 'terrainGrass'), ('ng', 'Geometry Nodes.002', 'Object Info', 0, 'objects', 'archivePoleInstance'), ('ng', 'terrain', 'Image', 'image', 'images', 'terrainFurnitures'), ('ng', 'terrain', 'Image.001', 'image', 'images', 'terrainGrass'), ('ng', 'terrain', 'Image.002', 'image', 'images', 'terrainWater'), ('ng', 'terrain', 'Image.003', 'image', 'images', 'terrainAlpha'), ('mat', 'airDancer', 'Image Texture', 'image', 'images', 'circuitAirDancerFace.png'), ('mat', 'blackboardLabels', 'Image Texture', 'image', 'images', 'blackboardLabels.png'), ('mat', 'bowlingLabelStrike', 'Image Texture', 'image', 'images', 'bowlingLabelStrike.png'), ('mat', 'careerTextFreelancer', 'Image Texture', 'image', 'images', 'careerFreelancer.png'), ('mat', 'careerTextHetic', 'Image Texture', 'image', 'images', 'careerHetic.png'), ('mat', 'careerTextImmersive', 'Image Texture', 'image', 'images', 'careerImmersiveGarden.png'), ('mat', 'careerTextIRLTeacher', 'Image Texture', 'image', 'images', 'careerIRLTeacher.png'), ('mat', 'careerTextOnlineTeacher', 'Image Texture', 'image', 'images', 'careerOnlineTeacher.png'), ('mat', 'careerTextUzik', 'Image Texture', 'image', 'images', 'careerUzik.png'), ('mat', 'circuitBrand', 'Image Texture', 'image', 'images', 'circuitBrand.png'), ('mat', 'circuitThreejs', 'Image Texture', 'image', 'images', 'circuitLogoThreejs.png'), ('mat', 'circuitWebgl', 'Image Texture', 'image', 'images', 'circuitLogoWebgl.png'), ('mat', 'circuitWebgpu', 'Image Texture', 'image', 'images', 'circuitLogoWebgpu.png'), ('mat', 'cookieBanner', 'Image Texture', 'image', 'images', 'cookieBanner.png'), ('mat', 'labCarpet', 'Image Texture', 'image', 'images', 'labCarpet.png'), ('mat', 'palette', 'Image Texture', 'image', 'images', 'palette'), ('mat', 'projectsCarpet', 'Image Texture', 'image', 'images', 'projectsCarpet.png'), ('mat', 'projectsLabels', 'Image Texture', 'image', 'images', 'projectsLabels.png'), ('mat', 'stylizedMap', 'Image Texture', 'image', 'images', 'stylized-map.png'), ('mat', 'terrain', 'Image Texture', 'image', 'images', 'terrain.png'), ('mat', 'terrain', 'Image Texture.001', 'image', 'images', 'terrainGrass'), ('mat', 'terrain', 'Image Texture.002', 'image', 'images', 'terrainFurnitures'), ('mat', 'terrain', 'Image Texture.003', 'image', 'images', 'terrainWater'), ('mat', 'terrain', 'Image Texture.004', 'image', 'images', 'slabs.png')]
    for kind, owner, node_name, key, cont, db_name in _fixups:
        if kind == 'ng': tree = bpy.data.node_groups.get(owner)
        elif kind == 'mat': mm = bpy.data.materials.get(owner); tree = mm.node_tree if mm else None
        elif kind == 'world': ww = bpy.data.worlds.get(owner); tree = ww.node_tree if ww else None
        else: tree = None
        if not tree: continue
        node = tree.nodes.get(node_name)
        if not node: continue
        target = getattr(bpy.data, cont).get(db_name) if hasattr(bpy.data, cont) else None
        if target is None: continue
        try:
            if isinstance(key, int): node.inputs[key].default_value = target
            else: setattr(node, key, target)
        except Exception as _e: print('[refs] fix fail:', kind, owner, node_name, key, _e)

    print('[99_finalize] done')

if __name__ == '__main__': run()