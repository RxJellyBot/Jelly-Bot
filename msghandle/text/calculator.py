from typing import List

from sympy import sympify
from sympy.core.compatibility import exec_
from sympy.core.sympify import SympifyError
# noinspection PyProtectedMember
from sympy.abc import _clash1

from flags import BotFeature
from mongodb.factory import BotFeatureUsageDataManager
from msghandle import logger
from msghandle.models import TextMessageEventObject, HandledMessageEvent, HandledMessageCalculateResult

__all__ = ["process_calculator"]


# Obtained and modified from https://stackoverflow.com/a/14822667
def process_calculator(e: TextMessageEventObject) -> List[HandledMessageEvent]:
    if e.text and e.text[-1] == "=":
        expr = e.text[:-1]

        ns = {"_clash1": _clash1}

        try:
            BotFeatureUsageDataManager.record_usage(BotFeature.TXT_FN_CALCULATOR, e.channel_oid, e.user_model.id)

            if "\n" in expr:
                msgs = expr.split("\n")
                expr = msgs[-1]

                exec_("\n".join(msgs[:-1]), ns)

            return [HandledMessageCalculateResult(expr_before=expr, expr_after=sympify(expr, ns))]
        except SympifyError as e:
            logger.logger.debug(
                f"Exception occurred for text message calculator. Expr: {e.expr} / Base Exception: {e.base_exc}")
            return []
        except NameError as e:
            logger.logger.debug(
                f"Exception occurred for text message calculator. Message: {e.args}")
            return []
        except SyntaxError:
            return []
