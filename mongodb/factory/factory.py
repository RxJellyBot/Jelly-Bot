import os

import pymongo

from mongodb.exceptions import MongoURLNotFoundError

_url = os.environ.get("MONGO_URL")
if _url is None:
    raise MongoURLNotFoundError()

MONGO_CLIENT = pymongo.MongoClient(_url)
