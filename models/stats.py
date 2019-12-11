import math
from datetime import datetime, timedelta

from django.utils import timezone

from models.field import (
    BooleanField, DictionaryField, APICommandField, DateTimeField, TextField, ObjectIDField,
    MessageTypeField, BotFeatureField, FloatField
)
from models import Model, ModelDefaultValueExt, OID_KEY
from extutils.utils import rotate_list


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
    ProcessTimeMs = FloatField("pt", default=ModelDefaultValueExt.Optional)


class BotFeatureUsageModel(Model):
    Feature = BotFeatureField("ft", default=ModelDefaultValueExt.Required)
    ChannelOid = ObjectIDField("ch", default=ModelDefaultValueExt.Required)
    SenderRootOid = ObjectIDField("u", default=ModelDefaultValueExt.Required, stores_uid=True)


class HourlyIntervalAverageMessageResult:
    DAYS_NONE = 0
    KEY = "count"

    def __init__(self, cursor, days_collected: float):
        # Create hours label for webpage
        self.hours_label = [i for i in range(24)]

        now = datetime.utcnow()
        earliest = now - timedelta(days=days_collected)

        d_collected_int = math.floor(days_collected)

        # Initialize count data array, index = utc hr
        count_data = [0] * 24
        for d in cursor:
            count_data[d[OID_KEY]] = d[HourlyIntervalAverageMessageResult.KEY]

        # Days collected parameter provided
        avg_calculatable = d_collected_int > HourlyIntervalAverageMessageResult.DAYS_NONE

        # Pre-generate denominator (days collected in the hour interval)
        denom = []
        if avg_calculatable:
            add_one_end = now.hour
            if earliest.hour > now.hour:
                add_one_end += 24

            denom = [d_collected_int] * 24
            for hr in range(earliest.hour, add_one_end + 1):
                denom[hr % 24] += 1

        if avg_calculatable:
            self.avg_data = [ct / dm for ct, dm in zip(count_data, denom)]
        else:
            self.avg_data = count_data

        self.hr_range = int(days_collected * 24)


class DailyMessageResult:
    KEY = "count"

    def __init__(self, cursor):
        # FIXME: Handle 0 message count

        self.date_label = []
        self.date_count = []

        for data in cursor:
            self.date_label.append(data[OID_KEY])
            self.date_count.append(data[DailyMessageResult.KEY])
