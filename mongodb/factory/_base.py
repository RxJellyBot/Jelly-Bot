from datetime import timedelta
from threading import Thread
from typing import Type, Optional, Tuple

from bson import ObjectId
from bson.errors import InvalidDocument
from django.conf import settings
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

from extutils.mongo import get_codec_options
from extutils.dt import now_utc_aware
from models import Model, OID_KEY
from models.exceptions import InvalidModelError
from models.field.exceptions import FieldReadOnly, FieldTypeMismatch, FieldValueInvalid, FieldCastingFailed
from models.utils import ModelFieldChecker
from mongodb.utils import CursorWithCount
from mongodb.factory import MONGO_CLIENT
from mongodb.factory.results import WriteOutcome


class ControlExtensionMixin(Collection):
    def insert_one_model(self, model: Model) -> Tuple[WriteOutcome, Optional[Exception]]:
        ex = None

        try:
            insert_result = self.insert_one(model)
            if insert_result.acknowledged:
                model.set_oid(insert_result.inserted_id)
                outcome = WriteOutcome.O_INSERTED
            else:
                outcome = WriteOutcome.X_NOT_ACKNOWLEDGED
        except (AttributeError, InvalidDocument) as e:
            outcome = WriteOutcome.X_NOT_SERIALIZABLE
            ex = e
        except DuplicateKeyError as e:
            # The model's ID will be set by the call `self.insert_one()`,
            # so if the data exists, then we should get the object ID of it and insert it onto the model.
            model.set_oid(self._get_duplicated_doc_id_(model.to_json()))

            outcome = WriteOutcome.O_DATA_EXISTS
            ex = e
        except InvalidModelError as e:
            outcome = WriteOutcome.X_INVALID_MODEL
            ex = e
        except Exception as e:
            outcome = WriteOutcome.X_INSERT_UNKNOWN
            ex = e

        return outcome, ex

    def _get_duplicated_doc_id_(self, model_dict: dict):
        unique_keys = []

        # Get unique indexes
        for idx_info in self.index_information().values():
            if idx_info.get("unique", False):
                unique_keys.append(idx_info["key"])

        filter_ = {}
        or_list = []
        for unique_key in unique_keys:
            if len(unique_key) > 1:
                # Compound Index
                for key, order in unique_key:
                    data = model_dict.get(key)
                    if data is not None:
                        if isinstance(data, list):
                            filter_[key] = {"$elemMatch": {"$in": data}}
                        else:
                            filter_[key] = data
            else:
                key, order = unique_key[0]

                data = model_dict.get(key)
                if data is not None:
                    if isinstance(data, list):
                        or_list.append({key: {"$elemMatch": {"$in": data}}})
                    else:
                        or_list.append({key: data})

        if or_list:
            filter_["$or"] = or_list

        return self.find_one(filter_)[OID_KEY]

    def insert_one_data(self, model_cls: Type[Type[Model]], **model_args) \
            -> Tuple[Optional[Model], WriteOutcome, Optional[Exception]]:
        """
        :param model_cls: The class for the data to be sealed.
        :param model_args: The arguments for the `Model` construction.

        :return: model, outcome, ex
        """
        model = None
        outcome: WriteOutcome = WriteOutcome.X_NOT_EXECUTED
        ex = None

        try:
            if issubclass(model_cls, Model):
                model = model_cls(**model_args)
            else:
                outcome = WriteOutcome.X_NOT_MODEL
        except FieldReadOnly as e:
            outcome = WriteOutcome.X_READONLY
            ex = e
        except FieldTypeMismatch as e:
            outcome = WriteOutcome.X_TYPE_MISMATCH
            ex = e
        except FieldValueInvalid as e:
            outcome = WriteOutcome.X_INVALID_FIELD
            ex = e
        except FieldCastingFailed as e:
            outcome = WriteOutcome.X_CASTING_FAILED
            ex = e
        except Exception as e:
            outcome = WriteOutcome.X_CONSTRUCT_UNKNOWN
            ex = e

        if model:
            outcome, ex = self.insert_one_model(model)

        if settings.DEBUG and not outcome.is_success:
            raise ex

        return model, outcome, ex

    def update_many_outcome(self, filter_, update, upsert=False, collation=None) -> WriteOutcome:
        update_result = self.update_many(filter_, update, upsert, collation)

        if update_result.matched_count > 0:
            if update_result.modified_count > 0:
                outcome = WriteOutcome.O_DATA_UPDATED
            else:
                outcome = WriteOutcome.O_DATA_EXISTS
        else:
            outcome = WriteOutcome.X_NOT_FOUND

        return outcome

    def update_many_async(self, filter_, update, upsert=False, collation=None):
        Thread(
            target=self.update_many, args=(filter_, update), kwargs={"upsert": upsert, "collation": collation}).start()

    def update_one_async(self, filter_, update, upsert=False, collation=None):
        Thread(
            target=self.update_one, args=(filter_, update), kwargs={"upsert": upsert, "collation": collation}).start()

    def find_cursor_with_count(
            self, filter_, *args, parse_cls=None, hours_within: Optional[int] = None, **kwargs) -> CursorWithCount:
        if hours_within:
            self._attach_hours_within_(filter_, hours_within)

        return CursorWithCount(
            self.find(filter_, *args, **kwargs), self.count_documents(filter_), parse_cls=parse_cls)

    def find_one_casted(self, filter_, *args, parse_cls: Type[Model] = None, **kwargs) -> Optional[Model]:
        return parse_cls.cast_model(self.find_one(filter_, *args, **kwargs))

    @staticmethod
    def _attach_hours_within_(filter_: dict, hours_within: Optional[int] = None):
        fltr = {"$gt": ObjectId.from_datetime(now_utc_aware() - timedelta(hours=hours_within))}

        if OID_KEY in filter_:
            filter_[OID_KEY] = {"$eq": filter_[OID_KEY]}
            filter_[OID_KEY].update(fltr)
        else:
            filter_[OID_KEY] = fltr


class BaseCollection(ControlExtensionMixin, Collection):
    database_name: str = None
    collection_name: str = None
    model_class: type(Model) = None

    @classmethod
    def get_db_name(cls):
        if cls.database_name is None:
            raise AttributeError(f"Define `database_name` as class variable for {cls.__qualname__}.")
        else:
            return cls.database_name

    @classmethod
    def get_col_name(cls):
        if cls.collection_name is None:
            raise AttributeError(f"Define `collection_name` as class variable for {cls.__qualname__}.")
        else:
            return cls.collection_name

    @classmethod
    def get_model_cls(cls):
        if cls.model_class is None:
            raise AttributeError(f"Define `model_class` as class variable for {cls.__qualname__}.")
        else:
            return cls.model_class

    def __init__(self):
        self._db = MONGO_CLIENT.get_database(self.get_db_name())
        super().__init__(self._db, self.get_col_name(), codec_options=get_codec_options())
        self._data_model = self.get_model_cls()

        ModelFieldChecker.check_async(self)

    def insert_one_data(self, **model_args) -> Tuple[Optional[Model], WriteOutcome, Optional[Exception]]:
        return super().insert_one_data(self.get_model_cls(), **model_args)

    @property
    def data_model(self):
        return self._data_model
