from abc import ABC
from datetime import datetime
from typing import Union, Tuple, Any, Iterable, Optional


class FieldError(ABC, Exception):
    def __init__(self, key: str, *, error_msg: str = None):
        super().__init__(f"Field (Key: {key}) - {error_msg}")


class FieldReadOnlyError(FieldError):
    def __init__(self, key: str):
        super().__init__(key, error_msg="Readonly.")


class FieldTypeMismatchError(FieldError):
    def __init__(self, key: str, actual_type: type, actual_value: Any,
                 expected_types: Union[type, Iterable[type]] = None, *, extra_message: str = None):
        if expected_types is None:
            expected_name = "(Unknown)"
        elif isinstance(expected_types, type):
            expected_name = expected_types.__name__
        else:
            expected_name = " or ".join([t.__name__ for t in expected_types])

        super().__init__(
            key,
            error_msg=f"Type mismatch. {extra_message or ''} "
                      f"Expected Type: {expected_name} / Actual Type: {actual_type.__name__} / "
                      f"Actual Value: {actual_value}")


class FieldValueTypeMismatchError(FieldError):
    def __init__(self, key: str, actual: type, expected: Union[type, Tuple[type, ...]] = None, *,
                 extra_message: str = None):
        if expected is None:
            expected_name = "(Unknown)"
        elif isinstance(expected, type):
            expected_name = expected.__name__
        else:
            expected_name = " or ".join([t.__name__ for t in expected])

        super().__init__(
            key,
            error_msg=f"Type mismatch. {extra_message or ''} "
                      f"Expected: {expected_name}, Actual: {actual.__name__}")


class FieldValueInvalidError(FieldError):
    def __init__(self, key: str, value: Optional[Any] = None, *, error_msg: Optional[str] = None):
        super().__init__(key, error_msg=error_msg or f"Invalid value: {value}")


class FieldCastingFailedError(FieldError):
    def __init__(self, key: str, value: str, desired_type: type, *, exc: Exception = None):
        super().__init__(
            key,
            error_msg=f"Auto casting failed. Value: ({value}) {type(value)} / Desired type: {desired_type} / "
                      f"Exception: {exc}")


class FieldNoneNotAllowedError(FieldValueInvalidError):
    def __init__(self, key: str):
        super().__init__(key, error_msg="`None` not allowed.")


class FieldEmptyValueNotAllowedError(FieldValueInvalidError):
    def __init__(self, key: str):
        super().__init__(key, error_msg="Empty value not allowed.")


class FieldMaxLengthReachedError(FieldValueInvalidError):
    def __init__(self, key: str, cur_len: int, max_len: int):
        super().__init__(key, error_msg=f"Max length reached. {cur_len}/{max_len}")


class FieldInvalidUrlError(FieldValueInvalidError):
    def __init__(self, key: str, url: str):
        super().__init__(key, error_msg=f"Invalid URL: {url}")


class FieldFlagNotFoundError(FieldValueInvalidError):
    def __init__(self, key: str, obj: Any, flag):
        super().__init__(key, error_msg=f"Object ({obj}) not found in the flag ({flag}).")


class FieldFlagDefaultUndefinedError(FieldError):
    def __init__(self, key: str, flag):
        super().__init__(key, error_msg=f"Default value of the flag ({flag}) undefined.")


class FieldRegexNotMatchError(FieldValueInvalidError):
    def __init__(self, key: str, value: str, regex: str):
        super().__init__(key, error_msg=f"Regex ({regex}) not match with ({value}).")


class FieldInstanceClassInvalidError(FieldError):
    def __init__(self, key: str, inst_cls):
        super().__init__(key, error_msg=f"Invalid field instance class type: {inst_cls}")


class FieldModelClassInvalidError(FieldError):
    def __init__(self, key: str, model_cls):
        super().__init__(key, error_msg=f"Invalid model class type: {model_cls}")


class FieldValueNegativeError(FieldValueInvalidError):
    def __init__(self, key: str, val: Union[int, float]):
        super().__init__(key, error_msg=f"Field value should not be negative. (Actual: {val})")


class FieldOidDatetimeOutOfRangeError(FieldValueInvalidError):
    def __init__(self, key: str, dt: datetime):
        super().__init__(key, error_msg=f"Datetime to initialize `ObjectId` out of range. (Actual: {dt})")


class FieldOidStringInvalidError(FieldValueInvalidError):
    def __init__(self, key: str, val: str):
        super().__init__(key, error_msg=f"Invalid string initialize `ObjectId`. (Actual: {val})")


class FieldInvalidDefaultValueError(FieldError):
    def __init__(self, key: str, default_value: Any, *, exc: Exception = None):
        super().__init__(key, error_msg=f"Invalid default value. {default_value} - <{exc}>")


class FieldValueRequiredError(FieldValueInvalidError):
    def __init__(self, key: str):
        super().__init__(key, error_msg=f"Field (key: {key}) requires value.")


class FieldDimensionMismtachError(FieldValueInvalidError):
    def __init__(self, key: str, expected_dimension: int, actual_dimension: int):
        super().__init__(key, error_msg=f"Field dimension mismatch. "
                                        f"(Expected: {expected_dimension} / Actual: {actual_dimension})")
