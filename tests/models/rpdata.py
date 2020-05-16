from typing import Dict, Tuple, Any, Type

from models import Model, PendingRepairDataModel

from ._test_base import TestModel

__all__ = ["TestPendingRepairDataModel"]


class TestPendingRepairDataModel(TestModel.TestClass):
    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return PendingRepairDataModel

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("d", "Data"): {"A": "B"},
            ("m", "MissingKeys"): ["c", "d"]
        }
