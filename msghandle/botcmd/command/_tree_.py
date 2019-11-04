from JellyBot.systemconfig import Bot

from ._base_ import CommandNode

from .trfm import cmd as cmd_trfm
from .uintg import cmd as cmd_uintg
from .id import cmd as cmd_id

# List all main command nodes for some pages to get the command data
__all__ = ["cmd_root", "cmd_trfm", "cmd_id", "cmd_uintg"]


cmd_root = CommandNode(is_root=True, splittor=Bot.Splittor, prefix=Bot.Prefix)
cmd_root.attach_child_node(cmd_trfm)
cmd_root.attach_child_node(cmd_id)
cmd_root.attach_child_node(cmd_uintg)
