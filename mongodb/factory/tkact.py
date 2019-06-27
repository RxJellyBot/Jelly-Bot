from datetime import datetime, timedelta
from typing import Type, Iterator

from bson import ObjectId

from flags import TokenAction, Platform, TokenActionCollationFailedReason, TokenActionCompletionOutcome
from mongodb.factory import ChannelManager, AutoReplyModuleManager
from mongodb.factory.results import (
    EnqueueTokenActionResult, CompleteTokenActionResult,
    OperationOutcome
)
from models import TokenActionModel, Model, AutoReplyModuleTokenActionModel
from models.exceptions import ModelConstructionError
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
                 action: TokenAction, key: str, err_code: TokenActionCollationFailedReason, inner_ex: Exception = None):
        super().__init__(
            f"Error occurred during collation of action {str(action)} at {key}. (Err #{err_code}, {inner_ex})")


class TokenActionManager(GenerateTokenMixin, BaseCollection):
    token_length = TokenActionModel.TOKEN_LENGTH
    token_key = TokenActionModel.Token.key

    database_name = DB_NAME
    collection_name = "main"
    model_class = TokenActionModel

    def __init__(self):
        super().__init__()
        self.create_index(TokenActionModel.Token.key, name="Token", unique=True)
        self.create_index(TokenActionModel.Timestamp.key,
                          name="Timestamp (for TTL)", expireAfterSeconds=Database.TokenActionExpirySeconds)

    def enqueue_action(self, creator: ObjectId, token_action: TokenAction, data_cls: Type[Model], **data_kw_args):
        token = self.generate_hex_token()
        now = datetime.utcnow()

        entry, outcome, ex, insert_result = self.insert_one_data(
            TokenActionModel, CreatorOid=creator,
            Token=token, ActionType=token_action, Timestamp=now, Data=data_cls(**data_kw_args))

        return EnqueueTokenActionResult(outcome, token, now + timedelta(seconds=Database.TokenActionExpirySeconds), ex)

    def get_queued_actions(self, creator_oid: ObjectId) -> Iterator[TokenActionModel]:
        csr = self.find({TokenActionModel.CreatorOID.key: creator_oid})
        for dict_ in csr:
            o = TokenActionModel(**dict_, from_db=True)
            yield o

    def complete_action(self, token: str, token_args: dict):
        lacking_keys = set()
        cond_dict = {TokenActionModel.Token.key: token}
        ex = None
        tk_model = None
        cmpl_outcome = None

        if type(token_args) != dict:
            token_args = dict(token_args)

        if token:
            tk_model = self.find_one(cond_dict)

            if tk_model:
                try:
                    tk_model = TokenActionModel(**tk_model, from_db=True)
                    required_keys = TokenActionRequiredKeys.get_required_keys(tk_model.action_type)

                    if required_keys == token_args.keys():
                        try:
                            cmpl_outcome = TokenActionCompletor.complete_action(tk_model, token_args)

                            if cmpl_outcome.is_success:
                                outcome = OperationOutcome.SUCCESS_COMPLETED
                                self.delete_one(cond_dict)
                            else:
                                outcome = OperationOutcome.X_COMPLETION_FAILED
                        except NoCompleteActionError as e:
                            outcome = OperationOutcome.X_NO_COMPLETE_ACTION
                            ex = e
                        except TokenActionCollationError as e:
                            outcome = OperationOutcome.X_COLLATION_ERROR
                            ex = e
                        except Exception as e:
                            outcome = OperationOutcome.X_COMPLETION_ERROR
                            ex = e
                    else:
                        outcome = OperationOutcome.X_KEYS_LACKING
                        lacking_keys = required_keys.difference(token_args.keys())
                except ModelConstructionError:
                    outcome = OperationOutcome.X_CONSTRUCTION_ERROR
            else:
                outcome = OperationOutcome.X_TOKEN_NOT_FOUND
        else:
            outcome = OperationOutcome.X_TOKEN_EMPTY

        return CompleteTokenActionResult(outcome, cmpl_outcome, tk_model, lacking_keys, ex)


class TokenActionCompletor:
    # noinspection PyArgumentList
    @staticmethod
    def complete_action(action_model: TokenActionModel, xparams: dict) -> TokenActionCompletionOutcome:
        action = action_model.action
        xparams = TokenActionParameterCollator.collate_parameters(TokenAction(action_model.action), xparams)

        if action == TokenAction.AR_ADD:
            return TokenActionCompletor._token_ar_add_(action_model, xparams)
        else:
            raise NoCompleteActionError(action)

    @staticmethod
    def _token_ar_add_(action_model: TokenActionModel, xparams: dict) -> TokenActionCompletionOutcome:
        cnl = ChannelManager.register(xparams[param.AutoReply.PLATFORM], xparams[param.AutoReply.CHANNEL_TOKEN])
        if not cnl.success:
            return TokenActionCompletionOutcome.X_AR_REGISTER_CHANNEL

        try:
            conn = AutoReplyModuleTokenActionModel(**action_model.data, from_db=True).to_actual_model(cnl.model.id)
        except ModelConstructionError:
            return TokenActionCompletionOutcome.X_MODEL_CONSTRUCTION

        if not AutoReplyModuleManager.add_conn_by_model(conn).success:
            return TokenActionCompletionOutcome.X_AR_REGISTER_MODULE

        return TokenActionCompletionOutcome.O_OK


class TokenActionParameterCollator:
    @staticmethod
    def collate_parameters(action: TokenAction, xparams: dict) -> dict:
        if action == TokenAction.AR_ADD:
            return TokenActionParameterCollator._token_ar_add_(action, xparams)
        else:
            return xparams

    # noinspection PyArgumentList
    @staticmethod
    def _token_ar_add_(action: TokenAction, xparams: dict) -> dict:
        k = param.AutoReply.PLATFORM
        if xparams.get(k) is None or len(xparams[k][0]) == 0:
            raise TokenActionCollationError(action, k, TokenActionCollationFailedReason.EMPTY_CONTENT)
        else:
            try:
                xparams[k] = Platform(int(xparams[k][0]))
            except Exception as e:
                raise TokenActionCollationError(action, k, TokenActionCollationFailedReason.MISC, e)

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
