import os
from abc import ABC
from datetime import datetime

from django.test import TestCase


class DatabaseTestMixin(TestCase, ABC):
    _org_os_ = None

    @classmethod
    def setUpClass(cls):
        cls._org_os_ = os.environ.get("MONGO_DB")
        os.environ["MONGO_DB"] = f"Test @ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')}"

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

    def setUpData(self):
        pass

    def tearDownData(self):
        pass

    @classmethod
    def setUpDataClass(cls):
        pass

    @classmethod
    def tearDownDataClass(cls):
        pass
