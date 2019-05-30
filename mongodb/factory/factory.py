import os

import pymongo

from mongodb.exceptions import MongoURLNotFoundException


_url = os.environ.get("MONGO_URL")
if _url is None:
    raise MongoURLNotFoundException()

MONGO_CLIENT = pymongo.MongoClient(_url)
