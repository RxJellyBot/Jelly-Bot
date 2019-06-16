from datetime import datetime, timezone

from ._base import BaseField


class DateTimeField(BaseField):
    def __init__(self, key, dt: datetime = None, allow_none=False, readonly=False):
        super().__init__(key, dt, allow_none, readonly=readonly)

    @classmethod
    def none_obj(cls):
        return datetime.min

    def is_value_valid(self, value) -> bool:
        return self.is_type_matched(value)

    def set_value(self, value: datetime):
        super().set_value(value.replace(tzinfo=timezone.utc))

    @property
    def expected_types(self):
        return datetime
