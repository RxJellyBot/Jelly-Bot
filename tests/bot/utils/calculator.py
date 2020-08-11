from bot.utils import calculate_expression
from tests.base import TestCase

__all__ = ["TestBotCalculator"]


class TestBotCalculator(TestCase):
    def test_calculate_simple(self):
        expr = "5+5"
        result = calculate_expression(expr)

        if not result:
            self.fail("No calculation result")

        result = result[0]

        self.assertEqual(expr, result.calc_expr, "Calculation expression not match.")
        self.assertEqual("10", result.calc_result, "Calculation result not match.")
        self.assertFalse(result.latex_available, "LaTeX should not be available.")
        self.assertFalse(result.has_evaluated, "Expression should not be evaluated.")

    def test_calculate_float(self):
        expr = "5.5+5"
        result = calculate_expression(expr)

        if not result:
            self.fail("No calculation result")

        result = result[0]

        self.assertEqual(expr, result.calc_expr, "Calculation expression not match.")
        self.assertEqual("10.5", result.calc_result, "Calculation result not match.")
        self.assertFalse(result.latex_available, "LaTeX should not be available.")
        self.assertFalse(result.has_evaluated, "Expression should not be evaluated.")

    def test_calculate_rational(self):
        expr = "7/2 + 1"
        result = calculate_expression(expr)

        if not result:
            self.fail("No calculation result")

        result = result[0]

        self.assertEqual(expr, result.calc_expr, "Calculation expression not match.")
        self.assertEqual("9/2", result.calc_result, "Calculation result not match.")
        self.assertTrue(result.latex_available, "LaTeX should be available.")
        self.assertTrue(result.has_evaluated, "Expression should be evaluated.")
        self.assertEqual(4.5, result.evaluated, "Evaluated result not match.")

    def test_solve_equation(self):
        expr = "solve(x-1)"
        result = calculate_expression(expr)

        if not result:
            self.fail("No calculation result")

        result = result[0]

        self.assertEqual(expr, result.calc_expr, "Calculation expression not match.")
        self.assertEqual("[1]", result.calc_result, "Calculation result not match.")
        self.assertTrue(result.latex_available, "LaTeX should be available.")
        self.assertFalse(result.has_evaluated, "Expression should not be evaluated.")

    def test_multiline(self):
        expr = "a = 7\na + 1"
        result = calculate_expression(expr)

        if not result:
            self.fail("No calculation result")

        result = result[0]

        self.assertEqual("a + 1", result.calc_expr, "Calculation expression not match.")
        self.assertEqual("8", result.calc_result, "Calculation result not match.")
        self.assertFalse(result.latex_available, "LaTeX should not be available.")
        self.assertFalse(result.has_evaluated, "Expression should not be evaluated.")

    def test_malformed(self):
        expr = "=_="
        result = calculate_expression(expr)

        if result:
            self.fail(f"Got a calculation result.\n{result[0].to_json()}")

    def test_force_output_error(self):
        expr = "5+"
        result = calculate_expression(expr, output_error=True)

        if not result:
            self.fail("No error output")

        result = result[0]

        self.assertEqual(expr, result.calc_expr, "Calculation expression not match.")
        self.assertFalse(result.latex_available, "LaTeX should not be available.")
        self.assertFalse(result.has_evaluated, "Expression should not be evaluated.")
