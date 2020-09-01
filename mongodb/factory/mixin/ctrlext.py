"""Wrapper for the controls on a MongoDB collection as a mixin."""
from datetime import datetime, tzinfo
from threading import Thread
from typing import Optional, Tuple, Union, TypeVar

from bson.errors import InvalidDocument
from django.conf import settings
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

from extutils.dt import TimeRange
from extutils.utils import dt_to_objectid
from env_var import is_testing
from models import Model, OID_KEY
from models.exceptions import (
    InvalidModelError, InvalidModelFieldError, RequiredKeyNotFilledError, FieldKeyNotExistError
)
from models.field.exceptions import (
    FieldReadOnlyError, FieldTypeMismatchError, FieldValueInvalidError, FieldCastingFailedError
)
from mongodb.utils import ExtendedCursor
from mongodb.factory.results import WriteOutcome, UpdateOutcome

from .prop import CollectionPropertiesMixin

T = TypeVar('T', bound=Model)  # pylint: disable=invalid-name


class ControlExtensionMixin(CollectionPropertiesMixin, Collection):
    """
    A wrapper class for :class:`Collection`.

    Wraps various database manipulating functions to provide additional functionality.
    """

    @staticmethod
    def _dup_doc_id_handle_compound_idx(filter_: dict, model_dict: dict, unique_key):
        for key, _ in unique_key:
            data = model_dict.get(key)
            if data is not None:
                if isinstance(data, list):
                    filter_[key] = {"$elemMatch": {"$in": data}}
                else:
                    filter_[key] = data

    @staticmethod
    def _dup_doc_id_handle_single_idx(or_list: list, model_dict: dict, unique_key):
        key, _ = unique_key[0]

        data = model_dict.get(key)
        if data is not None:
            if isinstance(data, list):
                or_list.append({key: {"$elemMatch": {"$in": data}}})
            else:
                or_list.append({key: data})

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
                self._dup_doc_id_handle_compound_idx(filter_, model_dict, unique_key)
            else:
                self._dup_doc_id_handle_single_idx(or_list, model_dict, unique_key)

        if or_list:
            filter_["$or"] = or_list

        return self.find_one(filter_)[OID_KEY]

    def insert_one_model(self, model: Model) -> Tuple[WriteOutcome, Optional[Exception]]:
        """
        Insert an object into the database by providing a constructed model.

        OID will be attached iuf the insertion succeed.

        :param model: model to be inserted into the database
        :return: outcome, exception (if any)
        """
        exc = None

        try:
            insert_result = self.insert_one(model)
            if insert_result.acknowledged:
                model.set_oid(insert_result.inserted_id)
                outcome = WriteOutcome.O_INSERTED
            else:
                outcome = WriteOutcome.X_NOT_ACKNOWLEDGED
        except (AttributeError, InvalidDocument) as ex:
            outcome = WriteOutcome.X_NOT_SERIALIZABLE
            exc = ex
        except DuplicateKeyError as ex:
            # A new model ID will be set when calling `self.insert_one()`.
            # However, that is not the desired if a conflicting data is already in the database.
            # `self._get_duplicated_doc_id()` will get the OID of the conflicting data.
            model.set_oid(self._get_duplicated_doc_id(model.to_json()))

            outcome = WriteOutcome.O_DATA_EXISTS
            exc = ex
        except InvalidModelError as ex:
            outcome = WriteOutcome.X_INVALID_MODEL
            exc = ex
        except Exception as ex:
            outcome = WriteOutcome.X_INSERT_UNKNOWN
            exc = ex

        return outcome, exc

    @staticmethod
    def _field_error_to_outcome(ex: InvalidModelFieldError) -> WriteOutcome:
        if isinstance(ex.inner_exception, FieldCastingFailedError):
            outcome = WriteOutcome.X_CASTING_FAILED
        elif isinstance(ex.inner_exception, FieldValueInvalidError):
            outcome = WriteOutcome.X_INVALID_FIELD_VALUE
        elif isinstance(ex.inner_exception, FieldTypeMismatchError):
            outcome = WriteOutcome.X_TYPE_MISMATCH
        elif isinstance(ex.inner_exception, FieldReadOnlyError):
            outcome = WriteOutcome.X_READONLY
        else:
            outcome = WriteOutcome.X_INVALID_MODEL_FIELD

        return outcome

    def insert_one_data(self, *, from_db: bool = False, **model_args) \
            -> Tuple[Optional[T], WriteOutcome, Optional[Exception]]:
        """
        Insert an object into the database using the provided the arguments of the model.

        This function constructs the model and if the construction succeed, executes ``insert_one_model()``.

        If the constructed model has duplicated key, its OID will be updated. Consistency of the constructed model
        and the data stored in database is not guaranteed, which means that the data of the constructed model and the
        actual may have some difference. If you want to access the field of the data other than ID, consider getting
        the data from the database using the attached ID instead.

        ``from_db`` determines the key type of ``model_args`` (json key or field key).

        .. seealso::
            Documentation of ``ControlExtensionMixin.insert_one_model()``

        :param from_db: if the values in `model_args` comes from the database
        :param model_args: arguments for the `Model` construction

        :return: model, outcome, exception (if any)
        """
        model = None
        model_cls = self.get_model_cls()
        outcome: WriteOutcome = WriteOutcome.X_NOT_EXECUTED
        ex = None

        try:
            if issubclass(model_cls, Model):
                model = model_cls(from_db=from_db, **model_args)
            else:
                outcome = WriteOutcome.X_NOT_MODEL
        except InvalidModelFieldError as e:
            outcome = self._field_error_to_outcome(e)
            ex = e
        except RequiredKeyNotFilledError as e:
            outcome = WriteOutcome.X_REQUIRED_NOT_FILLED
            ex = e
        except FieldKeyNotExistError as e:
            outcome = WriteOutcome.X_MODEL_KEY_NOT_EXIST
            ex = e
        except Exception as e:
            outcome = WriteOutcome.X_CONSTRUCT_UNKNOWN
            ex = e

        if model:
            outcome, ex = self.insert_one_model(model)

        if settings.DEBUG and not outcome.is_success:
            raise ex

        return model, outcome, ex

    def update_one_outcome(self, filter_, update, upsert=False, collation=None) -> UpdateOutcome:
        """
        Update one data matching ``filter_`` with the update statement ``update``.

        :param filter_: condition of the data to be updated
        :param update: mongo update statement
        :param upsert: to insert the data if not found
        :param collation: collation to be used against `filter_`
        :return: outcome of the update
        """
        update_result = self.update_one(filter_, update, upsert=upsert, collation=collation)

        if update_result.matched_count > 0:
            if update_result.modified_count > 0:
                outcome = UpdateOutcome.O_UPDATED
            else:
                outcome = UpdateOutcome.O_FOUND
        else:
            outcome = UpdateOutcome.X_NOT_FOUND

        return outcome

    def update_many_outcome(self, filter_, update, upsert=False, collation=None) -> UpdateOutcome:
        """
        Update one data matching ``filter_`` with the update statement ``update``.

        :param filter_: condition of the data to be updated
        :param update: mongo update statement
        :param upsert: to insert the data if not found
        :param collation: collation to be used against `filter_`
        :return: outcome of the update
        """
        update_result = self.update_many(filter_, update, upsert=upsert, collation=collation)

        if update_result.matched_count > 0:
            if update_result.modified_count > 0:
                outcome = UpdateOutcome.O_UPDATED
            else:
                outcome = UpdateOutcome.O_FOUND
        else:
            outcome = UpdateOutcome.X_NOT_FOUND

        return outcome

    def update_many_async(self, filter_, update, upsert=False, collation=None):
        """
        Same functionality as ``update_many()`` except that this function has return anything and run asynchronously.

        :param filter_: condition of the data to be updated
        :param update: mongo update statement
        :param upsert: to insert the data if not found
        :param collation: collation to be used against `filter_`
        """
        if is_testing():
            self.update_many(filter_, update, upsert=upsert, collation=collation)
        else:
            Thread(
                target=self.update_many,
                args=(filter_, update),
                kwargs={"upsert": upsert, "collation": collation}
            ).start()

    def update_one_async(self, filter_, update, upsert=False, collation=None):
        """
        Same functionality as ``update_one()`` except that this function has return anything and run asynchronously.

        :param filter_: condition of the data to be updated
        :param update: mongo update statement
        :param upsert: to insert the data if not found
        :param collation: collation to be used against `filter_`
        """
        if is_testing():
            self.update_one(filter_, update, upsert=upsert, collation=collation)
        else:
            Thread(
                target=self.update_one,
                args=(filter_, update),
                kwargs={"upsert": upsert, "collation": collation}
            ).start()

    def find_cursor_with_count(self, filter_: Optional[dict] = None, /,  # pylint: disable=keyword-arg-before-vararg
                               *args,
                               hours_within: Optional[int] = None, start: Optional[datetime] = None,
                               end: Optional[datetime] = None, **kwargs) \
            -> ExtendedCursor[T]:
        """
        Find the data matching the condition ``filter_`` and return it as an :class:`ExtendedCursor`.

        ``*args`` can be any args for ``db.col.find()``.

        ``**kwargs`` can be any args for ``db.col.find()``.

        ``start``, ``end`` and ``hours_within`` will be used as the time range parameters for ``filter_``.

        :param filter_: condition to filter the returned data
        :param args: args for `find()`
        :param hours_within: hour range for the time range filtering
        :param start: start time for the time range filtering
        :param end: end time for the time range filtering
        :param kwargs: keyword-args for `find()`
        :return: an `ExtendedCursor` yielding the filtered data
        """
        if not filter_:
            filter_ = {}

        self.attach_time_range(filter_, hours_within=hours_within, start=start, end=end)

        return ExtendedCursor(self.find(filter_, *args, **kwargs), self.count_documents(filter_),
                              parse_cls=self.get_model_cls())

    def find_one_casted(self, filter_: Optional[dict] = None, /, *args,  # pylint: disable=keyword-arg-before-vararg
                        **kwargs) -> Optional[T]:
        """
        Same functionality as ``find_one()`` except that this function will cast the returned :class:`dict` to model.

        :param filter_: filter to get the data
        :param args: args for `find_one()`
        :param kwargs: kwargs for `find_one()`
        :return: casted data in `parse_cls` or `None` if not found
        """
        return self.get_model_cls().cast_model(self.find_one(filter_, *args, **kwargs))

    @staticmethod
    def attach_time_range(filter_: dict, *, hours_within: Optional[int] = None,
                          start: Optional[datetime] = None, end: Optional[datetime] = None,
                          range_mult: Union[int, float] = 1.0, tzinfo_: Optional[tzinfo] = None,
                          trange: Optional[TimeRange] = None):
        """
        Attach parsed time range to ``filter_``.

        Both start and end time are inclusive.

        If ``trange`` is specified, ``hours_within``, ``start``, ``end``, ``range_mult`` will be ignored.

        :param filter_: filter to be attached the time range
        :param hours_within: hour range for the time range
        :param start: start time for the time range
        :param end: end time for the time range
        :param range_mult: range length multiplier for the time range
        :param tzinfo_: timezone info for the time range
        :param trange: time range to be used
        """
        id_filter = {}

        # Get the time range

        if not trange:
            trange = TimeRange(
                range_hr=hours_within, start=start, end=end, range_mult=range_mult, tzinfo_=tzinfo_,
                end_autofill_now=False)

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
