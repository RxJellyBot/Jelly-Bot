import abc
from typing import Dict, Any, Sequence, Set

from models import Model

from .base import TestCase


def _clear_oid(mdl):
    if isinstance(mdl, Model):
        mdl = mdl.__class__.cast_model(mdl.to_json())
        mdl.clear_oid()

    return mdl


class TestModelMixin(TestCase, abc.ABC):
    def assertModelEqual(self, a: Model, b: Model, *, ignore_oid: bool = True):
        if ignore_oid and isinstance(a, Model) and isinstance(b, Model):
            # Duplicating model because `clear_oid()` modifies the model itself, which is undesired

            a = _clear_oid(a)
            b = _clear_oid(b)

        self.assertDictEqual(a.to_json(), b.to_json())
        self.assertEqual(type(a), type(b))

    def assertModelSequenceEqual(self, a: Sequence[Model], b: Sequence[Model], *, ignore_oid: bool = True):
        if ignore_oid:
            a = [_clear_oid(m) for m in a]
            b = [_clear_oid(m) for m in b]

        self.assertSequenceEqual(a, b)

    def assertModelSetEqual(self, a: Set[Model], b: Set[Model], *, ignore_oid: bool = True):
        if ignore_oid:
            a = [_clear_oid(m) for m in a]
            b = [_clear_oid(m) for m in b]

        # For some reason, casting twice yielding correct result
        # https://stackoverflow.com/q/62145686/11571888
        self.assertSetEqual(set(list(a)), set(list(b)))

    def assertModelDictEqual(self, a: Dict[Any, Model], b: Dict[Any, Model], *, ignore_oid: bool = True):
        if ignore_oid:
            a = {k: _clear_oid(m) for k, m in a.items()}
            b = {k: _clear_oid(m) for k, m in b.items()}

        self.assertDictEqual(a, b)
