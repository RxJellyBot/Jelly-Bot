from django.test import TestCase
from bot.utils import calculate_expression


class TestBotCalculator(TestCase):
    def test_calculate_simple(self):
        expr = "5+5"
        result = calculate_expression(expr)

        if not result:
            self.fail("No calculation result")

        result = result[0]

        self.assertEquals(expr, result.calc_expr)
        self.assertEquals("10", result.calc_result)
        self.assertFalse(result.latex_available)
        self.assertFalse(result.has_evaluated)

    def test_calculate_float(self):
        expr = "5.5+5"
        result = calculate_expression(expr)

        if not result:
            self.fail("No calculation result")

        result = result[0]

        self.assertEquals(expr, result.calc_expr)
        self.assertEquals("10.5", result.calc_result)
        self.assertFalse(result.latex_available)
        self.assertFalse(result.has_evaluated)

    def test_calculate_rational(self):
        expr = "7/2 + 1"
        result = calculate_expression(expr)

        if not result:
            self.fail("No calculation result")

        result = result[0]

        self.assertEquals(expr, result.calc_expr)
        self.assertEquals("9/2", result.calc_result)
        self.assertTrue(result.latex_available)
        self.assertTrue(result.has_evaluated)
        self.assertEquals(4.5, result.evaluated)

    def test_solve_equation(self):
        expr = "solve(x-1)"
        result = calculate_expression(expr)

        if not result:
            self.fail("No calculation result")

        result = result[0]

        self.assertEquals(expr, result.calc_expr)
        self.assertEquals("[1]", result.calc_result)
        self.assertTrue(result.latex_available)
        self.assertFalse(result.has_evaluated)

    def test_multiline(self):
        expr = "a = 7\na + 1"
        result = calculate_expression(expr)

        if not result:
            self.fail("No calculation result")

        result = result[0]

        self.assertEquals("a + 1", result.calc_expr)
        self.assertEquals("8", result.calc_result)
        self.assertFalse(result.latex_available)
        self.assertFalse(result.has_evaluated)

    def test_malformed(self):
        expr = "=_="
        result = calculate_expression(expr)

        if result:
            self.fail("Got a calculation result")

    def test_force_output_error(self):
        expr = "5+"
        result = calculate_expression(expr, output_error=True)

        if not result:
            self.fail("No error output")

        result = result[0]

        self.assertEquals(expr, result.calc_expr)
        self.assertFalse(result.latex_available)
        self.assertFalse(result.has_evaluated)
