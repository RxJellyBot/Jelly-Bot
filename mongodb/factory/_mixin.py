import secrets
from threading import Thread
from typing import Type, Optional, Tuple

from tinydb import TinyDB, Query as tinyDbQuery
from tinydb.storages import MemoryStorage
from tinydb.database import Table

from models import Model
from mongodb.utils import UpdateOperation, Query
from mongodb.factory.results import WriteOutcome

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


class CacheMixin(BaseCollection):
    cache_name: str = None
    cache_table: Table = None

    def get_cache_table(self) -> Table:
        if self.cache_name is None:
            raise AttributeError(f"Assign a value to `cache_name` in {self.__class__.__qualname__}.")
        else:
            self.cache_table = cache_db.table(self.cache_name)

            return self.cache_table

    def insert_cache(self, item: Model):
        self.get_cache_table().insert(item)

    def insert_one_model_cache(self, model: Model):
        outcome, ex = self.insert_one_model(model)

        if outcome.is_inserted:
            self.insert_cache_async(model)

        return outcome, ex

    def insert_one_data_cache(self, **model_args) -> Tuple[Optional[Model], WriteOutcome, Optional[Exception]]:
        model, outcome, ex = self.insert_one_data(**model_args)

        if outcome.is_inserted:
            self.insert_cache_async(model)

        return model, outcome, ex

    def insert_cache_async(self, item: Model):
        Thread(target=self.get_cache_table().insert, args=(item,)).start()

    def get_cache(self, query: tinyDbQuery, parse_cls: Type[Model] = None):
        ret = self.get_cache_table().get(query)
        if ret:
            if parse_cls:
                return parse_cls.cast_model(ret)
            else:
                return ret
        else:
            return None

    def get_cache_one(self, query: Query, parse_cls: Type[Model] = None, **kwargs):
        """
        Attempt to get the data using `query` from cache. If not existed, then get it from MongoDB.

        Store the data to the cache if found, otherwise return `None` and not making changes on the cache.

        `**kwargs` is passed into `find_one_casted()`.
        """
        cache_table = self.get_cache_table()

        ret = cache_table.get(query.to_tinydb())
        if not ret:
            ret = self.find_one_casted(query.to_mongo(), parse_cls=parse_cls, **kwargs)

            if ret:
                self.clear_cache(query.to_tinydb())
                self.insert_cache_async(ret)

        if parse_cls:
            return parse_cls.cast_model(ret)
        else:
            return ret

    def update_cache_async(self, query: Query, operation: UpdateOperation):
        Thread(target=self.get_cache_table().update, args=(operation.tinydb_ops(), query.to_tinydb())).start()

    def update_cache_db_async(self, query: Query, operation: UpdateOperation):
        self.update_cache_async(query, operation)
        self.update_one_async(query.to_mongo(), operation.mongo_ops())

    def update_cache_db_outcome(self, query: Query, operation: UpdateOperation):
        outcome = self.update_many_outcome(query.to_mongo(), operation.mongo_ops())

        if outcome == WriteOutcome.O_DATA_UPDATED:
            self.update_cache_async(query, operation)

        return outcome

    def clear_cache(self, query: tinyDbQuery):
        self.get_cache_table().remove(query)

    @staticmethod
    def empty_query():
        return tinyDbQuery()
