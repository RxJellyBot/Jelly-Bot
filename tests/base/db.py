import os
from abc import ABC, abstractmethod
from datetime import datetime

from django.test import TestCase


class TestWithDatabase(TestCase, ABC):
    _org_os_ = None

    @classmethod
    def setUpClass(cls):
        cls._org_os_ = os.environ.get("MONGO_DB")
        os.environ["MONGO_DB"] = f"Test{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        cls.setUpDataClass()

    @classmethod
    def tearDownClass(cls):
        del os.environ["MONGO_DB"]
        if cls._org_os_:
            os.environ["MONGO_DB"] = cls._org_os_

        cls.tearDownDataClass()

    def setUp(self) -> None:
        self.setUpData()

    def tearDown(self) -> None:
        self.tearDownData()

    @abstractmethod
    def setUpData(self):
        raise NotImplementedError()

    @abstractmethod
    def tearDownData(self):
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def setUpDataClass(cls):
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def tearDownDataClass(cls):
        raise NotImplementedError()
