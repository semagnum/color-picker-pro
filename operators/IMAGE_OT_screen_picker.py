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
from gpu_extras.batch import batch_for_shader
import numpy as np

vertices = ((0, 0), (50, 0),
            (0, -50), (50, -50))
indices = ((0, 1, 2), (2, 1, 3), (0, 1, 1), (1, 2, 2), (2, 2, 3), (3, 0, 0))
fill_shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
edge_shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')

def draw(operator):
    m_x, m_y = operator.x, operator.y
    length = operator.sqrt_length + 5
    curr_color = tuple(list(operator.curr_color) + [1.0])
    fill_shader.uniform_float("color", curr_color)

    draw_verts = tuple((m_x + x + length, m_y + y - length) for x,y in vertices)
    batch = batch_for_shader(fill_shader, 'TRIS', {"pos": draw_verts}, indices=indices)
    batch.draw(fill_shader)

    edge_shader.uniform_float("color", (1.0, 0.0, 0.0, 1.0))

    edges = (draw_verts[0], draw_verts[1],
             draw_verts[0], draw_verts[2],
             draw_verts[2], draw_verts[3],
             draw_verts[1], draw_verts[3])

    edge_batch = batch_for_shader(edge_shader, 'LINES', {"pos": edges})
    edge_batch.draw(edge_shader)


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

            self.x = event.mouse_region_x
            self.y = event.mouse_region_y

            fb = gpu.state.active_framebuffer_get()
            screen_buffer = fb.read_color(start_x, start_y, self.sqrt_length, self.sqrt_length, 3, 0, 'FLOAT')

            channels = np.array(screen_buffer.to_list()).reshape((self.sqrt_length * self.sqrt_length, 3))

            curr_picker_buffer = fb.read_color(event.mouse_x, event.mouse_y, 1, 1, 3, 0, 'FLOAT')
            self.curr_color = np.array(curr_picker_buffer.to_list()).reshape(-1)

            dot = np.sum(channels, axis=1)
            max_ind = np.argmax(dot, axis=0)
            min_ind = np.argmin(dot, axis=0)

            wm.picker_mean = tuple(np.mean(channels, axis=0))
            wm.picker_max = tuple(channels[max_ind])
            wm.picker_min = tuple(channels[min_ind])
            wm.picker_median = tuple(np.median(channels, axis=0))

        if event.type == 'LEFTMOUSE':
            context.window.cursor_modal_restore()
            space = getattr(bpy.types, self.space_type)
            space.draw_handler_remove(self._handler, 'WINDOW')
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            wm.picker_mean = self.prev_mean
            wm.picker_median = self.prev_median
            wm.picker_max = self.prev_max
            wm.picker_min = self.prev_min
            context.window.cursor_modal_restore()

            space = getattr(bpy.types, self.space_type)
            space.draw_handler_remove(self._handler, 'WINDOW')
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

        self.space_type = context.space_data.__class__.__name__
        space = getattr(bpy.types, self.space_type)
        self._handler = space.draw_handler_add(draw, (self,), 'WINDOW', 'POST_PIXEL')

        return {'RUNNING_MODAL'}
