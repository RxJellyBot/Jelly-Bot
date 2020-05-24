from datetime import datetime, timedelta
from typing import Type, Optional

from bson import ObjectId

from flags import Execode, ExecodeCompletionOutcome
from mongodb.factory.results import (
    EnqueueExecodeResult, CompleteExecodeResult, GetExecodeEntryResult,
    OperationOutcome, GetOutcome
)
from models import ExecodeEntryModel, Model
from models.exceptions import ModelConstructionError
from mongodb.utils import CursorWithCount
from mongodb.helper import ExecodeRequiredKeys, ExecodeCompletor
from mongodb.exceptions import NoCompleteActionError, ExecodeCollationError
from JellyBot.systemconfig import Database

from ._base import BaseCollection
from .mixin import GenerateTokenMixin


DB_NAME = "execode"


class ExecodeManager(GenerateTokenMixin, BaseCollection):
    token_length = ExecodeEntryModel.EXECODE_LENGTH
    token_key = ExecodeEntryModel.Execode.key

    database_name = DB_NAME
    collection_name = "main"
    model_class = ExecodeEntryModel

    def __init__(self):
        super().__init__()
        self.create_index(ExecodeEntryModel.Execode.key, name="Execode", unique=True)
        self.create_index(ExecodeEntryModel.Timestamp.key,
                          name="Timestamp (for TTL)", expireAfterSeconds=Database.ExecodeExpirySeconds)

    def enqueue_execode(
            self, root_uid: ObjectId, execode_type: Execode, data_cls: Type[Model] = None, **data_kw_args) -> \
            EnqueueExecodeResult:
        execode = self.generate_hex_token()
        now = datetime.utcnow()

        if data_cls is not None:
            data = data_cls(**data_kw_args)
        else:
            data = data_kw_args

        entry, outcome, ex = self.insert_one_data(
            CreatorOid=root_uid, Execode=execode, ActionType=execode_type, Timestamp=now, Data=data)

        return EnqueueExecodeResult(outcome, ex, execode, now + timedelta(seconds=Database.ExecodeExpirySeconds))

    def get_queued_execodes(self, root_uid: ObjectId) -> CursorWithCount:
        filter_ = {ExecodeEntryModel.CreatorOid.key: root_uid}
        return CursorWithCount(self.find(filter_), self.count_documents(filter_), parse_cls=ExecodeEntryModel)

    def clear_all_execodes(self, root_uid: ObjectId):
        self.delete_many({ExecodeEntryModel.CreatorOid.key: root_uid})

    def get_execode_entry(self, execode: str, action: Execode) -> GetExecodeEntryResult:
        cond = {ExecodeEntryModel.Execode.key: execode}

        if action:
            cond[ExecodeEntryModel.ActionType.key] = action

        # noinspection PyTypeChecker
        ret: ExecodeEntryModel = self.find_one_casted(cond, parse_cls=ExecodeEntryModel)

        if ret:
            return GetExecodeEntryResult(GetOutcome.O_CACHE_DB, model=ret)
        else:
            if self.count_documents({ExecodeEntryModel.Execode.key: execode}) > 0:
                return GetExecodeEntryResult(GetOutcome.X_EXECODE_TYPE_INCORRECT)
            else:
                return GetExecodeEntryResult(GetOutcome.X_NOT_FOUND_ABORTED_INSERT)

    def remove_execode(self, execode: str):
        self.delete_one({ExecodeEntryModel.Execode.key: execode})

    def complete_execode(self, execode: str, execode_kwargs: dict, action: Execode = None) -> CompleteExecodeResult:
        """
        Finalize the pending Execode.

        :param execode: The Execode.
        :param execode_kwargs: Arguments for completing the Execode. Could carry more data than the required keys
            of the type of the execode to be completed.
        :param action: Execode action type
        """
        lacking_keys = set()
        ex = None
        tk_model: Optional[ExecodeEntryModel] = None
        cmpl_outcome = None

        # Force type to be dict because the type of `execode_kwargs` might be django QueryDict
        if type(execode_kwargs) != dict:
            execode_kwargs = dict(execode_kwargs)

        if not execode:
            outcome = OperationOutcome.X_EXECODE_EMPTY
            return CompleteExecodeResult(outcome, None, None, set(), ExecodeCompletionOutcome.X_NOT_EXECUTED)

        # Not using self.find_one_casted for catching `ModelConstructionError`
        get_execode = self.get_execode_entry(execode, action)

        if get_execode.success:
            tk_model = get_execode.model

            try:
                required_keys = ExecodeRequiredKeys.get_required_keys(tk_model.action_type)

                lacking_keys = required_keys.difference(execode_kwargs)
                if len(lacking_keys) == 0:
                    try:
                        cmpl_outcome = ExecodeCompletor.complete_execode(tk_model, execode_kwargs)

                        if cmpl_outcome.is_success:
                            outcome = OperationOutcome.O_COMPLETED
                            self.remove_execode(execode)
                        else:
                            outcome = OperationOutcome.X_COMPLETION_FAILED
                    except NoCompleteActionError as e:
                        outcome = OperationOutcome.X_NO_COMPLETE_ACTION
                        ex = e
                    except ExecodeCollationError as e:
                        outcome = OperationOutcome.X_COLLATION_ERROR
                        ex = e
                    except Exception as e:
                        outcome = OperationOutcome.X_COMPLETION_ERROR
                        ex = e
                else:
                    outcome = OperationOutcome.X_KEYS_LACKING
            except ModelConstructionError as e:
                outcome = OperationOutcome.X_CONSTRUCTION_ERROR
                ex = e
        else:
            if get_execode.outcome == GetOutcome.X_NOT_FOUND_ABORTED_INSERT:
                outcome = OperationOutcome.X_EXECODE_NOT_FOUND
            elif get_execode.outcome == GetOutcome.X_EXECODE_TYPE_INCORRECT:
                outcome = OperationOutcome.X_EXECODE_TYPE_MISMATCH
            else:
                outcome = OperationOutcome.X_ERROR

        return CompleteExecodeResult(outcome, ex, tk_model, lacking_keys, cmpl_outcome)


_inst = ExecodeManager()
