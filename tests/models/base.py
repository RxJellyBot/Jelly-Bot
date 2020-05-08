from django.test import TestCase

from models import Model


class DummyModel(Model):
    pass


class TestModel(TestCase):
    def test_model(self):
        pass
