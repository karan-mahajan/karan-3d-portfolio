import bpy

def run():
    print('[01_texts] embedded text blocks')
    t = bpy.data.texts.new('changeViewportColor')
    t.use_fake_user = True
    t.from_string('# Change viewport color of every child of the selected collection\n\nimport bpy\n\n# Ensure a collection is selected\nselected_collection = bpy.context.view_layer.active_layer_collection.collection\n\nif selected_collection:\n    print(f"Selected Collection: {selected_collection.name}")\n\n    # Optionally, loop through objects in the child collection\n    for obj in selected_collection.objects:\n        obj.color = (0.229465, 1, 0.893311, 1)\n\n\nelse:\n    print("No collection is selected.")')
    t = bpy.data.texts.new('getRelativeLocation')
    t.use_fake_user = True
    t.from_string("import bpy\n\nobj = bpy.context.active_object\n\nlocal_matrix = obj.parent.matrix_world.inverted() @ obj.matrix_world\nlocal_position = local_matrix.to_translation()\nprint(f'{local_position.x}, {local_position.y}')")
    t = bpy.data.texts.new('getWhispersForbiddenAreas')
    t.use_fake_user = True
    t.from_string('s')

if __name__ == '__main__': run()