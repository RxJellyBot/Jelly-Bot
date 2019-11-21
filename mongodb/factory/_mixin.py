import secrets
from typing import Type

from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from tinydb.database import Table

from models import Model
from ._base import BaseCollection


class GenerateTokenMixin(BaseCollection):
    token_length: int = None
    token_key: str = None

    @classmethod
    def get_token_length(cls) -> int:
        if cls.token_length is None:
            raise AttributeError(f"Assign a value to `token_length` in {cls.__qualname__}.")
        else:
            return cls.token_length

    @classmethod
    def get_token_key(cls) -> str:
        if cls.token_key is None:
            raise AttributeError(f"Assign a value to `token_key` in {cls.__qualname__}.")
        else:
            return cls.token_key

    # noinspection PyTypeChecker
    def generate_hex_token(self):
        token = secrets.token_hex(int(self.__class__.get_token_length() / 2))
        if self.count_documents({self.__class__.get_token_key(): token}) > 0:
            token = self.generate_hex_token()

        return token


cache_db = TinyDB(storage=MemoryStorage)


class CacheMixin:
    cache_name: str = None
    cache_table: Table = None

    @classmethod
    def get_cache_table(cls) -> Table:
        if cls.cache_name is None:
            raise AttributeError(f"Assign a value to `cache_name` in {cls.__qualname__}.")
        else:
            cls.cache_table = cache_db.table(cls.cache_name)

            return cls.cache_table

    @classmethod
    def set_cache(cls, item: Model):
        cls.get_cache_table().insert(item)

    @classmethod
    def get_cache(cls, query: Query, parse_cls: Type[Model] = None):
        ret = cls.get_cache_table().get(query)
        if ret:
            return parse_cls.cast_model(ret)
        else:
            return None

    @staticmethod
    def empty_query():
        return Query()
