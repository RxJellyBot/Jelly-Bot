import re
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from ._base import BaseField
from .exceptions import FieldInvalidUrl, FieldMaxLengthReached, FieldRegexNotMatch, FieldEmptyValueNotAllowed


class TextField(BaseField):
    DEFAULT_MAX_LENGTH = 2000

    def __init__(self, key, *, regex: str = None, maxlen: int = DEFAULT_MAX_LENGTH,
                 must_have_content: int = False, **kwargs):
        """
        The max length of the string is determined by ``maxlen``.

        - Set to ``None`` or :class:`math.inf` for unlimited length.

        .. note::

            Default Properties Overrided:

            - ``allow_none`` - ``False``

            Default Properties Added:

            - ``regex`` - ``None``

            - ``maxlen`` - ``2000``

            - ``must_have_content`` - ``False``

        .. seealso::
            Check the document of :class:`BaseField` for other default properties.

        :param regex: Regex to validate the string
        :param maxlen: Max length of the string
        :param must_have_content: If the string must have some content

        :raises FieldMaxLengthReached: if the default value reaches to the max length
        :raises FieldRegexNotMatch: if the regex does not match the default value
        :raises FieldEmptyValueNotAllowed: if the defualt vlaue is empty
        """
        if "allow_none" not in kwargs:
            kwargs["allow_none"] = False

        self._regex = regex
        self._maxlen = maxlen
        self._must_have_content = must_have_content

        super().__init__(key, **kwargs)

    def _check_value_valid_not_none_(self, value):
        if isinstance(value, str):
            # Length check
            if len(value) > self._maxlen:
                raise FieldMaxLengthReached(self.key, len(value), self._maxlen)

            # Regex check
            if self._regex is not None and not re.fullmatch(self._regex, value):
                raise FieldRegexNotMatch(self.key, value, self._regex)

            # Empty Value
            if self._must_have_content and len(value) == 0:
                raise FieldEmptyValueNotAllowed(self.key)

    @classmethod
    def none_obj(cls):
        return ""

    @property
    def expected_types(self):
        return str, int, bool


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

    def _check_value_valid_not_none_(self, value):
        if not UrlField.is_valid_url(value):
            raise FieldInvalidUrl(self.key, value)

    @staticmethod
    def is_valid_url(url) -> bool:
        try:
            URLValidator()(url)
        except ValidationError:
            return False

        return True
