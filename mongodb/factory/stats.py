from datetime import datetime, timezone, timedelta
from threading import Thread
from typing import Any, Optional, Union, List

import pymongo
from bson import ObjectId
from pymongo.command_cursor import CommandCursor

from extutils.checker import param_type_ensure
from flags import APICommand, MessageType, BotFeature
from mongodb.factory.results import RecordAPIStatisticsResult, MessageRecordResult
from models import APIStatisticModel, MessageRecordModel, OID_KEY, BotFeatureUsageModel
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

    @param_type_ensure
    def record_message_async(
            self, channel_oid: ObjectId, user_root_oid: ObjectId,
            message_type: MessageType, message_content: Any, proc_time_ms: float):
        Thread(
            target=self.record_message,
            args=(channel_oid, user_root_oid, message_type, message_content, proc_time_ms)).start()

    @param_type_ensure
    def record_message(
            self, channel_oid: ObjectId, user_root_oid: ObjectId,
            message_type: MessageType, message_content: Any, proc_time_ms: float):
        self.insert_one_data(
            ChannelOid=channel_oid, UserRootOid=user_root_oid, MessageType=message_type,
            MessageContent=str(message_content)[:Database.MessageStats.MaxContentCharacter],
            ProcessTimeMs=proc_time_ms
        )

    # Statistics

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
            -> CommandCursor:
        if isinstance(channel_oids, ObjectId):
            match_d = {MessageRecordModel.ChannelOid.key: channel_oids}
        elif isinstance(channel_oids, list):
            match_d = {MessageRecordModel.ChannelOid.key: {"$in": channel_oids}}
        else:
            raise ValueError("Parameter `channel_oids` must be either `ObjectId` or `List[ObjectId]`.")

        if hours_within:
            match_d.update(**{
                OID_KEY: {
                    "$gt": ObjectId.from_datetime(
                        datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(hours=hours_within))
                }})

        aggr_pipeline = [
            {"$match": match_d},
            {"$group": {
                OID_KEY: "$" + MessageRecordModel.UserRootOid.key,
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": pymongo.DESCENDING, OID_KEY: pymongo.ASCENDING}}
        ]

        return self.aggregate(aggr_pipeline)


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


_inst = APIStatisticsManager()
_inst2 = MessageRecordStatisticsManager()
_inst3 = BotFeatureUsageDataManager()
