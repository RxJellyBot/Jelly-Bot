from bson import ObjectId

from JellyBotAPI import SystemConfig
from flags import AutoReplyContentType, ModelValidityCheckResult
from models.utils import AutoReplyValidators

from ._base import Model, ModelDefaultValueExt
from .field import (
    ObjectIDField, TextField, AutoReplyContentTypeField,
    BooleanField, IntegerField, ArrayField, DateTimeField, ColorField, FloatField
)


class AutoReplyContentModel(Model):
    Content = TextField(
        "c", default=ModelDefaultValueExt.Required, maxlen=SystemConfig.AutoReply.MaxContentLength,
        allow_none=False, must_have_content=True)
    ContentType = AutoReplyContentTypeField("t")

    # noinspection PyAttributeOutsideInit
    def perform_validity_check(self) -> ModelValidityCheckResult:
        if self.content_type is None:
            self.content_type = AutoReplyContentType.default()

        if self.is_field_none("Content"):
            return ModelValidityCheckResult.X_AR_CONTENT_EMPTY

        valid = AutoReplyValidators.is_valid_content(self.content_type, self.content)

        if not valid:
            if self.content_type == AutoReplyContentType.IMAGE:
                return ModelValidityCheckResult.X_AR_CONTENT_NOT_IMAGE
            elif self.content_type == AutoReplyContentType.LINE_STICKER:
                return ModelValidityCheckResult.X_AR_CONTENT_NOT_LINE_STICKER

        return ModelValidityCheckResult.O_OK


class AutoReplyModuleModel(Model):
    # TODO: Auto Reply: Target User - Mixed with Exclude User

    KeywordOid = ObjectIDField("k", default=ModelDefaultValueExt.Required, readonly=True)
    ResponsesOids = ArrayField("r", ObjectId, default=ModelDefaultValueExt.Required,
                               max_len=SystemConfig.AutoReply.MaxResponses)
    CreatorOid = ObjectIDField("cr", readonly=True)
    Pinned = BooleanField("p", readonly=True)
    Disabled = BooleanField("d", readonly=True)
    Private = BooleanField("pr", readonly=True)
    CooldownSec = IntegerField("cd", readonly=True)
    CalledCount = IntegerField("c", readonly=True)
    LastUsed = DateTimeField("l", readonly=True, allow_none=False)
    ExcludedOids = ArrayField("e", ObjectId)
    TagIds = ArrayField("t", ObjectId)
    ChannelIds = ArrayField("ch", ObjectId, allow_empty=False)

    @property
    def creation_time(self):
        return self.id.generation_time


class AutoReplyModuleTokenActionModel(Model):
    KeywordOid = ObjectIDField("k", default=ModelDefaultValueExt.Required, readonly=True)
    ResponsesOids = ArrayField("r", ObjectId, default=ModelDefaultValueExt.Required,
                               max_len=SystemConfig.AutoReply.MaxResponses)
    CreatorOid = ObjectIDField("cr", readonly=True)
    Pinned = BooleanField("p", readonly=True)
    Private = BooleanField("pr", readonly=True)
    CooldownSec = IntegerField("cd", readonly=True)
    TagIds = ArrayField("t", ObjectId)

    def to_actual_model(self, channel_id: ObjectId):
        return AutoReplyModuleModel(**self.to_json(), ch=[channel_id], from_db=True)


class AutoReplyModuleTagModel(Model):
    Name = TextField("n", must_have_content=True)
    Color = ColorField("c")


class AutoReplyTagPopularityDataModel(Model):
    WeightedAvgTimeDiff = FloatField("w_avg_time_diff")
    WeightedAppearances = FloatField("w_appearances")
    Appearances = IntegerField("u_appearances")
    Score = FloatField("score")
