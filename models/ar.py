from dataclasses import dataclass
from datetime import timedelta
from typing import Optional, Union, List

from bson import ObjectId

from extutils.dt import localtime
from extutils.line_sticker import LineStickerManager
from JellyBot import systemconfig
from flags import AutoReplyContentType, ModelValidityCheckResult
from models import OID_KEY
from models.exceptions import FieldKeyNotExistError
from models.utils import AutoReplyValidator
from extutils.utils import enumerate_ranking

from ._base import Model
from .field import (
    ObjectIDField, TextField, AutoReplyContentTypeField, ModelField, ModelArrayField,
    BooleanField, IntegerField, ArrayField, DateTimeField, ColorField, ModelDefaultValueExt
)

__all__ = ["AutoReplyContentModel", "AutoReplyModuleModel", "AutoReplyModuleExecodeModel", "AutoReplyModuleTagModel",
           "AutoReplyTagPopularityScore", "UniqueKeywordCountEntry", "UniqueKeywordCountResult"]


def _content_to_str(content_type, content):
    if content_type == AutoReplyContentType.TEXT:
        return content
    else:
        return f"({content_type.key} / {content})"


def _content_to_html(content_type, content):
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
        return _content_to_html(self.content_type, self.content)

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
        return _content_to_str(self.content_type, self.content)


class AutoReplyModuleModel(Model):
    key_kw = "kw"

    # Main
    Keyword = ModelField(key_kw, AutoReplyContentModel, default=ModelDefaultValueExt.Required)
    Responses = ModelArrayField("rp", AutoReplyContentModel, default=ModelDefaultValueExt.Required,
                                max_len=systemconfig.AutoReply.MaxResponses)

    KEY_KW_CONTENT = f"{key_kw}.{AutoReplyContentModel.Content.key}"
    KEY_KW_TYPE = f"{key_kw}.{AutoReplyContentModel.ContentType.key}"
    ChannelOid = ObjectIDField("ch", default=ModelDefaultValueExt.Required)
    Active = BooleanField("at", default=True)

    # Type
    ReferTo = ObjectIDField("rid", allow_none=True, default=ModelDefaultValueExt.Optional)

    # Record
    CreatorOid = ObjectIDField("cr", stores_uid=True, default=ModelDefaultValueExt.Required)
    RemoverOid = ObjectIDField("rmv", stores_uid=True, default=ModelDefaultValueExt.Optional)

    # Property
    Pinned = BooleanField("p")
    Private = BooleanField("pr")
    CooldownSec = IntegerField("cd", positive_only=True)
    ExcludedOids = ArrayField("e", ObjectId, stores_uid=True)
    TagIds = ArrayField("t", ObjectId)

    # Stats
    CalledCount = IntegerField("c")
    LastUsed = DateTimeField("l", allow_none=True)
    RemovedAt = DateTimeField("rm", allow_none=True)

    @property
    def refer_oid(self) -> Optional[ObjectId]:
        try:
            if self.is_reference:
                return self.refer_to
            else:
                return None
        except (KeyError, FieldKeyNotExistError, AttributeError):
            return None

    @property
    def is_reference(self) -> bool:
        try:
            return not self.is_field_none("ReferTo")
        except (KeyError, FieldKeyNotExistError, AttributeError):
            return False

    @property
    def keyword_repr(self) -> str:
        return f"{str(self.keyword)}"

    @property
    def created_at_expr(self) -> str:
        """
        Expression of the module creation timestamp.

        Used in module info displaying on the website.
        """
        return localtime(self.id.generation_time).strftime("%Y-%m-%d %H:%M:%S")

    @property
    def last_used_expr(self) -> Optional[str]:
        """
        Expression of the module last used timestamp.

        Used in module info displaying on the website.
        """
        if self.last_used:
            return localtime(self.last_used).strftime("%Y-%m-%d %H:%M:%S")
        else:
            return None

    @property
    def removed_at_expr(self) -> Optional[str]:
        """
        Expression of the module removal timestamp.

        Used in module info displaying on the website.
        """
        if self.removed_at:
            return localtime(self.removed_at).strftime("%Y-%m-%d %H:%M:%S")
        else:
            return None

    def can_be_used(self, current_time):
        if self.last_used:
            return current_time - self.last_used > timedelta(seconds=self.cooldown_sec)
        else:
            return True


class AutoReplyModuleExecodeModel(Model):
    WITH_OID = False

    Keyword = ModelField(AutoReplyModuleModel.key_kw, AutoReplyContentModel,
                         default=ModelDefaultValueExt.Required)
    Responses = ModelArrayField("rp", AutoReplyContentModel, default=ModelDefaultValueExt.Required,
                                max_len=systemconfig.AutoReply.MaxResponses)
    Pinned = BooleanField("p", readonly=True)
    Private = BooleanField("pr", readonly=True)
    CooldownSec = IntegerField("cd", readonly=True)
    TagIds = ArrayField("t", ObjectId)


class AutoReplyModuleTagModel(Model):
    Name = TextField("n", must_have_content=True, default=ModelDefaultValueExt.Required)
    Color = ColorField("c")


@dataclass
class AutoReplyTagPopularityScore:
    KEY_W_AVG_TIME_DIFF = "w_atd"
    KEY_W_APPEARANCE = "w_app"
    KEY_APPEARANCE = "app"
    SCORE = "sc"

    tag_id: ObjectId
    score: float
    appearances: int
    weighted_avg_time_diff: float
    weighted_appearances: float

    @staticmethod
    def parse(d: dict):
        return AutoReplyTagPopularityScore(
            tag_id=d[OID_KEY],
            score=d[AutoReplyTagPopularityScore.SCORE],
            appearances=d[AutoReplyTagPopularityScore.KEY_APPEARANCE],
            weighted_avg_time_diff=d[AutoReplyTagPopularityScore.KEY_W_AVG_TIME_DIFF],
            weighted_appearances=d[AutoReplyTagPopularityScore.KEY_W_APPEARANCE],
        )


@dataclass
class UniqueKeywordCountEntry:
    word: str
    word_type: Union[int, AutoReplyContentType]
    count_usage: int
    count_module: int
    rank: str

    def __post_init__(self):
        self.word_type = AutoReplyContentType.cast(self.word_type)
        self.word = _content_to_html(self.word_type, self.word)

    @property
    def word_str(self):
        return _content_to_str(self.word_type, self.word)


class UniqueKeywordCountResult:
    KEY_WORD = "w"
    KEY_WORD_TYPE = "wt"

    KEY_COUNT_USAGE = "cu"
    KEY_COUNT_MODULE = "cm"

    def __init__(self, crs, limit: Optional[int] = None):
        self.data: List[UniqueKeywordCountEntry] = []

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
