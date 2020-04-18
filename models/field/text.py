import re
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from ._base import BaseField
from .exceptions import FieldInvalidUrl, FieldMaxLengthReached, FieldRegexNotMatch, FieldEmptyValueNotAllowed


class TextField(BaseField):
    def __init__(self, key, default=None, regex: str = None, allow_none=False, maxlen=2000,
                 must_have_content=False, auto_cast=True):
        self._regex = regex
        self._maxlen = maxlen
        self._must_have_content = must_have_content
        super().__init__(key, default, allow_none, auto_cast=auto_cast)

    def _check_value_valid_not_none_(self, value, *, skip_type_check=False, pass_on_castable=False):
        # Length check
        if len(value) > self._maxlen:
            raise FieldMaxLengthReached(self.key, len(value), self._maxlen)

        # Regex check
        if self._regex is not None and not re.match(self._regex, value):
            raise FieldRegexNotMatch(self.key, value, self._regex)

        # Empty Value
        if self._must_have_content and len(value) == 0:
            raise FieldEmptyValueNotAllowed(self.key)

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

    def _check_value_valid_not_none_(self, value, *, skip_type_check=False, pass_on_castable=False):
        if not UrlField.is_valid_url(value):
            raise FieldInvalidUrl(self.key, value)

    @staticmethod
    def is_valid_url(url) -> bool:
        try:
            URLValidator()(url)
        except ValidationError:
            return False

        return True
