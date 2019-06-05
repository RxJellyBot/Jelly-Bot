from datetime import datetime, timedelta
from typing import Type

from mongodb.factory.results import EnqueueTokenActionResult
from models import TokenActionModel, Model
from JellyBotAPI.SystemConfig import Database

from ._base import BaseCollection
from ._mixin import GenerateTokenMixin


DB_NAME = "tk_act"


class TokenActionManager(GenerateTokenMixin, BaseCollection):
    token_length = TokenActionModel.TOKEN_LENGTH
    token_key = TokenActionModel.Token

    def __init__(self):
        super().__init__(DB_NAME, "main", TokenActionModel.Token)
        self.create_index(TokenActionModel.Token, name="Token", unique=True)
        self.create_index(TokenActionModel.Timestamp,
                          name="Timestamp (for TTL)", expireAfterSeconds=Database.TokenActionExpirySeconds)

    def enqueue_action_ar_add(self, token_action, data_cls: Type[Model], **data_kw_args):
        token = self.generate_hex_token()
        now = datetime.now()

        entry, outcome, ex, insert_result = self.insert_one_data(
            TokenActionModel,
            token=token, action=token_action, timestamp=now, data=data_cls(**data_kw_args).serialize())

        return EnqueueTokenActionResult(outcome, token, now + timedelta(seconds=Database.TokenActionExpirySeconds), ex)


_inst = TokenActionManager()
