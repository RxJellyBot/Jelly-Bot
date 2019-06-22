import os

import pymongo

from mongodb.exceptions import MongoURLNotFoundException

if int(os.environ.get("MONGO_LOCAL", 0)):
    MONGO_CLIENT = pymongo.MongoClient("localhost", 27017)
else:
    _url = os.environ.get("MONGO_URL")
    if _url is None:
        raise MongoURLNotFoundException()

    MONGO_CLIENT = pymongo.MongoClient(_url)
