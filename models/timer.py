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
    Countup = BooleanField("c", default=False)
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
    past_done: List[TimerModel] = field(init=False, default_factory=list)
    past_continue: List[TimerModel] = field(init=False, default_factory=list)
    future: List[TimerModel] = field(init=False, default_factory=list)
    has_data: bool = field(init=False, default=False)

    cursor: InitVar[CursorWithCount] = None

    def __post_init__(self, cursor):
        now = now_utc_aware()

        for mdl in cursor:
            self.has_data = True

            if mdl.is_after(now):
                self.future.append(mdl)
            else:
                if mdl.countup:
                    self.past_continue.append(mdl)
                else:
                    self.past_done.append(mdl)
