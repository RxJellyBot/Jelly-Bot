from enum import Enum

from .mongo import register_encoder


class FlagMixin:
    @classmethod
    def default(cls):
        raise ValueError(f"Default in {cls.__name__} not implemented.")


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

    # noinspection PyUnresolvedReferences
    def __str__(self):
        return f"<{self.__class__.__name__}.{self.name}: {self._code}>"

    def __repr__(self):
        return self.__str__()


class FlagSingleMixin(FlagCodeMixin):
    def __init__(self, code: int, key: str):
        super().__init__(code)
        self._key = key

    @property
    def key(self):
        return self._key

    # noinspection PyUnresolvedReferences
    def __str__(self):
        return f"<{self.__class__.__name__}.{self.name}: {self._code} ({self._key})>"


class FlagDoubleMixin(FlagSingleMixin):
    def __init__(self, code: int, key: str, description: str):
        super().__init__(code, key)
        self._desc = description

    @property
    def description(self):
        return self._desc


class FlagEnumMixin:
    @classmethod
    def contains(cls, item):
        if isinstance(item, str) and not isinstance(cls, FlagSingleMixin):
            return False

        if isinstance(item, int):
            det_fn = FlagEnumMixin._match_int_
        elif isinstance(item, str):
            det_fn = FlagEnumMixin._match_str_
        else:
            return False

        for i in list(cls):
            if det_fn(i, item):
                return True

        return False

    @staticmethod
    def _match_int_(enum, item):
        return enum.code == item

    @staticmethod
    def _match_str_(enum, item):
        return enum.key == item or enum.name == item


class FlagCodeEnum(FlagCodeMixin, FlagEnumMixin, Enum):
    pass


class FlagSingleEnum(FlagSingleMixin, FlagEnumMixin, Enum):
    pass


class FlagDoubleEnum(FlagDoubleMixin, FlagEnumMixin, Enum):
    pass
