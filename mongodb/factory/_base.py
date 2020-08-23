import os
from abc import ABC
from threading import Thread
from typing import final

from django.conf import settings
from pymongo.collection import Collection

from JellyBot.systemconfig import Database
from extutils.mongo import get_codec_options
from mixin import ClearableMixin
from models.utils import ModelFieldChecker
from mongodb.utils import backup_collection
from mongodb.factory import MONGO_CLIENT

from ._dbctrl import SINGLE_DB_NAME
from .mixin import ControlExtensionMixin

__all__ = ("BaseCollection",)


class BaseCollection(ControlExtensionMixin, ClearableMixin, Collection, ABC):
    def __init__(self):
        self._db = MONGO_CLIENT.get_database(self.get_db_name())

        super().__init__(self._db, self.get_col_name(), codec_options=get_codec_options())

        self.get_model_cls()  # Dummy call to check if `model_class` has been defined

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
