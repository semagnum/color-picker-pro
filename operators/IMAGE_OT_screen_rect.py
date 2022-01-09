import bpy
import bgl
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

            x_len = (end_x - start_x)
            buffer_size = (end_y - start_y) * x_len
            bgl.glBindFramebuffer(bgl.GL_READ_FRAMEBUFFER, 0)
            screen_buffer = bgl.Buffer(bgl.GL_FLOAT, [buffer_size, 3])

            for x_ind, x in enumerate(range(start_x, end_x)):
                for y_ind, y in enumerate(range(start_y, end_y)):
                    index = y_ind * x_len + x_ind
                    bgl.glReadPixels(x, y, 1, 1, bgl.GL_RGB, bgl.GL_FLOAT, screen_buffer[index])

            channels = np.array(screen_buffer)
            context.scene.picker_mean = tuple(np.mean(channels, axis=0))
            context.scene.picker_max = tuple(np.max(channels, axis=0))
            context.scene.picker_min = tuple(np.min(channels, axis=0))
            context.scene.picker_median = tuple(np.median(channels, axis=0))
            context.area.tag_redraw()
            return {'FINISHED'}
        elif event.type == 'ESC':
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.start_x, self.start_y = -1, -1
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
