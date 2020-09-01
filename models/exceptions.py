"""Exceptions for :class:`Model`."""
from abc import ABC
from typing import List, Type

from flags import ModelValidityCheckResult


class ModelConstructionError(Exception, ABC):
    """Base class for model construction error."""


class ModelOperationError(Exception, ABC):
    """Base class for model operation error."""


class ModelKeyNotExistError(AttributeError, ABC):
    """Base class for model key not exists error."""


class InvalidModelError(ModelConstructionError):
    """Raised if the model is invalid."""

    def __init__(self, model_name: str, reason: ModelValidityCheckResult):
        self._reason = reason
        super().__init__(f"Invalid model `{model_name}`. Reason: {repr(reason)}")

    @property
    def reason(self) -> ModelValidityCheckResult:
        """
        Get the invalid reason.

        :return: invalid reason
        """
        return self._reason


class InvalidModelFieldError(ModelConstructionError):
    """Raised if the model field is invalid."""

    def __init__(self, model_name: str, exception: Exception):
        self._inner = exception
        super().__init__(f"Invalid model `{model_name}`. Exception: {exception}")

    @property
    def inner_exception(self) -> Exception:
        """
        Get the inner exception (possibly the reason of invalid).

        :return: inner exception
        """
        return self._inner


class ModelUncastableError(ModelConstructionError):
    """Raised if the model is uncastable."""

    def __init__(self, model_name: str, reason: str):
        super().__init__(f"Model `{model_name}` cannot be casted. {reason}")


class RequiredKeyNotFilledError(ModelConstructionError):
    """Raised if the required key for the model is not filled."""

    def __init__(self, model_cls: Type, ks: List[str]):
        super().__init__(f"Required fields not filled. Keys: {', '.join(ks)} / Model Class: {model_cls}")


class IdUnsupportedError(ModelConstructionError, KeyError, AttributeError):
    """Raised if OID is not supported for the model."""

    def __init__(self, model_name: str):
        super().__init__(
            f"`{model_name}` is not designated to have `_id` field. Set `WITH_OID` to True to support this.")


class FieldKeyNotExistError(ModelKeyNotExistError):
    """Raised if the field key does not exist in the model."""

    def __init__(self, fk: str, model_name: str):
        super().__init__(f"Field key `{fk}` not existed in the model `{model_name}`.")


class JsonKeyNotExistedError(ModelKeyNotExistError):
    """Raised if the json key does not exist in the model."""

    def __init__(self, fk: str, model_name: str):
        super().__init__(f"Json key `{fk}` not existed in the model `{model_name}`.")


class JsonKeyDuplicatedError(ModelConstructionError):
    """Raised if the model contains duplicated json key."""

    def __init__(self, dup_key: str, model_name: str):
        super().__init__(f"Model `{model_name}` contains duplicated json key: {dup_key}.")


class DeleteNotAllowedError(ModelOperationError):
    """Raised if the statement ``del`` is not allowed to be performed on the model."""

    def __init__(self, model_name: str):
        super().__init__(f"Not allowed to perform `del` on {model_name}")
