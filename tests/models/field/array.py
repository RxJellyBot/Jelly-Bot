from typing import Tuple, Any, Type

from django.test import TestCase

from field.exceptions import FieldException
from models.field import BaseField, ArrayField
from models.field.exceptions import (
    FieldTypeMismatch, FieldValueTypeMismatch, FieldCastingFailed,
    FieldMaxLengthReached, FieldInvalidDefaultValue, FieldNoneNotAllowed
)

from ._test_val import TestFieldValueMixin
from ._test_prop import TestFieldPropertyMixin


class TestArrayFieldValueDefault(TestFieldValueMixin):
    def get_field(self) -> BaseField:
        return ArrayField("k", int)

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
            ((), True),
            ((5, 7), True),
            (set(), True),
            ({5, 7}, True),
            ([], True),
            ([7, 9], True),
            ([7, "9"], True),
            (["7", "9"], True)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            ({}, False),
            (7, False),
            ("7", False),
            (True, False),
            (object(), False),
            ((), True),
            ((5, 7), True),
            (set(), True),
            ({5, 7}, True),
            ([], True),
            ([7, 9], True),
            ([7, "9"], True),
            (["7", "9"], True)
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ((), []),
            ((5, 7), [5, 7]),
            (set(), []),
            ({5, 7}, [5, 7]),
            ([], []),
            ([7, 9], [7, 9]),
            ([7, "9"], [7, 9]),
            (["7", "9"], [7, 9])
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldException]], ...]:
        return (
            (None, FieldNoneNotAllowed),
            ({}, FieldTypeMismatch),
            (7, FieldTypeMismatch),
            ("7", FieldTypeMismatch),
            (True, FieldTypeMismatch),
            ([7, object()], FieldCastingFailed),
        )

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ((), []),
            ((5, 7), [5, 7]),
            (set(), []),
            ((5, 7), [5, 7]),
            ((), []),
            ({5, 7}, [5, 7]),
            ([], []),
            ([7, 9], [7, 9]),
            ([7, "9"], [7, 9]),
            (["7", "9"], [7, 9])
        )


class TestArrayFieldValueAllowNone(TestFieldValueMixin):
    def get_field(self) -> BaseField:
        return ArrayField("k", int, allow_none=True)

    def is_auto_cast(self) -> bool:
        return True

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            ({}, False),
            (7, False),
            ("7", False),
            (True, False),
            (object(), False),
            ((), True),
            ((5, 7), True),
            (set(), True),
            ({5, 7}, True),
            ([], True),
            ([7, 9], True),
            ([7, "9"], True),
            (["7", "9"], True)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            ({}, False),
            (7, False),
            ("7", False),
            (True, False),
            (object(), False),
            ((), True),
            ((5, 7), True),
            (set(), True),
            ({5, 7}, True),
            ([], True),
            ([7, 9], True),
            ([7, "9"], True),
            (["7", "9"], True)
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            ((), []),
            ((5, 7), [5, 7]),
            (set(), []),
            ({5, 7}, [5, 7]),
            ([], []),
            ([7, 9], [7, 9]),
            ([7, "9"], [7, 9]),
            (["7", "9"], [7, 9])
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldException]], ...]:
        return (
            ({}, FieldTypeMismatch),
            (7, FieldTypeMismatch),
            ("7", FieldTypeMismatch),
            (True, FieldTypeMismatch),
            ([7, object()], FieldCastingFailed),
        )

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            ((), []),
            ((5, 7), [5, 7]),
            (set(), []),
            ((5, 7), [5, 7]),
            ((), []),
            ({5, 7}, [5, 7]),
            ([], []),
            ([7, 9], [7, 9]),
            ([7, "9"], [7, 9]),
            (["7", "9"], [7, 9])
        )


class TestArrayFieldValueNoAutoCast(TestFieldValueMixin):
    def get_field(self) -> BaseField:
        return ArrayField("k", int, auto_cast=False)

    def is_auto_cast(self) -> bool:
        return False

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            ({}, False),
            (7, False),
            ("7", False),
            (True, False),
            (object(), False),
            ((), True),
            ((5, 7), True),
            (set(), True),
            ({5, 7}, True),
            ([], True),
            ([7, 9], True),
            ([7, "9"], False),
            (["7", "9"], False)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            ({}, False),
            (7, False),
            ("7", False),
            (True, False),
            (object(), False),
            ((), True),
            ((5, 7), True),
            (set(), True),
            ({5, 7}, True),
            ([], True),
            ([7, 9], True),
            ([7, "9"], False),
            (["7", "9"], False)
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ((), ()),
            ((5, 7), (5, 7)),
            (set(), set()),
            ({5, 7}, {5, 7}),
            ((), ()),
            ((5, 7), (5, 7)),
            ([], []),
            ([7, 9], [7, 9]),
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldException]], ...]:
        return (
            (None, FieldNoneNotAllowed),
            ({}, FieldTypeMismatch),
            (7, FieldTypeMismatch),
            ("7", FieldTypeMismatch),
            (True, FieldTypeMismatch),
            ([7, object()], FieldValueTypeMismatch),
            ([7, "9"], FieldValueTypeMismatch),
            (["7", "9"], FieldValueTypeMismatch)
        )

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ((), []),
            ((5, 7), [5, 7]),
            (set(), []),
            ({5, 7}, [5, 7]),
            ([], []),
            ([7, 9], [7, 9])
        )


class TestArrayFieldValueLengthLimited(TestFieldValueMixin):
    def get_field(self) -> BaseField:
        return ArrayField("k", int, max_len=3)

    def is_auto_cast(self) -> bool:
        return True

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            ([7], True),
            ([7, 9], True),
            ([7, 9, 11], True),
            ([7, 9, 11, 13], True),
            ([7, 9, 11, 13, 15], True),
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            ([7], True),
            ([7, 9], True),
            ([7, 9, 11], True),
            ([7, 9, 11, 13], False),
            ([7, 9, 11, 13, 15], False),
        )

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return ()

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ([7], [7]),
            ([7, 9], [7, 9]),
            ([7, 9, 11], [7, 9, 11])
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldException]], ...]:
        return (
            ([7, 6, 5, 4], FieldMaxLengthReached),
            ([7, 6, 5, 4, 3], FieldMaxLengthReached),
        )


class TestArrayFieldProperty(TestFieldPropertyMixin):
    def get_field_class(self) -> Type[BaseField]:
        return ArrayField

    def get_initialize_required_args(self) -> Tuple[Any, ...]:
        return int,

    def expected_none_object(self) -> Any:
        return []

    def valid_not_none_value(self) -> Any:
        return [5]

    def get_valid_default_values(self) -> Tuple[Tuple[Any, Any], ...]:
        # Not testing `set` because it's unordered
        return (
            ([5, 7], [5, 7]),
            ([5, "7"], [5, 7]),
            (["5", "7"], [5, 7]),
            (("5", "7"), [5, 7])
        )

    def get_invalid_default_values(self) -> Tuple[Any, ...]:
        return 7, "7", True, {}

    def get_expected_types(self) -> Tuple[Type[Any], ...]:
        return list, tuple, set

    def get_desired_type(self) -> Type[Any]:
        return list


class TestArrayFieldExtra(TestCase):
    def test_properties_max_length(self):
        f = ArrayField("af", int, max_len=3)
        self.assertEquals(3, f.max_len)
        self.assertTrue(f.is_type_matched([1, 2]))
        self.assertTrue(f.is_value_valid([1, 2]))
        self.assertTrue(f.is_type_matched([1, 2, 3]))
        self.assertTrue(f.is_value_valid([1, 2, 3]))
        self.assertTrue(f.is_type_matched([1, 2, 3, 4]))
        self.assertFalse(f.is_value_valid([1, 2, 3, 4]))
        self.assertTrue(f.is_type_matched([1, 2, 3, 4, 7, 9]))
        self.assertFalse(f.is_value_valid([1, 2, 3, 4, 7, 9]))

        with self.assertRaises(FieldInvalidDefaultValue):
            ArrayField("af", int, max_len=5, default=[0, 1, 2, 3, 4, 5])
        with self.assertRaises(ValueError):
            ArrayField("af", int, max_len=-1)
        with self.assertRaises(TypeError):
            ArrayField("af", int, max_len=7.5)


# For single file testing, or these abstract classes will be instantiated, causing error
del TestFieldValueMixin
del TestFieldPropertyMixin
