from ._base_ import CommandHandler
from ._tree_ import cmd_root, cmd_root_old, cmd_uintg, cmd_trfm, cmd_id

__all__ = ["cmd_handler", "cmd_handler_old", "cmd_root", "cmd_root_old", "cmd_uintg", "cmd_trfm", "cmd_id"]


cmd_handler = CommandHandler(cmd_root)
cmd_handler_old = CommandHandler(cmd_root_old)
