from typing import List

from flags import AutoReplyContentType
from JellyBot.systemconfig import AutoReply
from mongodb.factory import AutoReplyManager
from msghandle.models import TextEventObject, HandledEventObject, HandledEventObjectText


def process_auto_reply(e: TextEventObject) -> List[HandledEventObject]:
    return [
        HandledEventObjectText(content=response) for response
        in AutoReplyManager.get_responses(
            e.text, AutoReplyContentType.TEXT, e.channel_oid, case_insensitive=AutoReply.CaseInsensitive)
        if response]
