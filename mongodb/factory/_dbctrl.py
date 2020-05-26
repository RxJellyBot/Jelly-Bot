import os
import time

from extutils.logger import SYSTEM

__all__ = ["get_single_db_name", "SINGLE_DB_NAME", "is_test_db"]


def get_single_db_name():
    """
    Method to get the single db name, if any.

    Should only being called in the tests or when the module is initialized.
    """
    expected_db_name = os.environ.get("MONGO_DB")
    if not expected_db_name and bool(int(os.environ.get("TEST", 0))):
        expected_db_name = f"Test-{time.time_ns() // 1000000}"

    return expected_db_name


SINGLE_DB_NAME = get_single_db_name()
if SINGLE_DB_NAME:
    SYSTEM.logger.info("MongoDB single database is activated "
                       "by setting values to the environment variable 'MONGO_DB'.")
    SYSTEM.logger.info(f"MongoDB single database name: {SINGLE_DB_NAME}")
elif bool(int(os.environ.get("TEST", 0))):
    SYSTEM.logger.info("MongoDB single database activated because `TEST` has been set to true.")
    SYSTEM.logger.info(f"MongoDB single database name: {SINGLE_DB_NAME}")


def is_test_db(db_name: str):
    if "-" in db_name:
        prefix, epoch = db_name.split("-", 2)

        return "Test" in prefix and int(epoch) < time.time_ns() // 1000000

    return False
