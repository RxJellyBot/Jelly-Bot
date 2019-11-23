from JellyBot.systemconfig import Bot

from ._base_ import CommandNode

from .trfm import cmd as cmd_trfm
from .uintg import cmd as cmd_uintg
from .id import cmd as cmd_id
from .ar import cmd_main as cmd_ar
from .help import cmd as cmd_help

# List all main command nodes for some pages to get the command data
__all__ = ["cmd_root", "cmd_trfm", "cmd_id", "cmd_uintg", "cmd_help"]


cmd_root = CommandNode(
    is_root=True, splittors=Bot.Splittors, prefix=Bot.Prefix, case_insensitive=Bot.CaseInsensitive)
cmd_root.attach_child_node(cmd_trfm)
cmd_root.attach_child_node(cmd_id)
cmd_root.attach_child_node(cmd_uintg)
cmd_root.attach_child_node(cmd_ar)
cmd_root.attach_child_node(cmd_help)
