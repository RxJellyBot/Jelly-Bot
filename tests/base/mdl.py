import abc
from typing import Dict, Any, Sequence, Set

from models import Model

from .base import TestCase


class TestModelMixin(TestCase, abc.ABC):
    def assertModelEqual(self, a: Model, b: Model, *, ignore_oid: bool = True):
        if ignore_oid:
            # Duplicating model because `clear_oid()` modifies the model itself, which is undesired
            a = a.__class__.cast_model(a.to_json())
            b = b.__class__.cast_model(b.to_json())

            a.clear_oid()
            b.clear_oid()

        self.assertEqual(a, b)

    def assertModelSequenceEqual(self, a: Sequence[Model], b: Sequence[Model], *, ignore_oid: bool = True):
        if ignore_oid:
            a = [m.__class__.cast_model(m.to_json()) for m in a]
            for mdl in a:
                mdl.clear_oid()

            b = [m.__class__.cast_model(m.to_json()) for m in b]
            for mdl in b:
                mdl.clear_oid()

        self.assertSequenceEqual(a, b)

    def assertModelSetEqual(self, a: Set[Model], b: Set[Model], *, ignore_oid: bool = True):
        if ignore_oid:
            a = [m.__class__.cast_model(m.to_json()) for m in a]
            for mdl in a:
                mdl.clear_oid()

            b = [m.__class__.cast_model(m.to_json()) for m in b]
            for mdl in b:
                mdl.clear_oid()

        # For some reason, casting twice yielding correct result
        # https://stackoverflow.com/q/62145686/11571888
        self.assertSetEqual(set(list(a)), set(list(b)))

    def assertModelDictEqual(self, a: Dict[Any, Model], b: Dict[Any, Model], *, ignore_oid: bool = True):
        if ignore_oid:
            a = {k: m.__class__.cast_model(m.to_json()) for k, m in a.items()}
            for k in a:
                a[k].clear_oid()

            b = {k: m.__class__.cast_model(m.to_json()) for k, m in b.items()}
            for k in b:
                b[k].clear_oid()

        self.assertDictEqual(a, b)
