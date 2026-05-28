import bpy

def run():
    print('[09_lights] light datablocks')

    # --- Area (AREA) ---
    L = bpy.data.lights.new('Area', type='AREA')
    L.energy = 350000.0; L.color = (0.10321345925331116, 0.2634023129940033, 1.0)
    try: L.shadow_soft_size = 0.0
    except Exception: pass
    try: L.use_shadow = True
    except Exception: pass
    try: L.use_custom_distance = False
    except Exception: pass
    try: L.cutoff_distance = 40.0
    except Exception: pass
    try: L.diffuse_factor = 1.0
    except Exception: pass
    try: L.specular_factor = 1.0
    except Exception: pass
    try: L.volume_factor = 1.0
    except Exception: pass
    L.size = 1.0; L.size_y = 1.0; L.shape = 'SQUARE'
    L.name = 'Area'

    # --- Area.001 (AREA) ---
    L = bpy.data.lights.new('Area.001', type='AREA')
    L.energy = 350000.0; L.color = (1.0, 0.9113355875015259, 0.8047811985015869)
    try: L.shadow_soft_size = 0.0
    except Exception: pass
    try: L.use_shadow = True
    except Exception: pass
    try: L.use_custom_distance = False
    except Exception: pass
    try: L.cutoff_distance = 40.0
    except Exception: pass
    try: L.diffuse_factor = 1.0
    except Exception: pass
    try: L.specular_factor = 1.0
    except Exception: pass
    try: L.volume_factor = 1.0
    except Exception: pass
    L.size = 1.0; L.size_y = 1.0; L.shape = 'SQUARE'
    L.name = 'Area.001'

if __name__ == '__main__': run()