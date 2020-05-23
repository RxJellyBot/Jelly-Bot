from abc import ABC, abstractmethod
from typing import Type, final

from models import Model
from JellyBot.api.static import result
from mongodb.factory.results import BaseResult, ModelResult, WriteOutcome
from tests.base import TestCase

__all__ = ["TestOnBaseResult", "TestOnModelResult"]


class TestOnBaseResult(ABC):
    class TestClass(TestCase):
        @classmethod
        @abstractmethod
        def get_result_class(cls) -> Type[BaseResult]:
            raise NotImplementedError()

        @classmethod
        @final
        def get_result(cls):
            # noinspection PyArgumentList
            return cls.get_result_class()(WriteOutcome.O_DATA_EXISTS, None)

        @classmethod
        @final
        def get_result_has_error(cls):
            # noinspection PyArgumentList
            return cls.get_result_class()(WriteOutcome.X_NOT_EXECUTED, ValueError("Test error"))

        def test_property(self):
            r = self.get_result()
            self.assertEqual(r.outcome, WriteOutcome.O_DATA_EXISTS)
            self.assertIsNone(r.exception)

        def test_serialize(self):
            r = self.get_result()
            self.assertEqual(
                r.serialize(),
                {
                    result.Results.EXCEPTION: "None",
                    result.Results.OUTCOME: -101
                }
            )

        def test_is_success(self):
            r = self.get_result()
            self.assertTrue(r.success)

        def test_property_has_error(self):
            r = self.get_result_has_error()
            self.assertEqual(r.outcome, WriteOutcome.X_NOT_EXECUTED)
            self.assertIsInstance(r.exception, ValueError)

        def test_serialize_has_error(self):
            r = self.get_result_has_error()
            self.assertEqual(
                r.serialize(),
                {
                    result.Results.EXCEPTION: "ValueError('Test error')",
                    result.Results.OUTCOME: 901
                }
            )

        def test_is_success_has_error(self):
            r = self.get_result_has_error()
            self.assertFalse(r.success)


class TestOnModelResult(ABC):
    class TestClass(TestCase):
        @classmethod
        @abstractmethod
        def get_result_class(cls) -> Type[ModelResult]:
            raise NotImplementedError()

        @classmethod
        @abstractmethod
        def get_constructed_model(cls) -> Model:
            raise NotImplementedError()

        @classmethod
        @final
        def get_result(cls, mdl: Model):
            # noinspection PyArgumentList
            return cls.get_result_class()(WriteOutcome.O_DATA_EXISTS, None, mdl)

        @classmethod
        @final
        def get_result_has_error(cls, mdl: Model):
            # noinspection PyArgumentList
            return cls.get_result_class()(WriteOutcome.X_NOT_EXECUTED, ValueError("Test error"), mdl)

        def test_property(self):
            r = self.get_result(self.get_constructed_model())
            self.assertEqual(r.outcome, WriteOutcome.O_DATA_EXISTS)
            self.assertIsNone(r.exception)

        def test_serialize(self):
            r = self.get_result(self.get_constructed_model())
            self.assertEqual(
                r.serialize(),
                {
                    result.Results.EXCEPTION: "None",
                    result.Results.OUTCOME: -101,
                    result.Results.MODEL: self.get_constructed_model()
                }
            )

        def test_is_success(self):
            r = self.get_result(self.get_constructed_model())
            self.assertTrue(r.success)

        def test_model(self):
            r = self.get_result(self.get_constructed_model())
            self.assertEqual(r.model, self.get_constructed_model())

        def test_property_has_error(self):
            r = self.get_result_has_error(self.get_constructed_model())
            self.assertEqual(r.outcome, WriteOutcome.X_NOT_EXECUTED)
            self.assertIsInstance(r.exception, ValueError)

        def test_serialize_has_error(self):
            r = self.get_result_has_error(self.get_constructed_model())
            self.assertEqual(
                r.serialize(),
                {
                    result.Results.EXCEPTION: "ValueError('Test error')",
                    result.Results.OUTCOME: 901,
                    result.Results.MODEL: self.get_constructed_model()
                }
            )

        def test_is_success_has_error(self):
            r = self.get_result_has_error(self.get_constructed_model())
            self.assertFalse(r.success)

        def test_model_has_error(self):
            r = self.get_result_has_error(self.get_constructed_model())
            self.assertEqual(r.model, self.get_constructed_model())
