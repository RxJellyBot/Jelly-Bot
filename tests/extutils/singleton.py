from extutils.singleton import Singleton, SingletonABC
from tests.base import TestCase


class SingletonTest(metaclass=Singleton):
    pass


class SingletonABCTest(metaclass=SingletonABC):
    pass


class SingletonInheritedFromABC(SingletonABCTest):
    pass


class SingletonDoublyInheritedFromABC(SingletonABCTest):
    pass


class TestSingleton(TestCase):
    def test_singleton(self):
        a = SingletonTest()
        b = SingletonTest()
        self.assertEquals(id(a), id(b))

    def test_singleton_abc(self):
        a = SingletonInheritedFromABC()
        b = SingletonInheritedFromABC()
        self.assertEquals(id(a), id(b))

    def test_singleton_abc_double(self):
        a = SingletonDoublyInheritedFromABC()
        b = SingletonDoublyInheritedFromABC()
        self.assertEquals(id(a), id(b))
