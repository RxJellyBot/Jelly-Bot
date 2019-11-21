from typing import Optional

from bson import ObjectId

from JellyBot import systemconfig
from flags import AutoReplyContentType, ModelValidityCheckResult
from models.exceptions import KeyNotExistedError
from models.utils import AutoReplyValidators

from ._base import Model, ModelDefaultValueExt
from .field import (
    ObjectIDField, TextField, AutoReplyContentTypeField,
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
        if self.content_type != AutoReplyContentType.TEXT:
            return f"({self.content_type.key} / {self.content})"
        else:
            return self.content


class AutoReplyModuleModel(Model):
    # TODO: Bot Feature / Auto Reply: Auto expire (Auto disabled after certain time)

    # Main
    KeywordOid = ObjectIDField("k", default=ModelDefaultValueExt.Required, readonly=True)
    ResponseOids = ArrayField("r", ObjectId, default=ModelDefaultValueExt.Required,
                              max_len=systemconfig.AutoReply.MaxResponses)
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
    def creation_time(self):
        return self.id.generation_time

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
    def keyword(self) -> Optional[str]:
        from mongodb.factory import AutoReplyContentManager
        ctnt = AutoReplyContentManager.get_content_by_id(self.keyword_oid)
        return str(ctnt.content) if ctnt else None


class AutoReplyModuleExecodeModel(Model):
    KeywordOid = ObjectIDField("k", default=ModelDefaultValueExt.Required, readonly=True)
    ResponseOids = ArrayField("r", ObjectId, default=ModelDefaultValueExt.Required,
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
