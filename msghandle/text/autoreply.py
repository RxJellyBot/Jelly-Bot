from typing import List

from flags import AutoReplyContentType
from JellyBot.systemconfig import AutoReply
from mongodb.factory import AutoReplyManager
from msghandle.models import TextMessageEventObject, HandledMessageEvent, HandledMessageEventText


def process_auto_reply(e: TextMessageEventObject) -> List[HandledMessageEvent]:
    return [
        HandledMessageEventText(content=response, bypass_multiline_check=bypass_ml_check) for response, bypass_ml_check
        in AutoReplyManager.get_responses(
            e.text, AutoReplyContentType.TEXT, e.channel_oid, case_insensitive=AutoReply.CaseInsensitive)
        if response]
