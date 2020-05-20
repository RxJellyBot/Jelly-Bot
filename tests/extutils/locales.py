from extutils.dt import now_utc_aware
from extutils.locales import sec_diff_to_utc_offset, locales
from tests.base import TestCase


class TestLocaleFunctions(TestCase):
    def test_sec_diff_to_utc_offset(self):
        self.assertEqual("-0200", sec_diff_to_utc_offset(-7200))
        self.assertEqual("+0000", sec_diff_to_utc_offset(0))
        self.assertEqual("+0500", sec_diff_to_utc_offset(18000))
        self.assertEqual("+0800", sec_diff_to_utc_offset(28800))


class TestLocaleInfo(TestCase):
    def test_locale_info(self):
        """Only testing if the info can be acquired without any exceptions. Not testing the correctness."""
        for locale in locales:
            with self.subTest(locale=locale):
                self.assertIsNotNone(locale.current_utc_hr_offset)

                pytzinfo = locale.to_tzinfo()
                now = now_utc_aware()
                self.assertIsNotNone(pytzinfo)
                self.assertIsNotNone(pytzinfo.utcoffset(now))
                self.assertIsNotNone(pytzinfo.dst(now))
                self.assertIsNotNone(pytzinfo.tzname(now))
                self.assertEqual(locale.pytz_code, pytzinfo.tzidentifier)
