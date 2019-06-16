from typing import Tuple

from bson import ObjectId

from JellyBotAPI import SystemConfig
from flags import AutoReplyContentType, PreserializationFailedReason

from ._base import Model, ModelDefaultValueExtension
from .exceptions import PreserializationFailedError
from .field import (
    ObjectIDField, TextField, AutoReplyContentTypeField,
    BooleanField, IntegerField, ArrayField, DateTimeField
)
from .utils import AutoReplyValidators


class AutoReplyContentModel(Model):
    Content = "c"
    ContentType = "t"

    default_vals = (
        (Content, ModelDefaultValueExtension.Required),
        (ContentType, AutoReplyContentType.default())
    )

    def _init_fields_(self, **kwargs):
        self.type = AutoReplyContentTypeField(AutoReplyContentModel.ContentType)
        self.content = TextField(AutoReplyContentModel.Content, maxlen=SystemConfig.AutoReply.MAX_CONTENT_LENGTH,
                                 allow_none=False, regex=r"\w+")

    # noinspection PyAttributeOutsideInit
    def pre_serialize(self):
        if self.type is None:
            self.type = AutoReplyContentType.default()

        if self.content.is_none():
            raise PreserializationFailedError(PreserializationFailedReason.AR_CONTENT_EMPTY)

        valid = AutoReplyValidators.is_valid_content(self.type.value, self.content.value)

        if not valid:
            if self.type == AutoReplyContentType.IMAGE:
                raise PreserializationFailedError(PreserializationFailedReason.AR_CONTENT_NOT_IMAGE)
            elif self.type == AutoReplyContentType.LINE_STICKER:
                raise PreserializationFailedError(PreserializationFailedReason.AR_CONTENT_NOT_LINE_STICKER)


class AutoReplyConnectionModel(Model):
    # DRAFT: AR_CONN MOD - Exclude user function

    KeywordID = "k"
    ResponsesIDs = "r"
    CreatorUserID = "cr"
    Pinned = "p"
    Disabled = "d"
    Private = "pr"
    CoolDownSeconds = "cd"
    CalledCount = "c"
    LastUsed = "l"
    ExcludeUserIDs = "e"
    ChannelIDs = "ch"

    default_vals = (
        (KeywordID, ModelDefaultValueExtension.Required),
        (ResponsesIDs, ModelDefaultValueExtension.Required),
        (CreatorUserID, ModelDefaultValueExtension.Required),
        (Pinned, False),
        (Disabled, False),
        (Private, False),
        (CoolDownSeconds, 0),
        (CalledCount, 0),
        (LastUsed, DateTimeField.none_obj()),
        (ExcludeUserIDs, []),
        (ChannelIDs, []),
    )

    def _init_fields_(self, **kwargs):
        self.keyword_oid = ObjectIDField(AutoReplyConnectionModel.KeywordID, readonly=True)
        self.responses_oids = \
            ArrayField(AutoReplyConnectionModel.ResponsesIDs, ObjectId, max_len=SystemConfig.AutoReply.MAX_RESPONSES)
        self.creator_oid = ObjectIDField(AutoReplyConnectionModel.CreatorUserID, readonly=True)
        self.pinned = BooleanField(AutoReplyConnectionModel.Pinned, readonly=True)
        self.disabled = BooleanField(AutoReplyConnectionModel.Disabled, readonly=True)
        self.private = BooleanField(AutoReplyConnectionModel.Private, readonly=True)
        self.cooldown_sec = IntegerField(AutoReplyConnectionModel.CoolDownSeconds, readonly=True)
        self.called_count = IntegerField(AutoReplyConnectionModel.CalledCount, readonly=True)
        self.last_used = DateTimeField(AutoReplyConnectionModel.LastUsed, readonly=True, allow_none=False)
        self.exclude_user_oids = ArrayField(AutoReplyConnectionModel.ExcludeUserIDs, ObjectId, allow_none=True)
        self.channel_ids = ArrayField(AutoReplyConnectionModel.ChannelIDs, ObjectId, allow_none=False)

    @property
    def creation_time(self):
        return self.id.value.generation_time


class AutoReplyBundle(Model):
    Name = "n"
    TagIDs = "t"  # TODO: AR_CONN UTILS - Create model for tags
    ConnectionIDs = "c"

    @property
    def default_vals(self) -> Tuple:
        return (
            (AutoReplyBundle.Name, None),
            (AutoReplyBundle.TagIDs, []),
            (AutoReplyBundle.ConnectionIDs, None)
        )

    # TODO: AR_CONN UTILS - Bundle to copy a set of auto reply connections
    def _init_fields_(self, **kwargs):
        pass
