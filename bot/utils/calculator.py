from typing import List

from django.utils.translation import gettext_lazy as _

from sympy import sympify
from sympy.core.compatibility import exec_
from sympy.core.sympify import SympifyError
# noinspection PyProtectedMember
from sympy.abc import _clash1

from msghandle import logger
from msghandle.models import HandledMessageCalculateResult


def calculate_expression(expr: str, output_error: bool = False) -> List[HandledMessageCalculateResult]:
    ns = {"_clash1": _clash1}

    try:
        if "\n" in expr:
            msgs = expr.split("\n")
            expr = msgs[-1]

            exec_("\n".join(msgs[:-1]), ns)

        return [HandledMessageCalculateResult(expr_before=expr, expr_after=sympify(expr, ns))]
    except SympifyError as e:
        logger.logger.debug(
            f"Exception occurred for text message calculator. Expr: {e.expr} / Base Exception: {e.base_exc}")

        if output_error:
            return [HandledMessageCalculateResult(
                expr_before=_("I have difficulty understanding you.\n{} ({})").format(e.expr, e.base_exc))]
        else:
            return []
    except NameError as e:
        logger.logger.debug(f"Exception occurred for text message calculator. Message: {e.args}")

        if output_error:
            return [HandledMessageCalculateResult(expr_before=_("WTF are you talking about?\n{}").format(e.args))]
        else:
            return []
    except SyntaxError as e:
        if output_error:
            return [HandledMessageCalculateResult(
                expr_before=_("I can't understand.\n{} ({})").format(e.args, e.text))]
        else:
            return []
