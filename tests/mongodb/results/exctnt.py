from datetime import datetime
from typing import Type

from bson import ObjectId
from django.urls import reverse

from JellyBot.systemconfig import HostUrl
from models import Model, ExtraContentModel
from mongodb.factory.results import ModelResult, RecordExtraContentResult, WriteOutcome
from tests.base import TestOnModelResult

__all__ = ["TestRecordExtraContentResult"]


class TestRecordExtraContentResult(TestOnModelResult.TestClass):
    TS = datetime.utcnow()

    @classmethod
    def get_result_class(cls) -> Type[ModelResult]:
        return RecordExtraContentResult

    @classmethod
    def get_constructed_model(cls) -> Model:
        return ExtraContentModel(Content="AAAAA", Timestamp=TestRecordExtraContentResult.TS)

    def test_get_model_id(self):
        oid = ObjectId()
        mdl = ExtraContentModel(Content="AAAAA", Timestamp=TestRecordExtraContentResult.TS)
        mdl.set_oid(oid)
        r = RecordExtraContentResult(WriteOutcome.O_INSERTED, model=mdl)
        self.assertEqual(r.model_id, oid)

        r = RecordExtraContentResult(WriteOutcome.X_NOT_EXECUTED)
        self.assertIsNone(r.model_id, oid)

    def test_get_url(self):
        oid = ObjectId()
        mdl = ExtraContentModel(Content="AAAAA", Timestamp=TestRecordExtraContentResult.TS)
        mdl.set_oid(oid)
        r = RecordExtraContentResult(WriteOutcome.O_INSERTED, model=mdl)
        self.assertEqual(r.url, f'{HostUrl}{reverse("page.extra", kwargs={"page_id": str(oid)})}')

        r = RecordExtraContentResult(WriteOutcome.X_NOT_EXECUTED)
        self.assertEqual(r.url, "")
