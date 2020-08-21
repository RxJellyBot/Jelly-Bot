"""Calculator using ``sympy.sympify`` to perform calculation by passing ``str``."""
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
    """
    Calculate the expression ``expr`` using ``sympify()``.

    :param expr: expression to be calculated
    :param output_error: output the error if any during the calculation
    :return: packed calculation result
    """
    ns_sympy = {"_clash1": _clash1}

    try:
        if "\n" in expr:
            msgs = expr.split("\n")
            expr = msgs[-1]

            exec_("\n".join(msgs[:-1]), ns_sympy)

        ret = [HandledMessageCalculateResult(expr_before=expr, expr_after=sympify(expr, ns_sympy))]
    except SympifyError as ex:
        logger.logger.debug(
            "Exception occurred for text message calculator. Expr: %s / Base Exception: %s", ex.expr, ex.base_exc)

        if output_error:
            str_dict = {
                "expr": ex.expr,
                "exc": ex.base_exc
            }

            ret = [HandledMessageCalculateResult(
                expr_before=expr,
                expr_after=_("I have difficulty understanding you.\n%(expr)s (%(exc)s)") % str_dict)]
        else:
            ret = []
    except NameError as ex:
        logger.logger.debug("Exception occurred for text message calculator. Message: %s", ex.args)

        if output_error:
            ret = [HandledMessageCalculateResult(
                expr_before=expr,
                expr_after=_("WTF are you talking about?\n{}") % ex.args)]
        else:
            ret = []
    except SyntaxError as ex:
        if output_error:
            ret = [HandledMessageCalculateResult(
                expr_before=expr,
                expr_after=_("I can't understand.\n{} ({})") % (ex.args, ex.text))]
        else:
            ret = []

    return ret
