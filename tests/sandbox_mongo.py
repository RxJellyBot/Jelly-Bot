import os

import pymongo
from bson import ObjectId

from extutils import exec_timing_ns


MONGO_CLIENT = pymongo.MongoClient("localhost", 27017)


@exec_timing_ns
def wrap():
    col = MONGO_CLIENT.get_database("test").get_collection("test")
    id_ = col.update_one({"e": "b"}, {"$addToSet": {"c": "e"}}, upsert=True).upserted_id

    if id_:
        print(col.find_one({"_id": id_}))
    else:
        print(col.find_one({"e": "b"}))


if __name__ == "__main__":
    wrap()
