from extutils.color import Color, ColorFactory

from ._base import BaseField
from .exceptions import FieldValueInvalid, FieldTypeMismatch


class ColorField(BaseField):
    def __init__(self, key, **kwargs):
        if "allow_none" not in kwargs:
            kwargs["allow_none"] = False

        super().__init__(key, **kwargs)

    @property
    def expected_types(self):
        return Color, int, str

    @classmethod
    def none_obj(cls):
        return ColorFactory.DEFAULT

    def _check_value_valid_not_none_(self, value):
        if isinstance(value, int):
            if Color.color_num_valid(value):
                return
            else:
                raise FieldValueInvalid(self.key, value)
        elif isinstance(value, str):
            try:
                ColorFactory.from_hex(value)
            except ValueError:
                raise FieldValueInvalid(self.key, value)
        elif isinstance(value, Color):
            pass
        else:
            raise FieldTypeMismatch(self.key, type(value), self.expected_types)

    def _cast_to_desired_type_(self, value):
        # Data store in the database is int
        if isinstance(value, int):
            return Color(value)
        else:
            return ColorFactory.from_hex(value)
