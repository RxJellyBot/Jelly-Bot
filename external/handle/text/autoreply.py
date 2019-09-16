from typing import List

from flags import AutoReplyContentType
from JellyBotAPI.sysconfig import AutoReply
from mongodb.factory import AutoReplyManager
from external.handle import TextEventObject, HandledEventObject, HandledEventObjectText


def process_auto_reply(e: TextEventObject) -> List[HandledEventObject]:
    # FIXME: [MP] Not yet channel specified (Handle channel and publics)
    return [
        HandledEventObjectText(content=response) for response
        in AutoReplyManager.get_responses(e.text, AutoReplyContentType.TEXT, case_insensitive=AutoReply.CaseSensitive)
        if response]
