import abc
import math
from collections import namedtuple
from datetime import datetime, timedelta

import pymongo
from bson import ObjectId
from django.utils.translation import gettext_lazy as _

from extutils.dt import now_utc_aware, localtime
from flags import BotFeature, MessageType
from models.field import (
    BooleanField, DictionaryField, APICommandField, DateTimeField, TextField, ObjectIDField,
    MessageTypeField, BotFeatureField, FloatField
)
from models import Model, ModelDefaultValueExt, OID_KEY


class APIStatisticModel(Model):
    Timestamp = DateTimeField("t", default=ModelDefaultValueExt.Required, allow_none=False)
    SenderOid = ObjectIDField("sd", default=ModelDefaultValueExt.Optional, allow_none=True, stores_uid=True)
    APIAction = APICommandField("a")
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


class BotFeatureUsageModel(Model):
    Feature = BotFeatureField("ft", default=ModelDefaultValueExt.Required)
    ChannelOid = ObjectIDField("ch", default=ModelDefaultValueExt.Required)
    SenderRootOid = ObjectIDField("u", default=ModelDefaultValueExt.Required, stores_uid=True)


# --- Results


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
    def data_days_collected(collection, filter_, hr_range):
        if hr_range:
            return hr_range / 24
        else:
            oldest = collection.find_one(filter_, sort=[(OID_KEY, pymongo.ASCENDING)])

            if oldest:
                # Replace to let both be Offset-naive
                return (now_utc_aware() - ObjectId(oldest[OID_KEY]).generation_time).total_seconds() / 86400
            else:
                return HourlyResult.DAYS_NONE


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


class DailyMessageResult:
    KEY_DATE = "dt"
    KEY_HOUR = "hr"

    KEY_COUNT = "ct"

    def __init__(self, cursor, days_collected, tzinfo):
        ResultEntry = namedtuple("ResultEntry", ["date", "data"])
        DataPoint = namedtuple("DataPoint", ["count", "percentage", "is_max"])

        self.label_hr = [h for h in range(24)]
        self.label_date = self._prepare_label_data_(days_collected, tzinfo)

        data_sum = {dt: 0 for dt in self.label_date}
        data = {dt: [0] * 24 for dt in self.label_date}

        for d in cursor:
            date = d[OID_KEY][DailyMessageResult.KEY_DATE]
            hr = d[OID_KEY][DailyMessageResult.KEY_HOUR]

            count = d[DailyMessageResult.KEY_COUNT]

            data[date][hr] += count
            data_sum[date] += count

        for dt, pts in data.items():
            sum_ = sum(pts)
            max_ = max(pts)

            if sum_ > 0:
                data[dt] = [DataPoint(count=dp, percentage=dp / sum_ * 100, is_max=max_ == dp) for dp in pts]
            else:
                data[dt] = [DataPoint(count=dp, percentage=0.0, is_max=False) for dp in pts]

        self.data_sum = [data_sum[k] for k in
                         sorted(data_sum.keys(), key=lambda x: datetime.strptime(x, "%Y-%m-%d"))]
        self.data = [ResultEntry(date=date, data=data[date])
                     for date in sorted(data.keys(), key=lambda x: datetime.strptime(x, "%Y-%m-%d"))]

    @staticmethod
    def _prepare_label_data_(days_collected, tzinfo):
        ret = []

        _end_ = localtime(now_utc_aware(), tz=tzinfo)
        _start_ = (_end_ - timedelta(days=days_collected)).date()

        for i in range((_end_.date() - _start_).days + 1):
            ret.append((_start_ + timedelta(days=i)).strftime("%Y-%m-%d"))

        return ret


class MemberMessageResult:
    KEY_MEMBER_ID = "uid"
    KEY_CATEGORY = "cat"

    KEY_COUNT = "ct"

    def __init__(self, cursor):
        # Hand typing this to create custom order without consuming system performance
        self.label_category = [
            MessageType.TEXT, MessageType.LINE_STICKER, MessageType.IMAGE, MessageType.VIDEO,
            MessageType.AUDIO, MessageType.LOCATION, MessageType.FILE
        ]

        self.data = {}

        for d in cursor:
            uid = d[OID_KEY][MemberMessageResult.KEY_MEMBER_ID]
            cat = MessageType.cast(d[OID_KEY][MemberMessageResult.KEY_CATEGORY])

            if uid not in self.data:
                self.data[uid] = self.get_default_data_entry()

            count = d[MemberMessageResult.KEY_COUNT]

            self.data[uid][cat] += count

    def get_default_data_entry(self):
        return {lbl: 0 for lbl in self.label_category}


class BotFeatureUsageResult:
    KEY = "count"

    def __init__(self, cursor, incl_not_used: bool):
        FeatureUsageEntry = namedtuple("FeatureUsageEntry", ["feature_name", "count"])

        self.data = [
            FeatureUsageEntry(feature_name=BotFeature.cast(d[OID_KEY]).key, count=d[BotFeatureUsageResult.KEY])
            for d in cursor
        ]

        if incl_not_used:
            diff = {feature for feature in BotFeature}.difference({BotFeature.cast(d[OID_KEY]) for d in cursor})
            for diff_ in diff:
                self.data.append(FeatureUsageEntry(feature_name=diff_.key, count=0))

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

        self.data = [UsageEntry(feature=_("(Total)"), data=hr_sum, color="#323232", hidden="false")] \
            + list(sorted(self.data, key=lambda i: i.feature.code))
