import bpy

from .screen_rect import ScreenRectOperator
from .screen_picker import ScreenPickerOperator
from .copy_color import CopyColorOperator, ClearUpdateOperator

_classes_to_register = [ScreenRectOperator, ScreenPickerOperator, CopyColorOperator, ClearUpdateOperator]

register, unregister = bpy.utils.register_classes_factory(_classes_to_register)
