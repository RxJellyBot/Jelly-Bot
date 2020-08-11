from typing import Tuple, Any, Type

from models import Model
from models.field import BaseField, MultiDimensionalArrayField, IntegerField
from models.field.exceptions import (
    FieldError, FieldTypeMismatchError, FieldDimensionMismtachError, FieldNoneNotAllowedError,
    FieldValueTypeMismatchError
)

from ._test_val import TestFieldValue
from ._test_prop import TestFieldProperty

__all__ = ["TestMultiDimensionalArrayFieldProperty", "TestMultiDimensionalArrayFieldValue2D",
           "TestMultiDimensionalArrayFieldValue2DModel"]


class TestMultiDimensionalArrayFieldProperty(TestFieldProperty.TestClass):
    def get_field_class(self) -> Type[BaseField]:
        return MultiDimensionalArrayField

    def get_initialize_required_args(self) -> Tuple[Any, ...]:
        return 2, int,

    def expected_none_object(self) -> Any:
        return [[]]

    def valid_not_none_obj_value(self) -> Any:
        return [[5], [7]]

    def get_valid_default_values(self) -> Tuple[Tuple[Any, Any], ...]:
        # Not testing `set` because it's unordered
        return (
            ([[5], [7]], [[5], [7]]),
            ([["5"], [7]], [[5], [7]]),
            ([["5"], ["7"]], [[5], [7]]),
            (([5], ["7"]), [[5], [7]])
        )

    def get_invalid_default_values(self) -> Tuple[Any, ...]:
        return 7, "7", True, {}

    def get_expected_types(self) -> Tuple[Type[Any], ...]:
        return list, tuple, set

    def get_desired_type(self) -> Type[Any]:
        return list


class TestMultiDimensionalArrayFieldValue2D(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return MultiDimensionalArrayField("k", 2, int)

    def is_auto_cast(self) -> bool:
        return True

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            ({}, False),
            (7, False),
            ("7", False),
            (True, False),
            (object(), False),
            ((), False),
            ((5, 7), False),
            (set(), False),
            ({5, 7}, False),
            ([], False),
            ([7, 9], False),
            ([7, "9"], False),
            (["7", "9"], False),
            ([[]], True),
            ([[7, 9]], True),
            ([[7, 9], [5]], True),
            ([[7, 9], [5, 3]], True),
            ([["7", "9"]], True)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            ({}, False),
            (7, False),
            ("7", False),
            (True, False),
            (object(), False),
            ((), False),
            ((5, 7), False),
            (set(), False),
            ({5, 7}, False),
            ([], False),
            ([7, 9], False),
            ([7, "9"], False),
            (["7", "9"], False),
            ([[]], True),
            ([[7, 9]], True),
            ([[7, 9], [5]], True),
            ([[7, 9], [5, 3]], True),
            ([["7", "9"]], True)
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ([[]], [[]]),
            ([[7, 9]], [[7, 9]]),
            ([[7, 9], [5]], [[7, 9], [5]]),
            ([[7, 9], [5, 3]], [[7, 9], [5, 3]]),
            ([["7", "9"]], [[7, 9]])
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            (None, FieldNoneNotAllowedError),
            ({}, FieldTypeMismatchError),
            (7, FieldTypeMismatchError),
            ("7", FieldTypeMismatchError),
            (True, FieldTypeMismatchError),
            ([7, object()], FieldDimensionMismtachError),
            ((), FieldDimensionMismtachError),
            ((5, 7), FieldDimensionMismtachError),
            (set(), FieldDimensionMismtachError),
            ({5, 7}, FieldDimensionMismtachError),
            ([], FieldDimensionMismtachError),
            ([7, 9], FieldDimensionMismtachError),
            ([7, "9"], FieldDimensionMismtachError),
            (["7", "9"], FieldDimensionMismtachError)
        )

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ([[]], [[]]),
            ([[7, 9]], [[7, 9]]),
            ([[7, 9], [5]], [[7, 9], [5]]),
            ([[7, 9], [5, 3]], [[7, 9], [5, 3]]),
            ([["7", "9"]], [[7, 9]])
        )


class TestModel(Model):
    WITH_OID = False

    Number = IntegerField("num")


class TestMultiDimensionalArrayFieldValue2DModel(TestFieldValue.TestClass):
    MDL1 = TestModel(Number=2)
    MDL2 = TestModel(Number=3)

    def get_field(self) -> BaseField:
        return MultiDimensionalArrayField("k", 2, TestModel)

    def is_auto_cast(self) -> bool:
        return True

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            ({}, False),
            (7, False),
            ("7", False),
            (True, False),
            (object(), False),
            ((), False),
            ((5, 7), False),
            (set(), False),
            ({5, 7}, False),
            ([], False),
            ([7, 9], False),
            ([7, "9"], False),
            (["7", "9"], False),
            ([[]], True),
            ([[7, 9]], False),
            ([[7, 9], [5]], False),
            ([[7, 9], [5, 3]], False),
            ([["7", "9"]], False),
            ([[self.MDL1, self.MDL2]], True),
            ([[self.MDL1], [self.MDL2]], True),
            ([[{"num": 2}, {"num": 3}]], True),
            ([[{"num": 2}], [{"num": 3}]], True),
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            ({}, False),
            (7, False),
            ("7", False),
            (True, False),
            (object(), False),
            ((), False),
            ((5, 7), False),
            (set(), False),
            ({5, 7}, False),
            ([], False),
            ([7, 9], False),
            ([7, "9"], False),
            (["7", "9"], False),
            ([[]], True),
            ([[7, 9]], False),
            ([[7, 9], [5]], False),
            ([[7, 9], [5, 3]], False),
            ([["7", "9"]], False),
            ([[self.MDL1, self.MDL2]], True),
            ([[self.MDL1], [self.MDL2]], True),
            ([[{"num": 2}, {"num": 3}]], True),
            ([[{"num": 2}], [{"num": 3}]], True),
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ([[]], [[]]),
            ([[self.MDL1, self.MDL2]], [[self.MDL1, self.MDL2]]),
            ([[self.MDL1], [self.MDL2]], [[self.MDL1], [self.MDL2]]),
            ([[{"num": 2}, {"num": 3}]], [[self.MDL1, self.MDL2]]),
            ([[{"num": 2}], [{"num": 3}]], [[self.MDL1], [self.MDL2]]),
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            (None, FieldNoneNotAllowedError),
            ({}, FieldTypeMismatchError),
            (7, FieldTypeMismatchError),
            ("7", FieldTypeMismatchError),
            (True, FieldTypeMismatchError),
            ([7, object()], FieldDimensionMismtachError),
            ((), FieldDimensionMismtachError),
            ((5, 7), FieldDimensionMismtachError),
            (set(), FieldDimensionMismtachError),
            ({5, 7}, FieldDimensionMismtachError),
            ([], FieldDimensionMismtachError),
            ([7, 9], FieldDimensionMismtachError),
            ([7, "9"], FieldDimensionMismtachError),
            (["7", "9"], FieldDimensionMismtachError),
            ([[7, 9]], FieldValueTypeMismatchError),
            ([[7, 9], [5]], FieldValueTypeMismatchError),
            ([[7, 9], [5, 3]], FieldValueTypeMismatchError),
            ([["7", "9"]], FieldValueTypeMismatchError)
        )

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ([[]], [[]]),
            ([[self.MDL1, self.MDL2]], [[self.MDL1, self.MDL2]]),
            ([[self.MDL1], [self.MDL2]], [[self.MDL1], [self.MDL2]]),
            ([[{"num": 2}, {"num": 3}]], [[self.MDL1, self.MDL2]]),
            ([[{"num": 2}], [{"num": 3}]], [[self.MDL1], [self.MDL2]]),
        )
