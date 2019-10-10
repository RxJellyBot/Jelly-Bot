from datetime import datetime
from typing import Any

from bson import ObjectId

from flags import APICommand, MessageType
from mongodb.factory.results import RecordAPIStatisticsResult, MessageRecordResult
from models import APIStatisticModel, MessageRecordModel
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

    def record_stats(self, api_action: APICommand, sender_oid: ObjectId, parameter: dict, response: dict, success: bool,
                     org_param: dict, path_info: str, path_info_full: str) -> RecordAPIStatisticsResult:
        entry, outcome, ex, insert_result = self.insert_one_data(
            APIStatisticModel,
            APIAction=api_action, SenderOid=sender_oid, Parameter=parameter, Response=response, Success=success,
            Timestamp=datetime.utcnow(), PathInfo=path_info, PathInfoFull=path_info_full, PathParameter=org_param)

        return RecordAPIStatisticsResult(outcome, entry, ex)


class MessageRecordStatisticsManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "msg"
    model_class = MessageRecordModel

    def record_message(
            self, channel_oid: ObjectId, user_root_oid: ObjectId,
            message_type: MessageType, message_content: Any) -> MessageRecordResult:
        entry, outcome, ex, insert_result = self.insert_one_data(
            MessageRecordModel,
            ChannelOid=channel_oid, UserRootOid=user_root_oid, MessageType=message_type, MessageContent=message_content)

        return MessageRecordResult(outcome, entry, ex)

# INCOMPLETE: Bot Statistics: Implement stats for recording message activity and message content
#   accompany with jieba https://github.com/fxsjy/jieba to provide message summary feature


_inst = APIStatisticsManager()
_inst2 = MessageRecordStatisticsManager()
