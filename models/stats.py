import abc
import math
from collections import namedtuple
from dataclasses import dataclass, field, InitVar
from datetime import datetime, timedelta, date
from time import gmtime, strftime
from typing import Dict, Optional, List

import pymongo
from bson import ObjectId
from django.utils.translation import gettext_lazy as _

from extutils.dt import now_utc_aware, TimeRange
from extutils.utils import enumerate_ranking
from flags import BotFeature, MessageType
from models import Model, ModelDefaultValueExt, OID_KEY
from models.field import (
    BooleanField, DictionaryField, APICommandField, DateTimeField, TextField, ObjectIDField,
    MessageTypeField, BotFeatureField, FloatField
)


# region Models
class APIStatisticModel(Model):
    Timestamp = DateTimeField("t", default=ModelDefaultValueExt.Required, allow_none=False)
    SenderOid = ObjectIDField("sd", default=ModelDefaultValueExt.Optional, allow_none=True, stores_uid=True)
    ApiAction = APICommandField("a")
    Parameter = DictionaryField("p", allow_none=True)
    PathParameter = DictionaryField("pp", allow_none=True)
    Response = DictionaryField("r", allow_none=True)
    Success = BooleanField("s", allow_none=True)
    PathInfo = TextField("pi", default=ModelDefaultValueExt.Required, must_have_content=True, allow_none=False)
    PathInfoFull = TextField("pf", default=ModelDefaultValueExt.Required, must_have_content=True, allow_none=False)


class MessageRecordModel(Model):
    ChannelOid = ObjectIDField("ch", default=ModelDefaultValueExt.Required)
    UserRootOid = ObjectIDField("u", default=ModelDefaultValueExt.Required, stores_uid=True)
    MessageType = MessageTypeField("t", default=ModelDefaultValueExt.Required)
    MessageContent = TextField("ct", default=ModelDefaultValueExt.Required)
    ProcessTimeSecs = FloatField("pt", default=ModelDefaultValueExt.Optional)
    Timestamp = DateTimeField("ts")


class BotFeatureUsageModel(Model):
    Feature = BotFeatureField("ft", default=ModelDefaultValueExt.Required)
    ChannelOid = ObjectIDField("ch", default=ModelDefaultValueExt.Required)
    SenderRootOid = ObjectIDField("u", default=ModelDefaultValueExt.Required, stores_uid=True)


# endregion


# region Results - Base
class HourlyResult(abc.ABC):
    DAYS_NONE = 0

    def __init__(self, days_collected: float):
        d_collected_int = math.floor(days_collected)

        now = datetime.utcnow()
        earliest = now - timedelta(days=days_collected)
        self.avg_calculatable = d_collected_int > HourlyResult.DAYS_NONE

        self.denom = []
        if self.avg_calculatable:
            add_one_end = now.hour
            if earliest.hour > now.hour:
                add_one_end += 24

            self.denom = [d_collected_int] * 24
            for hr in range(earliest.hour, add_one_end + 1):
                self.denom[hr % 24] += 1

    @staticmethod
    def data_days_collected(collection, filter_, *, hr_range: Optional[int] = None,
                            start: Optional[datetime] = None, end: Optional[datetime] = None):
        trange = TimeRange(range_hr=hr_range, start=start, end=end)

        if trange.is_inf:
            oldest = collection.find_one(filter_, sort=[(OID_KEY, pymongo.ASCENDING)])

            if oldest:
                # Replace to let both be Offset-naive
                return (now_utc_aware() - ObjectId(oldest[OID_KEY]).generation_time).total_seconds() / 86400
            else:
                return HourlyResult.DAYS_NONE
        else:
            return trange.hr_length / 24


class DailyResult(abc.ABC):
    FMT_DATE = "%Y-%m-%d"

    KEY_DATE = "dt"

    @staticmethod
    def trange_ensure_not_inf(days_collected, trange, tzinfo):
        """Ensure that time range are not `inf` length."""
        if trange.is_inf:
            return TimeRange(range_hr=days_collected * 24, start=trange.start, end=trange.end, tzinfo_=tzinfo)
        else:
            return trange

    @staticmethod
    def date_list(days_collected, tzinfo, *,
                  start: Optional[datetime] = None, end: Optional[datetime] = None,
                  trange: Optional[TimeRange] = None) -> List[date]:
        """Returns the date list within the time range. Disregard `start` and `end` if `trange` is specified."""
        ret = []

        if not trange:
            trange = TimeRange(range_hr=days_collected * 24, start=start, end=end, tzinfo_=tzinfo)

        if trange.is_inf:
            raise ValueError("TimeRange is infinity.")

        for i in range((trange.end.date() - trange.start.date()).days + 1):
            ret.append(trange.start.date() + timedelta(days=i))

        return ret

    @staticmethod
    def date_list_str(days_collected, tzinfo, *,
                      start: Optional[datetime] = None, end: Optional[datetime] = None,
                      trange: Optional[TimeRange] = None) -> List[str]:
        """Returns the date list within the time range. Disregard `start` and `end` if `trange` is specified."""
        return [dt.strftime(DailyResult.FMT_DATE) for dt
                in DailyResult.date_list(days_collected, tzinfo, start=start, end=end, trange=trange)]


# endregion


class HourlyIntervalAverageMessageResult(HourlyResult):
    KEY_CATEGORY = "cat"
    KEY_HR = "hr"

    KEY_COUNT = "ct"

    def __init__(self, cursor, days_collected: float):
        super().__init__(days_collected)

        CountDataEntry = namedtuple("CountDataEntry", ["category_name", "data", "color", "hidden"])

        # Create hours label for webpage
        self.label_hr = [i for i in range(24)]

        count_data = {}
        count_sum = [0 for __ in range(24)]

        for d in cursor:
            ctg = MessageType.cast(d[OID_KEY][HourlyIntervalAverageMessageResult.KEY_CATEGORY])
            hr = d[OID_KEY][HourlyIntervalAverageMessageResult.KEY_HR]

            if ctg not in count_data:
                count_data[ctg] = [0] * 24

            count = d[HourlyIntervalAverageMessageResult.KEY_COUNT]
            count_data[ctg][hr] = count
            count_sum[hr] += count

        count_data = [
            CountDataEntry(
                category_name=cat.key,
                data=[ct / dm for ct, dm in zip(data, self.denom)] if self.avg_calculatable else data,
                color="#777777",
                hidden="true"
            )
            for cat, data in count_data.items()
        ]
        count_sum = [
            CountDataEntry(
                category_name=_("(Total)"),
                data=[ct / dm for ct, dm in zip(count_sum, self.denom)] if self.avg_calculatable else count_sum,
                color="#323232",
                hidden="false"
            )
        ]

        self.data = count_sum + count_data

        self.hr_range = int(days_collected * 24)


class DailyMessageResult(DailyResult):
    KEY_HOUR = "hr"

    KEY_COUNT = "ct"

    def __init__(self, cursor, days_collected, tzinfo, *,
                 start: Optional[datetime] = None, end: Optional[datetime] = None):
        ResultEntry = namedtuple("ResultEntry", ["date", "data"])
        DataPoint = namedtuple("DataPoint", ["count", "percentage", "is_max"])

        self.label_hr = [h for h in range(24)]
        self.label_date = self.date_list_str(days_collected, tzinfo, start=start, end=end)

        data_sum = {dt: 0 for dt in self.label_date}
        data = {dt: [0] * 24 for dt in self.label_date}

        for d in cursor:
            date_ = d[OID_KEY][DailyMessageResult.KEY_DATE]
            hr = d[OID_KEY][DailyMessageResult.KEY_HOUR]

            count = d[DailyMessageResult.KEY_COUNT]

            data[date_][hr] += count
            data_sum[date_] += count

        for dt, pts in data.items():
            sum_ = sum(pts)
            max_ = max(pts)

            if sum_ > 0:
                data[dt] = [DataPoint(count=dp, percentage=dp / sum_ * 100, is_max=max_ == dp) for dp in pts]
            else:
                data[dt] = [DataPoint(count=dp, percentage=0.0, is_max=False) for dp in pts]

        self.data_sum = [data_sum[k] for k in
                         sorted(data_sum.keys(), key=lambda x: datetime.strptime(x, DailyResult.FMT_DATE))]
        self.data = [ResultEntry(date=date_, data=data[date_])
                     for date_ in sorted(data.keys(), key=lambda x: datetime.strptime(x, DailyResult.FMT_DATE))]


class MeanMessageResult:
    def __init__(self, date_list: List[date], data_list: List[float], mean_days: int):
        self.date_list = date_list
        self.data_list = data_list
        self.label = _("{} days mean").format(mean_days)


class MeanMessageResultGenerator(DailyResult):
    KEY_COUNT = "ct"

    def __init__(self, cursor, days_collected, tzinfo, *, trange: TimeRange, max_mean_days: int):
        self.max_madays = max_mean_days
        self.trange = self.trange_ensure_not_inf(days_collected, trange, tzinfo)
        self.dates = self.date_list(days_collected, tzinfo, start=self.trange.start, end=self.trange.end)
        self.data = {date_: 0 for date_ in self.dates}

        for d in cursor:
            date_ = datetime.strptime(d[OID_KEY][MeanMessageResultGenerator.KEY_DATE], DailyResult.FMT_DATE).date()
            count = d[MeanMessageResultGenerator.KEY_COUNT]

            self.data[date_] += count

    def generate_result(self, mean_days: int) -> MeanMessageResult:
        if mean_days > self.max_madays:
            raise ValueError("Max mean average calculation range reached.")

        date_list = []
        data_list = []

        current_date = self.trange.start_org.date()
        end_date = self.trange.end.date()
        while current_date <= end_date:
            total = 0
            for i in range(mean_days):
                total += self.data.get(current_date - timedelta(days=i), 0)

            date_list.append(current_date)
            data_list.append(total / mean_days)

            current_date += timedelta(days=1)

        return MeanMessageResult(date_list, data_list, mean_days)


class MemberDailyMessageResult(DailyResult):
    KEY_MEMBER = "mbr"

    KEY_COUNT = "ct"

    def __init__(self, cursor, days_collected, tzinfo, *, trange: TimeRange):
        self.trange = self.trange_ensure_not_inf(days_collected, trange, tzinfo)
        self.dates = self.date_list_str(days_collected, tzinfo, start=self.trange.start, end=self.trange.end)
        self.data_count = {date_: {} for date_ in self.dates}
        for d in cursor:
            _date_ = d[OID_KEY][MemberDailyMessageResult.KEY_DATE]
            _member_ = d[OID_KEY][MemberDailyMessageResult.KEY_MEMBER]
            _count_ = d[MemberDailyMessageResult.KEY_COUNT]
            self.data_count[_date_][_member_] = _count_


class CountBeforeTimeResult(DailyResult):
    KEY_SEC_OF_DAY = "sd"

    KEY_COUNT = "ct"

    def __init__(self, cursor, days_collected, tzinfo, *, trange: TimeRange):
        self.trange = self.trange_ensure_not_inf(days_collected, trange, tzinfo)
        self.dates = self.date_list_str(days_collected, tzinfo, start=self.trange.start, end=self.trange.end)

        self.data_count = {date_: 0 for date_ in self.dates}
        for d in cursor:
            _date_ = d[OID_KEY][CountBeforeTimeResult.KEY_DATE]
            _count_ = d[CountBeforeTimeResult.KEY_COUNT]
            self.data_count[_date_] = _count_

        self.data_count = [ct for dt, ct in self.data_count.items()]

    @property
    def title(self):
        return _("Message Count Before {}").format(strftime("%I:%M:%S %p", gmtime(self.trange.end_time_seconds)))


# region MemberMessageCountResult
@dataclass
class MemberMessageCountEntry:
    intervals: InitVar[int]
    count: List[int] = field(init=False)

    def __post_init__(self, intervals: int):
        self.count = [0] * intervals

    @property
    def total(self) -> int:
        return sum(self.count)


class MemberMessageCountResult:
    KEY_MEMBER_ID = "uid"
    KEY_INTERVAL_IDX = "idx"

    KEY_COUNT = "ct"

    def __init__(self, cursor, interval: int, trange: TimeRange):
        self.trange = trange

        self.interval = interval
        self.data = {}  # {<UID>: <Entry>, <UID>: <Entry>, ...}

        for d in cursor:
            uid = d[OID_KEY][MemberMessageCountResult.KEY_MEMBER_ID]
            idx = int(d[OID_KEY].get(MemberMessageCountResult.KEY_INTERVAL_IDX, interval - 1))

            if uid not in self.data:
                self.data[uid] = MemberMessageCountEntry(interval)

            count = d[MemberMessageByCategoryResult.KEY_COUNT]

            self.data[uid].count[idx] = count


# endregion


# region MemberMessageByCategoryResult
@dataclass
class MemberMessageByCategoryEntry:
    label_category: InitVar[List[MessageType]]
    data: Optional[Dict[MessageType, int]] = None
    total: int = field(init=False)

    def __post_init__(self, label_category):
        if not self.data:
            self.data = {lbl: 0 for lbl in label_category}

        self.total = sum(self.data.values())

    def add(self, category: MessageType, count: int):
        if category not in self.data:
            raise ValueError("Message type not initialized in the data dict.")

        self.data[category] += count
        self.total += count

    def get_count(self, category: MessageType):
        return self.data.get(category, 0)


class MemberMessageByCategoryResult:
    KEY_MEMBER_ID = "uid"
    KEY_CATEGORY = "cat"

    KEY_COUNT = "ct"

    def __init__(self, cursor):
        # Hand typing this to create custom order without additional implementations
        self.label_category = [
            MessageType.TEXT, MessageType.LINE_STICKER, MessageType.IMAGE, MessageType.VIDEO,
            MessageType.AUDIO, MessageType.LOCATION, MessageType.FILE
        ]

        self.data = {}  # {<UID>: <Entry>, <UID>: <Entry>, ...}

        for d in cursor:
            uid = d[OID_KEY][MemberMessageByCategoryResult.KEY_MEMBER_ID]
            cat = MessageType.cast(d[OID_KEY][MemberMessageByCategoryResult.KEY_CATEGORY])

            if uid not in self.data:
                self.data[uid] = self.get_default_data_entry()

            count = d[MemberMessageByCategoryResult.KEY_COUNT]

            self.data[uid].add(cat, count)

    def get_default_data_entry(self):
        return MemberMessageByCategoryEntry(self.label_category)


# endregion


class BotFeatureUsageResult:
    KEY = "count"

    def __init__(self, cursor, incl_not_used: bool):
        FeatureUsageEntry = namedtuple("FeatureUsageEntry", ["feature_name", "count", "rank"])

        self.data = []
        for rank, d in enumerate_ranking(
                cursor, is_tie=lambda cur, prv: cur[BotFeatureUsageResult.KEY] == prv[BotFeatureUsageResult.KEY]):
            try:
                feature = BotFeature.cast(d[OID_KEY]).key

                self.data.append(
                    FeatureUsageEntry(feature_name=feature, count=d[BotFeatureUsageResult.KEY], rank=rank)
                )
            except TypeError:
                # Skip if the code has been added in the newer build but not in the current executing build
                pass

        if incl_not_used:
            diff = {feature for feature in BotFeature}.difference({BotFeature.cast(d[OID_KEY]) for d in cursor})
            for diff_ in diff:
                self.data.append(FeatureUsageEntry(feature_name=diff_.key, count=0, rank=1))

        self.chart_label = [d.feature_name for d in self.data]
        self.chart_data = [d.count for d in self.data]


class BotFeaturePerUserUsageResult:
    KEY_FEATURE = "ft"
    KEY_UID = "uid"

    KEY_COUNT = "ct"

    def __init__(self, cursor):
        self.data = {}

        for d in cursor:
            uid = d[OID_KEY][BotFeaturePerUserUsageResult.KEY_UID]
            ft = BotFeature.cast(d[OID_KEY][BotFeaturePerUserUsageResult.KEY_FEATURE])

            if uid not in self.data:
                self.data[uid] = {feature: 0 for feature in BotFeature}

            self.data[uid][ft] = d[BotFeaturePerUserUsageResult.KEY_COUNT]


class BotFeatureHourlyAvgResult(HourlyResult):
    KEY_FEATURE = "ft"
    KEY_HR = "hr"

    KEY_COUNT = "ct"

    def __init__(self, cursor, incl_not_used: bool, days_collected: float):
        super().__init__(days_collected)

        self.hr_range = int(days_collected * 24)
        self.label_hr = [h for h in range(24)]

        # `show` is `str` because it's for js
        UsageEntry = namedtuple("UsageEntry", ["feature", "data", "color", "hidden"])

        data_points = {}
        hr_sum = [0] * 24

        for d in cursor:
            feature = BotFeature.cast(d[OID_KEY][BotFeatureHourlyAvgResult.KEY_FEATURE])
            hr = d[OID_KEY][BotFeatureHourlyAvgResult.KEY_HR]

            if feature not in data_points:
                data_points[feature] = [0] * 24

            c = d[BotFeatureHourlyAvgResult.KEY_COUNT]

            data_points[feature][hr] = c
            hr_sum[hr] += c

        if self.avg_calculatable:
            hr_sum = [ct / dm for ct, dm in zip(hr_sum, self.denom)]
            data_points = {ft: [ct / dm for ct, dm in zip(data, self.denom)] for ft, data in data_points.items()}

        self.data = [UsageEntry(feature=ft, data=data, color="#00A14B", hidden="true")
                     for ft, data in data_points.items()]

        if incl_not_used:
            diff = {feature for feature in BotFeature}.difference(data_points.keys())
            for diff_ in diff:
                self.data.append(UsageEntry(feature=diff_, data=[0] * 24, color="#9C0000", hidden="true"))

        entry = UsageEntry(feature=_("(Total)"), data=hr_sum, color="#323232", hidden="false")
        self.data = [entry] + list(sorted(self.data, key=lambda i: i.feature.code))
