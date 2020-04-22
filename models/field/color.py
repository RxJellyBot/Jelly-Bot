from extutils.color import Color, ColorFactory

from ._base import BaseField


class ColorField(BaseField):
    def __init__(self, key, allow_none=False):
        super().__init__(key, allow_none=allow_none)

    @property
    def expected_types(self):
        return Color

    @classmethod
    def none_obj(cls):
        return ColorFactory.DEFAULT

    def _cast_to_desired_type_(self, value):
        # Data store in the database is int
        if isinstance(value, int):
            return Color(value)
        else:
            return ColorFactory.from_hex(value)
