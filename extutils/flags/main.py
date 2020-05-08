from enum import Enum
from typing import Union

from .mongo import register_encoder


__all__ = [
    "FlagCodeEnum", "FlagSingleEnum", "FlagDoubleEnum", "FlagPrefixedDoubleEnum", "FlagOutcomeMixin",
    "is_flag_class", "is_flag_single", "is_flag_double", "is_flag_instance"
]


def is_flag_instance(inst):
    return isinstance(inst, FlagCodeMixin)


def is_flag_class(cls):
    return issubclass(cls, FlagCodeMixin)


def is_flag_single(cls):
    return issubclass(cls, FlagSingleMixin)


def is_flag_double(cls):
    return issubclass(cls, FlagDoubleMixin)


class FlagMixin:
    @classmethod
    def default(cls):
        raise ValueError(f"Default in {cls.__qualname__} not implemented.")


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
            return self.code == other
        elif isinstance(other, str):
            if other.isnumeric():
                return self.code == int(other)
            elif hasattr(self, "name"):
                return self.name == other
            else:
                return self.code_str == other

        return super().__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self._code))

    def _cmp_(self, other) -> int:
        if isinstance(other, self.__class__):
            return self._code - other._code
        elif isinstance(other, int):
            return self._code - other
        else:
            raise TypeError(f"Not comparable. ({type(self).__qualname__} & {type(other).__qualname__})")

    @property
    def code(self) -> int:
        return self._code

    @property
    def code_str(self) -> str:
        return f"{self._code}"

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

    @property
    def code_str(self) -> str:
        return f"{self._code}"

    def __eq__(self, other):
        if isinstance(other, str):
            eq = self.code_str == other
            if eq:
                return eq

            if other.isnumeric():
                return self.code == int(other)

        return super().__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self._code))


class FlagPrefixedDoubleMixin(FlagDoubleMixin):
    def __init__(self, code: int, key: str, description: str):
        super().__init__(code, key, description)
        self._desc = description

    @property
    def code_prefix(self) -> str:
        raise NotImplementedError()

    @property
    def description(self) -> str:
        return self._desc

    @property
    def code_str(self) -> str:
        return f"{self.code_prefix}{self._code}"

    def __hash__(self):
        return hash((self.__class__, self._code))

    def __eq__(self, other):
        return super().__eq__(other)


class FlagEnumMixin:
    @classmethod
    def cast(cls, item: Union[str, int], *, silent_fail=False):
        """
        Cast ``item`` to the corresponding :class:`FlagEnumMixin`.
        ``item`` can only be either :class:`str` or :class:`int`.

        :param item: The item to be casted. Can be the name or the code of the enum.
        :param silent_fail: Indicate if this function should throw an error if casting failed.
        :return: Casted enum.
        :exception TypeError: The type of the `item` does not match the type which can be casted.
        :exception ValueError: The value does not match any of the element in the enum.
        """
        if isinstance(item, cls):
            return item

        if not type(item) in (str, int):
            raise TypeError(f"Source type ({type(item)}) for casting not handled.")

        # noinspection PyTypeChecker
        for i in list(cls):
            if i == item:
                return i

        if silent_fail:
            return None
        else:
            raise ValueError(f"`{cls.__qualname__}` casting failed. Item: {item} Type: {type(item)}")

    @classmethod
    def contains(cls, item):
        if not type(item) in (str, int, cls):
            return False

        # noinspection PyTypeChecker
        for i in list(cls):
            if i == item:
                return True

        return False


class FlagCodeEnum(FlagCodeMixin, FlagEnumMixin, Enum):
    pass


class FlagSingleEnum(FlagSingleMixin, FlagEnumMixin, Enum):
    pass


class FlagDoubleEnum(FlagDoubleMixin, FlagEnumMixin, Enum):
    pass


class FlagPrefixedDoubleEnum(FlagPrefixedDoubleMixin, FlagEnumMixin, Enum):
    @property
    def code_prefix(self) -> str:
        raise NotImplementedError()


class FlagOutcomeMixin(FlagCodeMixin):
    @property
    def is_success(self):
        return self._code < 0
