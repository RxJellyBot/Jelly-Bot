from enum import Enum, auto


# region Configurations

case_insensitive = True

true_word = ("true", "t", "yes", "y")
false_word = ("false", "f", "no", "n")

# endregion

if case_insensitive:
    true_word = tuple(map(str.lower, true_word))
    false_word = tuple(map(str.lower, false_word))


class StrBoolResult(Enum):
    TRUE = auto()
    FALSE = auto()
    UNKNOWN = auto()

    def to_bool(self) -> bool:
        """
        Cast this enum to :class:`bool`.

        :exception ValueError: the value is unknown.
        """
        if self == self.TRUE:
            return True
        elif self == self.FALSE:
            return False
        else:
            raise ValueError("The result is `UNKNOWN`.")


def str_to_bool(s: str) -> StrBoolResult:
    if case_insensitive:
        s = s.lower()

    if s in true_word:
        return StrBoolResult.TRUE
    elif s in false_word:
        return StrBoolResult.FALSE
    else:
        return StrBoolResult.UNKNOWN
