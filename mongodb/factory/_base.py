from collections import Iterable
from typing import Union, Tuple, Type, Optional, Iterable as TIterable
from bson.errors import InvalidDocument

from django.conf import settings
from pymongo.collation import Collation
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.errors import DuplicateKeyError
from pymongo.results import InsertOneResult
from ttldict import TTLOrderedDict

from extutils.flags import get_codec_options

from JellyBotAPI.SystemConfig import Database
from models import Model
from models.exceptions import PreserializationFailedError
from models.field.exceptions import FieldReadOnly, FieldTypeMismatch, FieldValueInvalid
from mongodb.factory.results import InsertOutcome

from .factory import MONGO_CLIENT

CACHE_EXPIRATION_SECS = Database.CacheExpirySeconds


class BaseCollection(Collection):
    def __init__(self, db_name, col_name, cache_keys: Union[str, TIterable[str]] = None):
        self._db = MONGO_CLIENT.get_database(db_name)
        super().__init__(self._db, col_name, codec_options=get_codec_options())
        self._cache = TTLOrderedDict(default_ttl=CACHE_EXPIRATION_SECS)
        if cache_keys is not None:
            if isinstance(cache_keys, Iterable):
                for k in cache_keys:
                    self.init_cache(k)
            else:
                self.init_cache(cache_keys)

    def init_cache(self, cache_key):
        self._cache[cache_key] = {}

    def set_cache(self, cache_key, item_key, item):
        if cache_key not in self._cache:
            self.init_cache(cache_key)

        self._cache[cache_key][item_key] = item

    def get_cache(self, cache_key, item_key, acquire_func=None, acquire_args: Tuple = None,
                  acquire_kw_args: dict = None, acquire_auto=True, parse_cls=None, case_insensitive=False):
        # OPTIMIZE: Local Cache case-insensitive getter
        if acquire_func is None:
            acquire_func = self.find_one

        if cache_key not in self._cache:
            self.init_cache(cache_key)

        if item_key not in self._cache[cache_key]:
            if not acquire_auto:
                return None

            if acquire_kw_args is None:
                acquire_kw_args = {}

            if case_insensitive:
                acquire_kw_args["collation"] = Collation(locale='en', strength=1)

            if acquire_args is None:
                data = acquire_func({cache_key: item_key}, **acquire_kw_args)
            else:
                data = acquire_func(*acquire_args, **acquire_kw_args)

            if isinstance(data, Cursor):
                data = list(data)

            self.set_cache(cache_key, item_key, data)

        ret = self._cache[cache_key][item_key]

        if parse_cls is not None and ret is not None and not isinstance(ret, parse_cls):
            return parse_cls.parse(ret)
        else:
            return ret

    def insert_one_model(self, model: Model, include_oid=False) -> (InsertOutcome, Optional[Exception]):
        ex = None

        try:
            insert_result = self.insert_one(model.serialize(include_oid))
            if insert_result.acknowledged:
                model.set_oid(insert_result.inserted_id)
                outcome = InsertOutcome.SUCCESS_INSERTED
            else:
                outcome = InsertOutcome.FAILED_NOT_ACKNOWLEDGED
        except (AttributeError, InvalidDocument) as e:
            outcome = InsertOutcome.FAILED_NOT_SERIALIZABLE
            ex = e
        except DuplicateKeyError as e:
            outcome = InsertOutcome.SUCCESS_DATA_EXISTS
            ex = e
        except PreserializationFailedError as e:
            outcome = InsertOutcome.FAILED_PRE_SERIALIZE_FAILED
            ex = e
        except Exception as e:
            outcome = InsertOutcome.FAILED_INSERT_UNKNOWN
            ex = e

        return outcome, ex

    def insert_one_data(self, model_cls: Type[Type[Model]], **model_args) \
            -> (Model, InsertOutcome, Optional[Exception], InsertOneResult):
        """
        :param model_cls: The class for the data to be sealed.
        :param model_args: The arguments for the `Model` construction.
        """
        model = None
        outcome: InsertOutcome = InsertOutcome.FAILED_NOT_EXECUTED
        ex = None
        insert_result = None

        try:
            if issubclass(model_cls, Model):
                model = model_cls(**model_args)
            else:
                outcome = InsertOutcome.FAILED_NOT_MODEL
        except FieldReadOnly as e:
            outcome = InsertOutcome.FAILED_READONLY
            ex = e
        except FieldTypeMismatch as e:
            outcome = InsertOutcome.FAILED_TYPE_MISMATCH
            ex = e
        except FieldValueInvalid as e:
            outcome = InsertOutcome.FAILED_INVALID
            ex = e
        except Exception as e:
            outcome = InsertOutcome.FAILED_CONSTRUCT_UNKNOWN
            ex = e

        if model is not None:
            outcome, ex = self.insert_one_model(model)

        if settings.DEBUG and not InsertOutcome.is_success(outcome):
            raise ex

        return model, outcome, ex, insert_result
