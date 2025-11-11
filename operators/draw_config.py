import bpy
import gpu

IS_BEFORE_3_4 = bpy.app.version < (3, 4, 0)
IS_AFTER_4_5 = bpy.app.version >= (4, 5, 0)

IS_UPDATING = False

if IS_BEFORE_3_4:
    UNIFORM_COLOR = '2D_UNIFORM_COLOR'
else:
    UNIFORM_COLOR = 'UNIFORM_COLOR'

if IS_BEFORE_3_4:
    UNIFORM_LINE_COLOR = '2D_UNIFORM_COLOR'
else:
    UNIFORM_LINE_COLOR = 'POLYLINE_UNIFORM_COLOR'


def config_line_shader(shader, color):
    shader.uniform_float('color', color)
    if IS_AFTER_4_5:
        shader.uniform_float("viewportSize", gpu.state.viewport_get()[2:])
        shader.uniform_float("lineWidth", 1.0)