
from datetime import datetime, timezone
from typing import Union

from extutils.dt import is_tz_naive, parse_to_dt

from ._base import BaseField, FieldInstance
from .exceptions import FieldValueInvalid


class DateTimeField(BaseField):
    def __init__(self, key, **kwargs):
        if "inst_cls" not in kwargs:
            kwargs["inst_cls"] = DateTimeFieldInstance
        if "allow_none" not in kwargs:
            kwargs["allow_none"] = False

        super().__init__(key, **kwargs)

    @classmethod
    def none_obj(cls):
        return datetime.min.replace(tzinfo=timezone.utc)

    def _check_value_valid_not_none_(self, value, *, skip_type_check=False, pass_on_castable=False):
        if isinstance(value, str) and parse_to_dt(value) is None:
            raise FieldValueInvalid(self.key, value)

    def _cast_to_desired_type_(self, value):
        if isinstance(value, str):
            return parse_to_dt(value)
        else:
            return value

    @property
    def expected_types(self):
        return datetime, str


class DateTimeFieldInstance(FieldInstance):
    def force_set(self, value: Union[datetime, str], skip_type_check=False):
        super().force_set(value, skip_type_check=skip_type_check)

        # Post process to ensure tz-aware after setting the value
        # Value may be `None` when allowed, so checking `None` here
        if self.value is not None and is_tz_naive(self.value):
            self.value = value.replace(tzinfo=timezone.utc)
