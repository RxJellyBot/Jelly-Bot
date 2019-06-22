from datetime import datetime

from bson import ObjectId

from flags import APIAction
from mongodb.factory.results import RecordAPIStatisticsResult
from models import APIStatisticModel
from JellyBotAPI.SystemConfig import Database

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

    def record_stats(self, api_action: APIAction, sender_oid: ObjectId, parameter: dict, response: dict, success: bool,
                     org_param: dict, path_info: str, path_info_full: str):
        entry, outcome, ex, insert_result = self.insert_one_data(
            APIStatisticModel,
            APIAction=api_action, SenderOid=sender_oid, Parameter=parameter, Response=response, Success=success,
            Timestamp=datetime.now(), PathInfo=path_info, PathInfoFull=path_info_full, PathParameter=org_param)

        return RecordAPIStatisticsResult(outcome, entry, ex)


_inst = APIStatisticsManager()
