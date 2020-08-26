from datetime import timedelta

from extutils.dt import t_delta_str

from tests.base import TestCase, locale_en, locale_cht

__all__ = ("TestFunctions",)


class TestFunctions(TestCase):
    @locale_en
    def test_t_delta_lt_3_days_en(self):
        self.assertEqual(t_delta_str(timedelta(days=2, hours=5, minutes=6, seconds=7)), "53 H 06 M 07 S")

    @locale_en
    def test_t_delta_eq_3_days_en(self):
        self.assertEqual(t_delta_str(timedelta(days=3)), "72 H 00 M 00 S")

    @locale_en
    def test_t_delta_gt_3_days_en(self):
        self.assertEqual(t_delta_str(timedelta(days=4, hours=1, minutes=2, seconds=3)), "4 Days 1 H 02 M 03 S")

    @locale_cht
    def test_t_delta_lt_3_days_cht(self):
        self.assertEqual(t_delta_str(timedelta(days=2, hours=5, minutes=6, seconds=7)), "53 時 06 分 07 秒")

    @locale_cht
    def test_t_delta_eq_3_days_cht(self):
        self.assertEqual(t_delta_str(timedelta(days=3)), "72 時 00 分 00 秒")

    @locale_cht
    def test_t_delta_gt_3_days_cht(self):
        self.assertEqual(t_delta_str(timedelta(days=4, hours=1, minutes=2, seconds=3)), "4 日 1 時 02 分 03 秒")
