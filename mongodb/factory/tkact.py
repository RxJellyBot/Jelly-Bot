from datetime import datetime, timedelta
from typing import Type, Generator

from bson import ObjectId

from flags import TokenAction, Platform, TokenActionCollationErrorCode
from mongodb.factory import ChannelManager, AutoReplyConnectionManager
from mongodb.factory.results import (
    EnqueueTokenActionResult, CompleteTokenActionResult,
    OperationOutcome, InsertOutcome
)
from models import TokenActionModel, Model, AutoReplyConnectionModel
from JellyBotAPI.SystemConfig import Database
from JellyBotAPI.api.static import param

from ._base import BaseCollection
from ._mixin import GenerateTokenMixin


DB_NAME = "tk_act"


class NoCompleteActionError(Exception):
    def __init__(self, action: TokenAction):
        super().__init__(f"No complete action implemented for {action}.")


class TokenActionCollationError(Exception):
    def __init__(self,
                 action: TokenAction, key: str, err_code: TokenActionCollationErrorCode, inner_ex: Exception = None):
        super().__init__(
            f"Error occurred during collation of action {str(action)} at {key}. (Err #{err_code}, {inner_ex})")


class TokenActionManager(GenerateTokenMixin, BaseCollection):
    token_length = TokenActionModel.TOKEN_LENGTH
    token_key = TokenActionModel.Token

    def __init__(self):
        super().__init__(DB_NAME, "main")
        self.create_index(TokenActionModel.Token, name="Token", unique=True)
        self.create_index(TokenActionModel.Timestamp,
                          name="Timestamp (for TTL)", expireAfterSeconds=Database.TokenActionExpirySeconds)

    def enqueue_action(self, creator: ObjectId, token_action: TokenAction, data_cls: Type[Model], **data_kw_args):
        token = self.generate_hex_token()
        now = datetime.now()

        entry, outcome, ex, insert_result = self.insert_one_data(
            TokenActionModel, creator_oid=creator,
            token=token, action=token_action, timestamp=now, data=data_cls(**data_kw_args).serialize())

        return EnqueueTokenActionResult(outcome, token, now + timedelta(seconds=Database.TokenActionExpirySeconds), ex)

    def get_queued_actions(self, creator_oid: ObjectId) -> Generator:
        csr = self.find({TokenActionModel.CreatorOID: creator_oid})
        for dict_ in csr:
            yield TokenActionModel(**dict_, from_db=True)

    def complete_action(self, token: str, token_args: dict):
        lacking_keys = set()
        cond_dict = {TokenActionModel.Token: token}
        ex = None
        tk_model = None

        if type(token_args) != dict:
            token_args = dict(token_args)

        if token:
            tk_model = self.find_one(cond_dict)

            if tk_model:
                tk_model = TokenActionModel(from_db=True, **tk_model)
                required_keys = TokenActionRequiredKeys.get_required_keys(tk_model.action.value)

                if required_keys == token_args.keys():
                    try:
                        cmpres = TokenActionCompletor.complete_action(tk_model, token_args)

                        if cmpres:
                            outcome = OperationOutcome.SUCCESS_COMPLETED
                            self.delete_one(cond_dict)
                        else:
                            outcome = OperationOutcome.FAILED_COMPLETION_FAILED
                    except NoCompleteActionError as e:
                        outcome = OperationOutcome.FAILED_NO_COMPLETE_ACTION
                        ex = e
                    except TokenActionCollationError as e:
                        outcome = OperationOutcome.FAILED_COLLATION_ERROR
                        ex = e
                    except Exception as e:
                        outcome = OperationOutcome.FAILED_COMPLETION_ERROR
                        ex = e
                else:
                    outcome = OperationOutcome.FAILED_KEYS_LACKING
                    lacking_keys = required_keys.difference(token_args.keys())
            else:
                outcome = OperationOutcome.FAILED_TOKEN_NOT_FOUND
        else:
            outcome = OperationOutcome.FAILED_TOKEN_EMPTY

        return CompleteTokenActionResult(outcome, tk_model, lacking_keys, ex)


class TokenActionCompletor:
    # noinspection PyArgumentList
    @staticmethod
    def complete_action(action_model: TokenActionModel, xparams: dict) -> bool:
        action = action_model.action.value
        xparams = TokenActionParameterCollator.collate_parameters(TokenAction(action_model.action.value), xparams)

        if action == TokenAction.AR_ADD:
            return TokenActionCompletor._token_ar_add(action_model, xparams)
        else:
            raise NoCompleteActionError(action)

    @staticmethod
    def _token_ar_add(action_model: TokenActionModel, xparams: dict):
        conn = AutoReplyConnectionModel(**action_model.data.value, from_db=True, init_oid=False)
        cnl = ChannelManager.register(xparams[param.AutoReply.PLATFORM], xparams[param.AutoReply.CHANNEL_TOKEN])
        success = InsertOutcome.is_success(cnl.outcome)
        if success:
            conn.channel_ids.add_item(cnl.model.id.value)
            success = InsertOutcome.is_success(AutoReplyConnectionManager.add_conn_by_model(conn).outcome)

        return success


class TokenActionParameterCollator:
    @staticmethod
    def collate_parameters(action: TokenAction, xparams: dict) -> dict:
        if action == TokenAction.AR_ADD:
            return TokenActionParameterCollator._token_ar_add(action, xparams)
        else:
            return xparams

    # noinspection PyArgumentList
    @staticmethod
    def _token_ar_add(action: TokenAction, xparams: dict) -> dict:
        k = param.AutoReply.PLATFORM
        if xparams.get(k) is None or len(xparams[k][0]) == 0:
            raise TokenActionCollationError(action, k, TokenActionCollationErrorCode.EMPTY_CONTENT)
        else:
            try:
                xparams[k] = Platform(int(xparams[k][0]))
            except Exception as e:
                raise TokenActionCollationError(action, k, TokenActionCollationErrorCode.MISC, e)

        k = param.AutoReply.CHANNEL_TOKEN
        xparams[k] = xparams[k][0]

        return xparams


class TokenActionRequiredKeys:
    @staticmethod
    def get_required_keys(token_action: TokenAction) -> set:
        st = {param.TokenAction.TOKEN}

        if token_action == TokenAction.AR_ADD:
            st.add(param.AutoReply.CHANNEL_TOKEN)
            st.add(param.AutoReply.PLATFORM)

        return st


_inst = TokenActionManager()
