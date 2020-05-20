import math
from datetime import datetime, timezone, timedelta, time

import pytz

from extutils.dt import (
    is_tz_naive, now_utc_aware, localtime, parse_to_dt, time_to_seconds,
    TimeRange, TimeRangeEndBeforeStart, make_tz_aware
)
from tests.base import TestCase


class TestDatetime(TestCase):
    def test_dt_make_aware(self):
        self.assertFalse(is_tz_naive(make_tz_aware(datetime.now())))
        self.assertFalse(is_tz_naive(make_tz_aware(datetime.utcnow())))
        self.assertFalse(is_tz_naive(make_tz_aware(localtime().replace(tzinfo=None))))
        self.assertFalse(is_tz_naive(make_tz_aware(now_utc_aware())))
        self.assertFalse(is_tz_naive(make_tz_aware(datetime(2020, 5, 7))))
        self.assertFalse(is_tz_naive(make_tz_aware(datetime.min)))
        self.assertFalse(is_tz_naive(make_tz_aware(datetime.min.replace(tzinfo=timezone.utc))))
        self.assertFalse(is_tz_naive(make_tz_aware(datetime.max)))
        self.assertFalse(is_tz_naive(make_tz_aware(datetime.max.replace(tzinfo=timezone.utc))))

    def test_dt_naive(self):
        self.assertTrue(is_tz_naive(datetime.now()))
        self.assertTrue(is_tz_naive(datetime.utcnow()))
        self.assertTrue(is_tz_naive(localtime().replace(tzinfo=None)))
        self.assertFalse(is_tz_naive(now_utc_aware()))
        self.assertTrue(is_tz_naive(datetime(2020, 5, 7)))
        self.assertTrue(is_tz_naive(datetime.min))
        self.assertFalse(is_tz_naive(datetime.min.replace(tzinfo=timezone.utc)))
        self.assertTrue(is_tz_naive(datetime.max))
        self.assertFalse(is_tz_naive(datetime.max.replace(tzinfo=timezone.utc)))

    def test_parse_to_dt(self):
        dt_parsed = parse_to_dt("2020-04-04 16:00")
        dt_expected = datetime(2020, 4, 4, 16, 0, 0, 0, tzinfo=pytz.UTC)
        self.assertFalse(is_tz_naive(dt_parsed))
        self.assertEqual(dt_expected, dt_parsed)
        self.assertEqual(dt_expected.tzinfo, dt_parsed.tzinfo)
        self.assertEqual(pytz.UTC, dt_parsed.tzinfo)

        dt_parsed = parse_to_dt("2020-04-04 16:00+0200")
        tz_expected = timezone(timedelta(hours=2))
        dt_expected = datetime(2020, 4, 4, 16, 0, 0, 0, tzinfo=tz_expected)

        self.assertFalse(is_tz_naive(dt_parsed))
        self.assertEqual(dt_expected, dt_parsed)
        self.assertEqual(dt_expected.tzinfo.utcoffset(datetime.now()), dt_parsed.tzinfo.utcoffset(datetime.now()))
        self.assertEqual(tz_expected.utcoffset(datetime.now()), dt_parsed.tzinfo.utcoffset(datetime.now()))

        dt_parsed = parse_to_dt("ABCD")
        self.assertIsNone(dt_parsed)

    def test_time_to_seconds(self):
        t = time(0, 0, 10, 120)
        self.assertEqual(10.000120, time_to_seconds(t))
        t = time(0, 10, 10, 120)
        self.assertEqual(610.000120, time_to_seconds(t))
        t = time(10, 10, 10, 120)
        self.assertEqual(36610.000120, time_to_seconds(t))


# noinspection PyTypeChecker
class TestParseTimeRange(TestCase):
    def test_nfill_all_none(self):
        tr = TimeRange(end_autofill_now=True)
        now = now_utc_aware()
        self.assertIsNone(tr.start)
        self.assertIsNone(tr.start_org)
        self.assertAlmostEquals(0, abs((tr.end - now).total_seconds()), 0)
        self.assertIsNone(tr.tzinfo_)
        self.assertFalse(tr.expandable)
        self.assertFalse(tr.expanded)
        self.assertTrue(tr.is_inf)
        self.assertEqual(math.inf, tr.hr_length_org)
        self.assertEqual(math.inf, tr.hr_length)
        self.assertEqual(f"- ~ {now.strftime('%m-%d')}", tr.expr_period_short)
        self.assertAlmostEquals(tr.end_time_seconds, time_to_seconds(now), 0)
        prd = tr.get_periods()
        self.assertListEqual([tr], prd)

    def test_fill_all_none(self):
        tr = TimeRange()
        now = now_utc_aware()
        self.assertIsNone(tr.start)
        self.assertIsNone(tr.start_org)
        self.assertAlmostEquals(0, abs((tr.end - now).total_seconds()), 0)
        self.assertIsNone(tr.tzinfo_)
        self.assertFalse(tr.expandable)
        self.assertFalse(tr.expanded)
        self.assertTrue(tr.is_inf)
        self.assertEqual(math.inf, tr.hr_length_org)
        self.assertEqual(math.inf, tr.hr_length)
        self.assertEqual(f"- ~ {now.strftime('%m-%d')}", tr.expr_period_short)
        self.assertAlmostEquals(tr.end_time_seconds, time_to_seconds(now), 0)
        prd = tr.get_periods()
        self.assertListEqual([tr], prd)

    def test_nfill_range_only(self):
        tr = TimeRange(range_hr=120, end_autofill_now=False)
        now = now_utc_aware()
        expected_start = now - timedelta(hours=120)
        self.assertAlmostEquals(0, abs((expected_start - tr.start).total_seconds()), 0)
        self.assertAlmostEquals(0, abs((expected_start - tr.start_org).total_seconds()), 0)
        self.assertIsNone(tr.end)
        self.assertIsNone(tr.tzinfo_)
        self.assertFalse(tr.expandable)
        self.assertFalse(tr.expanded)
        self.assertTrue(tr.is_inf)
        self.assertAlmostEquals(120, tr.hr_length_org, 0)
        self.assertAlmostEquals(120, tr.hr_length, 0)
        self.assertEqual(f"{expected_start.strftime('%m-%d')} ~ -", tr.expr_period_short)
        self.assertAlmostEquals(tr.end_time_seconds, time_to_seconds(now), 0)
        prd = tr.get_periods()
        self.assertListEqual([tr], prd)

    def test_fill_range_only(self):
        tr = TimeRange(range_hr=120)
        now = now_utc_aware()
        expected_start = now - timedelta(hours=120)
        self.assertAlmostEquals(0, abs((expected_start - tr.start).total_seconds()), 0)
        self.assertAlmostEquals(0, abs((expected_start - tr.start_org).total_seconds()), 0)
        self.assertAlmostEquals(0, abs((tr.end - now).total_seconds()), 0)
        self.assertIsNone(tr.tzinfo_)
        self.assertTrue(tr.expandable)
        self.assertFalse(tr.expanded)
        self.assertFalse(tr.is_inf)
        self.assertAlmostEquals(120, tr.hr_length_org, 0)
        self.assertAlmostEquals(120, tr.hr_length, 0)
        self.assertEqual(f"{expected_start.strftime('%m-%d')} ~ {now.strftime('%m-%d')}", tr.expr_period_short)
        self.assertAlmostEquals(tr.end_time_seconds, time_to_seconds(now), 0)
        prd = tr.get_periods()
        self.assertListEqual([tr], prd)

    def test_fill_range_hr_0(self):
        tr = TimeRange(range_hr=0)
        now = now_utc_aware()
        expected_start_end = now
        self.assertAlmostEquals(0, abs((expected_start_end - tr.start).total_seconds()), 0)
        self.assertAlmostEquals(0, abs((expected_start_end - tr.start_org).total_seconds()), 0)
        self.assertAlmostEquals(0, abs((tr.end - now).total_seconds()), 0)
        self.assertIsNone(tr.tzinfo_)
        self.assertTrue(tr.expandable)
        self.assertFalse(tr.expanded)
        self.assertFalse(tr.is_inf)
        self.assertAlmostEquals(0, tr.hr_length_org, 0)
        self.assertAlmostEquals(0, tr.hr_length, 0)
        self.assertEqual(f"{expected_start_end.strftime('%m-%d')} ~ {now.strftime('%m-%d')}", tr.expr_period_short)
        self.assertAlmostEquals(tr.end_time_seconds, time_to_seconds(now), 0)
        prd = tr.get_periods()
        self.assertListEqual([tr], prd)

    def test_nfill_start(self):
        start_dt = datetime(2020, 4, 4, 1, 1, 1, tzinfo=pytz.UTC)

        tr = TimeRange(start=start_dt, end_autofill_now=False)
        now = now_utc_aware()
        hr_diff = (now - start_dt).total_seconds() / 3600
        self.assertAlmostEquals(0, abs((start_dt - tr.start).total_seconds()), 0)
        self.assertAlmostEquals(0, abs((start_dt - tr.start_org).total_seconds()), 0)
        self.assertIsNone(tr.end)
        self.assertIsNone(tr.tzinfo_)
        self.assertFalse(tr.expandable)
        self.assertFalse(tr.expanded)
        self.assertTrue(tr.is_inf)
        self.assertAlmostEquals(hr_diff, tr.hr_length_org, 0)
        self.assertAlmostEquals(hr_diff, tr.hr_length, 0)
        self.assertEqual(f"{start_dt.strftime('%m-%d')} ~ -", tr.expr_period_short)
        self.assertAlmostEquals(tr.end_time_seconds, time_to_seconds(now), 0)
        prd = tr.get_periods()
        self.assertListEqual([tr], prd)

    def test_fill_start(self):
        start_dt = datetime(2020, 4, 4, 1, 1, 1, tzinfo=pytz.UTC)

        tr = TimeRange(start=start_dt, end_autofill_now=True)
        now = now_utc_aware()
        hr_diff = (now - tr.start).total_seconds() / 3600
        self.assertAlmostEquals(0, abs((start_dt - tr.start).total_seconds()), 0)
        self.assertAlmostEquals(0, abs((start_dt - tr.start_org).total_seconds()), 0)
        self.assertAlmostEquals(0, abs((tr.end - now).total_seconds()), 0)
        self.assertIsNone(tr.tzinfo_)
        self.assertTrue(tr.expandable)
        self.assertFalse(tr.expanded)
        self.assertFalse(tr.is_inf)
        self.assertAlmostEquals(hr_diff, tr.hr_length_org, 0)
        self.assertAlmostEquals(hr_diff, tr.hr_length, 0)
        self.assertEqual(f"{start_dt.strftime('%m-%d')} ~ {now.strftime('%m-%d')}", tr.expr_period_short)
        self.assertAlmostEquals(tr.end_time_seconds, time_to_seconds(now), 0)
        prd = tr.get_periods()
        self.assertListEqual([tr], prd)

    def test_end(self):
        end_dt = datetime(2020, 4, 4, 1, 1, 1, tzinfo=pytz.UTC)
        tr = TimeRange(end=end_dt)
        self.assertIsNone(tr.start)
        self.assertIsNone(tr.start_org)
        self.assertAlmostEquals(0, abs((tr.end - end_dt).total_seconds()), 0)
        self.assertIsNone(tr.tzinfo_)
        self.assertFalse(tr.expandable)
        self.assertFalse(tr.expanded)
        self.assertTrue(tr.is_inf)
        self.assertEqual(math.inf, tr.hr_length_org)
        self.assertEqual(math.inf, tr.hr_length)
        self.assertEqual(f"- ~ {end_dt.strftime('%m-%d')}", tr.expr_period_short)
        self.assertAlmostEquals(tr.end_time_seconds, time_to_seconds(end_dt.time()), 0)
        prd = tr.get_periods()
        self.assertListEqual([tr], prd)

    def test_start_hr_range(self):
        start_dt = datetime(2020, 4, 4, 1, 1, 1, tzinfo=pytz.UTC)
        end_dt_expected = start_dt + timedelta(hours=120)
        tr = TimeRange(start=start_dt, range_hr=120)
        self.assertAlmostEquals(0, abs((start_dt - tr.start).total_seconds()), 0)
        self.assertAlmostEquals(0, abs((start_dt - tr.start_org).total_seconds()), 0)
        self.assertAlmostEquals(0, abs((tr.end - end_dt_expected).total_seconds()), 0)
        self.assertIsNone(tr.tzinfo_)
        self.assertTrue(tr.expandable)
        self.assertFalse(tr.expanded)
        self.assertFalse(tr.is_inf)
        self.assertAlmostEquals(120, tr.hr_length_org, 0)
        self.assertAlmostEquals(120, tr.hr_length, 0)
        self.assertEqual(f"{start_dt.strftime('%m-%d')} ~ {end_dt_expected.strftime('%m-%d')}", tr.expr_period_short)
        self.assertAlmostEquals(tr.end_time_seconds, time_to_seconds(end_dt_expected.time()), 0)
        prd = tr.get_periods()
        self.assertListEqual([tr], prd)

    def test_end_hr_range(self):
        end_dt = datetime(2020, 4, 4, 1, 1, 1, tzinfo=pytz.UTC)
        start_dt_expected = end_dt - timedelta(hours=120)
        tr = TimeRange(end=end_dt, range_hr=120)
        self.assertAlmostEquals(0, abs((start_dt_expected - tr.start).total_seconds()), 0)
        self.assertAlmostEquals(0, abs((start_dt_expected - tr.start_org).total_seconds()), 0)
        self.assertAlmostEquals(0, abs((tr.end - end_dt).total_seconds()), 0)
        self.assertIsNone(tr.tzinfo_)
        self.assertTrue(tr.expandable)
        self.assertFalse(tr.expanded)
        self.assertFalse(tr.is_inf)
        self.assertAlmostEquals(120, tr.hr_length_org, 0)
        self.assertAlmostEquals(120, tr.hr_length, 0)
        self.assertEqual(f"{start_dt_expected.strftime('%m-%d')} ~ {end_dt.strftime('%m-%d')}", tr.expr_period_short)
        self.assertAlmostEquals(tr.end_time_seconds, time_to_seconds(end_dt.time()), 0)
        prd = tr.get_periods()
        self.assertListEqual([tr], prd)

    def test_start_end(self):
        start_dt = datetime(2020, 4, 2, 1, 1, 1, tzinfo=pytz.UTC)
        end_dt = datetime(2020, 4, 4, 1, 1, 1, tzinfo=pytz.UTC)
        tr = TimeRange(start=start_dt, end=end_dt)
        self.assertAlmostEquals(0, abs((start_dt - tr.start).total_seconds()), 0)
        self.assertAlmostEquals(0, abs((start_dt - tr.start_org).total_seconds()), 0)
        self.assertAlmostEquals(0, abs((tr.end - end_dt).total_seconds()), 0)
        self.assertIsNone(tr.tzinfo_)
        self.assertTrue(tr.expandable)
        self.assertFalse(tr.expanded)
        self.assertFalse(tr.is_inf)
        self.assertAlmostEquals(48, tr.hr_length_org, 0)
        self.assertAlmostEquals(48, tr.hr_length, 0)
        self.assertEqual(f"{start_dt.strftime('%m-%d')} ~ {end_dt.strftime('%m-%d')}", tr.expr_period_short)
        self.assertAlmostEquals(tr.end_time_seconds, time_to_seconds(end_dt.time()), 0)
        prd = tr.get_periods()
        self.assertListEqual([tr], prd)

    def test_mult(self):
        start_mult_expected = datetime(2020, 4, 12, 1, 1, 1, tzinfo=pytz.UTC)
        start_dt = datetime(2020, 4, 14, 1, 1, 1, tzinfo=pytz.UTC)
        end_dt = datetime(2020, 4, 16, 1, 1, 1, tzinfo=pytz.UTC)
        tr = TimeRange(start=start_dt, end=end_dt, range_mult=2)
        self.assertAlmostEquals(0, abs((start_mult_expected - tr.start).total_seconds()), 0)
        self.assertAlmostEquals(0, abs((start_dt - tr.start_org).total_seconds()), 0)
        self.assertAlmostEquals(0, abs((tr.end - end_dt).total_seconds()), 0)
        self.assertIsNone(tr.tzinfo_)
        self.assertTrue(tr.expandable)
        self.assertTrue(tr.expanded)
        self.assertFalse(tr.is_inf)
        self.assertAlmostEquals(48, tr.hr_length_org, 0)
        self.assertAlmostEquals(96, tr.hr_length, 0)
        self.assertEqual(f"{start_mult_expected.strftime('%m-%d')} ~ {end_dt.strftime('%m-%d')}",
                         tr.expr_period_short)
        self.assertAlmostEquals(tr.end_time_seconds, time_to_seconds(end_dt.time()), 0)
        prd = tr.get_periods()
        tr2 = TimeRange(start=start_mult_expected, end=start_dt)
        tr3 = TimeRange(start=start_dt, end=end_dt)
        self.assertListEqual([tr2, tr3], prd)

    def test_tzinfo(self):
        start_dt = datetime(2020, 2, 14, 12, 1, 1, tzinfo=pytz.UTC)
        end_dt = datetime(2020, 2, 16, 12, 1, 1, tzinfo=pytz.UTC)
        tz = pytz.timezone("America/New_York")
        tr = TimeRange(start=start_dt, end=end_dt, tzinfo_=tz)
        self.assertAlmostEquals(0, abs((start_dt - tr.start).total_seconds()), 0)
        self.assertAlmostEquals(0, abs((start_dt - tr.start_org).total_seconds()), 0)
        self.assertAlmostEquals(0, abs((tr.end - end_dt).total_seconds()), 0)
        self.assertEqual(tz.utcoffset(datetime.now()), tr.tzinfo_.utcoffset(datetime.now()))
        self.assertTrue(tr.expandable)
        self.assertFalse(tr.expanded)
        self.assertFalse(tr.is_inf)
        self.assertAlmostEquals(48, tr.hr_length_org, 0)
        self.assertAlmostEquals(48, tr.hr_length, 0)
        self.assertEqual(f"{start_dt.strftime('%m-%d')} ~ {end_dt.strftime('%m-%d')}", tr.expr_period_short)
        self.assertAlmostEquals(tr.end_time_seconds, time_to_seconds(localtime(end_dt, tz).time()), 0)
        prd = tr.get_periods()
        self.assertListEqual([tr], prd)

    def test_set_day_offset_pos(self):
        start_dt = datetime(2020, 2, 14, 1, 1, 1, tzinfo=pytz.UTC)

        tr = TimeRange(start=start_dt)
        self.assertEqual(start_dt, tr.start)
        self.assertEqual(start_dt, tr.start_org)
        tr.set_start_day_offset(5)
        self.assertEqual(start_dt, tr.start_org)
        self.assertEqual(start_dt + timedelta(days=5), tr.start)

    def test_set_day_offset_neg(self):
        start_dt = datetime(2020, 2, 14, 1, 1, 1, tzinfo=pytz.UTC)

        tr = TimeRange(start=start_dt)
        self.assertEqual(start_dt, tr.start)
        self.assertEqual(start_dt, tr.start_org)
        tr.set_start_day_offset(-5)
        self.assertEqual(start_dt, tr.start_org)
        self.assertEqual(start_dt - timedelta(days=5), tr.start)

    def test_set_day_tz_naive(self):
        start_dt = datetime(2020, 2, 14, 1, 1, 1)
        end_dt = datetime(2020, 2, 17, 1, 1, 1)

        tr = TimeRange(start=start_dt, end=end_dt, tzinfo_=pytz.UTC)
        self.assertFalse(is_tz_naive(tr.start))
        self.assertEqual(pytz.UTC.localize(start_dt), tr.start)
        self.assertFalse(is_tz_naive(tr.end))
        self.assertEqual(pytz.UTC.localize(end_dt), tr.end)

    def test_set_day_offset_none(self):
        tr = TimeRange()
        self.assertIsNone(tr.start)
        self.assertIsNone(tr.start_org)
        tr.set_start_day_offset(5)
        self.assertIsNone(tr.start)
        self.assertIsNone(tr.start_org)

    def test_malformed(self):
        start_dt = datetime(2020, 4, 16, 1, 1, 1, tzinfo=pytz.UTC)
        end_dt = datetime(2020, 4, 14, 1, 1, 1, tzinfo=pytz.UTC)
        with self.assertRaises(TimeRangeEndBeforeStart):
            TimeRange(start=start_dt, end=end_dt)
