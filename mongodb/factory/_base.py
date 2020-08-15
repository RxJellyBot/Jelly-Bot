import os
from abc import ABC
from threading import Thread
from typing import Type, Optional, Tuple, final

from django.conf import settings
from pymongo.collection import Collection

from JellyBot.systemconfig import Database
from extutils.mongo import get_codec_options
from mixin import ClearableMixin
from models import Model
from models.utils import ModelFieldChecker
from mongodb.utils import backup_collection
from mongodb.factory import MONGO_CLIENT
from mongodb.factory.results import WriteOutcome

from ._dbctrl import SINGLE_DB_NAME
from .mixin import ControlExtensionMixin

__all__ = ("BaseCollection",)


class BaseCollection(ControlExtensionMixin, ClearableMixin, Collection, ABC):
    database_name: str = None
    collection_name: str = None
    model_class: Type[Model] = None

    @classmethod
    def get_db_name(cls):
        if SINGLE_DB_NAME:
            return SINGLE_DB_NAME

        if cls.database_name is None:
            raise AttributeError(f"Define `database_name` as class variable for {cls.__qualname__}.")
        else:
            return cls.database_name

    @classmethod
    def get_col_name(cls):
        if cls.collection_name is None:
            raise AttributeError(f"Define `collection_name` as class variable for {cls.__qualname__}.")
        else:
            if SINGLE_DB_NAME:
                return f"{cls.database_name}.{cls.collection_name}"
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

        self.build_indexes()

        self.on_init()
        Thread(target=self.on_init_async).start()

    @final
    def on_init(self):
        if not os.environ.get("NO_FIELD_CHECK") and not os.environ.get("TEST"):
            ModelFieldChecker.check_async(self)

        if settings.PRODUCTION:
            backup_collection(
                MONGO_CLIENT, self.get_db_name(), self.get_col_name(),
                SINGLE_DB_NAME is not None, Database.BackupIntervalSeconds)

    def on_init_async(self):
        """Hook method to be called asychronously on the initialization of this class."""
        pass

    def build_indexes(self):
        """Method to be called when building the indexes of this collection."""
        pass

    def clear(self):
        self.delete_many({})

    def insert_one_data(self, *, from_db: bool = False, **model_args) \
            -> Tuple[Optional[Model], WriteOutcome, Optional[Exception]]:
        return super().insert_one_data(self.data_model, from_db=from_db, **model_args)

    @property
    def data_model(self):
        return self._data_model
