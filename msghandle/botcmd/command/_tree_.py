from JellyBot.systemconfig import Bot

from ._base_ import CommandNode

from .trfm import cmd as cmd_trfm
from .uintg import cmd as cmd_uintg
from .id import cmd as cmd_id
from .ar import cmd_main as cmd_ar, cmd_old_add as cmd_old_ar_add

# List all main command nodes for some pages to get the command data
__all__ = ["cmd_root", "cmd_root_old", "cmd_trfm", "cmd_id", "cmd_uintg"]


cmd_root = CommandNode(
    is_root=True, splittor=Bot.Splittor, prefix=Bot.Prefix, case_insensitive=Bot.CaseInsensitive)
cmd_root.attach_child_node(cmd_trfm)
cmd_root.attach_child_node(cmd_id)
cmd_root.attach_child_node(cmd_uintg)
cmd_root.attach_child_node(cmd_ar)

# DEPRECATE: Bot Command - Tree Root of old ways to call command
cmd_root_old = CommandNode(
    is_root=True, splittor=Bot.OldSplittor, prefix=Bot.OldPrefix, case_insensitive=Bot.CaseInsensitive)
cmd_root_old.attach_child_node(cmd_old_ar_add)
