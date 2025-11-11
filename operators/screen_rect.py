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
import time

from .draw_config import UNIFORM_LINE_COLOR, IS_AFTER_4_5, config_line_shader

indices = ((0, 1, 2), (2, 1, 3))
try:
    shader = gpu.shader.from_builtin(UNIFORM_LINE_COLOR)
    
except SystemError as e:
    import logging
    log = logging.getLogger(__name__)
    log.warn('Failed to initialize gpu shader, draw will not work as expected')

def draw(operator):
    start_x, end_x = sorted([operator.draw_start_x, operator.draw_end_x])
    start_y, end_y = sorted([operator.draw_start_y, operator.draw_end_y])

    if start_x == -1:
        return

    draw_verts = ((start_x, start_y), (start_x, end_y),
                  (start_x, end_y), (end_x, end_y),
                  (end_x, end_y), (end_x, start_y),
                  (end_x, start_y), (start_x, start_y))

    config_line_shader(shader, (1.0, 1.0, 1.0, 1.0))
    batch = batch_for_shader(shader, 'LINES', {"pos": draw_verts})
    batch.draw(shader)


class ScreenRectOperator(bpy.types.Operator):
    bl_idname = 'image.screen_rect'
    bl_label = 'Rectangle Color Picker'
    bl_description = 'Select a rectangle of the screen and extract its color information'
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):
        self.draw_end_x, self.draw_end_y = event.mouse_region_x, event.mouse_region_y

        context.region.tag_redraw()

        if event.type == 'LEFTMOUSE':
            self.start_x, self.start_y = event.mouse_x, event.mouse_y
            self.draw_start_x, self.draw_start_y = event.mouse_region_x, event.mouse_region_y
        elif event.type == 'RIGHTMOUSE':
            self.cleanup()

            if self.start_x == -1 or self.start_y == -1:
                return {'CANCELLED'}

            self.end_x, self.end_y = event.mouse_x, event.mouse_y
            self.finished = time.time()
        elif self.finished is not None and (time.time() - self.finished) > 0.2:

            start_x, end_x = sorted([self.start_x, self.end_x])
            start_y, end_y = sorted([self.start_y, self.end_y])

            x_len = (end_x - start_x) + 1
            y_len = (end_y - start_y) + 1

            fb = gpu.state.active_framebuffer_get()
            screen_buffer = fb.read_color(start_x, start_y, x_len, y_len, 3, 0, 'FLOAT')

            channels = np.array(screen_buffer.to_list()).reshape((x_len * y_len, 3))

            wm = context.window_manager

            wm.picker_mean = tuple(np.mean(channels, axis=0))
            wm.picker_max = tuple(np.max(channels, axis=0))
            wm.picker_min = tuple(np.min(channels, axis=0))
            wm.picker_median = tuple(np.median(channels, axis=0))
            context.area.tag_redraw()
            return {'FINISHED'}
        elif event.type == 'ESC':
            self.cleanup()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def cleanup(self):
        if self._handler is not None:
            space = getattr(bpy.types, self.space_type)
            space.draw_handler_remove(self._handler, 'WINDOW')
            self._handler = None

        bpy.context.area.header_text_set(None)
        bpy.context.window.cursor_modal_restore()

    def invoke(self, context, event):
        self.start_x, self.start_y = -1, -1

        self.draw_start_x, self.draw_start_y = -1, -1
        self.draw_end_x, self.draw_end_y = -1, -1

        self.space_type = context.space_data.__class__.__name__
        space = getattr(bpy.types, self.space_type)
        self._handler = space.draw_handler_add(draw, (self,), 'WINDOW', 'POST_PIXEL')

        self.finished = None

        context.area.header_text_set('Left click to set first corner of rectangle, '
                                     'right click to set opposite corner, '
                                     'Escape key to cancel')
        context.window.cursor_modal_set('CROSSHAIR')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
