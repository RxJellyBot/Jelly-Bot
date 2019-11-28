from datetime import datetime

from django.utils import timezone

from models.field import (
    BooleanField, DictionaryField, APICommandField, DateTimeField, TextField, ObjectIDField,
    MessageTypeField, BotFeatureField, FloatField
)
from models import Model, ModelDefaultValueExt
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

    def __init__(self, cursor, days_collected: int):
        # Create hours label for webpage
        self.hours_label = [i for i in range(24)]
        # Initialize average data object
        self.avg_data = [0 for _ in range(24)]

        now = datetime.utcnow()
        now_utc_hr = now.hour
        tz_offset = int(timezone.get_current_timezone().utcoffset(dt=now).total_seconds() // 3600)

        for d in list(cursor):
            utc_hr = d["_id"]
            offset_hr = (utc_hr + tz_offset) % 24

            if days_collected > HourlyIntervalAverageMessageResult.DAYS_NONE:
                # Count 1 days more if the current hour passed the recording hour
                denom = days_collected
                if now_utc_hr > utc_hr:
                    denom += 1

                self.avg_data[offset_hr] = d[HourlyIntervalAverageMessageResult.KEY] / denom
            else:
                self.avg_data[offset_hr] = d[HourlyIntervalAverageMessageResult.KEY]

        self.hr_range = int(days_collected * 24)
