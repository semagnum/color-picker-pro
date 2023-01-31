import bpy

from ..operators.IMAGE_OT_screen_picker import IMAGE_OT_screen_picker
from ..operators.IMAGE_OT_screen_rect import IMAGE_OT_screen_rect

panel_title = 'Color Picker Pro'


def draw_panel(layout, context):
    wm = context.window_manager
    layout.prop(wm, 'picker_max', text='Max')
    layout.prop(wm, 'picker_mean', text='Mean')
    layout.prop(wm, 'picker_median', text='Median')
    layout.prop(wm, 'picker_min', text='Min')
    layout.operator(IMAGE_OT_screen_picker.bl_idname, text='3x3 Color Picker', icon='EYEDROPPER').sqrt_length = 3
    layout.operator(IMAGE_OT_screen_picker.bl_idname, text='5x5 Color Picker', icon='EYEDROPPER').sqrt_length = 5
    layout.prop(wm, 'custom_size', slider=True)
    tile_str = str(wm.custom_size)
    custom_label = 'Custom ' + tile_str + 'x' + tile_str + ' Color Picker'
    layout.operator(IMAGE_OT_screen_picker.bl_idname, text=custom_label,
                    icon='EYEDROPPER').sqrt_length = wm.custom_size
    layout.separator()
    layout.operator(IMAGE_OT_screen_rect.bl_idname, text='Rect Color Picker', icon='SELECT_SET')


class IMAGE_PT_color_picker(bpy.types.Panel):
    bl_label = panel_title
    bl_idname = 'IMAGE_PT_color_picker'
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        draw_panel(self.layout, context)


class VIEW_PT_color_picker(bpy.types.Panel):
    bl_label = panel_title
    bl_idname = 'VIEW_PT_color_picker'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        draw_panel(self.layout, context)


class CLIP_PT_color_picker(bpy.types.Panel):
    bl_label = panel_title
    bl_idname = 'CLIP_PT_color_picker'
    bl_space_type = 'CLIP_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        draw_panel(self.layout, context)
