from datetime import datetime, timezone, date, timedelta

from bson import ObjectId
from pymongo.collection import Collection

from extutils.dt import TimeRange
from tests.base import TestDatabaseMixin
from models import HourlyResult, DailyResult

__all__ = ["TestDailyResult", "TestHourlyResult"]


class TestHourlyResult(TestDatabaseMixin):
    class TestSample1(HourlyResult):
        pass

    def test_no_days_collected(self):
        result = TestHourlyResult.TestSample1(0)

        data = (
            (self.assertFalse, (result.avg_calculatable,)),
            (self.assertEqual, (result.denom, []))
        )

        for method, args in data:
            with self.subTest(method=method, args=args):
                method(*args)

    def test_has_days_collected(self):
        expected_denoms = {
            0: [6] * 1 + [5] * 11 + [6] * 12,
            1: [6] * 2 + [5] * 11 + [6] * 11,
            2: [6] * 3 + [5] * 11 + [6] * 10,
            3: [6] * 4 + [5] * 11 + [6] * 9,
            4: [6] * 5 + [5] * 11 + [6] * 8,
            5: [6] * 6 + [5] * 11 + [6] * 7,
            6: [6] * 7 + [5] * 11 + [6] * 6,
            7: [6] * 8 + [5] * 11 + [6] * 5,
            8: [6] * 9 + [5] * 11 + [6] * 4,
            9: [6] * 10 + [5] * 11 + [6] * 3,
            10: [6] * 11 + [5] * 11 + [6] * 2,
            11: [6] * 12 + [5] * 11 + [6] * 1,
            12: [6] * 13 + [5] * 11,
            13: [5] * 1 + [6] * 13 + [5] * 10,
            14: [5] * 2 + [6] * 13 + [5] * 9,
            15: [5] * 3 + [6] * 13 + [5] * 8,
            16: [5] * 4 + [6] * 13 + [5] * 7,
            17: [5] * 5 + [6] * 13 + [5] * 6,
            18: [5] * 6 + [6] * 13 + [5] * 5,
            19: [5] * 7 + [6] * 13 + [5] * 4,
            20: [5] * 8 + [6] * 13 + [5] * 3,
            21: [5] * 9 + [6] * 13 + [5] * 2,
            22: [5] * 10 + [6] * 13 + [5] * 1,
            23: [5] * 11 + [6] * 13
        }

        for hr in range(24):
            result = TestHourlyResult.TestSample1(5.5, end_time=datetime(2020, 5, 7, hr))

            data = (
                (self.assertTrue, (result.avg_calculatable,)),
                (self.assertEqual, (result.denom, expected_denoms[hr]))  # Incorrect
            )

            for method, args in data:
                with self.subTest(hr=hr, method=method.__name__, args=args):
                    method(*args)

        now = datetime.utcnow()
        result = TestHourlyResult.TestSample1(5.5)

        data = (
            (self.assertTrue, (result.avg_calculatable,)),
            (self.assertEqual, (result.denom, expected_denoms[now.hour]))  # Incorrect
        )

        for method, args in data:
            with self.subTest(hr=now.hour, method=method.__name__, args=args):
                method(*args)

    def prepare_data(self) -> Collection:
        col = self.get_mongo_client().get_database(self.get_db_name()).get_collection("testcol")

        col.insert_one({"_id": ObjectId.from_datetime(datetime(2020, 5, 1))})

        return col

    def test_data_days_collected_has_data(self):
        col = self.prepare_data()

        days_past_from_oldest = (datetime.utcnow() - datetime(2020, 5, 1)).total_seconds() / 86400

        data = (
            (30, {"end": datetime(2020, 5, 31)}),
            (30, {"end": datetime(2020, 5, 31).replace(tzinfo=timezone.utc)}),
            (HourlyResult.DAYS_NONE, {"end": datetime(2020, 4, 1)}),
            (HourlyResult.DAYS_NONE, {"end": datetime(2020, 4, 1).replace(tzinfo=timezone.utc)}),
            (HourlyResult.DAYS_NONE, {"start": datetime(2090, 5, 31)}),
            (HourlyResult.DAYS_NONE, {"start": datetime(2090, 5, 31).replace(tzinfo=timezone.utc)}),
            (days_past_from_oldest, {"start": datetime(2020, 4, 1)}),
            (days_past_from_oldest, {"start": datetime(2020, 4, 1).replace(tzinfo=timezone.utc)}),
            (days_past_from_oldest, {}),
            (15, {"start": datetime(2020, 4, 1), "end": datetime(2020, 4, 16), "hr_range": 5})
        )

        for expected_value, kwargs in data:
            with self.subTest(expected_value=expected_value, kwargs=kwargs):
                self.assertAlmostEqual(expected_value,
                                       TestHourlyResult.TestSample1.data_days_collected(col, {}, **kwargs),
                                       0)

    def test_data_days_collected_no_data(self):
        col = self.get_mongo_client().get_database(self.get_db_name()).get_collection("AAAAA")
        dc = TestHourlyResult.TestSample1.data_days_collected(col, {}, end=datetime(2090, 5, 31))

        self.assertEqual(dc, 0)


class TestDailyResult(TestDatabaseMixin):
    def test_date_list(self):
        data = (
            (5, {},
             [datetime.utcnow().date() - timedelta(days=i) for i in range(5, -1, -1)]),
            (5, {"start": datetime(2020, 5, 1)},
             [date(2020, 5, 1), date(2020, 5, 2), date(2020, 5, 3),
              date(2020, 5, 4), date(2020, 5, 5), date(2020, 5, 6)]),
            (5.5, {"start": datetime(2020, 5, 1)},
             [date(2020, 5, 1), date(2020, 5, 2), date(2020, 5, 3),
              date(2020, 5, 4), date(2020, 5, 5), date(2020, 5, 6)]),
            (5, {"end": datetime(2020, 5, 1)},
             [date(2020, 4, 26), date(2020, 4, 27), date(2020, 4, 28),
              date(2020, 4, 29), date(2020, 4, 30), date(2020, 5, 1)]),
            (5, {"start": datetime(2020, 5, 1), "end": datetime(2020, 5, 3)},
             [date(2020, 5, 1), date(2020, 5, 2), date(2020, 5, 3)]),
            (5, {"start": datetime(2020, 5, 1), "end": datetime(2020, 5, 3),
                 "trange": TimeRange(start=datetime(2020, 5, 3), end=datetime(2020, 5, 6))},
             [date(2020, 5, 3), date(2020, 5, 4), date(2020, 5, 5), date(2020, 5, 6)]),
            (5, {"trange": TimeRange(start=datetime(2020, 5, 3), end=datetime(2020, 5, 6))},
             [date(2020, 5, 3), date(2020, 5, 4), date(2020, 5, 5), date(2020, 5, 6)])
        )

        for days_collected, kwargs, expected_datelist in data:
            actual_datelist = DailyResult.date_list(days_collected, timezone.utc, **kwargs)

            with self.subTest(days_collected=days_collected, kwargs=kwargs):
                self.assertEqual(actual_datelist, expected_datelist)

    def test_date_list_str(self):
        data = (
            (5, {},
             [(datetime.utcnow().date() - timedelta(days=i)).strftime(DailyResult.FMT_DATE)
              for i in range(5, -1, -1)]),
            (5, {"start": datetime(2020, 5, 1)},
             ["2020-05-01", "2020-05-02", "2020-05-03", "2020-05-04", "2020-05-05", "2020-05-06"]),
            (5.5, {"start": datetime(2020, 5, 1)},
             ["2020-05-01", "2020-05-02", "2020-05-03", "2020-05-04", "2020-05-05", "2020-05-06"]),
            (5, {"end": datetime(2020, 5, 1)},
             ["2020-04-26", "2020-04-27", "2020-04-28", "2020-04-29", "2020-04-30", "2020-05-01"]),
            (5, {"start": datetime(2020, 5, 1), "end": datetime(2020, 5, 3)},
             ["2020-05-01", "2020-05-02", "2020-05-03"]),
            (5, {"start": datetime(2020, 5, 1), "end": datetime(2020, 5, 3, 14, 0)},
             ["2020-05-01", "2020-05-02", "2020-05-03"]),
            (5, {"start": datetime(2020, 5, 1), "end": datetime(2020, 5, 3),
                 "trange": TimeRange(start=datetime(2020, 5, 3), end=datetime(2020, 5, 6))},
             ["2020-05-03", "2020-05-04", "2020-05-05", "2020-05-06"]),
            (5, {"trange": TimeRange(start=datetime(2020, 5, 3), end=datetime(2020, 5, 6))},
             ["2020-05-03", "2020-05-04", "2020-05-05", "2020-05-06"])
        )

        for days_collected, kwargs, expected_datelist in data:
            actual_datelist = DailyResult.date_list_str(days_collected, timezone.utc, **kwargs)

            with self.subTest(days_collected=days_collected, kwargs=kwargs):
                self.assertEqual(actual_datelist, expected_datelist)

    def test_trange_not_inf(self):
        data = (
            (3, TimeRange(start=None, end=None, end_autofill_now=False), timezone.utc),
            (0, TimeRange(start=None, end=None, end_autofill_now=False), timezone.utc),
            (3, TimeRange(start=None, end=None, end_autofill_now=True), timezone.utc),
            (0, TimeRange(start=None, end=None, end_autofill_now=True), timezone.utc)
        )

        for args in data:
            new_trange = DailyResult.trange_ensure_not_inf(*args)

            with self.subTest(args):
                self.assertFalse(new_trange.is_inf)
