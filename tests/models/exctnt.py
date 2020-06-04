from datetime import datetime, timedelta, timezone
from typing import Dict, Tuple, Any, Type

from bson import ObjectId

from flags import ExtraContentType
from models import Model, ExtraContentModel
from JellyBot.systemconfig import Database

from ._test_base import TestModel

__all__ = ["TestExtraContentModel"]


class TestExtraContentModel(TestModel.TestClass):
    CHANNEL_OID = ObjectId()
    TIMESTAMP = datetime.utcnow().replace(tzinfo=timezone.utc)

    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return ExtraContentModel

    @classmethod
    def get_default(cls) -> Dict[Tuple[str, str], Tuple[Any, Any]]:
        return {
            ("tp", "Type"): (ExtraContentType.default(), ExtraContentType.AUTO_REPLY_SEARCH),
        }

    @classmethod
    def get_optional(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("t", "Title"): "Head",
        }

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("c", "Content"): "ABCD",
            ("e", "Timestamp"): TestExtraContentModel.TIMESTAMP,
            ("ch", "ChannelOid"): TestExtraContentModel.CHANNEL_OID
        }

    def test_expiry(self):
        mdl = self.get_constructed_model()
        self.assertEqual(mdl.expires_on, mdl.timestamp + timedelta(seconds=Database.ExtraContentExpirySeconds))

    def test_content_html(self):
        mdl = self.get_constructed_model(tp=ExtraContentType.AUTO_REPLY_SEARCH)
        self.assertIsNotNone(mdl.content_html)

        mdl = self.get_constructed_model(tp=ExtraContentType.PURE_TEXT, c="AAAAA")
        self.assertEqual("AAAAA", mdl.content_html)

        mdl = self.get_constructed_model(tp=ExtraContentType.EXTRA_MESSAGE, c=[("r", "c")])
        self.assertIsNotNone(mdl.content_html)
