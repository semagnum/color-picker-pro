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
import gpu
import numpy as np


class IMAGE_OT_screen_picker(bpy.types.Operator):
    bl_idname = 'image.screen_picker'
    bl_label = 'Screen Picker'
    bl_description = 'Extract color information from multiple adjacent pixels'
    bl_options = {'REGISTER'}

    # square root of number of pixels taken into account, 3 is a 3x3 square
    sqrt_length: bpy.props.IntProperty()

    def modal(self, context, event):
        context.area.tag_redraw()
        wm = context.window_manager

        if event.type in {'MOUSEMOVE', 'LEFTMOUSE'}:
            distance = self.sqrt_length // 2

            start_x = max(event.mouse_x - distance, 0)
            start_y = max(event.mouse_y - distance, 0)

            fb = gpu.state.active_framebuffer_get()
            screen_buffer = fb.read_color(start_x, start_y, self.sqrt_length, self.sqrt_length, 3, 0, 'FLOAT')

            channels = np.array(screen_buffer.to_list())\
                .reshape((self.sqrt_length * self.sqrt_length, 3))

            dot = np.sum(channels, axis=1)
            max_ind = np.argmax(dot, axis=0)
            min_ind = np.argmin(dot, axis=0)

            wm.picker_mean = tuple(np.mean(channels, axis=0))
            wm.picker_max = tuple(channels[max_ind])
            wm.picker_min = tuple(channels[min_ind])
            wm.picker_median = tuple(np.median(channels, axis=0))

        if event.type == 'LEFTMOUSE':
            context.window.cursor_modal_restore()
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            wm.picker_mean = self.prev_mean
            wm.picker_median = self.prev_median
            wm.picker_max = self.prev_max
            wm.picker_min = self.prev_min
            context.window.cursor_modal_restore()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        wm = context.window_manager
        self.prev_mean = (wm.picker_mean[0], wm.picker_mean[1], wm.picker_mean[2])
        self.prev_median = (wm.picker_median[0], wm.picker_median[1], wm.picker_median[2])
        self.prev_max = (wm.picker_max[0], wm.picker_max[1], wm.picker_max[2])
        self.prev_min = (wm.picker_min[0], wm.picker_min[1], wm.picker_min[2])
        context.window_manager.modal_handler_add(self)
        context.window.cursor_modal_set('EYEDROPPER')
        return {'RUNNING_MODAL'}
