from datetime import datetime

from bson import ObjectId

from models import TimerModel
from mongodb.factory.results import WriteOutcome
from extutils.checker import param_type_ensure
from extutils.locales import UTC

from ._base import BaseCollection

DB_NAME = "timer"


class TimerManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "timer"
    model_class = TimerModel

    def __init__(self):
        super().__init__()

    @param_type_ensure
    def add_new_timer(
            self, kw_oid: ObjectId, title: str, target_time: datetime,
            continue_on_timeup: bool = False, period_sec: int = 0) -> WriteOutcome:
        """`target_time` is recommended to be tz-aware. Tzinfo will be forced to be UTC if tz-naive."""
        # Force target time to be tz-aware in UTC
        if target_time.tzinfo is None or target_time.tzinfo.utcoffset(datetime.now()) is None:
            target_time = target_time.replace(tzinfo=UTC.to_tzinfo())

        model, outcome, ex = self.insert_one_data(
            KeywordOid=kw_oid, Title=title, TargetTime=target_time, ContinueOnTimeUp=continue_on_timeup,
            PeriodSeconds=period_sec)

        return outcome

    @param_type_ensure
    def list_timer(self, kw_oid: ObjectId):
        # FIXME: Custom Order
        self.find_cursor_with_count({TimerModel.KeywordOid: kw_oid}).sort([(TimerModel.TargetTime)])
