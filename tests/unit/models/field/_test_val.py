from abc import abstractmethod, ABC
from typing import Tuple, Any, Type, final

from models.field import BaseField
from models.field.exceptions import FieldError
from tests.base import TestCase


@final
class TestFieldValue(ABC):
    """
    Class to test the value setting and getting of a field.

    This can be setup and called multiple times for a field.

    To use this, inherit a new class from :class:`TestFieldValue.TestClass`.

    .. seealso::
        https://stackoverflow.com/a/25695512/11571888 to see why there's a class wrapper.
    """

    class TestClass(TestCase):
        """The class to be inherited for :class:`TestFieldValue`."""

        @abstractmethod
        def get_field(self) -> BaseField:
            """
            Should return an instantiated :class:`BaseField` to be tested on value checking.

            :return:
            """
            raise NotImplementedError()

        # region Value checks
        @abstractmethod
        def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
            """
            Values that will be tested on type matching.

            Should return a :class:`tuple` of :class:`tuple` which

            - 1st dimension: value pairs

            - 2nd dimension: value and the expected outcome
            """
            raise NotImplementedError()

        def test_value_type_match(self):
            f = self.get_field()

            for value, expected_outcome in self.get_value_type_match_test():
                with self.subTest(value=value, expected_outcome=expected_outcome):
                    if expected_outcome:
                        self.assertTrue(f.is_type_matched(value))
                    else:
                        self.assertFalse(f.is_type_matched(value))

        @abstractmethod
        def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
            """
            Values that will be tested on validity.

            Should return a :class:`tuple` of :class:`tuple` which

            - 1st dimension: value pairs

            - 2nd dimension: value and the expected validity
            """
            raise NotImplementedError()

        def test_value_validity(self):
            f = self.get_field()

            for value, expected_outcome in self.get_value_validity_test():
                with self.subTest(value=value, expected_outcome=expected_outcome):
                    if expected_outcome:
                        self.assertTrue(f.is_value_valid(value))
                    else:
                        self.assertFalse(f.is_value_valid(value))

        # endregion

        # region Autocast
        @abstractmethod
        def is_auto_cast(self) -> bool:
            """If the field should auto cast."""
            raise NotImplementedError()

        def test_auto_cast(self):
            if self.is_auto_cast():
                self.assertTrue(self.get_field().auto_cast)
            else:
                self.assertFalse(self.get_field().auto_cast)

        @abstractmethod
        def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
            """
            Values that will be casted to the desired type.

            Should return a :class:`tuple` of :class:`tuple` which

            - 1st dimension: value pairs

            - 2nd dimension: value to be casted and the expected value after casting
            """
            raise NotImplementedError()

        def test_cast_value(self):
            f = self.get_field()

            for before, expected in self.get_values_to_cast():
                with self.subTest(before=before, expected=expected):
                    self.assertEqual(f.cast_to_desired_type(before), expected)

        # endregion

        # region Set value
        @abstractmethod
        def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
            """
            Values that will be set to `FieldInstance` and the expected value after setting it.

            Should return a :class:`tuple` of :class:`tuple` which

            - 1st dimension: value pairs

            - 2nd dimension: value and the expected value after setting it
            """
            raise NotImplementedError()

        def test_set_value_to_field(self):
            f = self.get_field()

            for val_to_set, val_to_get in self.get_valid_value_to_set():
                fi = f.new()

                with self.subTest(val_to_set=val_to_set, val_to_get=val_to_get):
                    fi.value = val_to_set
                    self.assertEqual(val_to_get, fi.value)

        @abstractmethod
        def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
            """
            Values that will be set to :class:`models.field._base.FieldInstance` and the exception it should throw.

            Should return a :class:`tuple` of :class:`tuple` which

            - 1st dimension: value pairs

            - 2nd dimension: value and the expected class of :class:`FieldException`
            """
            raise NotImplementedError()

        def test_set_invalid_value_to_field(self):
            f = self.get_field()

            for value, expected_exception in self.get_invalid_value_to_set():
                fi = f.new()

                with self.subTest(value=value, expected_exception=expected_exception):
                    with self.assertRaises(expected_exception):
                        fi.value = value
        # endregion
