from enum import Enum

from .mongo import register_encoder


class FlagMixin:
    @staticmethod
    def default():
        raise NotImplementedError(f"Default in FlagMixin not implemented.")


class FlagCodeMixin(FlagMixin):
    def __new__(cls, *args, **kwargs):
        register_encoder(cls)
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, code: int):
        self._code = code

    def __int__(self):
        return self._code

    def __lt__(self, other):
        return self._cmp_(other) < 0

    def __le__(self, other):
        return self._cmp_(other) <= 0

    def __gt__(self, other):
        return self._cmp_(other) > 0

    def __ge__(self, other):
        return self._cmp_(other) >= 0

    def __eq__(self, other):
        if isinstance(other, int):
            return self._code == other
        else:
            return super().__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self._code))

    def _cmp_(self, other) -> int:
        if isinstance(other, self.__class__):
            return self._code - other._code
        elif isinstance(other, int):
            return self._code - other
        else:
            raise TypeError(f"Not comparable. ({type(self).__name__} & {type(other).__name__})")

    @property
    def code(self):
        return self._code

    def __str__(self):
        return f"<{self.__class__.__name__}.{self.name}: {self._code}>"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def default():
        raise NotImplementedError(f"Default in FlagCodeMixin not implemented.")


class FlagSingleMixin(FlagCodeMixin):
    def __init__(self, code: int, key: str):
        super().__init__(code)
        self._key = key

    @property
    def key(self):
        return self._key

    def __str__(self):
        return f"<{self.__class__.__name__}.{self.name}: {self._code} ({self._key})>"

    @staticmethod
    def default():
        raise NotImplementedError(f"Default in FlagSingleMixin not implemented.")


class FlagDoubleMixin(FlagSingleMixin):
    def __init__(self, code: int, key: str, description: str):
        super().__init__(code, key)
        self._desc = description

    @property
    def description(self):
        return self._desc

    def __str__(self):
        return f"<{self.__class__.__name__}.{self.name}: {self._code} ({self._key}) - {self._desc[:40]}>"

    @staticmethod
    def default():
        raise NotImplementedError(f"Default in FlagDoubleMixin not implemented.")


class FlagCodeEnum(FlagCodeMixin, Enum):
    @staticmethod
    def default():
        raise NotImplementedError(f"Default in FlagCodeEnum not implemented.")


class FlagSingleEnum(FlagSingleMixin, Enum):
    @staticmethod
    def default():
        raise NotImplementedError(f"Default in FlagSingleEnum not implemented.")


class FlagDoubleEnum(FlagDoubleMixin, Enum):
    @staticmethod
    def default():
        raise NotImplementedError(f"Default in FlagDoubleEnum not implemented.")
