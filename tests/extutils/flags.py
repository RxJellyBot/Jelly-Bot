from extutils.flags import (
    FlagCodeEnum, FlagSingleEnum, FlagDoubleEnum, FlagPrefixedDoubleEnum,
    is_flag_instance, is_flag_class, is_flag_single, is_flag_double
)
from tests.base import TestCase


class CodeEnum(FlagCodeEnum):
    A = 1
    B = 2


class CodeSingleEnum(FlagSingleEnum):
    A = 1, "C"
    B = 2, "D"


class CodeDoubleEnum(FlagDoubleEnum):
    A = 1, "C", "E"
    B = 2, "D", "F"

    @classmethod
    def default(cls):
        return CodeDoubleEnum.A


class CodePrefixedDoubleEnum(FlagPrefixedDoubleEnum):
    @property
    def code_prefix(self) -> str:
        return "P"

    A = 1, "C", "E"
    B = 2, "D", "F"


class TestFlagMisc(TestCase):
    def test_flag_instance(self):
        self.assertTrue(is_flag_instance(CodeEnum.A))
        self.assertTrue(is_flag_instance(CodeSingleEnum.A))
        self.assertTrue(is_flag_instance(CodeDoubleEnum.A))
        self.assertTrue(is_flag_instance(CodePrefixedDoubleEnum.A))
        self.assertFalse(is_flag_instance(5))

    def test_flag_code(self):
        self.assertTrue(is_flag_class(CodeEnum))
        self.assertFalse(is_flag_single(CodeEnum))
        self.assertFalse(is_flag_double(CodeEnum))

    def test_flag_single(self):
        self.assertTrue(is_flag_class(CodeSingleEnum))
        self.assertTrue(is_flag_single(CodeSingleEnum))
        self.assertFalse(is_flag_double(CodeSingleEnum))

    def test_flag_double(self):
        self.assertTrue(is_flag_class(CodeDoubleEnum))
        self.assertTrue(is_flag_single(CodeDoubleEnum))
        self.assertTrue(is_flag_double(CodeDoubleEnum))

    def test_flag_prefixed_double(self):
        self.assertTrue(is_flag_class(CodePrefixedDoubleEnum))
        self.assertTrue(is_flag_single(CodePrefixedDoubleEnum))
        self.assertTrue(is_flag_double(CodePrefixedDoubleEnum))

    def test_enum_cross_equals(self):
        self.assertNotEquals(CodeEnum.A, CodeSingleEnum.A)
        self.assertNotEquals(CodeEnum.A, CodeDoubleEnum.A)
        self.assertNotEquals(CodeEnum.A, CodePrefixedDoubleEnum.A)
        self.assertNotEquals(CodeSingleEnum.A, CodeDoubleEnum.A)
        self.assertNotEquals(CodeSingleEnum.A, CodePrefixedDoubleEnum.A)
        self.assertNotEquals(CodeDoubleEnum.A, CodePrefixedDoubleEnum.A)

    def test_enum_cross_cast(self):
        self.assertNotEquals(CodeEnum.cast("1"), CodeSingleEnum.cast("1"))
        self.assertNotEquals(CodeEnum.cast("1"), CodeDoubleEnum.cast("1"))
        self.assertNotEquals(CodeEnum.cast("1"), CodePrefixedDoubleEnum.cast("1"))
        self.assertNotEquals(CodeSingleEnum.cast("1"), CodeDoubleEnum.cast("1"))
        self.assertNotEquals(CodeSingleEnum.cast("1"), CodePrefixedDoubleEnum.cast("1"))
        self.assertNotEquals(CodeDoubleEnum.cast("1"), CodePrefixedDoubleEnum.cast("1"))

    def test_enum_cross_contains(self):
        self.assertFalse(CodeEnum.contains(CodeSingleEnum.A))
        self.assertFalse(CodeEnum.contains(CodeDoubleEnum.A))
        self.assertFalse(CodeEnum.contains(CodePrefixedDoubleEnum.A))
        self.assertFalse(CodeSingleEnum.contains(CodeDoubleEnum.A))
        self.assertFalse(CodeSingleEnum.contains(CodePrefixedDoubleEnum.A))
        self.assertFalse(CodeDoubleEnum.contains(CodePrefixedDoubleEnum.A))


class TestFlagCodeEnum(TestCase):
    def test_enum_equals(self):
        self.assertEqual(1, CodeEnum.A)
        self.assertEqual("1", CodeEnum.A)
        self.assertNotEquals(2, CodeEnum.A)
        self.assertEqual(CodeEnum.A, CodeEnum.A)
        self.assertNotEquals(CodeEnum.A, CodeEnum.B)

    def test_enum_greater(self):
        self.assertFalse(CodeEnum.A > CodeEnum.B)
        self.assertGreater(CodeEnum.B, CodeEnum.A)
        self.assertGreaterEqual(CodeEnum.B, CodeEnum.A)
        self.assertGreaterEqual(CodeEnum.A, CodeEnum.A)

    def test_enum_less(self):
        self.assertFalse(CodeEnum.B < CodeEnum.A)
        self.assertLess(CodeEnum.A, CodeEnum.B)
        self.assertLessEqual(CodeEnum.A, CodeEnum.B)
        self.assertLessEqual(CodeEnum.A, CodeEnum.A)

    def test_enum_properties(self):
        self.assertEqual(1, CodeEnum.A.code)
        self.assertEqual("1", CodeEnum.A.code_str)

    def test_enum_cast(self):
        self.assertEqual(1, int(CodeEnum.A))
        self.assertEqual(CodeEnum.A, CodeEnum.cast(1))
        self.assertEqual(CodeEnum.A, CodeEnum.cast("1"))
        self.assertEqual(CodeEnum.A, CodeEnum.cast("A"))
        with self.assertRaises(TypeError):
            CodeEnum.cast(True)
        with self.assertRaises(ValueError):
            CodeEnum.cast("C")
        with self.assertRaises(ValueError):
            CodeEnum.cast(3)
        self.assertIsNone(CodeEnum.cast("C", silent_fail=True))

    def test_enum_misc(self):
        self.assertTrue(CodeEnum.contains(1))
        self.assertTrue(CodeEnum.contains("1"))
        self.assertTrue(CodeEnum.contains("A"))
        self.assertTrue(CodeEnum.contains(CodeEnum.A))
        self.assertFalse(CodeEnum.contains(3))
        self.assertFalse(CodeEnum.contains("C"))
        self.assertFalse(CodeEnum.contains(False))

    def test_enum_default(self):
        with self.assertRaises(ValueError):
            CodeEnum.default()


class TestFlagSingleCodeEnum(TestCase):
    def test_enum_equals(self):
        self.assertEqual(1, CodeSingleEnum.A)
        self.assertEqual("1", CodeSingleEnum.A)
        self.assertNotEquals("C", CodeSingleEnum.A)
        self.assertNotEquals(2, CodeSingleEnum.A)
        self.assertEqual(CodeSingleEnum.A, CodeSingleEnum.A)
        self.assertNotEquals(CodeSingleEnum.A, CodeSingleEnum.B)

    def test_enum_greater(self):
        self.assertFalse(CodeSingleEnum.A > CodeSingleEnum.B)
        self.assertGreater(CodeSingleEnum.B, CodeSingleEnum.A)
        self.assertGreaterEqual(CodeSingleEnum.B, CodeSingleEnum.A)
        self.assertGreaterEqual(CodeSingleEnum.A, CodeSingleEnum.A)

    def test_enum_less(self):
        self.assertFalse(CodeSingleEnum.B < CodeSingleEnum.A)
        self.assertLess(CodeSingleEnum.A, CodeSingleEnum.B)
        self.assertLessEqual(CodeSingleEnum.A, CodeSingleEnum.B)
        self.assertLessEqual(CodeSingleEnum.A, CodeSingleEnum.A)

    def test_enum_properties(self):
        self.assertEqual(1, CodeSingleEnum.A.code)
        self.assertEqual("1", CodeSingleEnum.A.code_str)
        self.assertEqual("C", CodeSingleEnum.A.key)

    def test_enum_cast(self):
        self.assertEqual(1, int(CodeSingleEnum.A))
        self.assertEqual(CodeSingleEnum.A, CodeSingleEnum.cast(1))
        self.assertEqual(CodeSingleEnum.A, CodeSingleEnum.cast("1"))
        self.assertEqual(CodeSingleEnum.A, CodeSingleEnum.cast("A"))
        with self.assertRaises(TypeError):
            CodeSingleEnum.cast(True)
        with self.assertRaises(ValueError):
            CodeSingleEnum.cast("C")
        with self.assertRaises(ValueError):
            CodeSingleEnum.cast(3)
        self.assertIsNone(CodeSingleEnum.cast("C", silent_fail=True))

    def test_enum_misc(self):
        self.assertTrue(CodeSingleEnum.contains(1))
        self.assertTrue(CodeSingleEnum.contains("1"))
        self.assertTrue(CodeSingleEnum.contains("A"))
        self.assertTrue(CodeSingleEnum.contains(CodeSingleEnum.A))
        self.assertFalse(CodeSingleEnum.contains(3))
        self.assertFalse(CodeSingleEnum.contains("C"))
        self.assertFalse(CodeSingleEnum.contains(False))

    def test_enum_default(self):
        with self.assertRaises(ValueError):
            CodeSingleEnum.default()


class TestFlagDoubleCodeEnum(TestCase):
    def test_enum_equals(self):
        self.assertEqual(1, CodeDoubleEnum.A)
        self.assertEqual("1", CodeDoubleEnum.A)
        self.assertNotEquals("C", CodeDoubleEnum.A)
        self.assertNotEquals("E", CodeDoubleEnum.A)
        self.assertNotEquals(2, CodeDoubleEnum.A)
        self.assertEqual(CodeDoubleEnum.A, CodeDoubleEnum.A)
        self.assertNotEquals(CodeDoubleEnum.A, CodeDoubleEnum.B)

    def test_enum_greater(self):
        self.assertFalse(CodeDoubleEnum.A > CodeDoubleEnum.B)
        self.assertGreater(CodeDoubleEnum.B, CodeDoubleEnum.A)
        self.assertGreaterEqual(CodeDoubleEnum.B, CodeDoubleEnum.A)
        self.assertGreaterEqual(CodeDoubleEnum.A, CodeDoubleEnum.A)

    def test_enum_less(self):
        self.assertFalse(CodeDoubleEnum.B < CodeDoubleEnum.A)
        self.assertLess(CodeDoubleEnum.A, CodeDoubleEnum.B)
        self.assertLessEqual(CodeDoubleEnum.A, CodeDoubleEnum.B)
        self.assertLessEqual(CodeDoubleEnum.A, CodeDoubleEnum.A)

    def test_enum_properties(self):
        self.assertEqual(1, CodeDoubleEnum.A.code)
        self.assertEqual("1", CodeDoubleEnum.A.code_str)
        self.assertEqual("C", CodeDoubleEnum.A.key)
        self.assertEqual("E", CodeDoubleEnum.A.description)

    def test_enum_cast(self):
        self.assertEqual(1, int(CodeDoubleEnum.A))
        self.assertEqual(CodeDoubleEnum.A, CodeDoubleEnum.cast(1))
        self.assertEqual(CodeDoubleEnum.A, CodeDoubleEnum.cast("1"))
        self.assertEqual(CodeDoubleEnum.A, CodeDoubleEnum.cast("A"))
        with self.assertRaises(TypeError):
            CodeDoubleEnum.cast(True)
        with self.assertRaises(ValueError):
            CodeDoubleEnum.cast("C")
        with self.assertRaises(ValueError):
            CodeDoubleEnum.cast(3)
        self.assertIsNone(CodeDoubleEnum.cast("C", silent_fail=True))

    def test_enum_misc(self):
        self.assertTrue(CodeDoubleEnum.contains(1))
        self.assertTrue(CodeDoubleEnum.contains("1"))
        self.assertTrue(CodeDoubleEnum.contains("A"))
        self.assertTrue(CodeDoubleEnum.contains(CodeDoubleEnum.A))
        self.assertFalse(CodeDoubleEnum.contains(3))
        self.assertFalse(CodeDoubleEnum.contains("C"))
        self.assertFalse(CodeDoubleEnum.contains(False))

    def test_enum_default(self):
        self.assertEqual(CodeDoubleEnum.A, CodeDoubleEnum.default())


class TestFlagPrefixedDoubleCodeEnum(TestCase):
    def test_enum_equals(self):
        self.assertEqual(1, CodePrefixedDoubleEnum.A)
        self.assertEqual("1", CodePrefixedDoubleEnum.A)
        self.assertEqual("P1", CodePrefixedDoubleEnum.A)
        self.assertNotEquals("C", CodePrefixedDoubleEnum.A)
        self.assertNotEquals("E", CodePrefixedDoubleEnum.A)
        self.assertNotEquals(2, CodePrefixedDoubleEnum.A)
        self.assertEqual(CodePrefixedDoubleEnum.A, CodePrefixedDoubleEnum.A)
        self.assertNotEquals(CodePrefixedDoubleEnum.A, CodePrefixedDoubleEnum.B)

    def test_enum_greater(self):
        self.assertFalse(CodePrefixedDoubleEnum.A > CodePrefixedDoubleEnum.B)
        self.assertGreater(CodePrefixedDoubleEnum.B, CodePrefixedDoubleEnum.A)
        self.assertGreaterEqual(CodePrefixedDoubleEnum.B, CodePrefixedDoubleEnum.A)
        self.assertGreaterEqual(CodePrefixedDoubleEnum.A, CodePrefixedDoubleEnum.A)

    def test_enum_less(self):
        self.assertFalse(CodePrefixedDoubleEnum.B < CodePrefixedDoubleEnum.A)
        self.assertLess(CodePrefixedDoubleEnum.A, CodePrefixedDoubleEnum.B)
        self.assertLessEqual(CodePrefixedDoubleEnum.A, CodePrefixedDoubleEnum.B)
        self.assertLessEqual(CodePrefixedDoubleEnum.A, CodePrefixedDoubleEnum.A)

    def test_enum_properties(self):
        self.assertEqual(1, CodePrefixedDoubleEnum.A.code)
        self.assertEqual("P1", CodePrefixedDoubleEnum.A.code_str)
        self.assertEqual("C", CodePrefixedDoubleEnum.A.key)
        self.assertEqual("E", CodePrefixedDoubleEnum.A.description)

    def test_enum_cast(self):
        self.assertEqual(1, int(CodePrefixedDoubleEnum.A))
        self.assertEqual(CodePrefixedDoubleEnum.A, CodePrefixedDoubleEnum.cast(1))
        self.assertEqual(CodePrefixedDoubleEnum.A, CodePrefixedDoubleEnum.cast("1"))
        self.assertEqual(CodePrefixedDoubleEnum.A, CodePrefixedDoubleEnum.cast("P1"))
        self.assertEqual(CodePrefixedDoubleEnum.A, CodePrefixedDoubleEnum.cast("A"))
        with self.assertRaises(TypeError):
            CodePrefixedDoubleEnum.cast(True)
        with self.assertRaises(ValueError):
            CodePrefixedDoubleEnum.cast("C")
        with self.assertRaises(ValueError):
            CodePrefixedDoubleEnum.cast(3)
        self.assertIsNone(CodePrefixedDoubleEnum.cast("C", silent_fail=True))

    def test_enum_misc(self):
        self.assertTrue(CodePrefixedDoubleEnum.contains(1))
        self.assertTrue(CodePrefixedDoubleEnum.contains("1"))
        self.assertTrue(CodePrefixedDoubleEnum.contains("P1"))
        self.assertTrue(CodePrefixedDoubleEnum.contains("A"))
        self.assertTrue(CodePrefixedDoubleEnum.contains(CodePrefixedDoubleEnum.A))
        self.assertFalse(CodePrefixedDoubleEnum.contains(3))
        self.assertFalse(CodePrefixedDoubleEnum.contains("C"))
        self.assertFalse(CodePrefixedDoubleEnum.contains(False))

    def test_enum_default(self):
        with self.assertRaises(ValueError):
            CodePrefixedDoubleEnum.default()
