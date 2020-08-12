import sys
from abc import ABC
from typing import final

from extutils import exec_timing_result
from mongodb.factory import SINGLE_DB_NAME, MONGO_CLIENT
from tests.base import TestCase

if not SINGLE_DB_NAME:
    print("Utilize single DB by setting `MONGO_DB` in environment variables "
          "to prevent the possible data corruption.")
    sys.exit(1)


class TestDatabaseMixin(TestCase, ABC):
    """
    This class should be used if the test case will make use of database.

    This class sets a single database at the beginning of the test case and destroy them after each test case.

    This class provides functionality to get the database ping.
    """

    @staticmethod
    @final
    def get_mongo_client():
        return MONGO_CLIENT

    @staticmethod
    @final
    def get_db_name():
        return SINGLE_DB_NAME

    @classmethod
    @final
    def get_collection(cls, col_name):
        client = cls.get_mongo_client()
        db = cls.get_db_name()

        return client.get_database(db).get_collection(col_name)

    @classmethod
    def db_ping_ms(cls) -> float:
        return exec_timing_result(MONGO_CLIENT.get_database(SINGLE_DB_NAME or "admin").command, "ping").execution_ms
