from datetime import datetime, timezone, timedelta
from typing import Dict, Tuple, Any, Type

from bson import ObjectId

from extutils.dt import now_utc_aware, t_delta_str, localtime
from extutils.locales import LocaleInfo
from models import Model, TimerModel, TimerListResult, RootUserModel, RootUserConfigModel
from strnames.models import Timer
from tests.base import TestCase

from ._test_base import TestModel

__all__ = ["TestTimerModel", "TestTimerListResult"]


class TestTimerModel(TestModel.TestClass):
    CHANNEL_OID = ObjectId()
    TARGET_TIME = datetime(2020, 5, 7, 12).replace(tzinfo=timezone.utc)
    DELETION_TIME = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(days=7)

    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return TimerModel

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("ch", "ChannelOid"): TestTimerModel.CHANNEL_OID,
            ("k", "Keyword"): "ABCD",
            ("t", "Title"): "EFGH",
            ("tt", "TargetTime"): TestTimerModel.TARGET_TIME
        }

    @classmethod
    def get_default(cls) -> Dict[Tuple[str, str], Tuple[Any, Any]]:
        return {
            ("c", "Countup"): (False, True),
            ("nt", "Notified"): (False, True),
            ("nt-e", "NotifiedExpired"): (False, True),
            ("p", "PeriodSeconds"): (0, 5)
        }

    @classmethod
    def get_optional(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("del", "DeletionTime"): TestTimerModel.DELETION_TIME
        }

    def test_is_periodic(self):
        mdl = self.get_constructed_model()
        self.assertFalse(mdl.is_periodic)

        mdl = self.get_constructed_model(manual_default=True)
        self.assertTrue(mdl.is_periodic)

    def test_target_time_diff(self):
        mdl = self.get_constructed_model()

        self.assertEqual(mdl.get_target_time_diff(datetime(2020, 5, 6, 12).replace(tzinfo=timezone.utc)),
                         timedelta(days=1))
        self.assertEqual(mdl.get_target_time_diff(datetime(2020, 5, 8, 12).replace(tzinfo=timezone.utc)),
                         timedelta(days=1))
        self.assertEqual(mdl.get_target_time_diff(datetime(2020, 5, 7, 12).replace(tzinfo=timezone.utc)),
                         timedelta())

    def test_is_after(self):
        mdl = self.get_constructed_model()

        self.assertTrue(mdl.is_after(datetime(2020, 5, 6, 12).replace(tzinfo=timezone.utc)))
        self.assertTrue(mdl.is_after(datetime(2020, 5, 7, 12).replace(tzinfo=timezone.utc)))
        self.assertFalse(mdl.is_after(datetime(2020, 5, 8, 12).replace(tzinfo=timezone.utc)))


class TestTimerListResult(TestCase):
    CHANNEL_OID = ObjectId()

    TMR_1 = TimerModel(ChannelOid=CHANNEL_OID, Keyword="A", Title="D",
                       TargetTime=datetime.now() - timedelta(weeks=540))
    TMR_2 = TimerModel(ChannelOid=CHANNEL_OID, Keyword="A", Title="D",
                       TargetTime=datetime.now() - timedelta(weeks=520), Countup=True)
    TMR_3 = TimerModel(ChannelOid=CHANNEL_OID, Keyword="A", Title="D",
                       TargetTime=datetime.now() + timedelta(weeks=520))
    TMR_4 = TimerModel(ChannelOid=CHANNEL_OID, Keyword="A", Title="D",
                       TargetTime=datetime.now() + timedelta(weeks=540), Countup=True)

    @staticmethod
    def get_cursor():
        return [TestTimerListResult.TMR_1, TestTimerListResult.TMR_2,
                TestTimerListResult.TMR_3, TestTimerListResult.TMR_4]

    def get_data(self):
        return TimerListResult(self.get_cursor())

    @staticmethod
    def get_empty_data():
        return TimerListResult([])

    @staticmethod
    def get_user_model():
        return RootUserModel(ApiOid=ObjectId(), Config=RootUserConfigModel(Locale="Asia/Taipei"))

    def test_has_data(self):
        self.assertTrue(self.get_data().has_data)
        self.assertFalse(self.get_empty_data().has_data)

    def test_data_body(self):
        result = self.get_data()

        self.assertEqual(result.past_done, [TestTimerListResult.TMR_1])
        self.assertEqual(result.past_continue, [TestTimerListResult.TMR_2])
        self.assertEqual(result.future, [TestTimerListResult.TMR_3, TestTimerListResult.TMR_4])

    def test_data_get_item(self):
        result = self.get_data()

        self.assertEqual(result.get_item(0), TestTimerListResult.TMR_3)
        self.assertEqual(result.get_item(1), TestTimerListResult.TMR_4)
        self.assertEqual(result.get_item(2), TestTimerListResult.TMR_2)
        self.assertEqual(result.get_item(3), TestTimerListResult.TMR_1)

    def test_empty_data_body(self):
        result = self.get_empty_data()

        self.assertEqual(result.past_done, [])
        self.assertEqual(result.past_continue, [])
        self.assertEqual(result.future, [])

    def test_empty_to_string(self):
        actual_str = self.get_empty_data().to_string(self.get_user_model())
        self.assertEqual("", actual_str)

    def test_to_string(self):
        now = now_utc_aware()
        taipei_tzinfo = LocaleInfo.get_tzinfo("Asia/Taipei")

        actual_str = self.get_data().to_string(self.get_user_model())

        expected_str = [
            Timer.FUTURE.format(
                event=TestTimerListResult.TMR_3.title,
                diff=t_delta_str(TestTimerListResult.TMR_3.get_target_time_diff(now)),
                time=localtime(TestTimerListResult.TMR_3.target_time, taipei_tzinfo)
            ),
            Timer.FUTURE.format(
                event=TestTimerListResult.TMR_4.title,
                diff=t_delta_str(TestTimerListResult.TMR_4.get_target_time_diff(now)),
                time=localtime(TestTimerListResult.TMR_4.target_time, taipei_tzinfo)
            ),
            "",
            Timer.PAST_CONTINUE.format(
                event=TestTimerListResult.TMR_2.title,
                diff=t_delta_str(TestTimerListResult.TMR_2.get_target_time_diff(now)),
                time=localtime(TestTimerListResult.TMR_2.target_time, taipei_tzinfo)
            ),
            "",
            Timer.PAST_DONE.format(
                event=TestTimerListResult.TMR_1.title,
                diff=t_delta_str(TestTimerListResult.TMR_1.get_target_time_diff(now)),
                time=localtime(TestTimerListResult.TMR_1.target_time, taipei_tzinfo)
            )
        ]
        expected_str = "\n".join(expected_str)

        self.assertEqual(actual_str, expected_str)
