from strres.extutils import DateTime
from tests.base import TestCase, locale_en, locale_cht

__all__ = ("TestDateTime",)


class TestDateTime(TestCase):
    @locale_en
    def test_get_time_expr_lt_3_days_en(self):
        self.assertEqual(DateTime.get_time_expr(5, 6, 7, 2), "53 H 06 M 07 S")

    @locale_en
    def test_get_time_expr_eq_3_days_en(self):
        self.assertEqual(DateTime.get_time_expr(0, 0, 0, 3), "72 H 00 M 00 S")

    @locale_en
    def test_get_time_expr_gt_3_days_en(self):
        self.assertEqual(DateTime.get_time_expr(1, 2, 3, 4), "4 Days 1 H 02 M 03 S")

    @locale_cht
    def test_get_time_expr_lt_3_days_cht(self):
        self.assertEqual(DateTime.get_time_expr(5, 6, 7, 2), "53 時 06 分 07 秒")

    @locale_cht
    def test_get_time_expr_eq_3_days_cht(self):
        self.assertEqual(DateTime.get_time_expr(0, 0, 0, 3), "72 時 00 分 00 秒")

    @locale_cht
    def test_get_time_expr_gt_3_days_cht(self):
        self.assertEqual(DateTime.get_time_expr(1, 2, 3, 4), "4 日 1 時 02 分 03 秒")
