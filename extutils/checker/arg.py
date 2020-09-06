"""Module containing utilities to check and ensure the argument types."""
from abc import ABC, abstractmethod
from typing import Any, Type, List, Union, Optional
from inspect import signature, Parameter

from bson import ObjectId

from extutils.flags import is_flag_class
from .logger import LOGGER

__all__ = ("arg_type_ensure", "TypeCastingFailedError", "BaseDataTypeConverter", "NonSafeDataTypeConverter",)


class TypeCastingFailedError(Exception):
    """Raised if the type casting failed."""

    def __init__(self, data: Any, dtype: type, exception: Exception):
        self.data = data
        self.expected_type = dtype
        self.actual_type = type(data)
        self.inner_exception = exception

        super().__init__(
            f"Type casting failed. (Data: {data} / Expected: {self.expected_type} / Actual: {self.actual_type} / "
            f"Exception: {exception})")


class BaseDataTypeConverter(ABC):
    """
    Base of the data converter.

    Inherit this class for more customizations.
    """

    _ignore = [Any]
    valid_data_types: List[type] = []

    @staticmethod
    def _typing_alias_origin(dtype: Any) -> Optional[Any]:
        return getattr(dtype, "__origin__", None)

    @classmethod
    @abstractmethod
    def _convert(cls, data: Any, type_annt):
        # pylint: disable=too-many-return-statements
        # Terminate if the type is already valid
        # type annotation cannot be used with instance checks (generic may be the type annotation)
        if type(data) == type_annt:  # pylint: disable=unidiomatic-typecheck
            return data

        origin = cls._typing_alias_origin(type_annt)

        alias_origin_union = origin is Union
        alias_origin_list = origin is list
        alias_origin_dict = origin is dict

        if type_annt is not Parameter.empty \
                and type_annt not in cls.valid_data_types + cls._ignore \
                and not any([alias_origin_union, alias_origin_list, alias_origin_dict]):
            return cls.on_type_invalid(data, type_annt)

        try:
            # [origin is Union] before [not in _ignore] so if type_annt is Union, then it won't go to `type_annt(data)`
            if alias_origin_union:
                return cls._cast_union(data, type_annt)

            if alias_origin_list:
                return cls._cast_list(data, type_annt)

            if alias_origin_dict:
                return cls._cast_dict(data, type_annt)

            if type_annt not in cls._ignore:
                return type_annt(data)

            return data
        except Exception as ex:
            return cls.on_cast_fail(data, type_annt, ex)

    @classmethod
    def _cast_union(cls, data: Any, type_annt):
        # Early termination if the data type is in Union
        if type(data) in type_annt.__args__:
            return data

        last_e = None

        for allowed_type in type_annt.__args__:
            try:
                if allowed_type is None:
                    return None

                if cls._data_is_allowed_type(data, allowed_type):
                    return data

                return allowed_type(data)
            except Exception as ex:
                last_e = ex

        return cls.on_cast_fail(data, type_annt, last_e)

    @classmethod
    def _cast_list(cls, data: Any, type_annt):
        cast_type = type_annt.__args__[0]
        annt_union = cls._typing_alias_origin(cast_type) is Union

        try:
            iterator = iter(data)
        except TypeError:
            iterator = iter([data])

        if annt_union:
            ret = [cls._cast_union(obj, cast_type) for obj in iterator]
        else:
            ret = [(obj if isinstance(obj, cast_type) else cast_type(obj)) for obj in iterator]

        return ret

    @classmethod
    def _cast_dict(cls, data: Any, type_annt):
        ret = {}
        cast_key_type = type_annt.__args__[0]
        cast_val_type = type_annt.__args__[1]
        annt_key_union = cls._typing_alias_origin(cast_key_type) is Union
        annt_val_union = cls._typing_alias_origin(cast_val_type) is Union

        for k, v in data.items():
            if annt_key_union:
                k = cls._cast_union(k, cast_key_type)
            elif not isinstance(k, cast_key_type):
                k = cast_key_type(k)

            if annt_val_union:
                v = cls._cast_union(v, cast_val_type)
            elif not isinstance(v, cast_val_type):
                v = cast_key_type(v)

            ret[k] = v

        return ret

    @classmethod
    def _data_is_allowed_type(cls, data, allowed_type):
        data_type = type(data)
        return data_type == allowed_type or cls._typing_alias_origin(allowed_type) is data_type

    @classmethod
    def convert(cls, data: Any, type_annt):
        """
        Attempt to convert ``data`` to type ``type_annt``.

        Executes ``cls.on_type_invalid`` if the type is invalid.

        If all conditions below meet, then it is considered invalid:

        - ``type_annt`` is not ``Parameter.empty``

        - ``type_annt`` is not in ``cls.valid_data_types``

        - ``type_annt`` is not a ignored type (in ``cls._ignore``)

        - The origin of the alias (if it is a ``typing`` hint) of ``type_annt`` is not :class:`Union` or :class:`list`

        Executes ``cls.on_cast_fail`` if the type casting failed.

        :param data: data to be casted
        :param type_annt: target type to cast the data
        :return: casted data
        """
        if type_annt is Parameter.empty:
            return data

        return cls._convert(data, type_annt)

    @classmethod
    @abstractmethod
    def on_type_invalid(cls, data: Any, dtype: type):
        """
        Method to be executed if the target type to cast the data is invalid.

        The behavior defaults to:

        - If the destination type ``dtype`` is a flag class, then cast it to :class:`int`, then cast it to be a flag

        - Otherwise, returns the original data without casting

        :param data: data to be casted
        :param dtype: target type
        :return: post-processed data
        """
        if isinstance(dtype, type) and is_flag_class(dtype):
            return dtype(int(data))

        return data

    @staticmethod
    def on_cast_fail(data: Any, dtype: type, ex: Exception):
        """
        Method to be executed if failed to cast ``data`` to be the type of ``dtype``.

        :param data: data to be casted
        :param dtype: target type
        :param ex: raised exception during the cast
        :raises NotImplementedError: if the behavior is not defined
        """
        raise NotImplementedError()


class GeneralDataTypeConverter(BaseDataTypeConverter):
    """
    A general data type converter which can handle most argument type checking cases.

    Returns the original ``data`` if failed to cast.
    """

    valid_data_types = [int, str, bool, type, list, tuple, dict, ObjectId]

    @classmethod
    def _convert(cls, data: Any, type_annt):
        return super()._convert(data, type_annt)

    @classmethod
    def on_type_invalid(cls, data: Any, dtype: type) -> Any:
        return super().on_type_invalid(data, dtype)

    @staticmethod
    def on_cast_fail(data: Any, dtype: type, ex: Exception) -> Any:
        LOGGER.logger.warning("Type casting failed. Data: %s / Target Type: %s / Exception: %s", data, dtype, ex)

        return data


class NonSafeDataTypeConverter(GeneralDataTypeConverter):
    """
    Non-safe data converter.

    Raises :class:`TypeCastingFailed` and log a warning if any exception raised during casting.
    """

    valid_data_types = [int, str, bool, type, list, tuple, dict, ObjectId]

    @classmethod
    def _convert(cls, data: Any, type_annt):
        return super()._convert(data, type_annt)

    @classmethod
    def on_type_invalid(cls, data: Any, dtype: type) -> Any:
        return super().on_type_invalid(data, dtype)

    @staticmethod
    def on_cast_fail(data: Any, dtype: type, ex: Exception) -> Any:
        LOGGER.logger.warning("Type casting failed. Data: %s / Target Type: %s / Exception: %s", data, dtype, ex)

        raise TypeCastingFailedError(data, dtype, ex)


def arg_type_ensure(fn=None, *, converter: Optional[Type[BaseDataTypeConverter]] = GeneralDataTypeConverter):
    """
    A Decorator to ensure the parameter is the desired data type real time.

    This will inspect the signature of the function, and extract the type notation if available.
    Then the extracted notation will be used to cast the data by ``converter``.

    This function is expensive, it is recommended to use only when the argument type needs to be ensured.

    The behavior on invalid type or casting failed will depend on ``converter``.

    Example:

    >>> # Normal use
    >>> @arg_type_ensure
    >>> def a_function(num: int):
    >>>     pass  # `num` will be `int`
    >>>
    >>> # To raise an exception upon casting failed
    >>> @arg_type_ensure(converter=NonSafeDataTypeConverter)
    >>> def b_function(num: int):
    >>>     pass  # `num` will be `int`

    :param fn: function to check the parameter
    :param converter: converter to be used to cast the data
    """
    if fn:
        # Used when as decorator and with parentheses
        def _wrapper_in(*args_cast, **kwargs_cast):
            return _type_ensure(fn, converter, *args_cast, **kwargs_cast)

        return _wrapper_in

    # Used when as decorator and without parentheses
    def _fn_wrap(fn_in):
        def _wrapper_in_2(*args_cast, **kwargs_cast):
            return _type_ensure(fn_in, converter, *args_cast, **kwargs_cast)

        return _wrapper_in_2

    return _fn_wrap


def _type_ensure(fn, converter: Type[BaseDataTypeConverter], *args_cast, **kwargs_cast):
    sig = signature(fn)
    prms = sig.parameters
    prms_vars = filter(
        lambda _: prms[_].kind in (prms[_].POSITIONAL_OR_KEYWORD, prms[_].POSITIONAL_ONLY), prms)
    prms_kw = filter(
        lambda _: prms[_].kind == prms[_].KEYWORD_ONLY, prms)

    new_args = []
    for old_arg, prm in zip(args_cast, prms_vars):
        prm_ = prms[prm]

        if prm_ is prm_.empty:
            new_args.append(old_arg)
        else:
            new_args.append(converter.convert(old_arg, prm_.annotation))

    new_kwargs = {}
    for prm_name in prms_kw:
        prm_ = prms[prm_name]

        try:
            old = kwargs_cast.pop(prm_name)
            if prm_ is prm_.empty:
                new_kwargs[prm_name] = old
            else:
                new_kwargs[prm_name] = converter.convert(old, prm_.annotation)
        except KeyError:
            pass

    new_kwargs.update(**kwargs_cast)

    return fn(*new_args, **new_kwargs)
