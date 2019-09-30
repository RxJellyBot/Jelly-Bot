# FIXME: Complete user identity intergation webpage (Takes token action and requires login)
# FIXME: Complete bot command to create a token action, return token for user identity integration
from typing import List

from msghandle.models import TextMessageEventObject, HandledMessageEvent, HandledMessageEventText
from msghandle.botcmd import handle_bot_cmd_main


def process_bot_cmd(e: TextMessageEventObject) -> List[HandledMessageEvent]:
    return [HandledMessageEventText(content=resp) for resp in handle_bot_cmd_main(e)]
