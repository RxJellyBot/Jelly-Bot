from abc import ABC, abstractmethod
from typing import final, Any, Tuple

from models import Model
from JellyBot.api.static import result
from mongodb.factory.results import WriteOutcome
from tests.base import TestCase

__all__ = ["TestOnBaseResult", "TestOnModelResult"]


class _TestResult(ABC, TestCase):
    @classmethod
    @abstractmethod
    def get_result_class(cls):
        """Class of the result to be tested."""
        raise NotImplementedError()

    @classmethod
    @final
    def get_result(cls, *args):
        """Get the construted result instance, which the outcome is success."""
        return cls.get_result_class()(
            WriteOutcome.O_DATA_EXISTS, None, *args, *cls.result_args_all_no_error())

    @classmethod
    @final
    def get_result_has_error(cls, *args):
        """Get the construted result instance, which the outcome is failed."""
        return cls.get_result_class()(
            WriteOutcome.X_NOT_EXECUTED, ValueError("Test error"), *args, *cls.result_args_all_has_error())

    @classmethod
    def result_args_all_no_error(cls) -> Tuple[Any, ...]:
        """
        Arguments to construct a success result instance excluding ``outcome`` and ``exception``.

        This will be directly called to construct a result instance.
        """
        return cls.result_args_no_error()

    @classmethod
    def result_args_no_error(cls) -> Tuple[Any, ...]:
        """
        Additional arguments to construct a success result instance excluding ``outcome`` and ``exception``.
        """
        return ()

    @classmethod
    def result_args_all_has_error(cls) -> Tuple[Any, ...]:
        """
        Arguments to construct a failed result instance excluding ``outcome`` and ``exception``.

        This will be directly called to construct a result instance.
        """
        return cls.result_args_has_error()

    @classmethod
    def result_args_has_error(cls) -> Tuple[Any, ...]:
        """
        Additional arguments to construct a failed result instance excluding ``outcome`` and ``exception``.
        """
        return ()

    @classmethod
    def default_serialized(cls) -> dict:
        """
        Get the expected serialized successful result.

        :return: expected serialized successful result
        """
        return {
            result.Results.EXCEPTION: "None",
            result.Results.OUTCOME: -101
        }

    @classmethod
    def default_serialized_error(cls):
        """
        Get the expected serialized failing result.

        :return: expected serialized failing result
        """
        return {
            result.Results.EXCEPTION: "ValueError('Test error')",
            result.Results.OUTCOME: 901
        }

    def test_property(self):
        r = self.get_result()
        self.assertEqual(r.outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertIsNone(r.exception)

    def test_serialize(self):
        r = self.get_result()
        self.assertEqual(r.serialize(), self.default_serialized())

    def test_is_success(self):
        r = self.get_result()
        self.assertTrue(r.success)

    def test_property_has_error(self):
        r = self.get_result_has_error()
        self.assertEqual(r.outcome, WriteOutcome.X_NOT_EXECUTED)
        self.assertIsInstance(r.exception, ValueError)

    def test_serialize_has_error(self):
        r = self.get_result_has_error()
        self.assertEqual(r.serialize(), self.default_serialized_error())

    def test_is_success_has_error(self):
        r = self.get_result_has_error()
        self.assertFalse(r.success)


class TestOnBaseResult(ABC):
    class TestClass(_TestResult, ABC):
        pass


class TestOnModelResult(ABC):
    class TestClass(_TestResult, ABC):
        @classmethod
        @abstractmethod
        def get_constructed_model(cls) -> Model:
            """A constructed model to be put into the successful result."""
            raise NotImplementedError()

        @classmethod
        @final
        def result_args_all_no_error(cls) -> Tuple[Any, ...]:
            return (cls.get_constructed_model(),) + cls.result_args_no_error()

        @classmethod
        @final
        def result_args_all_has_error(cls) -> Tuple[Any, ...]:
            return (None,) + cls.result_args_has_error()

        @classmethod
        def default_serialized(cls):
            d = super().default_serialized()
            d.update({result.Results.MODEL: cls.get_constructed_model()})
            return d

        @classmethod
        def default_serialized_error(cls):
            d = super().default_serialized_error()
            d.update({result.Results.MODEL: None})
            return d

        def test_model(self):
            r = self.get_result()
            self.assertEqual(r.model, self.get_constructed_model())

        def test_model_has_error(self):
            r = self.get_result_has_error()
            self.assertIsNone(r.model)
