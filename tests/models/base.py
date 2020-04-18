import os
from abc import ABC
from datetime import datetime

from django.test import TestCase

from models.field import IntegerField
from models import Model


class DummyModel(Model):
    pass


class TestModel(TestCase):
    def test_model(self):
        pass
