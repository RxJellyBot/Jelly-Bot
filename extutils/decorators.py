"""
Module of various utility decorators.
"""
from abc import abstractmethod


def abstractproperty(func):
    """
    Define the property as abstract.

    Example:

    >>> @abstractproperty
    >>> def prop(self):
    >>>     raise NotImplementedError()

    :param func: function to be decorated
    """
    return property(abstractmethod(func))
