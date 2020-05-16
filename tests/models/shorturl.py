from datetime import datetime, timezone, timedelta
from typing import Dict, Tuple, Any, Type

from bson import ObjectId

from models import Model, ShortUrlRecordModel

from ._test_base import TestModel

__all__ = ["TestShortUrlRecordModel"]


class TestShortUrlRecordModel(TestModel.TestClass):
    CREATOR_OID = ObjectId()
    USED_TS = [datetime.now().replace(tzinfo=timezone.utc),
               (datetime.now() + timedelta(days=1)).replace(tzinfo=timezone.utc)]

    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return ShortUrlRecordModel

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("cd", "Code"): "ABCDEF",
            ("tgt", "Target"): "https://google.com",
            ("cr", "CreatorOid"): TestShortUrlRecordModel.CREATOR_OID
        }

    @classmethod
    def get_default(cls) -> Dict[Tuple[str, str], Tuple[Any, Any]]:
        return {
            ("d", "Disabled"): (False, True),
            ("ts", "UsedTimestamp"): ([], TestShortUrlRecordModel.USED_TS)
        }
