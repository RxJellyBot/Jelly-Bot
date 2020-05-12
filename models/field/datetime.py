from datetime import datetime
from typing import Union

from extutils.dt import is_tz_naive, parse_to_dt, make_tz_aware

from ._base import BaseField, FieldInstance
from .exceptions import FieldValueInvalid


class DateTimeField(BaseField):
    def __init__(self, key, **kwargs):
        """
        Default Properties Overrided:

        - ``allow_none`` - ``False``
        - ``inst_cls`` - :class:`DateTimeFieldInstance`

        .. seealso::
            Check the document of :class:`BaseField` for other default properties.
        """
        if "inst_cls" not in kwargs:
            kwargs["inst_cls"] = DateTimeFieldInstance
        if "allow_none" not in kwargs:
            kwargs["allow_none"] = False

        super().__init__(key, **kwargs)

    @classmethod
    def none_obj(cls):
        return make_tz_aware(datetime.min)

    def _check_value_valid_not_none_(self, value):
        if isinstance(value, str) and parse_to_dt(value) is None:
            raise FieldValueInvalid(self.key, value)

    def cast_to_desired_type(self, value):
        ret = super().cast_to_desired_type(value)

        if isinstance(ret, datetime) and is_tz_naive(ret):
            ret = make_tz_aware(ret)

        return ret

    def _cast_to_desired_type_(self, value):
        if isinstance(value, str):
            return parse_to_dt(value)
        else:
            return value

    @property
    def expected_types(self):
        return datetime, str

    def json_schema_property(self, allow_additional=True) -> dict:
        return {
            "bsonType": "date"
        }


class DateTimeFieldInstance(FieldInstance):
    def force_set(self, value: Union[datetime, str]):
        super().force_set(value)

        # - Post process to ensure tz-aware after setting the value
        # - Checking `None here because `value` could be `None` when allowed
        # - Type checking performed to make sure that the timezone replacement only applied on `datetime`
        if self.value is not None and isinstance(self.value, datetime) and is_tz_naive(self.value):
            self.value = make_tz_aware(self.value)
