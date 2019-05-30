from bson import ObjectId

from JellyBotAPI import SystemConfig

from ._base import Model
from .field import (
    ObjectIDField, TextField, AutoReplyContentTypeField,
    BooleanField, IntegerField, ArrayField, DateTimeField
)


class AutoReplyContentModel(Model):
    Content = "c"
    ContentType = "t"

    def _init_fields_(self, **kwargs):
        self.content = TextField(AutoReplyContentModel.Content, maxlen=SystemConfig.AutoReply.MAX_CONTENT_LENGTH)
        self.type = AutoReplyContentTypeField(AutoReplyContentModel.ContentType)


class AutoReplyConnectionModel(Model):
    # TODO: AR_CONN UTILS - Add Connection on site
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
    TagIDs = "t"
    ConnectionIDs = "c"

    # TODO: AR_CONN UTILS - Bundle to copy a set of auto reply connections
    def _init_fields_(self, **kwargs):
        pass
