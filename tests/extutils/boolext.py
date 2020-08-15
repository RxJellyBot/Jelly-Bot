from extutils.boolext import StrBoolResult, to_bool, WORD_TRUE, WORD_FALSE, CASE_INSENSITIVE
from tests.base import TestCase

__all__ = ["TestBooleanExtension"]


class TestBooleanExtension(TestCase):
    def test_true(self):
        for w in WORD_TRUE:
            w_lower = w.lower()
            w_upper = w.upper()
            with self.subTest(w_lower=w_lower, w_upper=w_upper, w=w):
                if CASE_INSENSITIVE:
                    self.assertEqual(StrBoolResult.TRUE, to_bool(w))
                    self.assertEqual(StrBoolResult.TRUE, to_bool(w_lower))
                    self.assertEqual(StrBoolResult.TRUE, to_bool(w_upper))
                else:
                    self.assertEqual(StrBoolResult.TRUE, to_bool(w))
                    if w == w_lower:
                        self.assertEqual(StrBoolResult.TRUE, to_bool(w_lower))
                    else:
                        self.assertNotEqual(StrBoolResult.TRUE, to_bool(w_lower))
                    if w == w_upper:
                        self.assertEqual(StrBoolResult.TRUE, to_bool(w_upper))
                    else:
                        self.assertNotEqual(StrBoolResult.TRUE, to_bool(w_upper))

                self.assertNotEqual(StrBoolResult.FALSE, to_bool(w))
                self.assertNotEqual(StrBoolResult.UNKNOWN, to_bool(w))
                self.assertNotEqual(StrBoolResult.FALSE, to_bool(w_lower))
                self.assertNotEqual(StrBoolResult.UNKNOWN, to_bool(w_lower))
                self.assertNotEqual(StrBoolResult.FALSE, to_bool(w_upper))
                self.assertNotEqual(StrBoolResult.UNKNOWN, to_bool(w_upper))

    def test_false(self):
        for w in WORD_FALSE:
            w_lower = w.lower()
            w_upper = w.upper()
            with self.subTest(w_lower=w_lower, w_upper=w_upper, w=w):
                if CASE_INSENSITIVE:
                    self.assertEqual(StrBoolResult.FALSE, to_bool(w))
                    self.assertEqual(StrBoolResult.FALSE, to_bool(w_lower))
                    self.assertEqual(StrBoolResult.FALSE, to_bool(w_upper))
                else:
                    self.assertEqual(StrBoolResult.FALSE, to_bool(w))
                    if w == w_lower:
                        self.assertEqual(StrBoolResult.FALSE, to_bool(w_lower))
                    else:
                        self.assertNotEqual(StrBoolResult.FALSE, to_bool(w_lower))
                    if w == w_upper:
                        self.assertEqual(StrBoolResult.FALSE, to_bool(w_upper))
                    else:
                        self.assertNotEqual(StrBoolResult.FALSE, to_bool(w_upper))

                self.assertNotEqual(StrBoolResult.TRUE, to_bool(w))
                self.assertNotEqual(StrBoolResult.UNKNOWN, to_bool(w))
                self.assertNotEqual(StrBoolResult.TRUE, to_bool(w_lower))
                self.assertNotEqual(StrBoolResult.UNKNOWN, to_bool(w_lower))
                self.assertNotEqual(StrBoolResult.TRUE, to_bool(w_upper))
                self.assertNotEqual(StrBoolResult.UNKNOWN, to_bool(w_upper))

    def test_unknown(self):
        unknown_words = ("A", "B", "C")

        for w in unknown_words:
            self.assertFalse(w in WORD_TRUE, f"`{w}` exists in `WORD_TRUE`")
            self.assertFalse(w in WORD_FALSE, f"`{w}` exists in `WORD_FALSE`")

            w_lower = w.lower()
            w_upper = w.upper()
            with self.subTest(w_lower=w_lower, w_upper=w_upper, w=w):
                if CASE_INSENSITIVE:
                    self.assertEqual(StrBoolResult.UNKNOWN, to_bool(w))
                    self.assertEqual(StrBoolResult.UNKNOWN, to_bool(w_lower))
                    self.assertEqual(StrBoolResult.UNKNOWN, to_bool(w_upper))
                else:
                    self.assertEqual(StrBoolResult.UNKNOWN, to_bool(w))
                    if w == w_lower:
                        self.assertEqual(StrBoolResult.UNKNOWN, to_bool(w_lower))
                    else:
                        self.assertNotEqual(StrBoolResult.UNKNOWN, to_bool(w_lower))
                    if w == w_upper:
                        self.assertEqual(StrBoolResult.UNKNOWN, to_bool(w_upper))
                    else:
                        self.assertNotEqual(StrBoolResult.UNKNOWN, to_bool(w_upper))

                self.assertNotEqual(StrBoolResult.TRUE, to_bool(w))
                self.assertNotEqual(StrBoolResult.FALSE, to_bool(w))
                self.assertNotEqual(StrBoolResult.TRUE, to_bool(w_lower))
                self.assertNotEqual(StrBoolResult.FALSE, to_bool(w_lower))
                self.assertNotEqual(StrBoolResult.TRUE, to_bool(w_upper))
                self.assertNotEqual(StrBoolResult.FALSE, to_bool(w_upper))

    def test_cast_non_str(self):
        self.assertEqual(StrBoolResult.UNKNOWN, to_bool(object()))

    def test_cast_bool(self):
        self.assertEqual(StrBoolResult.TRUE, to_bool(True))
        self.assertEqual(StrBoolResult.FALSE, to_bool(False))

    def test_str_bool_result(self):
        self.assertEqual(True, StrBoolResult.TRUE.to_bool())
        self.assertNotEqual(False, StrBoolResult.TRUE.to_bool())
        self.assertEqual(False, StrBoolResult.FALSE.to_bool())
        self.assertNotEqual(True, StrBoolResult.FALSE.to_bool())
        with self.assertRaises(ValueError):
            StrBoolResult.UNKNOWN.to_bool()
