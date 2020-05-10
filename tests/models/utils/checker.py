from mongodb.factory import BaseCollection
from models import Model, ModelDefaultValueExt
from models.field import IntegerField
from tests.base import TestDatabaseMixin, TestCase


class ModelTest(Model):
    Field1 = IntegerField("f1", default=ModelDefaultValueExt.Required)
    Field2 = IntegerField("f2", default=ModelDefaultValueExt.Optional)
    Field3 = IntegerField("f3", default=7)
    Field4 = IntegerField("f4")


class CollectionTest(BaseCollection):
    database_name: str = "testchecker"
    collection_name: str = "testchecker"
    model_class: type(Model) = ModelTest


class TestDataChecker(TestDatabaseMixin, TestCase):
    pass
