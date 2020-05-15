from datetime import datetime, timedelta, timezone
from typing import Dict, Tuple, Any, Type

from bson import ObjectId

from flags import Execode
from models import Model, ExecodeEntryModel
from JellyBot.systemconfig import Database

from ._test_base import TestModel

__all__ = ["TestExecodeEntryModel"]


class TestExecodeEntryModel(TestModel.TestClass):
    CREATOR_OID = ObjectId()
    TIMESTAMP = datetime.now().replace(tzinfo=timezone.utc)

    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return ExecodeEntryModel

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("cr", "CreatorOid"): TestExecodeEntryModel.CREATOR_OID,
            ("tk", "Execode"): "A" * ExecodeEntryModel.EXECODE_LENGTH,
            ("a", "ActionType"): Execode.AR_ADD,
            ("t", "Timestamp"): TestExecodeEntryModel.TIMESTAMP
        }

    @classmethod
    def get_default(cls) -> Dict[Tuple[str, str], Tuple[Any, Any]]:
        return {
            ("d", "Data"): (None, {"A": "B"})
        }

    def test_expiry(self):
        mdl = self.get_constructed_model()
        self.assertEquals(mdl.expire_time,
                          TestExecodeEntryModel.TIMESTAMP + timedelta(seconds=Database.ExecodeExpirySeconds))
