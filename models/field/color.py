from extutils.color import Color, ColorFactory

from ._base import BaseField
from .exceptions import FieldValueInvalidError, FieldTypeMismatchError


class ColorField(BaseField):
    def __init__(self, key, **kwargs):
        """
        Default Properties Overrided:

        - ``allow_none`` - ``False``

        .. seealso::
            Check the document of :class:`BaseField` for other default properties.
        """
        if "allow_none" not in kwargs:
            kwargs["allow_none"] = False

        super().__init__(key, **kwargs)

    @property
    def expected_types(self):
        return Color, int, str

    def none_obj(self):
        return ColorFactory.DEFAULT

    def _check_value_valid_not_none(self, value):
        if isinstance(value, int):
            if Color.color_num_valid(value):
                return
            else:
                raise FieldValueInvalidError(self.key, value)
        elif isinstance(value, str):
            try:
                ColorFactory.from_hex(value)
            except ValueError:
                raise FieldValueInvalidError(self.key, value)
        elif isinstance(value, Color):
            pass
        else:
            raise FieldTypeMismatchError(self.key, type(value), value, self.expected_types)

    def _cast_to_desired_type(self, value):
        # Data store in the database is int
        if isinstance(value, int):
            return Color(value)
        else:
            return ColorFactory.from_hex(value)
