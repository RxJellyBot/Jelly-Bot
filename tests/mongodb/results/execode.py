from datetime import datetime
from typing import Type, Tuple, Any

from bson import ObjectId

from JellyBot.api.static import result
from flags import Execode, ExecodeCompletionOutcome
from models import Model, ExecodeEntryModel
from mongodb.factory.results import (
    BaseResult, ModelResult, OperationOutcome,
    EnqueueExecodeResult, GetExecodeEntryResult, CompleteExecodeResult
)
from tests.base import TestOnModelResult

__all__ = ["TestEnqueueExecodeResult", "TestGetExecodeEntryResult", "TestCompleteExecodeResult"]

mdl = ExecodeEntryModel(Execode="ABCDEFGHIJ", CreatorOid=ObjectId(),
                        ActionType=Execode.AR_ADD, Timestamp=datetime.utcnow())


class TestEnqueueExecodeResult(TestOnModelResult.TestClass):
    EXPIRY = datetime.utcnow()

    @classmethod
    def get_result_class(cls) -> Type[BaseResult]:
        return EnqueueExecodeResult

    @classmethod
    def get_constructed_model(cls) -> Model:
        return mdl

    @classmethod
    def result_args_no_error(cls) -> Tuple[Any, ...]:
        return "ABCDEFGHIJ", TestEnqueueExecodeResult.EXPIRY

    @classmethod
    def result_args_has_error(cls) -> Tuple[Any, ...]:
        return None, None

    @classmethod
    def default_serialized(cls):
        d = super().default_serialized()
        d.update({result.ExecodeResponse.EXECODE: "ABCDEFGHIJ",
                  result.ExecodeResponse.EXPIRY: TestEnqueueExecodeResult.EXPIRY})
        return d

    @classmethod
    def default_serialized_error(cls):
        d = super().default_serialized_error()
        d.update({result.ExecodeResponse.EXECODE: None,
                  result.ExecodeResponse.EXPIRY: None})
        return d


class TestGetExecodeEntryResult(TestOnModelResult.TestClass):
    @classmethod
    def get_result_class(cls) -> Type[ModelResult]:
        return GetExecodeEntryResult

    @classmethod
    def get_constructed_model(cls) -> Model:
        return mdl


class TestCompleteExecodeResult(TestOnModelResult.TestClass):
    @classmethod
    def get_result_class(cls) -> Type[ModelResult]:
        return CompleteExecodeResult

    @classmethod
    def result_args_no_error(cls) -> Tuple[Any, ...]:
        return set(), ExecodeCompletionOutcome.O_OK

    @classmethod
    def result_args_has_error(cls) -> Tuple[Any, ...]:
        return {"a", "b"}, ExecodeCompletionOutcome.X_IDT_INTEGRATION_FAILED

    @classmethod
    def get_constructed_model(cls) -> Model:
        return mdl

    @classmethod
    def default_serialized(cls):
        d = super().default_serialized()
        d.update({result.ExecodeResponse.LACKING_KEYS: set(),
                  result.ExecodeResponse.COMPLETION_OUTCOME: ExecodeCompletionOutcome.O_OK})
        return d

    @classmethod
    def default_serialized_error(cls):
        d = super().default_serialized_error()
        d.update({result.ExecodeResponse.LACKING_KEYS: {"a", "b"},
                  result.ExecodeResponse.COMPLETION_OUTCOME: ExecodeCompletionOutcome.X_IDT_INTEGRATION_FAILED})
        return d

    def test_is_success_extra(self):
        data = (
            (
                CompleteExecodeResult(
                    OperationOutcome.O_COMPLETED, None, mdl, set(), ExecodeCompletionOutcome.O_OK),
                True
            ),
            (
                CompleteExecodeResult(
                    OperationOutcome.X_NOT_EXECUTED, None, mdl, set(), ExecodeCompletionOutcome.O_OK),
                False
            ),
            (
                CompleteExecodeResult(
                    OperationOutcome.O_COMPLETED, None, mdl, {"A"}, ExecodeCompletionOutcome.O_OK),
                False
            ),
            (
                CompleteExecodeResult(
                    OperationOutcome.X_NOT_EXECUTED, None, mdl, {"A"}, ExecodeCompletionOutcome.O_OK),
                False
            ),
            (
                CompleteExecodeResult(
                    OperationOutcome.O_COMPLETED, None, mdl, set(), ExecodeCompletionOutcome.X_NOT_EXECUTED),
                True
            ),
            (
                CompleteExecodeResult(
                    OperationOutcome.X_NOT_EXECUTED, None, mdl, set(), ExecodeCompletionOutcome.X_NOT_EXECUTED),
                False
            ),
            (
                CompleteExecodeResult(
                    OperationOutcome.O_COMPLETED, None, mdl, {"A"}, ExecodeCompletionOutcome.X_NOT_EXECUTED),
                False
            ),
            (
                CompleteExecodeResult(
                    OperationOutcome.X_NOT_EXECUTED, None, mdl, {"A"}, ExecodeCompletionOutcome.X_NOT_EXECUTED),
                False
            ),
        )

        for actual_result, expected_success in data:
            with self.subTest(result=result, expected_success=expected_success):
                self.assertEqual(actual_result.success, expected_success)
