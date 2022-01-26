import bpy

from .operators.IMAGE_OT_screen_rect import IMAGE_OT_screen_rect
from .operators.IMAGE_OT_screen_picker import IMAGE_OT_screen_picker
from .panels import IMAGE_PT_color_picker, VIEW_PT_color_picker, CLIP_PT_color_picker

bl_info = {
    'name': 'Color Picker Pro',
    'author': 'Spencer Magnusson',
    'version': (0, 8, 0),
    'blender': (2, 93, 0),
    'location': '(Image Editor, Clip Editor, and 3D View) -> Misc',
    'description': 'Extends color picker with a few extra features',
    'tracker_url': 'https://github.com/semagnum/color-picker-pro/issues',
    'category': 'Generic',
}

classes = [IMAGE_OT_screen_picker, IMAGE_OT_screen_rect, IMAGE_PT_color_picker, VIEW_PT_color_picker,
           CLIP_PT_color_picker]


def register():
    scene = bpy.types.Scene
    scene.picker_max = bpy.props.FloatVectorProperty(
        default=(1.0, 1.0, 1.0),
        precision=4,
        description='The max RGB values of the picked pixels',
        subtype='COLOR_GAMMA')
    scene.picker_min = bpy.props.FloatVectorProperty(
        default=(0.0, 0.0, 0.0),
        precision=4,
        description='The min RGB values of the picked pixels',
        subtype='COLOR_GAMMA')
    scene.picker_median = bpy.props.FloatVectorProperty(
        default=(0.5, 0.5, 0.5),
        precision=4,
        description='The median RGB values of the picked pixels',
        subtype='COLOR_GAMMA')
    scene.picker_mean = bpy.props.FloatVectorProperty(
        default=(0.5, 0.5, 0.5),
        precision=4,
        description='The mean RGB values of the picked pixels',
        subtype='COLOR_GAMMA')
    scene.custom_size = bpy.props.IntProperty(
        default=10,
        min=2,
        soft_max=100,
        soft_min=5,
        name='Custom Tile Size',
        description='Custom tile size for color picker')
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    scene = bpy.types.Scene
    del scene.picker_max
    del scene.picker_min
    del scene.picker_median
    del scene.picker_mean
    del scene.custom_size
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
