from ._base import BaseField


class BooleanField(BaseField):
    def __init__(self, key, bool_: bool = None, allow_none=False, readonly=False):
        super().__init__(key, bool_, allow_none, readonly=readonly)

    @classmethod
    def none_obj(cls):
        return False

    def is_value_valid(self, value) -> bool:
        return self.is_type_matched(value)

    @property
    def expected_types(self):
        return bool, int
