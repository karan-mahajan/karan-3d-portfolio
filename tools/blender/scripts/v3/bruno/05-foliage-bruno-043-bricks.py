"""Bruno's 043_bricks.py - verbatim recreation.

30 MESH brick blocks (Cube.NNN, all sharing mesh `Cube.062`) into collection
`bricks`. Hand-placed in small clusters of 2-6 at various positions, using
2-3 z-height layers per cluster to read as stacked/fallen brick piles; a few
have slight x/y tilts for a knocked-over look. `palette` material via mesh.

Adds: 30 MESH to collection `bricks`.

Source: folio-2025/scripts/blender_world_steps/steps/043_bricks.py
"""
import bpy

def run():
    print('[043_bricks] bricks')
    coll = bpy.data.collections.get('bricks')
    if coll is None: coll = bpy.data.collections.new('bricks')
    if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
        try: bpy.context.scene.collection.children.link(coll)
        except Exception: pass

    # --- object: Cube.042 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.042') or bpy.data.objects.new('Cube.042', bpy.data.meshes.get('Cube.062'))
    ob.location = (33.65188980102539, -21.788496017456055, 0.375)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.4793461561203003)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.044 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.044') or bpy.data.objects.new('Cube.044', bpy.data.meshes.get('Cube.062'))
    ob.location = (35.38994216918945, -21.629499435424805, 0.375)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.2164125442504883)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.045 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.045') or bpy.data.objects.new('Cube.045', bpy.data.meshes.get('Cube.062'))
    ob.location = (36.678524017333984, -20.981050491333008, 0.375)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.8327515721321106)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.046 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.046') or bpy.data.objects.new('Cube.046', bpy.data.meshes.get('Cube.062'))
    ob.location = (36.294368743896484, -21.631877899169922, 1.1436642408370972)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.3843036890029907)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.047 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.047') or bpy.data.objects.new('Cube.047', bpy.data.meshes.get('Cube.062'))
    ob.location = (34.53288650512695, -21.755043029785156, 1.1436642408370972)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.6227155923843384)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.050 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.050') or bpy.data.objects.new('Cube.050', bpy.data.meshes.get('Cube.062'))
    ob.location = (24.361055374145508, -51.69087600708008, 0.3749999701976776)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.6802505850791931)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.051 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.051') or bpy.data.objects.new('Cube.051', bpy.data.meshes.get('Cube.062'))
    ob.location = (25.56005096435547, -50.375789642333984, 0.3749999701976776)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.4357510507106781)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.052 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.052') or bpy.data.objects.new('Cube.052', bpy.data.meshes.get('Cube.062'))
    ob.location = (24.832796096801758, -51.10781478881836, 1.125)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.6802505850791931)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.055 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.055') or bpy.data.objects.new('Cube.055', bpy.data.meshes.get('Cube.062'))
    ob.location = (65.33455657958984, 38.015625, 0.3111882209777832)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-0.02488422580063343, -0.004551958758383989, -1.4715481996536255)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.056 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.056') or bpy.data.objects.new('Cube.056', bpy.data.meshes.get('Cube.062'))
    ob.location = (67.10823822021484, 38.08753204345703, 0.24088183045387268)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-0.05757727846503258, 0.006688911467790604, -1.225658893585205)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.057 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.057') or bpy.data.objects.new('Cube.057', bpy.data.meshes.get('Cube.062'))
    ob.location = (66.09888458251953, 38.095069885253906, 1.0422873497009277)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-0.02488422580063343, -0.004551958758383989, -1.4715481996536255)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.068 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.068') or bpy.data.objects.new('Cube.068', bpy.data.meshes.get('Cube.062'))
    ob.location = (17.27407455444336, -5.392132759094238, 0.37500032782554626)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -4.273771286010742)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.069 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.069') or bpy.data.objects.new('Cube.069', bpy.data.meshes.get('Cube.062'))
    ob.location = (15.693809509277344, -6.132991790771484, 0.37500032782554626)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -4.010837554931641)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.070 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.070') or bpy.data.objects.new('Cube.070', bpy.data.meshes.get('Cube.062'))
    ob.location = (16.457019805908203, -5.723337173461914, 1.1436645984649658)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -4.417140960693359)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.103 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.103') or bpy.data.objects.new('Cube.103', bpy.data.meshes.get('Cube.062'))
    ob.location = (51.65959167480469, -41.21300506591797, 0.36787939071655273)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.7103898525238037)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.104 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.104') or bpy.data.objects.new('Cube.104', bpy.data.meshes.get('Cube.062'))
    ob.location = (52.93156433105469, -40.003353118896484, 0.36787939071655273)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -1.4085274934768677)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.105 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.105') or bpy.data.objects.new('Cube.105', bpy.data.meshes.get('Cube.062'))
    ob.location = (52.148685455322266, -40.6444206237793, 1.1178793907165527)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.7103898525238037)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.138 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.138') or bpy.data.objects.new('Cube.138', bpy.data.meshes.get('Cube.062'))
    ob.location = (-8.73654842376709, 27.192829132080078, 0.36787939071655273)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.690804660320282)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.143 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.143') or bpy.data.objects.new('Cube.143', bpy.data.meshes.get('Cube.062'))
    ob.location = (60.39008712768555, -46.66997146606445, 0.29405486583709717)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 1.4673240184783936)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.144 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.144') or bpy.data.objects.new('Cube.144', bpy.data.meshes.get('Cube.062'))
    ob.location = (-7.523737907409668, 28.495189666748047, 0.36787939071655273)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.44630521535873413)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.145 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.145') or bpy.data.objects.new('Cube.145', bpy.data.meshes.get('Cube.062'))
    ob.location = (-8.25867748260498, 27.770877838134766, 1.1178793907165527)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, -0.690804660320282)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.150 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.150') or bpy.data.objects.new('Cube.150', bpy.data.meshes.get('Cube.062'))
    ob.location = (59.999481201171875, -48.284584045410156, 0.29405486583709717)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 2.7730934619903564)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.151 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.151') or bpy.data.objects.new('Cube.151', bpy.data.meshes.get('Cube.062'))
    ob.location = (60.41349411010742, -44.713043212890625, 0.1849508285522461)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.3664788603782654)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.154 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.154') or bpy.data.objects.new('Cube.154', bpy.data.meshes.get('Cube.062'))
    ob.location = (60.100929260253906, -47.37078857421875, 1.0618956089019775)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 2.8886358737945557)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.156 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.156') or bpy.data.objects.new('Cube.156', bpy.data.meshes.get('Cube.062'))
    ob.location = (60.24810791015625, -45.68061828613281, 0.9774340987205505)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-0.14959679543972015, 0.005792323034256697, 0.06459803134202957)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.160 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.160') or bpy.data.objects.new('Cube.160', bpy.data.meshes.get('Cube.062'))
    ob.location = (59.86351776123047, -43.2801399230957, 0.1849508285522461)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.3664788603782654)
    ob.scale = (1.0, 1.0, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.163 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.163') or bpy.data.objects.new('Cube.163', bpy.data.meshes.get('Cube.062'))
    ob.location = (59.90984344482422, -43.823726654052734, 0.9349508285522461)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.44103118777275085)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.167 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.167') or bpy.data.objects.new('Cube.167', bpy.data.meshes.get('Cube.062'))
    ob.location = (50.09434509277344, -50.232730865478516, 0.37417149543762207)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 4.328121185302734)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.169 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.169') or bpy.data.objects.new('Cube.169', bpy.data.meshes.get('Cube.062'))
    ob.location = (60.43845748901367, -44.77689743041992, 1.7045609951019287)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, -0.0, 0.3664788603782654)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    # --- object: Cube.170 (type=MESH) ---
    ob = bpy.data.objects.get('Cube.170') or bpy.data.objects.new('Cube.170', bpy.data.meshes.get('Cube.062'))
    ob.location = (51.3809928894043, -50.13755416870117, 0.5391016006469727)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (-0.5864594578742981, -0.00846422091126442, 4.856105327606201)
    ob.scale = (1.0, 0.9999998807907104, 1.0)
    try: ob.display_type = 'TEXTURED'
    except Exception: pass
    if ob.name not in {o.name for o in coll.objects}:
        try: coll.objects.link(ob)
        except Exception: pass

    print('  added 30 objects to bricks')

if __name__ == '__main__': run()