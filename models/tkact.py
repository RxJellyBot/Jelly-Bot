from datetime import timedelta, datetime
from typing import Optional

from django.utils import timezone

from JellyBotAPI import SystemConfig
from models import Model, ModelDefaultValueExtension
from models.field import TextField, TokenActionField, DateTimeField, DictionaryField, ObjectIDField


class TokenActionModel(Model):
    CreatorOID = "cr"
    Token = "tk"
    ActionType = "a"
    Timestamp = "t"
    Data = "d"

    default_vals = (
        (CreatorOID, ModelDefaultValueExtension.Required),
        (Token, ModelDefaultValueExtension.Required),
        (ActionType, ModelDefaultValueExtension.Required),
        (Timestamp, ModelDefaultValueExtension.Required),
        (Data, None)
    )

    TOKEN_LENGTH = 10

    def _init_fields_(self, **kwargs):
        self.creator_oid = ObjectIDField(TokenActionModel.CreatorOID)
        self.token = TextField(TokenActionModel.Token, regex=fr"\w{{{TokenActionModel.TOKEN_LENGTH}}}",
                               must_have_content=True)
        self.action = TokenActionField(TokenActionModel.ActionType)
        self.timestamp = DateTimeField(TokenActionModel.Timestamp)
        self.data = DictionaryField(TokenActionModel.Data)

    @property
    def expire_time(self) -> Optional[datetime]:
        if self.timestamp and not self.timestamp.is_none():
            return timezone.localtime(self.timestamp.value) + timedelta(
                seconds=SystemConfig.Database.TokenActionExpirySeconds)
        else:
            return None
