"""Stats entry data model."""
from extutils.dt import localtime
from models import Model, ModelDefaultValueExt  # pylint: disable=cyclic-import
from models.field import (
    BooleanField, DictionaryField, APICommandField, DateTimeField, TextField, ObjectIDField,
    MessageTypeField, BotFeatureField, FloatField
)


# region Models


class APIStatisticModel(Model):
    """Model of a single API usage."""

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
    """Model of a single entry of the handled message."""

    ChannelOid = ObjectIDField("ch", default=ModelDefaultValueExt.Required)
    UserRootOid = ObjectIDField("u", default=ModelDefaultValueExt.Required, stores_uid=True, allow_none=True)
    MessageType = MessageTypeField("t", default=ModelDefaultValueExt.Required)
    MessageContent = TextField("ct", default=ModelDefaultValueExt.Required, allow_none=True)
    ProcessTimeSecs = FloatField("pt", default=ModelDefaultValueExt.Optional)

    @property
    def timestamp(self):
        """
        Get a tz-aware timestamp of this model using ``_id``.

        :return: tz-aware timestamp of this model
        """
        return localtime(self.id.generation_time)


class BotFeatureUsageModel(Model):
    """Model of a single bot feature usage."""

    Feature = BotFeatureField("ft", default=ModelDefaultValueExt.Required)
    ChannelOid = ObjectIDField("ch", default=ModelDefaultValueExt.Required)
    SenderRootOid = ObjectIDField("u", default=ModelDefaultValueExt.Required, stores_uid=True)

# endregion
