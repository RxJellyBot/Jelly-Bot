from datetime import datetime, tzinfo, timedelta
from threading import Thread
from typing import Any, Optional, Union, List, Dict, Set

import pymongo
from bson import ObjectId

from JellyBot.systemconfig import Database
from extutils import dt_to_objectid
from extutils.checker import arg_type_ensure
from extutils.dt import now_utc_aware, localtime, TimeRange
from extutils.locales import UTC, PytzInfo
from flags import APICommand, MessageType, BotFeature
from models import (
    APIStatisticModel, MessageRecordModel, OID_KEY, BotFeatureUsageModel,
    HourlyIntervalAverageMessageResult, DailyMessageResult, BotFeatureUsageResult, BotFeatureHourlyAvgResult,
    HourlyResult, BotFeaturePerUserUsageResult, MemberMessageByCategoryResult, MemberDailyMessageResult,
    MemberMessageCountResult, MeanMessageResultGenerator, CountBeforeTimeResult
)
from mongodb.factory.results import RecordAPIStatisticsResult, WriteOutcome
from mongodb.utils import ExtendedCursor
from ._base import BaseCollection

__all__ = ["APIStatisticsManager", "MessageRecordStatisticsManager", "BotFeatureUsageDataManager"]

DB_NAME = "stats"


class _APIStatisticsManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "api"
    model_class = APIStatisticModel

    @arg_type_ensure
    def record_stats(self, api_action: APICommand, sender_oid: ObjectId, parameter: dict, response: dict,
                     success: bool, org_param: dict, path_info: str, path_info_full: str) -> RecordAPIStatisticsResult:
        entry, outcome, ex = self.insert_one_data(
            ApiAction=api_action, SenderOid=sender_oid, Parameter=parameter, Response=response, Success=success,
            Timestamp=datetime.utcnow(), PathInfo=path_info, PathInfoFull=path_info_full, PathParameter=org_param)

        return RecordAPIStatisticsResult(outcome, ex, entry)


class _MessageRecordStatisticsManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "msg"
    model_class = MessageRecordModel

    @arg_type_ensure
    def record_message_async(
            self, channel_oid: ObjectId, user_root_oid: ObjectId,
            message_type: MessageType, message_content: Any, proc_time_secs: float):
        Thread(
            target=self.record_message,
            args=(channel_oid, user_root_oid, message_type, message_content, proc_time_secs)).start()

    @arg_type_ensure
    def record_message(
            self, channel_oid: ObjectId, user_root_oid: ObjectId,
            message_type: MessageType, message_content: Any, proc_time_secs: float) -> WriteOutcome:
        mdl, outcome, ex = self.insert_one_data(
            ChannelOid=channel_oid, UserRootOid=user_root_oid, MessageType=message_type,
            MessageContent=str(message_content)[:Database.MessageStats.MaxContentCharacter],
            ProcessTimeSecs=proc_time_secs
        )

        return outcome

    @arg_type_ensure
    def get_recent_messages(self, channel_oid: ObjectId, limit: Optional[int] = None) \
            -> ExtendedCursor[MessageRecordModel]:
        return self.find_cursor_with_count(
            {MessageRecordModel.ChannelOid.key: channel_oid}, parse_cls=MessageRecordModel
        ).sort([(OID_KEY, pymongo.DESCENDING)]).limit(limit)

    @arg_type_ensure
    def get_message_frequency(self, channel_oid: ObjectId, range_mins: Union[float, int, None] = None) -> float:
        """
        Get the message frequency in terms of seconds per message.

        The calculation is based on the earliest and the latest time of the record.

        If ``within_mins`` is specified, then it will be applied to the filter to get the data,
        counting backwards from the current datetime.

        :param channel_oid: message of the channel
        :param range_mins: time range in minutes for the calculation
        :return: sec / message
        """
        filter_ = {MessageRecordModel.ChannelOid.key: channel_oid}

        if range_mins:
            filter_[OID_KEY] = {"$gt": ObjectId.from_datetime(now_utc_aware() - timedelta(minutes=range_mins))}

        rct_msg_count = self.count_documents(filter_)

        # Early termination if no message
        if rct_msg_count == 0:
            return 0.0

        # Calculate time range
        earliest = self.find_one(filter_, sort=[(OID_KEY, pymongo.ASCENDING)])
        if not earliest:
            return 0.0

        latest = self.find_one(filter_, sort=[(OID_KEY, pymongo.DESCENDING)])

        range_mins = (latest[OID_KEY].generation_time - earliest[OID_KEY].generation_time).total_seconds() / 60

        return range_mins / rct_msg_count

    def get_user_last_message_ts(self, channel_oid: ObjectId, user_oids: List[ObjectId], tzinfo_: tzinfo = None) \
            -> Dict[ObjectId, datetime]:
        ret = {}
        KEY_TS = "msgts"

        pipeline = [
            {"$match": {
                MessageRecordModel.ChannelOid.key: channel_oid,
                MessageRecordModel.UserRootOid.key: {"$in": user_oids}
            }},
            {"$sort": {
                "_id": pymongo.DESCENDING
            }},
            {"$group": {
                "_id": "$" + MessageRecordModel.UserRootOid.key,
                KEY_TS: {"$first": "$" + OID_KEY}
            }}
        ]
        for data in self.aggregate(pipeline):
            ret[data[OID_KEY]] = localtime(data[KEY_TS].generation_time, tzinfo_)

        return ret

    # Statistics

    @staticmethod
    def _channel_oids_filter(channel_oids: Union[ObjectId, List[ObjectId]]):
        if isinstance(channel_oids, ObjectId):
            return {MessageRecordModel.ChannelOid.key: channel_oids}
        elif isinstance(channel_oids, list):
            return {MessageRecordModel.ChannelOid.key: {"$in": channel_oids}}
        else:
            raise ValueError("Must be either `ObjectId` or `List[ObjectId]`.")

    def get_messages_distinct_channel(self, message_fragment: str) -> Set[ObjectId]:
        aggr = list(self.aggregate([
            {"$match": {
                MessageRecordModel.MessageContent.key: {"$regex": message_fragment, "$options": "i"}
            }},
            {"$group": {
                OID_KEY: None,
                "cid": {"$addToSet": "$" + MessageRecordModel.ChannelOid.key}
            }},
            {"$unwind": "$cid"},
            {"$project": {
                OID_KEY: 0
            }}
        ]))

        return {e["cid"] for e in aggr}

    def get_user_messages_total_count(
            self, channel_oids: Union[ObjectId, List[ObjectId]], *, hours_within: Optional[int] = None,
            start: Optional[datetime] = None, end: Optional[datetime] = None, period_count: int = 3,
            tzinfo_: Optional[tzinfo] = None) \
            -> MemberMessageCountResult:
        match_d = self._channel_oids_filter(channel_oids)
        trange = TimeRange(range_hr=hours_within, start=start, end=end, range_mult=period_count, tzinfo_=tzinfo_)

        self.attach_time_range(match_d, trange=trange)

        # $switch expression for time range
        switch_branches = []

        # Check for full range (inf)
        # `start` and `end` cannot be `None` for generating `ObjectId`,
        # however `start` and `end` for full range are `None`.
        if not trange.is_inf:
            for idx, range_ in enumerate(trange.get_periods()):
                start_id = dt_to_objectid(range_.start)
                if not start_id:
                    continue
                end_id = dt_to_objectid(range_.end)
                if not end_id:
                    continue

                switch_branches.append(
                    {"case": {"$and": [{"$gte": ["$" + OID_KEY, start_id]},
                                       {"$lt": ["$" + OID_KEY, end_id]}]},
                     "then": str(idx)}
                )

        group_key = {MemberMessageCountResult.KEY_MEMBER_ID: "$" + MessageRecordModel.UserRootOid.key}
        if switch_branches:
            group_key[MemberMessageCountResult.KEY_INTERVAL_IDX] = {
                "$switch": {
                    "branches": switch_branches,

                    # Set `default` to the highest index to handle the only missed case because of `low <= x < high`
                    # where `high` is inclusive for the function but not handled
                    "default": str(len(trange.get_periods()) - 1)
                }
            }

        aggr_pipeline = [
            {"$match": match_d},
            {"$group": {
                OID_KEY: group_key,
                MemberMessageCountResult.KEY_COUNT: {"$sum": 1}
            }}
        ]

        return MemberMessageCountResult(list(self.aggregate(aggr_pipeline)), period_count, trange)

    def get_user_messages_by_category(
            self, channel_oids: Union[ObjectId, List[ObjectId]], *, hours_within: Optional[int] = None,
            start: Optional[datetime] = None, end: Optional[datetime] = None, tzinfo_: Optional[tzinfo] = None) \
            -> MemberMessageByCategoryResult:
        match_d = self._channel_oids_filter(channel_oids)
        self.attach_time_range(match_d, hours_within=hours_within, start=start, end=end, tzinfo_=tzinfo_)

        aggr_pipeline = [
            {"$match": match_d},
            {"$group": {
                OID_KEY: {
                    MemberMessageByCategoryResult.KEY_MEMBER_ID: "$" + MessageRecordModel.UserRootOid.key,
                    MemberMessageByCategoryResult.KEY_CATEGORY: "$" + MessageRecordModel.MessageType.key
                },
                MemberMessageByCategoryResult.KEY_COUNT: {"$sum": 1}
            }}
        ]

        return MemberMessageByCategoryResult(list(self.aggregate(aggr_pipeline)))

    def hourly_interval_message_count(
            self, channel_oids: Union[ObjectId, List[ObjectId]], *,
            tzinfo_: PytzInfo = UTC.to_tzinfo(), hours_within: Optional[int] = None,
            start: Optional[datetime] = None, end: Optional[datetime] = None) -> \
            HourlyIntervalAverageMessageResult:
        match_d = self._channel_oids_filter(channel_oids)
        self.attach_time_range(match_d, hours_within=hours_within, start=start, end=end, tzinfo_=tzinfo_)

        pipeline = [
            {"$match": match_d},
            {"$group": {
                "_id": {
                    HourlyIntervalAverageMessageResult.KEY_HR:
                        {"$hour": {"date": "$_id", "timezone": tzinfo_.tzidentifier}},
                    HourlyIntervalAverageMessageResult.KEY_CATEGORY:
                        "$" + MessageRecordModel.MessageType.key
                },
                HourlyIntervalAverageMessageResult.KEY_COUNT: {"$sum": 1}
            }},
            {"$sort": {"_id": pymongo.ASCENDING}}
        ]

        return HourlyIntervalAverageMessageResult(
            list(self.aggregate(pipeline)),
            HourlyResult.data_days_collected(self, match_d, hr_range=hours_within, start=start, end=end),
            end_time=end
        )

    def daily_message_count(
            self, channel_oids: Union[ObjectId, List[ObjectId]], *,
            tzinfo_: PytzInfo = UTC.to_tzinfo(), hours_within: Optional[int] = None,
            start: Optional[datetime] = None, end: Optional[datetime] = None) -> \
            DailyMessageResult:
        match_d = self._channel_oids_filter(channel_oids)
        self.attach_time_range(match_d, hours_within=hours_within, start=start, end=end, tzinfo_=tzinfo_)
        pipeline = [
            {"$match": match_d},
            {"$group": {
                "_id": {
                    DailyMessageResult.KEY_DATE: {
                        "$dateToString": {
                            "date": "$_id",
                            "format": DailyMessageResult.FMT_DATE,
                            "timezone": tzinfo_.tzidentifier
                        }
                    },
                    DailyMessageResult.KEY_HOUR: {
                        "$hour": {
                            "date": "$_id",
                            "timezone": tzinfo_.tzidentifier
                        }
                    }
                },
                DailyMessageResult.KEY_COUNT: {"$sum": 1}
            }},
            {"$sort": {"_id": pymongo.ASCENDING}}
        ]

        return DailyMessageResult(
            list(self.aggregate(pipeline)),
            HourlyResult.data_days_collected(self, match_d, hr_range=hours_within, start=start, end=end),
            tzinfo_,
            start=start, end=end)

    def mean_message_count(
            self, channel_oids: Union[ObjectId, List[ObjectId]], *,
            tzinfo_: PytzInfo = UTC.to_tzinfo(), hours_within: Optional[int] = None,
            start: Optional[datetime] = None, end: Optional[datetime] = None,
            max_mean_days: int = 5) -> \
            MeanMessageResultGenerator:
        match_d = self._channel_oids_filter(channel_oids)

        trange = TimeRange(range_hr=hours_within, start=start, end=end, tzinfo_=tzinfo_)
        # Pushing back the starting time to calculate the mean data at `start`.
        trange.set_start_day_offset(-max_mean_days)

        self.attach_time_range(match_d, trange=trange)

        pipeline = [
            {"$match": match_d},
            {"$group": {
                "_id": {
                    MeanMessageResultGenerator.KEY_DATE: {
                        "$dateToString": {
                            "date": "$_id",
                            "format": MeanMessageResultGenerator.FMT_DATE,
                            "timezone": tzinfo_.tzidentifier
                        }
                    }
                },
                MeanMessageResultGenerator.KEY_COUNT: {"$sum": 1}
            }},
            {"$sort": {"_id": pymongo.ASCENDING}}
        ]

        return MeanMessageResultGenerator(
            list(self.aggregate(pipeline)),
            HourlyResult.data_days_collected(self, match_d, hr_range=hours_within, start=trange.start_org, end=end),
            tzinfo_,
            trange=trange, max_mean_days=max_mean_days)

    def message_count_before_time(
            self, channel_oids: Union[ObjectId, List[ObjectId]], *,
            tzinfo_: PytzInfo = UTC.to_tzinfo(), hours_within: Optional[int] = None,
            start: Optional[datetime] = None, end: Optional[datetime] = None) -> \
            CountBeforeTimeResult:
        match_d = self._channel_oids_filter(channel_oids)

        trange = TimeRange(range_hr=hours_within, start=start, end=end, tzinfo_=tzinfo_)

        self.attach_time_range(match_d, trange=trange)

        pipeline = [
            {"$match": match_d},
            {"$project": {
                CountBeforeTimeResult.KEY_SEC_OF_DAY: {
                    "$add": [
                        {"$multiply": [{"$hour": {"date": "$_id", "timezone": tzinfo_.tzidentifier}}, 3600]},
                        {"$multiply": [{"$minute": {"date": "$_id", "timezone": tzinfo_.tzidentifier}}, 60]},
                        {"$second": {"date": "$_id", "timezone": tzinfo_.tzidentifier}}
                    ]
                }
            }},
            {"$match": {
                CountBeforeTimeResult.KEY_SEC_OF_DAY: {"$lt": trange.end_time_seconds}
            }},
            {"$group": {
                "_id": {
                    CountBeforeTimeResult.KEY_DATE: {
                        "$dateToString": {
                            "date": "$_id",
                            "format": CountBeforeTimeResult.FMT_DATE,
                            "timezone": tzinfo_.tzidentifier
                        }
                    }
                },
                CountBeforeTimeResult.KEY_COUNT: {"$sum": 1}
            }},
            {"$sort": {"_id": pymongo.ASCENDING}}
        ]

        return CountBeforeTimeResult(
            list(self.aggregate(pipeline)),
            HourlyResult.data_days_collected(self, match_d, hr_range=hours_within, start=trange.start_org, end=end),
            tzinfo_,
            trange=trange)

    def member_daily_message_count(
            self, channel_oids: Union[ObjectId, List[ObjectId]], *,
            tzinfo_: PytzInfo = UTC.to_tzinfo(), hours_within: Optional[int] = None,
            start: Optional[datetime] = None, end: Optional[datetime] = None) -> \
            MemberDailyMessageResult:
        match_d = self._channel_oids_filter(channel_oids)

        trange = TimeRange(range_hr=hours_within, start=start, end=end, tzinfo_=tzinfo_)

        self.attach_time_range(match_d, trange=trange)

        pipeline = [
            {"$match": match_d},
            {"$group": {
                "_id": {
                    MemberDailyMessageResult.KEY_DATE: {
                        "$dateToString": {
                            "date": "$_id",
                            "format": MemberDailyMessageResult.FMT_DATE,
                            "timezone": tzinfo_.tzidentifier
                        }
                    },
                    MemberDailyMessageResult.KEY_MEMBER: "$" + MessageRecordModel.UserRootOid.key
                },
                MemberDailyMessageResult.KEY_COUNT: {"$sum": 1}
            }}
        ]

        return MemberDailyMessageResult(
            list(self.aggregate(pipeline)),
            HourlyResult.data_days_collected(self, match_d, hr_range=hours_within, start=start, end=end),
            tzinfo_,
            trange=trange)


class _BotFeatureUsageDataManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "bot"
    model_class = BotFeatureUsageModel

    @arg_type_ensure
    def record_usage_async(self, feature_used: BotFeature, channel_oid: ObjectId, root_oid: ObjectId):
        Thread(target=self.record_usage, args=(feature_used, channel_oid, root_oid)).start()

    @arg_type_ensure
    def record_usage(self, feature_used: BotFeature, channel_oid: ObjectId, root_oid: ObjectId):
        if feature_used != BotFeature.UNDEFINED:
            self.insert_one_data(Feature=feature_used, ChannelOid=channel_oid, SenderRootOid=root_oid)

    # Statistics

    @arg_type_ensure
    def get_channel_usage(
            self, channel_oid: ObjectId, *, hours_within: int = None, incl_not_used: bool = False) \
            -> BotFeatureUsageResult:
        filter_ = {BotFeatureUsageModel.ChannelOid.key: channel_oid}

        self.attach_time_range(filter_, hours_within=hours_within)

        pipeline = [
            {"$match": filter_},
            {"$group": {
                OID_KEY: "$" + BotFeatureUsageModel.Feature.key,
                BotFeatureUsageResult.KEY: {"$sum": 1}
            }},
            {"$sort": {BotFeatureUsageResult.KEY: pymongo.DESCENDING}}
        ]

        return BotFeatureUsageResult(list(self.aggregate(pipeline)), incl_not_used)

    @arg_type_ensure
    def get_channel_hourly_avg(
            self, channel_oid: ObjectId, *, hours_within: int = None, incl_not_used: bool = False,
            tzinfo_: PytzInfo = UTC.to_tzinfo()) -> BotFeatureHourlyAvgResult:
        filter_ = {BotFeatureUsageModel.ChannelOid.key: channel_oid}

        self.attach_time_range(filter_, hours_within=hours_within)

        pipeline = [
            {"$match": filter_},
            {"$group": {
                OID_KEY: {
                    BotFeatureHourlyAvgResult.KEY_FEATURE:
                        "$" + BotFeatureUsageModel.Feature.key,
                    BotFeatureHourlyAvgResult.KEY_HR:
                        {"$hour": {"date": "$_id", "timezone": tzinfo_.tzidentifier}}
                },
                BotFeatureHourlyAvgResult.KEY_COUNT: {"$sum": 1}
            }}
        ]

        return BotFeatureHourlyAvgResult(
            list(self.aggregate(pipeline)),
            incl_not_used,
            HourlyResult.data_days_collected(self, filter_, hr_range=hours_within))

    @arg_type_ensure
    def get_channel_per_user_usage(
            self, channel_oid: ObjectId, *, hours_within: int = None,
            member_oid_list: Optional[List[ObjectId]] = None) \
            -> BotFeaturePerUserUsageResult:
        filter_ = {BotFeatureUsageModel.ChannelOid.key: channel_oid}

        if member_oid_list:
            filter_[BotFeatureUsageModel.SenderRootOid.key] = {"$in": member_oid_list}

        self.attach_time_range(filter_, hours_within=hours_within)

        pipeline = [
            {"$match": filter_},
            {"$group": {
                OID_KEY: {
                    BotFeaturePerUserUsageResult.KEY_FEATURE:
                        "$" + BotFeatureUsageModel.Feature.key,
                    BotFeaturePerUserUsageResult.KEY_UID:
                        "$" + BotFeatureUsageModel.SenderRootOid.key
                },
                BotFeaturePerUserUsageResult.KEY_COUNT: {"$sum": 1}
            }},
            {"$sort": {
                f"{OID_KEY}.{BotFeaturePerUserUsageResult.KEY_UID}": pymongo.ASCENDING,
                f"{OID_KEY}.{BotFeaturePerUserUsageResult.KEY_FEATURE}": pymongo.ASCENDING
            }}
        ]

        return BotFeaturePerUserUsageResult(list(self.aggregate(pipeline)))


APIStatisticsManager = _APIStatisticsManager()
MessageRecordStatisticsManager = _MessageRecordStatisticsManager()
BotFeatureUsageDataManager = _BotFeatureUsageDataManager()
