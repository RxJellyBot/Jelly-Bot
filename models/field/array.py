import math
from collections import abc

from bson import ObjectId
from pymongo.client_session import ClientSession
from pymongo.collection import Collection

from extutils.arr import extract_list_action, extract_one

from ._base import BaseField, FieldInstance
from .exceptions import (
    FieldModelClassInvalidError, FieldValueTypeMismatchError, FieldMaxLengthReachedError,
    FieldCastingFailedError, FieldEmptyValueNotAllowedError, FieldDimensionMismtachError
)


def _check_array_type_match(value, elem_type, is_elem_type_model, key, attempt_cast):
    if not value:
        return value

    for v in value:
        value_type = type(v)

        if is_elem_type_model:
            if isinstance(v, abc.MutableMapping):
                elem_type.cast_model(v)
            else:
                raise FieldValueTypeMismatchError(key, value_type, elem_type)
        elif not value_type == elem_type:
            if not attempt_cast:
                raise FieldValueTypeMismatchError(key, value_type, elem_type)

            try:
                elem_type(v)
            except Exception as e:
                raise FieldCastingFailedError(key, v, elem_type, exc=e)

    return value


def _cast_array_item(value, elem_type):
    from models import Model

    # Not testing falsyness because value could be an empty iterable,
    # which if it is `set` or `tuple`, it should be casted to `list`.
    if value is None:
        return None

    elem_type_is_model = issubclass(elem_type, Model)

    v_new = []
    for v in value:
        value_type = type(v)

        if not value_type == elem_type:
            if elem_type_is_model:
                v = elem_type.cast_model(v)
            else:
                v = elem_type(v)

        v_new.append(v)

    return v_new


class ArrayField(BaseField):
    def __init__(self, key, elem_type: type, *, max_len=0, allow_empty=True, **kwargs):
        """
        Default Properties Overrided:

        - ``allow_none`` - ``False``
        - ``inst_cls`` - :class:`ArrayFieldInstance`

        Additional Properties:

        - ``max_len``: Max length of the array. Default is 0.

            - Unlimited length if the value is ``0``

        .. seealso::
            Check the document of :class:`BaseField` for other default properties.
        """
        if "inst_cls" not in kwargs:
            kwargs["inst_cls"] = ArrayFieldInstance
        if "allow_none" not in kwargs:
            kwargs["allow_none"] = False

        # Check max length
        if max_len < 0:
            raise ValueError("Max length of the array field must > 0.")
        if type(max_len) != int:
            raise TypeError("Max length of the array must be `int`.")

        self._elem_type = elem_type
        self._max_len = max_len
        self._allow_empty = allow_empty
        super().__init__(key, **kwargs)

    def _check_value_valid_not_none(self, value):
        # Check emptiness
        if not self._allow_empty and len(value) == 0:
            raise FieldEmptyValueNotAllowedError(self.key)

        # Check length
        if len(value) > self.max_len:
            raise FieldMaxLengthReachedError(self.key, len(value), self.max_len)

    def _check_type_matched_not_none(self, value, *, attempt_cast=False):
        from models import Model

        _check_array_type_match(value, self.elem_type, issubclass(self.elem_type, Model), self.key, attempt_cast)

    def none_obj(self):
        return []

    @property
    def expected_types(self):
        return list, tuple, set

    @property
    def elem_type(self):
        return self._elem_type

    @property
    def max_len(self):
        return self._max_len or math.inf

    def cast_to_desired_type(self, value):
        self.check_value_valid(value, attempt_cast=self.auto_cast)

        return _cast_array_item(value, self.elem_type)

    @property
    def replace_uid_implemented(self) -> bool:
        return True

    def replace_uid(self, collection_inst: Collection, old: ObjectId, new: ObjectId, session: ClientSession) -> bool:
        ack_push = collection_inst.update_many(
            {self.key: {"$in": [old]}}, {"$push": {self.key: new}}, session=session).acknowledged
        ack_pull = collection_inst.update_many(
            {self.key: {"$in": [old]}}, {"$pull": {self.key: old}}, session=session).acknowledged
        return ack_pull and ack_push


class MultiDimensionalArrayField(BaseField):
    def __init__(self, key, dimension: int, elem_type: type, *, allow_empty=True, **kwargs):
        """
        Default Properties Overrided:

        - ``allow_none`` - ``False``
        - ``inst_cls`` - :class:`ArrayFieldInstance`

        .. note::
            Dimension mismatch will be considered as type mismatch.

        .. seealso::
            Check the document of :class:`BaseField` for other default properties.
        """
        if "inst_cls" not in kwargs:
            kwargs["inst_cls"] = ArrayFieldInstance
        if "allow_none" not in kwargs:
            kwargs["allow_none"] = False

        # Check dimension
        if dimension < 2:
            raise ValueError("Dimension must be >= 2.")
        if type(dimension) != int:
            raise TypeError("Dimension of the array must be `int`.")

        self._elem_type = elem_type
        self._dimension = dimension
        self._allow_empty = allow_empty
        super().__init__(key, **kwargs)

    def _check_value_valid_not_none(self, value):
        # Check emptiness
        if not self._allow_empty and len(value) == 0:
            raise FieldEmptyValueNotAllowedError(self.key)

    def _check_type_matched_not_none(self, value, *, attempt_cast=False):
        from models import Model

        # Check dimension
        val = value
        for dim in range(self._dimension):
            try:
                val = extract_one(val)
            except TypeError:
                raise FieldDimensionMismtachError(self.key, self._dimension, dim)

        extract_list_action(
            value, _check_array_type_match, self.elem_type, issubclass(self.elem_type, Model), self.key, attempt_cast)

    def none_obj(self):
        v = []
        for _ in range(self._dimension - 1):
            v = [v]
        return v

    @property
    def expected_types(self):
        return list, tuple, set

    @property
    def elem_type(self):
        return self._elem_type

    def cast_to_desired_type(self, value):
        self.check_value_valid(value, attempt_cast=self.auto_cast)

        if self.allow_none and value is None:
            return None

        return extract_list_action(value, _cast_array_item, self.elem_type)


class ModelArrayField(ArrayField):
    def __init__(self, key, model_type, **kwargs):
        from models import Model

        if "inst_cls" not in kwargs:
            kwargs["inst_cls"] = ModelArrayFieldInstanceFactory.generate(model_type)

        if not issubclass(model_type, Model):
            raise FieldModelClassInvalidError(key, model_type)

        self._model_type = model_type

        super().__init__(key, model_type, **kwargs)

    def cast_to_desired_type(self, value):
        self.check_value_valid(value, attempt_cast=self.auto_cast)

        if self.allow_none and value is None:
            return None

        v_new = []
        for v in value:
            if not type(v) == self._model_type:
                v = self._model_type.cast_model(v)

            v_new.append(v)

        return v_new


class ArrayFieldInstance(FieldInstance):
    def __init__(self, base, value=None):
        if not isinstance(base, (ArrayField, MultiDimensionalArrayField)):
            raise ValueError(f"`ArrayFieldInstance` can only be used "
                             f"when the base class is {ArrayField} or {MultiDimensionalArrayField}. ({base})")

        super().__init__(base, value)


class ModelArrayFieldInstanceFactory:
    @staticmethod
    def generate(model_type):
        return type(f"{model_type.__name__}ModelArrayInstance",
                    (FieldInstance,),
                    {}, )
