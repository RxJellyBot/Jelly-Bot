from typing import List

from extutils import is_empty_string
from JellyBot.systemconfig import Bot
from msghandle.models import TextMessageEventObject
from msghandle.botcmd.command import cmd_handler


def handle_bot_cmd_main(e: TextMessageEventObject) -> List[str]:
    # Terminate if empty string / not starts with command prefix
    if is_empty_string(e.content) or not e.content.startswith(Bot.Prefix):
        return []

    return cmd_handler.handle(e)
