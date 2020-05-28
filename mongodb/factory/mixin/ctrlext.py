from datetime import datetime
from threading import Thread
from typing import Type, Optional, Tuple, Union, TypeVar

from bson.errors import InvalidDocument
from django.conf import settings
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

from extutils.dt import TimeRange
from extutils.utils import dt_to_objectid
from models import Model, OID_KEY
from models.exceptions import InvalidModelError, InvalidModelFieldError, RequiredKeyNotFilledError, \
    FieldKeyNotExistError
from models.field.exceptions import (
    FieldReadOnlyError, FieldTypeMismatchError, FieldValueInvalidError, FieldCastingFailedError
)
from mongodb.utils import CursorWithCount
from mongodb.factory.results import WriteOutcome

T = TypeVar('T', bound=Model)


class ControlExtensionMixin(Collection):
    def insert_one_model(self, model: Model) -> Tuple[WriteOutcome, Optional[Exception]]:
        """
        Insert an object into the database by providing a constructed model.

        OID will be attached iuf the insertion succeed.

        :param model: model to be inserted into the database
        :return: outcome, exception (if any)
        """
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
            model.set_oid(self._get_duplicated_doc_id(model.to_json()))

            outcome = WriteOutcome.O_DATA_EXISTS
            ex = e
        except InvalidModelError as e:
            outcome = WriteOutcome.X_INVALID_MODEL
            ex = e
        except Exception as e:
            outcome = WriteOutcome.X_INSERT_UNKNOWN
            ex = e

        return outcome, ex

    def _get_duplicated_doc_id(self, model_dict: dict):
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

    def insert_one_data(self, model_cls: Type[Type[T]], *, from_db: bool = False, **model_args) \
            -> Tuple[Optional[T], WriteOutcome, Optional[Exception]]:
        """
        Insert an object into the database by providing its model class and the arguments to construct the model.

        This function constructs the model and if the construction succeed, executes ``insert_one_model()``.

        ``from_db`` determines the key type of ``model_args`` (json key or field key).

        .. seealso::
            Documentation of ``ControlExtensionMixin.insert_one_model()``

        :param model_cls: class for the data to be constructed
        :param from_db: if the values in `model_args` comes from the database
        :param model_args: arguments for the `Model` construction

        :return: model, outcome, exception (if any)
        """
        model = None
        outcome: WriteOutcome = WriteOutcome.X_NOT_EXECUTED
        ex = None

        try:
            if issubclass(model_cls, Model):
                model = model_cls(from_db=from_db, **model_args)
            else:
                outcome = WriteOutcome.X_NOT_MODEL
        except InvalidModelFieldError as e:
            ex = e

            if isinstance(e.inner_exception, FieldCastingFailedError):
                outcome = WriteOutcome.X_CASTING_FAILED
            elif isinstance(e.inner_exception, FieldValueInvalidError):
                outcome = WriteOutcome.X_INVALID_FIELD
            elif isinstance(e.inner_exception, FieldTypeMismatchError):
                outcome = WriteOutcome.X_TYPE_MISMATCH
            elif isinstance(e.inner_exception, FieldReadOnlyError):
                outcome = WriteOutcome.X_READONLY
            else:
                outcome = WriteOutcome.X_INVALID_MODEL_FIELD
        except RequiredKeyNotFilledError as e:
            outcome = WriteOutcome.X_REQUIRED_NOT_FILLED
            ex = e
        except FieldKeyNotExistError as e:
            outcome = WriteOutcome.X_FIELD_NOT_EXIST
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
        update_result = self.update_many(filter_, update, upsert=upsert, collation=collation)

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
            self, filter_, *args, parse_cls=None, hours_within: Optional[int] = None,
            start: Optional[datetime] = None, end: Optional[datetime] = None, **kwargs) -> CursorWithCount:
        self.attach_time_range(filter_, hours_within=hours_within, start=start, end=end)

        return CursorWithCount(
            self.find(filter_, *args, **kwargs), self.count_documents(filter_), parse_cls=parse_cls)

    def find_one_casted(self, filter_, *args, parse_cls: Type[T], **kwargs) -> Optional[T]:
        return parse_cls.cast_model(self.find_one(filter_, *args, **kwargs))

    @staticmethod
    def attach_time_range(filter_: dict, *, hours_within: Optional[int] = None,
                          start: Optional[datetime] = None, end: Optional[datetime] = None,
                          range_mult: Union[int, float] = 1.0, trange: Optional[TimeRange] = None):
        """
        Attach parsed time range to ``filter_``.

        Both start and end time are inclusive.

        If ``trange`` is specified, ``hours_within``, ``start``, ``end``, ``range_mult`` will be ignored.
        """
        id_filter = {}

        # Get the time range

        if not trange:
            trange = TimeRange(
                range_hr=hours_within, start=start, end=end, range_mult=range_mult, end_autofill_now=False)

        gt_oid = dt_to_objectid(trange.start)
        if trange.start and gt_oid:
            id_filter["$gte"] = gt_oid

        lt_oid = dt_to_objectid(trange.end)
        if trange.end and lt_oid:
            id_filter["$lte"] = lt_oid

        # Modifying filter

        if id_filter:
            if OID_KEY in filter_:
                filter_[OID_KEY].update(id_filter)
            else:
                filter_[OID_KEY] = id_filter
