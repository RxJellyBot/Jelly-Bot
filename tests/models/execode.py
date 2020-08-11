from datetime import timedelta
from typing import Dict, Tuple, Any, Type

from bson import ObjectId

from extutils.dt import now_utc_aware
from flags import Execode, ModelValidityCheckResult
from models import Model, ExecodeEntryModel, AutoReplyModuleExecodeModel, AutoReplyContentModel
from models.exceptions import InvalidModelError
from JellyBot.systemconfig import Database

from tests.base import TestModel

__all__ = ["TestExecodeEntryModel"]


class TestExecodeEntryModel(TestModel.TestClass):
    CREATOR_OID = ObjectId()
    TIMESTAMP = now_utc_aware()

    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return ExecodeEntryModel

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("cr", "CreatorOid"): cls.CREATOR_OID,
            ("tk", "Execode"): "A" * ExecodeEntryModel.EXECODE_LENGTH,
            ("a", "ActionType"): Execode.REGISTER_CHANNEL,
            ("t", "Timestamp"): cls.TIMESTAMP
        }

    @classmethod
    def get_default(cls) -> Dict[Tuple[str, str], Tuple[Any, Any]]:
        return {
            ("d", "Data"): ({}, {"A": "B"})
        }

    def test_expiry(self):
        mdl = self.get_constructed_model()
        self.assertEqual(mdl.expire_time, self.TIMESTAMP + timedelta(seconds=Database.ExecodeExpirySeconds))

    def test_validate_ar_add_valid(self):
        ExecodeEntryModel(
            CreatorOid=self.CREATOR_OID, Execode="A" * ExecodeEntryModel.EXECODE_LENGTH,
            ActionType=Execode.AR_ADD, Timestamp=self.TIMESTAMP,
            Data=AutoReplyModuleExecodeModel(
                Keyword=AutoReplyContentModel(Content="A").to_json(),
                Responses=[AutoReplyContentModel(Content="B").to_json()]
            ).to_json())

    def test_validate_ar_add_invalid(self):
        with self.assertRaises(InvalidModelError) as e:
            ExecodeEntryModel(
                CreatorOid=self.CREATOR_OID, Execode="A" * ExecodeEntryModel.EXECODE_LENGTH,
                ActionType=Execode.AR_ADD, Timestamp=self.TIMESTAMP)

        self.assertEqual(e.exception.reason, ModelValidityCheckResult.X_EXC_DATA_ERROR)

    def test_validate_register_channel(self):
        ExecodeEntryModel(
            CreatorOid=self.CREATOR_OID, Execode="A" * ExecodeEntryModel.EXECODE_LENGTH,
            ActionType=Execode.REGISTER_CHANNEL, Timestamp=self.TIMESTAMP)

    def test_validate_integrate_user_data(self):
        ExecodeEntryModel(
            CreatorOid=self.CREATOR_OID, Execode="A" * ExecodeEntryModel.EXECODE_LENGTH,
            ActionType=Execode.INTEGRATE_USER_DATA, Timestamp=self.TIMESTAMP)

    def test_validate_unknown(self):
        with self.assertRaises(InvalidModelError) as e:
            ExecodeEntryModel(
                CreatorOid=self.CREATOR_OID, Execode="A" * ExecodeEntryModel.EXECODE_LENGTH,
                ActionType=Execode.UNKNOWN, Timestamp=self.TIMESTAMP)

        self.assertEqual(e.exception.reason, ModelValidityCheckResult.X_EXC_ACTION_UNKNOWN)
