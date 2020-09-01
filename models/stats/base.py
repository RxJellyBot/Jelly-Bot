"""Base result objects to be inherited."""
import abc
import math
from datetime import datetime, timedelta, date
from typing import Optional, List

import pymongo
from bson import ObjectId

from extutils.dt import now_utc_aware, TimeRange, make_tz_aware
from models import OID_KEY

__all__ = ("HourlyResult", "DailyResult")


class HourlyResult(abc.ABC):
    """
    Base hourly result object.

    **Fields**

    ``avg_calculatable``
        If this result can be used to calculate daily average.

    ``denom``
        Denominators to divide the accumulated result number.
        Will be an empty list if ``avg_calculatable`` is ``False``.
    """

    DAYS_NONE = 0

    def __init__(self, days_collected: float, *, end_time: Optional[datetime] = None):
        """
        Initalizing method of :class:`HourlyResult`.

        :param days_collected: "claimed" days collected of the data
        :param end_time: end time of the data. current time in UTC if not given
        """
        d_collected_int = math.floor(days_collected)

        end_time = end_time or datetime.utcnow()
        earliest = end_time - timedelta(days=days_collected)
        self.avg_calculatable: bool = d_collected_int > HourlyResult.DAYS_NONE

        self.denom: List[float] = []
        if self.avg_calculatable:
            add_one_end = end_time.hour
            if earliest.hour > end_time.hour:
                add_one_end += 24

            if days_collected * 24 % 1 > 0:
                add_one_end += 1

            self.denom = [d_collected_int] * 24
            for hour in range(earliest.hour, add_one_end):
                self.denom[hour % 24] += 1

    @staticmethod
    def data_days_collected(collection, filter_, *, hr_range: Optional[int] = None,
                            start: Optional[datetime] = None, end: Optional[datetime] = None) -> float:
        """
        Get the data collection time length in terms of days.

        Data query will not execute if there is a :class:`TimeRange` could be constructed and
        not having an infinite length by taking ``hr_range``, ``start`` and ``end``.

        .. note::

            This is different from ``days_collected`` in ``__init__()`` because
            this connects to the database to calculate the actual days collected in the filtered dataset
            while the one in ``__init__()`` assumes what is being passed is true.

            ``hr_range`` will be ignored if both ``start`` and ``end`` is specified.

        :param collection: collection class to apply `filter_` for calculation
        :param filter_: condition to filter the data to be checked
        :param hr_range: hour range to construct a time range
        :param start: start timestamp to construct a time range
        :param end: end timestamp to construct a time range
        :return: time length in days of the collection of filtered data
        """
        trange = TimeRange(range_hr=hr_range, start=start, end=end, end_autofill_now=False)

        if not trange.is_inf:
            return trange.hr_length / 24

        oldest = collection.find_one(filter_, sort=[(OID_KEY, pymongo.ASCENDING)])

        if not oldest:
            return HourlyResult.DAYS_NONE

        now = now_utc_aware()

        if start:
            start = make_tz_aware(start)

        if start and start > now:
            return HourlyResult.DAYS_NONE

        if end:
            end = make_tz_aware(end)

        return max(
            ((end or now) - ObjectId(oldest[OID_KEY]).generation_time).total_seconds() / 86400,
            0
        )


class DailyResult(abc.ABC):
    """Base daily result object."""

    FMT_DATE = "%Y-%m-%d"

    KEY_DATE = "dt"

    @staticmethod
    def trange_ensure_not_inf(days_collected, trange, tzinfo):
        """
        Ensure that the time legnth of ``trange`` is not infinitely long.

        If it is, create a ``TimeRange`` with ``days_collected`` and ``start``, ``end`` as the same, then return it.

        :param days_collected: "claimed" days collected for the data
        :param trange: time range to be checked
        :param tzinfo: timezone info to apply
        :return: a `TimeRange` that should not have an infinite time length
        """
        if trange.is_inf:
            return TimeRange(range_hr=days_collected * 24, start=trange.start, end=trange.end, tzinfo_=tzinfo)

        return trange

    @staticmethod
    def date_list(days_collected, tzinfo, *,
                  start: Optional[datetime] = None, end: Optional[datetime] = None,
                  trange: Optional[TimeRange] = None) -> List[date]:
        """
        Get a list of dates within the given time range starting with the oldest date.

        Disregards ``start`` and ``end`` if ``trange`` is specified.

        :param days_collected: "claimed" days collected of the data
        :param tzinfo: timezone info to apply to get the date list
        :param start: starting timestamp of the data
        :param end: ending timestamp of the data
        :param trange: time range to be used to get the date list
        :return: a list of `date`
        """
        ret = []

        if not trange:
            trange = TimeRange(range_hr=days_collected * 24, start=start, end=end, tzinfo_=tzinfo)

        if trange.is_inf:
            raise ValueError("TimeRange length is infinity.")

        for i in range((trange.end.date() - trange.start.date()).days + 1):
            ret.append(trange.start.date() + timedelta(days=i))

        return ret

    @staticmethod
    def date_list_str(days_collected, tzinfo, *,
                      start: Optional[datetime] = None, end: Optional[datetime] = None,
                      trange: Optional[TimeRange] = None) -> List[str]:
        """
        Same functionality as ``date_list()`` except that the returned dates will be :class:`str`.

        The returned dates will be in the format of ``%Y-%m-%d``.

        :param days_collected: "claimed" days collected of the data
        :param tzinfo: timezone info to apply to get the date list
        :param start: starting timestamp of the data
        :param end: ending timestamp of the data
        :param trange: time range to be used to get the date list
        :return: a list of `str` converted from `date_list()`
        """
        return [dt.strftime(DailyResult.FMT_DATE) for dt
                in DailyResult.date_list(days_collected, tzinfo, start=start, end=end, trange=trange)]
