from abc import abstractmethod


def abstractproperty(func):
    return property(abstractmethod(func))
