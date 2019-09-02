import os

import pymongo
from pymongo import InsertOne

from extutils import exec_timing_ns

MONGO_CLIENT = pymongo.MongoClient(os.environ.get("MONGO_URL"))
col = MONGO_CLIENT.get_database("pdrp").get_collection("channel.dict")
col2 = MONGO_CLIENT.get_database("channel").get_collection("dict")


@exec_timing_ns
def wrap():
    col.update_many({}, {"$set": {"d.n": {}}})
    ops = [InsertOne(d_parent["d"]) for d_parent in col.find()]
    col2.bulk_write(ops, ordered=False)


@exec_timing_ns
def wrap2():
    pass


if __name__ == "__main__":
    wrap()
    wrap2()
