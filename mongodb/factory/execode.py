"""Execode-related data controllers."""
from datetime import timedelta
from typing import Type, Optional, Tuple

from bson import ObjectId
from django.http import QueryDict  # pylint: disable=wrong-import-order

from extutils.dt import now_utc_aware
from flags import Execode, ExecodeCompletionOutcome, ExecodeCollationFailedReason
from mongodb.factory.results import (
    EnqueueExecodeResult, CompleteExecodeResult, GetExecodeEntryResult,
    OperationOutcome, GetOutcome
)
from models import ExecodeEntryModel, Model
from models.exceptions import ModelConstructionError
from mongodb.utils import ExtendedCursor
from mongodb.helper import ExecodeCompletor, ExecodeRequiredKeys
from mongodb.factory.results import WriteOutcome
from mongodb.exceptions import NoCompleteActionError, ExecodeCollationError
from JellyBot.systemconfig import Database

from ._base import BaseCollection
from .mixin import GenerateTokenMixin

__all__ = ("ExecodeManager",)

DB_NAME = "execode"


class _ExecodeManager(GenerateTokenMixin, BaseCollection):
    token_length = ExecodeEntryModel.EXECODE_LENGTH
    token_key = ExecodeEntryModel.Execode.key

    database_name = DB_NAME
    collection_name = "main"
    model_class = ExecodeEntryModel

    def build_indexes(self):
        self.create_index(ExecodeEntryModel.Execode.key, name="Execode", unique=True)
        self.create_index(ExecodeEntryModel.Timestamp.key,
                          name="Timestamp (for TTL)", expireAfterSeconds=Database.ExecodeExpirySeconds)

    def enqueue_execode(
            self, root_uid: ObjectId, execode_type: Execode, data_cls: Type[Model] = None, **data_kw_args) -> \
            EnqueueExecodeResult:
        """
        Enqueue an Execode action.

        :param root_uid: user to execute the enqueued Execode
        :param execode_type: type of the execode
        :param data_cls: model class of the additional data class
        :param data_kw_args: arguments to construct the model
        :return: enqueuing result
        """
        execode = self.generate_hex_token()
        now = now_utc_aware(for_mongo=True)

        if not data_cls and data_kw_args:
            return EnqueueExecodeResult(WriteOutcome.X_NO_MODEL_CLASS)

        if data_cls:
            try:
                data = data_cls(**data_kw_args).to_json()
            except ModelConstructionError as ex:
                return EnqueueExecodeResult(WriteOutcome.X_INVALID_MODEL, ex)
        else:
            data = {}

        if execode_type == Execode.UNKNOWN:
            return EnqueueExecodeResult(WriteOutcome.X_UNKNOWN_EXECODE_ACTION)

        model, outcome, ex = self.insert_one_data(
            CreatorOid=root_uid, Execode=execode, ActionType=execode_type, Timestamp=now, Data=data)

        return EnqueueExecodeResult(
            outcome, ex, model, execode, now + timedelta(seconds=Database.ExecodeExpirySeconds))

    def get_queued_execodes(self, root_uid: ObjectId) -> ExtendedCursor[ExecodeEntryModel]:
        filter_ = {ExecodeEntryModel.CreatorOid.key: root_uid}
        return ExtendedCursor(self.find(filter_), self.count_documents(filter_), parse_cls=ExecodeEntryModel)

    def get_execode_entry(self, execode: str, action: Optional[Execode] = None) -> GetExecodeEntryResult:
        cond = {ExecodeEntryModel.Execode.key: execode}

        if action:
            cond[ExecodeEntryModel.ActionType.key] = action

        ret: ExecodeEntryModel = self.find_one_casted(cond)

        if ret:
            return GetExecodeEntryResult(GetOutcome.O_CACHE_DB, model=ret)
        else:
            if self.count_documents({ExecodeEntryModel.Execode.key: execode}) > 0:
                return GetExecodeEntryResult(GetOutcome.X_EXECODE_TYPE_MISMATCH)
            else:
                return GetExecodeEntryResult(GetOutcome.X_NOT_FOUND_ABORTED_INSERT)

    def remove_execode(self, execode: str):
        self.delete_one({ExecodeEntryModel.Execode.key: execode})

    def _attempt_complete(self, execode: str, tk_model: ExecodeEntryModel, execode_kwargs: QueryDict) \
            -> Tuple[OperationOutcome, Optional[ExecodeCompletionOutcome], Optional[Exception]]:
        cmpl_outcome = ExecodeCompletionOutcome.X_NOT_EXECUTED
        ex = None

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
            if e.err_code == ExecodeCollationFailedReason.MISSING_KEY:
                outcome = OperationOutcome.X_MISSING_ARGS
            else:
                outcome = OperationOutcome.X_COLLATION_ERROR

            ex = e
        except Exception as e:
            outcome = OperationOutcome.X_COMPLETION_ERROR
            ex = e

        return outcome, cmpl_outcome, ex

    def complete_execode(self, execode: str, execode_kwargs: dict, action: Optional[Execode] = None) \
            -> CompleteExecodeResult:
        """
        Finalize the pending Execode.

        :param execode: execode of the action to be completed
        :param execode_kwargs: arguments may be needed to complete the Execode action
        :param action: type of the Execode action
        """
        ex = None
        tk_model: Optional[ExecodeEntryModel] = None

        # Force type to be dict because the type of `execode_kwargs` might be django QueryDict
        if isinstance(execode_kwargs, QueryDict):
            execode_kwargs = execode_kwargs.dict()

        if not execode:
            outcome = OperationOutcome.X_EXECODE_EMPTY
            return CompleteExecodeResult(outcome, None, None, set(), ExecodeCompletionOutcome.X_NOT_EXECUTED)

        # Not using self.find_one_casted for catching `ModelConstructionError`
        get_execode = self.get_execode_entry(execode, action)

        if get_execode.success:
            tk_model = get_execode.model

            # Check for missing keys
            if missing_keys := ExecodeRequiredKeys.get_required_keys(tk_model.action_type).difference(execode_kwargs):
                return CompleteExecodeResult(OperationOutcome.X_MISSING_ARGS, None, tk_model, missing_keys,
                                             ExecodeCompletionOutcome.X_MISSING_ARGS)

            try:
                outcome, cmpl_outcome, ex = self._attempt_complete(execode, tk_model, execode_kwargs)
            except ModelConstructionError as e:
                outcome = OperationOutcome.X_CONSTRUCTION_ERROR
                cmpl_outcome = ExecodeCompletionOutcome.X_MODEL_CONSTRUCTION
                ex = e
        else:
            cmpl_outcome = ExecodeCompletionOutcome.X_EXECODE_NOT_FOUND

            if get_execode.outcome == GetOutcome.X_NOT_FOUND_ABORTED_INSERT:
                outcome = OperationOutcome.X_EXECODE_NOT_FOUND
            elif get_execode.outcome == GetOutcome.X_EXECODE_TYPE_MISMATCH:
                outcome = OperationOutcome.X_EXECODE_TYPE_MISMATCH
            else:
                outcome = OperationOutcome.X_ERROR

        return CompleteExecodeResult(outcome, ex, tk_model, set(), cmpl_outcome)


ExecodeManager = _ExecodeManager()
