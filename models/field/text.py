import re

from ._base import BaseField


class TextField(BaseField):
    def __init__(self, key, text: str = None, regex: str = None, allow_none=False, maxlen=2000):
        self._regex = regex
        self._maxlen = maxlen
        super().__init__(key, text, allow_none)

    def is_value_valid(self, value) -> bool:
        return self.is_type_matched(value) \
               and ((self._allow_none and value is None)
                    or ((self._regex is None or re.match(self._regex, value)) and len(value) < self._maxlen))

    @classmethod
    def none_obj(cls):
        return ""

    @property
    def expected_types(self):
        return str
