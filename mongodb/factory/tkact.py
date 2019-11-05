from datetime import datetime, timedelta
from typing import Type, Optional

from bson import ObjectId

from flags import TokenAction
from mongodb.factory.results import (
    EnqueueTokenActionResult, CompleteTokenActionResult, GetTokenActionResult,
    OperationOutcome, GetOutcome
)
from models import TokenActionModel, Model
from models.exceptions import ModelConstructionError
from mongodb.utils import CheckableCursor
from mongodb.helper import TokenActionRequiredKeys, TokenActionCompletor
from mongodb.exceptions import NoCompleteActionError, TokenActionCollationError
from JellyBot.systemconfig import Database

from ._base import BaseCollection
from ._mixin import GenerateTokenMixin


DB_NAME = "tk_act"


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

        entry, outcome, ex = self.insert_one_data(
            CreatorOid=root_uid, Token=token, ActionType=token_action, Timestamp=now, Data=data)

        return EnqueueTokenActionResult(outcome, token, now + timedelta(seconds=Database.TokenActionExpirySeconds), ex)

    def get_queued_actions(self, root_uid: ObjectId) -> CheckableCursor:
        csr = self.find({TokenActionModel.CreatorOid.key: root_uid})
        return CheckableCursor(csr, parse_cls=TokenActionModel)

    def clear_all_token_actions(self, root_uid: ObjectId):
        self.delete_many({TokenActionModel.CreatorOid.key: root_uid})

    def get_token_action(self, token: str, action: TokenAction) -> GetTokenActionResult:
        cond = {TokenActionModel.Token.key: token}

        if action:
            cond[TokenActionModel.ActionType.key] = action

        ret = self.find_one_casted(cond, parse_cls=TokenActionModel)

        if ret:
            return GetTokenActionResult(GetOutcome.O_CACHE_DB, ret)
        else:
            if self.count_documents({TokenActionModel.Token.key: token}) > 0:
                return GetTokenActionResult(GetOutcome.X_TOKENACTION_TYPE_INCORRECT, None)
            else:
                return GetTokenActionResult(GetOutcome.X_NOT_FOUND_ABORTED_INSERT, None)

    def remove_token_action(self, token: str):
        self.delete_one({TokenActionModel.Token.key: token})

    def complete_action(self, token: str, token_kwargs: dict, action: TokenAction = None) -> CompleteTokenActionResult:
        """
        Finalize the pending token action.

        :param token: Token.
        :param token_kwargs: Arguments for completing the token action. Could carry more data than the required keys
            of the type of the token action to be completed.
        """
        lacking_keys = set()
        ex = None
        tk_model: Optional[TokenActionModel] = None
        cmpl_outcome = None

        # Force type to be dict because the type of `token_kwargs` might be django QueryDict
        if type(token_kwargs) != dict:
            token_kwargs = dict(token_kwargs)

        if token:
            # Not using self.find_one_casted for catching `ModelConstructionError`
            get_tkact = self.get_token_action(token, action)

            if get_tkact.success:
                # noinspection PyTypeChecker
                tk_model = get_tkact.model

                try:
                    required_keys = TokenActionRequiredKeys.get_required_keys(tk_model.action_type)

                    lacking_keys = required_keys.difference(token_kwargs.keys())
                    if len(lacking_keys) == 0:
                        try:
                            cmpl_outcome = TokenActionCompletor.complete_action(tk_model, token_kwargs)

                            if cmpl_outcome.is_success:
                                outcome = OperationOutcome.O_COMPLETED
                                self.remove_token_action(token)
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
                except ModelConstructionError:
                    outcome = OperationOutcome.X_CONSTRUCTION_ERROR
            else:
                if get_tkact.outcome == GetOutcome.X_NOT_FOUND_ABORTED_INSERT:
                    outcome = OperationOutcome.X_TOKEN_NOT_FOUND
                elif get_tkact.outcome == GetOutcome.X_TOKENACTION_TYPE_INCORRECT:
                    outcome = OperationOutcome.X_TOKEN_TYPE_MISMATCH
                else:
                    outcome = OperationOutcome.X_ERROR
        else:
            outcome = OperationOutcome.X_TOKEN_EMPTY

        return CompleteTokenActionResult(outcome, cmpl_outcome, tk_model, lacking_keys, ex)


_inst = TokenActionManager()
