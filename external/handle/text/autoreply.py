from typing import List

from flags import AutoReplyContentType
from JellyBotAPI.SystemConfig import AutoReply
from mongodb.factory import AutoReplyManager
from external.handle import TextEventObject, HandledEventObject, HandledEventObjectText


def process_auto_reply(e: TextEventObject) -> List[HandledEventObject]:
    return [
        HandledEventObjectText(txt) for txt in
        AutoReplyManager.get_response(e.text, AutoReplyContentType.TEXT, case_insensitive=AutoReply.CaseSensitive)]
