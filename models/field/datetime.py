from datetime import datetime, timezone

from extutils.dt import is_tz_naive

from ._base import BaseField, FieldInstance


class DateTimeField(BaseField):
    def __init__(self, key, default=None, allow_none=False, readonly=False, auto_cast=True):
        super().__init__(key, default, allow_none, readonly=readonly,
                         auto_cast=auto_cast, inst_cls=DateTimeFieldInstance)

    @classmethod
    def none_obj(cls):
        return datetime.min.replace(tzinfo=timezone.utc)

    @property
    def expected_types(self):
        return datetime


class DateTimeFieldInstance(FieldInstance):
    def force_set(self, value: datetime, skip_type_check=False):
        if is_tz_naive(value):
            value = value.replace(tzinfo=timezone.utc)

        super().force_set(value, skip_type_check=skip_type_check)
