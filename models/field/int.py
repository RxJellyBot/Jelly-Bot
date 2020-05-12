from ._base import BaseField
from .exceptions import FieldValueNegative


class IntegerField(BaseField):
    def __init__(self, key, *, positive_only=False, **kwargs):
        """
        Default Properties Overrided:

        - ``allow_none`` - ``False``

        .. seealso::
            Check the document of :class:`BaseField` for other default properties.
        """
        if "allow_none" not in kwargs:
            kwargs["allow_none"] = False

        self._positive_only = positive_only

        super().__init__(key, **kwargs)

    @property
    def positive_only(self):
        return self._positive_only

    def _check_value_valid_not_none_(self, value):
        if value < 0 and self.positive_only:
            raise FieldValueNegative(self.key, value)

    @classmethod
    def none_obj(cls):
        return 0

    @property
    def expected_types(self):
        return int, float

    def json_schema_property(self, allow_additional=True) -> dict:
        return {
            "bsonType": "int"
        }
