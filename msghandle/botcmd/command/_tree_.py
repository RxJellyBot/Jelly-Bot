from ._base_ import CommandNode

from .uintg import cmd as uintg_node
from .trfm import cmd as trfm_node

__all__ = ["cmd_root", "cmd_trfm", "cmd_uintg"]


cmd_root = CommandNode(is_root=True)
cmd_trfm = cmd_root.attach_child_node(trfm_node)
cmd_uintg = cmd_root.attach_child_node(uintg_node)
