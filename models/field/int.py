from ._base import BaseField


class IntegerField(BaseField):
    def __init__(self, key, default=None, allow_none=False, readonly=False, auto_cast=True):
        super().__init__(key, default, allow_none, readonly=readonly, auto_cast=auto_cast)

    def is_value_valid(self, value) -> bool:
        return self.is_type_matched(value)

    @classmethod
    def none_obj(cls):
        return 0

    @property
    def expected_types(self):
        return int
