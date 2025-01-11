"""
Copyright (C) 2023 Spencer Magnusson
semagnum@gmail.com
Created by Spencer Magnusson
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


import bpy

from ..operators import ScreenPickerOperator, ScreenRectOperator, CopyColorOperator, ClearUpdateOperator

panel_title = 'Color Picker Pro'


def draw_panel(layout, context):
    wm = context.window_manager

    layout.use_property_split = True
    layout.use_property_decorate = False

    def draw_picker(layout, attr, **kwargs):
        row = layout.row()
        row.prop(wm, attr, **kwargs)
        if wm.update_source == attr:
            row.operator(ClearUpdateOperator.bl_idname, text='', icon='X')
        else:
            op = row.operator(CopyColorOperator.bl_idname, text='', icon='COPYDOWN')
            op.picker_type = attr

    col = layout.column()
    draw_picker(col, 'picker_max', text='Picked Max')
    draw_picker(col, 'picker_mean', text='Mean')
    draw_picker(col, 'picker_median', text='Median')
    draw_picker(col, 'picker_min', text='Min')

    layout.separator()

    split = layout.split(factor=0.4)
    split.alignment = 'RIGHT'
    split.label(text='Color Picker 3x3')
    split.operator(ScreenPickerOperator.bl_idname, text='', icon='EYEDROPPER').sqrt_length = 3

    split = layout.split(factor=0.4)
    split.alignment = 'RIGHT'
    split.label(text='5x5')
    split.operator(ScreenPickerOperator.bl_idname, text='', icon='EYEDROPPER').sqrt_length = 5

    row = layout.row(align=True)
    row.prop(wm, 'custom_size', slider=True, text='Custom')
    row.operator(ScreenPickerOperator.bl_idname, text='', icon='EYEDROPPER').sqrt_length = wm.custom_size

    split = layout.split(factor=0.4)
    split.alignment = 'RIGHT'
    split.label(text='Rectangle')
    split.operator(ScreenRectOperator.bl_idname, text='', icon='SELECT_SET')


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


_classes_to_register = [IMAGE_PT_color_picker, VIEW_PT_color_picker, CLIP_PT_color_picker]

register, unregister = bpy.utils.register_classes_factory(_classes_to_register)
