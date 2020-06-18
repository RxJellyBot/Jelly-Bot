import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Tuple, Any, Type

from bson import ObjectId

from models import Model, ShortUrlRecordModel
from strres.models import ShortUrl

from tests.base import TestModel

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

    def test_used_count(self):
        mdl = self.get_constructed_model()
        self.assertEqual(mdl.used_count, 0)

        mdl = self.get_constructed_model(manual_default=True)
        self.assertEqual(mdl.used_count, 2)

    def test_shorturl_available(self):
        temp = os.environ.get("SERVICE_SHORT_URL")
        os.environ["SERVICE_SHORT_URL"] = "https://rnnx.cc"

        mdl = self.get_constructed_model()
        self.assertEqual(mdl.short_url, "https://rnnx.cc/ABCDEF")

        if temp:
            os.environ["SERVICE_SHORT_URL"] = temp

    def test_shorturl_unavailable(self):
        temp = os.environ.get("SERVICE_SHORT_URL")
        del os.environ["SERVICE_SHORT_URL"]

        mdl = self.get_constructed_model()
        self.assertEqual(mdl.short_url, ShortUrl.SERVICE_NOT_AVAILABLE)

        if temp:
            os.environ["SERVICE_SHORT_URL"] = temp
