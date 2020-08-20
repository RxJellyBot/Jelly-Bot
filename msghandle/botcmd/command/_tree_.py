from django.utils.translation import gettext_lazy as _

from JellyBot.systemconfig import Bot, HostUrl
from msghandle.models import HandledMessageEventText

from ._base import CommandNode
from .trfm import cmd as cmd_trfm
from .uintg import cmd as cmd_uintg
from .id import cmd as cmd_id
from .ar import cmd_main as cmd_ar
from .help import cmd as cmd_help
from .rdm import cmd as cmd_rdm
from .rmc import cmd as cmd_rmc
from .tmr import cmd as cmd_tmr
from .rct import cmd as cmd_rct
from .surl import cmd as cmd_surl
from .calc import cmd as cmd_calc
from .prof import cmd as cmd_prof
from .ping import cmd as cmd_ping
from .stk import cmd as cmd_stk

# List all main command nodes for some pages to get the command data
__all__ = ("cmd_root", "cmd_trfm", "cmd_id", "cmd_uintg", "cmd_help", "cmd_tmr", "cmd_rct",)


cmd_root = CommandNode(
    is_root=True, splitters=Bot.Splitters, prefix=Bot.Prefix, case_insensitive=Bot.CaseInsensitive)
cmd_root.attach_child_node(cmd_trfm)
cmd_root.attach_child_node(cmd_id)
cmd_root.attach_child_node(cmd_uintg)
cmd_root.attach_child_node(cmd_ar)
cmd_root.attach_child_node(cmd_help)
cmd_root.attach_child_node(cmd_rdm)
cmd_root.attach_child_node(cmd_tmr)
cmd_root.attach_child_node(cmd_rct)
cmd_root.attach_child_node(cmd_rmc)
cmd_root.attach_child_node(cmd_surl)
cmd_root.attach_child_node(cmd_calc)
cmd_root.attach_child_node(cmd_prof)
cmd_root.attach_child_node(cmd_ping)
cmd_root.attach_child_node(cmd_stk)

# DEPRECATE: Old command

cmd_ar_old = cmd_root.new_child_node(codes=["a", "aa", "d", "del"], order_idx=99999999)
cmd_root.attach_child_node(cmd_ar_old)


cmd_desc = _("Dummy command for accomodating new command usage.")
txt = _("Please add 'AR' which means 'Auto-Reply' between JC and the command code.\n------\n"
        "Example:\n"
        "**Old**\n"
        "```\n"
        "JC\n"
        "AA\n"
        "A\n"
        "B\n"
        "```\n"
        "\n"
        "**New**\n"
        "```\n"
        "JC\n"
        "AR\n"
        "AA\n"
        "A B\n"
        "C\n"
        "```\n"
        "\n"
        "Additionally, you can now use **single space** as the command splitter.\n"
        "For parameters that contains any spaces, "
        "use double quotation mark (`\"`) to wrap it. Example using the above command: `JC AA AR \"A B\" C`.\n"
        "For more command usage, visit {}").format(HostUrl)


# noinspection PyUnusedLocal
@cmd_ar_old.command_function()
def old_arg_0(e):
    return [HandledMessageEventText(content=txt)]


# noinspection PyUnusedLocal
@cmd_ar_old.command_function(arg_count=1)
def old_arg_1(e, dummy1):
    return [HandledMessageEventText(content=txt)]


# noinspection PyUnusedLocal
@cmd_ar_old.command_function(arg_count=2)
def old_arg_2(e, dummy1, dummy2):
    return [HandledMessageEventText(content=txt)]
