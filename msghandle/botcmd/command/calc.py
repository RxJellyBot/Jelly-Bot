from django.utils.translation import gettext_lazy as _

from flags import BotFeature
from bot.utils import calculate_expression
from msghandle.models import TextMessageEventObject

from ._base_ import CommandNode


cmd = CommandNode(
    codes=["calc"], order_idx=950, name=_("Calculator"),
    description=_("Execute the sympy calculator."))


# noinspection PyUnusedLocal
@cmd.command_function(
    feature_flag=BotFeature.TXT_CALCULATOR,
    arg_count=1,
    arg_help=[_("Expression string to be calculated."
                "<br>Does not need `=` at the end while for automatic calculator, it's required.")]
)
def calculator(e: TextMessageEventObject, expr: str):
    return calculate_expression(expr, output_error=True)
