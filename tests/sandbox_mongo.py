import os

import pymongo
from bson import ObjectId

from extutils import exec_timing


MONGO_CLIENT = pymongo.MongoClient(os.environ["MONGO_URL"])


def wrap():
    col = MONGO_CLIENT.get_database("user").get_collection("root")
    for dt in col.find():
        dt["c"]["n"] = dt["n"]
        col.replace_one({"_id": dt["_id"]}, dt)


if __name__ == "__main__":
    duration, ret = exec_timing(wrap)
    print(f"Duration: {duration}s")
