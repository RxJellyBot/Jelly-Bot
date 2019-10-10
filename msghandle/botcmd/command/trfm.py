from gettext import gettext as _
from msghandle.models import TextMessageEventObject

from ._base_ import CommandNode

cmd = CommandNode(
    ["tf", "trfm", "transform", "rp", "replace"], 300, _("Transform/Replace"), _("Transform/Replace the given text."))
cmd_nl = cmd.new_child_node(["nl", "newline"])


@cmd_nl.command_function(
    arg_count=1, arg_help=[_("String to be replaced.")],
    description=_("Replace the real newline character to be the escaped character \\n."))
def replace_newline(e: TextMessageEventObject, target: str):
    return target.replace("\n", "\\n")
