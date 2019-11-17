from gettext import gettext as _
from typing import List

from django.urls import reverse

from JellyBot.systemconfig import Bot, HostUrl
from msghandle.models import TextMessageEventObject, HandledMessageEventText
from msghandle.botcmd.command import cmd_handler, cmd_handler_old


def handle_bot_cmd_main(e: TextMessageEventObject) -> List[HandledMessageEventText]:
    # Terminate if empty string / not starts with command prefix
    if e.content:
        if e.content.startswith(Bot.Prefix) \
                or (Bot.CaseInsensitivePrefix and e.content.lower().startswith(Bot.Prefix.lower())):
            return cmd_handler.handle(e)

        # DEPRECATE: Bot Command - Parsing
        elif e.content.startswith(Bot.OldPrefix) \
                or (Bot.CaseInsensitivePrefix and e.content.lower().startswith(Bot.OldPrefix.lower())):
            return [HandledMessageEventText(
                content=_(
                    "This way of calling the command is deprecating. "
                    "Please visit {} to see what is available and to use it for the new command set."
                ).format(f"{HostUrl}{reverse('page.doc.botcmd.main')}"))]\
                   + cmd_handler_old.handle(e)

    return []
