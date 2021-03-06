"""Main ``Flag`` implementations."""
from enum import Enum
from typing import Union

from .mongo import register_encoder

__all__ = [
    "DuplicatedCodeError",
    "FlagCodeEnum", "FlagSingleEnum", "FlagDoubleEnum", "FlagPrefixedDoubleEnum", "FlagOutcomeMixin",
    "is_flag_class", "is_flag_single", "is_flag_double", "is_flag_instance"
]


class DuplicatedCodeError(Exception):
    """Raised if the flag code is duplicated."""

    def __init__(self, code: int):
        super().__init__(f"Duplicated flag code: {code}")


def is_flag_instance(inst):
    """
    Check if the instance ``inst`` is a ``Flag``.

    :param inst: instance to be checked
    :return: if `inst` is a `Flag`
    """
    return isinstance(inst, FlagCodeMixin)


def is_flag_class(obj):
    """
    Check if the object ``obj`` is a class of :class:`FlagCodeMixin`.

    :param obj: object to be checked
    :return: if `obj` is a `FlagCodeMixin`
    """
    return issubclass(obj, FlagCodeMixin)


def is_flag_single(obj):
    """
    Check if the object ``obj`` is a class of :class:`FlagSingleMixin`.

    :param obj: object to be checked
    :return: if `obj` is a `FlagSingleMixin`
    """
    return issubclass(obj, FlagSingleMixin)


def is_flag_double(obj):
    """
    Check if the object ``obj`` is a class of :class:`FlagDoubleMixin`.

    :param obj: object to be checked
    :return: if `obj` is a `FlagDoubleMixin`
    """
    return issubclass(obj, FlagDoubleMixin)


class FlagMixin:
    """Base class of a ``Flag``."""

    @classmethod
    def default(cls):
        """
        Default value of the ``Flag``.

        :raises ValueError: if not defined but used
        """
        raise ValueError(f"Default in {cls.__qualname__} not implemented.")


class FlagCodeMixin(FlagMixin):
    """
    ``Flag`` with a ``code`` (:class:`int`) only.

    Example:

    >>> class FlagCodeSample(FlagCodeMixin):
    >>>     A = 1
    >>>     B = 2

    where ``1`` and ``2`` are the ``code``.
    """

    def __new__(cls, *args):
        register_encoder(cls)
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, code: int):
        # noinspection PyTypeChecker
        if code in [v.code for v in self.__class__]:
            raise DuplicatedCodeError(code)

        self._code = code

    def __int__(self):
        return self._code

    def __lt__(self, other):
        return self._cmp(other) < 0

    def __le__(self, other):
        return self._cmp(other) <= 0

    def __gt__(self, other):
        return self._cmp(other) > 0

    def __ge__(self, other):
        return self._cmp(other) >= 0

    def __eq__(self, other):
        if isinstance(other, int):
            return self.code == other

        if isinstance(other, str):
            if other.isnumeric():
                return self.code == int(other)

            if hasattr(self, "name"):
                return self.name == other

            return self.code_str == other

        return super().__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self._code))

    def _cmp(self, other) -> int:
        if isinstance(other, self.__class__):
            return self._code - other.code

        if isinstance(other, int):
            return self._code - other

        raise TypeError(f"Not comparable. ({type(self).__qualname__} & {type(other).__qualname__})")

    @property
    def code(self) -> int:
        """
        Get the code of the flag member.

        :return: code of the flag member
        """
        return self._code

    @property
    def code_str(self) -> str:
        """
        Get the code of the flag member as a :class:`str`.

        :return: code of the enum memebr as a string
        """
        return f"{self._code}"

    # noinspection PyUnresolvedReferences
    def __str__(self):
        return f"<{self.__class__.__name__}.{self.name}: {self._code}>"

    def __repr__(self):
        return self.__str__()


class FlagSingleMixin(FlagCodeMixin):
    """
    ``Flag`` with a ``code`` (:class:`int`) and a ``key`` (:class:`str`).

    Example:

    >>> class FlagSingleSample(FlagSingleMixin):
    >>>     A = 1, "ONE"
    >>>     B = 2, "TWO"

    where ``1`` and ``2`` are the ``code`` and ``"ONE"``, ``"TWO"`` are the ``key``.
    """

    def __init__(self, code: int, key: str):
        super().__init__(code)
        self._key = key

    @property
    def key(self):
        """
        Get the key of the flag member.

        :return: key of the flag member
        """
        return self._key

    # noinspection PyUnresolvedReferences
    def __str__(self):
        return f"<{self.__class__.__name__}.{self.name}: {self._code} ({self._key})>"


class FlagDoubleMixin(FlagSingleMixin):
    """
    ``Flag`` with a ``code`` (:class:`int`), a ``key`` (:class:`str`) and a ``description`` (:class:`str`).

    Example:

    >>> class FlagDoubleSample(FlagDoubleMixin):
    >>>     A = 1, "ONE", "11"
    >>>     B = 2, "TWO", "22"

    where ``1`` and ``2`` are the ``code`` and ``"ONE"``, ``"TWO"`` are the ``key``
    and ``"11"``, ``"22"`` are the ``description``.
    """

    def __init__(self, code: int, key: str, description: str):
        super().__init__(code, key)
        self._desc = description

    @property
    def description(self):
        """
        Get the description of the flag member.

        :return: description of the flag member
        """
        return self._desc

    def __eq__(self, other):
        if isinstance(other, str):
            code_str_same = self.code_str == other
            if code_str_same:
                return True

            if other.isnumeric():
                return self.code == int(other)

        return super().__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self._code))

    # noinspection PyUnresolvedReferences
    def __str__(self):
        return f"<{self.__class__.__name__}.{self.name}: {self._code} ({self._key} - {self._desc})>"


class FlagPrefixedDoubleMixin(FlagDoubleMixin):
    # noinspection PyAbstractClass,PyUnresolvedReferences
    """
    ``Flag`` with a ``code`` (:class:`int`), a ``key`` (:class:`str`) and a ``description`` (:class:`str`).

    The ``code`` is prefixed by implementing the property ``code_prefix``.

    Example:

    >>> class FlagPrefixedDoubleSample(FlagPrefixedDoubleMixin):
    >>>     A = 1, "ONE", "11"
    >>>     B = 2, "TWO", "22"
    >>>
    >>> @property
    >>> def code_prefix(self) -> str:
    >>>     return "P-"

    where ``1`` and ``2`` are the ``code`` and ``"ONE"``, ``"TWO"`` are the ``key``
    and ``"11"``, ``"22"`` are the ``description``.

    The result of ``code`` and ``code_str`` will be different:

    >>> > FlagPrefixedDoubleSample.A.code
    >>> 1
    >>> > FlagPrefixedDoubleSample.A.code_str
    >>> "P-1"
    """

    def __init__(self, code: int, key: str, description: str):
        super().__init__(code, key, description)
        self._desc = description

    @property
    def code_prefix(self) -> str:
        """
        Code prefix of this :class:`FlagPrefixedDoubleMixin`.

        This will be prefixed to code if getting the code by calling ``code``.

        :return: code prefix of this class
        """
        raise NotImplementedError()

    @property
    def code_str(self) -> str:
        return f"{self.code_prefix}{self._code}"

    def __hash__(self):
        return hash((self.__class__, self._code))

    # noinspection PyUnresolvedReferences
    def __str__(self):
        return f"<{self.__class__.__name__}.{self.name}: {self.code_str} ({self._key} - {self._desc})>"


class FlagEnumMixin:
    """Mixin for some extend enum functionality."""

    @classmethod
    def cast(cls, item: Union[str, int], *, silent_fail=False):
        """
        Cast ``item`` to the corresponding :class:`FlagEnumMixin`.

        ``item`` can only be either ``code`` (:class:`str`) or ``name`` (:class:`int`).

        If ``silent_fail`` is ``True``, returns ``None`` if not found. Otherwise, raises :class:`ValueError`.

        :param item: item to be casted
        :param silent_fail: if this function should fail silently
        :return: casted enum/flag
        :raises TypeError: invalid type of the `item`
        :raises ValueError: ``item`` does not match any element of this enum/flag
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

        raise ValueError(f"`{cls.__qualname__}` casting failed. Item: {item} Type: {type(item)}")

    @classmethod
    def contains(cls, item):
        """
        Check if ``item`` is a member of this :class:`FlagEnumMixin`.

        :param item: item to check the membership
        :return: if `item` is the member of this `FlagEnumMixin`
        """
        if not type(item) in (str, int, cls):
            return False

        # noinspection PyTypeChecker
        for i in list(cls):
            if i == item:
                return True

        return False


class FlagCodeEnum(FlagCodeMixin, FlagEnumMixin, Enum):
    """
    Actual flag class with a ``code`` only.

    Example:

    >>> class FlagCodeSample(FlagCodeEnum):
    >>>     A = 1
    >>>     B = 2

    where ``1`` and ``2`` are the ``code``.
    """


class FlagSingleEnum(FlagSingleMixin, FlagEnumMixin, Enum):
    """
    Actual flag class with a ``code`` (:class:`int`) and a ``key`` (:class:`str`).

    Example:

    >>> class FlagSingleSample(FlagSingleEnum):
    >>>     A = 1, "ONE"
    >>>     B = 2, "TWO"

    where ``1`` and ``2`` are the ``code`` and ``"ONE"``, ``"TWO"`` are the ``key``.
    """


class FlagDoubleEnum(FlagDoubleMixin, FlagEnumMixin, Enum):
    """
    Actual flag class with a ``code`` (:class:`int`), a ``key`` (:class:`str`) and a ``description`` (:class:`str`).

    Example:

    >>> class FlagDoubleSample(FlagDoubleEnum):
    >>>     A = 1, "ONE", "11"
    >>>     B = 2, "TWO", "22"

    where ``1`` and ``2`` are the ``code`` and ``"ONE"``, ``"TWO"`` are the ``key``
    and ``"11"``, ``"22"`` are the ``description``.
    """


class FlagPrefixedDoubleEnum(FlagPrefixedDoubleMixin, FlagEnumMixin, Enum):
    # noinspection PyAbstractClass
    """
    Actual flag class with a ``code`` (:class:`int`), a ``key`` (:class:`str`) and a ``description`` (:class:`str`).

    The ``code`` is prefixed by implementing the property ``code_prefix``.

    Example:

    >>> class FlagPrefixedDoubleSample(FlagPrefixedDoubleEnum):
    >>>     A = 1, "ONE", "11"
    >>>     B = 2, "TWO", "22"
    >>>
    >>> @property
    >>> def code_prefix(self) -> str:
    >>>     return "P-"

    where ``1`` and ``2`` are the ``code`` and ``"ONE"``, ``"TWO"`` are the ``key``
    and ``"11"``, ``"22"`` are the ``description``.

    The result of ``code`` and ``code_str`` will be different:

    >>> > FlagPrefixedDoubleSample.A.code
    >>> 1
    >>> > FlagPrefixedDoubleSample.A.code_str
    >>> "P-1"
    """

    @property
    def code_prefix(self) -> str:
        raise NotImplementedError()


class FlagOutcomeMixin(FlagCodeMixin):
    """
    Same as :class:`FlagCodeEnum`, but with an additional property ``is_success``.

    Successive outcome code should have a positive value as ``code``.
    In contrast, the failing outcome code should have a negative value as ``code``.

    ``0`` is considered successive.
    """

    @property
    def is_success(self):
        """
        Check if the outcome is success.

        :return: if the outcome is success
        """
        return self._code < 0
