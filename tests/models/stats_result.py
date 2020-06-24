from datetime import datetime, date, timedelta
from time import gmtime, strftime

from bson import ObjectId
from django.utils import timezone
from pymongo.collection import Collection

from extutils.dt import TimeRange
from flags import MessageType, BotFeature
from tests.base import TestDatabaseMixin
from models import (
    HourlyResult, DailyResult, HourlyIntervalAverageMessageResult, DailyMessageResult, MemberMessageByCategoryResult,
    MeanMessageResultGenerator, MemberDailyMessageResult, CountBeforeTimeResult, MemberMessageCountResult,
    MemberMessageCountEntry, BotFeatureUsageResult, BotFeaturePerUserUsageResult, BotFeatureHourlyAvgResult
)
from strres.models import StatsResults
from tests.base import TestCase

__all__ = ["TestDailyResult", "TestHourlyResult", "TestHourlyIntervalAverageMessageResult", "TestDailyMessageResult",
           "TestMeanMessageResultGenerator", "TestMemberDailyMessageResult", "TestMemberMessageCountResult",
           "TestMemberMessageByCategoryResult", "TestBotFeatureUsageResult", "TestBotFeaturePerUserUsageResult",
           "TestBotFeatureHourlyAvgResult", "TestCountBeforeTimeResult"]


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
        col = self.get_collection("testcol")

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
        col = self.get_collection("AAAAA")
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
            (5, {"start": datetime(2020, 5, 1), "end": datetime(2020, 5, 3, 14)},
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


class TestHourlyIntervalAverageMessageResult(TestCase):
    @staticmethod
    def get_cursor():
        return [
            {
                "_id": {
                    HourlyIntervalAverageMessageResult.KEY_HR: 3,
                    HourlyIntervalAverageMessageResult.KEY_CATEGORY: MessageType.TEXT
                },
                HourlyIntervalAverageMessageResult.KEY_COUNT: 150
            },
            {
                "_id": {
                    HourlyIntervalAverageMessageResult.KEY_HR: 3,
                    HourlyIntervalAverageMessageResult.KEY_CATEGORY: MessageType.IMAGE
                },
                HourlyIntervalAverageMessageResult.KEY_COUNT: 100
            },
            {
                "_id": {
                    HourlyIntervalAverageMessageResult.KEY_HR: 4,
                    HourlyIntervalAverageMessageResult.KEY_CATEGORY: MessageType.TEXT
                },
                HourlyIntervalAverageMessageResult.KEY_COUNT: 18
            },
            {
                "_id": {
                    HourlyIntervalAverageMessageResult.KEY_HR: 4,
                    HourlyIntervalAverageMessageResult.KEY_CATEGORY: MessageType.IMAGE
                },
                HourlyIntervalAverageMessageResult.KEY_COUNT: 21
            }
        ]

    def test_empty_data(self):
        result = HourlyIntervalAverageMessageResult(
            [], 2, end_time=datetime(2020, 5, 7, 4, tzinfo=timezone.utc))

        self.assertEqual(result.label_hr, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                                           13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23])
        self.assertEqual(result.hr_range, 48)
        self.assertEqual(result.data, [
            (StatsResults.CATEGORY_TOTAL, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             "#323232", "false")
        ])

    def test_data(self):
        result = HourlyIntervalAverageMessageResult(
            self.get_cursor(), 2, end_time=datetime(2020, 5, 7, 4, tzinfo=timezone.utc))

        self.assertEqual(result.label_hr, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                                           13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23])
        self.assertEqual(result.hr_range, 48)
        self.assertEqual(result.data, [
            (StatsResults.CATEGORY_TOTAL, [0, 0, 0, 125, 13, 0, 0, 0, 0, 0, 0, 0,
                                           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             "#323232", "false"),
            (MessageType.TEXT.key, [0, 0, 0, 75, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             "#777777", "true"),
            (MessageType.IMAGE.key, [0, 0, 0, 50, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             "#777777", "true")
        ])


class TestDailyMessageResult(TestCase):
    @staticmethod
    def get_cursor():
        return [
            {
                "_id": {
                    DailyMessageResult.KEY_DATE: "2020-05-07",
                    DailyMessageResult.KEY_HOUR: 0
                },
                DailyMessageResult.KEY_COUNT: 10
            },
            {
                "_id": {
                    DailyMessageResult.KEY_DATE: "2020-05-07",
                    DailyMessageResult.KEY_HOUR: 1
                },
                DailyMessageResult.KEY_COUNT: 20
            },
            {
                "_id": {
                    DailyMessageResult.KEY_DATE: "2020-05-08",
                    DailyMessageResult.KEY_HOUR: 0
                },
                DailyMessageResult.KEY_COUNT: 30
            },
            {
                "_id": {
                    DailyMessageResult.KEY_DATE: "2020-05-08",
                    DailyMessageResult.KEY_HOUR: 1
                },
                DailyMessageResult.KEY_COUNT: 40
            }
        ]

    def test_data(self):
        result = DailyMessageResult(self.get_cursor(), 2, timezone.utc, start=datetime(2020, 5, 7))

        self.assertEqual(result.label_hr, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                                           13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23])
        self.assertEqual(result.label_date, ["2020-05-07", "2020-05-08", "2020-05-09"])
        self.assertEqual(result.data_sum, [30, 70, 0])

        data = (
            (
                "2020-05-07",
                [(10, 1 / 3 * 100, False), (20, 2 / 3 * 100, True), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False)]
            ),
            (
                "2020-05-08",
                [(30, 3 / 7 * 100, False), (40, 4 / 7 * 100, True), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False)]
            ),
            (
                "2020-05-09",
                [(0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False)]
            )
        )

        for idx, d in enumerate(data):
            with self.subTest(idx):
                self.assertEqual(result.data[idx], d)

    def test_empty_data(self):
        result = DailyMessageResult([], 2, timezone.utc, start=datetime(2020, 5, 7))

        self.assertEqual(result.label_hr, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                                           13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23])
        self.assertEqual(result.label_date, ["2020-05-07", "2020-05-08", "2020-05-09"])
        self.assertEqual(result.data_sum, [0, 0, 0])

        data = (
            (
                "2020-05-07",
                [(0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False)]
            ),
            (
                "2020-05-08",
                [(0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False)]
            ),
            (
                "2020-05-09",
                [(0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False),
                 (0, 0, False), (0, 0, False), (0, 0, False), (0, 0, False)]
            )
        )

        for idx, d in enumerate(data):
            with self.subTest(idx):
                self.assertEqual(result.data[idx], d)


class TestMeanMessageResultGenerator(TestCase):
    @staticmethod
    def get_cursor():
        return [
            {
                "_id": {MeanMessageResultGenerator.KEY_DATE: "2020-05-07"},
                MeanMessageResultGenerator.KEY_COUNT: 500
            },
            {
                "_id": {MeanMessageResultGenerator.KEY_DATE: "2020-05-08"},
                MeanMessageResultGenerator.KEY_COUNT: 600
            },
            {
                "_id": {MeanMessageResultGenerator.KEY_DATE: "2020-05-09"},
                MeanMessageResultGenerator.KEY_COUNT: 700
            },
        ]

    def get_result(self):
        return MeanMessageResultGenerator(
            self.get_cursor(), 2, timezone.utc,
            trange=TimeRange(start=datetime(2020, 5, 7), end=datetime(2020, 5, 9)), max_mean_days=2)

    @staticmethod
    def get_result_empty():
        return MeanMessageResultGenerator(
            [], 0, timezone.utc,
            trange=TimeRange(start=datetime(2020, 5, 7), end=datetime(2020, 5, 9)), max_mean_days=2)

    def test_empty_generator(self):
        result = self.get_result_empty()

        self.assertEqual(result.max_madays, 2)
        self.assertEqual(result.trange, TimeRange(start=datetime(2020, 5, 7), end=datetime(2020, 5, 9)))
        self.assertEqual(result.dates, [date(2020, 5, 7), date(2020, 5, 8), date(2020, 5, 9)])
        self.assertEqual(result.data, {date(2020, 5, 7): 0,
                                       date(2020, 5, 8): 0,
                                       date(2020, 5, 9): 0})

    def test_base_generator(self):
        result = self.get_result()

        self.assertEqual(result.max_madays, 2)
        self.assertEqual(result.trange, TimeRange(start=datetime(2020, 5, 7), end=datetime(2020, 5, 9)))
        self.assertEqual(result.dates, [date(2020, 5, 7), date(2020, 5, 8), date(2020, 5, 9)])
        self.assertEqual(result.data, {date(2020, 5, 7): 500,
                                       date(2020, 5, 8): 600,
                                       date(2020, 5, 9): 700})

    def test_generate_out_of_range(self):
        result = self.get_result()

        with self.assertRaises(ValueError):
            result.generate_result(3)

        with self.assertRaises(ValueError):
            result.generate_result(0)

        with self.assertRaises(ValueError):
            result.generate_result(-1)

    def test_generate_2_empty(self):
        result = self.get_result_empty()

        rst = result.generate_result(2)

        self.assertEqual(rst.date_list, [date(2020, 5, 7), date(2020, 5, 8), date(2020, 5, 9)])
        self.assertEqual(rst.data_list, [0, 0, 0])
        self.assertEqual(rst.label, StatsResults.DAYS_MEAN.format(2))

    def test_generate_2(self):
        result = self.get_result()

        rst = result.generate_result(2)

        self.assertEqual(rst.date_list, [date(2020, 5, 7), date(2020, 5, 8), date(2020, 5, 9)])
        self.assertEqual(rst.data_list, [250, 550, 650])
        self.assertEqual(rst.label, StatsResults.DAYS_MEAN.format(2))

    def test_generate_1_empty(self):
        result = self.get_result_empty()

        rst = result.generate_result(1)

        self.assertEqual(rst.date_list, [date(2020, 5, 7), date(2020, 5, 8), date(2020, 5, 9)])
        self.assertEqual(rst.data_list, [0, 0, 0])
        self.assertEqual(rst.label, StatsResults.DAYS_MEAN.format(1))

    def test_generate_1(self):
        result = self.get_result()

        rst = result.generate_result(1)

        self.assertEqual(rst.date_list, [date(2020, 5, 7), date(2020, 5, 8), date(2020, 5, 9)])
        self.assertEqual(rst.data_list, [500, 600, 700])
        self.assertEqual(rst.label, StatsResults.DAYS_MEAN.format(1))


class TestMemberDailyMessageResult(TestCase):
    MEMBER_1 = ObjectId()
    MEMBER_2 = ObjectId()

    @staticmethod
    def get_cursor():
        return [
            {
                "_id": {
                    MemberDailyMessageResult.KEY_DATE: "2020-05-07",
                    MemberDailyMessageResult.KEY_MEMBER: TestMemberDailyMessageResult.MEMBER_1
                },
                MemberDailyMessageResult.KEY_COUNT: 10
            },
            {
                "_id": {
                    MemberDailyMessageResult.KEY_DATE: "2020-05-08",
                    MemberDailyMessageResult.KEY_MEMBER: TestMemberDailyMessageResult.MEMBER_1
                },
                MemberDailyMessageResult.KEY_COUNT: 20
            },
            {
                "_id": {
                    MemberDailyMessageResult.KEY_DATE: "2020-05-07",
                    MemberDailyMessageResult.KEY_MEMBER: TestMemberDailyMessageResult.MEMBER_2
                },
                MemberDailyMessageResult.KEY_COUNT: 30
            },
            {
                "_id": {
                    MemberDailyMessageResult.KEY_DATE: "2020-05-08",
                    MemberDailyMessageResult.KEY_MEMBER: TestMemberDailyMessageResult.MEMBER_2
                },
                MemberDailyMessageResult.KEY_COUNT: 40
            }
        ]

    def test_data(self):
        result = MemberDailyMessageResult(self.get_cursor(), 2, timezone.utc,
                                          trange=TimeRange(start=datetime(2020, 5, 7), end=datetime(2020, 5, 8)))

        self.assertEqual(result.trange, TimeRange(start=datetime(2020, 5, 7), end=datetime(2020, 5, 8)))
        self.assertEqual(result.dates, ["2020-05-07", "2020-05-08"])
        self.assertEqual(result.data_count,
                         {
                             "2020-05-07": {
                                 TestMemberDailyMessageResult.MEMBER_1: 10,
                                 TestMemberDailyMessageResult.MEMBER_2: 30
                             },
                             "2020-05-08": {
                                 TestMemberDailyMessageResult.MEMBER_1: 20,
                                 TestMemberDailyMessageResult.MEMBER_2: 40
                             }
                         })

    def test_empty_data(self):
        result = MemberDailyMessageResult([], 2, timezone.utc,
                                          trange=TimeRange(start=datetime(2020, 5, 7), end=datetime(2020, 5, 8)))

        self.assertEqual(result.trange, TimeRange(start=datetime(2020, 5, 7), end=datetime(2020, 5, 8)))
        self.assertEqual(result.dates, ["2020-05-07", "2020-05-08"])
        self.assertEqual(result.data_count, {"2020-05-07": {}, "2020-05-08": {}})


class TestCountBeforeTimeResult(TestCase):
    @staticmethod
    def get_cursor():
        return [
            {
                "_id": {
                    CountBeforeTimeResult.KEY_DATE: "2020-05-07"
                },
                CountBeforeTimeResult.KEY_COUNT: 100
            },
            {
                "_id": {
                    CountBeforeTimeResult.KEY_DATE: "2020-05-08"
                },
                CountBeforeTimeResult.KEY_COUNT: 200
            },
            {
                "_id": {
                    CountBeforeTimeResult.KEY_DATE: "2020-05-09"
                },
                CountBeforeTimeResult.KEY_COUNT: 300
            },
            {
                "_id": {
                    CountBeforeTimeResult.KEY_DATE: "2020-05-10"
                },
                CountBeforeTimeResult.KEY_COUNT: 400
            }
        ]

    def test_data(self):
        result = CountBeforeTimeResult(self.get_cursor(), 4, timezone.utc,
                                       trange=TimeRange(start=datetime(2020, 5, 7), end=datetime(2020, 5, 10)))

        self.assertEqual(result.trange, TimeRange(start=datetime(2020, 5, 7), end=datetime(2020, 5, 10)))
        self.assertEqual(result.dates, ["2020-05-07", "2020-05-08", "2020-05-09", "2020-05-10"])
        self.assertEqual(result.data_count, [100, 200, 300, 400])
        self.assertEqual(result.title,
                         StatsResults.COUNT_BEFORE.format(
                             strftime("%I:%M:%S %p", gmtime(result.trange.end_time_seconds))))

    def test_empty_data(self):
        result = CountBeforeTimeResult([], 4, timezone.utc,
                                       trange=TimeRange(start=datetime(2020, 5, 7), end=datetime(2020, 5, 10)))

        self.assertEqual(result.trange, TimeRange(start=datetime(2020, 5, 7), end=datetime(2020, 5, 10)))
        self.assertEqual(result.dates, ["2020-05-07", "2020-05-08", "2020-05-09", "2020-05-10"])
        self.assertEqual(result.data_count, [0, 0, 0, 0])
        self.assertEqual(result.title,
                         StatsResults.COUNT_BEFORE.format(
                             strftime("%I:%M:%S %p", gmtime(result.trange.end_time_seconds))))


class TestMemberMessageCountResult(TestCase):
    MEMBER_1 = ObjectId()
    MEMBER_2 = ObjectId()

    @staticmethod
    def get_cursor_1_interval():
        return [
            {
                "_id": {
                    MemberMessageCountResult.KEY_MEMBER_ID: TestMemberMessageCountResult.MEMBER_1,
                    MemberMessageCountResult.KEY_INTERVAL_IDX: 0
                },
                MemberMessageCountResult.KEY_COUNT: 100
            },
            {
                "_id": {
                    MemberMessageCountResult.KEY_MEMBER_ID: TestMemberMessageCountResult.MEMBER_2,
                    MemberMessageCountResult.KEY_INTERVAL_IDX: 0
                },
                MemberMessageCountResult.KEY_COUNT: 200
            }
        ]

    @staticmethod
    def get_cursor_2_intervals():
        return [
            {
                "_id": {
                    MemberMessageCountResult.KEY_MEMBER_ID: TestMemberMessageCountResult.MEMBER_1,
                    MemberMessageCountResult.KEY_INTERVAL_IDX: 0
                },
                MemberMessageCountResult.KEY_COUNT: 100
            },
            {
                "_id": {
                    MemberMessageCountResult.KEY_MEMBER_ID: TestMemberMessageCountResult.MEMBER_1,
                    MemberMessageCountResult.KEY_INTERVAL_IDX: 1
                },
                MemberMessageCountResult.KEY_COUNT: 200
            },
            {
                "_id": {
                    MemberMessageCountResult.KEY_MEMBER_ID: TestMemberMessageCountResult.MEMBER_2,
                    MemberMessageCountResult.KEY_INTERVAL_IDX: 0
                },
                MemberMessageCountResult.KEY_COUNT: 300
            },
            {
                "_id": {
                    MemberMessageCountResult.KEY_MEMBER_ID: TestMemberMessageCountResult.MEMBER_2,
                    MemberMessageCountResult.KEY_INTERVAL_IDX: 1
                },
                MemberMessageCountResult.KEY_COUNT: 400
            }
        ]

    def test_data_empty(self):
        result = MemberMessageCountResult([], 3,
                                          trange=TimeRange(start=datetime(2020, 5, 7), end=datetime(2020, 5, 10)))

        self.assertEqual(result.trange, TimeRange(start=datetime(2020, 5, 7), end=datetime(2020, 5, 10)))
        self.assertEqual(result.interval, 3)

        self.assertEqual(result.data, {})

    def test_data_1_interval(self):
        result = MemberMessageCountResult(self.get_cursor_1_interval(), 1,
                                          trange=TimeRange(start=datetime(2020, 5, 7), end=datetime(2020, 5, 10)))

        self.assertEqual(result.trange, TimeRange(start=datetime(2020, 5, 7), end=datetime(2020, 5, 10)))
        self.assertEqual(result.interval, 1)

        entry = MemberMessageCountEntry(intervals=1)
        entry.count[0] = 100

        self.assertEqual(result.data[TestMemberMessageCountResult.MEMBER_1], entry)

        entry = MemberMessageCountEntry(intervals=1)
        entry.count[0] = 200

        self.assertEqual(result.data[TestMemberMessageCountResult.MEMBER_2], entry)

    def test_data_2_intervals(self):
        result = MemberMessageCountResult(self.get_cursor_2_intervals(), 2,
                                          trange=TimeRange(start=datetime(2020, 5, 7), end=datetime(2020, 5, 10)))

        self.assertEqual(result.trange, TimeRange(start=datetime(2020, 5, 7), end=datetime(2020, 5, 10)))
        self.assertEqual(result.interval, 2)

        entry = MemberMessageCountEntry(intervals=2)
        entry.count[0] = 100
        entry.count[1] = 200

        self.assertEqual(result.data[TestMemberMessageCountResult.MEMBER_1], entry)

        entry = MemberMessageCountEntry(intervals=2)
        entry.count[0] = 300
        entry.count[1] = 400

        self.assertEqual(result.data[TestMemberMessageCountResult.MEMBER_2], entry)


class TestMemberMessageByCategoryResult(TestCase):
    MEMBER_1 = ObjectId()
    MEMBER_2 = ObjectId()

    @staticmethod
    def get_cursor():
        return [
            {
                "_id": {
                    MemberMessageByCategoryResult.KEY_MEMBER_ID: TestMemberMessageByCategoryResult.MEMBER_1,
                    MemberMessageByCategoryResult.KEY_CATEGORY: MessageType.TEXT,
                },
                MemberMessageByCategoryResult.KEY_COUNT: 100
            },
            {
                "_id": {
                    MemberMessageByCategoryResult.KEY_MEMBER_ID: TestMemberMessageByCategoryResult.MEMBER_1,
                    MemberMessageByCategoryResult.KEY_CATEGORY: MessageType.IMAGE,
                },
                MemberMessageByCategoryResult.KEY_COUNT: 200
            },
            {
                "_id": {
                    MemberMessageByCategoryResult.KEY_MEMBER_ID: TestMemberMessageByCategoryResult.MEMBER_2,
                    MemberMessageByCategoryResult.KEY_CATEGORY: MessageType.TEXT,
                },
                MemberMessageByCategoryResult.KEY_COUNT: 300
            },
            {
                "_id": {
                    MemberMessageByCategoryResult.KEY_MEMBER_ID: TestMemberMessageByCategoryResult.MEMBER_2,
                    MemberMessageByCategoryResult.KEY_CATEGORY: MessageType.IMAGE,
                },
                MemberMessageByCategoryResult.KEY_COUNT: 400
            }
        ]

    def get_result(self):
        return MemberMessageByCategoryResult(self.get_cursor())

    @staticmethod
    def get_result_empty():
        return MemberMessageByCategoryResult([])

    def test_data(self):
        result = self.get_result()

        self.assertEqual(result.label_category, [
            MessageType.TEXT, MessageType.LINE_STICKER, MessageType.IMAGE, MessageType.VIDEO,
            MessageType.AUDIO, MessageType.LOCATION, MessageType.FILE
        ])

    def test_empty_data(self):
        result = self.get_result_empty()

        self.assertEqual(result.label_category, [
            MessageType.TEXT, MessageType.LINE_STICKER, MessageType.IMAGE, MessageType.VIDEO,
            MessageType.AUDIO, MessageType.LOCATION, MessageType.FILE
        ])

    def test_member_empty(self):
        result = self.get_result_empty()

        self.assertEqual(result.data, {})

    def test_member1(self):
        result = self.get_result()

        mbr = result.data[TestMemberMessageByCategoryResult.MEMBER_1]
        self.assertEqual(mbr.data, {MessageType.TEXT: 100, MessageType.IMAGE: 200, MessageType.LINE_STICKER: 0,
                                    MessageType.LOCATION: 0, MessageType.FILE: 0, MessageType.AUDIO: 0,
                                    MessageType.VIDEO: 0})
        self.assertEqual(mbr.total, 300)
        self.assertEqual(mbr.get_count(MessageType.TEXT), 100)
        self.assertEqual(mbr.get_count(MessageType.IMAGE), 200)
        self.assertEqual(mbr.get_count(MessageType.LINE_STICKER), 0)

    def test_member2(self):
        result = self.get_result()

        mbr = result.data[TestMemberMessageByCategoryResult.MEMBER_2]
        self.assertEqual(mbr.data, {MessageType.TEXT: 300, MessageType.IMAGE: 400, MessageType.LINE_STICKER: 0,
                                    MessageType.LOCATION: 0, MessageType.FILE: 0, MessageType.AUDIO: 0,
                                    MessageType.VIDEO: 0})
        self.assertEqual(mbr.total, 700)
        self.assertEqual(mbr.get_count(MessageType.TEXT), 300)
        self.assertEqual(mbr.get_count(MessageType.IMAGE), 400)
        self.assertEqual(mbr.get_count(MessageType.LINE_STICKER), 0)


class TestBotFeatureUsageResult(TestCase):
    @staticmethod
    def get_cursor():
        return [
            {"_id": BotFeature.TXT_AR_ADD, BotFeatureUsageResult.KEY: 100},
            {"_id": BotFeature.TXT_AR_INFO, BotFeatureUsageResult.KEY: 20},
            {"_id": BotFeature.TXT_AR_DEL, BotFeatureUsageResult.KEY: 20},
            {"_id": BotFeature.TXT_CALCULATOR, BotFeatureUsageResult.KEY: 1},
        ]

    def test_data_empty(self):
        result = BotFeatureUsageResult([], True)

        expected = (
            (BotFeature.TXT_AR_ADD.key, 0, "T1"),
            (BotFeature.TXT_AR_INFO.key, 0, "T1"),
            (BotFeature.TXT_AR_DEL.key, 0, "T1"),
            (BotFeature.TXT_CALCULATOR.key, 0, "T1"),
            (BotFeature.TXT_AR_ADD_EXECODE.key, 0, "T1"),
        )

        for e in expected:
            with self.subTest(e):
                self.assertTrue(e in result.data)

        self.assertEqual(result.chart_label, [d.feature_name for d in result.data])
        self.assertEqual(result.chart_data, [d.count for d in result.data])

    def test_data_incl_not_used(self):
        result = BotFeatureUsageResult(self.get_cursor(), True)

        expected = (
            (BotFeature.TXT_AR_ADD.key, 100, "1"),
            (BotFeature.TXT_AR_INFO.key, 20, "T2"),
            (BotFeature.TXT_AR_DEL.key, 20, "T2"),
            (BotFeature.TXT_CALCULATOR.key, 1, "4"),
            (BotFeature.TXT_AR_ADD_EXECODE.key, 0, "T5"),
        )

        for e in expected:
            with self.subTest(e):
                self.assertTrue(e in result.data)

        self.assertEqual(result.chart_label, [d.feature_name for d in result.data])
        self.assertEqual(result.chart_data, [d.count for d in result.data])

    def test_data_not_incl_not_used(self):
        result = BotFeatureUsageResult(self.get_cursor(), False)

        expected = (
            (BotFeature.TXT_AR_ADD.key, 100, "1"),
            (BotFeature.TXT_AR_INFO.key, 20, "T2"),
            (BotFeature.TXT_AR_DEL.key, 20, "T2"),
            (BotFeature.TXT_CALCULATOR.key, 1, "4")
        )

        for e in expected:
            with self.subTest(e):
                self.assertTrue(e in result.data)

        self.assertFalse((BotFeature.TXT_AR_ADD_EXECODE.key, 0, "5") in result.data)

        self.assertEqual(result.chart_label, [d.feature_name for d in result.data])
        self.assertEqual(result.chart_data, [d.count for d in result.data])


class TestBotFeaturePerUserUsageResult(TestCase):
    MEMBER_1 = ObjectId()
    MEMBER_2 = ObjectId()

    @staticmethod
    def get_cursor():
        return [
            {
                "_id": {
                    BotFeaturePerUserUsageResult.KEY_FEATURE: BotFeature.TXT_AR_ADD,
                    BotFeaturePerUserUsageResult.KEY_UID: TestBotFeaturePerUserUsageResult.MEMBER_1
                },
                BotFeaturePerUserUsageResult.KEY_COUNT: 10
            },
            {
                "_id": {
                    BotFeaturePerUserUsageResult.KEY_FEATURE: BotFeature.TXT_AR_INFO,
                    BotFeaturePerUserUsageResult.KEY_UID: TestBotFeaturePerUserUsageResult.MEMBER_1
                },
                BotFeaturePerUserUsageResult.KEY_COUNT: 20
            },
            {
                "_id": {
                    BotFeaturePerUserUsageResult.KEY_FEATURE: BotFeature.TXT_AR_ADD,
                    BotFeaturePerUserUsageResult.KEY_UID: TestBotFeaturePerUserUsageResult.MEMBER_2
                },
                BotFeaturePerUserUsageResult.KEY_COUNT: 30
            },
            {
                "_id": {
                    BotFeaturePerUserUsageResult.KEY_FEATURE: BotFeature.TXT_AR_INFO,
                    BotFeaturePerUserUsageResult.KEY_UID: TestBotFeaturePerUserUsageResult.MEMBER_2
                },
                BotFeaturePerUserUsageResult.KEY_COUNT: 40
            }
        ]

    def test_empty_data(self):
        result = BotFeaturePerUserUsageResult([])

        self.assertEqual(result.data, {})

    def test_data(self):
        result = BotFeaturePerUserUsageResult(self.get_cursor())

        dict_ = {ft: 0 for ft in BotFeature}
        dict_.update({BotFeature.TXT_AR_ADD: 10, BotFeature.TXT_AR_INFO: 20})

        self.assertEqual(result.data[TestBotFeaturePerUserUsageResult.MEMBER_1], dict_)

        dict_ = {ft: 0 for ft in BotFeature}
        dict_.update({BotFeature.TXT_AR_ADD: 30, BotFeature.TXT_AR_INFO: 40})

        self.assertEqual(result.data[TestBotFeaturePerUserUsageResult.MEMBER_2], dict_)


class TestBotFeatureHourlyAvgResult(TestCase):
    @staticmethod
    def get_cursor():
        return [
            {
                "_id": {
                    BotFeatureHourlyAvgResult.KEY_FEATURE: BotFeature.TXT_AR_INFO,
                    BotFeatureHourlyAvgResult.KEY_HR: 0
                },
                BotFeatureHourlyAvgResult.KEY_COUNT: 100
            },
            {
                "_id": {
                    BotFeatureHourlyAvgResult.KEY_FEATURE: BotFeature.TXT_AR_INFO,
                    BotFeatureHourlyAvgResult.KEY_HR: 1
                },
                BotFeatureHourlyAvgResult.KEY_COUNT: 200
            },
            {
                "_id": {
                    BotFeatureHourlyAvgResult.KEY_FEATURE: BotFeature.TXT_AR_ADD,
                    BotFeatureHourlyAvgResult.KEY_HR: 0
                },
                BotFeatureHourlyAvgResult.KEY_COUNT: 300
            },
            {
                "_id": {
                    BotFeatureHourlyAvgResult.KEY_FEATURE: BotFeature.TXT_AR_ADD,
                    BotFeatureHourlyAvgResult.KEY_HR: 1
                },
                BotFeatureHourlyAvgResult.KEY_COUNT: 400
            },
            {
                "_id": {
                    BotFeatureHourlyAvgResult.KEY_FEATURE: BotFeature.TXT_CALCULATOR,
                    BotFeatureHourlyAvgResult.KEY_HR: 8
                },
                BotFeatureHourlyAvgResult.KEY_COUNT: 300
            },
        ]

    def test_empty(self):
        result = BotFeatureHourlyAvgResult([], True, 2.25, end_time=datetime(2020, 5, 7, 12))

        self.assertEqual(result.hr_range, 54)
        self.assertEqual(result.label_hr, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                                           12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23])
        self.assertTrue(result.avg_calculatable)

        expected = (
            (BotFeature.TXT_AR_ADD, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "#9C0000", "true"),
            (BotFeature.TXT_AR_INFO, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "#9C0000", "true"),
            (BotFeature.TXT_CALCULATOR, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "#9C0000", "true"),
            (BotFeature.TXT_AR_ADD_EXECODE, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "#9C0000", "true"),
            (StatsResults.CATEGORY_TOTAL, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "#323232", "false")
        )

        for e in expected:
            with self.subTest(e):
                self.assertTrue(e in result.data)

    def test_empty_not_incl_not_used(self):
        result = BotFeatureHourlyAvgResult([], False, 2.25, end_time=datetime(2020, 5, 7, 12))

        self.assertEqual(result.hr_range, 54)
        self.assertEqual(result.label_hr, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                                           12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23])
        self.assertTrue(result.avg_calculatable)

        self.assertEqual(result.data,
                         [(StatsResults.CATEGORY_TOTAL,
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           "#323232", "false")])

    def test_incl_not_used(self):
        result = BotFeatureHourlyAvgResult(self.get_cursor(), True, 2.25, end_time=datetime(2020, 5, 7, 12))

        self.assertEqual(result.hr_range, 54)
        self.assertEqual(result.label_hr, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                                           12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23])
        self.assertTrue(result.avg_calculatable)

        expected = (
            (BotFeature.TXT_AR_ADD, [150, 200, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "#00A14B", "true"),
            (BotFeature.TXT_AR_INFO, [50, 100, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "#00A14B", "true"),
            (BotFeature.TXT_CALCULATOR, [0, 0, 0, 0, 0, 0, 0, 0, 100, 0, 0, 0,
                                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "#00A14B", "true"),
            (BotFeature.TXT_AR_ADD_EXECODE, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "#9C0000", "true"),
            (StatsResults.CATEGORY_TOTAL, [200, 300, 0, 0, 0, 0, 0, 0, 100, 0, 0, 0,
                                           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "#323232", "false")
        )

        for e in expected:
            with self.subTest(e):
                self.assertTrue(e in result.data)

    def test_not_incl_not_used(self):
        result = BotFeatureHourlyAvgResult(self.get_cursor(), False, 2.25, end_time=datetime(2020, 5, 7, 12))

        self.assertEqual(result.hr_range, 54)
        self.assertEqual(result.label_hr, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                                           12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23])
        self.assertTrue(result.avg_calculatable)

        expected = (
            (BotFeature.TXT_AR_ADD, [150, 200, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "#00A14B", "true"),
            (BotFeature.TXT_AR_INFO, [50, 100, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "#00A14B", "true"),
            (BotFeature.TXT_CALCULATOR, [0, 0, 0, 0, 0, 0, 0, 0, 100, 0, 0, 0,
                                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "#00A14B", "true"),
            (StatsResults.CATEGORY_TOTAL, [200, 300, 0, 0, 0, 0, 0, 0, 100, 0, 0, 0,
                                           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "#323232", "false")
        )

        for e in expected:
            with self.subTest(e):
                self.assertTrue(e in result.data)

        self.assertFalse((BotFeature.TXT_AR_ADD_EXECODE,
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "#9C0000", "true")
                         in result.data)
