import bpy
import bgl
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

        if event.type in {'MOUSEMOVE', 'LEFTMOUSE'}:
            distance = self.sqrt_length // 2

            start_x = max(event.mouse_x - distance, 0)
            start_y = max(event.mouse_y - distance, 0)

            buffer_size = self.sqrt_length ** 2
            bgl.glBindFramebuffer(bgl.GL_READ_FRAMEBUFFER, 0)
            screen_buffer = bgl.Buffer(bgl.GL_FLOAT, [buffer_size, 3])

            bgl.glReadPixels(start_x, start_y, self.sqrt_length, self.sqrt_length, bgl.GL_RGB, bgl.GL_FLOAT,
                             screen_buffer)

            channels = np.array(screen_buffer)

            dot = np.sum(channels, axis=1)
            max_ind = np.argmax(dot, axis=0)
            min_ind = np.argmin(dot, axis=0)

            context.scene.picker_mean = tuple(np.mean(channels, axis=0))
            context.scene.picker_max = tuple(channels[max_ind])
            context.scene.picker_min = tuple(channels[min_ind])
            context.scene.picker_median = tuple(np.median(channels, axis=0))

        if event.type == 'LEFTMOUSE':
            context.window.cursor_modal_restore()
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.scene.picker_mean = self.prev_mean
            context.scene.picker_median = self.prev_median
            context.scene.picker_max = self.prev_max
            context.scene.picker_min = self.prev_min
            context.window.cursor_modal_restore()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        scene = context.scene
        self.prev_mean = (scene.picker_mean[0], scene.picker_mean[1], scene.picker_mean[2])
        self.prev_median = (scene.picker_median[0], scene.picker_median[1], scene.picker_median[2])
        self.prev_max = (scene.picker_max[0], scene.picker_max[1], scene.picker_max[2])
        self.prev_min = (scene.picker_min[0], scene.picker_min[1], scene.picker_min[2])
        context.window_manager.modal_handler_add(self)
        context.window.cursor_modal_set('EYEDROPPER')
        return {'RUNNING_MODAL'}
