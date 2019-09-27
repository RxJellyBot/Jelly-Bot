from datetime import datetime

from bson import ObjectId

from flags import APICommand
from mongodb.factory.results import RecordAPIStatisticsResult
from models import APIStatisticModel
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
                     org_param: dict, path_info: str, path_info_full: str):
        entry, outcome, ex, insert_result = self.insert_one_data(
            APIStatisticModel,
            APIAction=api_action, SenderOid=sender_oid, Parameter=parameter, Response=response, Success=success,
            Timestamp=datetime.utcnow(), PathInfo=path_info, PathInfoFull=path_info_full, PathParameter=org_param)

        return RecordAPIStatisticsResult(outcome, entry, ex)

# FIXME: [LP] Implement stats for recording message activity and message content
#   accompany with jieba https://github.com/fxsjy/jieba to provide message summary feature (Personal and group)

# FIXME: [LP] Potentially remove this and change to use `pyga` (collect stats on messages sent/processed)
#  with https://docs.djangoproject.com/en/2.2/topics/signals/


_inst = APIStatisticsManager()
