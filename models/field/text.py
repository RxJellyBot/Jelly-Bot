import re
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from ._base import BaseField


class TextField(BaseField):
    def __init__(self, key, default=None, regex: str = None, allow_none=False, maxlen=2000,
                 must_have_content=False, auto_cast=True):
        self._regex = regex
        self._maxlen = maxlen
        self._must_have_content = must_have_content
        super().__init__(key, default, allow_none, auto_cast=auto_cast)

    def is_value_valid(self, value) -> bool:
        return self.is_type_matched(value) \
            and ((self.allow_none and value is None)
                 or ((self._regex is None or re.match(self._regex, value)) and len(value) < self._maxlen)
                 or self.is_none(value)) \
            and (not self._must_have_content or (self._must_have_content and len(value) > 0))

    @classmethod
    def none_obj(cls):
        return ""

    @property
    def expected_types(self):
        return str


class UrlField(BaseField):
    def __init__(self, key, default=None, allow_none=False):
        super().__init__(key, default, allow_none, readonly=True, auto_cast=True)

    @property
    def expected_types(self):
        return str

    def is_value_valid(self, value) -> bool:
        return UrlField.is_valid_url(value)

    @staticmethod
    def is_valid_url(url) -> bool:
        try:
            URLValidator()(url)
        except ValidationError:
            return False

        return True
