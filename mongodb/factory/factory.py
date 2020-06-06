import os

import pymongo

from mongodb.exceptions import MongoURLNotFoundError

__all__ = ["MONGO_CLIENT", "new_mongo_session"]

_url = os.environ.get("MONGO_URL")
if _url is None:
    raise MongoURLNotFoundError()

MONGO_CLIENT = pymongo.MongoClient(_url)


def new_mongo_session():
    """
    Create a new mongo session and return it.

    This should be used along with the ``with`` statement.

    >>> with new_mongo_session() as session:
    >>>     pass

    :return: mongo client session
    """
    return MONGO_CLIENT.start_session()
