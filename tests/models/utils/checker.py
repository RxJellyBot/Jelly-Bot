from django.conf import settings

from extutils.emailutils import EmailServer
from mongodb.factory import BaseCollection
from models import Model, ModelDefaultValueExt
from models.field import IntegerField
from models.utils import ModelFieldChecker
from tests.base import TestDatabaseMixin, TestCase

__all__ = ["TestDataChecker"]


# TEST: `ModelTest` use various fields #244


class ModelTest(Model):
    Field1 = IntegerField("f1", default=7)
    Field2 = IntegerField("f2", default=ModelDefaultValueExt.Required)
    Field3 = IntegerField("f3", default=ModelDefaultValueExt.Optional)
    Field4 = IntegerField("f4")


class CollectionTest(BaseCollection):
    database_name = "testchecker"
    collection_name = "testchecker"
    model_class = ModelTest


ColInst = CollectionTest()


class TestDataChecker(TestDatabaseMixin, TestCase):
    def test_repair_f1(self):
        # Setup data
        ColInst.insert_one({"f2": 5, "f3": 9, "f4": 1})

        # Perform check
        ModelFieldChecker.check(ColInst)

        # Checking results
        self.assertEquals(ColInst.estimated_document_count(), 1, "Data unexpectedly lost.")

        for data in ColInst.find():
            with self.subTest(data=data):
                if "f1" not in data:
                    self.fail("`Field1` not repaired.")

                self.assertEquals(data["f1"], 7)
                self.assertEquals(data["f2"], 5)
                self.assertEquals(data["f3"], 9)
                self.assertEquals(data["f4"], 1)

    def test_repair_f2(self):
        # Setup data
        ColInst.insert_one({"f1": 8, "f3": 9, "f4": 1})

        # Perform check
        ModelFieldChecker.check(ColInst)

        # Checking results
        self.assertEquals(ColInst.estimated_document_count(), 0, "Data not being moved out for repair.")
        self.assertGreater(len(EmailServer.get_mailbox(settings.EMAIL_HOST_USER).mails), 0, "Mail not sent.")

    def test_repair_f3(self):
        # Setup data
        ColInst.insert_one({"f1": 8, "f2": 10, "f4": 1})

        # Perform check
        ModelFieldChecker.check(ColInst)

        # Checking results
        self.assertEquals(ColInst.estimated_document_count(), 1, "Data unexpectedly lost.")

        data = ColInst.find_one()
        self.assertEquals(data["f1"], 8)
        self.assertEquals(data["f2"], 10)
        self.assertTrue("f3" not in data)
        self.assertEquals(data["f4"], 1)

    def test_repair_f4(self):
        # Setup data
        ColInst.insert_one({"f1": 8, "f2": 9, "f3": 1})

        # Perform check
        ModelFieldChecker.check(ColInst)

        # Checking results
        self.assertEquals(ColInst.estimated_document_count(), 1, "Data unexpectedly lost.")

        data = ColInst.find_one()
        self.assertEquals(data["f1"], 8)
        self.assertEquals(data["f2"], 9)
        self.assertEquals(data["f3"], 1)
        self.assertEquals(data["f4"], 0)

    def test_redundant(self):
        # Setup data
        ColInst.insert_one({"f1": 8, "f2": 9, "f3": 1, "f4": 7, "f5": 5})

        # Perform check
        ModelFieldChecker.check(ColInst, check_redundant=True)

        # Checking results
        self.assertEquals(ColInst.estimated_document_count(), 1, "Data unexpectedly lost.")

        data = ColInst.find_one()
        self.assertEquals(data["f1"], 8)
        self.assertEquals(data["f2"], 9)
        self.assertEquals(data["f3"], 1)
        self.assertEquals(data["f4"], 7)
        self.assertFalse("f5" in data)
