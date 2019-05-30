import os
import time
from inspect import signature
from typing import Type

import pymongo

MONGO_CLIENT = pymongo.MongoClient(os.environ.get("MONGO_URL"))


if __name__ == "__main__":
    pass

