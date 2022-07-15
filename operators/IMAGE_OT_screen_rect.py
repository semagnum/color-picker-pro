import bpy
import gpu
import numpy as np


class IMAGE_OT_screen_rect(bpy.types.Operator):
    bl_idname = 'image.screen_rect'
    bl_label = 'Screen Mean'
    bl_description = 'Select a rectangle of the screen and extract its color information'
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):
        if event.type == 'LEFTMOUSE':
            self.start_x, self.start_y = event.mouse_x, event.mouse_y
        elif event.type == 'RIGHTMOUSE':
            if self.start_x == -1 or self.start_y == -1:
                return {'CANCELLED'}
            start_x, end_x = sorted([self.start_x, event.mouse_x])
            start_y, end_y = sorted([self.start_y, event.mouse_y])

            x_len = (end_x - start_x) + 1
            y_len = (end_y - start_y) + 1

            fb = gpu.state.active_framebuffer_get()
            screen_buffer = fb.read_color(start_x, start_y, x_len, y_len, 3, 0, 'FLOAT')

            channels = np.array(screen_buffer.to_list())\
                .reshape((x_len * y_len, 3))

            wm = context.window_manager

            wm.picker_mean = tuple(np.mean(channels, axis=0))
            wm.picker_max = tuple(np.max(channels, axis=0))
            wm.picker_min = tuple(np.min(channels, axis=0))
            wm.picker_median = tuple(np.median(channels, axis=0))
            context.area.tag_redraw()
            return {'FINISHED'}
        elif event.type == 'ESC':
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.start_x, self.start_y = -1, -1
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
