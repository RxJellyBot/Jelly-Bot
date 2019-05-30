from typing import Union, List, Tuple, Type
from bson.errors import InvalidDocument

from django.conf import settings
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.errors import DuplicateKeyError
from ttldict import TTLOrderedDict

from extutils.flags import get_codec_options

from models import Model
from models.field.exceptions import FieldReadOnly, FieldTypeMismatch, FieldValueInvalid
from mongodb.factory.results import InsertOutcome

from .factory import MONGO_CLIENT

CACHE_EXPIRATION_SECS = 172800


class BaseCollection(Collection):
    def __init__(self, db_name, col_name, cache_keys: Union[str, List[str]] = None):
        self._db = MONGO_CLIENT.get_database(db_name)
        super().__init__(self._db, col_name, codec_options=get_codec_options())
        self._cache = TTLOrderedDict(default_ttl=CACHE_EXPIRATION_SECS)
        if cache_keys is not None:
            if isinstance(cache_keys, list):
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

    def get_cache(self, cache_key, item_key, acquire_func=None, acquire_args: Tuple = None, acquire_auto=True,
                  parse_cls=None):
        if acquire_func is None:
            acquire_func = self.find_one

        if cache_key not in self._cache:
            self.init_cache(cache_key)

        if item_key not in self._cache[cache_key]:
            if not acquire_auto:
                return None

            if acquire_args is None:
                data = acquire_func({cache_key: item_key})
            else:
                data = acquire_func(*acquire_args)

            if isinstance(data, Cursor):
                data = list(data)

            self.set_cache(cache_key, item_key, data)

        ret = self._cache[cache_key][item_key]

        if parse_cls is not None and ret is not None and not isinstance(ret, parse_cls):
            return parse_cls.parse(ret)
        else:
            return ret

    def insert_one_data(self, model_cls, **model_args) -> tuple:
        """

        :param model_cls: The class for the data to be sealed.
        :type model_cls: Type[Model]
        :param model_args: The arguments for the `Model` construction.
        :return: model (Model), outcome (InsertOutcome), ex(Exception or None), insert_result (InsertOneResult)
        """
        entry = None
        outcome: InsertOutcome = InsertOutcome.FAILED_NOT_EXECUTED
        ex = None
        insert_result = None

        try:
            if issubclass(model_cls, Model):
                entry = model_cls(**model_args)
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

        if entry is not None:
            try:
                insert_result = self.insert_one(entry.serialize())
                if insert_result.acknowledged:
                    entry.set_oid(insert_result.inserted_id)
                    outcome = InsertOutcome.SUCCESS_INSERTED
                else:
                    outcome = InsertOutcome.FAILED_NOT_ACKNOWLEDGED
            except (AttributeError, InvalidDocument) as e:
                outcome = InsertOutcome.FAILED_NOT_SERIALIZABLE
                ex = e
            except DuplicateKeyError as e:
                outcome = InsertOutcome.SUCCESS_DATA_EXISTS
                ex = e
            except Exception as e:
                outcome = InsertOutcome.FAILED_INSERT_UNKNOWN
                ex = e

        if settings.DEBUG and not InsertOutcome.is_success(outcome):
            raise ex

        return entry, outcome, ex, insert_result
