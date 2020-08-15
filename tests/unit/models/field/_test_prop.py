from abc import abstractmethod, ABC
from typing import Tuple, Any, Type, final

from models.field import BaseField, ModelDefaultValueExt
from models.field.exceptions import (
    FieldReadOnlyError, FieldInvalidDefaultValueError, FieldNoneNotAllowedError, FieldInstanceClassInvalidError,
    FieldValueRequiredError
)
from tests.base import TestCase


@final
class TestFieldProperty(ABC):
    """
    Class to test the property of a field.

    This should only being called once per field.

    To use this, inherit a new class from :class:`TestFieldProperty.TestClass`.

    .. seealso::
        https://stackoverflow.com/a/25695512/11571888 to see why there's a class wrapper.
    """

    class TestClass(TestCase):
        """The class to be inherited for :class:`TestFieldProperty`."""

        # region ### Data used to execute the tests ###
        @abstractmethod
        def get_field_class(self) -> Type[BaseField]:
            """Field class to be tested."""
            raise NotImplementedError()

        @classmethod
        def get_initialize_required_args(cls) -> Tuple[Any, ...]:
            """Additional required arguments to initialize the :class:`FieldBase`."""
            return tuple()

        def get_initialized_field(self, **kwargs) -> BaseField:
            """Get an initialized field with default value being set."""
            return self.get_field_class()("k", *self.get_initialize_required_args(), **kwargs)

        @abstractmethod
        def valid_not_none_obj_value(self) -> Any:
            """Value to be used on some tests that need this."""
            raise NotImplementedError()

        # endregion

        # region Field Key
        def test_field_key(self):
            self.assertEqual("k", self.get_initialized_field().key)

        # endregion

        # region Null Object
        @abstractmethod
        def expected_none_object(self) -> Any:
            raise NotImplementedError()

        def test_none_obj(self):
            self.assertEqual(self.expected_none_object(), self.get_initialized_field().none_obj())

        # endregion

        # region Auto Cast
        def test_auto_cast(self):
            f = self.get_initialized_field(auto_cast=True)
            self.assertTrue(f.auto_cast)
            f = self.get_initialized_field(auto_cast=False)
            self.assertFalse(f.auto_cast)

        # endregion

        # region Readonly
        def test_readonly(self):
            f = self.get_initialized_field(readonly=True)

            self.assertTrue(f.read_only, "Field not readonly")

            fi = f.new()
            with self.assertRaises(FieldReadOnlyError):
                fi.value = self.valid_not_none_obj_value()

        def test_not_readonly(self):
            f = self.get_initialized_field(readonly=False)

            self.assertFalse(f.read_only, "Field is readonly")

            fi = f.new()
            fi.value = self.valid_not_none_obj_value()

        # endregion

        # region Default value validity
        @abstractmethod
        def get_valid_default_values(self) -> Tuple[Tuple[Any, Any], ...]:
            """
            1st dimension: value combinations

            2nd dimension
                - default value to be used

                - expected value when getting it **with** ``autocast``

            .. Note::
                ``None`` should not be included. It will be automatically tested.
            """
            raise NotImplementedError()

        def test_properties_default_valid_no_autocast(self):
            for default_val, expected_autocast in self.get_valid_default_values():
                with self.subTest(default_val=default_val):
                    # Default value could be invalid if `auto_cast` set to `False`
                    # while the value does not considered valid
                    try:
                        f = self.get_initialized_field(auto_cast=False, default=default_val)
                        fi = f.new()
                        self.assertEqual(expected_autocast, fi.value)
                    except FieldInvalidDefaultValueError:
                        pass

        def test_properties_default_valid_autocast(self):
            for default_val, expected_autocast in self.get_valid_default_values():
                with self.subTest(default_val=default_val, expected_autocast=expected_autocast):
                    f = self.get_initialized_field(auto_cast=True, default=default_val)
                    fi = f.new()
                    self.assertEqual(expected_autocast, fi.value)

        @abstractmethod
        def get_invalid_default_values(self) -> Tuple[Any, ...]:
            """
            1st dimension: invalid default values

            .. Note::
                ``None`` should not be included. It will be automatically tested.
            """
            raise NotImplementedError()

        def test_properties_default_invalid(self):
            for invalid_default_value in self.get_invalid_default_values():
                with self.subTest(invalid_default_value=invalid_default_value):
                    with self.assertRaises(FieldInvalidDefaultValueError):
                        self.get_initialized_field(default=invalid_default_value)

        # endregion

        # region Handling `None`
        def test_allow_none_val_control(self):
            f = self.get_initialized_field(allow_none=True, readonly=False)

            self.assertTrue(f.allow_none)

            self.assertTrue(f.is_type_matched(None))
            self.assertTrue(f.is_value_valid(None))

            fi = f.new()
            fi.value = None

        def test_allow_none_set_default(self):
            self.get_initialized_field(allow_none=True, default=None)

        def test_not_allow_none_val_control(self):
            f = self.get_initialized_field(allow_none=False, readonly=False)

            self.assertFalse(f.allow_none)

            self.assertFalse(f.is_type_matched(None))
            self.assertFalse(f.is_value_valid(None))

            fi = f.new()
            with self.assertRaises(FieldNoneNotAllowedError):
                fi.value = None

        def test_not_allow_none_set_default(self):
            f = self.get_initialized_field(default=None, allow_none=False)
            self.assertEqual(f.none_obj(), f.default_value)

        # endregion

        # region Check `is_empty`
        def test_is_empty(self):
            f = self.get_initialized_field()

            test_data = (
                (None, True),
                (self.valid_not_none_obj_value(), False),
                (f.none_obj(), True)
            )

            for value, expected_outcome in test_data:
                with self.subTest(value=value, expected_outcome=expected_outcome):
                    self.assertEqual(f.is_empty(value), expected_outcome)

        # endregion

        # region Extended default value
        def test_default_required(self):
            f = self.get_initialized_field(default=ModelDefaultValueExt.Required)
            self.assertEqual(ModelDefaultValueExt.Required, f.default_value)
            with self.assertRaises(FieldValueRequiredError):
                f.new()

            # This value may change -> Calling the method twice may generate different value
            val = self.valid_not_none_obj_value()
            fi = f.new(val)
            self.assertEqual(fi.value, val)

        def test_default_optional(self):
            f = self.get_initialized_field(default=ModelDefaultValueExt.Optional)
            self.assertEqual(ModelDefaultValueExt.Optional, f.default_value)

            fi = f.new()
            self.assertEqual(fi.value, f.none_obj())

        # endregion

        # region Test instance class
        def test_incorrect_instance_class(self):
            with self.assertRaises(FieldInstanceClassInvalidError):
                self.get_initialized_field(inst_cls=object)

        # endregion

        # region Types
        @abstractmethod
        def get_expected_types(self) -> Tuple[Type[Any], ...]:
            """Get the expected types of the field."""
            raise NotImplementedError()

        def test_expected_types(self):
            self.assertTupleEqual(self.get_expected_types(), self.get_initialized_field().expected_types)

        @abstractmethod
        def get_desired_type(self) -> Type[Any]:
            """Get the desired type of the field."""
            raise NotImplementedError()

        def test_desired_types(self):
            self.assertEqual(self.get_desired_type(), self.get_initialized_field().desired_type)

        # endregion
