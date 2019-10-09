from typing import List

from msghandle.models import TextMessageEventObject, HandledMessageEvent, HandledMessageEventText
from msghandle.botcmd import handle_bot_cmd_main


def process_bot_cmd(e: TextMessageEventObject) -> List[HandledMessageEvent]:
    return [HandledMessageEventText(content=resp) for resp in handle_bot_cmd_main(e)]
