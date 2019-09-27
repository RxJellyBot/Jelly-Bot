from typing import List

from sympy import sympify, latex
from sympy.core.compatibility import exec_
from sympy.core.sympify import SympifyError
# noinspection PyProtectedMember
from sympy.abc import _clash1

from msghandle import logger
from msghandle.models import TextEventObject, HandledEventObject, HandledEventObjectCalculateResult

__all__ = ["process_calculator"]


# Obtained and modified from https://stackoverflow.com/a/14822667
def process_calculator(e: TextEventObject) -> List[HandledEventObject]:
    if e.text[-1] == "=":
        expr = e.text[:-1]
        symbol_vals = {}

        ns = {"_clash1": _clash1}

        try:
            if "\n" in expr:
                msgs = expr.split("\n")
                expr = msgs[-1]

                exec_("\n".join(msgs[:-1]), ns)

            expression = sympify(expr, ns)

            if hasattr(expression, "subs"):
                ret = repr(expression.subs(symbol_vals))
            else:
                ret = str(expression)

            return [HandledEventObjectCalculateResult(content=ret, latex=latex(expression))]
        except SympifyError as e:
            logger.logger.debug(
                f"Exception occurred for text message calculator. Expr: {e.expr} / Base Exception: {e.base_exc}")
            return []
