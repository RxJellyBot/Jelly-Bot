from typing import Tuple, Dict, Any, Type, List
from datetime import datetime, timezone

from bson import ObjectId

from flags import AutoReplyContentType, ModelValidityCheckResult
from models import Model, AutoReplyModuleModel, AutoReplyContentModel
from models.field.exceptions import FieldEmptyValueNotAllowed
from models.exceptions import ModelConstructionError, InvalidModelError

from ._test_base import TestModel

__all__ = ["TestAutoReplyModuleModel", "TestAutoReplyContentModel"]


# region AutoReplyContentModel

class TestAutoReplyContentModel(TestModel.TestClass):
    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return AutoReplyContentModel

    @classmethod
    def get_default(cls) -> Dict[Tuple[str, str], Tuple[Any, Any]]:
        return {("t", "ContentType"): (AutoReplyContentType.TEXT, AutoReplyContentType.IMAGE)}

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {("c", "Content"): "https://i.imgur.com/p7qm0vx.jpg"}

    @classmethod
    def get_required_invalid(cls) -> List[Tuple[Dict[Tuple[str, str], Any], Type[ModelConstructionError]]]:
        return [
            (
                {("c", "Content"): "87A", ("t", "ContentType"): AutoReplyContentType.LINE_STICKER},
                InvalidModelError
            ),
            (
                {("c", "Content"): "https://google.com", ("t", "ContentType"): AutoReplyContentType.IMAGE},
                InvalidModelError
            ),
            (
                {("c", "Content"): "", ("t", "ContentType"): AutoReplyContentType.TEXT},
                FieldEmptyValueNotAllowed
            )
        ]

    def test_validity_check(self):
        data = (
            (AutoReplyContentType.IMAGE, "https://i.imgur.com/o4vvhXy.jpg", "https://google.com",
             ModelValidityCheckResult.X_AR_CONTENT_NOT_IMAGE),
            (AutoReplyContentType.TEXT, "A", "", None),
            (AutoReplyContentType.LINE_STICKER, "34404512", "87A",
             ModelValidityCheckResult.X_AR_CONTENT_NOT_LINE_STICKER)
        )

        for content_type, content_init, content_new, validity_result in data:
            with self.subTest(content_type=content_type, content_new=content_new):
                mdl = self.get_constructed_model(c=content_init, t=content_type)

                # Some exception may happen when setting the value, this is the expected behavior
                try:
                    mdl.content = content_new
                except Exception:
                    continue

                # If the content can be set, it should invalidate the model
                actual_result = mdl.perform_validity_check()

                self.assertEquals(actual_result, validity_result, actual_result)

    def test_content_html(self):
        """Only testing if the content can be outputted without exception."""
        mdls = (
            AutoReplyContentModel(Content="X", ContentType=AutoReplyContentType.TEXT),
            AutoReplyContentModel(Content="https://i.imgur.com/o4vvhXy.jpg", ContentType=AutoReplyContentType.IMAGE),
            AutoReplyContentModel(Content="34404512", ContentType=AutoReplyContentType.LINE_STICKER),
        )

        for mdl in mdls:
            self.assertIsNotNone(mdl.content_html)
            self.assertIsNotNone(str(mdl))


# endregion


# region AutoReplyModuleModel

channel_oid = ObjectId()
creator_oid = ObjectId()
remover_oid = ObjectId()
refer_oid = ObjectId()
excluded_1 = ObjectId()
tag_1 = ObjectId()
last_used = datetime(2020, 5, 10, 10, 36, tzinfo=timezone.utc)
remove_at = datetime(2020, 5, 20, 10, 36, tzinfo=timezone.utc)


class TestAutoReplyModuleModel(TestModel.TestClass):
    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return AutoReplyModuleModel

    @classmethod
    def get_optional(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("rid", "ReferTo"): refer_oid,
            ("rmv", "RemoverOid"): remover_oid
        }

    @classmethod
    def get_default(cls) -> Dict[Tuple[str, str], Tuple[Any, Any]]:
        return {
            ("at", "Active"): (True, False),
            ("p", "Pinned"): (False, True),
            ("pr", "Private"): (False, True),
            ("cd", "CooldownSec"): (0, 10),
            ("e", "ExcludedOids"): ([], [excluded_1]),
            ("t", "TagIds"): ([], [tag_1]),
            ("c", "CalledCount"): (0, 10),
            ("l", "LastUsed"): (datetime.min.replace(tzinfo=timezone.utc), last_used),
            ("rm", "RemovedAt"): (datetime.min.replace(tzinfo=timezone.utc), remove_at)
        }

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("kw", "Keyword"): {"c": "ABC", "t": AutoReplyContentType.TEXT},
            ("rp", "Responses"): [{"c": "DEF", "t": AutoReplyContentType.TEXT}],
            ("ch", "ChannelId"): channel_oid,
            ("cr", "CreatorOid"): creator_oid
        }

    def test_refer(self):
        mdl = self.get_constructed_model()

        oid = ObjectId()
        mdl.refer_to = oid

        self.assertTrue(mdl.is_reference)
        self.assertEquals(mdl.refer_oid, oid)

    def test_kw_repr(self):
        mdl = self.get_constructed_model()

        self.assertIsNotNone(mdl.keyword_repr)

    def test_last_used_repr(self):
        mdl = self.get_constructed_model()
        self.assertEquals(mdl.last_used, datetime.min.replace(tzinfo=timezone.utc))

        mdl.last_used = last_used

        self.assertEquals(mdl.last_used, last_used)

    def test_remove_at_repr(self):
        mdl = self.get_constructed_model()
        self.assertEquals(mdl.removed_at, datetime.min.replace(tzinfo=timezone.utc))

        mdl.removed_at = remove_at
        self.assertEquals(mdl.removed_at, remove_at)

# endregion
