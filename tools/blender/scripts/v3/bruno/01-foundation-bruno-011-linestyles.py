import bpy

def run():
    print('[11_linestyles] linestyles')
    if 'LineStyle' not in bpy.data.linestyles:
        ls = bpy.data.linestyles.new('LineStyle')
    else:
        ls = bpy.data.linestyles['LineStyle']
    ls.use_fake_user = True

if __name__ == '__main__': run()