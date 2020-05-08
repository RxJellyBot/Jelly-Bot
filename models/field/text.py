import re
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from ._base import BaseField
from .exceptions import FieldInvalidUrl, FieldMaxLengthReached, FieldRegexNotMatch, FieldEmptyValueNotAllowed


class TextField(BaseField):
    def __init__(self, key, *, regex: str = None, maxlen=2000, must_have_content=False, **kwargs):
        if "allow_none" not in kwargs:
            kwargs["allow_none"] = False

        self._regex = regex
        self._maxlen = maxlen
        self._must_have_content = must_have_content

        super().__init__(key, **kwargs)

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
    def __init__(self, key, **kwargs):
        if "allow_none" not in kwargs:
            kwargs["allow_none"] = False
        if "readonly" not in kwargs:
            kwargs["readonly"] = True
        if "auto_cast" not in kwargs:
            kwargs["auto_cast"] = True

        super().__init__(key, **kwargs)

    @classmethod
    def none_obj(cls):
        return ""

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
