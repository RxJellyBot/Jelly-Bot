from datetime import datetime, tzinfo
from threading import Thread
from typing import Any, Optional, Union, List

import pymongo
from bson import ObjectId

from extutils.locales import UTC
from extutils.dt import now_utc_aware
from extutils.checker import param_type_ensure
from flags import APICommand, MessageType, BotFeature
from mongodb.factory.results import RecordAPIStatisticsResult
from mongodb.utils import CursorWithCount
from models import APIStatisticModel, MessageRecordModel, OID_KEY, BotFeatureUsageModel, \
    HourlyIntervalAverageMessageResult, DailyMessageResult, BotFeatureUsageResult, BotFeatureHourlyAvgResult, \
    HourlyResult, BotFeaturePerUserUsageResult, MemberMessageResult
from JellyBot.systemconfig import Database

from ._base import BaseCollection

DB_NAME = "stats"


class APIStatisticsManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "api"
    model_class = APIStatisticModel

    def __init__(self):
        super().__init__()
        self.create_index(APIStatisticModel.Timestamp.key,
                          expireAfterSeconds=Database.StatisticsExpirySeconds, name="Timestamp")

    @param_type_ensure
    def record_stats(self, api_action: APICommand, sender_oid: ObjectId, parameter: dict, response: dict, success: bool,
                     org_param: dict, path_info: str, path_info_full: str) -> RecordAPIStatisticsResult:
        entry, outcome, ex = self.insert_one_data(
            APIAction=api_action, SenderOid=sender_oid, Parameter=parameter, Response=response, Success=success,
            Timestamp=datetime.utcnow(), PathInfo=path_info, PathInfoFull=path_info_full, PathParameter=org_param)

        return RecordAPIStatisticsResult(outcome, entry, ex)


class MessageRecordStatisticsManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "msg"
    model_class = MessageRecordModel

    def __init__(self):
        super().__init__()
        self.create_index(MessageRecordModel.Timestamp.key,
                          expireAfterSeconds=Database.MessageStats.MessageRecordExpirySeconds, name="Timestamp")

    @param_type_ensure
    def record_message_async(
            self, channel_oid: ObjectId, user_root_oid: ObjectId,
            message_type: MessageType, message_content: Any, proc_time_secs: float):
        Thread(
            target=self.record_message,
            args=(channel_oid, user_root_oid, message_type, message_content, proc_time_secs)).start()

    @param_type_ensure
    def record_message(
            self, channel_oid: ObjectId, user_root_oid: ObjectId,
            message_type: MessageType, message_content: Any, proc_time_secs: float):
        self.insert_one_data(
            ChannelOid=channel_oid, UserRootOid=user_root_oid, MessageType=message_type,
            MessageContent=str(message_content)[:Database.MessageStats.MaxContentCharacter],
            ProcessTimeSecs=proc_time_secs, Timestamp=now_utc_aware()
        )

    @param_type_ensure
    def get_recent_messages(self, channel_oid: ObjectId, limit: Optional[int] = None) -> CursorWithCount:
        return self.find_cursor_with_count(
            {MessageRecordModel.ChannelOid.key: channel_oid}, parse_cls=MessageRecordModel
        ).sort([(OID_KEY, pymongo.DESCENDING)]).limit(limit)

    @param_type_ensure
    def get_message_frequency(self, channel_oid: ObjectId, limit: Optional[int] = None):
        rct_msg = list(self.get_recent_messages(channel_oid, limit))

        rct_msglen = len(rct_msg)
        if rct_msglen > 0:
            return abs((rct_msg[0].id.generation_time - rct_msg[-1].id.generation_time).total_seconds()) / rct_msglen
        else:
            return 0

    # Statistics

    @staticmethod
    def _channel_oids_filter_(channel_oids: Union[ObjectId, List[ObjectId]]):
        if isinstance(channel_oids, ObjectId):
            return {MessageRecordModel.ChannelOid.key: channel_oids}
        elif isinstance(channel_oids, list):
            return {MessageRecordModel.ChannelOid.key: {"$in": channel_oids}}
        else:
            raise ValueError("Must be either `ObjectId` or `List[ObjectId]`.")

    def get_messages_distinct_channel(self, message_fragment: str) -> List[ObjectId]:
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

        return [e["cid"] for e in aggr]

    def get_user_messages(
            self, channel_oids: Union[ObjectId, List[ObjectId]], hours_within: Optional[int] = None) \
            -> MemberMessageResult:
        match_d = self._channel_oids_filter_(channel_oids)
        self._attach_hours_within_(match_d, hours_within)

        aggr_pipeline = [
            {"$match": match_d},
            {"$group": {
                OID_KEY: {
                    MemberMessageResult.KEY_MEMBER_ID: "$" + MessageRecordModel.UserRootOid.key,
                    MemberMessageResult.KEY_CATEGORY: "$" + MessageRecordModel.MessageType.key
                },
                MemberMessageResult.KEY_COUNT: {"$sum": 1}
            }}
        ]

        return MemberMessageResult(list(self.aggregate(aggr_pipeline)))

    def hourly_interval_message_count(
            self, channel_oids: Union[ObjectId, List[ObjectId]], hours_within: Optional[int] = None,
            tzinfo_: tzinfo = UTC.to_tzinfo()) -> \
            HourlyIntervalAverageMessageResult:
        match_d = self._channel_oids_filter_(channel_oids)
        self._attach_hours_within_(match_d, hours_within)

        pipeline = [
            {"$match": match_d},
            {"$group": {
                "_id": {
                    HourlyIntervalAverageMessageResult.KEY_HR:
                        {"$hour": {"date": "$_id", "timezone": tzinfo_.tzname(datetime.utcnow())}},
                    HourlyIntervalAverageMessageResult.KEY_CATEGORY:
                        "$" + MessageRecordModel.MessageType.key
                },
                HourlyIntervalAverageMessageResult.KEY_COUNT: {"$sum": 1}
            }},
            {"$sort": {"_id": pymongo.ASCENDING}}
        ]

        return HourlyIntervalAverageMessageResult(
            list(self.aggregate(pipeline)), HourlyResult.data_days_collected(self, match_d, hours_within))

    def daily_message_count(
            self, channel_oids: Union[ObjectId, List[ObjectId]], hours_within: Optional[int] = None,
            tzinfo_: tzinfo = UTC.to_tzinfo()) -> \
            DailyMessageResult:
        match_d = self._channel_oids_filter_(channel_oids)
        self._attach_hours_within_(match_d, hours_within)

        pipeline = [
            {"$match": match_d},
            {"$group": {
                "_id": {
                    DailyMessageResult.KEY_DATE: {
                        "$dateToString": {
                            "date": "$_id",
                            "format": "%Y-%m-%d",
                            "timezone": tzinfo_.tzname(datetime.utcnow())
                        }
                    },
                    DailyMessageResult.KEY_HOUR: {
                        "$hour": {
                            "date": "$_id",
                            "timezone": tzinfo_.tzname(datetime.utcnow())
                        }
                    }
                },
                DailyMessageResult.KEY_COUNT: {"$sum": 1}
            }},
            {"$sort": {"_id": pymongo.ASCENDING}}
        ]

        return DailyMessageResult(
            list(self.aggregate(pipeline)), HourlyResult.data_days_collected(self, match_d, hours_within), tzinfo_)


class BotFeatureUsageDataManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "bot"
    model_class = BotFeatureUsageModel

    @param_type_ensure
    def record_usage_async(self, feature_used: BotFeature, channel_oid: ObjectId, root_oid: ObjectId):
        Thread(target=self.record_usage, args=(feature_used, channel_oid, root_oid)).start()

    @param_type_ensure
    def record_usage(self, feature_used: BotFeature, channel_oid: ObjectId, root_oid: ObjectId):
        if feature_used != BotFeature.UNDEFINED:
            self.insert_one_data(Feature=feature_used, ChannelOid=channel_oid, SenderRootOid=root_oid)

    # Statistics

    @param_type_ensure
    def get_channel_usage(self, channel_oid: ObjectId, hours_within: int = None, incl_not_used: bool = False) \
            -> BotFeatureUsageResult:
        filter_ = {BotFeatureUsageModel.ChannelOid.key: channel_oid}

        self._attach_hours_within_(filter_, hours_within)

        pipeline = [
            {"$match": filter_},
            {"$group": {
                OID_KEY: "$" + BotFeatureUsageModel.Feature.key,
                BotFeatureUsageResult.KEY: {"$sum": 1}
            }},
            {"$sort": {BotFeatureUsageResult.KEY: pymongo.DESCENDING}}
        ]

        return BotFeatureUsageResult(list(self.aggregate(pipeline)), incl_not_used)

    @param_type_ensure
    def get_channel_hourly_avg(
            self, channel_oid: ObjectId, hours_within: int = None, incl_not_used: bool = False,
            tzinfo_: tzinfo = UTC.to_tzinfo()) -> BotFeatureHourlyAvgResult:
        filter_ = {BotFeatureUsageModel.ChannelOid.key: channel_oid}

        self._attach_hours_within_(filter_, hours_within)

        pipeline = [
            {"$match": filter_},
            {"$group": {
                OID_KEY: {
                    BotFeatureHourlyAvgResult.KEY_FEATURE:
                        "$" + BotFeatureUsageModel.Feature.key,
                    BotFeatureHourlyAvgResult.KEY_HR:
                        {"$hour": {"date": "$_id", "timezone": tzinfo_.tzname(datetime.utcnow())}}
                },
                BotFeatureHourlyAvgResult.KEY_COUNT: {"$sum": 1}
            }}
        ]

        return BotFeatureHourlyAvgResult(
            list(self.aggregate(pipeline)),
            incl_not_used,
            HourlyResult.data_days_collected(self, filter_, hours_within))

    @param_type_ensure
    def get_channel_per_user_usage(
            self, channel_oid: ObjectId, hours_within: int = None, member_oid_list: Optional[List[ObjectId]] = None) \
            -> BotFeaturePerUserUsageResult:
        filter_ = {BotFeatureUsageModel.ChannelOid.key: channel_oid}

        if member_oid_list:
            filter_[BotFeatureUsageModel.SenderRootOid.key] = {"$in": member_oid_list}

        self._attach_hours_within_(filter_, hours_within)

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


_inst = APIStatisticsManager()
_inst2 = MessageRecordStatisticsManager()
_inst3 = BotFeatureUsageDataManager()
