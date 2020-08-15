"""Module of extensions on :class:`bool`."""
from enum import Enum, auto
from typing import Any

# region Configurations

CASE_INSENSITIVE = True

WORD_TRUE = ("true", "t", "yes", "y")
WORD_FALSE = ("false", "f", "no", "n")

# endregion

if CASE_INSENSITIVE:
    WORD_TRUE = tuple(map(str.lower, WORD_TRUE))
    WORD_FALSE = tuple(map(str.lower, WORD_FALSE))


class StrBoolResult(Enum):
    """Result :class:`Enum` to indicate the parsing result."""

    TRUE = auto()
    FALSE = auto()
    UNKNOWN = auto()

    def to_bool(self) -> bool:
        """
        Cast this :class:`Enum` to :class:`bool`.

        :raises ValueError: the value is unknown.
        """
        if self == self.TRUE:
            return True

        if self == self.FALSE:
            return False

        raise ValueError("The result is `UNKNOWN`.")


def to_bool(str_: Any) -> StrBoolResult:
    """
    Attempt to parse ``str_`` to :class:`bool`. Result is stored as :class:`StrBoolResult`.

    If ``str_`` is not a :class:`str`, it will be force-casted to :class:`str` by calling ``str(str_)``.

    :param str_: item to be parsed
    :return: a `StrBoolResult` indicating the parsing result
    """
    if isinstance(str_, bool):
        return StrBoolResult.TRUE if str_ else StrBoolResult.FALSE

    if not isinstance(str_, str):
        str_ = str(str_)

    if CASE_INSENSITIVE:
        str_ = str_.lower()

    if str_ in WORD_TRUE:
        return StrBoolResult.TRUE

    if str_ in WORD_FALSE:
        return StrBoolResult.FALSE

    return StrBoolResult.UNKNOWN
