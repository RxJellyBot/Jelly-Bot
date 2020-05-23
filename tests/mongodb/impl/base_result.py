from dataclasses import dataclass

from django.test import TestCase

from models import Model
from JellyBot.api.static import result
from mongodb.factory.results import BaseResult, ModelResult, WriteOutcome

__all__ = ["TestBaseResult", "TestModelResult"]


class TestBaseResult(TestCase):
    @dataclass
    class Result(BaseResult):
        pass

    # noinspection PyCallByClass
    @staticmethod
    def get_result():
        return TestBaseResult.Result(WriteOutcome.O_DATA_EXISTS, None)

    # noinspection PyCallByClass
    @staticmethod
    def get_result_has_error():
        return TestBaseResult.Result(WriteOutcome.X_NOT_EXECUTED, ValueError("Test error"))

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


class TestModelResult(TestCase):
    class ModelTest(Model):
        pass

    class Result(ModelResult):
        pass

    # noinspection PyCallByClass
    @staticmethod
    def get_result(mdl):
        return TestModelResult.Result(WriteOutcome.O_DATA_EXISTS, None, mdl)

    # noinspection PyCallByClass
    @staticmethod
    def get_result_has_error(mdl):
        return TestModelResult.Result(WriteOutcome.X_NOT_EXECUTED, ValueError("Test error"), mdl)

    def test_property(self):
        r = self.get_result(TestModelResult.ModelTest())
        self.assertEqual(r.outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertIsNone(r.exception)

    def test_serialize(self):
        mdl = TestModelResult.ModelTest()
        r = self.get_result(mdl)
        self.assertEqual(
            r.serialize(),
            {
                result.Results.EXCEPTION: "None",
                result.Results.OUTCOME: -101,
                result.Results.MODEL: mdl
            }
        )

    def test_is_success(self):
        r = self.get_result(TestModelResult.ModelTest())
        self.assertTrue(r.success)

    def test_model(self):
        mdl = TestModelResult.ModelTest()
        r = self.get_result(mdl)
        self.assertEqual(r.model, mdl)

    def test_property_has_error(self):
        r = self.get_result_has_error(TestModelResult.ModelTest())
        self.assertEqual(r.outcome, WriteOutcome.X_NOT_EXECUTED)
        self.assertIsInstance(r.exception, ValueError)

    def test_serialize_has_error(self):
        mdl = TestModelResult.ModelTest()
        r = self.get_result_has_error(mdl)
        self.assertEqual(
            r.serialize(),
            {
                result.Results.EXCEPTION: "ValueError('Test error')",
                result.Results.OUTCOME: 901,
                result.Results.MODEL: mdl
            }
        )

    def test_is_success_has_error(self):
        r = self.get_result_has_error(TestModelResult.ModelTest())
        self.assertFalse(r.success)

    def test_model_has_error(self):
        mdl = TestModelResult.ModelTest()
        r = self.get_result_has_error(mdl)
        self.assertEqual(r.model, mdl)
