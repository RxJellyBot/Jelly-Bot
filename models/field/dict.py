from ._base import BaseField


class DictionaryField(BaseField):
    def __init__(self, key, dict_: dict = None, allow_none=False, readonly=False):
        super().__init__(key, dict_, allow_none, readonly=readonly)

    @classmethod
    def none_obj(cls):
        return {}

    def is_value_valid(self, value) -> bool:
        return self.is_type_matched(value)

    @property
    def expected_types(self):
        return dict
