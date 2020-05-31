import os
import sys
from typing import final

from mongodb.factory import MONGO_CLIENT, is_test_db
from django.test import TestCase as DjangoTestCase

__all__ = ["TestCase"]


class TestCase(DjangoTestCase):
    @classmethod
    @final
    def setUpClass(cls):
        print(f"Setup {cls.__qualname__}...")

        # Ensure `TEST` flag is set
        if not bool(int(os.environ.get("TEST", 0))):
            # protect possible data corruption
            print("Set environment variable `TEST` to 1 to execute the tests.")
            sys.exit(1)

        # Drop all testing databases
        for db_name in MONGO_CLIENT.list_database_names():
            if is_test_db(db_name):
                MONGO_CLIENT.drop_database(db_name)
                print(f"Dropped test database <{db_name}>.")

        cls().setUpTestClass()

    @classmethod
    def setUpTestClass(cls):
        """Hook method to setup the test case."""
        pass

    @classmethod
    @final
    def tearDownClass(cls):
        cls.tearDownTestClass()

    @classmethod
    def tearDownTestClass(cls):
        """Hook method to tear down the test case."""
        pass
