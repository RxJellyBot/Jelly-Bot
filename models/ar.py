from typing import Optional

from bson import ObjectId

from JellyBot import systemconfig
from flags import AutoReplyContentType, ModelValidityCheckResult
from models.exceptions import KeyNotExistedError
from models.utils import AutoReplyValidators

from ._base import Model, ModelDefaultValueExt
from .field import (
    ObjectIDField, TextField, AutoReplyContentTypeField, ModelField, ModelArrayField,
    BooleanField, IntegerField, ArrayField, DateTimeField, ColorField, FloatField
)


class AutoReplyContentModel(Model):
    Content = TextField(
        "c", default=ModelDefaultValueExt.Required, maxlen=systemconfig.AutoReply.MaxContentLength,
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

    def __str__(self):
        if self.content_type == AutoReplyContentType.TEXT:
            return self.content
        else:
            return f"({self.content_type.key} / {self.content})"


class AutoReplyModuleModel(Model):
    # TODO: Bot Feature / Auto Reply: Auto expire (Auto disabled after certain time)

    key_kw = "kw"

    # Main
    Keyword = ModelField(key_kw, default=ModelDefaultValueExt.Required, model_cls=AutoReplyContentModel)
    Responses = ModelArrayField("rp", AutoReplyContentModel, default=ModelDefaultValueExt.Required,
                                max_len=systemconfig.AutoReply.MaxResponses)

    KEY_KW_CONTENT = f"{key_kw}.{AutoReplyContentModel.Content.key}"
    KEY_KW_TYPE = f"{key_kw}.{AutoReplyContentModel.ContentType.key}"
    ChannelId = ObjectIDField("ch")
    Active = BooleanField("at", default=True)

    # Type
    ReferTo = ObjectIDField("rid", allow_none=True, default=ModelDefaultValueExt.Optional)

    # Record
    CreatorOid = ObjectIDField("cr", stores_uid=True)
    RemoverOid = ObjectIDField("rmv", stores_uid=True, default=ModelDefaultValueExt.Optional)

    # Property
    Pinned = BooleanField("p")
    Private = BooleanField("pr")
    CooldownSec = IntegerField("cd")
    ExcludedOids = ArrayField("e", ObjectId, stores_uid=True)
    TagIds = ArrayField("t", ObjectId)

    # Stats
    CalledCount = IntegerField("c")
    LastUsed = DateTimeField("l", allow_none=False)
    RemovedAt = DateTimeField("rm", allow_none=False)

    @property
    def refer_oid(self) -> Optional[ObjectId]:
        try:
            if self.is_reference:
                return self.refer_to
            else:
                return None
        except (KeyError, KeyNotExistedError, AttributeError):
            return None

    @property
    def is_reference(self) -> bool:
        try:
            return not self.is_field_none("ReferTo")
        except (KeyError, KeyNotExistedError, AttributeError):
            return False

    @property
    def keyword_repr(self) -> str:
        return f"{str(self.keyword)} ({self.called_count})"


class AutoReplyModuleExecodeModel(Model):
    Keyword = ModelField(AutoReplyModuleModel.key_kw,
                         default=ModelDefaultValueExt.Required, model_cls=AutoReplyContentModel)
    Responses = ArrayField("rp", AutoReplyContentModel, default=ModelDefaultValueExt.Required,
                           max_len=systemconfig.AutoReply.MaxResponses)
    Pinned = BooleanField("p", readonly=True)
    Private = BooleanField("pr", readonly=True)
    CooldownSec = IntegerField("cd", readonly=True)
    TagIds = ArrayField("t", ObjectId)

    def to_actual_model(self, channel_id: ObjectId, creator_oid: ObjectId):
        return AutoReplyModuleModel(
            **self.to_json(), from_db=True, **{AutoReplyModuleModel.ChannelId.key: channel_id,
                                               AutoReplyModuleModel.CreatorOid.key: creator_oid})


class AutoReplyModuleTagModel(Model):
    Name = TextField("n", must_have_content=True)
    Color = ColorField("c")


class AutoReplyTagPopularityDataModel(Model):
    WeightedAvgTimeDiff = FloatField("w_avg_time_diff")
    WeightedAppearances = FloatField("w_appearances")
    Appearances = IntegerField("u_appearances")
    Score = FloatField("score")
