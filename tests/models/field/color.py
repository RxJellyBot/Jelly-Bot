from typing import Type, Any, Tuple

from extutils.color import Color, ColorFactory
from models.field import ColorField, BaseField
from models.field.exceptions import (
    FieldTypeMismatch, FieldNoneNotAllowed, FieldValueInvalid, FieldException
)

from ._test_val import TestFieldValue
from ._test_prop import TestFieldProperty

__all__ = ["TestColorFieldProperty", "TestColorFieldValueAllowNone",
           "TestColorFieldValueDefault", "TestColorFieldValueNoAutoCast"]


class TestColorFieldProperty(TestFieldProperty):
    def get_field_class(self) -> Type[BaseField]:
        return ColorField

    def valid_not_none_value(self) -> Any:
        return ColorFactory.WHITE

    def expected_none_object(self) -> Any:
        return ColorFactory.DEFAULT

    def get_valid_default_values(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (ColorFactory.DEFAULT, ColorFactory.DEFAULT),
            (5723991, Color(5723991)),
            ("#575757", Color(5723991)),
            ("575757", Color(5723991)),
            (Color(5723991), Color(5723991))
        )

    def get_invalid_default_values(self) -> Tuple[Any, ...]:
        return True, -8000, 20000000, "GGGGGG"

    def get_expected_types(self) -> Tuple[Type[Any], ...]:
        return Color, int, str

    def get_desired_type(self) -> Type[Any]:
        return Color


class TestColorFieldValueDefault(TestFieldValue):
    def get_field(self) -> BaseField:
        return ColorField("k")

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (ColorFactory.DEFAULT, True),
            (5723991, True),
            ("#575757", True),
            ("575757", True),
            (Color(5723991), True),
            (True, False),
            (-8000, True),
            (20000000, True),
            ("GGGGGG", True)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (ColorFactory.DEFAULT, True),
            (5723991, True),
            ("#575757", True),
            ("575757", True),
            (Color(5723991), True),
            (True, False),
            (-8000, False),
            (20000000, False),
            ("GGGGGG", False)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (ColorFactory.DEFAULT, ColorFactory.DEFAULT),
            (5723991, Color(5723991)),
            ("#575757", Color(5723991)),
            ("575757", Color(5723991)),
            (Color(5723991), Color(5723991))
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (ColorFactory.DEFAULT, ColorFactory.DEFAULT),
            (5723991, Color(5723991)),
            ("#575757", Color(5723991)),
            ("575757", Color(5723991)),
            (Color(5723991), Color(5723991))
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldException]], ...]:
        return (
            (None, FieldNoneNotAllowed),
            (True, FieldTypeMismatch),
            (-8000, FieldValueInvalid),
            (20000000, FieldValueInvalid),
            ("GGGGGG", FieldValueInvalid),
        )


class TestColorFieldValueAllowNone(TestFieldValue):
    def get_field(self) -> BaseField:
        return ColorField("k", allow_none=True)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            (ColorFactory.DEFAULT, True),
            (5723991, True),
            ("#575757", True),
            ("575757", True),
            (Color(5723991), True),
            (True, False),
            (-8000, True),
            (20000000, True),
            ("GGGGGG", True)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            (ColorFactory.DEFAULT, True),
            (5723991, True),
            ("#575757", True),
            ("575757", True),
            (Color(5723991), True),
            (True, False),
            (-8000, False),
            (20000000, False),
            ("GGGGGG", False)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            (ColorFactory.DEFAULT, ColorFactory.DEFAULT),
            (5723991, Color(5723991)),
            ("#575757", Color(5723991)),
            ("575757", Color(5723991)),
            (Color(5723991), Color(5723991))
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            (ColorFactory.DEFAULT, ColorFactory.DEFAULT),
            (5723991, Color(5723991)),
            ("#575757", Color(5723991)),
            ("575757", Color(5723991)),
            (Color(5723991), Color(5723991))
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldException]], ...]:
        return (
            (True, FieldTypeMismatch),
            (-8000, FieldValueInvalid),
            (20000000, FieldValueInvalid),
            ("GGGGGG", FieldValueInvalid),
        )


class TestColorFieldValueNoAutoCast(TestFieldValue):
    def get_field(self) -> BaseField:
        return ColorField("k", auto_cast=False)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (ColorFactory.DEFAULT, True),
            (5723991, True),
            ("#575757", True),
            ("575757", True),
            (Color(5723991), True),
            (True, False),
            (-8000, True),
            (20000000, True),
            ("GGGGGG", True)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (ColorFactory.DEFAULT, True),
            (5723991, True),
            ("#575757", True),
            ("575757", True),
            (Color(5723991), True),
            (True, False),
            (-8000, False),
            (20000000, False),
            ("GGGGGG", False)
        )

    def is_auto_cast(self) -> bool:
        return False

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (ColorFactory.DEFAULT, ColorFactory.DEFAULT),
            (5723991, Color(5723991)),
            ("#575757", Color(5723991)),
            ("575757", Color(5723991)),
            (Color(5723991), Color(5723991))
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (ColorFactory.DEFAULT, ColorFactory.DEFAULT),
            (5723991, 5723991),
            ("#575757", "#575757"),
            ("575757", "575757"),
            (Color(5723991), Color(5723991))
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldException]], ...]:
        return (
            (None, FieldNoneNotAllowed),
            (True, FieldTypeMismatch),
            (-8000, FieldValueInvalid),
            (20000000, FieldValueInvalid),
            ("GGGGGG", FieldValueInvalid),
        )


# These abstract classes will be instantiated (causing error) if not deleted
del TestFieldValue
del TestFieldProperty
