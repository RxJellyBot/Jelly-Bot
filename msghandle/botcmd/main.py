from typing import List, Optional, Type

from extutils import is_empty_string, list_get
from JellyBot.systemconfig import Bot
from msghandle.models import TextMessageEventObject


def handle_bot_cmd_main(e: TextMessageEventObject) -> List[str]:
    # Terminate if empty string / not starts with command prefix
    if is_empty_string(e.content) or not e.content.startswith(Bot.Prefix):
        return []

    # Remove prefix from the string content
    e.content = e.content[len(Bot.Prefix):]

    # FIXME: Bot handle

    return []


def _parse_content_(s: str):
    s = s.split(Bot.Splittor)
    return s[0], s[1:]


if __name__ == '__main__':
    print(handle_bot_cmd_main(TextMessageEventObject(raw="/uintg", text="/uintg")))
