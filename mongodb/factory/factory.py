import os

import pymongo

from models import Model
from mongodb.exceptions import MongoURLNotFoundException

_url = os.environ.get("MONGO_URL")
if _url is None:
    raise MongoURLNotFoundException()

MONGO_CLIENT = pymongo.MongoClient(_url, document_class=Model)
