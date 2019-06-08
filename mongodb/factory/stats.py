from datetime import datetime

from flags import APIAction
from mongodb.factory.results import RecordAPIStatisticsResult
from models import APIStatisticModel
from JellyBotAPI.SystemConfig import Database

from ._base import BaseCollection

DB_NAME = "stats"


class APIStatisticsManager(BaseCollection):
    def __init__(self):
        super().__init__(DB_NAME, "api")
        self.create_index(APIStatisticModel.Timestamp,
                          expireAfterSeconds=Database.StatisticsExpirySeconds, name="Timestamp")

    def record_stats(self, api_action: APIAction, parameter: dict, response: dict, success: bool,
                     org_param: dict, path_info: str, path_info_full: str):
        entry, outcome, ex, insert_result = self.insert_one_data(
            APIStatisticModel, api_action=api_action, parameter=parameter, response=response, success=success,
            timestamp=datetime.now(), path_info=path_info, path_info_full=path_info_full, path_parameter=org_param)

        return RecordAPIStatisticsResult(outcome, entry, ex)


_inst = APIStatisticsManager()
