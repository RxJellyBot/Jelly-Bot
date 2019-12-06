from datetime import datetime, timedelta

import pymongo
from bson import ObjectId

from models import TimerModel, TimerListResult
from mongodb.factory.results import WriteOutcome
from mongodb.utils import CursorWithCount
from extutils.checker import param_type_ensure
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
        self.create_index(TimerModel.KeywordOid.key)
        self.create_index(TimerModel.DeletionTime.key, expireAfterSeconds=0)

    @param_type_ensure
    def add_new_timer(
            self, ch_oid: ObjectId, kw_oid: ObjectId, title: str, target_time: datetime,
            countup: bool = False, period_sec: int = 0) -> WriteOutcome:
        """`target_time` is recommended to be tz-aware. Tzinfo will be forced to be UTC if tz-naive."""
        # Force target time to be tz-aware in UTC
        if is_tz_naive(target_time):
            target_time = target_time.replace(tzinfo=UTC.to_tzinfo())

        mdl = TimerModel(
            ChannelOid=ch_oid, KeywordOid=kw_oid, Title=title, TargetTime=target_time,
            Countup=countup, PeriodSeconds=period_sec)

        if not countup:
            mdl.deletion_time = target_time + timedelta(days=Bot.Timer.AutoDeletionDays)
            mdl.deletion_time = mdl.deletion_time.replace(tzinfo=target_time.tzinfo)

        outcome, ex = self.insert_one_model(mdl)

        return outcome

    @param_type_ensure
    def list_all_timer(self, channel_oid: ObjectId) -> TimerListResult:
        return TimerListResult(
            self.find_cursor_with_count({TimerModel.ChannelOid.key: channel_oid}, parse_cls=TimerModel)
                .sort([(TimerModel.TargetTime.key, pymongo.ASCENDING)]))

    @param_type_ensure
    def get_timer(self, channel_oid: ObjectId, kw_oid: ObjectId) -> TimerListResult:
        return TimerListResult(
            self.find_cursor_with_count({TimerModel.KeywordOid.key: kw_oid,
                                         TimerModel.ChannelOid.key: channel_oid}, parse_cls=TimerModel)
                .sort([(TimerModel.TargetTime.key, pymongo.ASCENDING)])
        )

    @param_type_ensure
    def get_notify(self, channel_oid: ObjectId) -> CursorWithCount:
        now = now_utc_aware()

        filter_ = {
            TimerModel.ChannelOid.key: channel_oid,
            TimerModel.TargetTime.key: {"$lt": now + timedelta(hours=Bot.Timer.NotifyWithinHours),
                                        "$gt": now},
            TimerModel.Notified.key: False
        }

        ret = self \
            .find_cursor_with_count(filter_, parse_cls=TimerModel)\
            .sort([(TimerModel.TargetTime.key, pymongo.ASCENDING)])

        self.update_many_async(filter_, {"$set": {TimerModel.Notified.key: True}})

        return ret


_inst = TimerManager()
