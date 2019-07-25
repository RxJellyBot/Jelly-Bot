import os
import pprint
from datetime import datetime, timezone, timedelta
from time import sleep
import math

import pymongo
from bson import ObjectId
from pymongo import InsertOne
from pymongo.errors import BulkWriteError

from extutils import exec_timing_ns

MONGO_CLIENT = pymongo.MongoClient("localhost", 27017)
MONGO_CLIENT.get_database("test").drop_collection("test")
MONGO_CLIENT.get_database("test").drop_collection("test2")
col = MONGO_CLIENT.get_database("test").get_collection("test")
col2 = MONGO_CLIENT.get_database("test").get_collection("test2")

col.create_index("name", unique=True)

# Appearance - Hours


TIME_INTERSECT_HR = 168
TIME_FUNC_COEFF = 40

APPEARANCE_INTERSECT = 100
APPEARANCE_FUNC_COEFF = 1.4
APPEARANCE_WEIGHTED_EQ_HR = 5

FN_CEF_A = 2 * TIME_INTERSECT_HR
FN_CEF_B = -1 / TIME_FUNC_COEFF
FN_CEF_C = 1 / math.pow(APPEARANCE_INTERSECT, APPEARANCE_FUNC_COEFF - 1)


@exec_timing_ns
def wrap():
    try:
        col.bulk_write([
            InsertOne({"name": "DragaliaLost"}),
            InsertOne({"name": "DragliaLost"}),
            InsertOne({"name": "DragaiaLost"}),
            InsertOne({"name": "DragalaLost"}),
            InsertOne({"name": "DrgalaLost"}),
            InsertOne({"name": "DragaliLost"})
        ], ordered=False)
    except BulkWriteError as e:
        print("Insert Many Error")
        pprint.pprint(e.details)


@exec_timing_ns
def wrap2():
    r = col.find({"name": {"$regex": r"Dra", "$options": "i"}}).sort([("_id", pymongo.DESCENDING)])

    for r_ in r:
        print(r_)


@exec_timing_ns
def wrap3():
    pass


if __name__ == "__main__":
    wrap()
    wrap2()
    col.drop()
    col2.drop()
