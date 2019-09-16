from typing import List

from flags import AutoReplyContentType
from JellyBotAPI.sysconfig import AutoReply
from mongodb.factory import AutoReplyManager
from external.handle import TextEventObject, HandledEventObject, HandledEventObjectText


def process_auto_reply(e: TextEventObject) -> List[HandledEventObject]:
    ret = []

    for responses in AutoReplyManager.get_response(
            e.text, AutoReplyContentType.TEXT, case_insensitive=AutoReply.CaseSensitive):
        if responses:
            ret.extend([HandledEventObjectText(content=response) for response in responses])

    return ret
