from datetime import datetime, timedelta
from typing import Type

from bson import ObjectId

from flags import TokenAction, Platform, TokenActionCollationFailedReason, TokenActionCompletionOutcome
from mongodb.factory import ChannelManager, AutoReplyManager, ProfileManager
from mongodb.factory.results import (
    EnqueueTokenActionResult, CompleteTokenActionResult,
    OperationOutcome
)
from models import TokenActionModel, Model, AutoReplyModuleTokenActionModel
from models.exceptions import ModelConstructionError
from mongodb.utils import CheckableCursor, UserIdentityIntegrationHelper
from JellyBot.systemconfig import Database
from JellyBot.api.static import param

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
            f"Error occurred during collation of action {str(action)} at {key}. (Err Reason {err_code}, {inner_ex})")


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

    def enqueue_action(
            self, root_uid: ObjectId, token_action: TokenAction, data_cls: Type[Model] = None, **data_kw_args) -> \
            EnqueueTokenActionResult:
        token = self.generate_hex_token()
        now = datetime.utcnow()

        if data_cls is not None:
            data = data_cls(**data_kw_args)
        else:
            data = data_kw_args

        entry, outcome, ex, insert_result = self.insert_one_data(
            TokenActionModel, CreatorOid=root_uid,
            Token=token, ActionType=token_action, Timestamp=now, Data=data)

        return EnqueueTokenActionResult(outcome, token, now + timedelta(seconds=Database.TokenActionExpirySeconds), ex)

    def get_queued_actions(self, root_uid: ObjectId) -> CheckableCursor:
        csr = self.find({TokenActionModel.CreatorOid.key: root_uid})
        return CheckableCursor(csr, parse_cls=TokenActionModel)

    def clear_all_token_actions(self, root_uid: ObjectId):
        self.delete_many({TokenActionModel.CreatorOid.key: root_uid})

    def complete_action(self, token: str, token_kwargs: dict) -> CompleteTokenActionResult:
        lacking_keys = set()
        cond_dict = {TokenActionModel.Token.key: token}
        ex = None
        tk_model = None
        cmpl_outcome = None

        # Force type to be dict because the type of `token_kwargs` might be django QueryDict
        if type(token_kwargs) != dict:
            token_kwargs = dict(token_kwargs)

        if token:
            # Not using self.find_one_casted for catching `ModelConstructionError`
            tk_model = self.find_one(cond_dict)

            if tk_model:
                try:
                    tk_model = TokenActionModel(**tk_model, from_db=True)
                    required_keys = TokenActionRequiredKeys.get_required_keys(tk_model.action_type)

                    if required_keys == token_kwargs.keys():
                        try:
                            cmpl_outcome = TokenActionCompletor.complete_action(tk_model, token_kwargs)

                            if cmpl_outcome.is_success:
                                outcome = OperationOutcome.O_COMPLETED
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
                        lacking_keys = required_keys.difference(token_kwargs.keys())
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
        action = action_model.action_type
        xparams = TokenActionParameterCollator.collate_parameters(TokenAction(action), xparams)

        # TEST: Test token actions
        if action == TokenAction.AR_ADD:
            return TokenActionCompletor._token_ar_add_(action_model, xparams)
        elif action == TokenAction.REGISTER_CHANNEL:
            return TokenActionCompletor._token_register_channel_(action_model, xparams)
        elif action == TokenAction.INTEGRATE_USER_IDENTITY:
            return TokenActionCompletor._token_integrate_identity_(action_model, xparams)
        else:
            raise NoCompleteActionError(action)

    @staticmethod
    def _token_ar_add_(action_model: TokenActionModel, xparams: dict) -> TokenActionCompletionOutcome:
        cnl = ChannelManager.register(xparams[param.AutoReply.PLATFORM], xparams[param.AutoReply.CHANNEL_TOKEN])
        if not cnl.success:
            return TokenActionCompletionOutcome.X_AR_REGISTER_CHANNEL

        try:
            conn = AutoReplyModuleTokenActionModel(**action_model.data, from_db=True).to_actual_model(
                cnl.model.id, action_model.creator_oid)
        except Exception:
            return TokenActionCompletionOutcome.X_MODEL_CONSTRUCTION

        if not AutoReplyManager.add_conn_by_model(conn).success:
            return TokenActionCompletionOutcome.X_AR_REGISTER_MODULE

        return TokenActionCompletionOutcome.O_OK

    @staticmethod
    def _token_register_channel_(action_model: TokenActionModel, xparams: dict) -> TokenActionCompletionOutcome:
        try:
            channel_data = ChannelManager.register(
                xparams[param.TokenAction.PLATFORM], xparams[param.TokenAction.CHANNEL_TOKEN])
        except Exception:
            return TokenActionCompletionOutcome.X_IDT_CHANNEL_ERROR

        if channel_data:
            try:
                ProfileManager.register_new_default(channel_data.model.id, action_model.creator_oid)
            except Exception:
                return TokenActionCompletionOutcome.X_IDT_REGISTER_DEFAULT_PROFILE
        else:
            return TokenActionCompletionOutcome.X_IDT_CHANNEL_NOT_FOUND

        return TokenActionCompletionOutcome.O_OK

    @staticmethod
    def _token_integrate_identity_(action_model: TokenActionModel, xparams: dict) -> TokenActionCompletionOutcome:
        try:
            success = UserIdentityIntegrationHelper.integrate(
                action_model.creator_oid, xparams.get(xparams[param.TokenAction.USER_OID]))
        except Exception:
            return TokenActionCompletionOutcome.X_IDT_INTEGRATION_ERROR

        if not success:
            return TokenActionCompletionOutcome.X_IDT_INTEGRATION_FAILED

        return TokenActionCompletionOutcome.O_OK


class TokenActionParameterCollator:
    @staticmethod
    def collate_parameters(action: TokenAction, xparams: dict) -> dict:
        if action == TokenAction.AR_ADD:
            return TokenActionParameterCollator._token_ar_add_(action, xparams)
        elif action == TokenAction.REGISTER_CHANNEL:
            return TokenActionParameterCollator._token_conn_channel_(xparams)
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

    # noinspection PyArgumentList
    @staticmethod
    def _token_conn_channel_(xparams: dict) -> dict:
        return {k: v[0] if isinstance(v, list) else v for k, v in xparams.items()}


class TokenActionRequiredKeys:
    @staticmethod
    def get_required_keys(token_action: TokenAction) -> set:
        st = {param.TokenAction.TOKEN}

        if token_action == TokenAction.AR_ADD:
            st.add(param.AutoReply.CHANNEL_TOKEN)
            st.add(param.AutoReply.PLATFORM)
        elif token_action == TokenAction.REGISTER_CHANNEL:
            st.add(param.TokenAction.CHANNEL_TOKEN)
            st.add(param.TokenAction.PLATFORM)

        return st


_inst = TokenActionManager()
