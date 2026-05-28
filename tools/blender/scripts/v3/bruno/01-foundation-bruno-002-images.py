# Copied verbatim from folio-2025/scripts/blender_world_steps/steps/002_images.py
# with the absolute texture-path prefix rebased from folio-2025/ to our local
# tools/blender/scripts/v3/bruno/resources/ copy. Logic is unchanged.
import bpy, os

def run():
    print('[02_images] loading images')
    if 'blackboardLabels.png' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/textures/blackboardLabels.png'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'blackboardLabels.png'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('blackboardLabels.png', width=255, height=256)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('blackboardLabels.png', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'sRGB'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'bowlingLabelStrike.png' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/textures/bowlingLabelStrike.png'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'bowlingLabelStrike.png'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('bowlingLabelStrike.png', width=128, height=32)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('bowlingLabelStrike.png', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'Non-Color'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'careerFreelancer.png' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/textures/career/careerFreelancer.png'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'careerFreelancer.png'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('careerFreelancer.png', width=240, height=60)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('careerFreelancer.png', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'sRGB'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'careerHetic.png' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/textures/career/careerHetic.png'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'careerHetic.png'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('careerHetic.png', width=316, height=60)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('careerHetic.png', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'sRGB'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'careerImmersiveGarden.png' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/textures/career/careerImmersiveGarden.png'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'careerImmersiveGarden.png'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('careerImmersiveGarden.png', width=340, height=60)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('careerImmersiveGarden.png', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'Non-Color'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'careerIRLTeacher.png' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/textures/career/careerIRLTeacher.png'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'careerIRLTeacher.png'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('careerIRLTeacher.png', width=268, height=92)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('careerIRLTeacher.png', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'sRGB'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'careerOnlineTeacher.png' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/textures/career/careerOnlineTeacher.png'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'careerOnlineTeacher.png'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('careerOnlineTeacher.png', width=332, height=92)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('careerOnlineTeacher.png', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'sRGB'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'careerUzik.png' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/textures/career/careerUzik.png'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'careerUzik.png'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('careerUzik.png', width=168, height=60)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('careerUzik.png', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'Non-Color'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'circuitAirDancerFace.png' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/textures/circuitAirDancerFace.png'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'circuitAirDancerFace.png'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('circuitAirDancerFace.png', width=128, height=128)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('circuitAirDancerFace.png', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'sRGB'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'circuitBrand.png' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/textures/circuitBrand.png'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'circuitBrand.png'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('circuitBrand.png', width=512, height=128)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('circuitBrand.png', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'sRGB'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'circuitLogoThreejs.png' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/textures/circuitLogoThreejs.png'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'circuitLogoThreejs.png'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('circuitLogoThreejs.png', width=128, height=128)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('circuitLogoThreejs.png', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'sRGB'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'circuitLogoWebgl.png' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/textures/circuitLogoWebgl.png'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'circuitLogoWebgl.png'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('circuitLogoWebgl.png', width=256, height=128)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('circuitLogoWebgl.png', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'sRGB'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'circuitLogoWebgpu.png' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/textures/circuitLogoWebgpu.png'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'circuitLogoWebgpu.png'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('circuitLogoWebgpu.png', width=128, height=128)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('circuitLogoWebgpu.png', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'sRGB'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'cookieBanner.png' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/textures/cookieBanner.png'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'cookieBanner.png'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('cookieBanner.png', width=314, height=500)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('cookieBanner.png', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'sRGB'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'labCarpet.png' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/textures/labCarpet.png'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'labCarpet.png'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('labCarpet.png', width=314, height=451)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('labCarpet.png', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'sRGB'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'palette' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/palette.png'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'palette'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('palette', width=128, height=4)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('palette', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'sRGB'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'projectsCarpet.png' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/textures/projectsCarpet.png'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'projectsCarpet.png'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('projectsCarpet.png', width=314, height=451)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('projectsCarpet.png', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'sRGB'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'projectsLabels.png' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/textures/projectsLabels.png'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'projectsLabels.png'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('projectsLabels.png', width=218, height=60)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('projectsLabels.png', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'Non-Color'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'slabs.png' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/textures/slabs.png'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'slabs.png'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('slabs.png', width=256, height=256)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('slabs.png', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'sRGB'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'stylized-map.png' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/textures/stylized-map.png'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'stylized-map.png'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('stylized-map.png', width=128, height=128)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('stylized-map.png', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'sRGB'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'terrain.png' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/static/terrain/terrain.png'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'terrain.png'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('terrain.png', width=512, height=512)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('terrain.png', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'Non-Color'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'terrainAlpha' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/static/terrain/terrain.png'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'terrainAlpha'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('terrainAlpha', width=1024, height=1024)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('terrainAlpha', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'Non-Color'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'terrainFurnitures' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/textures/terrainFurniture.exr'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'terrainFurnitures'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('terrainFurnitures', width=512, height=512)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('terrainFurnitures', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'Non-Color'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'terrainGrass' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/textures/terrainGrass.exr'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'terrainGrass'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('terrainGrass', width=512, height=512)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('terrainGrass', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'Non-Color'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass
    if 'terrainWater' not in bpy.data.images:
        _path = '/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/resources/textures/terrainWater.exr'
        try:
            if os.path.exists(_path):
                img = bpy.data.images.load(_path, check_existing=False)
                img.name = 'terrainWater'
            else:
                print('  missing:', _path)
                img = bpy.data.images.new('terrainWater', width=512, height=512)
                img.filepath = _path
        except Exception as _e:
            print('  load failed:', _e)
            img = bpy.data.images.new('terrainWater', width=1, height=1)
        try: img.source = 'FILE'
        except Exception: pass
        try: img.colorspace_settings.name = 'Non-Color'
        except Exception: pass
        try: img.alpha_mode = 'STRAIGHT'
        except Exception: pass

if __name__ == '__main__': run()