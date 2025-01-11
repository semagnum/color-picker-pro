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


if "bpy" in locals():
    import importlib
    import os
    import sys
    import types

    def reload_package(package):
        assert (hasattr(package, '__package__'))
        fn = package.__file__
        fn_dir = os.path.dirname(fn) + os.sep
        module_visit = {fn}
        del fn

        def reload_recursive_ex(module):
            module_iter = (
                module_child
                for module_child in vars(module).values()
                if isinstance(module_child, types.ModuleType)
            )
            for module_child in module_iter:
                fn_child = getattr(module_child, '__file__', None)
                if (fn_child is not None) and fn_child.startswith(fn_dir) and fn_child not in module_visit:
                    # print('Reloading:', fn_child, 'from', module)
                    module_visit.add(fn_child)
                    reload_recursive_ex(module_child)

            importlib.reload(module)

        return reload_recursive_ex(package)

    reload_package(sys.modules[__name__])


import bpy

from . import operators, panels

bl_info = {
    'name': 'Color Picker Pro',
    'author': 'Spencer Magnusson',
    'version': (1, 1, 0),
    'blender': (3, 2, 0),
    'location': '(Image Editor, Clip Editor, and 3D View) -> Misc',
    'description': 'Extends color picker with a few extra features',
    'tracker_url': 'https://github.com/semagnum/color-picker-pro/issues',
    'category': 'Generic',
}

NAME = bl_info['name']


def update_color(self, context):
    wm = self

    if not wm.update_target or not wm.update_source:
        return

    prop_real = eval(wm.update_target)
    median_real = getattr(wm, wm.update_source)

    prop_real[0] = median_real[0]
    prop_real[1] = median_real[1]
    prop_real[2] = median_real[2]


window_manager_props = [
    ('picker_max', bpy.props.FloatVectorProperty(
        default=(1.0, 1.0, 1.0),
        precision=4,
        name=NAME + ' Max',
        description='The max RGB values of the picked pixels',
        subtype='COLOR_GAMMA')),
    ('picker_min', bpy.props.FloatVectorProperty(
        default=(0.0, 0.0, 0.0),
        precision=4,
        name=NAME + ' Min',
        description='The min RGB values of the picked pixels',
        subtype='COLOR_GAMMA')),
    ('picker_median', bpy.props.FloatVectorProperty(
        default=(0.5, 0.5, 0.5),
        precision=4,
        name=NAME + ' Median',
        description='The median RGB values of the picked pixels',
        update=update_color,
        subtype='COLOR_GAMMA')),
    ('picker_mean', bpy.props.FloatVectorProperty(
        default=(0.5, 0.5, 0.5),
        precision=4,
        name=NAME + ' Mean',
        description='The mean RGB values of the picked pixels',
        subtype='COLOR_GAMMA')),
    ('custom_size', bpy.props.IntProperty(
        default=10,
        min=2,
        soft_max=100,
        soft_min=5,
        name='Custom Size',
        subtype='PIXEL',
        description='Custom tile size for color picker')),
    ('update_source', bpy.props.StringProperty(
        default='',
        options={'HIDDEN'}
    )),
    ('update_target', bpy.props.StringProperty(
        default='',
        options={'HIDDEN'}
    ))
]


def register():
    window_manager = bpy.types.WindowManager

    for name, prop in window_manager_props:
        setattr(window_manager, name, prop)

    operators.register()
    panels.register()


def unregister():
    panels.unregister()
    operators.unregister()

    for name, _ in window_manager_props:
        try:
            delattr(bpy.types.WindowManager, name)
        except AttributeError:
            pass


if __name__ == '__main__':
    register()
