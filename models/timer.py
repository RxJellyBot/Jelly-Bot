from dataclasses import dataclass, field, InitVar
from datetime import datetime
from typing import List, Union

from extutils.dt import now_utc_aware, t_delta_str, localtime, make_tz_aware
from models import Model, ModelDefaultValueExt
from models.field import DateTimeField, BooleanField, IntegerField, TextField, ObjectIDField
from mongodb.utils import ExtendedCursor
from strnames.models import Timer


class TimerModel(Model):
    ChannelOid = ObjectIDField("ch", default=ModelDefaultValueExt.Required)
    Keyword = TextField("k", default=ModelDefaultValueExt.Required)
    Title = TextField("t", default=ModelDefaultValueExt.Required)
    TargetTime = DateTimeField("tt", default=ModelDefaultValueExt.Required)
    DeletionTime = DateTimeField("del", default=ModelDefaultValueExt.Optional)
    Countup = BooleanField("c", default=False)
    PeriodSeconds = IntegerField("p")
    Notified = BooleanField("nt", default=False)
    NotifiedExpired = BooleanField("nt-e", default=False)

    @property
    def is_periodic(self) -> bool:
        return self.period_seconds > 0

    def get_target_time_diff(self, dt: datetime):
        return abs(self.target_time - make_tz_aware(dt))

    def is_after(self, dt: datetime) -> bool:
        """Check if the target time of the timer is after the given ``dt``."""
        return self.target_time >= make_tz_aware(dt)


@dataclass
class TimerListResult:
    future: List[TimerModel] = field(init=False, default_factory=list)
    past_continue: List[TimerModel] = field(init=False, default_factory=list)
    past_done: List[TimerModel] = field(init=False, default_factory=list)
    has_data: bool = field(init=False, default=False)

    cursor: InitVar[Union[ExtendedCursor[TimerModel], List[TimerModel]]] = None

    def __iter__(self):
        for t in self.future:
            yield t
        for t in self.past_continue:
            yield t
        for t in self.past_done:
            yield t

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

    def to_string(self, user_model):
        now = now_utc_aware()
        tzinfo = user_model.config.tzinfo

        ret = []

        if self.future:
            for tmr in self.future:
                ret.append(
                    Timer.FUTURE.format(
                        event=tmr.title, diff=t_delta_str(tmr.get_target_time_diff(now)),
                        time=localtime(tmr.target_time, tzinfo)
                    ))
            ret.append("")  # Separator

        if self.past_continue:
            for tmr in self.past_continue:
                ret.append(
                    Timer.PAST_CONTINUE.format(
                        event=tmr.title, diff=t_delta_str(tmr.get_target_time_diff(now)),
                        time=localtime(tmr.target_time, tzinfo)
                    ))
            ret.append("")  # Separator

        if self.past_done:
            for tmr in self.past_done:
                ret.append(
                    Timer.PAST_DONE.format(
                        event=tmr.title, time=localtime(tmr.target_time, tzinfo)))

        # Take out the final separator
        if ret and ret[-1] == "":
            ret = ret[:-1]

        return "\n".join(ret)

    def get_item(self, index: int):
        for idx, item in enumerate(self):
            if idx == index:
                return item

        return None
