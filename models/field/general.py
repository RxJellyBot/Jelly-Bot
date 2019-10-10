from ._base import BaseField


class GeneralField(BaseField):
    def __init__(self, key, default=None, allow_none=False, readonly=False):
        super().__init__(key, default, allow_none, readonly=readonly, auto_cast=False)

    @classmethod
    def none_obj(cls):
        return None

    def is_value_valid(self, value) -> bool:
        return self.is_type_matched(value)

    @property
    def expected_types(self):
        return bool, int, list, dict, str