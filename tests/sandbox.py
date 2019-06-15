import os
import time
from inspect import signature
from typing import Type

import pymongo

MONGO_CLIENT = pymongo.MongoClient(os.environ.get("MONGO_URL"))


if __name__ == "__main__":
    _start = time.time_ns()

    for i in range(99999999):
        5 % 7 == 0

    print(f"{time.time_ns() - _start} ns")
    _start = time.time_ns()

    for i in range(99999999):
        5 > 7

    print(f"{time.time_ns() - _start} ns")

