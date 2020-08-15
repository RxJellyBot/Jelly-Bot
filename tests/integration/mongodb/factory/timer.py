from datetime import datetime, timedelta

from bson import ObjectId
import pytz

from extutils.dt import now_utc_aware
from extutils.locales import LocaleInfo
from JellyBot.systemconfig import Bot
from models import TimerModel
from mongodb.factory import TimerManager
from mongodb.factory.results import WriteOutcome
from tests.base import TestModelMixin, TestTimeComparisonMixin

__all__ = ["TestTimerManager"]


class TestTimerManager(TestModelMixin, TestTimeComparisonMixin):
    CHANNEL_OID = ObjectId()

    @staticmethod
    def obj_to_clear():
        return [TimerManager]

    def test_add_timer(self):
        tz_8 = LocaleInfo.get_tzinfo("Asia/Taipei")

        now = now_utc_aware(for_mongo=True)
        now_tz_8 = now.astimezone(tz_8)

        outcome = TimerManager.add_new_timer(
            TestTimerManager.CHANNEL_OID, "KEYWORD", "TITLE", now_tz_8
        )

        self.assertEqual(outcome, WriteOutcome.O_INSERTED)
        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.ChannelOid.key: TestTimerManager.CHANNEL_OID,
                TimerModel.Keyword.key: "KEYWORD",
                TimerModel.Title.key: "TITLE",
                TimerModel.TargetTime.key: now,
                TimerModel.PeriodSeconds.key: 0,
                TimerModel.Countup.key: False
            }),
            1
        )

    def test_add_timer_duplicate_content(self):
        tz_8 = LocaleInfo.get_tzinfo("Asia/Taipei")

        now = now_utc_aware(for_mongo=True)
        now_tz_8 = now.astimezone(tz_8)

        outcome = TimerManager.add_new_timer(TestTimerManager.CHANNEL_OID, "KEYWORD", "TITLE", now_tz_8)
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)
        outcome = TimerManager.add_new_timer(TestTimerManager.CHANNEL_OID, "KEYWORD", "TITLE", now_tz_8)
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.ChannelOid.key: TestTimerManager.CHANNEL_OID,
                TimerModel.Keyword.key: "KEYWORD",
                TimerModel.Title.key: "TITLE",
                TimerModel.TargetTime.key: now,
                TimerModel.PeriodSeconds.key: 0,
                TimerModel.Countup.key: False
            }),
            2
        )

    def test_add_timer_no_tz(self):
        timer_time = datetime.utcnow() + timedelta(hours=1)

        outcome = TimerManager.add_new_timer(
            TestTimerManager.CHANNEL_OID, "KEYWORD", "TITLE", timer_time
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)
        outcome = TimerManager.add_new_timer(
            TestTimerManager.CHANNEL_OID, "KEYWORD", "TITLE", timer_time
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.ChannelOid.key: TestTimerManager.CHANNEL_OID,
                TimerModel.Keyword.key: "KEYWORD",
                TimerModel.Title.key: "TITLE",
                TimerModel.TargetTime.key: pytz.utc.localize(timer_time),
                TimerModel.PeriodSeconds.key: 0,
                TimerModel.Countup.key: False
            }),
            2
        )

    def test_add_timer_countup(self):
        now = now_utc_aware(for_mongo=True)

        outcome = TimerManager.add_new_timer(
            TestTimerManager.CHANNEL_OID, "KEYWORD", "TITLE", now, countup=True
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.ChannelOid.key: TestTimerManager.CHANNEL_OID,
                TimerModel.Keyword.key: "KEYWORD",
                TimerModel.Title.key: "TITLE",
                TimerModel.TargetTime.key: now,
                TimerModel.PeriodSeconds.key: 0,
                TimerModel.Countup.key: True
            }),
            1
        )

    def test_add_timer_del_after_days(self):
        now = now_utc_aware(for_mongo=True)

        outcome = TimerManager.add_new_timer(
            TestTimerManager.CHANNEL_OID, "KEYWORD", "TITLE", now
        )

        self.assertEqual(outcome, WriteOutcome.O_INSERTED)
        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.ChannelOid.key: TestTimerManager.CHANNEL_OID,
                TimerModel.Keyword.key: "KEYWORD",
                TimerModel.Title.key: "TITLE",
                TimerModel.TargetTime.key: now,
                TimerModel.PeriodSeconds.key: 0,
                TimerModel.Countup.key: False,
                TimerModel.DeletionTime.key: now + timedelta(days=Bot.Timer.AutoDeletionDays)
            }),
            1
        )

    def test_del_timer(self):
        now = now_utc_aware(for_mongo=True)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="TITLE", TargetTime=now
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        oid = TimerManager.find_one_casted(parse_cls=TimerModel).id
        TimerManager.del_timer(oid)

    def test_del_timer_missed(self):
        now = now_utc_aware(for_mongo=True)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="TITLE", TargetTime=now
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        TimerManager.del_timer(ObjectId())

    def test_del_timer_no_data(self):
        TimerManager.del_timer(ObjectId())

    def test_list_all_timer(self):
        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="PAST",
                TargetTime=now_utc_aware(for_mongo=True) - timedelta(hours=1)
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="PAST_UP",
                TargetTime=now_utc_aware(for_mongo=True) - timedelta(hours=1), Countup=True
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="FUTURE",
                TargetTime=now_utc_aware(for_mongo=True) + timedelta(hours=1)
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        result = TimerManager.list_all_timer(TestTimerManager.CHANNEL_OID)
        self.assertTrue(result.has_data)

        self.assertEqual(len(result.past_continue), 1)
        self.assertEqual(result.past_continue[0].title, "PAST_UP")
        self.assertEqual(len(result.past_done), 1)
        self.assertEqual(result.past_done[0].title, "PAST")
        self.assertEqual(len(result.future), 1)
        self.assertEqual(result.future[0].title, "FUTURE")

    def test_list_all_timer_has_duplicated(self):
        timer_time = now_utc_aware(for_mongo=True) - timedelta(hours=1)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="PAST", TargetTime=timer_time
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="PAST", TargetTime=timer_time
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        result = TimerManager.list_all_timer(TestTimerManager.CHANNEL_OID)
        self.assertTrue(result.has_data)

        self.assertEqual(len(result.past_continue), 0)
        self.assertEqual(len(result.past_done), 2)
        self.assertEqual(result.past_done[0].title, "PAST")
        self.assertEqual(result.past_done[1].title, "PAST")
        self.assertModelEqual(result.past_done[0], result.past_done[1])
        self.assertEqual(len(result.future), 0)

    def test_list_all_timer_channel_miss(self):
        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="PAST",
                TargetTime=now_utc_aware(for_mongo=True) - timedelta(hours=1)
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="PAST_UP",
                TargetTime=now_utc_aware(for_mongo=True) - timedelta(hours=1), Countup=True
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="FUTURE",
                TargetTime=now_utc_aware(for_mongo=True) + timedelta(hours=1)
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        result = TimerManager.list_all_timer(ObjectId())
        self.assertFalse(result.has_data)

        self.assertEqual(len(result.past_continue), 0)
        self.assertEqual(len(result.past_done), 0)
        self.assertEqual(len(result.future), 0)

    def test_list_all_timer_no_data(self):
        result = TimerManager.list_all_timer(ObjectId())
        self.assertFalse(result.has_data)

        self.assertEqual(len(result.past_continue), 0)
        self.assertEqual(len(result.past_done), 0)
        self.assertEqual(len(result.future), 0)

    def test_get_timers(self):
        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="PAST",
                TargetTime=now_utc_aware(for_mongo=True) - timedelta(hours=1)
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD_2", Title="PAST_UP",
                TargetTime=now_utc_aware(for_mongo=True) - timedelta(hours=1), Countup=True
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="FUTURE",
                TargetTime=now_utc_aware(for_mongo=True) + timedelta(hours=1)
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        result = TimerManager.get_timers(TestTimerManager.CHANNEL_OID, "KEYWORD")
        self.assertTrue(result.has_data)

        self.assertEqual(len(result.past_continue), 0)
        self.assertEqual(len(result.past_done), 1)
        self.assertEqual(result.past_done[0].title, "PAST")
        self.assertEqual(len(result.future), 1)
        self.assertEqual(result.future[0].title, "FUTURE")

    def test_get_timers_duplicated(self):
        past_time = now_utc_aware(for_mongo=True) - timedelta(hours=1)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="PAST", TargetTime=past_time
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="PAST", TargetTime=past_time
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD_2", Title="PAST_UP",
                TargetTime=past_time, Countup=True
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="FUTURE",
                TargetTime=now_utc_aware(for_mongo=True) + timedelta(hours=1)
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        result = TimerManager.get_timers(TestTimerManager.CHANNEL_OID, "KEYWORD")
        self.assertTrue(result.has_data)

        self.assertEqual(len(result.past_continue), 0)
        self.assertEqual(len(result.past_done), 2)
        self.assertEqual(result.past_done[0].title, "PAST")
        self.assertEqual(result.past_done[1].title, "PAST")
        self.assertModelEqual(result.past_done[0], result.past_done[1])
        self.assertEqual(len(result.future), 1)
        self.assertEqual(result.future[0].title, "FUTURE")

    def test_get_timers_channel_miss(self):
        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="PAST",
                TargetTime=now_utc_aware(for_mongo=True) - timedelta(hours=1)
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="PAST_UP",
                TargetTime=now_utc_aware(for_mongo=True) - timedelta(hours=1), Countup=True
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="FUTURE",
                TargetTime=now_utc_aware(for_mongo=True) + timedelta(hours=1)
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        result = TimerManager.get_timers(ObjectId(), "KEYWORD")
        self.assertFalse(result.has_data)

        self.assertEqual(len(result.past_continue), 0)
        self.assertEqual(len(result.past_done), 0)
        self.assertEqual(len(result.future), 0)

    def test_get_timers_keyword_miss(self):
        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="PAST",
                TargetTime=now_utc_aware(for_mongo=True) - timedelta(hours=1)
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="PAST_UP",
                TargetTime=now_utc_aware(for_mongo=True) - timedelta(hours=1), Countup=True
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="FUTURE",
                TargetTime=now_utc_aware(for_mongo=True) + timedelta(hours=1)
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        result = TimerManager.get_timers(TestTimerManager.CHANNEL_OID, "KW")
        self.assertFalse(result.has_data)

        self.assertEqual(len(result.past_continue), 0)
        self.assertEqual(len(result.past_done), 0)
        self.assertEqual(len(result.future), 0)

    def test_get_timers_no_data(self):
        result = TimerManager.get_timers(TestTimerManager.CHANNEL_OID, "KW")
        self.assertFalse(result.has_data)

        self.assertEqual(len(result.past_continue), 0)
        self.assertEqual(len(result.past_done), 0)
        self.assertEqual(len(result.future), 0)

    def test_get_notify(self):
        timer_time = now_utc_aware(for_mongo=True) + timedelta(seconds=590)
        timer_time_2 = now_utc_aware(for_mongo=True) + timedelta(seconds=1200)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="FUTURE",
                TargetTime=timer_time
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="FUTURE_2",
                TargetTime=timer_time_2
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.Title.key: "FUTURE",
                TimerModel.Notified.key: True
            }),
            0
        )

        result = TimerManager.get_notify(TestTimerManager.CHANNEL_OID, 600)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "FUTURE")
        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.Title.key: "FUTURE",
                TimerModel.Notified.key: True
            }),
            1
        )

    def test_get_notify_no_secs(self):
        timer_time = now_utc_aware(for_mongo=True) + timedelta(seconds=Bot.Timer.MaxNotifyRangeSeconds - 10)
        timer_time_2 = now_utc_aware(for_mongo=True) + timedelta(seconds=Bot.Timer.MaxNotifyRangeSeconds * 2)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="FUTURE",
                TargetTime=timer_time
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="FUTURE_2",
                TargetTime=timer_time_2
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.Title.key: "FUTURE",
                TimerModel.Notified.key: True
            }),
            0
        )

        result = TimerManager.get_notify(TestTimerManager.CHANNEL_OID)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "FUTURE")
        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.Title.key: "FUTURE",
                TimerModel.Notified.key: True
            }),
            1
        )

    def test_get_notify_multiple(self):
        timer_time = now_utc_aware(for_mongo=True) + timedelta(seconds=590)
        timer_time_2 = now_utc_aware(for_mongo=True) + timedelta(seconds=500)
        timer_time_3 = now_utc_aware(for_mongo=True) + timedelta(seconds=550)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="FUTURE",
                TargetTime=timer_time
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="FUTURE_2",
                TargetTime=timer_time_2
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="FUTURE_3",
                TargetTime=timer_time_3
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.Title.key: {"$in": ["FUTURE", "FUTURE_2", "FUTURE_3"]},
                TimerModel.Notified.key: True
            }),
            0
        )

        result = TimerManager.get_notify(TestTimerManager.CHANNEL_OID)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].title, "FUTURE_2")
        self.assertEqual(result[1].title, "FUTURE_3")
        self.assertEqual(result[2].title, "FUTURE")
        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.Title.key: {"$in": ["FUTURE", "FUTURE_2", "FUTURE_3"]},
                TimerModel.Notified.key: True
            }),
            3
        )

    def test_get_notify_no_renotify(self):
        timer_time = now_utc_aware(for_mongo=True) + timedelta(seconds=590)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="FUTURE",
                TargetTime=timer_time
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.Title.key: "FUTURE",
                TimerModel.Notified.key: True
            }),
            0
        )

        result = TimerManager.get_notify(TestTimerManager.CHANNEL_OID, 600)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "FUTURE")
        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.Title.key: "FUTURE",
                TimerModel.Notified.key: True
            }),
            1
        )

        result = TimerManager.get_notify(TestTimerManager.CHANNEL_OID, 600)

        self.assertEqual(len(result), 0)
        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.Title.key: "FUTURE",
                TimerModel.Notified.key: True
            }),
            1
        )

    def test_get_notify_longer_than_config(self):
        timer_time = now_utc_aware(for_mongo=True) + timedelta(seconds=Bot.Timer.MaxNotifyRangeSeconds)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="FUTURE",
                TargetTime=timer_time
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.Title.key: "FUTURE",
                TimerModel.Notified.key: True
            }),
            0
        )

        result = TimerManager.get_notify(TestTimerManager.CHANNEL_OID, Bot.Timer.MaxNotifyRangeSeconds * 2)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "FUTURE")
        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.Title.key: "FUTURE",
                TimerModel.Notified.key: True
            }),
            1
        )

    def test_get_notify_channel_miss(self):
        timer_time = now_utc_aware(for_mongo=True) + timedelta(seconds=580)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="FUTURE",
                TargetTime=timer_time
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.Title.key: "FUTURE",
                TimerModel.Notified.key: True
            }),
            0
        )

        result = TimerManager.get_notify(ObjectId(), 600)

        self.assertEqual(len(result), 0)
        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.Title.key: "FUTURE",
                TimerModel.Notified.key: True
            }),
            0
        )

    def test_get_notify_no_data(self):
        result = TimerManager.get_notify(ObjectId(), 600)

        self.assertEqual(len(result), 0)

    def test_get_time_up(self):
        timer_time = now_utc_aware(for_mongo=True) - timedelta(seconds=10)
        timer_time_2 = now_utc_aware(for_mongo=True) + timedelta(seconds=600)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="PAST",
                TargetTime=timer_time
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="FUTURE",
                TargetTime=timer_time_2
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.Title.key: "PAST",
                TimerModel.NotifiedExpired.key: True
            }),
            0
        )

        result = TimerManager.get_time_up(TestTimerManager.CHANNEL_OID)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "PAST")
        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.Title.key: "PAST",
                TimerModel.NotifiedExpired.key: True
            }),
            1
        )

    def test_get_time_up_multiple(self):
        timer_time = now_utc_aware(for_mongo=True) - timedelta(seconds=10)
        timer_time_2 = now_utc_aware(for_mongo=True) + timedelta(seconds=600)
        timer_time_3 = now_utc_aware(for_mongo=True) - timedelta(seconds=600)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="PAST",
                TargetTime=timer_time
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="FUTURE",
                TargetTime=timer_time_2
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="PAST_3",
                TargetTime=timer_time_3
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.Title.key: {"$in": ["PAST", "PAST_3"]},
                TimerModel.Notified.key: True
            }),
            0
        )

        result = TimerManager.get_time_up(TestTimerManager.CHANNEL_OID)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].title, "PAST_3")
        self.assertEqual(result[1].title, "PAST")
        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.Title.key: {"$in": ["PAST", "PAST_3"]},
                TimerModel.NotifiedExpired.key: True
            }),
            2
        )

    def test_get_time_up_no_renotify(self):
        timer_time = now_utc_aware(for_mongo=True) - timedelta(seconds=10)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="PAST",
                TargetTime=timer_time
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.Title.key: "PAST",
                TimerModel.NotifiedExpired.key: True
            }),
            0
        )

        result = TimerManager.get_time_up(TestTimerManager.CHANNEL_OID)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "PAST")
        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.Title.key: "PAST",
                TimerModel.NotifiedExpired.key: True
            }),
            1
        )

        result = TimerManager.get_time_up(TestTimerManager.CHANNEL_OID)

        self.assertEqual(len(result), 0)
        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.Title.key: "PAST",
                TimerModel.NotifiedExpired.key: True
            }),
            1
        )

    def test_get_time_up_channel_miss(self):
        timer_time = now_utc_aware(for_mongo=True) - timedelta(seconds=10)

        outcome, ex = TimerManager.insert_one_model(
            TimerModel(
                ChannelOid=TestTimerManager.CHANNEL_OID, Keyword="KEYWORD", Title="PAST",
                TargetTime=timer_time
            )
        )
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)

        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.Title.key: "PAST",
                TimerModel.NotifiedExpired.key: True
            }),
            0
        )

        result = TimerManager.get_time_up(ObjectId())

        self.assertEqual(len(result), 0)
        self.assertEqual(
            TimerManager.count_documents({
                TimerModel.Title.key: "PAST",
                TimerModel.NotifiedExpired.key: True
            }),
            0
        )

    def test_get_time_up_no_data(self):
        result = TimerManager.get_time_up(ObjectId())

        self.assertEqual(len(result), 0)

    def test_get_notify_within_secs(self):
        self.assertEqual(TimerManager.get_notify_within_secs(0), 600)
        self.assertEqual(TimerManager.get_notify_within_secs(9999999), Bot.Timer.MaxNotifyRangeSeconds)
