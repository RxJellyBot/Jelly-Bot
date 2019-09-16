from typing import List

from sympy import sympify
from sympy.core.compatibility import exec_
from sympy.core.sympify import SympifyError
from sympy.abc import _clash1

from external.handle import TextEventObject, HandledEventObject, HandledEventObjectText, logger

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

            return [HandledEventObjectText(content=ret)]
        except SympifyError as e:
            logger.logger.debug(
                f"Exception occurred for text message calculator. Expr: {e.expr} / Base Exception: {e.base_exc}")
            return []
