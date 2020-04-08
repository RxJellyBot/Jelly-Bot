from datetime import datetime, timedelta
from typing import Optional, List

import pymongo
from bson import ObjectId

from models import TimerModel, TimerListResult, OID_KEY
from mongodb.factory.results import WriteOutcome
from mongodb.utils import CursorWithCount
from extutils.checker import arg_type_ensure
from extutils.locales import UTC
from extutils.dt import is_tz_naive, now_utc_aware
from JellyBot.systemconfig import Bot

from ._base import BaseCollection

DB_NAME = "timer"


class TimerManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "timer"
    model_class = TimerModel

    def __init__(self):
        super().__init__()
        self.create_index(TimerModel.Keyword.key)
        self.create_index(TimerModel.DeletionTime.key, expireAfterSeconds=0)

    @arg_type_ensure
    def add_new_timer(
            self, ch_oid: ObjectId, keyword: str, title: str, target_time: datetime,
            countup: bool = False, period_sec: int = 0) -> WriteOutcome:
        """`target_time` is recommended to be tz-aware. Tzinfo will be forced to be UTC if tz-naive."""
        # Force target time to be tz-aware in UTC
        if is_tz_naive(target_time):
            target_time = target_time.replace(tzinfo=UTC.to_tzinfo())

        mdl = TimerModel(
            ChannelOid=ch_oid, Keyword=keyword, Title=title, TargetTime=target_time,
            Countup=countup, PeriodSeconds=period_sec)

        if not countup:
            mdl.deletion_time = target_time + timedelta(days=Bot.Timer.AutoDeletionDays)
            mdl.deletion_time = mdl.deletion_time.replace(tzinfo=target_time.tzinfo)

        outcome, ex = self.insert_one_model(mdl)

        return outcome

    @arg_type_ensure
    def del_timer(self, timer_oid: ObjectId) -> bool:
        return self.delete_one({OID_KEY: timer_oid}).deleted_count > 0

    @arg_type_ensure
    def list_all_timer(self, channel_oid: ObjectId) -> TimerListResult:
        return TimerListResult(
            self.find_cursor_with_count({TimerModel.ChannelOid.key: channel_oid}, parse_cls=TimerModel)
                .sort([(TimerModel.TargetTime.key, pymongo.ASCENDING)]))

    @arg_type_ensure
    def get_timers(self, channel_oid: ObjectId, keyword: str) -> TimerListResult:
        return TimerListResult(
            self.find_cursor_with_count({TimerModel.Keyword.key: keyword,
                                         TimerModel.ChannelOid.key: channel_oid}, parse_cls=TimerModel)
                .sort([(TimerModel.TargetTime.key, pymongo.ASCENDING)])
        )

    @arg_type_ensure
    def get_notify(self, channel_oid: ObjectId, within_secs: Optional[int] = None) -> List[TimerModel]:
        now = now_utc_aware()

        filter_ = {
            TimerModel.ChannelOid.key: channel_oid,
            TimerModel.TargetTime.key: {
                "$lt": now + timedelta(seconds=within_secs if within_secs else Bot.Timer.MaxNotifyRangeSeconds),
                "$gt": now
            },
            TimerModel.Notified.key: False
        }

        ret = list(
            self.find_cursor_with_count(
                filter_, parse_cls=TimerModel
            ).sort(
                [(TimerModel.TargetTime.key, pymongo.ASCENDING)]
            ))

        self.update_many_async(filter_, {"$set": {TimerModel.Notified.key: True}})

        return ret

    @arg_type_ensure
    def get_time_up(self, channel_oid: ObjectId) -> List[TimerModel]:
        now = now_utc_aware()

        filter_ = {
            TimerModel.ChannelOid.key: channel_oid,
            TimerModel.TargetTime.key: {"$lt": now},
            TimerModel.NotifiedExpired.key: False
        }

        ret = list(
            self.find_cursor_with_count(
                filter_, parse_cls=TimerModel
            ).sort(
                [(TimerModel.TargetTime.key, pymongo.ASCENDING)]
            ))

        self.update_many_async(filter_, {"$set": {TimerModel.NotifiedExpired.key: True}})

        return ret

    @staticmethod
    def get_notify_within_secs(message_frequency: float):
        return message_frequency * 13.5 + 495


_inst = TimerManager()
