import types
from typing import Tuple, Union, Type, Optional, Iterable as TIterable

from bson import ObjectId
from bson.errors import InvalidDocument
from django.conf import settings
from pymongo.collation import Collation
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.errors import DuplicateKeyError
from pymongo.results import InsertOneResult
from ttldict import TTLOrderedDict

from extutils.flags import get_codec_options
from models import Model
from models.exceptions import PreserializationFailedError
from models.field.exceptions import FieldReadOnly, FieldTypeMismatch, FieldValueInvalid
from models.utils import ModelFieldChecker
from mongodb.factory import MONGO_CLIENT
from mongodb.factory.results import InsertOutcome
from JellyBotAPI.SystemConfig import Database

CACHE_EXPIRATION_SECS = Database.CacheExpirySeconds


class DecoParamChecker:
    def __init__(self, args_index: tuple, dict_keys: tuple = None):
        self._args_idx = args_index
        self._dict_keys = dict_keys

    def __call__(self, f):
        def wrap_f(*args, **kwargs):
            new_args = []

            for idx, val in enumerate(args):
                if idx in self._args_idx:
                    new_args.append(DecoParamChecker.type_check(args[idx]))
                else:
                    new_args.append(args[idx])

            for key, val in kwargs.items():
                if key in self._dict_keys:
                    kwargs[key] = DecoParamChecker.type_check(val)
                else:
                    kwargs[key] = val

            return f(*new_args, **kwargs)

        return wrap_f

    @staticmethod
    def type_check(item):
        if isinstance(item, ObjectId):
            return str(item)

        return item


class CacheMixin(Collection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = TTLOrderedDict(default_ttl=CACHE_EXPIRATION_SECS)

    @DecoParamChecker((1,))
    def init_cache(self, cache_key):
        """
        Initialize a cache space if necessary.

        :param cache_key: The key for the cache. Act like the category of a collection of the cache.
        """
        if cache_key not in self._cache:
            self._cache[cache_key] = TTLOrderedDict(default_ttl=CACHE_EXPIRATION_SECS)

    @DecoParamChecker((1, 2,))
    def set_cache(self, cache_key, item_key, item, parse_cls=None):
        """
        Set data to the cache.

        :param cache_key: The key for the cache. Act like the category of a collection of the cache.
        :param item_key: The key for the item. Act like the key to find the item in a specific cache.
        :param item: The item to be stored.
        :param parse_cls: Class to parse after acquiring the data if found.
        :return: The parsed `item` if `parse_cls` is not `None`.
        """
        self.init_cache(cache_key)

        self._cache[cache_key][item_key] = CacheMixin._parse_item(item, parse_cls)

        return self._cache[cache_key][item_key]

    @DecoParamChecker((1, 2,), ("item_key_from_data",))
    def get_cache(self, cache_key: str, item_key, acquire_func=None, acquire_args: Tuple = None,
                  acquire_kw_args: dict = None, acquire_auto=True, parse_cls=None, case_insensitive=False,
                  item_key_from_data=None):
        """
        Get data from the cache. Data can be acquired from the database and
        inserted to the cache if `acquire_auto` is `True` and the data is not found in the cache.

        :param cache_key: The key for the cache. Act like the category of a collection of the cache.
        :param item_key: The key for the item. Act like the key to find the item in a specific cache.
        :param acquire_func: Function to acquire the data if not found in the cache. Default to `find_one`.
        :param acquire_args: Arguments with `acquire_func`.
        :param acquire_kw_args: Keyword arguments with `acquire_func`.
        :param acquire_auto: Determines if the data not found, will execute `acquire_func` to get the data.
        :param parse_cls: Class to parse after acquiring the data if found.
        :param case_insensitive: Determines if the searching will be case-insensitive.
        :param item_key_from_data: If this is set, the value of this key from the data will be used as `item_key`.
        """
        ret = None

        if acquire_func is None:
            acquire_func = self.find_one

        self.init_cache(cache_key)

        if item_key not in self._cache[cache_key] or self._cache[cache_key][item_key] is None:
            if not acquire_auto:
                return None

            if acquire_kw_args is None:
                acquire_kw_args = {}

            if case_insensitive:
                acquire_kw_args["collation"] = Collation(locale='en', strength=1)

                item_key_lower = item_key.lower()
                for k, v in self._cache[cache_key].items():
                    if item_key_lower == k.lower():
                        ret = v
                        break

            if ret is None:
                if acquire_args is None:
                    data = acquire_func({cache_key: item_key}, **acquire_kw_args)
                else:
                    data = acquire_func(*acquire_args, **acquire_kw_args)

                if isinstance(data, Cursor):
                    data = list(data)

                if item_key_from_data is not None:
                    item_key = data[item_key_from_data]

                ret = data
        else:
            ret = self._cache[cache_key][item_key]

        return self.set_cache(cache_key, item_key, ret, parse_cls)

    @DecoParamChecker((1,), ("item_key_from_data",))
    def get_cache_condition(self, cache_key: str, item_func: types.LambdaType, acquire_args: Tuple,
                            item_key_of_data=None, acquire_func=None, acquire_kw_args: dict = None, acquire_auto=True,
                            parse_cls=None, case_insensitive=False):
        """
        Return the first matched element using the given condition.

        Data can be acquired from the database and
        inserted to the cache if `acquire_auto` is `True` and the data is not found in the cache.

        :param cache_key: The key for the cache. Act like the category of a collection of the cache.
        :param item_func: A function returning a `bool` to indicate if the condition is match.
        :param acquire_args: Arguments with `acquire_func`.
        :param item_key_of_data: The key of the item which value will be stored in the cache.
          Will be `cache_key` if not set.
        :param acquire_func: Function to acquire the data if not found in the cache. Default to `find_one`.
        :param acquire_kw_args: Keyword arguments with `acquire_func`.
        :param acquire_auto: Determines if the data not found, will execute `acquire_func` to get the data.
        :param parse_cls: Class to parse after acquiring the data if found.
        :param case_insensitive: Determines if the searching will be case-insensitive.

        .. note:: `case_insensitive` only works for the database data acquiring, not for cache acquiring,
          because you defined `item_lambda`!
        """
        if item_key_of_data is None:
            item_key_of_data = cache_key

        self.init_cache(cache_key)

        ret = next((item for item in self._cache[cache_key].values() if item_func(item)), None)

        if ret is None:
            if not acquire_auto:
                return None

            if acquire_func is None:
                acquire_func = self.find_one

            if acquire_kw_args is None:
                acquire_kw_args = {}

            if case_insensitive:
                acquire_kw_args["collation"] = Collation(locale='en', strength=1)

            data = acquire_func(*acquire_args, **acquire_kw_args)

            if isinstance(data, Cursor):
                data = list(data)

            if data is not None:
                ret = self.set_cache(cache_key, data[item_key_of_data], data, parse_cls)

        return ret

    @staticmethod
    def _parse_item(ret, parse_cls):
        if ret is not None and parse_cls is not None and not isinstance(ret, parse_cls):
            return parse_cls.parse(ret)

        return ret


class ControlExtensionMixin(Collection):
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

        :return: model, outcome, ex, insert_result
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


class BaseCollection(CacheMixin, ControlExtensionMixin, Collection):
    database_name: str = None
    collection_name: str = None
    model_class: type(Model) = None

    @classmethod
    def get_db_name(cls):
        if cls.database_name is None:
            raise AttributeError(f"Define `database_name` as class variable for {cls.__name__}.")
        else:
            return cls.database_name

    @classmethod
    def get_col_name(cls):
        if cls.collection_name is None:
            raise AttributeError(f"Define `collection_name` as class variable for {cls.__name__}.")
        else:
            return cls.collection_name

    @classmethod
    def get_model_cls(cls):
        if cls.model_class is None:
            raise AttributeError(f"Define `model_class` as class variable for {cls.__name__}.")
        else:
            return cls.model_class

    def __init__(self, cache_keys: Union[str, TIterable[str]] = None):
        self._db = MONGO_CLIENT.get_database(self.__class__.get_db_name())
        super().__init__(self._db, self.__class__.get_col_name(), codec_options=get_codec_options())
        self._data_model = self.__class__.get_model_cls()
        if cache_keys is not None:
            if isinstance(cache_keys, (list, tuple, set)):
                for k in cache_keys:
                    self.init_cache(k)
            else:
                self.init_cache(cache_keys)

        ModelFieldChecker.check(self)

    @property
    def data_model(self):
        return self._data_model
