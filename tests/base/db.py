import os
import sys
from abc import ABC
from typing import final

import pymongo

from extutils import exec_timing_result
from mongodb.factory import single_db_name

from tests.base import TestCase

if not single_db_name:
    print("Utilize single DB by setting `MONGO_DB` in environment variables "
          "to prevent possible the data corruption.")
    sys.exit(1)

mongo_url = os.environ["MONGO_URL"]
if not mongo_url:
    print("`MONGO_URL` not specified in environment variables while some test cases seem to need that.")
    sys.exit(1)
mongo_client = pymongo.MongoClient(mongo_url)


class TestDatabaseMixin(TestCase, ABC):
    """
    This class should be used if the test case will make use of database.

    This class sets a single database at the beginning of the test case and destroy them after each test case.

    This class also provided functionality to get the database ping.
    """
    # Original env var `MONGO_DB`
    _os_mongo_db_ = None

    def setUpTestCase(self) -> None:
        """Hook method to setup each test cases."""
        pass

    @final
    def setUp(self) -> None:
        # Ensure the database is clear
        if single_db_name:
            mongo_client.drop_database(single_db_name)

        self.setUpTestCase()

    def tearDownTestCase(self) -> None:
        """Hook method to tear down each test cases."""
        pass

    @final
    def tearDown(self) -> None:
        # Drop the used database
        if single_db_name:
            mongo_client.drop_database(single_db_name)

        self.tearDownTestCase()

    @staticmethod
    @final
    def get_db_name():
        return single_db_name

    @staticmethod
    @final
    def get_mongo_client():
        return mongo_client

    @classmethod
    def db_ping_ms(cls) -> float:
        return exec_timing_result(mongo_client.get_database(single_db_name or "admin").command, "ping").execution_ms
