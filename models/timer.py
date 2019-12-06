from dataclasses import dataclass, field, InitVar
from datetime import datetime
from typing import List

from extutils.dt import now_utc_aware
from models import Model, ModelDefaultValueExt
from models.field import DateTimeField, BooleanField, IntegerField, TextField, ObjectIDField
from mongodb.utils import CursorWithCount


class TimerModel(Model):
    ChannelOid = ObjectIDField("ch")
    KeywordOid = ObjectIDField("kw")
    Title = TextField("t", default=ModelDefaultValueExt.Required)
    TargetTime = DateTimeField("tt", default=ModelDefaultValueExt.Required)
    DeletionTime = DateTimeField("del",default=ModelDefaultValueExt.Optional)
    ContinueOnTimeUp = BooleanField("c", default=False)
    PeriodSeconds = IntegerField("p", default=ModelDefaultValueExt.Optional)

    @property
    def is_periodic(self) -> bool:
        return self.period_seconds > 0

    def get_target_time_diff(self, dt: datetime):
        """`dt` needs to be tz-aware."""
        if self.target_time > dt:
            return self.target_time - dt
        else:
            return dt - self.target_time

    def is_after(self, dt: datetime):
        """`dt` needs to be tz-aware."""
        return self.target_time >= dt


@dataclass
class TimerListResult:
    PastDone: List[TimerModel] = field(init=False, default_factory=list)
    PastContinue: List[TimerModel] = field(init=False, default_factory=list)
    Future: List[TimerModel] = field(init=False, default_factory=list)

    cursor: InitVar[CursorWithCount] = None

    def __post_init__(self, cursor):
        now = now_utc_aware()

        for mdl in cursor:
            if mdl.is_after(now):
                self.Future.append(mdl)
            else:
                if mdl.continue_on_time_up:
                    self.PastContinue.append(mdl)
                else:
                    self.PastDone.append(mdl)
