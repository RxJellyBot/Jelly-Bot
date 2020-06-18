from ._base import BaseField
from .exceptions import FieldValueNegativeError


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

    def _check_value_valid_not_none(self, value):
        if value < 0 and self.positive_only:
            raise FieldValueNegativeError(self.key, value)

    def none_obj(self):
        return 0

    @property
    def expected_types(self):
        return int, float
