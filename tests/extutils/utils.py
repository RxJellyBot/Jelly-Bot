from datetime import datetime, timedelta

from django.test import TestCase

from extutils.utils import (
    cast_keep_none, cast_iterable, safe_cast, all_lower,
    to_snake_case, to_camel_case, split_fill, str_reduce_length, list_insert_in_between, enumerate_ranking,
    dt_to_objectid
)


# noinspection PyTypeChecker
class TestFunctions(TestCase):
    def test_cast_keep_none(self):
        self.assertEquals(7, cast_keep_none("7", int))
        self.assertIsNone(cast_keep_none(None, int))
        self.assertIsNone(cast_keep_none(None, bool))
        self.assertEquals(True, cast_keep_none("1", bool))
        self.assertEquals(True, cast_keep_none(1, bool))
        self.assertEquals(False, cast_keep_none("0", bool))
        self.assertEquals(False, cast_keep_none(0, bool))

    def test_cast_iterable(self):
        self.assertListEqual(
            [1, 2, 3],
            cast_iterable(["1", "2", "3"], int))
        self.assertListEqual(
            [1, 2, 3],
            cast_iterable(("1", "2", "3"), int))
        self.assertListEqual(
            [1, 2, 3, 1, 7],
            cast_iterable(["1", "2", "3", True, 7], int))
        self.assertListEqual(
            [1, 2, [1, 2, [1, 2]]],
            cast_iterable(["1", "2", ["1", "2", ["1", "2"]]], int))
        self.assertEquals(7, cast_iterable("7", int))

    def test_safe_cast(self):
        self.assertIsNone(safe_cast(None, int))
        self.assertIsNone(safe_cast(7, list))
        self.assertEquals(7, safe_cast(7, int))
        self.assertEquals("7", safe_cast(7, str))
        self.assertListEqual([1, 2], safe_cast((1, 2), list))

    def test_all_lower(self):
        s1 = "LOWER"
        s2 = ["LOWER"]
        s3 = ("LOWER",)
        s4 = {"LOWER"}
        s5 = {"A": "LOWER"}
        s6 = {"A": ("A", "97"), "B": {"B"}}

        self.assertEquals("lower", all_lower(s1))
        self.assertEquals("LOWER", s1)

        self.assertListEqual(["lower"], all_lower(s2))
        self.assertEquals(["LOWER"], s2)

        self.assertTupleEqual(("lower",), all_lower(s3))
        self.assertEquals(("LOWER",), s3)

        self.assertSetEqual({"lower"}, all_lower(s4))
        self.assertEquals({"LOWER"}, s4)

        self.assertDictEqual({"A": "lower"}, all_lower(s5))
        self.assertEquals({"A": "LOWER"}, s5)

        self.assertDictEqual({"A": ("a", "97"), "B": {"b"}}, all_lower(s6))
        self.assertEquals({"A": ("A", "97"), "B": {"B"}}, s6)

        self.assertEquals(77, all_lower(77))

    def test_to_snake_case(self):
        eq_pairs = [
            ("angel_dust", to_snake_case("AngelDust")),
            ("angel_dust", to_snake_case("angelDust")),
            ("besafe", to_snake_case("besafe")),
            ("besafe", to_snake_case("Besafe")),
            ("be_safe", to_snake_case("Be_safe")),
            ("raenonx_jellycat", to_snake_case("raenonx_jellycat")),
            ("a", to_snake_case("A")),
            ("a", to_snake_case("a")),
            ("", to_snake_case(""))
        ]
        for expected, actual in eq_pairs:
            with self.subTest(expected=expected, actual=actual):
                self.assertEquals(expected, actual)

    def test_to_camel_case(self):
        eq_pairs = [
            ("AngelDust", to_camel_case("angel_dust")),
            ("Besafe", to_camel_case("besafe")),
            ("BeSafe", to_camel_case("be_safe")),
            ("RaenonxJellycat", to_camel_case("raenonx_jellycat")),
            ("", to_camel_case("_")),
            ("A", to_camel_case("a_")),
            ("A", to_camel_case("a")),
            ("", to_camel_case(""))
        ]
        for expected, actual in eq_pairs:
            with self.subTest(expected=expected, actual=actual):
                self.assertEquals(expected, actual)

    def test_split_fill(self):
        eq_pairs = [
            (["A", "B", "C", "D", "D"], split_fill("A,B,C", 5, delim=",", fill="D")),
            (["A", "B", "C"], split_fill("A,B,C", 3, delim=",", fill="D")),
            (["A", "B"], split_fill("A,B,C", 2, delim=",", fill="D")),
            (["D", "D"], split_fill("", 2, delim=",", fill="D")),
            (["ABC", "D"], split_fill("ABC", 2, delim=",", fill="D")),
            (["AB", "C", ""], split_fill("AB,C", 3, delim=",", fill="")),
            (["AB", "C", None], split_fill("AB,C", 3, delim=",", fill=None))
        ]
        for expected, actual in eq_pairs:
            with self.subTest(expected=expected, actual=actual):
                self.assertListEqual(expected, actual)

    def test_str_reduce_length(self):
        eq_pairs = [
            ("12...", str_reduce_length("1234567890", 5)),
            ("1234...", str_reduce_length("1234567890", 7)),
            ("12345...", str_reduce_length("1234567890", 8)),
            ("123456...", str_reduce_length("1234567890", 9)),
            ("1234567890", str_reduce_length("1234567890", 10)),
            ("1234567890", str_reduce_length("1234567890", 11)),
            ("12345///", str_reduce_length("1234567890", 8, suffix="///")),
            ("~~~~~~~", str_reduce_length("1234567890", 7, suffix="~~~~~~~")),
            ("&lt;&gt;", str_reduce_length("<>", 10, escape_html=True)),
            ("&lt;&gt;", str_reduce_length("<>", 5, escape_html=True)),
            ("&lt;&gt;...", str_reduce_length("<><><>", 5, escape_html=True)),
            ("&lt;&gt;&amp;&amp;&amp;", str_reduce_length("<><><>", 5, escape_html=True, suffix="&&&")),
        ]
        for expected, actual in eq_pairs:
            with self.subTest(expected=expected, actual=actual):
                self.assertEquals(expected, actual)

        with self.assertRaises(ValueError):
            str_reduce_length("333", 5, suffix="12345678")

    def test_list_insert_in_between(self):
        eq_pairs = [
            (["A", "-", "B"], list_insert_in_between(["A", "B"], "-")),
            (["A", True, "B", True, "C"], list_insert_in_between(["A", "B", "C"], True)),
            (["A"], list_insert_in_between(["A"], "-")),
            ([], list_insert_in_between([], "-"))
        ]
        for expected, actual in eq_pairs:
            with self.subTest(expected=expected, actual=actual):
                self.assertListEqual(expected, actual)

    def test_enum_ranking_tie_fn(self):
        data = [1, 2, 3, 4, 5]
        self.assertListEqual(
            [("T1", 1), ("T1", 2), ("T1", 3), ("T1", 4), ("T1", 5)],
            list(enumerate_ranking(data, is_tie=lambda cur, prv: True)))

    def test_enum_ranking_no_tied(self):
        data = [1, 2, 3, 4, 5]
        self.assertListEqual(
            [("1", 1), ("2", 2), ("3", 3), ("4", 4), ("5", 5)],
            list(enumerate_ranking(data)))
        self.assertListEqual(
            [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)],
            list(enumerate_ranking(data, t_prefix=False)))
        self.assertListEqual(
            [("0", 1), ("1", 2), ("2", 3), ("3", 4), ("4", 5)],
            list(enumerate_ranking(data, start=0)))
        self.assertListEqual(
            [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],
            list(enumerate_ranking(data, t_prefix=False, start=0)))

    def test_enum_ranking_in_between_tied(self):
        data = [1, 2, 3, 3, 5]
        self.assertListEqual(
            [("1", 1), ("2", 2), ("T3", 3), ("T3", 3), ("5", 5)],
            list(enumerate_ranking(data)))
        self.assertListEqual(
            [(1, 1), (2, 2), (3, 3), (3, 3), (5, 5)],
            list(enumerate_ranking(data, t_prefix=False)))
        self.assertListEqual(
            [("0", 1), ("1", 2), ("T2", 3), ("T2", 3), ("4", 5)],
            list(enumerate_ranking(data, start=0)))
        self.assertListEqual(
            [(0, 1), (1, 2), (2, 3), (2, 3), (4, 5)],
            list(enumerate_ranking(data, t_prefix=False, start=0)))

    def test_enum_ranking_end_tied(self):
        data = [1, 3, 5, 5, 5]
        self.assertListEqual(
            [("1", 1), ("2", 3), ("T3", 5), ("T3", 5), ("T3", 5)],
            list(enumerate_ranking(data)))
        self.assertListEqual(
            [(1, 1), (2, 3), (3, 5), (3, 5), (3, 5)],
            list(enumerate_ranking(data, t_prefix=False)))
        self.assertListEqual(
            [("0", 1), ("1", 3), ("T2", 5), ("T2", 5), ("T2", 5)],
            list(enumerate_ranking(data, start=0)))
        self.assertListEqual(
            [(0, 1), (1, 3), (2, 5), (2, 5), (2, 5)],
            list(enumerate_ranking(data, t_prefix=False, start=0)))

    def test_enum_ranking_beginning_tied(self):
        data = [1, 1, 1, 3, 5]
        self.assertListEqual(
            [("T1", 1), ("T1", 1), ("T1", 1), ("4", 3), ("5", 5)],
            list(enumerate_ranking(data)))
        self.assertListEqual(
            [(1, 1), (1, 1), (1, 1), (4, 3), (5, 5)],
            list(enumerate_ranking(data, t_prefix=False)))
        self.assertListEqual(
            [("T0", 1), ("T0", 1), ("T0", 1), ("3", 3), ("4", 5)],
            list(enumerate_ranking(data, start=0)))
        self.assertListEqual(
            [(0, 1), (0, 1), (0, 1), (3, 3), (4, 5)],
            list(enumerate_ranking(data, t_prefix=False, start=0)))

    def test_enum_ranking_both_side_tied(self):
        data = [1, 1, 3, 5, 5]
        self.assertListEqual(
            [("T1", 1), ("T1", 1), ("3", 3), ("T4", 5), ("T4", 5)],
            list(enumerate_ranking(data)))
        self.assertListEqual(
            [(1, 1), (1, 1), (3, 3), (4, 5), (4, 5)],
            list(enumerate_ranking(data, t_prefix=False)))
        self.assertListEqual(
            [("T0", 1), ("T0", 1), ("2", 3), ("T3", 5), ("T3", 5)],
            list(enumerate_ranking(data, start=0)))
        self.assertListEqual(
            [(0, 1), (0, 1), (2, 3), (3, 5), (3, 5)],
            list(enumerate_ranking(data, t_prefix=False, start=0)))

    def test_dt_to_objectid(self):
        low_bound = datetime(1970, 1, 1)
        high_bound = datetime(2106, 2, 7)

        self.assertIsNotNone(dt_to_objectid(low_bound))
        self.assertIsNotNone(dt_to_objectid(high_bound))
        self.assertIsNone(dt_to_objectid(None))
        self.assertIsNone(dt_to_objectid(1))
        self.assertIsNone(dt_to_objectid("7"))
        self.assertIsNone(dt_to_objectid([8]))
        self.assertIsNone(dt_to_objectid(low_bound - timedelta(days=5)))
        self.assertIsNone(dt_to_objectid(high_bound + timedelta(days=5)))
