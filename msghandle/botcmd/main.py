from typing import List

from JellyBot.systemconfig import Bot
from msghandle.models import TextMessageEventObject, HandledMessageEventText
from msghandle.botcmd.command import cmd_handler


def handle_bot_cmd_main(e: TextMessageEventObject) -> List[HandledMessageEventText]:
    # Terminate if empty string / not starts with command prefix
    if e.content:
        if e.content.startswith(Bot.Prefix) \
                or (Bot.CaseInsensitivePrefix and e.content.lower().startswith(Bot.Prefix.lower())):
            return cmd_handler.handle(e)

    return []
