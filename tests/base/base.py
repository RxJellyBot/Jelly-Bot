import sys
from typing import final, List, Union, Type

from django.test import TestCase as DjangoTestCase

from env_var import is_testing
from mixin import ClearableMixin
from mongodb.factory import MONGO_CLIENT, is_test_db

__all__ = ["TestCase"]


class TestCase(DjangoTestCase):
    @classmethod
    @final
    def setUpClass(cls):
        print(f"Setup {cls.__qualname__}...")

        # Ensure `TEST` flag is set
        if not is_testing():
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

    @staticmethod
    def obj_to_clear() -> List[Union[Type[ClearableMixin], ClearableMixin]]:
        """Objects to be cleared (by calling ``clear()``)  on the start of each test cases."""
        return []

    def setUpTestCase(self) -> None:
        """Hook method to setup each test cases."""
        pass

    @final
    def setUp(self) -> None:
        # Clear related collections
        for col in self.obj_to_clear():
            col.clear()

        self.setUpTestCase()

    def tearDownTestCase(self) -> None:
        """Hook method to tear down each test cases."""
        pass

    @final
    def tearDown(self) -> None:
        self.tearDownTestCase()
