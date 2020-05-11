from dataclasses import dataclass
from typing import Optional, Union

from bson import ObjectId

from extutils.dt import localtime
from extutils.line_sticker import LineStickerManager
from JellyBot import systemconfig
from flags import AutoReplyContentType, ModelValidityCheckResult
from models import OID_KEY
from models.exceptions import FieldKeyNotExistedError
from models.utils import AutoReplyValidator
from extutils.utils import enumerate_ranking

from ._base import Model
from .field import (
    ObjectIDField, TextField, AutoReplyContentTypeField, ModelField, ModelArrayField,
    BooleanField, IntegerField, ArrayField, DateTimeField, ColorField, FloatField, ModelDefaultValueExt
)


def _content_to_str_(content_type, content):
    if content_type == AutoReplyContentType.TEXT:
        return content
    else:
        return f"({content_type.key} / {content})"


def _content_to_html_(content_type, content):
    if content_type == AutoReplyContentType.TEXT:
        return content.replace("\n", "<br>").replace(" ", "&nbsp;")
    elif content_type == AutoReplyContentType.IMAGE:
        return f'<img src="{content}"/>'
    elif content_type == AutoReplyContentType.LINE_STICKER:
        return f'<img src="{LineStickerManager.get_sticker_url(content)}"/>'
    else:
        return content


class AutoReplyContentModel(Model):
    WITH_OID = False

    Content = TextField(
        "c", default=ModelDefaultValueExt.Required, maxlen=systemconfig.AutoReply.MaxContentLength,
        allow_none=False, must_have_content=True)
    ContentType = AutoReplyContentTypeField("t")

    @property
    def content_html(self):
        return _content_to_html_(self.content_type, self.content)

    # noinspection PyAttributeOutsideInit
    def perform_validity_check(self) -> ModelValidityCheckResult:
        if self.content_type is None:
            self.content_type = AutoReplyContentType.default()

        if self.is_field_none("Content"):
            return ModelValidityCheckResult.X_AR_CONTENT_EMPTY

        valid = AutoReplyValidator.is_valid_content(self.content_type, self.content, online_check=False)

        if not valid:
            if self.content_type == AutoReplyContentType.IMAGE:
                return ModelValidityCheckResult.X_AR_CONTENT_NOT_IMAGE
            elif self.content_type == AutoReplyContentType.LINE_STICKER:
                return ModelValidityCheckResult.X_AR_CONTENT_NOT_LINE_STICKER

        return ModelValidityCheckResult.O_OK

    def __str__(self):
        return _content_to_str_(self.content_type, self.content)


class AutoReplyModuleModel(Model):
    key_kw = "kw"

    # Main
    Keyword = ModelField(key_kw, AutoReplyContentModel, default=ModelDefaultValueExt.Required)
    Responses = ModelArrayField("rp", AutoReplyContentModel, default=ModelDefaultValueExt.Required,
                                max_len=systemconfig.AutoReply.MaxResponses)

    KEY_KW_CONTENT = f"{key_kw}.{AutoReplyContentModel.Content.key}"
    KEY_KW_TYPE = f"{key_kw}.{AutoReplyContentModel.ContentType.key}"
    ChannelId = ObjectIDField("ch", default=ModelDefaultValueExt.Required)
    Active = BooleanField("at", default=True)

    # Type
    ReferTo = ObjectIDField("rid", allow_none=True, default=ModelDefaultValueExt.Optional)

    # Record
    CreatorOid = ObjectIDField("cr", stores_uid=True, default=ModelDefaultValueExt.Required)
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
        except (KeyError, FieldKeyNotExistedError, AttributeError):
            return None

    @property
    def is_reference(self) -> bool:
        try:
            return not self.is_field_none("ReferTo")
        except (KeyError, FieldKeyNotExistedError, AttributeError):
            return False

    @property
    def keyword_repr(self) -> str:
        return f"{str(self.keyword)}"

    @property
    def last_used_expr(self) -> Optional[str]:
        if self.last_used != DateTimeField.none_obj():
            return localtime(self.last_used).strftime("%Y-%m-%d %H:%M:%S")
        else:
            return None

    @property
    def removed_at_expr(self) -> Optional[str]:
        if self.removed_at != DateTimeField.none_obj():
            return localtime(self.removed_at).strftime("%Y-%m-%d %H:%M:%S")
        else:
            return None


class AutoReplyModuleExecodeModel(Model):
    Keyword = ModelField(AutoReplyModuleModel.key_kw, AutoReplyContentModel,
                         default=ModelDefaultValueExt.Required)
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


@dataclass
class UniqueKeywordCountEntry:
    word: str
    word_type: Union[int, AutoReplyContentType]
    count_usage: int
    count_module: int
    rank: int

    def __post_init__(self):
        self.word_type = AutoReplyContentType.cast(self.word_type)
        self.word = _content_to_html_(self.word_type, self.word)

    @property
    def word_str(self):
        return _content_to_str_(self.word_type, self.word)


class UniqueKeywordCountResult:
    KEY_WORD = "w"
    KEY_WORD_TYPE = "wt"

    KEY_COUNT_USAGE = "cu"
    KEY_COUNT_MODULE = "cm"

    def __init__(self, crs, limit: Optional[int] = None):
        self.data = []

        usage_key = UniqueKeywordCountResult.KEY_COUNT_USAGE

        for rank, d in enumerate_ranking(crs, is_tie=lambda cur, prv: cur[usage_key] == prv[usage_key]):
            self.data.append(
                UniqueKeywordCountEntry(
                    word=d[OID_KEY][UniqueKeywordCountResult.KEY_WORD],
                    word_type=d[OID_KEY][UniqueKeywordCountResult.KEY_WORD_TYPE],
                    count_usage=d[UniqueKeywordCountResult.KEY_COUNT_USAGE],
                    count_module=d[UniqueKeywordCountResult.KEY_COUNT_MODULE],
                    rank=rank
                )
            )

        self.limit = limit
