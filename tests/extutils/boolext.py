from extutils.boolext import StrBoolResult, to_bool, true_word, false_word, case_insensitive
from tests.base import TestCase


class TestBooleanExtension(TestCase):
    def test_true(self):
        for w in true_word:
            w_lower = w.lower()
            w_upper = w.upper()
            with self.subTest(w_lower=w_lower, w_upper=w_upper, w=w):
                if case_insensitive:
                    self.assertEqual(StrBoolResult.TRUE, to_bool(w))
                    self.assertEqual(StrBoolResult.TRUE, to_bool(w_lower))
                    self.assertEqual(StrBoolResult.TRUE, to_bool(w_upper))
                else:
                    self.assertEqual(StrBoolResult.TRUE, to_bool(w))
                    if w == w_lower:
                        self.assertEqual(StrBoolResult.TRUE, to_bool(w_lower))
                    else:
                        self.assertNotEquals(StrBoolResult.TRUE, to_bool(w_lower))
                    if w == w_upper:
                        self.assertEqual(StrBoolResult.TRUE, to_bool(w_upper))
                    else:
                        self.assertNotEquals(StrBoolResult.TRUE, to_bool(w_upper))

                self.assertNotEquals(StrBoolResult.FALSE, to_bool(w))
                self.assertNotEquals(StrBoolResult.UNKNOWN, to_bool(w))
                self.assertNotEquals(StrBoolResult.FALSE, to_bool(w_lower))
                self.assertNotEquals(StrBoolResult.UNKNOWN, to_bool(w_lower))
                self.assertNotEquals(StrBoolResult.FALSE, to_bool(w_upper))
                self.assertNotEquals(StrBoolResult.UNKNOWN, to_bool(w_upper))

    def test_false(self):
        for w in false_word:
            w_lower = w.lower()
            w_upper = w.upper()
            with self.subTest(w_lower=w_lower, w_upper=w_upper, w=w):
                if case_insensitive:
                    self.assertEqual(StrBoolResult.FALSE, to_bool(w))
                    self.assertEqual(StrBoolResult.FALSE, to_bool(w_lower))
                    self.assertEqual(StrBoolResult.FALSE, to_bool(w_upper))
                else:
                    self.assertEqual(StrBoolResult.FALSE, to_bool(w))
                    if w == w_lower:
                        self.assertEqual(StrBoolResult.FALSE, to_bool(w_lower))
                    else:
                        self.assertNotEquals(StrBoolResult.FALSE, to_bool(w_lower))
                    if w == w_upper:
                        self.assertEqual(StrBoolResult.FALSE, to_bool(w_upper))
                    else:
                        self.assertNotEquals(StrBoolResult.FALSE, to_bool(w_upper))

                self.assertNotEquals(StrBoolResult.TRUE, to_bool(w))
                self.assertNotEquals(StrBoolResult.UNKNOWN, to_bool(w))
                self.assertNotEquals(StrBoolResult.TRUE, to_bool(w_lower))
                self.assertNotEquals(StrBoolResult.UNKNOWN, to_bool(w_lower))
                self.assertNotEquals(StrBoolResult.TRUE, to_bool(w_upper))
                self.assertNotEquals(StrBoolResult.UNKNOWN, to_bool(w_upper))

    def test_unknown(self):
        unknown_words = ("A", "B", "C")

        for w in unknown_words:
            self.failIf(w in true_word, f"`{w}` exists in `true_word`")
            self.failIf(w in false_word, f"`{w}` exists in `false_word`")

            w_lower = w.lower()
            w_upper = w.upper()
            with self.subTest(w_lower=w_lower, w_upper=w_upper, w=w):
                if case_insensitive:
                    self.assertEqual(StrBoolResult.UNKNOWN, to_bool(w))
                    self.assertEqual(StrBoolResult.UNKNOWN, to_bool(w_lower))
                    self.assertEqual(StrBoolResult.UNKNOWN, to_bool(w_upper))
                else:
                    self.assertEqual(StrBoolResult.UNKNOWN, to_bool(w))
                    if w == w_lower:
                        self.assertEqual(StrBoolResult.UNKNOWN, to_bool(w_lower))
                    else:
                        self.assertNotEquals(StrBoolResult.UNKNOWN, to_bool(w_lower))
                    if w == w_upper:
                        self.assertEqual(StrBoolResult.UNKNOWN, to_bool(w_upper))
                    else:
                        self.assertNotEquals(StrBoolResult.UNKNOWN, to_bool(w_upper))

                self.assertNotEquals(StrBoolResult.TRUE, to_bool(w))
                self.assertNotEquals(StrBoolResult.FALSE, to_bool(w))
                self.assertNotEquals(StrBoolResult.TRUE, to_bool(w_lower))
                self.assertNotEquals(StrBoolResult.FALSE, to_bool(w_lower))
                self.assertNotEquals(StrBoolResult.TRUE, to_bool(w_upper))
                self.assertNotEquals(StrBoolResult.FALSE, to_bool(w_upper))

    def test_cast_non_str(self):
        self.assertEqual(StrBoolResult.UNKNOWN, to_bool(object()))

    def test_cast_bool(self):
        self.assertEqual(StrBoolResult.TRUE, to_bool(True))
        self.assertEqual(StrBoolResult.FALSE, to_bool(False))

    def test_str_bool_result(self):
        self.assertEqual(True, StrBoolResult.TRUE.to_bool())
        self.assertNotEquals(False, StrBoolResult.TRUE.to_bool())
        self.assertEqual(False, StrBoolResult.FALSE.to_bool())
        self.assertNotEquals(True, StrBoolResult.FALSE.to_bool())
        with self.assertRaises(ValueError):
            StrBoolResult.UNKNOWN.to_bool()
