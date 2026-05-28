import bpy

def run():
    print('[10_cameras] camera datablocks')

    # --- Camera ---
    C = bpy.data.cameras.new('Camera')
    try: C.type = 'ORTHO'
    except Exception: pass
    try: C.lens = 50.0
    except Exception: pass
    try: C.lens_unit = 'MILLIMETERS'
    except Exception: pass
    try: C.clip_start = 0.10000000149011612
    except Exception: pass
    try: C.clip_end = 1000.0
    except Exception: pass
    try: C.sensor_width = 36.0
    except Exception: pass
    try: C.sensor_height = 24.0
    except Exception: pass
    try: C.sensor_fit = 'AUTO'
    except Exception: pass
    try: C.shift_x = 0.0
    except Exception: pass
    try: C.shift_y = 0.0
    except Exception: pass
    C.ortho_scale = 192.0
    C.name = 'Camera'

    # --- Camera.001 ---
    C = bpy.data.cameras.new('Camera.001')
    try: C.type = 'ORTHO'
    except Exception: pass
    try: C.lens = 50.0
    except Exception: pass
    try: C.lens_unit = 'MILLIMETERS'
    except Exception: pass
    try: C.clip_start = 0.10000000149011612
    except Exception: pass
    try: C.clip_end = 1000.0
    except Exception: pass
    try: C.sensor_width = 36.0
    except Exception: pass
    try: C.sensor_height = 24.0
    except Exception: pass
    try: C.sensor_fit = 'AUTO'
    except Exception: pass
    try: C.shift_x = 0.0
    except Exception: pass
    try: C.shift_y = 0.0
    except Exception: pass
    C.ortho_scale = 3.800006866455078
    C.name = 'Camera.001'

if __name__ == '__main__': run()