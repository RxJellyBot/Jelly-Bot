import math
from dataclasses import dataclass, field, InitVar
from datetime import datetime, timedelta, tzinfo, time
from typing import Optional, Union, List

from dateutil import parser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def now_utc_aware(*, for_mongo: bool = False) -> datetime:
    """
    Return the current tz-aware :class:`datetime` with its timezone set to :class:`pytz.UTC`.

    -----

    If ``for_mongo`` is ``True``, the precision will be decreased to 1ms. if not, then it will be 1us.

    MongoDB only records time with 1ms precision.
    Setting ``for_mongo`` appropriately can eliminate the false negative of the tests.

    Step flow that have a great chance to cause false inequality:

    - Create a model with current timestamp

    - Store that model to the database

    - Get that model from the database

    At 1 and 2, the datetime may looks like ``...:52.300125``, but at 3, the acquire model will be ``...:52.300``.

    :param for_mongo: if this timestamp will be used as a data field of a MongoDB entry
    :return: current tz-aware datetime with timezone set to UTC
    """
    dt = timezone.utc.localize(datetime.utcnow())

    if for_mongo:
        dt = dt.replace(microsecond=dt.microsecond // 1000 * 1000)

    return dt


def localtime(dt: datetime = None, tz: timezone = None):
    return timezone.localtime(dt, tz)


def make_tz_aware(dt: datetime, tz: timezone = None):
    if not is_tz_naive(dt):
        return dt

    try:
        return timezone.make_aware(dt, tz)
    except OverflowError:
        return timezone.utc.localize(dt)


def is_tz_naive(dt: datetime) -> bool:
    try:
        return timezone.is_naive(dt)
    except OverflowError:
        # Checking `is_naive` will call `utcoffset()`
        # This exception will only raise if `utcoffset()` is not `None`

        # This exception might occur if dt = `datetime.min`.
        return False


def t_delta_str(t_delta: timedelta):
    h = t_delta.seconds // 3600
    m = (t_delta.seconds - 3600 * h) // 60
    s = t_delta.seconds % 60

    if t_delta.days > 3:
        return _("{} Days {} H {:02} M {:02} S").format(t_delta.days, h, m, s)
    else:
        h += t_delta.days * 24
        return _("{} H {:02} M {:02} S").format(h, m, s)


def parse_to_dt(dt_str: str, tzinfo_: Optional[tzinfo] = None) -> Optional[datetime]:
    """
    Parse ``dt_str`` to a tz-aware :class:`datetime`.

    :param dt_str: `str` to be parsed.
    :param tzinfo_: tzinfo to be applied to the datetime. Uses UTC if not provided.
    :return: `None` if the parsing failed. Otherwise, timezone-aware `datetime`.
    """
    if not dt_str:
        return None

    # Parse datetime string
    try:
        dt = parser.parse(dt_str, ignoretz=False)
    except (ValueError, OverflowError):
        return None

    # Attach timezone if needed
    if is_tz_naive(dt):
        dt = make_tz_aware(dt, tzinfo_ or timezone.utc)

    return dt


def time_to_seconds(t: time) -> float:
    """Convert `t` to second past in a day."""
    return t.hour * 3600 + t.minute * 60 + t.second + t.microsecond * 1E-6


class TimeRangeEndBeforeStart(Exception):
    pass


@dataclass
class TimeRange:
    """
    Represents a time range.

    If `start` and `end` specified
        > Ignore `range_hr`

    If `range_hr` specified
        > If `start` specified
            - `end` will be `start` + `range_hr` hrs
        > If `end` specified
            - `start` will be `end` - `range_hr` hrs
        > If both not specified
            - `start` will be the current time - `range_hr` hrs
    """
    start: Optional[datetime] = None
    start_org: Optional[datetime] = field(init=False)
    end: Optional[datetime] = None
    range_hr: InitVar[Optional[int]] = None
    range_mult: InitVar[Union[int, float]] = field(default=1.0)
    tzinfo_: Optional[tzinfo] = None
    end_autofill_now: InitVar[bool] = True

    def _localize(self, dt: Optional[datetime]):
        if dt:
            return localtime(make_tz_aware(dt, self.tzinfo_), self.tzinfo_)
        else:
            return None

    def _fill_start_end(self, now: datetime, range_hr: int, end_autofill_now: bool):
        if self.start and self.end:
            return

        # `range_hr` = 0 could be `False` so explicitly checking `None`
        if range_hr is not None:
            if self.start:
                self.end = self.start + timedelta(hours=range_hr)
            elif self.end:
                self.start = self.end - timedelta(hours=range_hr)
            else:
                self.start = now - timedelta(hours=range_hr)

        if not self.end and end_autofill_now:
            self.end = now

    def __post_init__(self, range_hr: Optional[int], range_mult: Union[int, float], end_autofill_now: bool):
        now = localtime(now_utc_aware(), self.tzinfo_)

        # Localize start and end timestamp if exists
        self.start = self._localize(self.start)
        self.end = self._localize(self.end)

        # Auto fill
        self._fill_start_end(now, range_hr, end_autofill_now)

        # Time order check
        if self.start and self.end and self.start > self.end:
            raise TimeRangeEndBeforeStart()

        self.start_org = self.start

        if self.expandable:
            self.start = self.start - timedelta(hours=self.hr_length * (range_mult - 1))

    @property
    def hr_length_org(self) -> float:
        """
        Time range length BEFORE applying range multiplier(`range_mult`).

        If `end` not set, uses now as the `end`.
        """
        if self.start_org and self.end:
            return (self.end - self.start_org).total_seconds() / 3600
        elif self.start_org:
            return (now_utc_aware() - self.start_org).total_seconds() / 3600
        else:
            return math.inf

    @property
    def hr_length(self) -> float:
        """
        Time range length AFTER applying range multiplier(`range_mult`).

        If `end` not set, uses now as the `end`.
        """
        if self.start and self.end:
            return (self.end - self.start).total_seconds() / 3600
        elif self.start:
            return (now_utc_aware() - self.start).total_seconds() / 3600
        else:
            return math.inf

    @property
    def expandable(self) -> bool:
        return self.start is not None and self.end is not None

    @property
    def expanded(self) -> bool:
        return self.expandable and self.start != self.start_org

    def get_periods(self) -> List['TimeRange']:
        if self.hr_length_org <= 0 or self.is_inf:
            return [self]

        ret = []

        _idx = 0
        _lbound = self.start
        _hbound = self.start + timedelta(hours=self.hr_length_org)

        while _hbound <= self.end:
            ret.append(TimeRange(start=_lbound, end=_hbound, tzinfo_=self.tzinfo_))

            _idx += 1
            _lbound += timedelta(hours=self.hr_length_org)
            _hbound += timedelta(hours=self.hr_length_org)

        return ret

    def set_start_day_offset(self, offset_days: int):
        """Offset `start` by `offset_days` days. Overwrites `start_org` to be the `start` before offsetting."""
        if self.start:
            self.start_org = self.start
            self.start = self.start + timedelta(days=offset_days)

    @property
    def is_inf(self):
        """Indicate if this time range is infinity (either one side of the range or both are not set)."""
        return self.start is None or self.end is None

    @property
    def expr_period_short(self):
        """
        Returns the short expression of the time period.

        Start = 01-01 and End = 01-07:
            01-01 ~ 01-07
        Start = 01-01 and End = None:
            01-01 ~ -
        Start = None and End = 01-07:
            - ~ 01-07
        Start = 01-01 and End = 01-07:
            - ~ -
        """
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

        return time_to_seconds(t)
