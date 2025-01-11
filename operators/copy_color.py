import logging

import bpy

logger = logging.getLogger(__name__)


def get_property_data(data, attr):
    """Gets bl_rna properties from the given attribute"""
    prop_properties = None
    prop = getattr(data, attr, None)
    if prop is not None:
        prop_bl_rna = getattr(data, 'bl_rna', None)
        if prop_bl_rna is not None:
            prop_properties = getattr(prop_bl_rna, 'properties', None)
            if prop_properties is not None:
                prop_properties = prop_properties[attr]

    return prop_properties


def is_valid_color_property(window_manager, full_path):
    """Checks if data path points to a valid color property"""
    valid, report_type, report_message = False, None, None

    if not full_path or '.' not in full_path or any(v in full_path for v in (';', '\n')):
        report_type, report_message = {'ERROR'}, 'Invalid data path!'
        return valid, report_type, report_message

    data, attr = full_path.rsplit('.', maxsplit=1)

    try:
        data_eval = eval(data, {'bpy': bpy}, {})  # prevents anything non-bpy from being used
    except (SyntaxError, AttributeError) as e:
        report_type, report_message = {'ERROR'}, 'Data property evaluation failed'
        logger.error(str(e))
        return valid, report_type, report_message

    if data_eval == window_manager and attr in ('picker_max', 'picker_min', 'picker_median', 'picker_mean'):
        report_type, report_message = {'ERROR'}, 'Cannot update itself, aborting'
        return valid, report_type, report_message

    prop_properties = get_property_data(data_eval, attr)
    if prop_properties is not None:
        data_prop_str_type = prop_properties.__class__.__name__
        if 'FloatProperty' != data_prop_str_type:
            report_type, report_message = {'ERROR'}, 'Can only access FloatProperty, not ' + data_prop_str_type
        elif prop_properties.array_length < 3 or prop_properties.array_length > 4:
            report_type, report_message = {'ERROR'}, 'Property unable to store RGB channels'
        else:
            valid = True

    if valid:
        if 'COLOR_GAMMA' != prop_properties.subtype:
            report_type, report_message = {'WARNING'}, ('Target property is not gamma corrected, '
                                                        'result may be unexpected')
        else:
            report_type, report_message = {'INFO'}, 'Color Picker Pro will now update ' + prop_properties.name

    return valid, report_type, report_message


class CopyColorOperator(bpy.types.Operator):
    bl_idname = 'wm.color_picker_pro_copy_update'
    bl_label = 'Update Color'

    picker_type: bpy.props.EnumProperty(
        name='Picker',
        default='picker_median',
        items=[
            ('picker_max', 'Max', ''),
            ('picker_mean', 'Mean', ''),
            ('picker_median', 'Median', ''),
            ('picker_min', 'Min', ''),
        ]
    )

    prop_to_update: bpy.props.StringProperty(
        name='Data path',
        description=('Full data path to update. '
                     'Right click on the property, select "Copy Full Data Path", '
                     'and paste the path here'),
        default='',
        options={'SKIP_SAVE'}
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        window_manager = context.window_manager
        valid, report_type, report_message = is_valid_color_property(window_manager, self.prop_to_update)

        if not valid:
            self.report(report_type, report_message)
            return {'CANCELLED'}

        window_manager.update_target = self.prop_to_update
        window_manager.update_source = self.picker_type

        self.report(report_type, report_message)

        return {'FINISHED'}


class ClearUpdateOperator(bpy.types.Operator):
    bl_idname = 'wm.color_picker_pro_clear'
    bl_label = 'Clear Updates'
    bl_description = 'Stop further updates to custom property'

    @classmethod
    def poll(cls, context):
        return context.window_manager.update_target or context.window_manager.update_source

    def execute(self, context):
        window_manager = context.window_manager
        window_manager.update_target = ''
        window_manager.update_source = ''
        self.report({'INFO'}, 'Color updates cleared')

        return {'FINISHED'}
