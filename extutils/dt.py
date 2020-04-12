import math
from dataclasses import dataclass, field, InitVar
from datetime import datetime, timedelta, tzinfo
from typing import Optional, Union, List

import pytz
from dateutil import parser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def now_utc_aware():
    return datetime.utcnow().replace(tzinfo=pytz.UTC)


def localtime(dt=None, tz=None):
    return timezone.localtime(dt, tz)


def is_tz_naive(dt) -> bool:
    return dt.tzinfo is None or dt.tzinfo.utcoffset(datetime.now()) is None


def t_delta_str(t_delta: timedelta):
    h = t_delta.seconds // 3600
    m = (t_delta.seconds - 3600 * h) // 60
    s = t_delta.seconds % 60

    if t_delta.days > 3:
        return _("{} Days {} H {:02} M {:02} S").format(t_delta.days, h, m, s)
    else:
        h += t_delta.days * 24
        return _("{} H {:02} M {:02} S").format(h, m, s)


def parse_to_dt(dt_str: str, tzinfo_: Optional[tzinfo] = None):
    if not dt_str:
        return None

    # Parse datetime string
    try:
        dt = parser.parse(dt_str, ignoretz=False)
    except (ValueError, OverflowError):
        return None

    # Attach timezone if needed
    if is_tz_naive(dt):
        dt = dt.replace(tzinfo=tzinfo_ or pytz.utc)

    return dt


class TimeRangeEndBeforeStart(Exception):
    pass


@dataclass
class TimeRange:
    start: Optional[datetime]
    start_org: Optional[datetime] = field(init=False)
    end: Optional[datetime]
    range_mult: InitVar[Union[int, float]] = field(default=1.0)
    tzinfo_: Optional[tzinfo] = None
    expandable: bool = False
    expanded: bool = False
    end_autofill_now: bool = True

    def __post_init__(self, range_mult: Union[int, float]):
        self.start_org = self.start
        if self.start:
            if not self.end and self.end_autofill_now:
                self.end = localtime(now_utc_aware(), self.tzinfo_)

            if self.end and self.start > self.end:
                raise TimeRangeEndBeforeStart()

            self.start = self.start - timedelta(hours=self.hr_length * (range_mult - 1))
            self.expandable = True
            self.expanded = self.start != self.start_org

    @property
    def hr_length_org(self) -> float:
        if self.start_org and self.end:
            return (self.end - self.start_org).total_seconds() / 3600
        elif self.start_org:
            return (now_utc_aware() - self.start_org).total_seconds() / 3600
        else:
            return math.inf

    @property
    def hr_length(self) -> float:
        if self.start and self.end:
            return (self.end - self.start).total_seconds() / 3600
        elif self.start:
            return (now_utc_aware() - self.start).total_seconds() / 3600
        else:
            return math.inf

    def get_periods(self) -> List['TimeRange']:
        if self.hr_length_org <= 0 or self.is_inf:
            return [self]

        ret = []

        _idx_ = 0
        _lbound_ = self.start
        _hbound_ = self.start + timedelta(hours=self.hr_length_org)

        while _hbound_ <= self.end:
            ret.append(TimeRange(start=_lbound_, end=_hbound_, tzinfo_=self.tzinfo_))

            _idx_ += 1
            _lbound_ += timedelta(hours=self.hr_length_org)
            _hbound_ += timedelta(hours=self.hr_length_org)

        return ret

    def set_start_day_offset(self, offset_days: int):
        """Offset `start` by `offset_days` days. Overwrites `start_org` to be the `start` before offsetting."""
        if self.start:
            self.start_org = self.start
            self.start = self.start + timedelta(days=offset_days)

    @property
    def is_inf(self):
        return math.isinf(self.hr_length)

    @property
    def expr_period_short(self):
        if self.start:
            start_str = self.start.strftime('%m-%d')
        else:
            start_str = "-"

        if self.end:
            end_str = self.end.strftime('%m-%d')
        else:
            end_str = "-"

        return f"{start_str} ~ {end_str}"

    @property
    def end_time_seconds(self):
        """
        Get the timeseconds of the ending timestamp.

        If `end` does not exist, use the current time with `tzinfo`.

        Example:
            17:00:00 -> 61200
            06:54:27 -> 24867
        """
        if self.end:
            t = self.end.time()
        else:
            t = localtime(now_utc_aware(), tz=self.tzinfo_).time()

        return t.hour * 3600 + t.minute + 60 + t.second + t.microsecond * 10E-7


def parse_time_range(
        *, hr_range: Optional[int] = None, start: Optional[datetime] = None, end: Optional[datetime] = None,
        range_mult: Union[int, float] = 1.0, tzinfo_: Optional[tzinfo] = None) \
        -> TimeRange:
    """
    Parse the time range with the given parameters.

    Parameters all unspecified
    > `start` and `end` will be `None`.

    `hr_range` specified
    > `start` will be `hr_range` hours before counting from now.

    `start` and `hr_range` are specified
    > `end` will be `start` after `hr_range` hours.

    `end` and `hr_range` are specfied
    > `start` will be `end` before `hr_range` hours.

    Either `start` or `end` is specified but not `hr_range`
    > the other side of the time range will be `None`.

    `start` and `end` are specified
    > `hr_range` will be ignored.

    Given time range will be expanded `range_mult` times if expandable.

    :param hr_range: hour range
    :param start: starting timestamp
    :param end: ending timestamp
    :return: a `TimeRange` object
    """
    if not hr_range and not start and not end:
        return TimeRange(start=None, end=None, range_mult=range_mult, tzinfo_=tzinfo_)

    now = localtime(now_utc_aware(), tzinfo_)
    if start:
        start = localtime(start, tzinfo_)
    if end:
        end = localtime(end, tzinfo_)

    if start and end:
        return TimeRange(start=start, end=end, range_mult=range_mult, tzinfo_=tzinfo_)

    if hr_range:
        if start:
            return TimeRange(start=start, end=start + timedelta(hours=hr_range), range_mult=range_mult, tzinfo_=tzinfo_)
        elif end:
            return TimeRange(start=end - timedelta(hours=hr_range), end=end, range_mult=range_mult, tzinfo_=tzinfo_)
        else:
            return TimeRange(start=now - timedelta(hours=hr_range), end=now, range_mult=range_mult, tzinfo_=tzinfo_)
    else:
        if start:
            return TimeRange(start=start, end=now, range_mult=range_mult, tzinfo_=tzinfo_)
        elif end:
            return TimeRange(start=None, end=end, range_mult=range_mult, tzinfo_=tzinfo_)
