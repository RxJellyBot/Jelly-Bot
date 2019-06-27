from extutils.color import Color, ColorFactory

from ._base import BaseField


class ColorField(BaseField):
    def __init__(self, key, allow_none=False):
        super().__init__(key, allow_none=allow_none)

    @property
    def expected_types(self):
        return Color

    def is_value_valid(self, value) -> bool:
        return self.is_type_matched(value)

    @classmethod
    def none_obj(cls):
        return ColorFactory.BLACK
