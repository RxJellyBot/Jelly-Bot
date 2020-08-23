"""Implementation for the mixin to force the user specify the collection properties."""
from typing import Type

from models import Model
from .._dbctrl import SINGLE_DB_NAME

__all__ = ("CollectionPropertiesMixin",)


class CollectionPropertiesMixin:
    """Mixin to force the user specify the collection properties."""

    database_name: str = None
    collection_name: str = None
    model_class: Type[Model] = None

    @classmethod
    def get_db_name(cls):
        """
        Get the database name (defined as class variable ``database_name``) of the collection.

        If single-db is in effect, return the name of the single-db instead.

        :return: database name of the collection
        :raises AttributeError: if `database_name` is undefined or `None`
        """
        if SINGLE_DB_NAME:
            return SINGLE_DB_NAME

        if cls.database_name is None:
            raise AttributeError(f"Define `database_name` as class variable for {cls.__qualname__}.")

        return cls.database_name

    @classmethod
    def get_col_name(cls):
        """
        Get the name (defined as class variable ``collection_name``) of the collection.

        If single-db is in effect, returned name will be in the format of <DATABASE_NAME>.<COLLECTION_NAME> where
        the database name is the **"planned"** database name, not the really in-effect database name.

        For example, if ``database_name`` is ``db`` and ``collection_name`` is ``col``, if single-db is in-effect,
        and the single-db name is ``single``, the return will be ``db.col``, **NOT** ``single.db.col``.

        :return: name of the collection
        :raises AttributeError: if `collection_name` is undefined or `None`
        """
        if cls.collection_name is None:
            raise AttributeError(f"Define `collection_name` as class variable for {cls.__qualname__}.")

        if SINGLE_DB_NAME:
            return f"{cls.database_name}.{cls.collection_name}"

        return cls.collection_name

    @classmethod
    def get_model_cls(cls):
        """
        Get the model class of this collection.

        :return: model class of this collection
        :raises AttributeError: if `model_class` is undefined or `None`
        """
        if cls.model_class is None:
            raise AttributeError(f"Define `model_class` as class variable for {cls.__qualname__}.")

        return cls.model_class
