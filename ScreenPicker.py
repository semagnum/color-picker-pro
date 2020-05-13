bl_info = {
    "name": "Color Picker Pro",
    "author": "Spencer Magnusson",
    "version": (0, 5),
    "blender": (2, 80, 0),
    "location": "Image Editor, Clip Editor, 3D View",
    "description": "Extends color picker with a few extra features",
    "tracker_url": "https://github.com/semagnum/color-picker-pro/issues",
    "category": "Generic",
}

import bpy
import bgl
import numpy as np

def draw_panel(layout, context):
    layout.prop(context.scene, 'picker_max', text='Max')
    layout.prop(context.scene, 'picker_mean', text='Mean')
    layout.prop(context.scene, 'picker_median', text='Median')
    layout.prop(context.scene, 'picker_min', text='Min')
    layout.operator(IMAGE_OT_screen_picker.bl_idname, text='3x3 Color Picker').sqrt_length = 3
    layout.operator(IMAGE_OT_screen_picker.bl_idname, text='5x5 Color Picker').sqrt_length = 5
    layout.operator(IMAGE_OT_screen_mean.bl_idname, text='Pick Window')

class IMAGE_PT_color_picker(bpy.types.Panel):
    bl_label = "Color Picker Pro"
    bl_idname = "IMAGE_PT_color_picker"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        draw_panel(self.layout, context)

class VIEW_PT_color_picker(bpy.types.Panel):
    bl_label = "Color Picker Pro"
    bl_idname = "VIEW_PT_color_picker"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        draw_panel(self.layout, context)

class CLIP_PT_color_picker(bpy.types.Panel):
    bl_label = "Color Picker Pro"
    bl_idname = "CLIP_PT_color_picker"
    bl_space_type = 'CLIP_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        draw_panel(self.layout, context)

class IMAGE_OT_screen_picker(bpy.types.Operator):
    bl_idname = "image.screen_picker"
    bl_label = "Screen Picker"
    bl_description = "Extract color information from multiple adjacent pixels"
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
            screen_buffer = bgl.Buffer(bgl.GL_FLOAT, [buffer_size,3])
            
            bgl.glReadPixels(start_x, start_y,self.sqrt_length,self.sqrt_length,bgl.GL_RGB,bgl.GL_FLOAT,screen_buffer)
            
            channels = np.array(screen_buffer)
            context.scene.picker_mean = tuple(np.mean(channels, axis=0))
            context.scene.picker_max = tuple(np.max(channels, axis=0))
            context.scene.picker_min = tuple(np.min(channels, axis=0))
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
        self.prev_mean = (context.scene.picker_mean[0], context.scene.picker_mean[1], context.scene.picker_mean[2])
        self.prev_median = (context.scene.picker_median[0], context.scene.picker_median[1], context.scene.picker_median[2])
        self.prev_max = (context.scene.picker_max[0], context.scene.picker_max[1], context.scene.picker_max[2])
        self.prev_min = (context.scene.picker_min[0], context.scene.picker_min[1], context.scene.picker_min[2])
        context.window_manager.modal_handler_add(self)
        context.window.cursor_modal_set('EYEDROPPER')
        return {'RUNNING_MODAL'}

class IMAGE_OT_screen_mean(bpy.types.Operator):
    bl_idname = "image.screen_mean"
    bl_label = "Screen Mean"
    bl_description = "Select a rectangle of the screen and extract its color information"
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
            screen_buffer = bgl.Buffer(bgl.GL_FLOAT, [buffer_size,3])
            
            for x_ind, x in enumerate(range(start_x, end_x)):
                for y_ind, y in enumerate(range(start_y, end_y)):
                    index = y_ind * x_len + x_ind
                    bgl.glReadPixels(x, y,1,1,bgl.GL_RGB,bgl.GL_FLOAT,screen_buffer[index])
            
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

classes = [IMAGE_OT_screen_picker, IMAGE_OT_screen_mean, IMAGE_PT_color_picker, VIEW_PT_color_picker, CLIP_PT_color_picker]

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
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
