from abc import ABC, abstractmethod
from typing import Any, Type, List, Union, Optional
from inspect import signature, Parameter

from bson import ObjectId

from extutils.flags import FlagCodeMixin
from .logger import logger


__all__ = [
    "param_type_ensure", "TypeCastingFailed",
    "BaseDataTypeConverter", "NonSafeDataTypeConverter"
]


class TypeCastingFailed(Exception):
    def __init__(self, data: Any, dtype: type, exception: Exception):
        self.data = data
        self.expected_type = dtype
        self.actual_type = type(data)
        self.inner_exception = exception

        super().__init__(
            f"Type casting failed. (Data: {data} / Expected: {self.expected_type} / Actual: {self.actual_type} / "
            f"Exception: {exception})")


class BaseDataTypeConverter(ABC):
    _ignore = [Any]
    valid_data_types: List[type] = []

    @classmethod
    @abstractmethod
    def _convert_(cls, data: Any, type_annt):
        # Terminate if the type is already valid
        if type(data) == type_annt:
            return data

        if type_annt is not Parameter.empty \
                and type_annt not in cls.valid_data_types + cls._ignore\
                and not (hasattr(type_annt, "__origin__") and type_annt.__origin__ is Union):
            return cls.on_type_invalid(data, type_annt)

        try:
            # [origin is Union] before [not in _ignore] so if type_annt is Union, then it won't go to `type_annt(data)`
            if hasattr(type_annt, "__origin__") and type_annt.__origin__ is Union:
                return cls._cast_union_(data, type_annt)
            elif type_annt not in cls._ignore:
                return type_annt(data)
            else:
                return data
        except Exception as e:
            return cls.on_cast_fail(data, type_annt, e)

    @classmethod
    def _cast_union_(cls, data: Any, type_annt):
        last_e = None

        for allowed_type in type_annt.__args__:
            try:
                if allowed_type is None:
                    return None
                elif cls._data_is_allowed_type_(data, allowed_type):
                    return data
                else:
                    return allowed_type(data)
            except Exception as e:
                last_e = e

        return cls.on_cast_fail(data, type_annt, last_e)

    @classmethod
    def _data_is_allowed_type_(cls, data, allowed_type):
        t = type(data)
        return t == allowed_type or (hasattr(allowed_type, "__origin__") and allowed_type.__origin__ is t)

    @classmethod
    def convert(cls, data: Any, type_annt):
        if type_annt is Parameter.empty:
            return data
        else:
            return cls._convert_(data, type_annt)

    @staticmethod
    def on_type_invalid(data: Any, dtype: type):
        raise NotImplementedError()

    @staticmethod
    def on_cast_fail(data: Any, dtype: type, e: Exception):
        raise NotImplementedError()


class GeneralDataTypeConverter(BaseDataTypeConverter):
    valid_data_types = [int, str, bool, type, dict, ObjectId]

    @classmethod
    def _convert_(cls, data: Any, type_annt):
        ret = super()._convert_(data, type_annt)
        return ret

    @staticmethod
    def on_type_invalid(data: Any, dtype: type) -> Any:
        if issubclass(dtype, FlagCodeMixin):
            return dtype(int(data))
        else:
            return data

    @staticmethod
    def on_cast_fail(data: Any, dtype: type, e: Exception) -> Any:
        logger.logger.warning(f"Type casting failed. Data: {data} / Target Type: {dtype} / Exception: {e}")

        return data


class NonSafeDataTypeConverter(GeneralDataTypeConverter):
    """Raises `TypeCastingFailed` on exception occurred during casting."""
    valid_data_types = [int, str, bool, type, dict, ObjectId]

    @classmethod
    def _convert_(cls, data: Any, type_annt):
        ret = super()._convert_(data, type_annt)
        return ret

    @staticmethod
    def on_type_invalid(data: Any, dtype: type) -> Any:
        if issubclass(dtype, FlagCodeMixin):
            return dtype(int(data))
        else:
            return data

    @staticmethod
    def on_cast_fail(data: Any, dtype: type, e: Exception) -> Any:
        logger.logger.warning(f"Type casting failed. Data: {data} / Target Type: {dtype} / Exception: {e}")

        raise TypeCastingFailed(data, dtype, e)


def param_type_ensure(fn=None, *, converter: Optional[Type[BaseDataTypeConverter]] = GeneralDataTypeConverter):
    if fn:
        def wrapper_in(*args_cast, **kwargs_cast):
            return _type_ensure_(fn, converter, *args_cast, **kwargs_cast)

        return wrapper_in
    else:
        def fn_wrap(fn_in):
            def wrapper_in_2(*args_cast, **kwargs_cast):
                return _type_ensure_(
                    fn_in, converter, *args_cast, **kwargs_cast)

            return wrapper_in_2
        return fn_wrap


def _type_ensure_(fn, converter: Type[BaseDataTypeConverter], *args_cast, **kwargs_cast):
    sg = signature(fn)
    prms = sg.parameters
    prms_vars = filter(
        lambda _: prms[_].kind in (prms[_].POSITIONAL_OR_KEYWORD, prms[_].POSITIONAL_ONLY), prms)
    prms_kw = filter(
        lambda _: prms[_].kind == prms[_].KEYWORD_ONLY, prms)

    new_args = []
    for old_arg, prm in zip(args_cast, prms_vars):
        p = prms[prm]

        if p is p.empty:
            new_args.append(old_arg)
        else:
            new_args.append(converter.convert(old_arg, p.annotation))

    new_kwargs = {}
    for prm_name in prms_kw:
        p = prms[prm_name]

        try:
            old = kwargs_cast.pop(prm_name)
            if p is p.empty:
                new_kwargs[prm_name] = old
            else:
                new_kwargs[prm_name] = converter.convert(old, p.annotation)
        except KeyError:
            pass

    new_kwargs.update(**kwargs_cast)

    return fn(*new_args, **new_kwargs)
