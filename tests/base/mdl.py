import abc
from typing import List, Dict, Any

from models import Model

from .base import TestCase


class TestModelMixin(TestCase, abc.ABC):
    def assertModelEqual(self, a: Model, b: Model, *, ignore_oid: bool = True):
        if ignore_oid:
            a.clear_oid()
            b.clear_oid()

        self.assertEqual(a, b)

    def assertModelSequenceEqual(self, a: List[Model], b: List[Model], *, ignore_oid: bool = True):
        if ignore_oid:
            for mdl in a:
                mdl.clear_oid()

            for mdl in b:
                mdl.clear_oid()

        self.assertSequenceEqual(a, b)

    def assertModelDictEqual(self, a: Dict[Any, Model], b: Dict[Any, Model], *, ignore_oid: bool = True):
        if ignore_oid:
            for k in a:
                a[k].clear_oid()

            for k in b:
                b[k].clear_oid()

        self.assertDictEqual(a, b)
