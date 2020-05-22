from django.utils.translation import gettext_lazy as _

from flags import BotFeature
from msghandle.models import TextMessageEventObject

from ._base import CommandNode

cmd = CommandNode(
    codes=["tf", "trfm", "transform", "rp", "replace"], order_idx=1000, name=_("Transform/Replace"),
    description=_("Transform/Replace the given text."))
cmd_nl = cmd.new_child_node(codes=["nl", "newline"])


# noinspection PyUnusedLocal
@cmd_nl.command_function(
    arg_count=1, arg_help=[_("String to be replaced.")],
    feature_flag=BotFeature.TXT_TRF_REPL_NEWLINE)
def replace_newline(e: TextMessageEventObject, target: str):
    return target.replace("\n", "\\n")
