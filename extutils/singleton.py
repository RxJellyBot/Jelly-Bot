"""Base class for implementing singleton classes."""
# Obtained from https://stackoverflow.com/a/6798042/11571888
from abc import ABC


class Singleton(type):
    """
    Singleton metaclass.

    Usage:
    >>> class SampleSingletonClass(metaclass=Singleton):
    >>>     pass
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonABC(ABC, type):
    """
    Singleton metaclass with ``ABC``.

    Usage:
    >>> class SampleSingletonClass(metaclass=SingletonABC):
    >>>     pass
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonABC, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
